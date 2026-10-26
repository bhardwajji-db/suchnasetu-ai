import React from 'react';
import { BrandLogo } from '../BrandLogo';
import { ShieldCheck, Globe } from 'lucide-react';
import { useTranslation, SUPPORTED_LANGUAGES, type LanguageCode } from '../../i18n';

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle: string;
  currentLanguage?: string;
  onLanguageChange?: (lang: string) => void;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({
  children,
  title,
  subtitle,
  currentLanguage,
  onLanguageChange,
}) => {
  const { t, language, setLanguage } = useTranslation();
  const activeLang = (currentLanguage || language) as LanguageCode;

  const handleLangSelect = (code: LanguageCode) => {
    setLanguage(code);
    if (onLanguageChange) {
      onLanguageChange(code);
    }
  };

  return (
    <div className="auth-shell">
      {/* Top Header */}
      <header className="auth-header">
        <div className="auth-header-container">
          <BrandLogo size="md" />

          <div className="auth-header-actions">
            <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs font-medium text-[#526176] bg-[#F8FAFC] border border-[#CBD5E1]" role="group" aria-label="Language selection">
              <Globe className="w-3.5 h-3.5 text-[#08785D]" />
              <select
                value={activeLang}
                onChange={(e) => handleLangSelect(e.target.value as LanguageCode)}
                className="bg-transparent text-[#12233D] text-xs font-semibold outline-hidden cursor-pointer py-0.5"
                title="Select interface language"
                aria-label="Select interface language"
              >
                {Object.values(SUPPORTED_LANGUAGES).map((meta) => (
                  <option key={meta.code} value={meta.code} className="bg-white text-[#12233D]">
                    {meta.nativeName} ({meta.name})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="auth-main-content">
        <div className="auth-card-wrapper">
          <div className="auth-card-top-accent" />

          <div className="auth-card-header">
            <div className="auth-badge-kicker">
              <ShieldCheck size={14} className="text-emerald-600" />
              <span>{t('secureCitizenAccess')}</span>
            </div>
            <h1 className="auth-card-title">{title}</h1>
            <p className="auth-card-subtitle">{subtitle}</p>
          </div>

          <div className="auth-card-body">
            {children}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="auth-footer">
        <div className="auth-footer-container">
          <span>SuchnaSetu AI &bull; सूचना + सेतु</span>
          <span>{t('appSubtitle')} &bull; Gemma 4 Integration</span>
        </div>
      </footer>
    </div>
  );
};
