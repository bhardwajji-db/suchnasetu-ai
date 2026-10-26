import React, { useState } from 'react';
import { AuthLayout } from './AuthLayout';
import { registerAccount } from '../../services/api';
import type { AuthPageView } from '../../types/api';
import { useTranslation } from '../../i18n';
import { User, Mail, Lock, Eye, EyeOff, UserPlus, AlertCircle, CheckCircle2, ArrowRight } from 'lucide-react';

interface SignupPageProps {
  currentLanguage?: string;
  onLanguageChange?: (lang: string) => void;
  onNavigateAuth: (view: AuthPageView, state?: { email?: string }) => void;
}

export const SignupPage: React.FC<SignupPageProps> = ({
  currentLanguage,
  onLanguageChange,
  onNavigateAuth,
}) => {
  const { t } = useTranslation();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [emailDelivered, setEmailDelivered] = useState<boolean>(true);
  const [alreadyVerified, setAlreadyVerified] = useState<boolean>(false);
  const [submittedEmail, setSubmittedEmail] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const cleanName = name.trim();
    const cleanEmail = email.trim().toLowerCase();

    if (!cleanName || cleanName.length < 2) {
      setError(t('signupFullNameRequiredError'));
      return;
    }
    if (!cleanEmail || !cleanEmail.includes('@')) {
      setError(t('validEmailError'));
      return;
    }
    if (password.length < 8) {
      setError(t('signupPasswordMinLengthError'));
      return;
    }
    if (password !== confirmPassword) {
      setError(t('signupPasswordMismatchError'));
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

      setSubmittedEmail(cleanEmail);
      try {
        sessionStorage.setItem('suchnasetu_pending_verification_email', cleanEmail);
      } catch {}

      const isAlready = !!res.already_verified;
      setAlreadyVerified(isAlready);
      const isDelivered = res.email_delivered !== false && !isAlready;
      setEmailDelivered(isDelivered);

      setSuccessMessage(
        res.message ||
          (isAlready
            ? t('signupAlreadyHaveAccount')
            : t('verifyEmailSuccessHeading'))
      );
    } catch (err: any) {
      setError(err.message || t('invalidCredentialsError'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      title={t('signupTitle')}
      subtitle={t('signupSubtitle')}
      currentLanguage={currentLanguage}
      onLanguageChange={onLanguageChange}
    >
      {successMessage ? (
        <div className="auth-success-state">
          <div className={emailDelivered ? 'auth-success-icon-badge' : 'auth-success-icon-badge warning'}>
            {emailDelivered ? (
              <CheckCircle2 size={36} className="text-emerald-600" />
            ) : (
              <AlertCircle size={36} className="text-amber-600" />
            )}
          </div>
          <h2 className="auth-success-title">
            {alreadyVerified
              ? t('signupAlreadyHaveAccount')
              : emailDelivered
                ? t('verifyEmailSuccessHeading')
                : t('signupTitle')}
          </h2>
          <p className="auth-success-text">{successMessage}</p>
          <div className="auth-success-notice">
            <p>
              {alreadyVerified
                ? `${t('loginEmailLabel')}: ${submittedEmail}`
                : `${t('verifyEmailCodeLabel')}: ${submittedEmail}`}
            </p>
          </div>
          <div className="auth-success-actions">
            {alreadyVerified ? (
              <button
                type="button"
                className="btn-auth-primary"
                onClick={() => onNavigateAuth('login')}
              >
                <span>{t('signupSignInDirectly')}</span>
                <ArrowRight size={16} />
              </button>
            ) : (
              <button
                type="button"
                className="btn-auth-primary"
                onClick={() => onNavigateAuth('verify_email', { email: submittedEmail })}
              >
                <span>{t('enterVerificationCode')}</span>
                <ArrowRight size={16} />
              </button>
            )}
            <button
              type="button"
              className="btn-auth-secondary"
              onClick={() => onNavigateAuth('login')}
            >
              {t('signupReturnToSignIn')}
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

          {/* Full Name */}
          <div className="form-group">
            <label htmlFor="signup-name" className="form-label">
              {t('signupNameLabel')}
            </label>
            <div className="input-with-icon">
              <User size={16} className="input-icon" />
              <input
                id="signup-name"
                type="text"
                className="form-input"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder={t('signupNamePlaceholder')}
                autoComplete="name"
                required
                disabled={isLoading}
              />
            </div>
          </div>

          {/* Email Address */}
          <div className="form-group">
            <label htmlFor="signup-email" className="form-label">
              {t('loginEmailLabel')}
            </label>
            <div className="input-with-icon">
              <Mail size={16} className="input-icon" />
              <input
                id="signup-email"
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

          {/* Password */}
          <div className="form-group">
            <label htmlFor="signup-password" className="form-label">
              {t('loginPasswordLabel')}
            </label>
            <div className="input-with-icon">
              <Lock size={16} className="input-icon" />
              <input
                id="signup-password"
                type={showPassword ? 'text' : 'password'}
                className="form-input pr-10"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
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
            <label htmlFor="signup-confirm-password" className="form-label">
              {t('signupConfirmPassword')}
            </label>
            <div className="input-with-icon">
              <Lock size={16} className="input-icon" />
              <input
                id="signup-confirm-password"
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
                <span>{t('signupCreatingAccount')}</span>
              </span>
            ) : (
              <>
                <UserPlus size={16} />
                <span>{t('signupCreateAccountButton')}</span>
              </>
            )}
          </button>

          {/* Alternate Link */}
          <div className="auth-alternate-action">
            <span>{t('signupAlreadyHaveAccount')}</span>
            <button
              type="button"
              className="btn-text-link font-semibold"
              onClick={() => onNavigateAuth('login')}
            >
              {t('signIn')}
            </button>
          </div>
        </form>
      )}
    </AuthLayout>
  );
};
