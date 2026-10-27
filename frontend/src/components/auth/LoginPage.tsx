import React, { useState } from 'react';
import { AuthLayout } from './AuthLayout';
import { loginAccount } from '../../services/api';
import type { UserProfile, AuthPageView } from '../../types/api';
import { useTranslation } from '../../i18n';
import { Mail, Lock, Eye, EyeOff, LogIn, AlertCircle, Sparkles, ArrowRight } from 'lucide-react';

interface LoginPageProps {
  currentLanguage?: string;
  onLanguageChange?: (lang: string) => void;
  onLoginSuccess: (user: UserProfile) => void;
  onNavigateAuth: (view: AuthPageView, state?: { email?: string }) => void;
  onContinueAsGuest?: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({
  currentLanguage,
  onLanguageChange,
  onLoginSuccess,
  onNavigateAuth,
  onContinueAsGuest,
}) => {
  const { t } = useTranslation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) return;
    setError(null);

    const cleanEmail = email.trim();
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
        rememberMe: true,
      });

      if (res.user) {
        onLoginSuccess(res.user);
      } else {
        onLoginSuccess({
          id: 'user_active',
          email: cleanEmail,
          name: cleanEmail.split('@')[0],
          username: cleanEmail.split('@')[0],
          is_verified: true,
          created_at: new Date().toISOString(),
        });
      }
    } catch (err: any) {
      setError(err.message || 'Invalid email or password.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      title={t('loginTitle')}
      subtitle={t('loginSubtitle')}
      currentLanguage={currentLanguage}
      onLanguageChange={onLanguageChange}
    >
      <form onSubmit={handleSubmit} className="auth-form" noValidate>
        {error && (
          <div className="auth-error-banner" role="alert">
            <AlertCircle size={16} className="error-icon" />
            <div className="error-text">
              <div>{error}</div>
            </div>
          </div>
        )}

        {/* Email Field */}
        <div className="form-group">
          <label htmlFor="login-email" className="form-label">
            {t('loginEmailLabel')}
          </label>
          <div className="input-with-icon">
            <Mail size={16} className="input-icon" />
            <input
              id="login-email"
              type="email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="citizen@example.gov.in"
              autoComplete="email"
              required
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Password Field */}
        <div className="form-group">
          <div className="form-label-row">
            <label htmlFor="login-password" className="form-label">
              {t('loginPasswordLabel')}
            </label>
            <button
              type="button"
              className="btn-text-link"
              onClick={() => onNavigateAuth('forgot_password')}
            >
              {t('loginForgotPassword')}
            </button>
          </div>
          <div className="input-with-icon">
            <Lock size={16} className="input-icon" />
            <input
              id="login-password"
              type={showPassword ? 'text' : 'password'}
              className="form-input pr-10"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              autoComplete="current-password"
              required
              disabled={isLoading}
            />
            <button
              type="button"
              className="password-toggle-btn"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? 'Hide password' : 'Show password'}
              tabIndex={-1}
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>

        {/* Remember Me Checkbox */}
        <div className="form-options-row">
          <label className="checkbox-label">
            <input
              type="checkbox"
              className="form-checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              disabled={isLoading}
            />
            <span>{t('loginRememberMe')}</span>
          </label>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="btn-auth-primary"
          disabled={isLoading}
        >
          {isLoading ? (
            <span className="btn-loading-content">
              <span className="btn-spinner" />
              <span>{t('signingInStatus')}</span>
            </span>
          ) : (
            <>
              <LogIn size={16} />
              <span>{t('signIn')}</span>
            </>
          )}
        </button>

        {/* Divider */}
        <div className="auth-divider">
          <span>{t('orDivider')}</span>
        </div>

        {/* Sign Up Link */}
        <div className="auth-alternate-action">
          <span>{t('loginNoAccount')}</span>
          <button
            type="button"
            className="btn-text-link font-semibold"
            onClick={() => onNavigateAuth('signup')}
          >
            {t('loginCreateAccountLink')}
          </button>
        </div>

        {/* Continue as Demo / Guest Button */}
        {onContinueAsGuest && (
          <div className="auth-guest-option">
            <button
              type="button"
              className="btn-auth-secondary"
              onClick={onContinueAsGuest}
            >
              <Sparkles size={14} className="text-emerald-600" />
              <span>{t('loginContinueAsGuest')}</span>
              <ArrowRight size={14} />
            </button>
          </div>
        )}
      </form>
    </AuthLayout>
  );
};
