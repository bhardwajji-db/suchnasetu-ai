import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Header } from '../components/Header';
import { NoticeProvider } from '../context/NoticeContext';

describe('Header Component', () => {
  it('renders application branding and PS02 badge', () => {
    render(
      <NoticeProvider>
        <Header />
      </NoticeProvider>
    );

    expect(screen.getByText(/Notice-to-Action Accessibility Assistant/i)).toBeInTheDocument();
    expect(screen.getByText(/PS02/i)).toBeInTheDocument();
    expect(screen.getByText(/Local Gemma 4/i)).toBeInTheDocument();
  });

  it('renders single unified language selector dropdown and notification access', () => {
    render(
      <NoticeProvider>
        <Header />
      </NoticeProvider>
    );

    // Single language selector with English and Hindi in dropdown
    const langSelect = screen.getByRole('combobox', { name: /Select Website Language/i });
    expect(langSelect).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /^EN$/ })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /^हिन्दी$/ })).not.toBeInTheDocument();

    // Notification Center access button
    const notifBtn = screen.getByRole('button', { name: /Open notifications/i });
    expect(notifBtn).toBeInTheDocument();
  });

  it('renders top-right profile avatar or citizen sign-in access', () => {
    render(
      <NoticeProvider>
        <Header />
      </NoticeProvider>
    );

    // Guest state renders the accessible Sign In CTA with User icon
    const headerSignInBtn = screen.getByRole('button', { name: /Sign In or Create Citizen Account/i });
    expect(headerSignInBtn).toBeInTheDocument();
  });

  it('renders dark theme quick toggle and switches between Slate Green and Midnight Teal', async () => {
    const { fireEvent } = await import('@testing-library/react');
    render(
      <NoticeProvider>
        <Header />
      </NoticeProvider>
    );

    // Initial state: Light theme (Slate + Deep Green)
    const toggleBtn = screen.getByRole('button', { name: /Switch to dark theme/i });
    expect(toggleBtn).toBeInTheDocument();
    expect(toggleBtn).toHaveAttribute('title', expect.stringContaining('Midnight Navy + Teal'));

    // Click to switch to Dark theme
    fireEvent.click(toggleBtn);
    expect(screen.getByRole('button', { name: /Switch to light theme/i })).toBeInTheDocument();
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);

    // Click again to switch back to Light theme
    fireEvent.click(screen.getByRole('button', { name: /Switch to light theme/i }));
    expect(screen.getByRole('button', { name: /Switch to dark theme/i })).toBeInTheDocument();
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });
});
