# SochnaSetu AI — Risk & Dependency Analysis Matrix

**Role:** Senior Systems Architect & Security Auditor  
**Objective:** Identify architectural risks, regression paths, dependency chains, and privacy guarantees across all proposed enhancements.  

---

## 1. Architectural Risk & Impact Matrix

| Change Area | Affected Files | API Changes | Database Changes | Functionality at Risk | Mitigation Strategy | Security & Privacy Impact |
|---|---|---|---|---|---|---|
| **1. Orientation Recovery Upgrade** | `src/notice2action/ocr.py` | None | None | Potential over-rotation on square images | Fall back to 0° if edge density variance $<15\%$ | Zero external network transmission |
| **2. Intra-Numeral Spacing Normalization** | `ocr.py`, `grounding.py` | None | None | Accidental merging of legitimate spaced numbers (e.g. phone numbers) | Restrict space collapse strictly to date patterns (`DD/MM/YYYY`) and 4-digit years | None |
| **3. Gazette Rule Decoupling** | `ocr.py` | None | None | Regression on `test_gazette_ocr_benchmark.py` | Move rules into conditional `GazettePostProcessor` triggered by masthead tags | None |
| **4. RapidOCR ONNX Activation** | `pyproject.toml`, `ocr.py` | None | None | ONNX runtime binary incompatibility on older CPUs without AVX | Catch ONNX `ImportError`/`RuntimeError` and fall back to native Tesseract C++ | 100% offline; uses local ONNX weights |
| **5. Database Schema Migration 6** | `storage/db.py` | New endpoints | 2 new tables, 1 FTS5 virtual table | Potential SQLite lock or schema corruption during upgrade | Wrap migration in atomic `BEGIN TRANSACTION` / `ROLLBACK`; additive-only changes | Local SQLite only; zero data leakage |
| **6. Token-Level HITL Review** | `server.py`, `OriginalNoticeViewerModal.tsx` | `POST /api/ocr/correct-token` | Writes to `ocr_tokens`, `documents` | Desynchronization between raw text and structured facts | Re-run `verify_structured_notice()` immediately upon committing edits | User edits remain on-device |
| **7. Split-Screen Layout Redesign** | `ApplicationLayout.tsx`, `GroundedFactsView.tsx`| None | None | Layout breakage on narrow mobile screens ($<640\text{px}$) | Implement responsive breakpoint collapsing left pane on mobile viewports | Pure CSS/React; no data exposure |
| **8. Binary PDF Export Endpoint** | `server.py`, `pdf_export_service.py` | `POST /api/export/pdf` | None | High CPU / RAM spikes during heavy PDF rasterization | Enforce 15MB file size limit and cache generated PDF bytes | Emits directly to client socket |
| **9. Frontend Code-Splitting** | `ApplicationLayout.tsx` | None | None | Flashes of unstyled content (FOUC) during chunk loads | Provide high-contrast accessible skeleton loaders (`<Suspense fallback={...}>`) | None |
| **10. CSRF Loopback Bypass** | `server.py` (lines 406–411) | None | None | Accidental exposure of state-changing endpoints in production | Condition bypass strictly on `ENVIRONMENT == 'development'` or loopback IP | High security; strict production enforcement remains active |

---

## 2. Dependency Graph & Sequencing Constraints

```
  [ TASK-P0-01: Fix OSD Orientation ] ───► Independent (Can merge immediately)
  [ TASK-P0-02: Fix CSRF Test Header ] ──► Independent (Unblocks 32 backend tests)
  [ TASK-P1-01: Numeral Space Repair ] ──► Independent (Improves grounding pass rate)
  [ TASK-P1-02: Decouple Gazette Overfit ] ─► Independent (Generalizes OCR)
  [ TASK-P1-03: RapidOCR ONNX Adapter ] ─► Independent (Requires pip install)
  
  [ TASK-P2-01: Schema Migration 6 ]
             │
             ├──► [ TASK-P1-04: Backend Token Correction Endpoint ]
             │             │
             │             └──► [ TASK-P1-05: Frontend Token Editor Popover ]
             │                           │
             │                           └──► [ TASK-P2-02: Split-Screen Workspace ]
             │
             └──► [ TASK-P2-03: Server Binary PDF Export ]
```

---

## 3. Privacy, Air-Gap & Security Guarantees

Every enhancement in this plan strictly upholds SochnaSetu AI's core architectural tenets:
1. **Zero Cloud Dependency:** Neither RapidOCR nor Tesseract make external HTTP requests. All neural weights run in-process on CPU/GPU via ONNX runtime or native C++ binaries.
2. **Local Token Integrity:** All token edits, correction dictionaries, and audit logs are stored strictly inside the local SQLite database (`data/suchnasetu.db`).
3. **Session & Cryptographic Continuity:** The authentication layer (Argon2id hashing, HMAC-SHA256 session digests, sliding-window rate limiting) remains unchanged and fully enforced across all new API routes.
