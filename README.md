# Notice2Action AI 📢

> **PS02 — Notice-to-Action Accessibility Assistant**  
> **Event:** Hacktoberfest 2026 HackDay@Meerut × E-Cell IIMT University  
> **Track:** Track 1 — Best Use of Gemma 4  
> **Theme:** "AI Belongs to Everyone"  
> **Official Challenge Reference:** [events2026.co.in/problem-statements](https://events2026.co.in/problem-statements)  
> **License:** Apache License 2.0 (See [LICENSE](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/LICENSE))  

---

## 🌟 Executive Summary

Official college circulars, scholarship announcements, government notices, and application forms are frequently published as low-resolution image posters, cluttered scans, or dense bureaucratic legalese. Students and applicants routinely miss critical deadlines, overlook mandatory documents, or misinterpret eligibility criteria.

**Notice2Action AI** transforms complex administrative communications into clear, structured, evidence-grounded action plans. By default, it operates **100% locally and air-gapped** using **Google Gemma 4** (`gemma4:latest`) via Ollama and **Tesseract OCR v5.4.0**, guaranteeing that no user documents ever leave the host machine. For users seeking cloud scalability, a modular multi-provider integration layer also supports **OpenRouter**, **Google Gemini**, and **Hugging Face Inference**.

---

## 🚀 Key Capabilities & Implemented Features

### 1. Multi-Provider LLM Integration Layer
- **Local Ollama (Default):** Runs 100% on-device via Ollama (`gemma4:latest`). Zero cloud dependencies, zero external network requests.
- **OpenRouter (Cloud):** OpenAI-compatible chat completion routing supporting open and commercial models.
- **Google Gemini (Cloud):** Direct integration with Gemini 1.5 / 2.0 via Google Generative AI REST API (`v1beta`).
- **Hugging Face Inference (Cloud):** Serverless router integration for open-access model checkpoints.
- **Clean Configuration & Credential Safety:** Starts without cloud keys. Clear diagnostic status when a selected cloud provider requires credentials. **Never hardcodes API keys or transmits documents to external providers without explicit user selection.**

### 2. Six Core Notice Fields (Structured Legal Extraction)
Inspects and extracts the six essential fields required to understand any legal or administrative notice:
1. **Issuing Authority or Department** (e.g. Directorate of Higher Education, Municipal Corporation)
2. **Notice / Reference Number** (e.g. `REF-2026-8812`)
3. **Notice Date** (Date of official issuance)
4. **Recipient or Concerned Party** (Target audience or applicant group)
5. **Main Issue, Allegation, or Subject** (Core purpose of the notice)
6. **Required Action and Deadline** (Mandatory steps paired with explicit cutoff date/time)

### 3. Uncertain OCR & Interpretation Confirmation
- Detects tentative, provisional, or ambiguous terms (`tentative`, `subject to revision`, `approximate`).
- Distinguishes OCR quality degradation (low character confidence, faint scans) from semantic text ambiguity.
- Provides interactive **Review & Confirm Modal** allowing users to correct or verify fields before downstream action plan generation.
- **Non-Destructive Ground Truth:** Preserves original verbatim notice extraction alongside user-confirmed values.

### 4. Grounded Evidence Service & Session Store
- **Evidence Service (`EvidenceService`):** Segments notice text into 1-based line numbers, indexes tokens, and provides sub-second keyword and semantic search for verbatim quotations.
- **Session Store (`SessionStore`):** Thread-safe local persistence (`.sessions/`) providing complete session isolation. Questions and analyses in one session never leak into another.

### 5. Multilingual Support (English & Hindi)
- Language toggle switches plain-language summaries, action checklists, and follow-up Q&A into Hindi (Devanagari script).
- **Critical Entity Audit:** Automatically ensures dates, monetary amounts, reference numbers, percentages, and contacts are preserved verbatim without translation distortion.

### 6. Reading-Level Selector
- **Simple (Grade 5):** Plain vocabulary, direct short sentences.
- **Standard (Grade 8):** Clear, balanced explanation answering the 7 core user questions.
- **Detailed:** Comprehensive operational breakdown.
- **Informational Disclaimer:** Displays a prominent legal disclaimer clarifying that simplified summaries are for accessibility and informational purposes and do not substitute for professional legal advice.

### 7. Truthful Evidence-Grounded Q&A
- Answers queries strictly based on the active notice text and Evidence Service index.
- If an inquired detail (such as late submissions, unstated fees, or unmentioned exemptions) is absent, the system truthfully responds:  
  **`"This information was not found in the provided notice."`**
- Treats notice content strictly as **inert data**, immune to prompt injection attacks.

### 8. Original Notice Document Viewer
- Global slide-over drawer accessible from any tab.
- Displays verbatim raw notice text, word/character/line counters, and high-resolution scanned image previews.
- Full-text search bar and single-click clipboard copy. Never exposes server filesystem paths to users.

### 9. Three Dedicated Fictional Demo Notices
Clearly labeled **DEMO / FICTIONAL** notices ready for one-click evaluation without file upload:
- 📋 **Demo 1 (Compliance):** Missing mandatory enrollment certificates with a 14-day cure deadline ([`demo_missing_compliance.txt`](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/tests/fixtures/demo_missing_compliance.txt)).
- 💰 **Demo 2 (Outstanding Dues):** Municipal water and sewerage demand assessment with penalty surcharge date ([`demo_outstanding_dues.txt`](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/tests/fixtures/demo_outstanding_dues.txt)).
- ⚖️ **Demo 3 (Administrative Hearing):** Environmental air emission compliance show-cause notice and statutory personal hearing schedule ([`demo_response_hearing.txt`](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/tests/fixtures/demo_response_hearing.txt)).

---

## ⚙️ Configuration & Environment Variables

All settings are configured via environment variables or a local `.env` file in the project root. Copy `.env.example` to get started:

```powershell
cp .env.example .env
```

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `LLM_PROVIDER` | `ollama` | Active provider: `ollama`, `openrouter`, `gemini`, `huggingface` |
| `LLM_API_KEY` | *(empty)* | Generic fallback API key |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Local Ollama daemon URL |
| `OLLAMA_MODEL` | `gemma4:latest` | Local Gemma 4 model identifier |
| `OLLAMA_TIMEOUT_SECONDS` | `120` | Max timeout for local inference |
| `OPENROUTER_API_KEY` | *(empty)* | Optional: OpenRouter API Key |
| `OPENROUTER_MODEL` | `google/gemma-2-9b-it:free` | Model identifier for OpenRouter |
| `GEMINI_API_KEY` | *(empty)* | Optional: Google Gemini API Key |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Model identifier for Google Gemini |
| `HUGGINGFACE_API_KEY`| *(empty)* | Optional: Hugging Face Inference User Token |
| `HUGGINGFACE_MODEL` | `google/gemma-2-9b-it` | Model identifier for Hugging Face |
| `OCR_ENGINE` | `tesseract` | OCR engine: `tesseract` (default) or `rapidocr` |
| `TESSERACT_CMD` | `C:\Program Files\Tesseract-OCR\tesseract.exe` | Path to local Tesseract executable |
| `MAX_UPLOAD_SIZE_MB` | `10` | Maximum upload ceiling |
| `ALLOWED_EXTENSIONS` | `png,jpg,jpeg,webp,txt`| Permitted file extensions |
| `SESSION_STORAGE_DIR`| `.sessions` | Directory for isolated session storage |

> [!IMPORTANT]
> **API Key Policy:** Never commit `.env` or real API keys to version control. `.env` and `.sessions/` are strictly excluded in `.gitignore`. The application starts and runs tests completely offline without any API keys.

---

## ⚡ Quickstart Runbook

Execute all commands from the project root:
`C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`

### 1. Start Local Ollama Server (Terminal 1)
```powershell
ollama serve
```

### 2. Start FastAPI REST Backend (Terminal 2)
```powershell
.\.venv\Scripts\python.exe -m uvicorn notice2action.api.server:app --host 127.0.0.1 --port 8000
```
*Verify API health:*
```powershell
curl.exe -s http://127.0.0.1:8000/api/health
```

### 3. Start React 19 Frontend Dashboard (Terminal 3)
```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
*Access UI in browser:* [http://127.0.0.1:5173/](http://127.0.0.1:5173/)

---

## 🧪 Automated Testing Suite

```powershell
# 1. Run all backend unit, contract, multi-provider & pipeline tests
.\.venv\Scripts\python.exe -m pytest tests/test_api_endpoints.py tests/test_multi_provider_llm.py tests/test_services_and_six_fields.py tests/test_unit_pipeline.py tests/test_structured_notice_regression.py tests/test_negative_and_edge_cases.py -v

# 2. Run frontend Vitest component tests (10 suites, 16 tests)
cd frontend
npm test -- --run
cd ..

# 3. Compile frontend production bundle (TypeScript strict check + Vite build)
cd frontend
npx tsc -b
npm run build
cd ..

# 4. Run live local Ollama & Gemma 4 integration tests
.\.venv\Scripts\python.exe -m pytest tests/test_live_gemma4.py -v
```

---

## 📂 Repository Layout

```
ps2/
├── pyproject.toml                 # Canonical Python project configuration (Apache-2.0)
├── requirements.txt               # Locked Python dependencies
├── LICENSE                        # Apache 2.0 Open-Source License
├── .env.example                   # Environment configuration template
├── ARCHITECTURE.md                # System architecture & OCR comparison
├── API.md                         # Complete REST API specification
├── IMPLEMENTATION_REPORT.md       # Comprehensive implementation report
├── TEST_REPORT.md                 # Full test ledger and execution log
│
├── frontend/                      # Modern React 19 Frontend
│   ├── package.json               # Node dependencies & build scripts
│   ├── vite.config.ts             # Vite configuration with API proxy
│   ├── tsconfig.json              # TypeScript root configuration
│   └── src/
│       ├── context/NoticeContext.tsx # Global state: sessions, providers, language
│       ├── components/            # Reusable UI component library
│       │   ├── Header.tsx         # Header with provider & language selectors
│       │   ├── FactCard.tsx       # Grounded fact cards with uncertainty badges
│       │   ├── ConfirmationModal.tsx # Human-in-the-loop review modal
│       │   ├── OriginalNoticeViewerModal.tsx # Raw notice & OCR image viewer
│       │   ├── PlainLanguageSummaryView.tsx # 3-level summary & read-aloud
│       │   └── ActionChecklistTable.tsx # Interactive action checklist
│       ├── views/                 # Primary tabs: Ingestion, Facts, Summary, QA
│       ├── services/apiClient.ts  # Typed API client for FastAPI
│       └── test/                  # Vitest test suites (16 tests)
│
├── src/notice2action/             # Core Python package
│   ├── api/server.py              # FastAPI REST backend application
│   ├── config.py                  # Configuration & diagnostics
│   ├── schemas.py                 # Six Core Fields, Pydantic models
│   ├── ocr.py                     # Dual-engine OCR (Tesseract / RapidOCR)
│   ├── analysis.py                # Structured notice analysis orchestrator
│   ├── grounding.py               # Deterministic anti-hallucination verification
│   ├── summary.py                 # Multi-level summary generator
│   ├── checklist.py               # Grounded action checklist generator
│   ├── followup.py                # Truthful Q&A engine
│   ├── translation.py             # Hindi & English bilingual engine
│   ├── services/                  # Domain Services
│   │   ├── evidence_service.py    # Line-level evidence segmenting & search
│   │   └── session_store.py       # Isolated thread-safe session storage
│   └── llm/                       # Modular LLM Integration Layer
│       ├── base.py                # BaseLLMClient interface & exceptions
│       ├── factory.py             # Provider discovery & instantiation
│       ├── ollama_client.py       # Local Ollama Gemma 4 adapter
│       ├── openrouter_client.py   # OpenRouter cloud adapter
│       ├── gemini_client.py       # Google Gemini cloud adapter
│       └── huggingface_client.py  # Hugging Face cloud adapter
│
├── tests/                         # Pytest test suites (87+ tests)
│   ├── test_multi_provider_llm.py # Multi-provider & offline mock tests
│   ├── test_services_and_six_fields.py # EvidenceService, SessionStore, 6 fields
│   ├── test_api_endpoints.py      # FastAPI REST endpoint integration tests
│   ├── test_live_gemma4.py        # Live local model integration tests
│   └── fixtures/                  # Three dedicated fictional demos + samples
│
└── release/                       # Standalone clean distribution archive
    └── notice2action_ps02_release.zip
```
