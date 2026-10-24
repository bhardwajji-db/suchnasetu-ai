import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation, SUPPORTED_LANGUAGES, LANGUAGE_CODES } from '../i18n';
import { Cpu, CheckCircle2, AlertTriangle, XCircle, Eye, Server, Globe, Menu, X } from 'lucide-react';

export const Header: React.FC = () => {
  const {
    systemHealth,
    providers,
    activeProvider,
    switchProvider,
    selectedLang,
    setSelectedLang,
    openOriginalNoticeModal,
    rawNoticeText,
    setActiveTab,
    isMobileMenuOpen,
    toggleMobileMenu,
  } = useNotice();

  const { setLanguage, t } = useTranslation();

  const getStatusBadge = () => {
    if (!systemHealth) {
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
          <span className="w-2 h-2 rounded-full bg-slate-400 animate-pulse" />
          {t('loading') || 'Checking System...'}
        </span>
      );
    }
    if (systemHealth.overall_status === 'ok') {
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]">
          <CheckCircle2 className="w-3.5 h-3.5 text-[#08785D]" />
          <span>{t('healthReady') || 'System Online'} • {systemHealth.model_name || 'Ready'}</span>
        </span>
      );
    }
    if (systemHealth.overall_status === 'warning') {
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-[#FFF4D6] text-[#92500A] border border-[#FDE68A]">
          <AlertTriangle className="w-3.5 h-3.5 text-[#92500A]" />
          <span>{t('warning') || 'Preflight Warning'}</span>
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-[#FEE8E7] text-[#B42318] border border-[#FCA5A5]">
        <XCircle className="w-3.5 h-3.5 text-[#B42318]" />
        <span>{t('healthError') || 'Provider Offline'}</span>
      </span>
    );
  };

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between px-3 sm:px-6 py-2.5 sm:py-3 bg-white/95 backdrop-blur-sm border-b border-[#E1E7EE] shadow-xs w-full min-w-0">
      {/* Brand Identity & Navigation Toggle */}
      <div className="flex items-center gap-2 sm:gap-4 min-w-0">
        {/* Mobile Hamburger Drawer Toggle */}
        <button
          type="button"
          onClick={toggleMobileMenu}
          className="md:hidden p-1.5 sm:p-2 rounded-xl text-[#12233D] hover:bg-[#E8F7F0] hover:text-[#08785D] border border-[#E1E7EE] transition cursor-pointer"
          aria-label={isMobileMenuOpen ? 'Close navigation drawer' : 'Open navigation drawer'}
          title={isMobileMenuOpen ? 'Close navigation drawer' : 'Open navigation drawer'}
        >
          {isMobileMenuOpen ? <X className="w-5 h-5 text-[#B42318]" /> : <Menu className="w-5 h-5 text-[#08785D]" />}
        </button>

        <button
          type="button"
          onClick={() => setActiveTab(0)}
          className="flex items-center gap-2 sm:gap-2.5 text-left group cursor-pointer focus:outline-hidden min-w-0"
          title="Return to Home"
        >
          <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-gradient-to-br from-[#08785D] to-[#06664E] flex items-center justify-center shadow-xs shadow-[#08785D]/20 font-black text-white text-base sm:text-lg shrink-0">
            स
          </div>
          <div className="flex flex-col min-w-0">
            <div className="flex items-center gap-1.5 leading-none">
              <span className="text-base sm:text-lg font-extrabold tracking-tight text-[#12233D] truncate">
                Suchna<span className="text-[#08785D]">Setu</span> <span className="hidden xs:inline">AI</span>
              </span>
              <span className="text-[9px] sm:text-[10px] font-mono uppercase bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2] px-1 py-0.2 sm:px-1.5 sm:py-0.5 rounded-md font-bold shrink-0">
                PS02
              </span>
            </div>
            <span className="text-[11px] font-medium text-[#526176] mt-0.5 hidden md:inline truncate">
              Understand the notice. Know your next step.
            </span>
          </div>
        </button>

        <span className="hidden xl:inline-block text-xs text-[#68778B] border-l border-[#E1E7EE] pl-3 py-1">
          Notice-to-Action Accessibility Assistant
        </span>
      </div>

      {/* Center / Right Control Cluster */}
      <div className="flex items-center gap-1.5 sm:gap-3 shrink-0">
        {/* System Health Badge */}
        <div className="hidden md:flex">{getStatusBadge()}</div>

        {/* Original Notice Document Viewer Button */}
        <button
          type="button"
          onClick={openOriginalNoticeModal}
          disabled={!rawNoticeText}
          className="flex items-center gap-1.5 p-1.5 sm:px-3 sm:py-1.5 rounded-lg text-xs font-semibold text-[#12233D] hover:text-[#08785D] bg-[#F8FAFC] hover:bg-[#E8F7F0] border border-[#E1E7EE] hover:border-[#B7E7D2] transition disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
          title="View Original Ground-Truth Notice Document"
          aria-label="View Original Ground-Truth Notice Document"
        >
          <Eye className="w-4 h-4 sm:w-3.5 sm:h-3.5 text-[#08785D]" />
          <span className="hidden sm:inline">{t('viewOriginalNotice') || 'Original Notice'}</span>
        </button>

        {/* Local Privacy & Model Badge */}
        <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-[#526176] bg-[#F8FAFC] border border-[#E1E7EE]">
          <Cpu className="w-3.5 h-3.5 text-[#08785D]" />
          <span>Local Gemma 4 (100% Privacy)</span>
        </div>

        {/* LLM Provider Selector */}
        <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium text-[#526176] bg-[#F8FAFC] border border-[#E1E7EE]">
          <Server className="w-3.5 h-3.5 text-[#08785D]" />
          <select
            value={activeProvider}
            onChange={(e) => switchProvider(e.target.value)}
            className="bg-transparent text-[#12233D] text-xs font-semibold outline-hidden cursor-pointer py-0.5"
            title="Select AI Inference Provider"
            aria-label="Select AI Inference Provider"
          >
            {providers.length > 0 ? (
              providers.map((p) => (
                <option key={p.id} value={p.id} className="bg-white text-[#12233D]">
                  {p.name} {p.status === 'ready' ? '✓' : ''}
                </option>
              ))
            ) : (
              <option value="ollama" className="bg-white text-[#12233D]">
                Local Ollama
              </option>
            )}
          </select>
        </div>

        {/* 10-Language Switcher Cluster */}
        <div className="flex items-center gap-0.5 sm:gap-1 p-0.5 rounded-lg bg-[#F8FAFC] border border-[#E1E7EE]">
          <div className="hidden md:flex items-center gap-1 pl-1">
            <Globe className="w-3.5 h-3.5 text-[#08785D]" />
          </div>
          <button
            type="button"
            onClick={() => {
              setSelectedLang('en');
              setLanguage('en');
            }}
            className={`px-1.5 sm:px-2 py-1 rounded-md text-[11px] sm:text-xs font-bold transition-all cursor-pointer ${
              selectedLang === 'en'
                ? 'bg-[#08785D] text-white shadow-xs'
                : 'text-[#526176] hover:text-[#12233D]'
            }`}
            aria-label={selectedLang === 'en' ? 'English language selected' : 'Switch interface language to English (अंग्रेजी चुनें)'}
            aria-pressed={selectedLang === 'en'}
          >
            EN
          </button>
          <button
            type="button"
            onClick={() => {
              setSelectedLang('hi');
              setLanguage('hi');
            }}
            className={`px-1.5 sm:px-2 py-1 rounded-md text-[11px] sm:text-xs font-bold transition-all cursor-pointer ${
              selectedLang === 'hi'
                ? 'bg-[#08785D] text-white shadow-xs'
                : 'text-[#526176] hover:text-[#12233D]'
            }`}
            aria-label={selectedLang === 'hi' ? 'हिन्दी भाषा चयनित है' : 'Switch interface language to Hindi (हिन्दी भाषा चुनें)'}
            aria-pressed={selectedLang === 'hi'}
          >
            हिन्दी
          </button>
          <select
            value={selectedLang}
            onChange={(e) => {
              const code = e.target.value as any;
              setSelectedLang(code);
              setLanguage(code);
            }}
            aria-label="Select Website Language (10 Indian Languages)"
            title="Select Website Language"
            className="bg-transparent text-[#12233D] text-[11px] sm:text-xs font-bold px-1 sm:px-1.5 py-1 rounded-md border-l border-[#E1E7EE] outline-hidden cursor-pointer max-w-[85px] sm:max-w-none"
          >
            {LANGUAGE_CODES.map((code) => (
              <option key={code} value={code} className="bg-white text-[#12233D]">
                {SUPPORTED_LANGUAGES[code].nativeName} ({SUPPORTED_LANGUAGES[code].name})
              </option>
            ))}
          </select>
        </div>
      </div>
    </header>
  );
};
