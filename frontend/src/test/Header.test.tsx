import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
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

  it('renders accessible sign in control and opens auth modal', () => {
    render(
      <NoticeProvider>
        <Header />
      </NoticeProvider>
    );

    const signInBtn = screen.getByRole('button', { name: /Sign In/i });
    expect(signInBtn).toBeInTheDocument();
    fireEvent.click(signInBtn);
    expect(screen.getByRole('dialog', { name: /Citizen Authentication/i })).toBeInTheDocument();
  });
});
