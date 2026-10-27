---
title: SuchnaSetu AI
emoji: 📢
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# SuchnaSetu AI 📢

> **PS02 — Notice-to-Action Accessibility Assistant**  
> **Event:** Hacktoberfest 2026 HackDay@Meerut × E-Cell IIMT University  
> **Track:** Track 1 — Best Use of Gemma 4  
> **Theme:** "AI Belongs to Everyone"  
> **Official Challenge Reference:** [events2026.co.in/problem-statements](https://events2026.co.in/problem-statements)  
> **Repository:** [https://github.com/bhardwajji-db/suchnasetu-ai](https://github.com/bhardwajji-db/suchnasetu-ai)  
> **License:** Apache License 2.0 (See [LICENSE](LICENSE))  

---

## 🌟 Executive Summary

Official college circulars, scholarship announcements, government notices, and application forms are frequently published as low-resolution image posters, cluttered scans, or dense bureaucratic legalese. Students and applicants routinely miss critical deadlines, overlook mandatory documents, or misinterpret eligibility criteria.

**SuchnaSetu AI** (Notice-to-Action) transforms complex administrative communications into clear, structured, evidence-grounded action plans. By default, it operates **100% locally and air-gapped** using **Google Gemma 4** (`gemma4:latest`) via Ollama and **Tesseract OCR v5.4.0**, guaranteeing that no user documents ever leave the host machine. For users seeking cloud scalability, a modular multi-provider integration layer also supports **OpenRouter**, **Google Gemini**, and **Hugging Face Inference**.

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
- 📋 **Demo 1 (Compliance):** Missing mandatory enrollment certificates with a 14-day cure deadline ([`demo_missing_compliance.txt`](tests/fixtures/demo_missing_compliance.txt)).
- 💰 **Demo 2 (Outstanding Dues):** Municipal water and sewerage demand assessment with penalty surcharge date ([`demo_outstanding_dues.txt`](tests/fixtures/demo_outstanding_dues.txt)).
- ⚖️ **Demo 3 (Administrative Hearing):** Environmental air emission compliance show-cause notice and statutory personal hearing schedule ([`demo_response_hearing.txt`](tests/fixtures/demo_response_hearing.txt)).

### 10. Multi-Notice Revision Ledger & Personal Impact Change Tracker
- **Automatic Relationship Detection:** Detects whether a document is an `AMENDMENT`, `EXTENSION`, `CANCELLATION`, `REPLACEMENT`, or `RELATED` notice with verbatim legal evidence citations (e.g., *"This corrigendum modifies Advertisement No. 04/2026"*).
- **Field-by-Field Semantic Diff:** Compares base notices against corrigenda across deadlines, application fees, eligibility criteria, and required documents.
- **Personal Impact Tracker:** Evaluates personal impact directly against applicant profiles (detecting deadline extensions, category fee waivers, and marks relaxations).
- **Side-by-Side Delta Comparison:** Visualizes exactly what changed, what was added, and what remains unchanged with old vs. new values and excerpt citations.
- **Audit Markdown Export:** Single-click export of complete revision audit reports.

### 11. Explainable Applicant Eligibility Engine
- **Deterministic Rules Without Hallucination:** Extracts explicit criteria (Age cutoffs, Min Marks %, Academic Degrees, Category Quotas) and evaluates an applicant profile deterministically in Python.
- **Category-Based Relaxations:** Automatically calculates and applies statutory relaxations (e.g. OBC +3 years, SC/ST +5 years) as of the exact notice cutoff date.
- **Strict Boundary Check:** Mathematical verification ensures percentages (e.g. 59.8% vs 60.0%) are never rounded up or hallucinated.
- **Transparent Verdicts:** Returns color-coded `PASS`, `FAIL`, or `UNKNOWN` statuses for each criterion paired with the exact verbatim notice quotation and explanation.

### 12. Evidence-First Trust Engine & Verification Drawer
- **Universal Evidence Drawer:** Slide-out evidence inspector with line-level citations, OCR fuzzy matching (handling character scan noise), and integrity badges.
- **Ungrounded Claim Detection:** Flags assertions lacking verbatim backing in official notices.
- **Prompt Injection Defense:** Wraps untrusted user content and scans for adversarial prompt overrides.

### 13. Personalized Action Navigator
- **Dependency-Ordered Roadmap:** Generates tailored action steps (Documentation, Submission, Verification, Fee Payment, Exam Prep).
- **Prerequisite Blocking:** Automatically blocks downstream actions (e.g. "Submit Final Application") until prerequisites (e.g. "Obtain OBC Certificate") are completed.
- **Interactive Management & Export:** Allows toggling statuses, filtering by category, and exporting as CSV or JSON.

### 14. Cross-Notice Intelligence Workspace
- **Multi-Document Registry:** Aggregates multiple circulars, addenda, and announcements into a unified workspace.
- **Chronological Timeline:** Sequences all deadlines and publication dates across multiple documents.
- **Contradiction & Conflict Engine:** Flags conflicting deadlines, fees, and instructions across circulars.

### 15. Accessibility-First Voice Guidance & Speech Input
- **Universal Voice Guidance Bar:** Floating audio player with playback speed control (0.8x - 1.5x) and real-time live captions.
- **Air-Gapped Speech Synthesis:** Uses browser-native Web Speech API (`window.speechSynthesis`) by default with zero network transmission.
- **Hands-Free Voice Recognition:** Speech-to-text mic input in Q&A chat for citizens with motor or typing impairments.

---

## ⚙️ Configuration & Environment Variables

All settings are configured via environment variables or a local `.env` file in the project root. Copy `.env.example` to get started:

````powershell
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

> [!TIP]
> **First-Time Setup on Windows?** See the complete step-by-step [SETUP.md](SETUP.md) for prerequisites, environment creation, Tesseract OCR, Ollama, and troubleshooting.

Execute all commands from the project root:
```powershell
git clone https://github.com/bhardwajji-db/suchnasetu-ai.git
cd suchnasetu-ai
```

### 1. Start Local Ollama Server (Terminal 1)
Make sure the Gemma 4 model is pulled and running locally:
```powershell
ollama run gemma4:latest
# or start the background server:
# ollama serve
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

## 🎯 Hackathon Demo Walkthrough (Live Scenario)

Follow these steps to demonstrate SuchnaSetu AI's flagship features in under 5 minutes:

### Scenario: UPSC Central Merit Scholarship Corrigendum & Eligibility Check

#### Step 1: Ingest Original Notice
1. Navigate to **Tab 1: Notice Ingestion & Analysis**.
2. Click **"Load Demo Fixture"** or paste [`tests/fixtures/demo_upsc_scholarship.txt`](tests/fixtures/demo_upsc_scholarship.txt).
3. Click **"Run Notice-to-Action Analysis"**.
4. Observe the **Six Core Fields** extraction with confidence tags, line-level evidence citations, and interactive **Uncertain Fact Confirmation**.

#### Step 2: Compare with Corrigendum in Revision Ledger
1. Click on **Tab 4: Revision Ledger** in the sidebar.
2. Notice 1 is automatically populated with the active notice.
3. Click **"Load Corrigendum Sample"** (loads [`tests/fixtures/demo_upsc_corrigendum.txt`](tests/fixtures/demo_upsc_corrigendum.txt)).
4. Click **"Compare Notice Revisions"**.
5. Observe:
   - **Relationship Badge:** `AMENDMENT` (Detected with 100% confidence).
   - **Legal Citation:** *"This corrigendum modifies and supersedes specific clauses of Advertisement No. 04/2026..."*
   - **Field Delta Cards:** Shows deadline extended from `October 15, 2026` to `November 05, 2026` and application fee reduced from `Rs. 500` to `Rs. 250`.
   - Click **"Export Revision Report"** to download the clean markdown audit trail.

#### Step 3: Check Candidate Qualification in Eligibility Engine
1. Click on **Tab 5: Eligibility Check** in the sidebar.
2. Click **"Extract Criteria from Current Notice"** (detects Min 60.0% marks, Age <= 30 cutoff, Master's Degree requirement).
3. Enter Applicant Profile:
   - **Date of Birth:** `1994-08-15` (Age 32 as of 2026-10-01)
   - **Category:** `OBC` (Triggers statutory +3 years relaxation: max age becomes 33 -> **PASS**)
   - **Aggregate Marks (%):** `62.5%` (Passes 60.0% threshold -> **PASS**)
   - **Highest Qualification:** `M.Sc. Computer Science` (Meets Master's degree rule -> **PASS**)
4. Click **"Evaluate My Eligibility"**.
5. Observe the instant explainable verdict breakdown with color-coded badges, statutory relaxation notes, and verbatim citations.

#### Step 4: Verify Air-Gapped Offline Privacy
1. Switch to **Tab 3: Plain-Language Summary & Actions**.
2. Click **"Read Aloud"** to hear the summary via browser-native Web Speech API. Notice in browser DevTools Network tab that **zero audio packets** leave your computer.
3. Go to **Settings > Privacy & Local Data Storage** and click **"Purge All Stored Data"** to securely wipe all local records.

---

## 🧪 Automated Testing Suite

```powershell
# 1. Run all 151 backend unit, integration, trust engine, action roadmap & timeline tests
uv run pytest tests/ --ignore=tests/test_playwright_react_frontend.py -m "not live" -v

# 2. Run frontend Vitest component tests (10 suites, 16 tests)
cd frontend
npm test -- --run
cd ..

# 3. Compile frontend production bundle (TypeScript strict check + Vite build)
cd frontend
npm run build
cd ..

# 4. Run live local Ollama & Gemma 4 integration tests (requires Ollama running)
uv run pytest tests/test_live_gemma4.py -v
```

---

## 📂 Repository Layout

```
suchnasetu-ai/
├── pyproject.toml                 # Canonical Python project configuration (Apache-2.0)
├── requirements.txt               # Locked Python dependencies
├── LICENSE                        # Apache 2.0 Open-Source License
├── CONTRIBUTING.md                # Contribution guidelines
├── SETUP.md                       # Complete step-by-step Windows setup guide
├── .env.example                   # Environment configuration template
├── ARCHITECTURE.md                # System architecture & design specification
├── API.md                         # Complete REST API specification
├── run_app.bat                    # One-click Windows runner (FastAPI + React)
├── assets/                        # Multi-viewport screenshots & local tessdata
├── docs/                          # Comprehensive technical documentation & requirements
├── reports/                       # Validation reports & evaluation benchmarks
├── scripts/                       # Setup, diagnostics, test runner & release packager
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
├── tests/                         # Pytest test suites (127 tests)
│   ├── test_multi_provider_llm.py # Multi-provider & offline mock tests
│   ├── test_services_and_six_fields.py # EvidenceService, SessionStore, 6 fields
│   ├── test_api_endpoints.py      # FastAPI REST endpoint integration tests
│   ├── test_live_gemma4.py        # Live local model integration tests
│   └── fixtures/                  # Three dedicated fictional demos + samples
```
