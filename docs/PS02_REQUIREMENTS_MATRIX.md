# PS02 Traceability & Requirements Matrix

**Event:** Hacktoberfest 2026 HackDay@Meerut × E-Cell IIMT University  
**Track:** Track 1 — Best Use of Gemma 4  
**Problem Statement:** PS 02 — Notice-to-Action Accessibility Assistant  
**Theme:** “AI Belongs to Everyone”  
**Official Source:** [events2026.co.in/problem-statements](https://events2026.co.in/problem-statements)  
**Last Verified:** 20 October 2026  

---

## 1. Official Core Requirements Traceability

| ID | Official Requirement (Source) | Planned Implementation | Relevant Source File(s) | Acceptance Test(s) | Verification Status |
|---|---|---|---|---|---|
| **REQ-01** | Accept at least one image-based notice or text notice and extract its key contents. | Support direct text pasting and image upload (PNG, JPG, JPEG, WEBP) with preprocessed Tesseract OCR pipeline. | `src/notice2action/ingestion.py`, `src/notice2action/ocr.py` | `test_image_ocr_pipeline`, `test_text_notice_ingestion` | verified |
| **REQ-02** | Show structured fields such as purpose, eligibility, deadline, required documents, contact, and action; label fields that are not stated. | Strict Pydantic models with explicit certainty states (`stated`, `not_stated`, `uncertain`, `conflicting`, `unreadable`). Absent fields labelled "Not stated in the notice." | `src/notice2action/schemas.py`, `src/notice2action/analysis.py`, `src/notice2action/grounding.py` | `test_missing_deadline`, `test_missing_eligibility`, `test_missing_documents`, `test_missing_contact` | verified |
| **REQ-03** | Provide a concise plain-language summary and an ordered checklist of actions. | Grounded plain-language summary answering the 7 core questions; numbered checklist with verification status and user-controllable completion toggles. | `src/notice2action/summary.py`, `src/notice2action/checklist.py` | `test_plain_language_summary`, `test_action_checklist_generation` | verified |
| **REQ-04** | Offer output in at least two selected languages, or in one language plus a demonstrably accessible alternative such as read-aloud using suitable tooling. | First-class English and Hindi bilingual modes preserving critical facts (dates, amounts, contacts) verbatim; integrated browser/audio read-aloud accessibility feature. | `src/notice2action/translation.py`, `src/notice2action/ui/components.py`, `app.py` | `test_hindi_translation_fact_preservation`, `test_mixed_language_notice` | verified |
| **REQ-05** | Handle a clarification question and require confirmation before treating uncertain extracted details as facts. | Interactive follow-up Q&A strictly grounded in notice context; uncertain facts require explicit user confirmation before becoming actionable checklist steps. | `src/notice2action/followup.py`, `src/notice2action/grounding.py`, `src/notice2action/checklist.py` | `test_unsupported_followup_question`, `test_uncertainty_confirmation_gate` | verified |
| **REQ-06** | Use Gemma 4 centrally to interpret information and guide the user. | Local `gemma4:latest` model via Ollama adapter for semantic extraction, structured JSON parsing, plain-language summarization, and grounded Q&A. | `src/notice2action/llm/ollama_client.py`, `src/notice2action/analysis.py` | `test_ollama_client_live_inference`, `test_gemma4_structured_analysis` | verified |

---

## 2. Official Demonstration Checklist (Judge Checks)

| ID | Judge Demonstration Item | Implementation / Feature | Relevant File | Demo Flow Step | Status |
|---|---|---|---|---|---|
| **DEMO-01** | Display a sample scholarship, campus-event, or public-service notice. | Synthetic sample notices in `tests/fixtures/` and one-click quick-load in the Streamlit UI. | `tests/fixtures/scholarship_notice.txt`, `app.py` | Step 1: Ingestion & Preview | verified |
| **DEMO-02** | Show the simplified checklist in two modes, such as two languages or a language and accessible alternative. | Toggle between English and Hindi, with accompanying TTS audio read-aloud accessibility button. | `src/notice2action/ui/components.py`, `src/notice2action/translation.py` | Step 4: Checklist & Language Toggle | verified |
| **DEMO-03** | Ask about a requirement that is not stated and demonstrate that the assistant reports the information is absent. | Built-in sample question: "Can I submit the application late?" -> Assistant explicitly replies that the notice does not specify late submission. | `src/notice2action/followup.py` | Step 5: Grounded Follow-up Q&A | verified |

---

## 3. Engineering Quality & Security Requirements

| ID | Engineering Requirement | Planned Implementation | Relevant Source File | Test Verification | Status |
|---|---|---|---|---|---|
| **ENG-01** | Local-First & Free to Run | Ollama local inference (`gemma4:latest`) at 127.0.0.1:11434 with zero external API calls or cloud dependencies. | `src/notice2action/llm/ollama_client.py` | `test_ollama_offline_capability` | verified |
| **ENG-02** | Windows PowerShell Compatibility | Standard PowerShell scripts (`setup.ps1`, `run.ps1`, `preflight.ps1`, `test.ps1`) handling Windows path spaces properly. | `scripts/*.ps1` | `test_windows_paths_and_scripts` | verified |
| **ENG-03** | Strict Evidence Grounding | Every extracted fact must quote its evidence from the source text; ungrounded or hallucinated claims are caught and flagged. | `src/notice2action/grounding.py` | `test_altered_deadline_or_amount`, `test_invented_document` | verified |
| **ENG-04** | Input Validation & Prompt Injection Defense | Image type/size validation (max 10MB), prompt injection delimiter guards, untrusted input containment. | `src/notice2action/security.py` | `test_oversized_upload`, `test_corrupt_image`, `test_prompt_injection` | verified |
| **ENG-05** | Privacy & Session Isolation | Uploaded data stays in memory/session-state; temp files cleaned up immediately; no cross-session data leakage. | `src/notice2action/security.py`, `app.py` | `test_session_isolation`, `test_tempfile_cleanup` | verified |
| **ENG-06** | Graceful Degradation & Diagnostics | Clear preflight diagnostic; transparent error messages if Ollama is stopped, model is missing, or OCR fails. | `src/notice2action/config.py`, `scripts/preflight.py` | `test_ollama_unavailable`, `test_model_missing` | verified |

---

## Status Legend
- `verified`: Fully implemented and confirmed through automated or manual test execution.
- `implemented_but_unverified`: Code written but waiting for runtime verification.
- `incomplete`: Feature partially implemented.
- `blocked`: Blocked by external constraint.
