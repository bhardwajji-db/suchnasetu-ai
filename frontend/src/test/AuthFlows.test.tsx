import { AuthPageView } from '../views/AuthPageView';
import { NoticeProvider } from '../context/NoticeContext';
import { I18nProvider } from '../i18n';
import { App } from '../App';
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

  it('renders SignupPage with username, email, and password without OTP', () => {
    render(
      <SignupPage
        currentLanguage="en"
        onLanguageChange={vi.fn()}
        onNavigateAuth={vi.fn()}
      />
    );

    expect(screen.getByText(/Create Citizen Account/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Password/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/Confirm Password/i)).not.toBeInTheDocument();
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

  it('renders AuthPageView with clean tabs, no stray parenthesis, and smooth tab switching', () => {
    const handleComplete = vi.fn();
    const { container } = render(
      <I18nProvider>
        <NoticeProvider>
          <AuthPageView onComplete={handleComplete} />
        </NoticeProvider>
      </I18nProvider>
    );

    // Verify tablist and clean tabs
    const tablist = screen.getByRole('tablist');
    expect(tablist).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Sign In/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Register|Create Account/i })).toBeInTheDocument();

    // Verify stray '(' character is absent from the DOM
    const rawText = container.textContent || '';
    expect(rawText).not.toMatch(/\(\s*Sign In/);

    // Switch to Create Account / Register tab
    fireEvent.click(screen.getByRole('tab', { name: /Register|Create Account/i }));
    expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();

    // Switch back to Sign In tab
    fireEvent.click(screen.getByRole('tab', { name: /Sign In/i }));
    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();

    // Test Guest continue button
    const guestBtn = screen.getByText(/Continue exploring as Guest Citizen/i);
    expect(guestBtn).toBeInTheDocument();
    fireEvent.click(guestBtn);
    expect(handleComplete).toHaveBeenCalledTimes(1);
  });

  it('opens application directly to AuthPageView on startup for unauthenticated visitors', () => {
    render(<App />);

    expect(screen.getByRole('tablist')).toBeInTheDocument();
    expect(screen.getByText(/Sign In to SuchnaSetu AI/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
  });
});
