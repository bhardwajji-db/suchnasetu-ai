import React, { useState, useEffect, useRef } from 'react';

import { useNotice } from '../context/NoticeContext';

import { useTranslation, SUPPORTED_LANGUAGES, LANGUAGE_CODES } from '../i18n';

import { Cpu, CheckCircle2, AlertTriangle, XCircle, Eye, Server, Globe, Menu, X, LogOut, Sun, Moon, Bell, User, Settings, BookMarked, ChevronDown } from 'lucide-react';

import { AuthModal } from './auth/AuthModal';

import type { AuthPageView } from '../types/api';



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
    isAuthModalOpen,
    setIsAuthModalOpen,
    currentUser,
    setCurrentUser,
    logout,
    theme,
    toggleTheme,
    unreadNotificationsCount,
    openAuthPage,
  } = useNotice();

  const { setLanguage, t } = useTranslation();

  const [authInitialView, setAuthInitialView] = useState<AuthPageView>('login');

  useEffect(() => {
    try {
      if (typeof window !== 'undefined') {
        const path = (window.location.pathname || '').toLowerCase();
        const search = window.location.search || '';
        const params = new URLSearchParams(search);
        if (path.includes('verify-email') || path.includes('verify_email') || params.has('token')) {
          setAuthInitialView('verify_email');
          setIsAuthModalOpen(true);
        } else if (path.includes('reset-password') || path.includes('reset_password')) {
          setAuthInitialView('reset_password');
          setIsAuthModalOpen(true);
        } else if (path.includes('login')) {
          setAuthInitialView('login');
          setIsAuthModalOpen(true);
        } else if (path.includes('signup')) {
          setAuthInitialView('signup');
          setIsAuthModalOpen(true);
        } else if (path.includes('forgot-password') || path.includes('forgot_password')) {
          setAuthInitialView('forgot_password');
          setIsAuthModalOpen(true);
        }
      }
    } catch {}
  }, [setIsAuthModalOpen]);

  const handleLogout = async () => {
    await logout();
  };



  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const profileMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(e.target as Node)) {
        setIsProfileMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getInitials = (name?: string, email?: string): string => {
    if (name && name.trim()) {
      const parts = name.trim().split(/\s+/);
      if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
      }
      return parts[0].slice(0, 2).toUpperCase();
    }
    if (email && email.trim()) {
      return email.slice(0, 2).toUpperCase();
    }
    return 'CZ';
  };

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

          title={rawNoticeText?.trim() ? "View Original Ground-Truth Notice Document" : "Load or paste a notice to view the original document"}

          aria-label={rawNoticeText?.trim() ? "View Original Ground-Truth Notice Document" : "View Original Ground-Truth Notice Document (Disabled: No notice loaded)"}

        >

          <Eye className="w-4 h-4 sm:w-3.5 sm:h-3.5 text-[#08785D]" />

          <span className="hidden sm:inline">{t('viewOriginalNotice') || 'Original Notice'}</span>

        </button>



        {/* Local Privacy & Model Badge */}

        <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-[#526176] bg-[#F8FAFC] border border-[#E1E7EE]">

          <Cpu className="w-3.5 h-3.5 text-[#08785D]" />

          <span>{t('localGemmaBadge')}</span>

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



        {/* Notification Center Access Button */}
        <button
          type="button"
          onClick={() => {
            setActiveTab(0);
            setTimeout(() => {
              const el = document.getElementById('notification-center-section');
              el?.scrollIntoView({ behavior: 'smooth' });
            }, 100);
          }}
          className="relative flex items-center justify-center p-1.5 sm:px-2.5 sm:py-1.5 rounded-lg text-xs font-semibold text-[#12233D] hover:text-[#08785D] bg-[#F8FAFC] hover:bg-[#E8F7F0] border border-[#E1E7EE] hover:border-[#B7E7D2] transition cursor-pointer"
          title="Notification Center"
          aria-label="Open notifications"
        >
          <Bell className="w-4 h-4 text-[#526176]" />
          {unreadNotificationsCount > 0 && (
            <span className="absolute -top-1 -right-1 min-w-[16px] h-4 px-1 rounded-full bg-purple-600 text-white text-[9px] font-bold flex items-center justify-center animate-pulse">
              {unreadNotificationsCount > 9 ? '9+' : unreadNotificationsCount}
            </span>
          )}
        </button>

        {/* Single Unified Language Selector */}
        <div className="flex items-center gap-1.5 px-2 py-1.5 rounded-lg bg-[#F8FAFC] border border-[#E1E7EE]">
          <Globe className="w-3.5 h-3.5 text-[#08785D] shrink-0" />
          <select
            value={selectedLang}
            onChange={(e) => {
              const code = e.target.value as any;
              setSelectedLang(code);
              setLanguage(code);
            }}
            aria-label="Select Website Language"
            title="Select Website Language"
            className="bg-transparent text-[#12233D] text-[11px] sm:text-xs font-bold outline-hidden cursor-pointer"
          >
            {LANGUAGE_CODES.map((code) => (
              <option key={code} value={code} className="bg-white text-[#12233D]">
                {SUPPORTED_LANGUAGES[code].nativeName} ({SUPPORTED_LANGUAGES[code].name})
              </option>
            ))}
          </select>
        </div>
        {/* Dark Theme Quick Toggle */}
        <button
          type="button"
          onClick={toggleTheme}
          className="flex items-center gap-1.5 p-1.5 sm:px-2.5 sm:py-1.5 rounded-lg text-xs font-semibold text-[#12233D] hover:text-[#08785D] bg-[#F8FAFC] hover:bg-[#E8F7F0] border border-[#E1E7EE] hover:border-[#B7E7D2] transition cursor-pointer"
          title={theme === 'dark' ? 'Switch to light theme (Slate + Deep Green)' : 'Switch to dark theme (Midnight Navy + Teal)'}
          aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
        >
          {theme === 'dark' ? (
            <Sun className="w-4 h-4 text-[#14B8A6]" />
          ) : (
            <Moon className="w-4 h-4 text-[#526176]" />
          )}
          <span className="hidden xl:inline text-[11px] font-medium">
            {theme === 'dark' ? 'Light' : 'Dark'}
          </span>
        </button>

        {/* Top-Right Profile Avatar & Dropdown / Guest Auth CTA */}
        <div className="relative" ref={profileMenuRef}>
          {currentUser ? (
            <div>
              <button
                type="button"
                onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
                className="flex items-center gap-2 p-1 pl-1.5 pr-2 rounded-xl text-xs font-semibold bg-[#F8FAFC] hover:bg-[#E8F7F0] border border-[#E1E7EE] hover:border-[#B7E7D2] transition cursor-pointer focus:outline-hidden focus:ring-2 focus:ring-[#08785D]"
                aria-expanded={isProfileMenuOpen}
                aria-haspopup="true"
                aria-label="Citizen Account Menu"
                title={`${currentUser.name} (${currentUser.email})`}
              >
                <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#08785D] to-[#06664E] text-white flex items-center justify-center font-bold text-xs shadow-2xs">
                  {getInitials(currentUser.name, currentUser.email)}
                </div>
                <span className="hidden sm:inline font-bold text-[#12233D] max-w-[100px] truncate">
                  {currentUser.name}
                </span>
                <ChevronDown className={`w-3.5 h-3.5 text-[#68778B] transition-transform duration-200 ${isProfileMenuOpen ? 'rotate-180' : ''}`} />
              </button>

              {isProfileMenuOpen && (
                <div className="absolute right-0 mt-2 w-64 rounded-2xl bg-white border border-[#E1E7EE] shadow-xl py-2 z-50 animate-in fade-in slide-in-from-top-1 duration-150">
                  {/* User Profile Summary */}
                  <div className="px-4 py-3 border-b border-[#E1E7EE] space-y-1">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#08785D] to-[#06664E] text-white flex items-center justify-center font-bold text-xs shrink-0 shadow-2xs">
                        {getInitials(currentUser.name, currentUser.email)}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-1.5">
                          <span className="text-xs font-bold text-[#12233D] truncate">{currentUser.name}</span>
                          {currentUser.is_verified && (
                            <span className="text-[9px] font-bold text-[#08785D] bg-[#E8F7F0] border border-[#B7E7D2] px-1 py-0.2 rounded-sm shrink-0">
                              Verified
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-[#64748B] font-mono truncate" title={currentUser.email}>
                          {currentUser.email}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Account Actions */}
                  <div className="p-1.5 space-y-0.5">
                    <button
                      type="button"
                      onClick={() => {
                        setActiveTab(10);
                        setIsProfileMenuOpen(false);
                      }}
                      className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold text-[#12233D] hover:bg-[#F8FAFC] hover:text-[#08785D] transition cursor-pointer"
                    >
                      <Settings className="w-4 h-4 text-[#68778B]" />
                      <span>Settings & Diagnostics</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => {
                        setActiveTab(9);
                        setIsProfileMenuOpen(false);
                      }}
                      className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold text-[#12233D] hover:bg-[#F8FAFC] hover:text-[#08785D] transition cursor-pointer"
                    >
                      <BookMarked className="w-4 h-4 text-[#68778B]" />
                      <span>Saved Notices Tracker</span>
                    </button>
                  </div>

                  {/* Sign Out Action */}
                  <div className="pt-1.5 px-1.5 border-t border-[#E1E7EE]">
                    <button
                      type="button"
                      onClick={async () => {
                        setIsProfileMenuOpen(false);
                        await handleLogout();
                      }}
                      className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold text-[#B42318] hover:bg-[#FEE8E7] transition cursor-pointer"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <button
              type="button"
              onClick={() => openAuthPage('login')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-white bg-[#08785D] hover:bg-[#06664E] shadow-2xs transition cursor-pointer"
              aria-label="Sign In or Create Citizen Account"
              title="Sign In to access persistent notices and tasks"
            >
              <User className="w-3.5 h-3.5" />
              <span>Sign In</span>
            </button>
          )}
        </div>


      </div>

      <AuthModal

        isOpen={isAuthModalOpen}

        onClose={() => setIsAuthModalOpen(false)}
        initialView={authInitialView}

        currentLanguage={selectedLang}

        onLanguageChange={(lang) => {

          setSelectedLang(lang as any);

          setLanguage(lang as any);

        }}

        onLoginSuccess={(user) => setCurrentUser(user)}

      />

    </header>

  );

};

