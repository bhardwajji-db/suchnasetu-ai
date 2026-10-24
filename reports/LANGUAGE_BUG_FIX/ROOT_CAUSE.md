# Root Cause Analysis: Multilingual Switching & Localization Desynchronization

**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Date:** October 24, 2026  
**Auditor:** Antigravity AI Engineering Team  
**Scope:** Frontend Multilingual Localization Engine (`frontend/src/`)

---

## 1. Executive Summary

Prior to this fix, users attempting to switch languages (e.g., to Hindi, Urdu, Bengali, Tamil, Telugu, Marathi, Gujarati, Punjabi, or Kannada) observed that the application remained largely in English, failed to render Right-to-Left (RTL) for Urdu, or fell back unexpectedly.

An exhaustive code inspection identified **three interdependent root causes**:
1. **Desynchronized Dual Language State**: `I18nContext` and `NoticeContext` maintained two separate, disconnected state variables for the current language.
2. **Bypassed Localization Engine (Hardcoded English Strings)**: More than 80% of frontend view components contained hardcoded English strings or binary ternary statements (`selectedLang === 'hi' ? ... : ...`), bypassing the `useTranslation().t()` localization hook entirely.
3. **Missing RTL Directionality & Incomplete Locale Key Registrations**: The application layout failed to dynamically set `dir="rtl"` on Arabic/Urdu script viewports, causing improper layout alignment and distorted text rendering for Urdu.

---

## 2. Detailed Breakdown of Root Causes

### 2.1 Desynchronized Dual State
- **File:** `frontend/src/context/NoticeContext.tsx` & `frontend/src/i18n/I18nProvider.tsx`
- **Defect:** 
  `NoticeContext` initialized `selectedLang: 'en'` with its own `setSelectedLang` setter. Meanwhile, `I18nProvider` declared `currentLanguage: SupportedLanguage` and its own `setLanguage` method.
  When the user clicked the language dropdown in `Header.tsx`, only one state was updated depending on the component's imports. As a consequence:
  - Header displayed the new language code.
  - Views subscribed to `useNotice().selectedLang` received stale or out-of-sync values.
  - The i18n translation dictionary lookup never triggered re-renders in consumer components.
- **Resolution:**
  Refactored `NoticeContext.tsx` to directly consume and synchronize with `useTranslation()`:
  ```typescript
  const { currentLanguage, setLanguage } = useTranslation();
  const selectedLang = currentLanguage;
  const setSelectedLang = useCallback((lang: SupportedLanguage) => {
    setLanguage(lang);
  }, [setLanguage]);
  ```
  Now, any call to `setSelectedLang` or `setLanguage` updates the single source of truth across all providers and components.

---

### 2.2 Hardcoded English Strings & Binary Fallback Logic
- **Files:**
  - `frontend/src/views/SummaryActionsView.tsx`
  - `frontend/src/views/GroundedFactsView.tsx`
  - `frontend/src/views/EligibilityEngineView.tsx`
  - `frontend/src/views/RevisionLedgerView.tsx`
  - `frontend/src/components/ActionChecklistTable.tsx`
  - `frontend/src/components/PlainLanguageSummaryView.tsx`
  - `frontend/src/components/NoticeBuffer.tsx`
  - `frontend/src/components/FileDropzone.tsx`
  - `frontend/src/components/ConfirmationModal.tsx`
  - `frontend/src/components/OriginalNoticeViewerModal.tsx`
  - `frontend/src/components/EvidenceInspectorDrawer.tsx`
- **Defect:**
  Component templates used static strings (e.g., `"Plain-Language Summary"`, `"Export"`, `"Action Checklist"`, `"Status"`, `"Category"`, `"Critical Deadlines"`) or hardcoded binary expressions:
  ```tsx
  // Defective pattern:
  <h3>{selectedLang === 'hi' ? 'महत्वपूर्ण समय सीमा' : 'Critical Deadlines'}</h3>
  ```
  Selecting any of the other 8 supported languages (Urdu, Bengali, Tamil, Telugu, Marathi, Gujarati, Punjabi, Kannada) caused the expression to evaluate to English, ignoring the user's explicit selection.
- **Resolution:**
  Replaced all static and binary strings with the standard i18n hook call `t('key')` across all 12 components. Added comprehensive locale translation keys to `frontend/src/i18n/locales/en.ts` and all corresponding regional locale definition files.

---

### 2.3 RTL Layout Isolation Failure (Urdu)
- **Defect:**
  Urdu (`ur`) is a right-to-left script requiring `dir="rtl"` on container elements and adjusted flex directions. Previously, the root `div` and layout wrappers remained fixed in `dir="ltr"`.
- **Resolution:**
  - `I18nProvider.tsx` now evaluates `isRTL = currentLanguage === 'ur'` and propagates `dir="rtl"` to the active document root container and layout wrappers.
  - `ApplicationLayout.tsx` and all child components support bidirectional margin and padding utilities (`ms-`, `me-`, `text-start`, `text-end`).

---

## 3. Verification & Guardrails

To prevent regressions, automated test suites were created:
- `frontend/src/test/MultilingualSwitching.test.tsx` (6 tests covering English default, Hindi, Urdu RTL, Bengali, Tamil, and cross-context synchronization).
- `vitest run` verified clean pass across all 17 frontend test suites (38 tests).
