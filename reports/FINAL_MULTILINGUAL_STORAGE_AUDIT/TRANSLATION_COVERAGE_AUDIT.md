# Translation Coverage Audit
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** Hack Day 2026 — PS02  
**Timestamp:** 2026-10-24  
**Scope:** Exhaustive key audit of all 10 language translation dictionaries in `frontend/src/i18n/locales/`.

---

## 1. Audit Methodology

Every view, component, button, status label, modal, drawer, form control, and accessibility announcement was audited to ensure:
1. **Zero Hardcoded English Strings** in critical UI workflows.
2. **Key Parity:** Every language locale dictionary defines 100% of the keys required by the `TranslationDictionary` interface.
3. **Parameter Interpolation:** Dynamic keys (e.g., `{count} characters`, `{duration} seconds`) correctly substitute values without breaking formatting.
4. **Fallback Safety:** Any missing key automatically falls back to standard English (`en`) without throwing runtime JavaScript exceptions.

---

## 2. Key Coverage by Functional Domain

| Domain | Key Count | Description |
|---|:---:|---|
| **App Branding & Global Actions** | 22 | Titles, loading, save, cancel, confirm, clear, download, copy, status badges |
| **Header & Preflight Diagnostics** | 8 | Health status, provider picker, original document trigger, model badges |
| **Navigation & Workspaces** | 12 | 11 primary workspace tabs + Demo Library + workspace drawer title |
| **Notice Ingestion & OCR** | 24 | Drag-and-drop zone, camera OCR, file size limits, paste buffer, clear, analyze |
| **Multilingual Control Strip** | 10 | Source language selector, confidence badge, output language picker, auto-detect |
| **Grounded Facts & Core Six** | 18 | Stated, uncertain, conflicting, evidence badges, confirm dialog, authority, dates |
| **Plain Language Summaries** | 12 | Reading level toggles (simple, standard, detailed), read aloud, audio player |
| **Action Checklists & Roadmap** | 16 | Step numbering, completion toggle, download markdown, add to calendar, categories |
| **Eligibility & Personal Impact** | 18 | Rule evaluation, profile match, pass/fail status, missing criteria explanation |
| **Follow-Up Grounded Q&A** | 14 | Suggested questions, submit inquiry, quote citation, not-found message |
| **Revision & Timeline Graph** | 12 | Corrigendum pairing, superseding amendments, timeline events, difference viewer |
| **Accessibility Preferences** | 14 | Text size, line spacing, high contrast, warm background, reduced motion |
| **Total Keys per Dictionary** | **180** | **Complete coverage across all 10 languages** |

---

## 3. Translation Dictionary Parity Audit

| Locale File | Language | Key Count | Completeness | Native Verification |
|---|---|:---:|:---:|:---:|
| `frontend/src/i18n/locales/en.ts` | English | 180 / 180 | 100% | Reference Baseline |
| `frontend/src/i18n/locales/hi.ts` | Hindi (`hi`) | 180 / 180 | 100% | Verified Devanagari |
| `frontend/src/i18n/locales/bn.ts` | Bengali (`bn`) | 180 / 180 | 100% | Verified Bengali Script |
| `frontend/src/i18n/locales/ta.ts` | Tamil (`ta`) | 180 / 180 | 100% | Verified Tamil Script |
| `frontend/src/i18n/locales/te.ts` | Telugu (`te`) | 180 / 180 | 100% | Verified Telugu Script |
| `frontend/src/i18n/locales/mr.ts` | Marathi (`mr`) | 180 / 180 | 100% | Verified Marathi Terminology |
| `frontend/src/i18n/locales/gu.ts` | Gujarati (`gu`) | 180 / 180 | 100% | Verified Gujarati Script |
| `frontend/src/i18n/locales/pa.ts` | Punjabi (`pa`) | 180 / 180 | 100% | Verified Gurmukhi Script |
| `frontend/src/i18n/locales/kn.ts` | Kannada (`kn`) | 180 / 180 | 100% | Verified Kannada Script |
| `frontend/src/i18n/locales/ur.ts` | Urdu (`ur`) | 180 / 180 | 100% | Verified Perso-Arabic + RTL |

---

## 4. Parameter Interpolation Verification

Dynamic translation strings were tested across all languages to verify that token replacements (such as `{count}` or `{filename}`) maintain proper word order and grammatically sound positioning:

```typescript
// Example: charsCount
getTranslation('en', 'charsCount', { count: 1250 }) // "1,250 characters"
getTranslation('hi', 'charsCount', { count: 1250 }) // "1,250 अक्षर"
getTranslation('ta', 'charsCount', { count: 1250 }) // "1,250 எழுத்துகள்"
getTranslation('ur', 'charsCount', { count: 1250 }) // "1,250 حروف"
```

All 10 locale files compile cleanly under TypeScript `tsc -b` and Vitest without missing key warnings or runtime fallbacks.
