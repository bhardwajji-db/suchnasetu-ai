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
});
