import React, { useState } from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation, SUPPORTED_LANGUAGES, type LanguageCode } from '../i18n';
import { loginAccount, registerAccount, verifyEmailAddress } from '../services/api';
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
  KeyRound,
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
  const { setCurrentUser, setActiveTab, setSelectedLang } = useNotice();
  const { t, language, setLanguage } = useTranslation();

  const [mode, setMode] = useState<'login' | 'signup' | 'verify'>(initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');
  const [verificationCode, setVerificationCode] = useState('');

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
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
      }
      handleReturn();
    } catch (err: any) {
      const msg = err.message || 'Invalid email or password.';
      setError(msg);
      if (msg.toLowerCase().includes('not verified') || msg.toLowerCase().includes('verification')) {
        setMode('verify');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Registration handler
  const handleSignupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessNotice(null);

    const cleanName = name.trim();
    const cleanEmail = email.trim().toLowerCase();

    if (!cleanName || cleanName.length < 2) {
      setError(t('signupFullNameRequiredError') || 'Full Name is required.');
      return;
    }
    if (!cleanEmail || !cleanEmail.includes('@')) {
      setError(t('validEmailError') || 'Please enter a valid email address.');
      return;
    }
    if (password.length < 8) {
      setError(t('signupPasswordMinLengthError') || 'Password must be at least 8 characters.');
      return;
    }
    if (password !== confirmPassword) {
      setError(t('signupPasswordMismatchError') || 'Passwords do not match.');
      return;
    }

    setIsLoading(true);
    try {
      const res = await registerAccount({
        name: cleanName,
        email: cleanEmail,
        password,
        confirmPassword,
      });

      if (res.already_verified) {
        setSuccessNotice('Account already exists and is verified. Please sign in.');
        setMode('login');
      } else {
        setSuccessNotice(res.message || 'Account created! Enter the 6-digit verification code below.');
        setMode('verify');
      }
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please check your details.');
    } finally {
      setIsLoading(false);
    }
  };

  // Verification code submit
  const handleVerifySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const cleanCode = verificationCode.trim();
    if (!cleanCode || cleanCode.length < 6) {
      setError('Please enter the 6-digit verification code.');
      return;
    }

    setIsLoading(true);
    try {
      await verifyEmailAddress({
        email: email.trim().toLowerCase(),
        code: cleanCode,
      });

      setSuccessNotice('Email verified successfully! You may now sign in.');
      setMode('login');
    } catch (err: any) {
      setError(err.message || 'Verification code is invalid or expired.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-[#F5F8FA] via-white to-[#E8F7F0]/30 text-[#12233D] font-sans selection:bg-[#08785D] selection:text-white pb-12">
      {/* Top Navigation Bar */}
      <header className="w-full bg-white/90 backdrop-blur-md border-b border-[#E1E7EE] sticky top-0 z-30 px-4 sm:px-8 py-3.5 shadow-xs">
        <div className="max-w-6xl mx-auto flex items-center justify-between gap-4">
          <BrandLogo size="md" />

          <div className="flex items-center gap-3">
            {/* Language Selector */}
            <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-semibold text-[#526176] bg-[#F8FAFC] border border-[#CBD5E1]">
              <Globe className="w-3.5 h-3.5 text-[#08785D]" />
              <select
                value={language}
                onChange={(e) => handleLanguageSelect(e.target.value as LanguageCode)}
                aria-label="Select interface language"
                className="bg-transparent text-[#12233D] text-xs font-bold outline-hidden cursor-pointer"
              >
                {Object.values(SUPPORTED_LANGUAGES).map((meta) => (
                  <option key={meta.code} value={meta.code} className="bg-white text-[#12233D]">
                    {meta.nativeName} ({meta.name})
                  </option>
                ))}
              </select>
            </div>

            {/* Return to Main Application Button */}
            <button
              type="button"
              onClick={handleReturn}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold text-[#12233D] bg-white hover:bg-slate-50 border border-[#CBD5E1] transition shadow-xs cursor-pointer focus:ring-2 focus:ring-[#2563EB]"
              aria-label="Return to application"
            >
              <ArrowLeft className="w-4 h-4 text-[#08785D]" />
              <span>{t('returnToSignIn') || 'Return to Application'}</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-xl w-full mx-auto p-4 sm:p-6 my-auto flex flex-col justify-center animate-fadeIn">
        <div className="bg-white rounded-3xl border border-[#E1E7EE] shadow-xl overflow-hidden p-6 sm:p-8 space-y-6">
          {/* Header Strip & Badge */}
          <div className="text-center space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]">
              <ShieldCheck className="w-3.5 h-3.5 text-[#08785D]" />
              <span>{t('secureCitizenAccess') || 'Zero PII • Offline-First Civic Access'}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-[#12233D] tracking-tight">
              {mode === 'login' && (t('loginTitle') || 'Sign In to SuchnaSetu AI')}
              {mode === 'signup' && (t('signupTitle') || 'Create Citizen Account')}
              {mode === 'verify' && (t('verifyEmailTitle') || 'Verify Your Account')}
            </h1>
            <p className="text-xs sm:text-sm text-[#526176] max-w-md mx-auto">
              {mode === 'login' && (t('loginSubtitle') || 'Access your saved notices, action checklists, and verified deadlines across sessions.')}
              {mode === 'signup' && (t('signupSubtitle') || 'Create an account to isolate your civic intelligence, weekly actions, and preferences.')}
              {mode === 'verify' && 'Enter the 6-digit verification code dispatched to your email address.'}
            </p>
          </div>

          {/* Toggle Switch: Sign In vs Create Account */}
          {mode !== 'verify' && (
            <div className="flex bg-[#F1F5F9] p-1 rounded-xl border border-[#CBD5E1]" role="tablist">
              <button
                type="button"
                role="tab"
                aria-selected={mode === 'login'}
                onClick={() => {
                  setMode('login');
                  setError(null);
                  setSuccessNotice(null);
                }}
                className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-xs font-bold transition cursor-pointer ${
                  mode === 'login'
                    ? 'bg-white text-[#12233D] shadow-xs'
                    : 'text-[#526176] hover:text-[#12233D]'
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
                className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-xs font-bold transition cursor-pointer ${
                  mode === 'signup'
                    ? 'bg-white text-[#12233D] shadow-xs'
                    : 'text-[#526176] hover:text-[#12233D]'
                }`}
              >
                <UserPlus className="w-3.5 h-3.5" />
                <span>{t('register') || 'Create Account'}</span>
              </button>
            </div>
          )}

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
                  {t('signupFullName') || 'Full Name'}
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
                    placeholder="Priya Sharma"
                    required
                    disabled={isLoading}
                    autoComplete="name"
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
                    placeholder="priya.sharma@example.gov.in"
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

              <div>
                <label htmlFor="signup-confirm-password" className="block text-xs font-bold text-[#12233D] mb-1.5">
                  {t('signupConfirmPassword') || 'Confirm Password'}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#68778B]">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    id="signup-confirm-password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    disabled={isLoading}
                    autoComplete="new-password"
                    className="w-full pl-10 pr-10 py-2.5 bg-[#F8FAFC] border border-[#CBD5E1] rounded-xl text-xs text-[#12233D] focus:border-[#08785D] focus:ring-1 focus:ring-[#08785D] focus:outline-hidden transition"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-[#68778B] hover:text-[#12233D] cursor-pointer"
                    aria-label={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
                  >
                    {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
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
                    <span>{t('signupCreateAccountButton') || 'Create Citizen Account'}</span>
                  </>
                )}
              </button>
            </form>
          )}

          {/* FORM: Verify Email Code */}
          {mode === 'verify' && (
            <form onSubmit={handleVerifySubmit} className="space-y-4">
              <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-xs space-y-1">
                <div className="font-bold text-[#12233D] flex items-center gap-1.5">
                  <KeyRound className="w-4 h-4 text-[#08785D]" />
                  <span>Enter 6-Digit Verification Code</span>
                </div>
                <p className="text-[#526176]">
                  A code was sent to <strong className="text-[#12233D]">{email}</strong>.
                </p>
                <p className="text-[11px] text-[#08785D] pt-1">
                  💡 In local development (console backend), check your backend terminal window for the 6-digit code.
                </p>
              </div>

              <div>
                <label htmlFor="verify-code" className="block text-xs font-bold text-[#12233D] mb-1.5">
                  6-Digit Verification Code
                </label>
                <input
                  id="verify-code"
                  type="text"
                  maxLength={6}
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
                  placeholder="123456"
                  required
                  disabled={isLoading}
                  className="w-full text-center tracking-widest text-lg font-mono py-2.5 bg-[#F8FAFC] border border-[#CBD5E1] rounded-xl text-[#12233D] focus:border-[#08785D] focus:ring-1 focus:ring-[#08785D] focus:outline-hidden transition font-bold"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading || verificationCode.length < 6}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-xs text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-md disabled:opacity-50 cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <RotateCw className="w-4 h-4 animate-spin" />
                    <span>Verifying...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Verify & Continue</span>
                  </>
                )}
              </button>

              <div className="text-center pt-2">
                <button
                  type="button"
                  onClick={() => setMode('login')}
                  className="text-xs font-semibold text-[#08785D] hover:underline cursor-pointer"
                >
                  ← Back to Sign In
                </button>
              </div>
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
