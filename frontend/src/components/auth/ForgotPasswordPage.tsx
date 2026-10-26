import React, { useState } from 'react';
import { AuthLayout } from './AuthLayout';
import { requestPasswordReset } from '../../services/api';
import type { AuthPageView } from '../../types/api';
import { useTranslation } from '../../i18n';
import { Mail, Send, Link2, KeyRound, AlertCircle, CheckCircle2, ArrowRight } from 'lucide-react';

interface ForgotPasswordPageProps {
  currentLanguage?: string;
  onLanguageChange?: (lang: string) => void;
  onNavigateAuth: (view: AuthPageView) => void;
}

export const ForgotPasswordPage: React.FC<ForgotPasswordPageProps> = ({
  currentLanguage,
  onLanguageChange,
  onNavigateAuth,
}) => {
  const { t } = useTranslation();

  const [email, setEmail] = useState('');
  const [method, setMethod] = useState<'link' | 'code'>('link');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const cleanEmail = email.trim();
    if (!cleanEmail || !cleanEmail.includes('@')) {
      setError(t('validEmailError'));
      return;
    }

    setIsLoading(true);
    try {
      await requestPasswordReset({
        email: cleanEmail,
        method,
      });
      setIsSubmitted(true);
    } catch (err: any) {
      setError(err.message || t('invalidCredentialsError'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      title={t('forgotPasswordTitle')}
      subtitle={t('forgotPasswordSubtitle')}
      currentLanguage={currentLanguage}
      onLanguageChange={onLanguageChange}
    >
      {isSubmitted ? (
        <div className="auth-success-state">
          <div className="auth-success-icon-badge">
            <CheckCircle2 size={36} className="text-emerald-600" />
          </div>
          <h2 className="auth-success-title">
            {t('forgotPasswordInstructionDispatched')}
          </h2>
          <p className="auth-success-text">
            {method === 'code' ? t('forgotPasswordSentOtpNotice') : t('forgotPasswordSentLinkNotice')}
          </p>
          <div className="auth-success-notice">
            <p>
              {t('loginEmailLabel')}: {email}
            </p>
          </div>
          <div className="auth-success-actions">
            {method === 'code' ? (
              <button
                type="button"
                className="btn-auth-primary"
                onClick={() => onNavigateAuth('reset_password')}
              >
                <span>{t('forgotPasswordEnterCodeBtn')}</span>
                <ArrowRight size={16} />
              </button>
            ) : null}
            <button
              type="button"
              className="btn-auth-secondary"
              onClick={() => onNavigateAuth('login')}
            >
              {t('returnToSignIn')}
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

          {/* Email Field */}
          <div className="form-group">
            <label htmlFor="recovery-email" className="form-label">
              {t('loginEmailLabel')}
            </label>
            <div className="input-with-icon">
              <Mail size={16} className="input-icon" />
              <input
                id="recovery-email"
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

          {/* Recovery Method Option */}
          <div className="form-group">
            <label className="form-label">
              {t('recoveryMethodLabel')}
            </label>
            <div className="recovery-method-cards">
              <div
                className={`recovery-method-card ${method === 'link' ? 'selected' : ''}`}
                onClick={() => setMethod('link')}
                role="button"
                tabIndex={0}
              >
                <div className="recovery-method-icon">
                  <Link2 size={18} />
                </div>
                <div className="recovery-method-text">
                  <div className="recovery-method-title">
                    {t('forgotPasswordMagicLink')}
                  </div>
                  <div className="recovery-method-desc">
                    {t('forgotPasswordMagicLinkDesc')}
                  </div>
                </div>
              </div>

              <div
                className={`recovery-method-card ${method === 'code' ? 'selected' : ''}`}
                onClick={() => setMethod('code')}
                role="button"
                tabIndex={0}
              >
                <div className="recovery-method-icon">
                  <KeyRound size={18} />
                </div>
                <div className="recovery-method-text">
                  <div className="recovery-method-title">
                    {t('forgotPasswordOtpCode')}
                  </div>
                  <div className="recovery-method-desc">
                    {t('forgotPasswordOtpCodeDesc')}
                  </div>
                </div>
              </div>
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
                <span>{t('forgotPasswordSending')}</span>
              </span>
            ) : (
              <>
                <Send size={16} />
                <span>{t('forgotPasswordSendBtn')}</span>
              </>
            )}
          </button>

          {/* Alternate Link */}
          <div className="auth-alternate-action">
            <button
              type="button"
              className="btn-text-link"
              onClick={() => onNavigateAuth('login')}
            >
              {t('returnToSignIn')}
            </button>
          </div>
        </form>
      )}
    </AuthLayout>
  );
};
