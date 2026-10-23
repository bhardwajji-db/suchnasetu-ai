"""
SuchnaSetu AI — FastAPI REST Backend
Modular REST layer supporting:
- Multi-provider LLMs (Ollama, OpenRouter, Gemini, Hugging Face)
- Evidence indexing and citation retrieval (EvidenceService)
- Isolated analysis sessions (SessionStore)
- Six Core Legal Notice Fields and human-in-the-loop confirmation
- Adaptive OCR (Tesseract / RapidOCR)
- Multilingual translation (English and Hindi)
- Reading-level calibration (Simple, Standard, Detailed)
"""

from __future__ import annotations

import io
import time
import uuid
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from PIL import Image

from notice2action.config import config, run_preflight_diagnostics
from notice2action.schemas import (
    StructuredNotice,
    SixCoreFields,
    PlainLanguageSummary,
    ActionChecklist,
    FollowUpAnswer,
    ExtractedFact,
)
from notice2action.ingestion import ingest_pasted_text, ingest_uploaded_file
from notice2action.ocr import extract_text_from_image, get_ocr_engine
from notice2action.analysis import NoticeAnalyzer
from notice2action.summary import generate_deterministic_summary
from notice2action.checklist import generate_action_checklist
from notice2action.translation import (
    translate_summary_to_hindi,
    translate_checklist_to_hindi,
)
from notice2action.followup import FollowUpAssistant
from notice2action.tts import generate_audio_bytes
from notice2action.llm import (
    get_llm_client,
    get_all_provider_statuses,
    LLMClientError,
    LLMConfigError,
    LLMAuthError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMRateLimitError,
)
from notice2action.services.evidence_service import evidence_service, EvidenceCitation
from notice2action.services.session_store import session_store, SessionState


app = FastAPI(
    title="SuchnaSetu AI API",
    version="2.0.0",
    description="REST backend for SuchnaSetu AI Notice-to-Action Accessibility Assistant (PS02)",
)

# Enable CORS for local Vite dev and frontend clients (explicit origins for credential safety)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Analysis Cache (Avoids redundant LLM inference)
# ---------------------------------------------------------
_ANALYSIS_CACHE: Dict[str, StructuredNotice] = {}
_MAX_CACHE_ENTRIES = 64


# ---------------------------------------------------------
# Centralized Error Handlers
# ---------------------------------------------------------

@app.exception_handler(LLMConfigError)
async def llm_config_error_handler(request: Request, exc: LLMConfigError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_type": "LLMConfigError"},
    )


@app.exception_handler(LLMAuthError)
async def llm_auth_error_handler(request: Request, exc: LLMAuthError):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc), "error_type": "LLMAuthError"},
    )


@app.exception_handler(LLMRateLimitError)
async def llm_rate_limit_handler(request: Request, exc: LLMRateLimitError):
    return JSONResponse(
        status_code=429,
        content={"detail": str(exc), "error_type": "LLMRateLimitError"},
    )


@app.exception_handler(LLMConnectionError)
async def llm_connection_handler(request: Request, exc: LLMConnectionError):
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc), "error_type": "LLMConnectionError"},
    )


# ---------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------

class IngestTextRequest(BaseModel):
    text: str = Field(..., description="Raw text of the notice")


class IngestTextResponse(BaseModel):
    raw_text: str
    char_count: int
    line_count: int
    security_warning: Optional[str] = None
    fingerprint: str


class OCRResponse(BaseModel):
    extracted_text: str
    confidence_score: float
    languages_used: str
    line_count: int
    char_count: int
    is_preprocessed: bool
    engine_used: str = "tesseract"
    is_uncertain: bool = False
    uncertainty_reason: Optional[str] = None
    warning: Optional[str] = None
    error: Optional[str] = None
    fingerprint: str


class AnalyzeRequest(BaseModel):
    notice_text: str = Field(..., description="Notice text to analyze")
    target_language: str = Field(default="en", description="'en' or 'hi'")
    reading_level: str = Field(default="standard", description="'simple', 'standard', 'detailed'")
    session_id: Optional[str] = Field(default=None, description="Optional persistent session ID")
    provider: Optional[str] = Field(default=None, description="Optional LLM provider override")


class AnalyzeResponse(BaseModel):
    session_id: str
    structured_notice: StructuredNotice
    six_core_fields: SixCoreFields
    summary_en: PlainLanguageSummary
    summary_hi: PlainLanguageSummary
    checklist_en: ActionChecklist
    checklist_hi: ActionChecklist
    fingerprint: str
    duration_seconds: float


class ConfirmFactRequest(BaseModel):
    field_name: str = Field(..., description="Fact attribute being confirmed (e.g. 'deadline', 'notice_date')")
    confirmed_value: str = Field(..., description="User confirmed or corrected value")
    structured_notice: StructuredNotice = Field(..., description="Active structured notice")
    reading_level: str = Field(default="standard", description="'simple', 'standard', 'detailed'")
    session_id: Optional[str] = Field(default=None, description="Optional session ID")


class ConfirmFactResponse(BaseModel):
    structured_notice: StructuredNotice
    six_core_fields: SixCoreFields
    summary_en: PlainLanguageSummary
    summary_hi: PlainLanguageSummary
    checklist_en: ActionChecklist
    checklist_hi: ActionChecklist


class ReadingLevelRequest(BaseModel):
    structured_notice: StructuredNotice
    reading_level: str = Field(default="standard", description="'simple', 'standard', 'detailed'")


class ReadingLevelResponse(BaseModel):
    summary_en: PlainLanguageSummary
    summary_hi: PlainLanguageSummary
    reading_level: str


class FollowUpRequest(BaseModel):
    question: str = Field(..., description="User's query")
    notice_text: str = Field(..., description="Active ground-truth notice text")
    session_id: Optional[str] = Field(default=None, description="Session ID for context isolation")
    target_language: str = Field(default="en", description="'en' or 'hi'")


class SelectProviderRequest(BaseModel):
    provider: str = Field(..., description="Provider name: 'ollama', 'openrouter', 'gemini', 'huggingface'")


class EvidenceSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    notice_text: str = Field(..., description="Raw text of the active notice")
    max_results: int = Field(default=5, description="Max citations to return")


class ExportMarkdownRequest(BaseModel):
    structured_notice: StructuredNotice
    summary: Optional[PlainLanguageSummary] = None
    checklist: Optional[ActionChecklist] = None


class ExportIcsRequest(BaseModel):
    checklist: ActionChecklist
    title: str = "Notice Action Plan"


class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to read aloud")
    lang: str = Field(default="en", description="'en' or 'hi'")


# ---------------------------------------------------------
# Health & Diagnostic Routes
# ---------------------------------------------------------

@app.get("/api/health")
def get_health() -> Dict[str, Any]:
    """Runs preflight diagnostics and returns system health status."""
    report = run_preflight_diagnostics()
    return {
        "overall_status": report.overall_status,
        "active_provider": config.llm_provider,
        "model_name": config.ollama_model if config.llm_provider == "ollama" else getattr(config, f"{config.llm_provider}_model", "unknown"),
        "is_ready_for_inference": report.is_ready_for_inference(),
        "items": [
            {
                "name": item.name,
                "status": item.status,
                "details": item.details,
                "remedy": item.remedy,
            }
            for item in report.items
        ],
    }


# ---------------------------------------------------------
# LLM Provider Management Routes
# ---------------------------------------------------------

@app.get("/api/providers")
def get_providers() -> List[Dict[str, Any]]:
    """Returns configuration and credential status for all supported LLM providers."""
    return get_all_provider_statuses()


@app.post("/api/providers/select")
def select_provider(payload: SelectProviderRequest) -> Dict[str, Any]:
    """Selects the active LLM provider for subsequent inference operations."""
    prov = payload.provider.lower().strip()
    valid = ["ollama", "openrouter", "gemini", "huggingface"]
    if prov not in valid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider '{prov}'. Valid providers: {', '.join(valid)}"
        )

    config.llm_provider = prov
    client = get_llm_client(prov)
    health = client.check_health()
    return {
        "active_provider": prov,
        "status": health,
    }


# ---------------------------------------------------------
# Sample Notice Fixtures
# ---------------------------------------------------------

@app.get("/api/samples")
def list_samples() -> List[Dict[str, str]]:
    """Lists available synthetic demo fixtures and sample notices."""
    return [
        {
            "id": "demo_missing_compliance.txt",
            "title": "📋 Fictional Demo 1: Missing Documents & Compliance",
            "type": "text",
            "language": "en",
        },
        {
            "id": "demo_outstanding_dues.txt",
            "title": "💰 Fictional Demo 2: Outstanding Dues & Demand",
            "type": "text",
            "language": "en",
        },
        {
            "id": "demo_response_hearing.txt",
            "title": "⚖️ Fictional Demo 3: Show-Cause & Statutory Hearing",
            "type": "text",
            "language": "en",
        },
        {
            "id": "demo_scholarship_ambiguous.txt",
            "title": "🎓 Demo A: Scholarship (Ambiguous Deadline)",
            "type": "text",
            "language": "en",
        },
        {
            "id": "demo_campus_placement.txt",
            "title": "💼 Demo B: Campus Placement (CGPA & NOC)",
            "type": "text",
            "language": "en",
        },
        {
            "id": "demo_municipal_water_advisory.txt",
            "title": "🚰 Demo C: Municipal Water Advisory (Zero-Hallucination)",
            "type": "text",
            "language": "en",
        },
        {
            "id": "synthetic_scholarship_notice.txt",
            "title": "🎯 Competition Demo (TEST-SCH-2026-001)",
            "type": "text",
            "language": "en",
        },
        {
            "id": "sample_scholarship_notice.txt",
            "title": "📄 Scholarship Notice (EN)",
            "type": "text",
            "language": "en",
        },
        {
            "id": "sample_hindi_notice.txt",
            "title": "🇮🇳 Notice (Hindi)",
            "type": "text",
            "language": "hi",
        },
        {
            "id": "synthetic_notice_ocr.png",
            "title": "🖼️ Scanned Notice (OCR Demo)",
            "type": "image",
            "language": "en",
        },
        {
            "id": "sample_uncertain_notice.txt",
            "title": "⚠️ Tentative Dates Notice",
            "type": "text",
            "language": "en",
        },
        {
            "id": "sample_missing_fields_notice.txt",
            "title": "❓ Missing Fields Notice",
            "type": "text",
            "language": "en",
        },
    ]


@app.get("/api/samples/{filename}")
def get_sample_content(filename: str):
    """Retrieves content of a synthetic demo notice fixture."""
    clean_name = Path(filename).name
    p = config.synthetic_fixtures_dir / clean_name
    if not p.is_file():
        raise HTTPException(status_code=404, detail=f"Sample fixture '{clean_name}' not found.")

    if clean_name.endswith(".png") or clean_name.endswith(".jpg"):
        return Response(content=p.read_bytes(), media_type="image/png")

    text = p.read_text(encoding="utf-8")
    fp = hashlib.sha256(text.strip().encode("utf-8")).hexdigest()
    return {
        "filename": clean_name,
        "content": text,
        "fingerprint": fp,
    }


# ---------------------------------------------------------
# Ingestion & OCR Endpoints
# ---------------------------------------------------------

@app.post("/api/ingest/text", response_model=IngestTextResponse)
def ingest_text_endpoint(payload: IngestTextRequest):
    """Sanitizes text and calculates its fingerprint."""
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=422, detail="Notice text cannot be empty.")

    res = ingest_pasted_text(payload.text)
    if res.error:
        raise HTTPException(status_code=400, detail=res.error)

    raw_text = res.raw_text or ""
    fp = hashlib.sha256(raw_text.strip().encode("utf-8")).hexdigest()
    line_count = len(raw_text.splitlines()) if raw_text else 0

    # Index into EvidenceService
    evidence_service.index_notice(raw_text)

    return IngestTextResponse(
        raw_text=raw_text,
        char_count=len(raw_text),
        line_count=line_count,
        security_warning=res.security_warning,
        fingerprint=fp,
    )


@app.post("/api/ingest/upload")
async def ingest_upload_endpoint(file: UploadFile = File(...)):
    """Uploads and validates a document (text or image)."""
    file_bytes = await file.read()
    res = ingest_uploaded_file(file.filename or "uploaded_notice", file_bytes)

    if res.error:
        raise HTTPException(status_code=400, detail=res.error)

    if res.source_type in ["text", "pdf"]:
        raw_text = res.raw_text or ""
        fp = hashlib.sha256(raw_text.strip().encode("utf-8")).hexdigest()
        evidence_service.index_notice(raw_text)
        return {
            "source_type": res.source_type,
            "filename": res.filename,
            "raw_text": raw_text,
            "char_count": len(raw_text),
            "line_count": len(raw_text.splitlines()),
            "security_warning": res.security_warning,
            "fingerprint": fp,
        }
    else:
        return {
            "source_type": "image",
            "filename": res.filename,
            "size_bytes": len(file_bytes),
            "content_type": file.content_type,
            "security_warning": None,
        }


@app.post("/api/ocr", response_model=OCRResponse)
async def ocr_endpoint(
    file: UploadFile = File(...),
    target_lang: str = Form("eng"),
    enhance_contrast: bool = Form(True),
    engine: Optional[str] = Form(None),
):
    """Executes OCR on an uploaded image with selected engine."""
    try:
        content = await file.read()
        img = Image.open(io.BytesIO(content)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {e}")

    lang_code = "hin" if "hin" in target_lang and "+" not in target_lang else ("eng+hin" if "+" in target_lang else "eng")
    ocr_res = extract_text_from_image(
        img,
        target_lang=lang_code,
        apply_preprocessing=enhance_contrast,
        engine_name=engine,
    )

    fp = hashlib.sha256(ocr_res.extracted_text.strip().encode("utf-8")).hexdigest() if ocr_res.extracted_text else ""
    if ocr_res.extracted_text:
        evidence_service.index_notice(ocr_res.extracted_text)

    return OCRResponse(
        extracted_text=ocr_res.extracted_text,
        confidence_score=ocr_res.confidence_score,
        languages_used=ocr_res.languages_used,
        line_count=ocr_res.line_count,
        char_count=ocr_res.char_count,
        is_preprocessed=ocr_res.is_preprocessed,
        engine_used=ocr_res.engine_used,
        is_uncertain=ocr_res.is_uncertain,
        uncertainty_reason=ocr_res.uncertainty_reason,
        warning=ocr_res.warning,
        error=ocr_res.error,
        fingerprint=fp,
    )


# ---------------------------------------------------------
# Evidence Service & Session Store Endpoints
# ---------------------------------------------------------

@app.post("/api/evidence/search")
def search_evidence_endpoint(payload: EvidenceSearchRequest) -> List[EvidenceCitation]:
    """Retrieves line-level grounded citations for a search query."""
    return evidence_service.search_evidence(
        query=payload.query,
        notice_text=payload.notice_text,
        max_results=payload.max_results,
    )


@app.get("/api/evidence/{fingerprint}")
def get_evidence_endpoint(fingerprint: str):
    """Retrieves stored evidence index for a notice fingerprint."""
    store = evidence_service.get_evidence_store(fingerprint)
    if not store:
        raise HTTPException(status_code=404, detail="Evidence index not found for fingerprint.")
    return store


@app.get("/api/session/{session_id}")
def get_session_endpoint(session_id: str):
    """Retrieves stored state for an isolated session."""
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session


# ---------------------------------------------------------
# Analysis & Confirmation Endpoints
# ---------------------------------------------------------

@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_endpoint(payload: AnalyzeRequest):
    """Executes the full structured analysis pipeline using the configured LLM."""
    text = payload.notice_text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Notice text cannot be empty.")

    start_time = time.time()
    custom_client = get_llm_client(payload.provider) if payload.provider else None
    analyzer = NoticeAnalyzer(client=custom_client)

    try:
        # Index document in EvidenceService
        evidence_service.index_notice(text)
        fp = hashlib.sha256(text.encode("utf-8")).hexdigest()
        cache_key = f"{fp}:{payload.provider or config.llm_provider}"

        # Structured extraction & deterministic verification (with LRU cache check)
        if cache_key in _ANALYSIS_CACHE:
            structured = _ANALYSIS_CACHE[cache_key].model_copy(deep=True)
        else:
            structured = analyzer.analyze_notice(text)
            if len(_ANALYSIS_CACHE) >= _MAX_CACHE_ENTRIES:
                _ANALYSIS_CACHE.pop(next(iter(_ANALYSIS_CACHE)))
            _ANALYSIS_CACHE[cache_key] = structured.model_copy(deep=True)

        six_core = structured.to_six_core_fields()

        # Summaries & Checklists
        summary_en = generate_deterministic_summary(structured, reading_level=payload.reading_level)
        checklist_en = generate_action_checklist(structured)

        # Bilingual translations
        summary_hi = translate_summary_to_hindi(summary_en, client=None)
        checklist_hi = translate_checklist_to_hindi(checklist_en, client=None)

        duration = time.time() - start_time

        # Create or update session state
        s_id = payload.session_id or str(uuid.uuid4())
        session_store.update_session(s_id, {
            "raw_notice_text": text,
            "fingerprint": fp,
            "reading_level": payload.reading_level,
            "target_language": payload.target_language,
            "structured_notice": structured.model_dump(),
            "summary_en": summary_en.model_dump(),
            "summary_hi": summary_hi.model_dump(),
            "checklist_en": checklist_en.model_dump(),
            "checklist_hi": checklist_hi.model_dump(),
        })

        return AnalyzeResponse(
            session_id=s_id,
            structured_notice=structured,
            six_core_fields=six_core,
            summary_en=summary_en,
            summary_hi=summary_hi,
            checklist_en=checklist_en,
            checklist_hi=checklist_hi,
            fingerprint=fp,
            duration_seconds=round(duration, 2),
        )
    except (LLMConfigError, LLMAuthError, LLMRateLimitError, LLMConnectionError):
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis pipeline error: {e}. Active provider: '{config.llm_provider}'",
        )


@app.post("/api/confirm", response_model=ConfirmFactResponse)
def confirm_fact_endpoint(payload: ConfirmFactRequest):
    """Updates an uncertain fact with user confirmation/correction and refreshes dependent summaries and checklists."""
    field_name = payload.field_name.strip()
    valid_fields = [
        "purpose", "eligibility", "deadline", "fee_or_cost",
        "required_documents", "contact_details", "required_actions", "important_conditions",
        "issuing_authority", "notice_reference_number", "notice_date", "recipient",
        "main_subject", "required_action_and_deadline"
    ]
    if field_name not in valid_fields:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid field_name '{field_name}'. Allowed: {', '.join(valid_fields)}"
        )

    sn = payload.structured_notice
    if hasattr(sn, field_name):
        fact = getattr(sn, field_name)
        fact.user_confirmed = True
        fact.confirmed_value = payload.confirmed_value.strip()
        fact.requires_confirmation = False

    # Refresh dependent summary & checklist
    summary_en = generate_deterministic_summary(sn, reading_level=payload.reading_level)
    checklist_en = generate_action_checklist(sn)
    summary_hi = translate_summary_to_hindi(summary_en, client=None)
    checklist_hi = translate_checklist_to_hindi(checklist_en, client=None)

    # Update session if provided
    if payload.session_id:
        session = session_store.get_session(payload.session_id)
        if session:
            session.user_confirmations[field_name] = payload.confirmed_value.strip()
            session.structured_notice = sn.model_dump()
            session_store.update_session(payload.session_id, {
                "user_confirmations": session.user_confirmations,
                "structured_notice": session.structured_notice,
            })

    return ConfirmFactResponse(
        structured_notice=sn,
        six_core_fields=sn.to_six_core_fields(),
        summary_en=summary_en,
        summary_hi=summary_hi,
        checklist_en=checklist_en,
        checklist_hi=checklist_hi,
    )


@app.post("/api/summary/reading-level", response_model=ReadingLevelResponse)
def reading_level_endpoint(payload: ReadingLevelRequest):
    """Generates plain language summary tailored to the requested reading level."""
    lvl = payload.reading_level.lower().strip()
    if lvl not in ["simple", "standard", "detailed"]:
        lvl = "standard"
    summary_en = generate_deterministic_summary(payload.structured_notice, reading_level=lvl)
    summary_hi = translate_summary_to_hindi(summary_en, client=None)
    return ReadingLevelResponse(
        summary_en=summary_en,
        summary_hi=summary_hi,
        reading_level=lvl,
    )


@app.post("/api/followup", response_model=FollowUpAnswer)
def followup_endpoint(payload: FollowUpRequest):
    """Answers follow-up queries grounded strictly within the active notice text."""
    q = payload.question.strip()
    text = payload.notice_text.strip()

    if not q:
        raise HTTPException(status_code=422, detail="Question cannot be empty.")
    if not text:
        raise HTTPException(status_code=422, detail="Notice text cannot be empty.")

    assistant = FollowUpAssistant()
    answer = assistant.answer_question(q, text, target_lang=payload.target_language)

    # Record in session history if session_id is active
    if payload.session_id:
        session = session_store.get_session(payload.session_id)
        if session:
            session.qa_history.append({
                "question": q,
                "answer": answer.answer,
                "is_supported": answer.is_supported,
                "evidence_quote": answer.evidence_quote,
                "timestamp": time.time(),
            })
            session_store.update_session(payload.session_id, {"qa_history": session.qa_history})

    return answer


@app.post("/api/export/markdown")
def export_markdown_endpoint(payload: ExportMarkdownRequest):
    """Exports structured notice results as a formatted Markdown report."""
    sn = payload.structured_notice
    sm = payload.summary
    cl = payload.checklist

    report = (
        f"# SuchnaSetu AI — Action Report\n\n"
        f"**Notice Purpose**: {sn.purpose.value}\n"
        f"**Issuing Authority**: {sn.issuing_authority.value}\n"
        f"**Reference Number**: {sn.notice_reference_number.value}\n"
        f"**Notice Date**: {sn.notice_date.value}\n"
        f"**Recipient**: {sn.recipient.value}\n"
        f"**Deadline**: {sn.deadline.value}\n"
        f"**Eligibility**: {sn.eligibility.value}\n\n"
        f"## Plain-Language Summary\n"
        f"- About: {sm.about if sm else ''}\n"
        f"- Eligibility: {sm.eligible if sm else ''}\n"
        f"- Action Steps: {sm.actions if sm else ''}\n"
        f"- Documents: {sm.documents if sm else ''}\n"
        f"- Deadline: {sm.deadline if sm else ''}\n"
        f"- Contact: {sm.help_contact if sm else ''}\n"
        f"- Missing Info: {sm.missing if sm else ''}\n\n"
        f"## Grounded Action Checklist\n"
    )
    if cl and cl.items:
        for it in cl.items:
            mand = "MANDATORY" if it.is_mandatory else "ADVISORY"
            report += f"{it.step_number}. [{mand}] ({it.category}) {it.action}\n"
            if it.grounded_quote:
                report += f"   - Quote: \"{it.grounded_quote}\"\n"

    return Response(
        content=report,
        media_type="text/markdown",
        headers={"Content-Disposition": 'attachment; filename="notice2action_plan.md"'},
    )


@app.post("/api/export/ics")
def export_ics_endpoint(payload: ExportIcsRequest):
    """Exports checklist actions as an RFC 5545 iCalendar (.ics) file."""
    ics_bytes = payload.checklist.to_ics_bytes(title=payload.title)
    return Response(
        content=ics_bytes,
        media_type="text/calendar",
        headers={"Content-Disposition": 'attachment; filename="notice_deadline.ics"'},
    )


@app.post("/api/tts")
def tts_endpoint(payload: TTSRequest):
    """Generates MP3 audio for text read-aloud via gTTS."""
    audio_bytes = generate_audio_bytes(payload.text, lang=payload.lang)
    if audio_bytes is None:
        return Response(status_code=204)

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Content-Disposition": 'inline; filename="read_aloud.mp3"'},
    )
