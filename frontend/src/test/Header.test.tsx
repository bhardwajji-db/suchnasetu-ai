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

  it('renders language toggle buttons', () => {
    render(
      <NoticeProvider>
        <Header />
      </NoticeProvider>
    );

    expect(screen.getByText('EN')).toBeInTheDocument();
    expect(screen.getByText('हिन्दी')).toBeInTheDocument();
  });

  it('preserves clean top-bar navigation without cluttered guest sign in button', () => {
    render(
      <NoticeProvider>
        <Header />
      </NoticeProvider>
    );

    // Standalone top-bar sign in is removed in favor of sidebar account entry
    const headerSignInBtn = screen.queryByRole('button', { name: /^Sign In$/i });
    expect(headerSignInBtn).not.toBeInTheDocument();
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
