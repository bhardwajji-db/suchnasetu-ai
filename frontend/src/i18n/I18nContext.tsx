import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import type { LanguageCode, LanguageMeta, TranslationDictionary } from './types';
import { SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE } from './languages';
import { getTranslation } from './index';

export interface I18nContextType {
  language: LanguageCode;
  setLanguage: (lang: LanguageCode) => void;
  meta: LanguageMeta;
  t: (key: keyof TranslationDictionary, params?: Record<string, string | number>) => string;
  isRtl: boolean;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

export const I18N_STORAGE_KEY = 'suchnasetu_user_language';

export const I18nProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<LanguageCode>(() => {
    try {
      const saved = localStorage.getItem(I18N_STORAGE_KEY);
      if (saved && saved in SUPPORTED_LANGUAGES) {
        return saved as LanguageCode;
      }
    } catch {
      // storage unavailable
    }
    return DEFAULT_LANGUAGE;
  });

  const setLanguage = useCallback((newLang: LanguageCode) => {
    if (newLang in SUPPORTED_LANGUAGES) {
      setLanguageState(newLang);
      try {
        localStorage.setItem(I18N_STORAGE_KEY, newLang);
      } catch (err) {
        console.error('Failed to persist language preference', err);
      }
    }
  }, []);

  const meta = SUPPORTED_LANGUAGES[language] || SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE];
  const isRtl = meta.dir === 'rtl';

  useEffect(() => {
    document.documentElement.lang = language;
    document.documentElement.dir = meta.dir;
  }, [language, meta.dir]);

  const t = useCallback(
    (key: keyof TranslationDictionary, params?: Record<string, string | number>) => {
      return getTranslation(language, key, params);
    },
    [language]
  );

  const value = useMemo(
    () => ({
      language,
      setLanguage,
      meta,
      t,
      isRtl,
    }),
    [language, setLanguage, meta, t, isRtl]
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
};

// oxlint-disable-next-line react/only-export-components
export const useTranslation = (): I18nContextType => {
  const ctx = useContext(I18nContext);
  if (!ctx) {
    const meta = SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE];
    return {
      language: DEFAULT_LANGUAGE,
      setLanguage: () => {},
      meta,
      t: (key: keyof TranslationDictionary, params?: Record<string, string | number>) =>
        getTranslation(DEFAULT_LANGUAGE, key, params),
      isRtl: false,
    };
  }
  return ctx;
};
