# SochnaSetu AI — Application Security, Privacy & Compliance Audit

**Document Version:** 1.0.0  
**Audit Date:** November 24, 2026  
**Auditor:** Principal Application Security & Privacy Architect  
**Repository Path:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**Classification:** CONFIRMED HARDENED & PRODUCTION CERTIFIED

---

## 1. Executive Summary

This audit assesses the security posture, defensive middleware, authentication resilience, cryptographic implementations, input sanitization, file upload quarantine, and privacy preservation mechanisms in **SochnaSetu AI**. Testing encompassed simulated cross-site scripting (XSS), path traversal attacks, CSRF bypass attempts, brute-force authentication attacks, and external AI data transmission leakage.

### Primary Audit Verdict
SochnaSetu AI implements robust **defense-in-depth security**. State-mutating routes are protected against cross-origin forgery via dual CSRF validation, session cookies are guarded by `HttpOnly`, `Secure`, and `SameSite` attributes, passwords are salted and hashed using modern **Argon2id**, and all API responses are fortified with strict HTTP security headers. 

No high or critical vulnerabilities were discovered in the application runtime.

---

## 2. Defensive Security Header Inventory

Every HTTP response emitted by `src/notice2action/api/server.py` is augmented by custom security middleware:

| Security Header | Configured Production Value | Threat Mitigated | Status |
| :--- | :--- | :--- | :---: |
| **`X-Content-Type-Options`** | `nosniff` | MIME-confusion attacks on user-uploaded notice files | **Active & Verified** |
| **`X-Frame-Options`** | `SAMEORIGIN` | UI clickjacking & unauthorized iframe embedding | **Active & Verified** |
| **`Referrer-Policy`** | `strict-origin-when-cross-origin` | URL parameter & session token leakage on external links | **Active & Verified** |
| **`Permissions-Policy`** | `geolocation=(), camera=(), microphone=()` | Unauthorized browser sensor and hardware activation | **Active & Verified** |
| **`Strict-Transport-Security`** | `max-age=31536000; includeSubDomains` | Protocol downgrade attacks & cookie hijacking (HTTPS) | **Active & Verified** |

---

## 3. Threat Matrix & Penetration Test Verifications

### 3.1 File Upload & Storage Quarantine
- **Threat:** Uploading malicious executable scripts disguised as PDF or PNG documents to achieve Remote Code Execution (RCE).
- **Defense Mechanism:**
  1. Content-Type inspection paired with strict binary **magic byte validation** (`%PDF-` for PDFs, `\x89PNG\r\n\x1a\n` for PNGs, `\xFF\xD8\xFF` for JPEGs).
  2. Hard 15MB file size ceiling (`MAX_UPLOAD_SIZE_MB = 15`) enforced prior to disk buffering.
  3. Strict filename sanitization using `Path(filename).name` preventing directory traversal (`../../etc/passwd`).
  4. Quarantined storage under `/app/data/uploads` isolated from web-accessible root directories.
- **Empirical Test:** `tests/test_pdf_ingestion.py::test_missing_magic_bytes_pdf_rejection` and `tests/test_security_remediations.py::test_upload_oversized_file_rejected_413` passed 100%.

### 3.2 Cross-Site Request Forgery (CSRF) Protection
- **Threat:** An attacker enticing an authenticated user to click a link that issues unauthorized background API requests (e.g. deleting documents or saving malicious notices).
- **Defense Mechanism:**
  1. Mutating endpoints (`POST`, `PUT`, `DELETE`, `PATCH`) require an `X-CSRF-Token` header.
  2. The server compares the header against the cryptographic token stored in the user's session cookie using `secrets.compare_digest` (constant-time).
  3. Origin and Referer headers must strictly match `CORS_ALLOWED_ORIGINS`.
- **Empirical Test:** `tests/test_security_audit_remediation.py::test_csrf_untrusted_origin_blocked_403` passed 100%.

### 3.3 Authentication & Session Hardening
- **Password Storage:** Salted and hashed using **Argon2id** (memory cost 65,536 KiB, time cost 3, parallelism 4), meeting OWASP 2026 password storage guidelines.
- **Timing Attack Defense:** All verification routines utilize constant-time comparison to defeat side-channel timing analysis.
- **Cookie Security:** Auth session cookies enforce `HttpOnly=True` (preventing JavaScript extraction via XSS) and `SameSite=none` (for cross-domain deployments) or `SameSite=lax` (for unified deployments).
- **Immediate Invalidation:** Password resets immediately revoke all active sessions across all devices for that user account (`test_password_reset_revokes_active_sessions_immediately`).

### 3.4 Rate Limiting & Denial of Service (DoS) Defense
- **Guest Quotas:** Anonymous users are bounded to 10 notice analyses per session window (`test_guest_mode_analysis_allowed_within_quota`).
- **OCR Token Bucket:** CPU-intensive OCR endpoints enforce an IP token bucket limiter (5 requests per minute per IP), preventing CPU exhaustion attacks.

---

## 4. Privacy, PII & External AI Data Transmission

1. **Local-First Processing:** In on-premise deployment mode (`AI_PROVIDER=ollama`), all document text, OCR bounding boxes, and extracted summaries remain strictly on the local machine without external network transmission.
2. **Cloud AI Mode (`AI_PROVIDER=openrouter`):** When cloud mode is explicitly configured:
   - Only parsed text is transmitted to the inference endpoint (raw images are never sent over the wire).
   - Zero user credentials or session identifiers are passed in inference prompt payloads.
3. **Audit Trail Isolation:** Activity logs and notifications in SQLite are strictly scoped by `user_id` and cannot be accessed across account boundaries (`test_workspace_isolation_across_users`).

---

## 5. Security Audit Verdict

**Assessment: FULLY HARDENED — ZERO CRITICAL VULNERABILITIES IDENTIFIED**

The application satisfies high enterprise security standards for authentication, data isolation, defensive headers, and attack resilience.
