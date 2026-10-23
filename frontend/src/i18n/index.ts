import type { LanguageCode, TranslationDictionary } from './types';
import { DEFAULT_LANGUAGE } from './languages';
import { en } from './locales/en';
import { hi } from './locales/hi';
import { bn } from './locales/bn';
import { ta } from './locales/ta';
import { te } from './locales/te';
import { mr } from './locales/mr';
import { gu } from './locales/gu';
import { pa } from './locales/pa';
import { kn } from './locales/kn';
import { ur } from './locales/ur';

export * from './types';
export * from './languages';
export * from './I18nContext';

export const DICTIONARIES: Record<LanguageCode, TranslationDictionary> = {
  en,
  hi,
  bn,
  ta,
  te,
  mr,
  gu,
  pa,
  kn,
  ur,
};

/**
 * Pure translation lookup with fallback to English and parameter interpolation.
 * Example: getTranslation('hi', 'charsCount', { count: 42 }) => "42 अक्षर"
 */
export function getTranslation(
  lang: LanguageCode,
  key: keyof TranslationDictionary,
  params?: Record<string, string | number>
): string {
  const dict = DICTIONARIES[lang] || DICTIONARIES[DEFAULT_LANGUAGE];
  let text = dict[key] || DICTIONARIES[DEFAULT_LANGUAGE][key] || String(key);

  if (params) {
    for (const [pKey, pVal] of Object.entries(params)) {
      text = text.replace(new RegExp(`\\{${pKey}\\}`, 'g'), String(pVal));
    }
  }

  return text;
}
