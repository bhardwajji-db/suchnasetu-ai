"""
Notice2Action AI — FastAPI REST Backend
Wraps existing notice2action domain modules without modifying business logic.
Provides REST endpoints for React frontend and external integrations.
"""

from __future__ import annotations

import io
import time
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from PIL import Image

from notice2action.config import config, run_preflight_diagnostics
from notice2action.schemas import (
    StructuredNotice,
    PlainLanguageSummary,
    ActionChecklist,
    FollowUpAnswer,
    ExtractedFact,
)
from notice2action.ingestion import ingest_pasted_text, ingest_uploaded_file
from notice2action.ocr import extract_text_from_image
from notice2action.analysis import NoticeAnalyzer
from notice2action.summary import generate_deterministic_summary
from notice2action.checklist import generate_action_checklist
from notice2action.translation import (
    translate_summary_to_hindi,
    translate_checklist_to_hindi,
)
from notice2action.followup import FollowUpAssistant
from notice2action.tts import generate_audio_bytes


app = FastAPI(
    title="Notice2Action AI API",
    version="1.0.0",
    description="REST backend for Notice-to-Action Accessibility Assistant (PS02)",
)

# Enable CORS for local Vite dev and frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    warning: Optional[str] = None
    error: Optional[str] = None
    fingerprint: str


class AnalyzeRequest(BaseModel):
    notice_text: str = Field(..., description="Notice text to analyze")
    target_language: str = Field(default="en", description="'en' or 'hi'")
    reading_level: str = Field(default="standard", description="'simple', 'standard', 'detailed'")


class AnalyzeResponse(BaseModel):
    structured_notice: StructuredNotice
    summary_en: PlainLanguageSummary
    summary_hi: PlainLanguageSummary
    checklist_en: ActionChecklist
    checklist_hi: ActionChecklist
    fingerprint: str
    duration_seconds: float


class ConfirmFactRequest(BaseModel):
    field_name: str = Field(..., description="Fact attribute being confirmed (e.g. 'deadline')")
    confirmed_value: str = Field(..., description="User confirmed or corrected value")
    structured_notice: StructuredNotice = Field(..., description="Active structured notice")
    reading_level: str = Field(default="standard", description="'simple', 'standard', 'detailed'")


class ConfirmFactResponse(BaseModel):
    structured_notice: StructuredNotice
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
# Routes
# ---------------------------------------------------------

@app.get("/api/health")
def get_health() -> Dict[str, Any]:
    """Runs preflight diagnostics and returns system health status."""
    report = run_preflight_diagnostics()
    return {
        "overall_status": report.overall_status,
        "model_name": config.ollama_model,
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


@app.get("/api/samples")
def list_samples() -> List[Dict[str, str]]:
    """Lists available synthetic demo fixtures and sample notices."""
    return [
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
    # Prevent directory traversal
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

    if res.source_type == "text":
        raw_text = res.raw_text or ""
        fp = hashlib.sha256(raw_text.strip().encode("utf-8")).hexdigest()
        return {
            "source_type": "text",
            "filename": res.filename,
            "raw_text": raw_text,
            "char_count": len(raw_text),
            "line_count": len(raw_text.splitlines()),
            "security_warning": res.security_warning,
            "fingerprint": fp,
        }
    else:
        # Image was uploaded
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
):
    """Executes Tesseract OCR on an uploaded image."""
    try:
        content = await file.read()
        img = Image.open(io.BytesIO(content)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {e}")

    # Map target language code
    lang_code = "hin" if "hin" in target_lang and "+" not in target_lang else ("eng+hin" if "+" in target_lang else "eng")
    ocr_res = extract_text_from_image(img, target_lang=lang_code, apply_preprocessing=enhance_contrast)

    fp = hashlib.sha256(ocr_res.extracted_text.strip().encode("utf-8")).hexdigest() if ocr_res.extracted_text else ""

    return OCRResponse(
        extracted_text=ocr_res.extracted_text,
        confidence_score=ocr_res.confidence_score,
        languages_used=ocr_res.languages_used,
        line_count=ocr_res.line_count,
        char_count=ocr_res.char_count,
        is_preprocessed=ocr_res.is_preprocessed,
        warning=ocr_res.warning,
        error=ocr_res.error,
        fingerprint=fp,
    )


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_endpoint(payload: AnalyzeRequest):
    """Executes the full 5-phase analysis pipeline using local Gemma 4."""
    text = payload.notice_text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Notice text cannot be empty.")

    start_time = time.time()
    analyzer = NoticeAnalyzer()

    try:
        # Phase 3: Structured extraction via Gemma 4 & deterministic verification
        structured = analyzer.analyze_notice(text)

        # Phase 5: Summaries & Checklists
        summary_en = generate_deterministic_summary(structured, reading_level=payload.reading_level)
        checklist_en = generate_action_checklist(structured)

        # Bilingual translations
        summary_hi = translate_summary_to_hindi(summary_en, client=None)
        checklist_hi = translate_checklist_to_hindi(checklist_en, client=None)

        duration = time.time() - start_time
        fp = hashlib.sha256(text.encode("utf-8")).hexdigest()

        return AnalyzeResponse(
            structured_notice=structured,
            summary_en=summary_en,
            summary_hi=summary_hi,
            checklist_en=checklist_en,
            checklist_hi=checklist_hi,
            fingerprint=fp,
            duration_seconds=round(duration, 2),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis pipeline error: {e}. Please ensure Ollama is running with model '{config.ollama_model}'.",
        )


@app.post("/api/confirm", response_model=ConfirmFactResponse)
def confirm_fact_endpoint(payload: ConfirmFactRequest):
    """Updates an uncertain fact with user confirmation/correction and refreshes dependent summaries and checklists."""
    field_name = payload.field_name.strip()
    valid_fields = [
        "purpose", "eligibility", "deadline", "fee_or_cost",
        "required_documents", "contact_details", "required_actions", "important_conditions"
    ]
    if field_name not in valid_fields:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid field_name '{field_name}'. Allowed: {', '.join(valid_fields)}"
        )

    sn = payload.structured_notice
    fact = getattr(sn, field_name)
    fact.user_confirmed = True
    fact.confirmed_value = payload.confirmed_value.strip()
    fact.requires_confirmation = False

    # Refresh dependent summary & checklist
    summary_en = generate_deterministic_summary(sn, reading_level=payload.reading_level)
    checklist_en = generate_action_checklist(sn)
    summary_hi = translate_summary_to_hindi(summary_en, client=None)
    checklist_hi = translate_checklist_to_hindi(checklist_en, client=None)

    return ConfirmFactResponse(
        structured_notice=sn,
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
    answer = assistant.answer_question(q, text)
    return answer


@app.post("/api/export/markdown")
def export_markdown_endpoint(payload: ExportMarkdownRequest):
    """Exports structured notice results as a formatted Markdown report."""
    sn = payload.structured_notice
    sm = payload.summary
    cl = payload.checklist

    report = (
        f"# Notice2Action AI — Action Report\n\n"
        f"**Notice Purpose**: {sn.purpose.value}\n"
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
        # Offline or gTTS unavailable; return 204 to signal client to use Web Speech API
        return Response(status_code=204)

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Content-Disposition": 'inline; filename="read_aloud.mp3"'},
    )
