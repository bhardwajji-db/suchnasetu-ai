import { describe, it, expect, beforeEach } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { I18nProvider, useTranslation, LANGUAGE_CODES, SUPPORTED_LANGUAGES, I18N_STORAGE_KEY } from '../i18n';
import { en } from '../i18n/locales/en';
import { hi } from '../i18n/locales/hi';
import { kn } from '../i18n/locales/kn';
import { bn } from '../i18n/locales/bn';
import { ta } from '../i18n/locales/ta';
import { te } from '../i18n/locales/te';
import { mr } from '../i18n/locales/mr';
import { gu } from '../i18n/locales/gu';
import { pa } from '../i18n/locales/pa';
import { ur } from '../i18n/locales/ur';
import { NoticeProvider, useNotice } from '../context/NoticeContext';
import type { LanguageCode } from '../i18n/types';

const allLocales: Record<LanguageCode, Record<string, string>> = {
  en,
  hi,
  kn,
  bn,
  ta,
  te,
  mr,
  gu,
  pa,
  ur,
};

const TestConsumerComponent: React.FC = () => {
  const { language, setLanguage, t, isRtl } = useTranslation();
  const { rawNoticeText, setRawNoticeText } = useNotice();

  return (
    <div>
      <div data-testid="current-lang">{language}</div>
      <div data-testid="is-rtl">{isRtl ? 'RTL' : 'LTR'}</div>
      <div data-testid="dashboard-overview">{t('dashboardOverview')}</div>
      <div data-testid="dashboard-subtitle">{t('dashboardSubtitle')}</div>
      <div data-testid="dropzone-title">{t('dropzoneTitle')}</div>
      <div data-testid="upload-ocr-source">{t('uploadOcrSource')}</div>
      <div data-testid="doc-ingestion-title">{t('docIngestionOcrTitle')}</div>
      <div data-testid="tab-overview">{t('tabOverview')}</div>
      <div data-testid="tab-key-facts">{t('tabKeyFacts')}</div>
      <div data-testid="tab-eligibility">{t('tabEligibility')}</div>
      <div data-testid="tab-evidence">{t('tabEvidence')}</div>
      <div data-testid="tab-action-plan">{t('tabActionPlan')}</div>
      <div data-testid="local-gemma-badge">{t('localGemmaBadge')}</div>
      <div data-testid="reset-workspace">{t('resetWorkspace')}</div>
      <div data-testid="raw-notice-display">{rawNoticeText}</div>
      <button
        data-testid="set-hindi"
        onClick={() => setLanguage('hi')}
      >
        Set Hindi
      </button>
      <button
        data-testid="set-kannada"
        onClick={() => setLanguage('kn')}
      >
        Set Kannada
      </button>
      <button
        data-testid="set-telugu"
        onClick={() => setLanguage('te')}
      >
        Set Telugu
      </button>
      <button
        data-testid="set-marathi"
        onClick={() => setLanguage('mr')}
      >
        Set Marathi
      </button>
      <button
        data-testid="set-gujarati"
        onClick={() => setLanguage('gu')}
      >
        Set Gujarati
      </button>
      <button
        data-testid="set-punjabi"
        onClick={() => setLanguage('pa')}
      >
        Set Punjabi
      </button>
      <button
        data-testid="set-urdu"
        onClick={() => setLanguage('ur')}
      >
        Set Urdu
      </button>
      <button
        data-testid="set-english"
        onClick={() => setLanguage('en')}
      >
        Set English
      </button>
      <button
        data-testid="load-source-notice"
        onClick={() => setRawNoticeText('NORTHERN COALFIELDS LIMITED\nEmployment Notice Ref: NCL/HR/2026/894\nEligibility: Matriculation with ITI')}
      >
        Load Notice
      </button>
    </div>
  );
};

describe('Comprehensive Multilingual Localization & Key Parity Suite', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.lang = 'en';
    document.documentElement.dir = 'ltr';
  });

  it('verifies 100% dictionary key parity across all 10 supported Indic languages', () => {
    const enKeys = Object.keys(en).sort();
    expect(enKeys.length).toBeGreaterThan(500);

    for (const code of LANGUAGE_CODES) {
      const localeDict = allLocales[code];
      const localeKeys = Object.keys(localeDict).sort();

      // Exactly identical keys
      expect(localeKeys.length).toBe(enKeys.length);
      expect(localeKeys).toEqual(enKeys);

      // Verify no empty or undefined values
      for (const key of enKeys) {
        const val = localeDict[key];
        expect(val).toBeDefined();
        expect(typeof val).toBe('string');
        expect(val.trim().length).toBeGreaterThan(0);
      }
    }
  });

  it('switches to Kannada and verifies authentic Indic UI translations', () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <TestConsumerComponent />
        </NoticeProvider>
      </I18nProvider>
    );

    act(() => {
      fireEvent.click(screen.getByTestId('set-kannada'));
    });

    expect(screen.getByTestId('current-lang')).toHaveTextContent('kn');
    expect(screen.getByTestId('dashboard-overview')).toHaveTextContent(kn.dashboardOverview);
    expect(screen.getByTestId('dashboard-subtitle')).toHaveTextContent(kn.dashboardSubtitle);
    expect(screen.getByTestId('dropzone-title')).toHaveTextContent(kn.dropzoneTitle);
    expect(document.documentElement.lang).toBe('kn');
    expect(document.documentElement.dir).toBe('ltr');
    expect(localStorage.getItem(I18N_STORAGE_KEY)).toBe('kn');
  });

  it('switches to Telugu, Marathi, Gujarati, and Punjabi with immediate UI updates', () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <TestConsumerComponent />
        </NoticeProvider>
      </I18nProvider>
    );

    // Telugu
    act(() => {
      fireEvent.click(screen.getByTestId('set-telugu'));
    });
    expect(screen.getByTestId('current-lang')).toHaveTextContent('te');
    expect(screen.getByTestId('dashboard-overview')).toHaveTextContent(te.dashboardOverview);
    expect(document.documentElement.lang).toBe('te');

    // Marathi
    act(() => {
      fireEvent.click(screen.getByTestId('set-marathi'));
    });
    expect(screen.getByTestId('current-lang')).toHaveTextContent('mr');
    expect(screen.getByTestId('dashboard-overview')).toHaveTextContent(mr.dashboardOverview);
    expect(document.documentElement.lang).toBe('mr');

    // Gujarati
    act(() => {
      fireEvent.click(screen.getByTestId('set-gujarati'));
    });
    expect(screen.getByTestId('current-lang')).toHaveTextContent('gu');
    expect(screen.getByTestId('dashboard-overview')).toHaveTextContent(gu.dashboardOverview);
    expect(document.documentElement.lang).toBe('gu');

    // Punjabi
    act(() => {
      fireEvent.click(screen.getByTestId('set-punjabi'));
    });
    expect(screen.getByTestId('current-lang')).toHaveTextContent('pa');
    expect(screen.getByTestId('dashboard-overview')).toHaveTextContent(pa.dashboardOverview);
    expect(document.documentElement.lang).toBe('pa');
  });

  it('verifies Urdu activates right-to-left (RTL) mode and sets html dir="rtl"', () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <TestConsumerComponent />
        </NoticeProvider>
      </I18nProvider>
    );

    act(() => {
      fireEvent.click(screen.getByTestId('set-urdu'));
    });

    expect(screen.getByTestId('current-lang')).toHaveTextContent('ur');
    expect(screen.getByTestId('is-rtl')).toHaveTextContent('RTL');
    expect(screen.getByTestId('dashboard-overview')).toHaveTextContent(ur.dashboardOverview);
    expect(document.documentElement.lang).toBe('ur');
    expect(document.documentElement.dir).toBe('rtl');

    // Switching back to English restores LTR
    act(() => {
      fireEvent.click(screen.getByTestId('set-english'));
    });

    expect(screen.getByTestId('current-lang')).toHaveTextContent('en');
    expect(screen.getByTestId('is-rtl')).toHaveTextContent('LTR');
    expect(document.documentElement.lang).toBe('en');
    expect(document.documentElement.dir).toBe('ltr');
  });

  it('guarantees source notice text is preserved verbatim across language switches without corruption', () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <TestConsumerComponent />
        </NoticeProvider>
      </I18nProvider>
    );

    act(() => {
      fireEvent.click(screen.getByTestId('load-source-notice'));
    });

    const expectedNoticeText = 'NORTHERN COALFIELDS LIMITED\nEmployment Notice Ref: NCL/HR/2026/894\nEligibility: Matriculation with ITI';
    expect(screen.getByTestId('raw-notice-display').textContent).toBe(expectedNoticeText);

    // Switch across multiple languages: kn -> ur -> pa -> en
    act(() => {
      fireEvent.click(screen.getByTestId('set-kannada'));
    });
    expect(screen.getByTestId('raw-notice-display').textContent).toBe(expectedNoticeText);

    act(() => {
      fireEvent.click(screen.getByTestId('set-urdu'));
    });
    expect(screen.getByTestId('raw-notice-display').textContent).toBe(expectedNoticeText);

    act(() => {
      fireEvent.click(screen.getByTestId('set-punjabi'));
    });
    expect(screen.getByTestId('raw-notice-display').textContent).toBe(expectedNoticeText);

    act(() => {
      fireEvent.click(screen.getByTestId('set-english'));
    });
    expect(screen.getByTestId('raw-notice-display').textContent).toBe(expectedNoticeText);
  });

  it('restores preferred language from localStorage on initial load', () => {
    localStorage.setItem(I18N_STORAGE_KEY, 'kn');

    render(
      <I18nProvider>
        <NoticeProvider>
          <TestConsumerComponent />
        </NoticeProvider>
      </I18nProvider>
    );

    expect(screen.getByTestId('current-lang')).toHaveTextContent('kn');
    expect(screen.getByTestId('dashboard-overview')).toHaveTextContent(kn.dashboardOverview);
    expect(document.documentElement.lang).toBe('kn');
  });
  it('verifies seamless switching between English, Hindi, and Kannada for all Ingestion and Workspace UI strings without page reload', () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <TestConsumerComponent />
        </NoticeProvider>
      </I18nProvider>
    );

    // Initial state: English
    expect(screen.getByTestId('current-lang')).toHaveTextContent('en');
    expect(screen.getByTestId('upload-ocr-source')).toHaveTextContent(en.uploadOcrSource);
    expect(screen.getByTestId('doc-ingestion-title')).toHaveTextContent(en.docIngestionOcrTitle);
    expect(screen.getByTestId('tab-overview')).toHaveTextContent(en.tabOverview);
    expect(screen.getByTestId('tab-key-facts')).toHaveTextContent(en.tabKeyFacts);
    expect(screen.getByTestId('tab-eligibility')).toHaveTextContent(en.tabEligibility);
    expect(screen.getByTestId('tab-evidence')).toHaveTextContent(en.tabEvidence);
    expect(screen.getByTestId('tab-action-plan')).toHaveTextContent(en.tabActionPlan);
    expect(screen.getByTestId('local-gemma-badge')).toHaveTextContent(en.localGemmaBadge);
    expect(screen.getByTestId('reset-workspace')).toHaveTextContent(en.resetWorkspace);

    // Switch to Hindi
    act(() => {
      fireEvent.click(screen.getByTestId('set-hindi'));
    });
    expect(screen.getByTestId('current-lang')).toHaveTextContent('hi');
    expect(screen.getByTestId('upload-ocr-source')).toHaveTextContent(hi.uploadOcrSource);
    expect(screen.getByTestId('doc-ingestion-title')).toHaveTextContent(hi.docIngestionOcrTitle);
    expect(screen.getByTestId('tab-overview')).toHaveTextContent(hi.tabOverview);
    expect(screen.getByTestId('tab-key-facts')).toHaveTextContent(hi.tabKeyFacts);
    expect(screen.getByTestId('tab-eligibility')).toHaveTextContent(hi.tabEligibility);
    expect(screen.getByTestId('tab-evidence')).toHaveTextContent(hi.tabEvidence);
    expect(screen.getByTestId('tab-action-plan')).toHaveTextContent(hi.tabActionPlan);
    expect(screen.getByTestId('local-gemma-badge')).toHaveTextContent(hi.localGemmaBadge);
    expect(screen.getByTestId('reset-workspace')).toHaveTextContent(hi.resetWorkspace);
    expect(document.documentElement.lang).toBe('hi');

    // Switch to Kannada
    act(() => {
      fireEvent.click(screen.getByTestId('set-kannada'));
    });
    expect(screen.getByTestId('current-lang')).toHaveTextContent('kn');
    expect(screen.getByTestId('upload-ocr-source')).toHaveTextContent(kn.uploadOcrSource);
    expect(screen.getByTestId('doc-ingestion-title')).toHaveTextContent(kn.docIngestionOcrTitle);
    expect(screen.getByTestId('tab-overview')).toHaveTextContent(kn.tabOverview);
    expect(screen.getByTestId('tab-key-facts')).toHaveTextContent(kn.tabKeyFacts);
    expect(screen.getByTestId('tab-eligibility')).toHaveTextContent(kn.tabEligibility);
    expect(screen.getByTestId('tab-evidence')).toHaveTextContent(kn.tabEvidence);
    expect(screen.getByTestId('tab-action-plan')).toHaveTextContent(kn.tabActionPlan);
    expect(screen.getByTestId('local-gemma-badge')).toHaveTextContent(kn.localGemmaBadge);
    expect(screen.getByTestId('reset-workspace')).toHaveTextContent(kn.resetWorkspace);
    expect(document.documentElement.lang).toBe('kn');

    // Switch back to English
    act(() => {
      fireEvent.click(screen.getByTestId('set-english'));
    });
    expect(screen.getByTestId('current-lang')).toHaveTextContent('en');
    expect(screen.getByTestId('upload-ocr-source')).toHaveTextContent(en.uploadOcrSource);
    expect(screen.getByTestId('doc-ingestion-title')).toHaveTextContent(en.docIngestionOcrTitle);
    expect(screen.getByTestId('local-gemma-badge')).toHaveTextContent(en.localGemmaBadge);
    expect(screen.getByTestId('reset-workspace')).toHaveTextContent(en.resetWorkspace);
    expect(document.documentElement.lang).toBe('en');
  });
});
