# 07. LOCAL OLLAMA GEMMA 4 VERIFICATION — SOCHNASETU AI

**LLM Provider:** Local Ollama (Daemon at `http://127.0.0.1:11434`)  
**Target Model:** `gemma4:latest` (Google Gemma 4, 9.6 GB, ID: `c6eb396dbd59`)

---

## 1. Daemon & Model Health Status

- **Connection Test:** `GET http://127.0.0.1:11434/api/version` -> Version `0.40.3` (Status 200).
- **Model Check:** `& "C:\\Users\\Avinash\\AppData\\Local\\Programs\\Ollama\\ollama.exe" list`
  - Confirmed `gemma4:latest` is installed locally on disk (9.6 GB). Zero download required.
- **Application Health:** `GET http://127.0.0.1:8000/api/health`
  - Returned: `{"ollama": {"connected": true, "has_target_model": true, "target_model": "gemma4:latest"}}`.

---

## 2. Live Inference & Extraction Execution

A live structured analysis was executed against the synthetic scholarship notice through the full application pipeline:
- **Input Characters:** 2,042 characters
- **Elapsed Inference Time:** 14.8 seconds
- **Output Validation:**
  - Status: Stated
  - Purpose: *"To provide a one-time direct technology grant for purchasing learning equipment, digital tablets, or peripheral devices."*
  - Deadline: *"15 November 2026, 5:00 PM IST"*
  - Eligibility: *"Full-time undergraduate student enrolled at a participating college; Total family annual income must be Rs. 3,00,000 per year or less."*
  - Required Documents: *"Valid Student ID card; Self-declared household income statement (<= Rs. 3,00,000); Duly completed application form; Study statement."*
  - Contact Details: *"helpdesk@example.invalid"*
  - Authenticity / Uncertainty: *"The entire notice is explicitly stated to be fictional and for demonstration purposes."*

---

## 3. Failure Handling & Resilience

1. **Daemon Unreachable / Offline:** Tested in `tests/test_ollama_integration.py::test_ollama_connection_error_on_invalid_endpoint`. If Ollama is terminated, the application gracefully surfaces an informative error without unhandled server crashes, and safely falls back to deterministic extraction.
2. **Timeout Protection:** Configured with a 120-second request timeout (`OLLAMA_TIMEOUT_SECONDS=120`). Long or stalled inferences fail gracefully with an actionable HTTP 504 Gateway Timeout.
3. **Zero Secret Leakage:** Ollama calls are strictly local (`127.0.0.1`). No tokens, authentication headers, or notice contents are ever transmitted to the internet.
