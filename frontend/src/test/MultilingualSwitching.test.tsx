import { describe, it, expect, beforeEach } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { I18nProvider, useTranslation, LANGUAGE_CODES, SUPPORTED_LANGUAGES } from '../i18n';
import { NoticeProvider, useNotice } from '../context/NoticeContext';
import { Header } from '../components/Header';
import { Sidebar } from '../components/Sidebar';

const MultilingualTestApp: React.FC = () => {
  const { language, setLanguage, t, isRtl } = useTranslation();
  const { selectedLang, setSelectedLang } = useNotice();

  return (
    <div>
      <Header />
      <Sidebar />
      <div data-testid="current-lang">{language}</div>
      <div data-testid="notice-lang">{selectedLang}</div>
      <div data-testid="is-rtl">{isRtl ? 'RTL' : 'LTR'}</div>
      <div data-testid="nav-dashboard-text">{t('navDashboard')}</div>
      <div data-testid="nav-facts-text">{t('navFacts')}</div>
      <div data-testid="sample-notices-text">{t('sampleNotices')}</div>
      <button data-testid="switch-to-hi" onClick={() => { setLanguage('hi'); setSelectedLang('hi'); }}>
        Force Hindi
      </button>
      <button data-testid="switch-to-ur" onClick={() => { setLanguage('ur'); setSelectedLang('ur'); }}>
        Force Urdu
      </button>
      <button data-testid="switch-to-bn" onClick={() => { setLanguage('bn'); setSelectedLang('bn'); }}>
        Force Bengali
      </button>
      <button data-testid="switch-to-ta" onClick={() => { setLanguage('ta'); setSelectedLang('ta'); }}>
        Force Tamil
      </button>
    </div>
  );
};

describe('Multilingual Language Switching & RTL Engine', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.lang = 'en';
    document.documentElement.dir = 'ltr';
  });

  it('renders with English by default and propagates language across contexts', () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <MultilingualTestApp />
        </NoticeProvider>
      </I18nProvider>
    );

    expect(screen.getByTestId('current-lang')).toHaveTextContent('en');
    expect(screen.getByTestId('notice-lang')).toHaveTextContent('en');
    expect(screen.getByTestId('is-rtl')).toHaveTextContent('LTR');
    expect(screen.getByTestId('nav-dashboard-text')).toHaveTextContent('Dashboard');
    expect(screen.getByTestId('nav-facts-text')).toHaveTextContent('2. Grounded Facts');
  });

  it('switches to Hindi immediately and updates UI labels across components', () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <MultilingualTestApp />
        </NoticeProvider>
      </I18nProvider>
    );

    // Switch to Hindi via single language selector dropdown in Header
    const langSelect = screen.getByRole('combobox', { name: /Select Website Language/i });
    act(() => {
      fireEvent.change(langSelect, { target: { value: 'hi' } });
    });

    expect(screen.getByTestId('current-lang')).toHaveTextContent('hi');
    expect(screen.getByTestId('notice-lang')).toHaveTextContent('hi');
    expect(screen.getByTestId('nav-dashboard-text')).toHaveTextContent('डैशबोर्ड');
    expect(screen.getByTestId('nav-facts-text')).toHaveTextContent('2. प्रमाणित तथ्य');
    expect(screen.getByTestId('sample-notices-text')).toHaveTextContent('नमूना सूचनाएं');
    expect(document.documentElement.lang).toBe('hi');
    expect(document.documentElement.dir).toBe('ltr');
  });

  it('switches to Urdu and properly enforces RTL document direction', () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <MultilingualTestApp />
        </NoticeProvider>
      </I18nProvider>
    );

    const urduBtn = screen.getByTestId('switch-to-ur');
    act(() => {
      fireEvent.click(urduBtn);
    });

    expect(screen.getByTestId('current-lang')).toHaveTextContent('ur');
    expect(screen.getByTestId('notice-lang')).toHaveTextContent('ur');
    expect(screen.getByTestId('is-rtl')).toHaveTextContent('RTL');
    expect(screen.getByTestId('nav-dashboard-text')).toHaveTextContent('ڈیش بورڈ');
    expect(screen.getByTestId('nav-facts-text')).toHaveTextContent('2. مصدقہ حقائق');
    expect(document.documentElement.lang).toBe('ur');
    expect(document.documentElement.dir).toBe('rtl');
  });

  it('switches to Bengali and updates UI labels immediately', () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <MultilingualTestApp />
        </NoticeProvider>
      </I18nProvider>
    );

    const bnBtn = screen.getByTestId('switch-to-bn');
    act(() => {
      fireEvent.click(bnBtn);
    });

    expect(screen.getByTestId('current-lang')).toHaveTextContent('bn');
    expect(screen.getByTestId('notice-lang')).toHaveTextContent('bn');
    expect(screen.getByTestId('nav-dashboard-text')).toHaveTextContent('ড্যাশবোর্ড');
    expect(document.documentElement.lang).toBe('bn');
  });

  it('switches to Tamil and updates UI labels immediately', () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <MultilingualTestApp />
        </NoticeProvider>
      </I18nProvider>
    );

    const taBtn = screen.getByTestId('switch-to-ta');
    act(() => {
      fireEvent.click(taBtn);
    });

    expect(screen.getByTestId('current-lang')).toHaveTextContent('ta');
    expect(screen.getByTestId('notice-lang')).toHaveTextContent('ta');
    expect(screen.getByTestId('nav-dashboard-text')).toHaveTextContent('டாஷ்போர்டு');
    expect(document.documentElement.lang).toBe('ta');
  });

  it('supports all 10 defined Indian languages in the metadata list', () => {
    expect(LANGUAGE_CODES).toHaveLength(10);
    for (const code of LANGUAGE_CODES) {
      expect(SUPPORTED_LANGUAGES[code]).toBeDefined();
      expect(SUPPORTED_LANGUAGES[code].code).toBe(code);
      expect(SUPPORTED_LANGUAGES[code].nativeName).toBeTruthy();
    }
  });
});
