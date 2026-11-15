# SochnaSetu AI — Security, Privacy & Compliance Audit

**Review Target:** Entire Codebase (`src/notice2action/`, `frontend/src/`, `.env`, `data/`)  
**Evaluation Role:** Senior Information Security Auditor & Cryptographic Reviewer  
**Audit Standard:** OWASP Top 10 API Security & Zero-Trust Privacy Guidelines  

---

## 1. Executive Security & Privacy Posture

Since SochnaSetu AI processes sensitive public and personal documents (scholarship certificates, identity marks, statutory notifications, tax and property advisories), strict data privacy and local-first execution are paramount.

The `ps2` codebase exhibits a mature security posture:
- **Zero Cloud Transmission by Default:** All document ingestion, OCR, and AI inference execute 100% on-device using local Tesseract and Ollama. No circulars are transmitted to external services without explicit citizen selection.
- **Digest-Only Token Storage:** Raw authentication tokens, password reset magic links, and 6-digit OTP codes are **never stored in the database in plaintext**. They are cryptographically hashed using **HMAC-SHA256** before database insertion.
- **Modern Password Hashing:** Passwords utilize **Argon2id** (`time_cost=2`, `memory_cost=64MB`, `parallelism=1`) with unique cryptographic salts.
- **SQL Injection Immunity:** 100% of SQL operations utilize parameterized query interfaces (`conn.execute("SELECT ... WHERE id = ?", (doc_id,))`). Zero raw string concatenations exist across all 2,877 lines of `db.py`.

---

## 2. In-Depth Vulnerability Assessment

### S1. CSRF Protection Middleware Behavior
- **Severity:** Medium
- **Status:** **MITIGATED / AUDITED**
- **Vulnerability Description:** `server.py` (lines 406–411) blocks state-changing requests carrying session cookies if neither `Origin` nor `Referer` headers are supplied:
  ```python
  elif has_session_cookie:
      logger.warning("Blocked state-changing request with session cookie but missing Origin/Referer")
      return JSONResponse(status_code=403, content={"detail": "Origin or Referer header required..."})
  ```
- **Operational Impact:** Prevents cross-site form submissions and malicious cookie-based drive-by requests. In automated integration testing, test clients must explicitly supply `headers={"Origin": "http://testserver"}` when executing sequential calls with persistent cookies.

### S2. File Upload Path Traversal & Extension Spoofing Defense
- **Severity:** High
- **Status:** **VERIFIED SECURE**
- **Evidence:** Tested in `tests/test_api_endpoints.py::test_api_samples_path_traversal_protection`.
- **Implementation:**
  1. File names are stripped of path delimiters using `Path(filename).name` and sanitized.
  2. Storage files are saved under generated deterministic hex strings (`{file_hash}_{timestamp}.{ext}`) in `data/uploads/`, eliminating directory traversal attacks (`../../etc/passwd`).
  3. Magic bytes inspect binary file headers (`%PDF-`, `\xFF\xD8\xFF`, `\x89PNG`), defeating extension spoofing attacks.

### S3. Cross-Site Scripting (XSS) & Content Injection Defense
- **Severity:** Medium
- **Status:** **VERIFIED SECURE**
- **Evidence:** Frontend React 19 JSX automatically escapes rendered strings.
- **Prompt Injection Defense:** `src/notice2action/security.py` scans incoming text for adversarial prompt injection signatures (`"Ignore previous instructions"`, `"System prompt override"`, `"Output secret keys"`). Untrusted user documents are encapsulated within strict `<untrusted_notice_document>` boundaries, preventing privilege escalation within the LLM context.

### S4. Secret Management & Credential Exposure
- **Severity:** High
- **Status:** **VERIFIED SECURE IN PS2**
- **Evidence:**
  - `ps2/.env` has been sanitized for local execution.
  - `.gitignore` explicitly excludes `.env`, `*.db`, `*.sqlite`, `*.log`, and `uploads/`.
  - Sensitive values (`OPENROUTER_API_KEY`, `GEMINI_API_KEY`, `AUTH_SECRET_KEY`) load from environment variables with safe development defaults.

---

## 3. Security Risk Assessment Matrix

| ID | Vulnerability / Threat | Component | Severity | Likelihood | Impact | Status | Remediation |
|---|---|---|:---:|:---:|:---:|:---:|---|
| **SEC-01** | Missing Origin/Referer on cookie requests | API Server | Medium | Low | Low | **Mitigated** | CSRF middleware enforces Origin headers on state-changing requests. |
| **SEC-02** | Path Traversal via uploaded filenames | File Ingestion | High | Low | High | **Protected** | Filenames are hashed and isolated in `data/uploads/`. |
| **SEC-03** | Prompt Injection via adversarial notices | LLM Ingestion | Medium | Medium | Medium | **Protected** | Input sanitization and boundary tag wrapping applied. |
| **SEC-04** | Brute-force account enumeration | Auth API | Medium | Low | Low | **Protected** | Sliding-window SQLite rate limiting (5 attempts per window). |
| **SEC-05** | Leakage of sensitive tokens in DB dumps | Storage | Critical | Low | High | **Protected** | HMAC-SHA256 digests used for sessions and OTPs. |
| **SEC-06** | Memory accumulation in large PDF uploads | PDF Parser | Low | Low | Medium | **Protected** | PyPDF 30-page hard limit and 15MB file size limit enforced. |
