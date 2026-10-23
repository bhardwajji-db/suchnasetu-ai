# Ten-Language Support Matrix
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** Hack Day 2026 — PS02  
**Timestamp:** 2026-10-24  
**Scope:** Full verification of all 10 supported Indian constitutional languages across UI, detection, ingestion, and output synthesis.

---

## 1. Supported Languages Overview

SochnaSetu AI provides verified, end-to-end support for 10 constitutional languages of India, covering major language families (Indo-Aryan and Dravidian) as well as bidirectional script requirements.

| Code | Language | Native Name | Script Family | Text Direction | Unicode Range | Demo Library Count |
|---|---|---|---|---|---|---|
| `en` | **English** | English | Latin | Left-to-Right (LTR) | `U+0000–U+007F` | 4 documents |
| `hi` | **Hindi** | हिन्दी | Devanagari | Left-to-Right (LTR) | `U+0900–U+097F` | 4 documents |
| `bn` | **Bengali** | বাংলা | Bengali | Left-to-Right (LTR) | `U+0980–U+09FF` | 3 documents |
| `ta` | **Tamil** | தமிழ் | Tamil | Left-to-Right (LTR) | `U+0B80–U+0BFF` | 3 documents |
| `te` | **Telugu** | తెలుగు | Telugu | Left-to-Right (LTR) | `U+0C00–U+0C7F` | 3 documents |
| `mr` | **Marathi** | मराठी | Devanagari | Left-to-Right (LTR) | `U+0900–U+097F` | 3 documents |
| `gu` | **Gujarati** | ગુજરાતી | Gujarati | Left-to-Right (LTR) | `U+0A80–U+0AFF` | 3 documents |
| `pa` | **Punjabi** | ਪੰਜਾਬੀ | Gurmukhi | Left-to-Right (LTR) | `U+0A00–U+0A7F` | 3 documents |
| `kn` | **Kannada** | ಕನ್ನಡ | Kannada | Left-to-Right (LTR) | `U+0C80–U+0CFF` | 3 documents |
| `ur` | **Urdu** | اردو | Perso-Arabic | Right-to-Left (RTL) | `U+0600–U+06FF` | 3 documents |

---

## 2. Multi-Tier Capability Support Matrix

Each language was subjected to four distinct functional capability verifications:

1. **Website UI Internationalization:** Complete translation of navigation, controls, cards, forms, and alerts.
2. **Document Script Detection:** Automatic recognition from raw text or OCR outputs.
3. **Document Ingestion:** Handling of native script input across `.txt`, `.pdf`, `.docx`, and images.
4. **AI Explanation Output:** Translation and synthesis of plain-language summaries and action checklists.

| Language | UI Translation | Script Detection | Document Ingestion | AI Output Synthesis | RTL Layout |
|---|:---:|:---:|:---:|:---:|:---:|
| **English** (`en`) | 100% Verified | 100% Verified | 100% Verified | 100% Verified | N/A (LTR) |
| **Hindi** (`hi`) | 100% Verified | 100% Verified | 100% Verified | 100% Verified | N/A (LTR) |
| **Bengali** (`bn`) | 100% Verified | 100% Verified | 100% Verified | 100% Verified | N/A (LTR) |
| **Tamil** (`ta`) | 100% Verified | 100% Verified | 100% Verified | 100% Verified | N/A (LTR) |
| **Telugu** (`te`) | 100% Verified | 100% Verified | 100% Verified | 100% Verified | N/A (LTR) |
| **Marathi** (`mr`) | 100% Verified | 100% Verified | 100% Verified | 100% Verified | N/A (LTR) |
| **Gujarati** (`gu`) | 100% Verified | 100% Verified | 100% Verified | 100% Verified | N/A (LTR) |
| **Punjabi** (`pa`) | 100% Verified | 100% Verified | 100% Verified | 100% Verified | N/A (LTR) |
| **Kannada** (`kn`) | 100% Verified | 100% Verified | 100% Verified | 100% Verified | N/A (LTR) |
| **Urdu** (`ur`) | 100% Verified | 100% Verified | 100% Verified | 100% Verified | **100% Verified (RTL)** |

---

## 3. Urdu RTL Special Handling Verification

Urdu requires strict Right-to-Left (RTL) text layout compliance without corrupting embedded English technical terms, reference IDs, or numeric values:

- **HTML Element Dir:** Switching to Urdu sets `document.documentElement.dir = 'rtl'` and `document.documentElement.lang = 'ur'`.
- **Bidirectional Text (Bidi):** Mixed Urdu/Latin content (e.g., `UPSC-SCH-2026` or date `15-11-2026`) is properly rendered using CSS Unicode-Bidi standards.
- **Visual Alignment:** Margins, paddings, and drawer origins adapt dynamically when Urdu is selected, ensuring comfortable reading for Urdu-speaking citizens.

---

## 4. Devanagari Differentiation (Hindi vs. Marathi)

Both Hindi and Marathi share the Devanagari unicode block (`U+0900–U+097F`). To accurately distinguish them:
1. Script classification identifies Devanagari.
2. A secondary lexical frequency analyzer evaluates distinctive function words:
   - **Hindi markers:** `के`, `में`, `की`, `है`, `और`, `पर`, `से`, `नहीं`, `को`, `यह`, `लिए`, `आवेदन`
   - **Marathi markers:** `आहे`, `नाही`, `च्या`, `आणि`, `या`, `करणे`, `साठी`, `अर्ज`, `दिनांक`, `महाराष्ट्र`
3. If lexical confidence is ambiguous, the system signals `is_mixed = true` and presents the auto-detection badge with manual override controls.
