import React, { useState } from 'react';
import { AuthLayout } from './AuthLayout';
import { completePasswordReset } from '../../services/api';
import { useTranslation } from '../../i18n';
import { Lock, Eye, EyeOff, CheckCircle2, AlertCircle, Mail, KeyRound, LogIn } from 'lucide-react';

interface ResetPasswordPageProps {
  currentLanguage?: string;
  onLanguageChange?: (lang: string) => void;
  onResetSuccess: () => void;
  onNavigateLogin: () => void;
}

export const ResetPasswordPage: React.FC<ResetPasswordPageProps> = ({
  currentLanguage,
  onLanguageChange,
  onResetSuccess,
  onNavigateLogin,
}) => {
  const { t } = useTranslation();

  const [token] = useState<string | null>(() => {
    try {
      return new URLSearchParams(window.location.search).get('token');
    } catch {
      return null;
    }
  });
  const [email, setEmail] = useState<string>(() => {
    try {
      return new URLSearchParams(window.location.search).get('email') || '';
    } catch {
      return '';
    }
  });
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate inputs
    if (!token) {
      if (!email.trim() || !email.includes('@')) {
        setError(t('validEmailError'));
        return;
      }
      if (code.trim().length !== 6) {
        setError(t('resetPasswordCodeLabel'));
        return;
      }
    }

    if (newPassword.length < 8) {
      setError(t('signupPasswordMinLengthError'));
      return;
    }
    if (newPassword !== confirmPassword) {
      setError(t('signupPasswordMismatchError'));
      return;
    }

    setIsLoading(true);
    try {
      await completePasswordReset({
        token: token || undefined,
        email: email.trim() || undefined,
        code: code.trim() || undefined,
        newPassword,
        confirmPassword,
      });
      setIsSuccess(true);
      onResetSuccess();
    } catch (err: any) {
      setError(err.message || t('invalidCredentialsError'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      title={t('resetPasswordTitle')}
      subtitle={t('resetPasswordSubtitle')}
      currentLanguage={currentLanguage}
      onLanguageChange={onLanguageChange}
    >
      {isSuccess ? (
        <div className="auth-success-state">
          <div className="auth-success-icon-badge">
            <CheckCircle2 size={40} className="text-emerald-600" />
          </div>
          <h2 className="auth-success-title">
            {t('resetPasswordSuccess')}
          </h2>
          <p className="auth-success-text">
            {t('resetPasswordSuccessDesc')}
          </p>
          <div className="auth-success-actions">
            <button
              type="button"
              className="btn-auth-primary"
              onClick={onNavigateLogin}
            >
              <LogIn size={16} />
              <span>{t('signIn')}</span>
            </button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="auth-form" noValidate>
          {error && (
            <div className="auth-error-banner" role="alert">
              <AlertCircle size={16} className="error-icon" />
              <div className="error-text">{error}</div>
            </div>
          )}

          {/* Email & Code fields if not using URL token */}
          {!token && (
            <>
              <div className="form-group">
                <label htmlFor="reset-email" className="form-label">
                  {t('loginEmailLabel')}
                </label>
                <div className="input-with-icon">
                  <Mail size={16} className="input-icon" />
                  <input
                    id="reset-email"
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

              <div className="form-group">
                <label htmlFor="reset-code" className="form-label">
                  {t('resetPasswordCodeLabel')}
                </label>
                <div className="input-with-icon">
                  <KeyRound size={16} className="input-icon" />
                  <input
                    id="reset-code"
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={6}
                    className="form-input text-center font-mono font-bold tracking-widest text-lg"
                    value={code}
                    onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    placeholder="123456"
                    required
                    disabled={isLoading}
                    autoComplete="one-time-code"
                  />
                </div>
              </div>
            </>
          )}

          {/* New Password */}
          <div className="form-group">
            <label htmlFor="new-password" className="form-label">
              {t('resetPasswordNewPasswordLabel')}
            </label>
            <div className="input-with-icon">
              <Lock size={16} className="input-icon" />
              <input
                id="new-password"
                type={showPassword ? 'text' : 'password'}
                className="form-input pr-10"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="••••••••••••"
                autoComplete="new-password"
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

          {/* Confirm Password */}
          <div className="form-group">
            <label htmlFor="confirm-password" className="form-label">
              {t('resetPasswordConfirmPasswordLabel')}
            </label>
            <div className="input-with-icon">
              <Lock size={16} className="input-icon" />
              <input
                id="confirm-password"
                type={showConfirmPassword ? 'text' : 'password'}
                className="form-input pr-10"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••••••"
                autoComplete="new-password"
                required
                disabled={isLoading}
              />
              <button
                type="button"
                className="password-toggle-btn"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                tabIndex={-1}
              >
                {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
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
                <span>{t('resetPasswordResetting')}</span>
              </span>
            ) : (
              <span>{t('resetPasswordButton')}</span>
            )}
          </button>

          {/* Return to Login */}
          <div className="auth-alternate-action">
            <button
              type="button"
              className="btn-text-link"
              onClick={onNavigateLogin}
            >
              {t('returnToSignIn')}
            </button>
          </div>
        </form>
      )}
    </AuthLayout>
  );
};
