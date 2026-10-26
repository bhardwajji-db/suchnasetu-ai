import React, { useState, useEffect, useCallback } from 'react';
import { LoginPage } from './LoginPage';
import { SignupPage } from './SignupPage';
import { VerifyEmailPage } from './VerifyEmailPage';
import { ForgotPasswordPage } from './ForgotPasswordPage';
import { ResetPasswordPage } from './ResetPasswordPage';
import type { UserProfile, AuthPageView } from '../../types/api';
import { X } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialView?: AuthPageView;
  currentLanguage: string;
  onLanguageChange: (lang: string) => void;
  onLoginSuccess: (user: UserProfile) => void;
}

const AuthModalContent: React.FC<{
  onClose: () => void;
  initialView: AuthPageView;
  currentLanguage: string;
  onLanguageChange: (lang: string) => void;
  onLoginSuccess: (user: UserProfile) => void;
}> = ({
  onClose,
  initialView,
  currentLanguage,
  onLanguageChange,
  onLoginSuccess,
}) => {
  const [currentView, setCurrentView] = useState<AuthPageView>(initialView);
  const [authEmail, setAuthEmail] = useState<string>('');

  const handleLogin = (user: UserProfile) => {
    onLoginSuccess(user);
    onClose();
  };

  const handleNavigate = (view: AuthPageView, state?: { email?: string }) => {
    if (state?.email) {
      setAuthEmail(state.email);
    }
    setCurrentView(view);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-3 sm:p-4 overflow-y-auto animate-fadeIn"
      role="dialog"
      aria-modal="true"
      aria-label="Citizen Authentication"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div className="relative w-full max-w-lg bg-white rounded-2xl shadow-2xl overflow-hidden my-auto border border-[#E1E7EE]">
        {/* Floating Close Button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 z-20 p-2 rounded-xl text-[#526176] hover:text-[#12233D] hover:bg-slate-100 transition cursor-pointer"
          aria-label="Close authentication modal"
          title="Close authentication modal (Esc)"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Dynamic Auth View */}
        <div className="max-h-[90vh] overflow-y-auto">
          {currentView === 'login' && (
            <LoginPage
              currentLanguage={currentLanguage}
              onLanguageChange={onLanguageChange}
              onLoginSuccess={handleLogin}
              onNavigateAuth={handleNavigate}
              onContinueAsGuest={onClose}
            />
          )}

          {currentView === 'signup' && (
            <SignupPage
              currentLanguage={currentLanguage}
              onLanguageChange={onLanguageChange}
              onNavigateAuth={handleNavigate}
            />
          )}

          {(currentView === 'verify-email' || currentView === 'verify_email') && (
            <VerifyEmailPage
              initialEmail={authEmail}
              currentLanguage={currentLanguage}
              onLanguageChange={onLanguageChange}
              onVerificationSuccess={() => setCurrentView('login')}
              onNavigateLogin={() => setCurrentView('login')}
              onNavigateSignup={() => setCurrentView('signup')}
            />
          )}

          {(currentView === 'forgot-password' || currentView === 'forgot_password') && (
            <ForgotPasswordPage
              currentLanguage={currentLanguage}
              onLanguageChange={onLanguageChange}
              onNavigateAuth={handleNavigate}
            />
          )}

          {(currentView === 'reset-password' || currentView === 'reset_password') && (
            <ResetPasswordPage
              currentLanguage={currentLanguage}
              onLanguageChange={onLanguageChange}
              onResetSuccess={() => setCurrentView('login')}
              onNavigateLogin={() => setCurrentView('login')}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  initialView = 'login',
  currentLanguage,
  onLanguageChange,
  onLoginSuccess,
}) => {
  // Close on Escape key press
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    },
    [isOpen, onClose]
  );

  useEffect(() => {
    if (!isOpen) return;
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, handleKeyDown]);

  if (!isOpen) return null;

  return (
    <AuthModalContent
      onClose={onClose}
      initialView={initialView}
      currentLanguage={currentLanguage}
      onLanguageChange={onLanguageChange}
      onLoginSuccess={onLoginSuccess}
    />
  );
};
