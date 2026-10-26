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

- Multi-Notice Revision Ledger and Corrigendum Tracking

- Explainable Applicant Eligibility Engine

"""



from __future__ import annotations



import io

import time

import uuid

import hashlib

import asyncio

import threading

import logging

from pathlib import Path

from typing import List, Optional, Dict, Any



from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Response, Depends

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import JSONResponse, FileResponse

from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel, Field

from PIL import Image



from notice2action.config import config, run_preflight_diagnostics, PROJECT_ROOT

from notice2action.schemas import (

    StructuredNotice,

    SixCoreFields,

    PlainLanguageSummary,

    ActionChecklist,

    FollowUpAnswer,

    ExtractedFact,

    RevisionLedger,

    RevisionEntry,

    NoticeRelationship,

    RelationshipType,

    ChangeCategory,

    CompareNoticesRequest,

    EligibilityCriterion,

    CriterionType,

    ApplicantProfile,

    CriterionEvaluationResult,

    EligibilityAssessment,

    EvaluateEligibilityRequest,

    VerifyEvidenceRequest,

    VerifyEvidenceResponse,

    TrustEvidence,

    EvaluatePersonalImpactRequest,

    PersonalImpactReport,

    GenerateActionPlanRequest,

    UpdateActionStatusRequest,

    PersonalizedActionPlan,

    NoticeMetadata,

    WorkspaceTimelineReport,

)

from notice2action.ingestion import ingest_pasted_text, ingest_uploaded_file

from notice2action.security import validate_uploaded_file, SecurityValidationError

from notice2action.ocr import extract_text_from_image, get_ocr_engine

from notice2action.analysis import NoticeAnalyzer

from notice2action.summary import generate_deterministic_summary

from notice2action.checklist import generate_action_checklist

from notice2action.translation import (

    SUPPORTED_LANGUAGES,

    translate_summary,

    translate_checklist,

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

    LLMModelError,

)

from notice2action.services.evidence_service import evidence_service, EvidenceCitation

from notice2action.services.session_store import session_store, SessionState

from notice2action.storage.db import get_db

from notice2action.language_detection import detect_document_language

from notice2action.services.relationship_engine import relationship_engine

from notice2action.services.revision_engine import revision_engine

from notice2action.services.eligibility_engine import eligibility_engine

from notice2action.services.trust_engine import TrustEngine

from notice2action.services.impact_engine import PersonalImpactEngine

from notice2action.services.action_navigator_service import ActionNavigatorService

from notice2action.services.workspace_service import get_workspace

from notice2action.services.weekly_planner_service import weekly_planner

from notice2action.api.auth_routes import router as auth_router, get_current_user, get_current_user_or_guest

from notice2action.auth.auth_service import auth_service



logger = logging.getLogger("notice2action.api")



app = FastAPI(

    title="SuchnaSetu AI API",

    version="2.1.0",

    description="REST backend for SuchnaSetu AI Notice-to-Action Accessibility Assistant (PS02)",

)



# Authorized CORS origins configuration (Vite dev, local clients, and configured app URL)

app.add_middleware(

    CORSMiddleware,

    allow_origins=config.get_cors_origins(),

    allow_origin_regex=(

        r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+|169\.254\.\d+\.\d+)(:\d+)?$"

        if getattr(config, "app_env", "development").lower() != "production"

        else None

    ),

    allow_credentials=True,

    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],

    allow_headers=["*"],

)



# Structured Request ID and Redacted Audit Logging Middleware

@app.middleware("http")

async def request_id_and_audit_logging(request: Request, call_next):

    req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

    request.state.request_id = req_id

    t0 = time.time()

    

    # Safe redacted log of incoming request

    client_host = request.client.host if request.client else "unknown"

    query_str = str(request.url.query)

    if any(k in query_str.lower() for k in ("password", "token", "secret", "otp")):

        query_str = "[REDACTED_SENSITIVE_PARAMS]"

    

    logger.info(f"[{req_id}] -> {request.method} {request.url.path} from {client_host}")

    

    response = await call_next(request)

    duration_ms = (time.time() - t0) * 1000

    response.headers["X-Request-ID"] = req_id

    response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

    

    logger.info(f"[{req_id}] <- {response.status_code} {request.method} {request.url.path} in {duration_ms:.2f}ms")

    return response





def _is_private_dev_origin(origin: str) -> bool:

    """Verifies whether an origin originates from a private RFC1918 / link-local network during local dev."""

    try:

        from urllib.parse import urlparse

        import ipaddress

        parsed = urlparse(origin)

        hostname = parsed.hostname

        port = parsed.port or (443 if parsed.scheme == "https" else 80)

        if not hostname:

            return False

        if hostname in ("localhost", "127.0.0.1", "::1", "testserver"):

            return True

        ip = ipaddress.ip_address(hostname)

        return (ip.is_private or ip.is_loopback) and port in (5173, 8000, 3000)

    except Exception:

        return False





# CSRF and Trusted-Origin Protection Middleware for state-changing requests

@app.middleware("http")

async def verify_csrf_and_origin(request: Request, call_next):

    if request.method in ("POST", "PUT", "DELETE", "PATCH"):

        origin = request.headers.get("origin")

        if origin:

            trusted_origins = set(config.get_cors_origins())

            is_dev = getattr(config, "app_env", "development").lower() != "production"

            if origin.rstrip("/") not in trusted_origins and not (is_dev and _is_private_dev_origin(origin)):

                logger.warning(f"Blocked state-changing request from untrusted origin: {origin}")

                return JSONResponse(

                    status_code=403,

                    content={"detail": "Untrusted request origin / CSRF verification failed."}

                )

    return await call_next(request)



# Include Authentication Routes

app.include_router(auth_router)





# ---------------------------------------------------------

# Thread-Safe Analysis Cache & Configuration Locks

# ---------------------------------------------------------

_ANALYSIS_CACHE: Dict[str, StructuredNotice] = {}

_MAX_CACHE_ENTRIES = 64

_CACHE_LOCK = threading.Lock()

_PROVIDER_LOCK = threading.Lock()

_IN_FLIGHT_ANALYSES: Dict[str, Any] = {}

_IN_FLIGHT_LOCK = threading.Lock()





# ---------------------------------------------------------

# Centralized Error Handlers

# ---------------------------------------------------------



_ACTIVE_ANALYSIS_COUNTER = 0

_ACTIVE_COUNTER_LOCK = threading.Lock()





@app.exception_handler(LLMTimeoutError)

async def llm_timeout_handler(request: Request, exc: LLMTimeoutError):

    return JSONResponse(

        status_code=504,

        content={"detail": str(exc), "error_type": "model_timeout", "category": "model"},

    )





@app.exception_handler(LLMConfigError)

async def llm_config_error_handler(request: Request, exc: LLMConfigError):

    return JSONResponse(

        status_code=400,

        content={"detail": str(exc), "error_type": "model_config", "category": "model"},

    )





@app.exception_handler(LLMAuthError)

async def llm_auth_error_handler(request: Request, exc: LLMAuthError):

    return JSONResponse(

        status_code=401,

        content={"detail": str(exc), "error_type": "model_auth", "category": "model"},

    )





@app.exception_handler(LLMRateLimitError)

async def llm_rate_limit_handler(request: Request, exc: LLMRateLimitError):

    return JSONResponse(

        status_code=429,

        content={"detail": str(exc), "error_type": "model_rate_limit", "category": "model"},

    )





@app.exception_handler(LLMConnectionError)

async def llm_connection_handler(request: Request, exc: LLMConnectionError):

    return JSONResponse(

        status_code=503,

        content={"detail": str(exc), "error_type": "model_offline", "category": "model"},

    )





@app.exception_handler(LLMModelError)

async def llm_model_error_handler(request: Request, exc: LLMModelError):

    return JSONResponse(

        status_code=503,

        content={"detail": str(exc), "error_type": "model_missing", "category": "model"},

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

    document_id: Optional[str] = None





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

    raw_ocr_text: Optional[str] = None

    document_quality_score: Optional[float] = None

    deskew_angle: Optional[float] = None

    orientation_applied: Optional[int] = None

    uncertain_spans: Optional[List[Dict[str, Any]]] = None





class AnalyzeRequest(BaseModel):

    notice_text: str = Field(..., description="Notice text to analyze")

    source_language: Optional[str] = Field(default=None, description="Source document language (or None for auto-detect)")

    target_language: str = Field(default="en", description="Target language code: en, hi, bn, ta, te, mr, gu, pa, kn, ur")

    output_language: Optional[str] = Field(default=None, description="Alias for target_language")

    reading_level: str = Field(default="standard", description="'simple', 'standard', 'detailed'")

    session_id: Optional[str] = Field(default=None, description="Optional persistent session ID")

    provider: Optional[str] = Field(default=None, description="Optional LLM provider override")

    document_id: Optional[str] = Field(default=None, description="Optional persistent document ID")





class AnalyzeResponse(BaseModel):

    session_id: str

    document_id: Optional[str] = None

    source_language: str = "en"

    detected_language: str = "en"

    language_confidence: float = 1.0

    is_mixed_language: bool = False

    structured_notice: StructuredNotice

    six_core_fields: SixCoreFields

    summary_en: PlainLanguageSummary

    summary_hi: PlainLanguageSummary

    checklist_en: ActionChecklist

    checklist_hi: ActionChecklist

    target_language: str = "en"

    localized_summary: Optional[PlainLanguageSummary] = None

    localized_checklist: Optional[ActionChecklist] = None

    fingerprint: str

    duration_seconds: float





class ConfirmFactRequest(BaseModel):

    field_name: str = Field(..., description="Fact attribute being confirmed (e.g. 'deadline', 'notice_date')")

    confirmed_value: str = Field(..., description="User confirmed or corrected value")

    structured_notice: StructuredNotice = Field(..., description="Active structured notice")

    reading_level: str = Field(default="standard", description="'simple', 'standard', 'detailed'")

    target_language: str = Field(default="en", description="Target language code")

    session_id: Optional[str] = Field(default=None, description="Optional session ID")





class ConfirmFactResponse(BaseModel):

    structured_notice: StructuredNotice

    six_core_fields: SixCoreFields

    summary_en: PlainLanguageSummary

    summary_hi: PlainLanguageSummary

    checklist_en: ActionChecklist

    checklist_hi: ActionChecklist

    target_language: str = "en"

    localized_summary: Optional[PlainLanguageSummary] = None

    localized_checklist: Optional[ActionChecklist] = None





class ReadingLevelRequest(BaseModel):

    structured_notice: StructuredNotice

    reading_level: str = Field(default="standard", description="'simple', 'standard', 'detailed'")

    target_language: str = Field(default="en", description="Target language code: en, hi, bn, ta, te, mr, gu, pa, kn, ur")

    session_id: Optional[str] = Field(default=None, description="Optional active session ID to synchronize cached state")





class ReadingLevelResponse(BaseModel):

    summary_en: PlainLanguageSummary

    summary_hi: PlainLanguageSummary

    reading_level: str

    target_language: str = "en"

    localized_summary: Optional[PlainLanguageSummary] = None





class FollowUpRequest(BaseModel):

    question: str = Field(..., description="User's query")

    notice_text: str = Field(..., description="Active ground-truth notice text")

    session_id: Optional[str] = Field(default=None, description="Session ID for context isolation")

    target_language: str = Field(default="en", description="Target language code: en, hi, bn, ta, te, mr, gu, pa, kn, ur")





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

    allow_cloud: bool = Field(default=False, description="Set True to allow external Google TTS network requests")





class DetectRelationshipRequest(BaseModel):

    source_session_id: Optional[str] = None

    target_session_id: Optional[str] = None

    source_text: Optional[str] = None

    target_text: Optional[str] = None





class ExtractCriteriaRequest(BaseModel):

    session_id: Optional[str] = None

    notice_text: Optional[str] = None

    target_language: str = "en"

    output_language: Optional[str] = None





# ---------------------------------------------------------

# Health & Diagnostic Routes

# ---------------------------------------------------------



@app.get("/api/health")
def get_health() -> Dict[str, Any]:
    """Runs preflight diagnostics and returns system health status."""
    report = run_preflight_diagnostics()

    ollama_item = next((i for i in report.items if i.name == "Ollama Server"), None)
    tesseract_item = next((i for i in report.items if "Tesseract" in i.name), None)
    model_item = next(
        (i for i in report.items if "LLM Model" in i.name or "API Key" in i.name or "Token" in i.name),
        None,
    )

    ollama_connected = (ollama_item.status == "ok") if ollama_item else False
    tesseract_available = (tesseract_item.status == "ok") if tesseract_item else False
    model_ready = (model_item.status == "ok") if model_item else False

    return {
        "overall_status": report.overall_status,
        "active_provider": config.llm_provider,
        "model_name": config.ollama_model if config.llm_provider == "ollama" else getattr(config, f"{config.llm_provider}_model", "unknown"),
        "is_ready_for_inference": report.is_ready_for_inference(),
        "ollama_connected": ollama_connected,
        "tesseract_available": tesseract_available,
        "model_ready": model_ready,
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

    """Selects the active LLM provider for subsequent inference operations (thread-safe)."""

    prov = payload.provider.lower().strip()

    valid = ["ollama", "openrouter", "gemini", "huggingface"]

    if prov not in valid:

        raise HTTPException(

            status_code=400,

            detail=f"Invalid provider '{prov}'. Valid providers: {', '.join(valid)}"

        )



    with _PROVIDER_LOCK:

        config.llm_provider = prov



    client = get_llm_client(prov)

    health = client.check_health()

    return {

        "active_provider": prov,

        "status": health,

    }





# ---------------------------------------------------------

# Local Model Lifecycle Management (Ollama)

# ---------------------------------------------------------



@app.get("/api/models/status")

def get_models_status() -> Dict[str, Any]:

    """Retrieves real-time RAM/VRAM resource allocation and loaded model info from Ollama."""

    client = get_llm_client("ollama")

    loaded = client.get_loaded_models() if hasattr(client, "get_loaded_models") else []

    return {

        "provider": "ollama",

        "target_model": config.ollama_model,

        "loaded_models_count": len(loaded),

        "loaded_models": loaded,

    }





@app.post("/api/models/warmup")

def warmup_model_endpoint() -> Dict[str, Any]:

    """Preloads model weights into RAM/VRAM to eliminate cold-start delay during demos."""

    client = get_llm_client("ollama")

    if hasattr(client, "warmup"):

        return client.warmup()

    return {"success": False, "message": "Provider does not support local warmup."}





@app.post("/api/models/unload")

def unload_model_endpoint() -> Dict[str, Any]:

    """Unloads model weights from RAM/VRAM to immediately free system memory."""

    client = get_llm_client("ollama")

    if hasattr(client, "unload_model"):

        res = client.unload_model()

        if isinstance(res, dict):

            return res

        return {

            "success": bool(res),

            "unloaded": bool(res),

            "model": getattr(client, "model", config.ollama_model),

            "message": "Model unloaded from memory." if res else "Failed to unload model.",

        }

    return {"success": False, "message": "Provider does not support local unload."}





# ---------------------------------------------------------

# Sample Notice Fixtures

# ---------------------------------------------------------



@app.get("/api/samples")

def list_samples() -> List[Dict[str, str]]:

    """Lists available synthetic demo fixtures and sample notices."""

    return [

        {

            "id": "demo_upsc_scholarship.txt",

            "title": "📜 Base Notice: National Merit Scholarship 2026",

            "type": "text",

            "language": "en",

        },

        {

            "id": "demo_upsc_corrigendum.txt",

            "title": "📑 Corrigendum: Deadline Extension & OBC Quota",

            "type": "text",

            "language": "en",

        },

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



    # Detect language and save to SQLite

    det = detect_document_language(raw_text)

    db_doc = get_db().save_document(

        raw_text=raw_text,

        filename="pasted_notice.txt",

        source_language=det.detected_language,

        detected_language=det.detected_language,

        language_confidence=det.confidence,

        is_mixed_language=det.is_mixed,

    )



    return IngestTextResponse(

        raw_text=raw_text,

        char_count=len(raw_text),

        line_count=line_count,

        security_warning=res.security_warning,

        fingerprint=fp,

        document_id=db_doc.id,

    )





@app.post("/api/ingest/upload")

async def ingest_upload_endpoint(file: UploadFile = File(...)):

    """Uploads and validates a document (text or image)."""

    max_bytes = config.max_upload_size_mb * 1024 * 1024

    if file.size and file.size > max_bytes:

        raise HTTPException(

            status_code=413,

            detail=f"File size exceeds maximum allowed limit of {config.max_upload_size_mb} MB."

        )

    file_bytes = await file.read()

    if len(file_bytes) > max_bytes:

        raise HTTPException(

            status_code=413,

            detail=f"File size exceeds maximum allowed limit of {config.max_upload_size_mb} MB."

        )

    res = ingest_uploaded_file(file.filename or "uploaded_notice", file_bytes)



    if res.error:

        raise HTTPException(status_code=400, detail=res.error)



    if res.source_type in ["text", "pdf", "docx"]:

        raw_text = res.raw_text or ""

        fp = hashlib.sha256(raw_text.strip().encode("utf-8")).hexdigest()

        evidence_service.index_notice(raw_text)

        det = detect_document_language(raw_text)

        mime_map = {

            "pdf": "application/pdf",

            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",

            "text": "text/plain",

        }

        detected_mime = mime_map.get(res.source_type, f"application/{res.source_type}")

        doc_mime = file.content_type if (file.content_type and file.content_type != "application/octet-stream") else detected_mime



        db_doc = get_db().save_document(

            raw_text=raw_text,

            filename=res.filename or "uploaded_notice",

            content_bytes=file_bytes,

            mime_type=doc_mime,

            source_language=det.detected_language,

            detected_language=det.detected_language,

            language_confidence=det.confidence,

            is_mixed_language=det.is_mixed,

        )

        return {

            "document_id": db_doc.id,

            "source_type": res.source_type,

            "filename": res.filename,

            "raw_text": raw_text,

            "char_count": len(raw_text),

            "line_count": len(raw_text.splitlines()),

            "security_warning": res.security_warning,

            "fingerprint": fp,

            "detected_language": det.detected_language,

            "language_name": det.language_name,

            "native_name": det.native_name,

            "language_confidence": det.confidence,

            "is_mixed_language": det.is_mixed,

            "script_distribution": det.script_distribution,

        }

    else:

        db_doc = get_db().save_document(

            raw_text="",

            filename=res.filename or "uploaded_image",

            content_bytes=file_bytes,

            mime_type=file.content_type or "image/png",

            source_language="en",

            detected_language="en",

        )

        return {

            "document_id": db_doc.id,

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

    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),

):

    """Executes OCR on an uploaded image with selected engine asynchronously."""

    client_ip = current_user.get("client_ip") or "unknown"

    is_authenticated = not bool(current_user.get("is_guest", True))

    allowed, remaining = auth_service.check_ocr_rate_limit(client_ip, is_authenticated=is_authenticated)

    if not allowed:

        raise HTTPException(

            status_code=429,

            detail="OCR request rate limit exceeded. Please wait a moment before extracting another document.",

        )

    max_bytes = config.max_upload_size_mb * 1024 * 1024

    if file.size and file.size > max_bytes:

        raise HTTPException(

            status_code=413,

            detail=f"File size exceeds maximum allowed limit of {config.max_upload_size_mb} MB."

        )

    content = await file.read()

    if len(content) > max_bytes:

        raise HTTPException(

            status_code=413,

            detail=f"File size exceeds maximum allowed limit of {config.max_upload_size_mb} MB."

        )

    if len(content) == 0:

        raise HTTPException(status_code=400, detail="The uploaded file is empty (0 bytes).")



    try:

        safe_name, file_type = validate_uploaded_file(file.filename or "image.png", content)

        if file_type != "image":

            raise HTTPException(

                status_code=400,

                detail=f"Uploaded file for OCR must be an image format (PNG, JPG, WEBP, TIFF). Detected: {file_type}"

            )

        img = Image.open(io.BytesIO(content)).convert("RGB")

    except HTTPException:

        raise

    except SecurityValidationError as e:

        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:

        raise HTTPException(status_code=400, detail=f"Invalid image file: {e}")



    lang_code = "hin" if "hin" in target_lang and "+" not in target_lang else ("eng+hin" if "+" in target_lang else "eng")



    # Run blocking OCR extraction in threadpool

    ocr_res = await asyncio.to_thread(

        extract_text_from_image,

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

        raw_ocr_text=ocr_res.raw_ocr_text,

        document_quality_score=ocr_res.document_quality_score,

        deskew_angle=ocr_res.deskew_angle,

        orientation_applied=ocr_res.orientation_applied,

        uncertain_spans=ocr_res.uncertain_spans,

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

async def analyze_endpoint(

    payload: AnalyzeRequest,

    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),

):

    """Executes the full structured analysis pipeline using the configured LLM asynchronously."""

    # Guest quota consumption: only consumed if text validation passes

    client_ip = current_user.get("client_ip") or "unknown"

    is_guest = bool(current_user.get("is_guest"))

    text = payload.notice_text.strip()

    if not text:

        raise HTTPException(status_code=422, detail="Notice text cannot be empty.")



    if is_guest:

        allowed, remaining = auth_service.consume_guest_quota(client_ip)

        if not allowed:

            raise HTTPException(

                status_code=429,

                detail="Guest notice analysis quota exceeded (10 notices per 10 minutes). Please sign in or register for unlimited citizen access.",

            )



    global _ACTIVE_ANALYSIS_COUNTER

    with _ACTIVE_COUNTER_LOCK:

        _ACTIVE_ANALYSIS_COUNTER += 1



    start_time = time.time()

    custom_client = get_llm_client(payload.provider) if payload.provider else None

    analyzer = NoticeAnalyzer(client=custom_client)



    try:

        # Index document in EvidenceService

        evidence_service.index_notice(text)

        fp = hashlib.sha256(text.encode("utf-8")).hexdigest()

        req_lang = (payload.output_language or payload.target_language or "en").lower().strip()

        src_lang_req = (payload.source_language or "").lower().strip() or None

        cache_key = f"{fp}:{req_lang}:{payload.reading_level}:{payload.provider or config.llm_provider}"



        # Thread-safe LRU cache check

        with _CACHE_LOCK:

            cached = _ANALYSIS_CACHE.get(cache_key)

            if cached:

                structured = cached.model_copy(deep=True)

            else:

                structured = None



        if structured is None:

            task = None

            is_creator = False

            with _IN_FLIGHT_LOCK:

                if cache_key in _IN_FLIGHT_ANALYSES:

                    task = _IN_FLIGHT_ANALYSES[cache_key]

                else:

                    task = asyncio.create_task(asyncio.to_thread(analyzer.analyze_notice, text, target_lang=req_lang, source_lang=src_lang_req))

                    _IN_FLIGHT_ANALYSES[cache_key] = task

                    is_creator = True



            try:

                res = await asyncio.shield(task)

                structured = res.model_copy(deep=True)

                if is_creator:

                    with _CACHE_LOCK:

                        if len(_ANALYSIS_CACHE) >= _MAX_CACHE_ENTRIES:

                            _ANALYSIS_CACHE.pop(next(iter(_ANALYSIS_CACHE)), None)

                        _ANALYSIS_CACHE[cache_key] = structured.model_copy(deep=True)

            finally:

                if is_creator:

                    with _IN_FLIGHT_LOCK:

                        _IN_FLIGHT_ANALYSES.pop(cache_key, None)



        six_core = structured.to_six_core_fields()



        # Summaries & Checklists (deterministic, fast)

        summary_en = generate_deterministic_summary(structured, reading_level=payload.reading_level, target_lang="en")

        checklist_en = generate_action_checklist(structured)



        # Bilingual translations

        summary_hi = generate_deterministic_summary(structured, reading_level=payload.reading_level, target_lang="hi")

        checklist_hi = translate_checklist(checklist_en, target_lang="hi", client=custom_client)



        # Localized target language translations

        if req_lang == "hi":

            localized_summary = summary_hi

            localized_checklist = checklist_hi

        elif req_lang == "en":

            localized_summary = summary_en

            localized_checklist = checklist_en

        else:

            localized_summary = translate_summary(summary_en, target_lang=req_lang, client=custom_client)

            localized_checklist = translate_checklist(checklist_en, target_lang=req_lang, client=custom_client)



        duration = time.time() - start_time



        # Create or update session state

        s_id = payload.session_id or str(uuid.uuid4())

        session_store.update_session(s_id, {

            "raw_notice_text": text,

            "fingerprint": fp,

            "reading_level": payload.reading_level,

            "target_language": req_lang,

            "structured_notice": structured.model_dump(),

            "summary_en": summary_en.model_dump(),

            "summary_hi": summary_hi.model_dump(),

            "checklist_en": checklist_en.model_dump(),

            "checklist_hi": checklist_hi.model_dump(),

            "localized_summary": localized_summary.model_dump(),

            "localized_checklist": localized_checklist.model_dump(),

        })



        # Detect source language if not provided

        det = detect_document_language(text)

        src_lang = (payload.source_language or det.detected_language).lower().strip()

        

        # Save analysis & checklist persistently in SQLite

        db = get_db()

        db_doc = db.save_document(

            raw_text=text,

            filename="notice.txt",

            source_language=src_lang,

            detected_language=det.detected_language,

            language_confidence=det.confidence,

            is_mixed_language=det.is_mixed,

            doc_id=payload.document_id,

        )

        db.save_analysis(

            session_id=s_id,

            fingerprint=fp,

            structured_notice=structured.model_dump(),

            six_core_fields=six_core.model_dump(),

            summary=localized_summary.model_dump(),

            action_checklist=localized_checklist.model_dump(),

            document_id=db_doc.id,

            reading_level=payload.reading_level,

            source_language=src_lang,

            output_language=req_lang,

            model_used=payload.provider or config.llm_provider,

            inference_duration=duration,

        )



        # Audit user activity

        if current_user and current_user.get("id"):

            sub_val = structured.main_subject.value if structured.main_subject else "Official Notice"

            db.record_activity(

                user_id=current_user["id"],

                activity_type="notice_analyzed",

                title=f"Analyzed Notice: {sub_val[:60]}",

                description=f"Extracted grounded facts and {len(checklist_en.items)} action items.",

                document_id=db_doc.id,

            )



        return AnalyzeResponse(

            session_id=s_id,

            document_id=db_doc.id,

            source_language=src_lang,

            detected_language=det.detected_language,

            language_confidence=det.confidence,

            is_mixed_language=det.is_mixed,

            structured_notice=structured,

            six_core_fields=six_core,

            summary_en=summary_en,

            summary_hi=summary_hi,

            checklist_en=checklist_en,

            checklist_hi=checklist_hi,

            target_language=req_lang,

            localized_summary=localized_summary,

            localized_checklist=localized_checklist,

            fingerprint=fp,

            duration_seconds=round(duration, 2),

        )

    except (LLMConnectionError, LLMModelError):

        if is_guest:

            auth_service.refund_guest_quota(client_ip)

        raise

    except (LLMConfigError, LLMAuthError, LLMRateLimitError, LLMTimeoutError):

        raise

    except Exception as e:

        if is_guest:

            auth_service.refund_guest_quota(client_ip)

        logger.error(f"Analysis pipeline error: {e}", exc_info=True)

        raise HTTPException(

            status_code=500,

            detail=f"Analysis pipeline error: {e}. Active provider: '{config.llm_provider}'",

        )

    finally:

        with _ACTIVE_COUNTER_LOCK:

            _ACTIVE_ANALYSIS_COUNTER = max(0, _ACTIVE_ANALYSIS_COUNTER - 1)





@app.get("/api/status/active-requests")

def get_active_requests_status():

    """Returns the count of in-flight analysis requests."""

    with _ACTIVE_COUNTER_LOCK:

        return {"active_requests": _ACTIVE_ANALYSIS_COUNTER}





@app.post("/api/ollama/unload")

def unload_ollama_endpoint():

    """Explicitly unloads the Ollama model from VRAM/RAM if no analyses are active."""

    with _ACTIVE_COUNTER_LOCK:

        if _ACTIVE_ANALYSIS_COUNTER > 0:

            raise HTTPException(status_code=409, detail="Cannot unload model while analysis is in progress.")

    client = get_llm_client("ollama")

    if hasattr(client, "unload_model"):

        success = client.unload_model()

        return {"status": "ok", "unloaded": success}

    return {"status": "skipped", "message": "Client does not support explicit unload"}





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

    summary_hi = translate_summary(summary_en, target_lang="hi", client=None)

    checklist_hi = translate_checklist(checklist_en, target_lang="hi", client=None)



    req_lang = payload.target_language.lower().strip() if payload.target_language else "en"

    localized_summary = translate_summary(summary_en, target_lang=req_lang, client=None)

    localized_checklist = translate_checklist(checklist_en, target_lang=req_lang, client=None)



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

        target_language=req_lang,

        localized_summary=localized_summary,

        localized_checklist=localized_checklist,

    )





@app.get("/api/languages")

def get_languages_endpoint():

    """Returns the list of 10 supported Indian official languages with metadata."""

    return {"languages": SUPPORTED_LANGUAGES}





@app.post("/api/summary/reading-level", response_model=ReadingLevelResponse)

def reading_level_endpoint(payload: ReadingLevelRequest):

    """Generates plain language summary tailored to the requested reading level."""

    lvl = payload.reading_level.lower().strip()

    if lvl not in ["simple", "standard", "detailed"]:

        lvl = "standard"

    req_lang = (payload.target_language or "en").lower().strip()

    summary_en = generate_deterministic_summary(payload.structured_notice, reading_level=lvl, target_lang="en")

    summary_hi = generate_deterministic_summary(payload.structured_notice, reading_level=lvl, target_lang="hi")

    if req_lang == "hi":

        localized_summary = summary_hi

    elif req_lang == "en":

        localized_summary = summary_en

    else:

        localized_summary = translate_summary(summary_en, target_lang=req_lang, client=None)



    # Invalidate/update session store cache for this reading level

    if payload.session_id:

        sess = session_store.get_session(payload.session_id)

        if sess:

            session_store.update_session(payload.session_id, {

                "reading_level": lvl,

                "summary_en": summary_en.model_dump(),

                "summary_hi": summary_hi.model_dump(),

                "localized_summary": localized_summary.model_dump() if localized_summary else None,

                "target_language": req_lang,

            })



    return ReadingLevelResponse(

        summary_en=summary_en,

        summary_hi=summary_hi,

        reading_level=lvl,

        target_language=req_lang,

        localized_summary=localized_summary,

    )





@app.post("/api/followup", response_model=FollowUpAnswer)

async def followup_endpoint(

    payload: FollowUpRequest,

    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),

):

    """Answers follow-up queries grounded strictly within the active notice text asynchronously."""

    client_ip = current_user.get("client_ip") or "unknown"

    is_guest = bool(current_user.get("is_guest"))

    if is_guest:

        allowed, remaining = auth_service.check_guest_rate_limit(client_ip, increment=False)

        if not allowed:

            raise HTTPException(

                status_code=429,

                detail="Guest follow-up quota exceeded. Please sign in or register for unlimited citizen access.",

            )



    q = payload.question.strip()

    text = payload.notice_text.strip()



    if not q:

        raise HTTPException(status_code=422, detail="Question cannot be empty.")

    if not text:

        raise HTTPException(status_code=422, detail="Notice text cannot be empty.")



    assistant = FollowUpAssistant()

    answer = await asyncio.to_thread(assistant.answer_question, q, text, target_lang=payload.target_language)



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

@app.post("/api/actions/export-calendar")

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

    """

    Generates MP3 audio for text read-aloud via gTTS ONLY when allow_cloud is True.

    By default (allow_cloud=False), returns 204 No Content to guarantee local air-gapped privacy.

    """

    audio_bytes = generate_audio_bytes(payload.text, lang=payload.lang, allow_cloud_tts=payload.allow_cloud)

    if audio_bytes is None:

        return Response(status_code=204)



    return Response(

        content=audio_bytes,

        media_type="audio/mpeg",

        headers={"Content-Disposition": 'inline; filename="read_aloud.mp3"'},

    )





# ---------------------------------------------------------

# Multi-Notice Revision Ledger Endpoints

# ---------------------------------------------------------



@app.post("/api/relationships/detect", response_model=NoticeRelationship)

async def detect_relationship_endpoint(payload: DetectRelationshipRequest):

    """Detects official relationship (AMENDMENT, EXTENSION, CANCELLATION, etc.) between two notices."""

    src_text = payload.source_text or ""

    tgt_text = payload.target_text or ""

    src_id = payload.source_session_id or "notice_a"

    tgt_id = payload.target_session_id or "notice_b"



    if payload.source_session_id and not src_text:

        sess = session_store.get_session(payload.source_session_id)

        if sess:

            src_text = sess.raw_notice_text

    if payload.target_session_id and not tgt_text:

        sess = session_store.get_session(payload.target_session_id)

        if sess:

            tgt_text = sess.raw_notice_text



    if not src_text and not tgt_text:

        raise HTTPException(status_code=422, detail="Notice texts or valid session IDs must be provided.")



    return await asyncio.to_thread(

        relationship_engine.detect_relationship,

        src_id,

        tgt_id,

        src_text,

        tgt_text,

    )





@app.post("/api/revision-ledger/compare", response_model=RevisionLedger)

@app.post("/api/compare/revisions", response_model=RevisionLedger)

async def compare_revision_ledger_endpoint(payload: CompareNoticesRequest):

    """

    Compares two notice versions field-by-field, producing an auditable revision ledger.

    Accepts either session IDs or raw notice texts.

    """

    src_text = payload.source_text or ""

    tgt_text = payload.target_text or ""

    src_id = payload.source_session_id or "original_notice"

    tgt_id = payload.target_session_id or "revised_notice"

    src_notice = None

    tgt_notice = None



    if payload.source_session_id:

        sess = session_store.get_session(payload.source_session_id)

        if sess:

            src_text = src_text or sess.raw_notice_text

            if sess.structured_notice:

                try:

                    src_notice = StructuredNotice.model_validate(sess.structured_notice)

                except Exception:

                    pass



    if payload.target_session_id:

        sess = session_store.get_session(payload.target_session_id)

        if sess:

            tgt_text = tgt_text or sess.raw_notice_text

            if sess.structured_notice:

                try:

                    tgt_notice = StructuredNotice.model_validate(sess.structured_notice)

                except Exception:

                    pass



    analyzer = NoticeAnalyzer()

    if src_notice is None:

        if not src_text.strip():

            raise HTTPException(status_code=422, detail="Original notice text or session ID is required.")

        src_notice = await asyncio.to_thread(analyzer.analyze_notice, src_text.strip())



    if tgt_notice is None:

        if not tgt_text.strip():

            raise HTTPException(status_code=422, detail="Revised notice text or session ID is required.")

        tgt_notice = await asyncio.to_thread(analyzer.analyze_notice, tgt_text.strip())



    req_lang = (payload.output_language or payload.target_language or "en").lower().strip()

    return await asyncio.to_thread(

        revision_engine.build_revision_ledger,

        source_id=src_id,

        target_id=tgt_id,

        source_notice=src_notice,

        target_notice=tgt_notice,

        source_raw_text=src_text,

        target_raw_text=tgt_text,

        target_language=req_lang,

    )





# ---------------------------------------------------------

# Explainable Applicant Eligibility Engine Endpoints

# ---------------------------------------------------------



@app.post("/api/eligibility/extract-criteria", response_model=List[EligibilityCriterion])

async def extract_criteria_endpoint(payload: ExtractCriteriaRequest):

    """Extracts machine-evaluable eligibility criteria from an analyzed notice or raw text."""

    notice = None

    if payload.session_id:

        sess = session_store.get_session(payload.session_id)

        if sess and sess.structured_notice:

            try:

                notice = StructuredNotice.model_validate(sess.structured_notice)

            except Exception:

                pass



    if notice is None:

        text = payload.notice_text or ""

        if not text.strip():

            raise HTTPException(status_code=422, detail="Session ID or notice text must be provided.")

        fp = hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

        cache_key = f"{fp}:{config.llm_provider}"

        with _CACHE_LOCK:

            cached = _ANALYSIS_CACHE.get(cache_key)

            if cached:

                notice = cached.model_copy(deep=True)

        if notice is None:

            analyzer = NoticeAnalyzer()

            notice = await asyncio.to_thread(analyzer.analyze_notice, text.strip())



    return eligibility_engine.extract_criteria(notice)





@app.post("/api/eligibility/evaluate", response_model=EligibilityAssessment)

@app.post("/api/eligibility/check", response_model=EligibilityAssessment)

async def evaluate_eligibility_endpoint(payload: EvaluateEligibilityRequest):

    """

    Evaluates an applicant profile deterministically against notice criteria.

    Returns PASS, FAIL, or UNKNOWN with verbatim citations.

    """

    notice = None

    if payload.session_id:

        sess = session_store.get_session(payload.session_id)

        if sess and sess.structured_notice:

            try:

                notice = StructuredNotice.model_validate(sess.structured_notice)

            except Exception:

                pass



    if notice is None:

        text = payload.notice_text or ""

        if not text.strip():

            raise HTTPException(status_code=422, detail="Session ID or notice text must be provided.")

        fp = hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

        cache_key = f"{fp}:{config.llm_provider}"

        with _CACHE_LOCK:

            cached = _ANALYSIS_CACHE.get(cache_key)

            if cached:

                notice = cached.model_copy(deep=True)

        if notice is None:

            analyzer = NoticeAnalyzer()

            notice = await asyncio.to_thread(analyzer.analyze_notice, text.strip())



    criteria = eligibility_engine.extract_criteria(notice)

    req_lang = (payload.output_language or payload.target_language or "en").lower().strip()

    return eligibility_engine.evaluate_profile(

        criteria=criteria,

        profile=payload.applicant_profile,

        session_id=payload.session_id,

        target_language=req_lang,

    )





# ---------------------------------------------------------

# Feature 1: Evidence-First Trust Engine Endpoints

# ---------------------------------------------------------



@app.post("/api/trust/verify-evidence", response_model=VerifyEvidenceResponse)

async def verify_evidence_endpoint(payload: VerifyEvidenceRequest):

    """

    Validates whether an excerpt is legitimately grounded in source notice text.

    Returns verification status (VERIFIED, UNCERTAIN_OCR, or UNVERIFIED) with line attribution.

    """

    return TrustEngine.verify_excerpt(

        source_text=payload.notice_text,

        excerpt=payload.excerpt,

        claim_text=payload.claim_text or "",

        source_doc_title=payload.source_doc_title or "Active Notice",

    )





# ---------------------------------------------------------

# Feature 2: Personal Impact Change Tracker Endpoints

# ---------------------------------------------------------



@app.post("/api/impact/evaluate", response_model=PersonalImpactReport)

async def evaluate_personal_impact_endpoint(payload: EvaluatePersonalImpactRequest):

    """

    Evaluates how notice amendments impact an applicant's specific profile,

    identifying deadline extensions, fee reductions, and qualification shifts.

    """

    return await asyncio.to_thread(

        PersonalImpactEngine.evaluate_impact,

        ledger=payload.revision_ledger,

        source_text=payload.source_text,

        target_text=payload.target_text,

        profile=payload.applicant_profile,

    )





# ---------------------------------------------------------

# Feature 3: Personalized Action Navigator Endpoints

# ---------------------------------------------------------



@app.post("/api/actions/generate", response_model=PersonalizedActionPlan)

async def generate_action_plan_endpoint(payload: GenerateActionPlanRequest):

    """

    Synthesizes a structured, dependency-aware action roadmap based on notice facts,

    applicant profile, and eligibility assessment.

    """

    notice_text = payload.notice_text or ""

    if payload.session_id and not notice_text:

        sess = session_store.get_session(payload.session_id)

        if sess:

            notice_text = sess.raw_notice_text



    if not notice_text.strip():

        raise HTTPException(status_code=422, detail="Notice text or valid session ID must be provided.")



    req_lang = (payload.output_language or payload.target_language or "en").lower().strip()

    return await asyncio.to_thread(

        ActionNavigatorService.generate_plan,

        notice_text=notice_text,

        session_id=payload.session_id,

        profile=payload.applicant_profile,

        eligibility=payload.eligibility_assessment,

        revision_ledger=payload.revision_ledger,

        target_language=req_lang,

    )





class UpdateActionItemRequest(BaseModel):

    plan: PersonalizedActionPlan

    action_id: str

    status: str

    user_notes: Optional[str] = None





@app.post("/api/actions/update-status", response_model=PersonalizedActionPlan)

def update_action_status_endpoint(payload: UpdateActionItemRequest):

    """Updates the completion or verification status of an action item in the plan."""

    from notice2action.schemas import ActionItemStatus

    try:

        new_status = ActionItemStatus(payload.status)

    except ValueError:

        raise HTTPException(status_code=422, detail=f"Invalid status: {payload.status}")



    return ActionNavigatorService.update_item_status(

        plan=payload.plan,

        action_id=payload.action_id,

        new_status=new_status,

        user_notes=payload.user_notes,

    )





# ---------------------------------------------------------

# Feature 4: Cross-Notice Intelligence & Workspace Endpoints

# ---------------------------------------------------------



class AddWorkspaceNoticeRequest(BaseModel):

    text: str

    title: Optional[str] = None

    doc_id: Optional[str] = None





@app.get("/api/workspace/notices", response_model=List[NoticeMetadata])

def get_workspace_notices_endpoint():

    """Lists all notices registered in the active workspace."""

    return get_workspace().get_notices()





@app.post("/api/workspace/notices", response_model=NoticeMetadata)

def add_workspace_notice_endpoint(payload: AddWorkspaceNoticeRequest):

    """Registers a notice into the multi-document workspace."""

    if not payload.text.strip():

        raise HTTPException(status_code=422, detail="Notice text cannot be empty.")

    return get_workspace().add_notice(text=payload.text, title=payload.title, doc_id=payload.doc_id)





@app.get("/api/workspace/timeline", response_model=WorkspaceTimelineReport)

def get_workspace_timeline_endpoint(active_id: Optional[str] = None):

    """Generates cross-notice timeline, relationships, and conflict report across workspace notices."""

    return get_workspace().build_report(active_notice_id=active_id)





@app.post("/api/workspace/clear")

def clear_workspace_endpoint():

    """Clears all notices from the workspace."""

    get_workspace().clear()

    return {"status": "ok", "message": "Workspace cleared."}







# ---------------------------------------------------------

# Feature: Judge-Ready Demo Library & Persistent Storage Routes

# ---------------------------------------------------------



@app.get("/api/demo-library")

def get_demo_library_endpoint(

    category: Optional[str] = None,

    source_lang: Optional[str] = None,

    format_type: Optional[str] = None,

    search: Optional[str] = None,

):

    """Returns the persistent demo library catalog from SQLite demo_registry."""

    return get_db().list_demos(

        category=category,

        source_lang=source_lang,

        format_type=format_type,

        search_query=search,

    )





@app.post("/api/demo-library/{demo_id}/load")

def load_demo_library_item_endpoint(demo_id: str):

    """Loads an actual version-controlled demo file and runs the ingestion pipeline."""

    demos = get_db().list_demos()

    matched = next((d for d in demos if d["id"] == demo_id), None)

    if not matched:

        raise HTTPException(status_code=404, detail=f"Demo '{demo_id}' not found in registry.")



    source_rel = matched["source_file"]

    file_path = PROJECT_ROOT / "tests" / "fixtures" / "demo_library" / source_rel

    if not file_path.is_file():

        raise HTTPException(status_code=404, detail=f"Demo file not found on disk at {file_path}")



    file_bytes = file_path.read_bytes()

    filename = file_path.name

    res = ingest_uploaded_file(filename, file_bytes)



    raw_text = res.raw_text or ""

    fp = hashlib.sha256(raw_text.strip().encode("utf-8")).hexdigest() if raw_text else ""

    if raw_text:

        evidence_service.index_notice(raw_text)



    det = detect_document_language(raw_text) if raw_text else None



    # Persist in SQLite

    doc_rec = get_db().save_document(

        raw_text=raw_text,

        filename=filename,

        content_bytes=file_bytes,

        source_language=matched["source_lang"],

        detected_language=det.detected_language if det else matched["source_lang"],

        language_confidence=det.confidence if det else 1.0,

        is_mixed_language=det.is_mixed if det else False,

    )



    return {

        "demo_id": demo_id,

        "title": matched["title"],

        "category": matched["category"],

        "format": matched["format"],

        "source_language": matched["source_lang"],

        "suggested_output_language": matched["target_lang"],

        "is_synthetic": matched["is_synthetic"],

        "document_id": doc_rec.id,

        "raw_text": raw_text,

        "fingerprint": fp,

        "char_count": len(raw_text),

        "line_count": len(raw_text.splitlines()),

        "ground_truth": matched["manifest_data"].get("ground_truth"),

        "expected_key_actions": matched["manifest_data"].get("expected_key_actions"),

        "edge_case_flags": matched["manifest_data"].get("edge_case_flags"),

        "detected_language": det.to_dict() if det else None,

    }





@app.post("/api/language/detect")

def detect_language_endpoint(payload: Dict[str, Any]):

    """Detects document language across all 10 supported constitutional languages."""

    text = str(payload.get("text", "")).strip()

    if not text:

        raise HTTPException(status_code=422, detail="Text cannot be empty.")

    det = detect_document_language(text)

    return det.to_dict()





@app.get("/api/documents")

def list_saved_documents_endpoint(limit: int = 50, offset: int = 0):

    """Lists saved documents from the SQLite database."""

    docs = get_db().list_documents(limit=limit, offset=offset)

    return [d.to_dict() for d in docs]





@app.post("/api/checklist/{item_id}/toggle")
def toggle_checklist_item_endpoint(item_id: str, payload: Dict[str, Any]):
    """Persistently updates the completion state of an action checklist item in SQLite."""
    completed = bool(payload.get("completed", payload.get("is_completed", False)))
    ok = get_db().set_checklist_item_completed(item_id, completed)
    return {
        "item_id": item_id,
        "completed": completed,
        "is_completed": completed,
        "success": ok,
        "updated": ok,
    }





# ---------------------------------------------------------

# Feature: User-Isolated Saved Notices & Weekly Action Planner

# ---------------------------------------------------------



@app.get("/api/user/saved-notices")

async def list_user_saved_notices(

    q: Optional[str] = None,

    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),

):

    """Retrieves all saved notices belonging strictly to the current user/guest."""

    user_id = current_user["id"]

    return get_db().list_saved_notices_for_user(user_id=user_id, search_query=q)





@app.post("/api/user/saved-notices/{document_id}")

async def save_notice_for_current_user(

    document_id: str,

    payload: Dict[str, Any],

    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),

):

    """Saves a notice for the current user/guest with parsed assignment and deadline."""

    user_id = current_user["id"]

    title = payload.get("title") or "Notice"

    authority = payload.get("authority") or ""

    deadline = payload.get("deadline") or ""

    raw_text = payload.get("raw_text") or ""

    assignment_title = payload.get("assignment_title") or title

    submission_date = payload.get("submission_date") or deadline



    parsed_d, is_amb, amb_reason = weekly_planner.parse_deadline_and_ambiguity(deadline or submission_date)



    saved = get_db().save_notice_for_user(

        user_id=user_id,

        document_id=document_id,

        title=title,

        authority=authority,

        deadline=deadline,

        raw_text=raw_text,

        assignment_title=assignment_title,

        submission_date=parsed_d.isoformat() if parsed_d else submission_date,

        is_ambiguous_date=is_amb,

    )

    get_db().record_activity(

        user_id=user_id,

        activity_type="notice_saved",

        title=f"Saved Notice: {title[:60]}",

        description=f"Added to personal tracker with deadline: {deadline or 'Not specified'}.",

        document_id=document_id,

    )

    if is_amb:

        get_db().create_notification(

            user_id=user_id,

            title="Unconfirmed Date in Saved Notice",

            message=f"'{title[:50]}' contains tentative date '{deadline}'. Please verify with official source.",

            type="warning",

            document_id=document_id,

        )

    return {"status": "success", "notice": saved}





@app.delete("/api/user/saved-notices/{document_id}")

async def unsave_notice_for_current_user(

    document_id: str,

    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),

):

    """Unsaves a notice for the current user/guest."""

    user_id = current_user["id"]

    ok = get_db().unsave_notice_for_user(user_id=user_id, document_id=document_id)

    if ok:

        get_db().record_activity(

            user_id=user_id,

            activity_type="notice_unsaved",

            title="Removed Notice",

            description=f"Removed document {document_id} from personal tracker.",

            document_id=document_id,

        )

    return {"status": "success", "removed": ok}





@app.get("/api/user/weekly-tasks")

async def get_weekly_tasks_endpoint(

    ref_date: Optional[str] = None,

    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),

):

    """

    Computes a 7-day chronological action planner for the current user's saved notices.

    Answers: 'What do I need to complete this week?'

    """

    user_id = current_user["id"]

    parsed_ref = None

    if ref_date:

        try:

            parsed_ref = datetime.strptime(ref_date, "%Y-%m-%d").date()

        except Exception:

            pass



    return weekly_planner.get_weekly_plan(user_id=user_id, reference_date=parsed_ref)





@app.post("/api/user/weekly-tasks/query")

async def query_weekly_tasks_endpoint(

    payload: Dict[str, Any],

    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),

):

    """Handles natural language task queries like 'What do I need to complete this week?'"""

    user_id = current_user["id"]

    query = payload.get("query", "").strip()

    plan = weekly_planner.get_weekly_plan(user_id=user_id)

    return {

        "query": query,

        "summary": plan["summary"],

        "due_this_week_count": plan["due_this_week_count"],

        "tasks": plan["due_this_week"],

        "ambiguous_tasks": plan["ambiguous_tasks"],

        "week_window": plan["week_window"],

    }





# ---------------------------------------------------------

# Feature: User Notifications & Activity Audit Trail

# ---------------------------------------------------------



@app.get("/api/user/notifications")

async def get_user_notifications_endpoint(

    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),

):

    """

    Retrieves active user notifications.

    Generates contextual notifications from saved notices or account status if none exist.

    """

    user_id = current_user["id"]

    db = get_db()

    notifs = db.list_notifications_for_user(user_id=user_id)



    if not notifs:

        try:

            plan = weekly_planner.get_weekly_plan(user_id=user_id)

            if plan.get("due_this_week_count", 0) > 0:

                first_task = plan["due_this_week"][0]

                db.create_notification(

                    user_id=user_id,

                    title="Upcoming Deadline This Week",

                    message=f"'{first_task['task_title']}' is due {first_task.get('parsed_date', 'soon')}. Check your action plan.",

                    type="deadline",

                    document_id=first_task.get("document_id"),

                )

            elif plan.get("total_saved_notices", 0) > 0:

                db.create_notification(

                    user_id=user_id,

                    title="All Deadlines on Track",

                    message=f"You have {plan['total_saved_notices']} saved notice(s) with no immediate deadlines due this week.",

                    type="info",

                )

            else:

                db.create_notification(

                    user_id=user_id,

                    title="Welcome to SuchnaSetu AI",

                    message="Ingest or upload official notices to automatically extract verified deadlines, eligibility criteria, and personalized checklists.",

                    type="system",

                )

            notifs = db.list_notifications_for_user(user_id=user_id)

        except Exception:

            pass



    unread_count = sum(1 for n in notifs if not n.get("is_read"))

    return {

        "notifications": notifs,

        "unread_count": unread_count,

        "total": len(notifs),

    }





@app.put("/api/user/notifications/{notification_id}/read")

async def mark_notification_read_endpoint(

    notification_id: str,

    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),

):

    """Marks a single notification as read."""

    user_id = current_user["id"]

    ok = get_db().mark_notification_read(user_id=user_id, notification_id=notification_id)

    return {"status": "success", "updated": ok}





@app.post("/api/user/notifications/mark-all-read")

async def mark_all_notifications_read_endpoint(

    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),

):

    """Marks all notifications as read for current user."""

    user_id = current_user["id"]

    count = get_db().mark_all_notifications_read(user_id=user_id)

    return {"status": "success", "marked_read": count}





@app.delete("/api/user/notifications/{notification_id}")

async def dismiss_notification_endpoint(

    notification_id: str,

    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),

):

    """Dismisses a notification."""

    user_id = current_user["id"]

    ok = get_db().dismiss_notification(user_id=user_id, notification_id=notification_id)

    return {"status": "success", "dismissed": ok}





@app.get("/api/user/activities")

async def get_user_activities_endpoint(

    limit: int = 20,

    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),

):

    """Retrieves chronological activity audit events for the current user."""

    user_id = current_user["id"]

    activities = get_db().list_activities_for_user(user_id=user_id, limit=limit)

    return activities





# ---------------------------------------------------------

# ---------------------------------------------------------
# Feature: Protected User Profile, Preferences & Checklist Progress
# ---------------------------------------------------------

@app.get("/api/user/profile")
async def get_user_profile_endpoint(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Returns strictly authenticated user profile. Rejects guests with HTTP 401."""
    return current_user


@app.get("/api/user/preferences")
async def get_user_preferences_endpoint(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Returns persistent user preferences (language, accessibility, theme) for authenticated user."""
    user_id = current_user["id"]
    prefs = get_db().get_user_preferences(user_id=user_id)
    return {"status": "success", "user_id": user_id, "preferences": prefs}


@app.put("/api/user/preferences")
async def update_user_preferences_endpoint(
    payload: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Persists user preferences across sessions for authenticated user."""
    user_id = current_user["id"]
    prefs = payload.get("preferences", payload)
    get_db().set_user_preferences(user_id=user_id, preferences=prefs)
    return {"status": "success", "user_id": user_id, "preferences": prefs}


@app.get("/api/user/checklist-progress")
async def get_user_checklist_progress_endpoint(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieves map of completed checklist tasks strictly isolated for current user."""
    user_id = current_user["id"]
    progress = get_db().get_user_checklist_progress(user_id=user_id)
    return {
        "status": "success",
        "user_id": user_id,
        "progress": progress,
        "checklist_progress": progress,
    }


@app.post("/api/user/checklist/{item_id}/toggle")
async def toggle_user_checklist_progress_endpoint(
    item_id: str,
    payload: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Persists checklist item completion state strictly under authenticated user ID."""
    user_id = current_user["id"]
    completed = bool(payload.get("completed", payload.get("is_completed", True)))
    get_db().set_user_checklist_progress(user_id=user_id, item_id=item_id, completed=completed)
    get_db().set_checklist_item_completed(item_id=item_id, completed=completed)
    return {
        "status": "success",
        "user_id": user_id,
        "item_id": item_id,
        "completed": completed,
        "is_completed": completed,
    }



# Feature: Production Frontend SPA Serving (Single-Port Deployment)

# ---------------------------------------------------------



frontend_dist = PROJECT_ROOT / "frontend" / "dist"

if (frontend_dist / "assets").is_dir():

    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="frontend-assets")





@app.get("/{full_path:path}", include_in_schema=False)

async def serve_spa_frontend(request: Request, full_path: str):

    """

    Serves the compiled React 19 SPA for client-side routing in production.

    Never intercepts /api/*, /docs, /redoc, or /openapi.json.

    """

    clean_path = full_path.lstrip("/")



    # Security check: Never serve sensitive paths or path traversal attempts

    if ".." in full_path or clean_path.startswith("etc") or clean_path.startswith("windows") or clean_path.startswith("bin"):

        raise HTTPException(status_code=404, detail="Not found")



    if (

        clean_path == "api"

        or clean_path.startswith("api/")

        or clean_path == "docs"

        or clean_path.startswith("docs/")

        or clean_path == "openapi.json"

        or clean_path == "redoc"

        or clean_path.startswith("redoc/")

    ):

        raise HTTPException(status_code=404, detail="API route not found")



    target_file = frontend_dist / clean_path

    if target_file.is_file() and not clean_path.endswith(".html"):

        return FileResponse(str(target_file))



    # Supported SPA application views

    valid_spa_routes = {

        "", "dashboard", "ingestion", "facts", "summary", "revision",

        "eligibility", "qa", "navigator", "timeline", "history", "settings", "demo", "login", "signup", "verify-email", "verify_email", "forgot-password", "forgot_password", "reset-password", "reset_password"

    }

    first_segment = clean_path.split("/")[0].lower()

    if clean_path == "" or first_segment in valid_spa_routes:

        index_html = frontend_dist / "index.html"

        if index_html.is_file():

            return FileResponse(str(index_html))



    raise HTTPException(status_code=404, detail="Page not found")



