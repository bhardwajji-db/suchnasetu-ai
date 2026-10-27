import React, { useState } from 'react';
import { AuthLayout } from './AuthLayout';
import { registerAccount } from '../../services/api';
import type { UserProfile, AuthPageView } from '../../types/api';
import { useTranslation } from '../../i18n';
import { User, Mail, Lock, Eye, EyeOff, UserPlus, AlertCircle, CheckCircle2 } from 'lucide-react';

interface SignupPageProps {
  currentLanguage?: string;
  onLanguageChange?: (lang: string) => void;
  onNavigateAuth: (view: AuthPageView, state?: { email?: string }) => void;
  onSignupSuccess?: (user: UserProfile) => void;
}

export const SignupPage: React.FC<SignupPageProps> = ({
  currentLanguage,
  onLanguageChange,
  onNavigateAuth,
  onSignupSuccess,
}) => {
  const { t } = useTranslation();

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) return;
    setError(null);

    const cleanUsername = username.trim();
    const cleanEmail = email.trim().toLowerCase();

    // Frontend validations
    if (!cleanUsername || cleanUsername.length < 2) {
      setError(t('signupFullNameRequiredError') || 'Username must be at least 2 characters long.');
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

      const user = res.user || {
        id: 'user_registered',
        email: cleanEmail,
        name: cleanUsername,
        username: cleanUsername,
        is_verified: true,
        created_at: new Date().toISOString(),
      };

      setSuccessMessage('Account created successfully! Directing to your dashboard...');

      if (onSignupSuccess) {
        setTimeout(() => {
          onSignupSuccess(user);
        }, 500);
      }
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please check your details.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      title={t('signupTitle') || 'Create Account'}
      subtitle={t('signupSubtitle') || 'Register for your secure citizen account'}
      currentLanguage={currentLanguage}
      onLanguageChange={onLanguageChange}
    >
      {successMessage ? (
        <div className="auth-success-state p-6 text-center space-y-4">
          <div className="auth-success-icon-badge flex justify-center">
            <CheckCircle2 size={42} className="text-[#08785D]" />
          </div>
          <h2 className="text-lg font-bold text-[#12233D]">
            {successMessage}
          </h2>
          <p className="text-xs text-[#526176]">
            Signed in as <strong className="text-[#12233D]">{email}</strong>
          </p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="auth-form" noValidate>
          {error && (
            <div className="auth-error-banner" role="alert">
              <AlertCircle size={16} className="error-icon" />
              <div className="error-text">{error}</div>
            </div>
          )}

          {/* 1. Username */}
          <div className="form-group">
            <label htmlFor="signup-username" className="form-label">
              Username
            </label>
            <div className="input-with-icon">
              <User size={16} className="input-icon" />
              <input
                id="signup-username"
                type="text"
                className="form-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="e.g. arjun_sharma"
                autoComplete="username"
                required
                disabled={isLoading}
              />
            </div>
          </div>

          {/* 2. Email Address */}
          <div className="form-group">
            <label htmlFor="signup-email" className="form-label">
              {t('loginEmailLabel') || 'Email Address'}
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

          {/* 3. Password */}
          <div className="form-group">
            <label htmlFor="signup-password" className="form-label">
              {t('loginPasswordLabel') || 'Password'}
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
            <p className="text-[11px] text-[#526176] mt-1">
              Minimum 8 characters. Must contain letters and numbers.
            </p>
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
                <span>Creating Account...</span>
              </span>
            ) : (
              <>
                <UserPlus size={16} />
                <span>Create Account</span>
              </>
            )}
          </button>

          {/* Link to Sign In */}
          <div className="auth-alternate-action">
            <span>Already have an account?</span>
            <button
              type="button"
              className="btn-text-link font-semibold"
              onClick={() => onNavigateAuth('login')}
            >
              Sign In
            </button>
          </div>
        </form>
      )}
    </AuthLayout>
  );
};
