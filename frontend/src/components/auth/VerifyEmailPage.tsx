import React, { useState, useEffect } from 'react';
import { AuthLayout } from './AuthLayout';
import { verifyEmailAddress, resendEmailVerification } from '../../services/api';
import { useTranslation } from '../../i18n';
import { CheckCircle2, AlertCircle, RefreshCw, Mail, KeyRound, LogIn } from 'lucide-react';

interface VerifyEmailPageProps {
  initialEmail?: string;
  currentLanguage?: string;
  onLanguageChange?: (lang: string) => void;
  onVerificationSuccess: () => void;
  onNavigateLogin: () => void;
  onNavigateSignup?: () => void;
}

export const VerifyEmailPage: React.FC<VerifyEmailPageProps> = ({
  initialEmail,
  currentLanguage,
  onLanguageChange,
  onVerificationSuccess,
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
      const urlEmail = new URLSearchParams(window.location.search).get('email');
      if (urlEmail) return urlEmail.trim().toLowerCase();
      if (initialEmail) return initialEmail.trim().toLowerCase();
      return (sessionStorage.getItem('suchnasetu_pending_verification_email') || '').trim().toLowerCase();
    } catch {
      return (initialEmail || '').trim().toLowerCase();
    }
  });

  // Keep track of the email for which the token/code was issued
  const [boundEmail, setBoundEmail] = useState<string>(() => {
    try {
      const urlEmail = new URLSearchParams(window.location.search).get('email');
      if (urlEmail) return urlEmail.trim().toLowerCase();
      if (initialEmail) return initialEmail.trim().toLowerCase();
      return (sessionStorage.getItem('suchnasetu_pending_verification_email') || '').trim().toLowerCase();
    } catch {
      return (initialEmail || '').trim().toLowerCase();
    }
  });

  const [isEditingEmail, setIsEditingEmail] = useState<boolean>(() => !email);
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState<boolean>(() => Boolean(token));
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resendStatus, setResendStatus] = useState<string | null>(null);
  const [resendWarning, setResendWarning] = useState<string | null>(null);
  const [resendCooldown, setResendCooldown] = useState<number>(0);

  // Auto-verify if single-use token parameter is detected in URL query
  useEffect(() => {
    if (!token) return;

    let isMounted = true;
    const verifyToken = async () => {
      try {
        const res = await verifyEmailAddress({ token });
        if (!isMounted) return;
        setIsSuccess(true);
        if ((res as any).user?.email) {
          setEmail((res as any).user.email);
        }
        onVerificationSuccess();
      } catch (err: any) {
        if (!isMounted) return;
        setError(err.message || t('invalidCredentialsError'));
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    verifyToken();
    return () => {
      isMounted = false;
    };
  }, [token, onVerificationSuccess, t]);

  // Resend cooldown timer
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setInterval(() => {
      setResendCooldown((prev) => Math.max(0, prev - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, [resendCooldown]);

  const handleManualCodeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code.trim() || code.trim().length !== 6) {
      setError(t('verifyEmailCodeLabel'));
      return;
    }

    const targetEmail = email.trim().toLowerCase();
    if (!targetEmail || !targetEmail.includes('@')) {
      setError(t('validEmailError'));
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      await verifyEmailAddress({
        email: targetEmail,
        code: code.trim(),
      });
      setIsSuccess(true);
      onVerificationSuccess();
    } catch (err: any) {
      setError(err.message || t('invalidCredentialsError'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEmailChange = (newEmail: string) => {
    setEmail(newEmail);
    setError(null);
    setResendStatus(null);
  };

  const handleResend = async () => {
    if (resendCooldown > 0 || isLoading || isSubmitting) return;

    const cleanEmail = email.trim().toLowerCase();
    if (!cleanEmail || !cleanEmail.includes('@')) {
      setError(t('validEmailError'));
      return;
    }

    setIsLoading(true);
    setError(null);
    setResendStatus(null);
    setResendWarning(null);

    try {
      const res = await resendEmailVerification(cleanEmail);
      setBoundEmail(cleanEmail);
      setIsEditingEmail(false);
      try {
        sessionStorage.setItem('suchnasetu_pending_verification_email', cleanEmail);
      } catch {}

      if (res.already_verified) {
        setResendStatus(res.message || t('signupAlreadyHaveAccount'));
      } else if (res.email_delivered === false) {
        setResendWarning(res.message || t('verifyEmailCheckSpamTip'));
      } else {
        setResendStatus(res.message || t('verifyEmailSuccessHeading'));
      }
      setResendCooldown(60);
    } catch (err: any) {
      const errMsg = err.message || '';
      setError(errMsg || t('invalidCredentialsError'));
      if (errMsg.includes('60 seconds') || errMsg.includes('wait') || errMsg.includes('Too many')) {
        setResendCooldown(60);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      title={t('verifyEmailTitle')}
      subtitle={t('verifyEmailSubtitle')}
      currentLanguage={currentLanguage}
      onLanguageChange={onLanguageChange}
    >
      {isSuccess ? (
        <div className="auth-success-state">
          <div className="auth-success-icon-badge">
            <CheckCircle2 size={40} className="text-emerald-600" />
          </div>
          <h2 className="auth-success-title">
            {t('verifyEmailSuccessHeading')}
          </h2>
          <p className="auth-success-text">
            {t('verifyEmailSuccessDesc')}
          </p>
          <div className="auth-success-actions">
            <button
              type="button"
              className="btn-auth-primary"
              onClick={onNavigateLogin}
            >
              <LogIn size={16} />
              <span>{t('verifyEmailSignInNow')}</span>
            </button>
          </div>
        </div>
      ) : (
        <div className="verify-flow-container">
          {error && (
            <div className="auth-error-banner" role="alert">
              <AlertCircle size={16} className="error-icon" />
              <div className="error-text">{error}</div>
            </div>
          )}

          {resendStatus && (
            <div className="auth-info-banner" role="status">
              <CheckCircle2 size={16} className="text-emerald-600" />
              <div className="info-text">{resendStatus}</div>
            </div>
          )}

          {resendWarning && (
            <div className="auth-error-banner" style={{ backgroundColor: '#fffbeb', borderColor: '#fef3c7', color: '#92400e' }} role="status">
              <AlertCircle size={16} className="text-amber-600" />
              <div className="info-text">{resendWarning}</div>
            </div>
          )}

          {token && isLoading ? (
            <div className="auth-verifying-spinner-box">
              <div className="btn-spinner large" />
              <p>{t('verifyEmailVerifying')}</p>
            </div>
          ) : (
            <form onSubmit={handleManualCodeSubmit} className="auth-form" noValidate>
              <p className="auth-code-instruction">
                {t('verifyEmailCodeLabel')}
              </p>

              {/* Email Address Section */}
              <div className="form-group">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <label htmlFor="verify-email" className="form-label" style={{ marginBottom: 0 }}>
                    {t('loginEmailLabel')}
                  </label>
                  {email && !isEditingEmail && (
                    <button
                      type="button"
                      className="btn-text-link"
                      style={{ fontSize: '0.75rem', fontWeight: 600 }}
                      onClick={() => setIsEditingEmail(true)}
                    >
                      {t('verifyEmailChangeEmail')}
                    </button>
                  )}
                </div>

                {!isEditingEmail && email ? (
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '8px 12px',
                      backgroundColor: '#f8fafc',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '0.875rem',
                      color: '#0f172a',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Mail size={16} className="text-emerald-600" />
                      <span className="font-mono font-medium">{email}</span>
                    </div>
                    <span
                      style={{
                        fontSize: '0.7rem',
                        fontWeight: 600,
                        backgroundColor: '#ecfdf5',
                        color: '#047857',
                        padding: '2px 8px',
                        borderRadius: '9999px',
                        border: '1px solid #a7f3d0',
                      }}
                    >
                      {t('userConfirmedBadge')}
                    </span>
                  </div>
                ) : (
                  <div>
                    <div className="input-with-icon">
                      <Mail size={16} className="input-icon" />
                      <input
                        id="verify-email"
                        type="email"
                        className="form-input"
                        value={email}
                        onChange={(e) => handleEmailChange(e.target.value)}
                        placeholder="citizen@example.gov.in"
                        autoComplete="email"
                        required
                        disabled={isLoading || isSubmitting}
                      />
                    </div>
                    {boundEmail && email !== boundEmail && (
                      <p style={{ fontSize: '0.75rem', color: '#b45309', marginTop: '4px', lineHeight: 1.4 }}>
                        {t('verifyEmailCheckSpamTip')}
                      </p>
                    )}
                  </div>
                )}
              </div>

              {/* 6-Digit Code */}
              <div className="form-group">
                <label htmlFor="verify-code" className="form-label">
                  {t('resetPasswordCodeLabel')}
                </label>
                <div className="input-with-icon">
                  <KeyRound size={16} className="input-icon" />
                  <input
                    id="verify-code"
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={6}
                    className="form-input text-center font-mono font-bold tracking-widest text-lg"
                    value={code}
                    onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    placeholder="123456"
                    required
                    disabled={isLoading || isSubmitting}
                    autoComplete="one-time-code"
                  />
                </div>
              </div>

              {/* Submit Verification Button */}
              <button
                type="submit"
                className="btn-auth-primary"
                disabled={isLoading || isSubmitting || code.length !== 6}
              >
                {isSubmitting ? (
                  <span className="btn-loading-content">
                    <span className="btn-spinner" />
                    <span>{t('verifyEmailVerifying')}</span>
                  </span>
                ) : (
                  <span>{t('verifyEmailVerifyButton')}</span>
                )}
              </button>

              {/* Resend Action */}
              <div className="auth-resend-row">
                <button
                  type="button"
                  className="btn-text-link"
                  onClick={handleResend}
                  disabled={resendCooldown > 0 || isLoading || isSubmitting}
                >
                  <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
                  <span>
                    {resendCooldown > 0
                      ? `${t('verifyEmailResendIn')} (${resendCooldown}s)`
                      : t('verifyEmailResend')}
                  </span>
                </button>
              </div>

              {/* Return to Login */}
              <div className="auth-alternate-action" style={{ marginTop: '0.75rem' }}>
                <button
                  type="button"
                  className="btn-text-link font-medium"
                  onClick={onNavigateLogin}
                >
                  {t('returnToSignIn')}
                </button>
              </div>
            </form>
          )}
        </div>
      )}
    </AuthLayout>
  );
};
