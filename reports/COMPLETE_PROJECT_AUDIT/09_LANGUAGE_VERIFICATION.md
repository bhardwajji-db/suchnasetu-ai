# 09. MULTILINGUAL & LOCALIZATION VERIFICATION — SOCHNASETU AI

**Supported Languages:** 10 Constitutional Indian Languages  
**Implementation:** `frontend/src/i18n/` dictionaries + `NoticeContext` state synchronization

---

## 1. Constitutional Language Verification Matrix

| Language | Code | Native Name | Script | Direction | Selector Functional | UI Labels Translated | RTL Verified | Persistence | Overall Verdict |
| :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **English** | `en` | English | Latin | LTR | YES | YES | N/A | YES | **PASS** |
| **Hindi** | `hi` | हिन्दी | Devanagari | LTR | YES | YES | N/A | YES | **PASS** |
| **Bengali** | `bn` | বাংলা | Bengali script | LTR | YES | YES | N/A | YES | **PASS** |
| **Tamil** | `ta` | தமிழ் | Tamil script | LTR | YES | YES | N/A | YES | **PASS** |
| **Telugu** | `te` | తెలుగు | Telugu script | LTR | YES | YES | N/A | YES | **PASS** |
| **Marathi** | `mr` | मराठी | Devanagari | LTR | YES | YES | N/A | YES | **PASS** |
| **Gujarati** | `gu` | ગુજરાતી | Gujarati script| LTR | YES | YES | N/A | YES | **PASS** |
| **Punjabi** | `pa` | ਪੰਜਾਬੀ | Gurmukhi | LTR | YES | YES | N/A | YES | **PASS** |
| **Kannada** | `kn` | ಕನ್ನಡ | Kannada script | LTR | YES | YES | N/A | YES | **PASS** |
| **Urdu** | `ur` | اردو | Arabic-derived | RTL | YES | YES | **YES (`dir=rtl`)** | YES | **PASS** |

---

## 2. Critical Entity Preservation During Translation

When generating translated summaries and checklists in Hindi or regional languages:
- **Dates & Times:** Preserved verbatim (e.g. *"15 November 2026, 5:00 PM IST"*).
- **Monetary Figures:** Preserved verbatim (e.g. *"Rs. 8,000"*).
- **Official References:** Preserved verbatim (e.g. *"DEMO-2026-017"*).
- **Email & URL Contacts:** Preserved verbatim (e.g. *"helpdesk@example.invalid"*).
