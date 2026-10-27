import React, { useState } from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation, SUPPORTED_LANGUAGES, type LanguageCode } from '../i18n';
import { loginAccount, registerAccount } from '../services/api';
import { BrandLogo } from '../components/BrandLogo';
import {
  Mail,
  Lock,
  User,
  Eye,
  EyeOff,
  LogIn,
  UserPlus,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  Globe,
  Sun,
  Moon,
  RotateCw,
} from 'lucide-react';

interface AuthPageViewProps {
  initialMode?: 'login' | 'signup';
  onComplete?: () => void;
}

export const AuthPageView: React.FC<AuthPageViewProps> = ({
  initialMode = 'login',
  onComplete,
}) => {
  const { theme, toggleTheme, setCurrentUser, setActiveTab, setSelectedLang } = useNotice();
  const { t, language, setLanguage } = useTranslation();

  const [mode, setMode] = useState<'login' | 'signup'>(initialMode);
  const [email, setEmail] = useState(() => {
    try {
      return localStorage.getItem('suchnasetu_last_email') || 'diwakarbhardwaj477@gmail.com';
    } catch {
      return 'diwakarbhardwaj477@gmail.com';
    }
  });
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);

  const handleReturn = () => {
    if (onComplete) {
      onComplete();
    } else {
      setActiveTab(0);
    }
  };

  const handleLanguageSelect = (code: LanguageCode) => {
    setLanguage(code);
    if (setSelectedLang) {
      setSelectedLang(code);
    }
  };

  // Login handler
  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessNotice(null);

    const cleanEmail = email.trim().toLowerCase();
    if (!cleanEmail || !cleanEmail.includes('@')) {
      setError(t('validEmailError') || 'Please enter a valid email address.');
      return;
    }
    if (!password) {
      setError(t('passwordRequiredError') || 'Password is required.');
      return;
    }

    setIsLoading(true);
    try {
      const res = await loginAccount({
        email: cleanEmail,
        password,
        rememberMe,
      });

      if (res.user) {
        setCurrentUser(res.user);
        try {
          localStorage.setItem('suchnasetu_last_email', cleanEmail);
        } catch {
          // ignore
        }
      }
      handleReturn();
    } catch (err: any) {
      const msg = err.message || 'Invalid email or password.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  // Registration handler
  const handleSignupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessNotice(null);

    const cleanUsername = name.trim();
    const cleanEmail = email.trim().toLowerCase();

    if (!cleanUsername || cleanUsername.length < 2) {
      setError('Username must be at least 2 characters long.');
      return;
    }
    if (cleanUsername.length > 100) {
      setError('Username cannot exceed 100 characters.');
      return;
    }
    if (!cleanEmail || !cleanEmail.includes('@') || !cleanEmail.includes('.')) {
      setError(t('validEmailError') || 'Please enter a valid email address.');
      return;
    }
    if (password.length < 8) {
      setError(t('signupPasswordMinLengthError') || 'Password must be at least 8 characters long.');
      return;
    }

    setIsLoading(true);
    try {
      const res = await registerAccount({
        username: cleanUsername,
        name: cleanUsername,
        email: cleanEmail,
        password,
      });

      if (res.user) {
        setCurrentUser(res.user);
      }
      setSuccessNotice('Account created successfully! Welcome to SochnaSetu AI.');
      setTimeout(() => {
        handleReturn();
      }, 700);
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please check your details.');
    } finally {
      setIsLoading(false);
    }
  };



  return (
    <div
      data-view="auth-page"
      className={`auth-page-root min-h-screen w-full flex flex-col overflow-x-hidden font-sans selection:bg-[#08785D] selection:text-white pb-12 transition-colors duration-200 ${
        theme === 'dark'
          ? 'bg-[#0B1220] text-[#E8EEF7]'
          : 'bg-gradient-to-br from-[#F5F8FA] via-white to-[#E8F7F0]/30 text-[#12233D]'
      }`}
    >
      {/* Top Navigation Bar */}
      <header className="w-full bg-white/90 dark:bg-[#0F172A]/90 backdrop-blur-md border-b border-[#E1E7EE] dark:border-[#29384D] sticky top-0 z-30 px-3 sm:px-8 py-2 sm:py-3.5 shadow-xs">
        <div className="max-w-6xl mx-auto flex items-center justify-between gap-2 sm:gap-4">
          <BrandLogo size="md" />

          <div className="flex items-center gap-1 sm:gap-3 shrink-0">
            {/* Dark / Light Theme Quick Toggle */}
            <button
              type="button"
              onClick={toggleTheme}
              className="flex items-center justify-center gap-1.5 p-1.5 sm:px-3 sm:py-1.5 rounded-xl text-xs font-semibold text-[#526176] dark:text-[#94A3B8] hover:text-[#12233D] dark:hover:text-white bg-[#F8FAFC] dark:bg-[#17243A] border border-[#CBD5E1] dark:border-[#29384D] hover:border-[#14B8A6] dark:hover:border-[#14B8A6] transition cursor-pointer shadow-2xs"
              title={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
              aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
            >
              {theme === 'dark' ? (
                <Sun className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-[#14B8A6]" />
              ) : (
                <Moon className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-[#526176]" />
              )}
              <span className="hidden md:inline">{theme === 'dark' ? 'Light' : 'Dark'}</span>
            </button>

            {/* Language Selector */}
            <div className="flex items-center gap-1 px-1.5 sm:px-2.5 py-1.5 rounded-xl text-xs font-semibold text-[#526176] dark:text-[#94A3B8] bg-[#F8FAFC] dark:bg-[#17243A] border border-[#CBD5E1] dark:border-[#29384D] shadow-2xs">
              <Globe className="w-3.5 h-3.5 text-[#08785D] dark:text-[#14B8A6] shrink-0" />
              <select
                value={language}
                onChange={(e) => handleLanguageSelect(e.target.value as LanguageCode)}
                aria-label="Select interface language"
                className="bg-transparent text-[#12233D] dark:text-[#E8EEF7] text-xs font-bold outline-hidden cursor-pointer max-w-[60px] xs:max-w-[100px] sm:max-w-none truncate"
              >
                {Object.values(SUPPORTED_LANGUAGES).map((meta) => (
                  <option key={meta.code} value={meta.code} className="bg-white dark:bg-[#17243A] text-[#12233D] dark:text-[#E8EEF7]">
                    {meta.nativeName} ({meta.name})
                  </option>
                ))}
              </select>
            </div>

            {/* Return to Main Application Button */}
            <button
              type="button"
              onClick={handleReturn}
              className="inline-flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3.5 py-1.5 rounded-xl text-xs font-bold text-[#12233D] dark:text-[#E8EEF7] bg-white dark:bg-[#17243A] hover:bg-slate-50 dark:hover:bg-[#203048] border border-[#CBD5E1] dark:border-[#29384D] hover:border-[#08785D] dark:hover:border-[#14B8A6] transition shadow-xs cursor-pointer focus:ring-2 focus:ring-[#14B8A6]"
              aria-label="Continue to application as guest"
            >
              <ArrowLeft className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-[#08785D] dark:text-[#14B8A6] shrink-0" />
              <span className="hidden sm:inline">{t('loginContinueAsGuest') || 'Continue as Guest'}</span>
              <span className="sm:hidden text-xs">Guest</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-xl w-full mx-auto p-3 sm:p-6 my-auto flex flex-col justify-center animate-fadeIn bg-transparent">
        <div className="auth-card bg-white dark:bg-[#111C2F] rounded-2xl sm:rounded-3xl border border-[#E1E7EE] dark:border-[#29384D] shadow-xl sm:shadow-2xl overflow-hidden p-4 sm:p-8 space-y-5 sm:space-y-6">
          {/* Header Strip & Badge */}
          <div className="text-center space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]">
              <ShieldCheck className="w-3.5 h-3.5 text-[#08785D]" />
              <span>{t('secureCitizenAccess') || 'Zero PII • Offline-First Civic Access'}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-[#12233D] tracking-tight">
              {mode === 'login' ? (t('loginTitle') || 'Sign In to SuchnaSetu AI') : (t('signupTitle') || 'Create Citizen Account')}
            </h1>
            <p className="text-xs sm:text-sm text-[#526176] max-w-md mx-auto">
              {mode === 'login'
                ? (t('loginSubtitle') || 'Access your saved notices, action checklists, and verified deadlines across sessions.')
                : (t('signupSubtitle') || 'Create an account to isolate your civic intelligence, weekly actions, and preferences.')}
            </p>
          </div>

          {/* Toggle Switch: Sign In vs Create Account */}
          <div className="flex bg-[#E2E8F0]/70 dark:bg-[#17243A] p-1 rounded-xl border border-[#CBD5E1] dark:border-[#29384D]" role="tablist">
            <button
              type="button"
              role="tab"
              aria-selected={mode === 'login'}
              onClick={() => {
                setMode('login');
                setError(null);
                setSuccessNotice(null);
              }}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-bold transition cursor-pointer focus-visible:ring-2 focus-visible:ring-[#14B8A6] focus-visible:outline-hidden ${
                mode === 'login'
                  ? 'bg-white dark:bg-[#203048] text-[#12233D] dark:text-[#2DD4BF] shadow-xs border border-[#CBD5E1]/50 dark:border-[#2DD4BF]/30'
                  : 'text-[#526176] dark:text-[#94A3B8] hover:text-[#12233D] dark:hover:text-white'
              }`}
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>{t('signIn') || 'Sign In'}</span>
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={mode === 'signup'}
              onClick={() => {
                setMode('signup');
                setError(null);
                setSuccessNotice(null);
              }}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-bold transition cursor-pointer focus-visible:ring-2 focus-visible:ring-[#14B8A6] focus-visible:outline-hidden ${
                mode === 'signup'
                  ? 'bg-white dark:bg-[#203048] text-[#12233D] dark:text-[#2DD4BF] shadow-xs border border-[#CBD5E1]/50 dark:border-[#2DD4BF]/30'
                  : 'text-[#526176] dark:text-[#94A3B8] hover:text-[#12233D] dark:hover:text-white'
              }`}
            >
              <UserPlus className="w-3.5 h-3.5" />
              <span>{t('register') || 'Create Account'}</span>
            </button>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="p-3.5 rounded-xl bg-[#FEE8E7] border border-[#FCA5A5] text-xs font-semibold text-[#B42318] flex items-start gap-2.5 animate-fadeIn" role="alert">
              <AlertCircle className="w-4 h-4 text-[#B42318] shrink-0 mt-0.5" />
              <div className="flex-1">{error}</div>
            </div>
          )}

          {/* Success Notice */}
          {successNotice && (
            <div className="p-3.5 rounded-xl bg-[#E8F7F0] border border-[#B7E7D2] text-xs font-semibold text-[#08785D] flex items-start gap-2.5 animate-fadeIn">
              <CheckCircle2 className="w-4 h-4 text-[#08785D] shrink-0 mt-0.5" />
              <div className="flex-1">{successNotice}</div>
            </div>
          )}

          {/* FORM: Sign In */}
          {mode === 'login' && (
            <form onSubmit={handleLoginSubmit} className="space-y-4" noValidate>
              <div>
                <label htmlFor="login-email" className="block text-xs font-bold text-[#12233D] mb-1.5">
                  {t('loginEmailLabel') || 'Email Address'}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#68778B]">
                    <Mail className="w-4 h-4" />
                  </div>
                  <input
                    id="login-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="citizen@example.gov.in"
                    required
                    disabled={isLoading}
                    autoComplete="email"
                    className="w-full pl-10 pr-3.5 py-2.5 bg-[#F8FAFC] border border-[#CBD5E1] rounded-xl text-xs text-[#12233D] focus:border-[#08785D] focus:ring-1 focus:ring-[#08785D] focus:outline-hidden transition"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="login-password" className="block text-xs font-bold text-[#12233D] mb-1.5">
                  {t('loginPasswordLabel') || 'Password'}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#68778B]">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    id="login-password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    disabled={isLoading}
                    autoComplete="current-password"
                    className="w-full pl-10 pr-10 py-2.5 bg-[#F8FAFC] border border-[#CBD5E1] rounded-xl text-xs text-[#12233D] focus:border-[#08785D] focus:ring-1 focus:ring-[#08785D] focus:outline-hidden transition"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-[#68778B] hover:text-[#12233D] cursor-pointer"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs pt-1">
                <label className="flex items-center gap-2 cursor-pointer text-[#526176]">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-3.5 h-3.5 rounded text-[#08785D] focus:ring-[#08785D] cursor-pointer"
                  />
                  <span>{t('loginRememberMe') || 'Remember me (30 days)'}</span>
                </label>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-xs text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-md disabled:opacity-50 cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <RotateCw className="w-4 h-4 animate-spin" />
                    <span>Signing In...</span>
                  </>
                ) : (
                  <>
                    <LogIn className="w-4 h-4" />
                    <span>{t('signIn') || 'Sign In to Citizen Account'}</span>
                  </>
                )}
              </button>
            </form>
          )}

          {/* FORM: Create Account */}
          {mode === 'signup' && (
            <form onSubmit={handleSignupSubmit} className="space-y-4" noValidate>
              <div>
                <label htmlFor="signup-name" className="block text-xs font-bold text-[#12233D] mb-1.5">
                  Username
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#68778B]">
                    <User className="w-4 h-4" />
                  </div>
                  <input
                    id="signup-name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. arjun_sharma"
                    required
                    disabled={isLoading}
                    autoComplete="username"
                    className="w-full pl-10 pr-3.5 py-2.5 bg-[#F8FAFC] border border-[#CBD5E1] rounded-xl text-xs text-[#12233D] focus:border-[#08785D] focus:ring-1 focus:ring-[#08785D] focus:outline-hidden transition"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="signup-email" className="block text-xs font-bold text-[#12233D] mb-1.5">
                  {t('loginEmailLabel') || 'Email Address'}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#68778B]">
                    <Mail className="w-4 h-4" />
                  </div>
                  <input
                    id="signup-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="citizen@example.gov.in"
                    required
                    disabled={isLoading}
                    autoComplete="email"
                    className="w-full pl-10 pr-3.5 py-2.5 bg-[#F8FAFC] border border-[#CBD5E1] rounded-xl text-xs text-[#12233D] focus:border-[#08785D] focus:ring-1 focus:ring-[#08785D] focus:outline-hidden transition"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="signup-password" className="block text-xs font-bold text-[#12233D] mb-1.5">
                  {t('loginPasswordLabel') || 'Password'} (Min 8 characters)
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#68778B]">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    id="signup-password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    disabled={isLoading}
                    autoComplete="new-password"
                    className="w-full pl-10 pr-10 py-2.5 bg-[#F8FAFC] border border-[#CBD5E1] rounded-xl text-xs text-[#12233D] focus:border-[#08785D] focus:ring-1 focus:ring-[#08785D] focus:outline-hidden transition"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-[#68778B] hover:text-[#12233D] cursor-pointer"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-xs text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-md disabled:opacity-50 cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <RotateCw className="w-4 h-4 animate-spin" />
                    <span>Creating Account...</span>
                  </>
                ) : (
                  <>
                    <UserPlus className="w-4 h-4" />
                    <span>Create Account</span>
                  </>
                )}
              </button>
            </form>
          )}

          

          {/* Escape Hatch / Guest Access */}
          <div className="pt-4 border-t border-[#E1E7EE] text-center">
            <button
              type="button"
              onClick={handleReturn}
              className="text-xs font-semibold text-[#526176] hover:text-[#08785D] transition cursor-pointer"
            >
              Continue exploring as Guest Citizen →
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};
