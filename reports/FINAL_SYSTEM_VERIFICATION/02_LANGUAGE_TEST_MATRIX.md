# 02 — 10-LANGUAGE TEST MATRIX & I18N VERIFICATION
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** PS02 (Hack Day 2026)  
**Verification Date:** 2026-10-24  

---

## 1. Supported Languages Overview

SochnaSetu AI supports ten Indian & official languages across the full user interface, document ingestion, and AI explanation pipeline:

| Code | Language | Native Script Label | Direction | Translation File | Keys Defined |
|---|---|---|---|---|---|
| `en` | English | English | LTR | `frontend/src/i18n/locales/en.ts` | 65 |
| `hi` | Hindi | हिन्दी | LTR | `frontend/src/i18n/locales/hi.ts` | 65 |
| `bn` | Bengali | বাংলা | LTR | `frontend/src/i18n/locales/bn.ts` | 65 |
| `ta` | Tamil | தமிழ் | LTR | `frontend/src/i18n/locales/ta.ts` | 65 |
| `te` | Telugu | తెలుగు | LTR | `frontend/src/i18n/locales/te.ts` | 65 |
| `mr` | Marathi | मराठी | LTR | `frontend/src/i18n/locales/mr.ts` | 65 |
| `gu` | Gujarati | ગુજરાતી | LTR | `frontend/src/i18n/locales/gu.ts` | 65 |
| `pa` | Punjabi | ਪੰਜਾਬੀ | LTR | `frontend/src/i18n/locales/pa.ts` | 65 |
| `kn` | Kannada | ಕನ್ನಡ | LTR | `frontend/src/i18n/locales/kn.ts` | 65 |
| `ur` | Urdu | اردو | RTL | `frontend/src/i18n/locales/ur.ts` | 65 |

---

## 2. Decoupled Architecture: Source Language vs Output Language

In SochnaSetu AI, the **Source Document Language** and **AI Output Language** are strictly decoupled:
- **UI Interface Language:** Changes all labels, menus, tables, buttons, and navigation without page refresh.
- **Document Source Language:** Automatically detected via script and word-frequency analysis (`src/notice2action/language_detection.py`), with manual override available in the Ingestion View.
- **AI Output Language:** Controls whether summaries, simplified action checklists, and explanations are generated in English, Hindi, Bengali, Tamil, etc., regardless of the original document language.

---

## 3. UI Language Switching Verification

| View / Component | English (`en`) | Hindi (`hi`) | Bengali (`bn`) | Tamil (`ta`) | Telugu (`te`) | Marathi (`mr`) | Gujarati (`gu`) | Punjabi (`pa`) | Kannada (`kn`) | Urdu (`ur` + RTL) |
|---|---|---|---|---|---|---|---|---|---|---|
| **Header Branding & Selectors** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS (RTL) |
| **Sidebar Navigation (11 views)** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS (RTL) |
| **Document Ingestion Controls** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS (RTL) |
| **Grounded Facts Cards** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS (RTL) |
| **Plain Language Summary** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS (RTL) |
| **Action Checklist Table** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS (RTL) |
| **Corrigendum Revision Ledger** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS (RTL) |
| **Eligibility Assessment Engine** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS (RTL) |
| **Grounded Q&A Chat** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS (RTL) |
| **Demo Library Gallery (32)** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS (RTL) |
| **Settings & Accessibility** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS (RTL) |

---

## 4. Urdu RTL Verification

- **HTML Element:** `document.documentElement.dir = 'rtl'` dynamically set when `ur` is selected.
- **Font Rendering:** High-legibility Nastaliq / Naskh unicode text rendering.
- **Form Controls:** Text alignments flipped, buttons mirrored appropriately, numbers and dates preserved in standard Indo-Arabic digits.
- **Fallback Safety:** Missing keys fall back seamlessly to English without runtime exceptions or broken UI elements.
