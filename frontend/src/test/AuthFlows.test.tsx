import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { LoginPage } from '../components/auth/LoginPage';
import { SignupPage } from '../components/auth/SignupPage';
import { VerifyEmailPage } from '../components/auth/VerifyEmailPage';
import { ForgotPasswordPage } from '../components/auth/ForgotPasswordPage';
import { ResetPasswordPage } from '../components/auth/ResetPasswordPage';

describe('Citizen Authentication UI Suite', () => {
  it('renders LoginPage with credentials input and guest escape hatch', () => {
    const handleLoginSuccess = vi.fn();
    const handleNavigateAuth = vi.fn();
    const handleContinueAsGuest = vi.fn();

    render(
      <LoginPage
        currentLanguage="en"
        onLanguageChange={vi.fn()}
        onLoginSuccess={handleLoginSuccess}
        onNavigateAuth={handleNavigateAuth}
        onContinueAsGuest={handleContinueAsGuest}
      />
    );

    expect(screen.getByText(/Sign in to SuchnaSetu AI/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/citizen@example.gov.in/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument();
    expect(screen.getByText(/Continue as Guest/i)).toBeInTheDocument();

    fireEvent.click(screen.getByText(/Continue as Guest/i));
    expect(handleContinueAsGuest).toHaveBeenCalledTimes(1);
  });

  it('renders SignupPage with full name, email, password confirmation', () => {
    render(
      <SignupPage
        currentLanguage="en"
        onLanguageChange={vi.fn()}
        onNavigateAuth={vi.fn()}
      />
    );

    expect(screen.getByText(/Create Citizen Account/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Full Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Confirm Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Create Account/i })).toBeInTheDocument();
  });

  it('renders VerifyEmailPage with 6-digit code input and resend cooldown', () => {
    render(
      <VerifyEmailPage
        initialEmail="citizen.test@suchnasetu.gov.in"
        currentLanguage="en"
        onLanguageChange={vi.fn()}
        onVerificationSuccess={vi.fn()}
        onNavigateLogin={vi.fn()}
      />
    );

    expect(screen.getByText(/Verify Email Address/i)).toBeInTheDocument();
    expect(screen.getByText('citizen.test@suchnasetu.gov.in')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('123456')).toBeInTheDocument();
    expect(screen.getByText(/Resend verification email/i)).toBeInTheDocument();
  });

  it('renders ForgotPasswordPage with link and 6-digit code option cards', () => {
    render(
      <ForgotPasswordPage
        currentLanguage="en"
        onLanguageChange={vi.fn()}
        onNavigateAuth={vi.fn()}
      />
    );

    expect(screen.getByText(/Recover Password/i)).toBeInTheDocument();
    expect(screen.getByText(/Magic Reset Link/i)).toBeInTheDocument();
    expect(screen.getByText(/6-Digit Verification Code/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Send Reset Instructions/i })).toBeInTheDocument();
  });

  it('renders ResetPasswordPage with code and new passphrase inputs', () => {
    render(
      <ResetPasswordPage
        currentLanguage="en"
        onLanguageChange={vi.fn()}
        onResetSuccess={vi.fn()}
        onNavigateLogin={vi.fn()}
      />
    );

    expect(screen.getByText(/Set New Password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^New Password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Confirm New Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Reset Password/i })).toBeInTheDocument();
  });
});
