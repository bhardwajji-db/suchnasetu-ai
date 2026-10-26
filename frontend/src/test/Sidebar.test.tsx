import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Sidebar } from '../components/Sidebar';
import { NoticeProvider } from '../context/NoticeContext';

describe('Sidebar Component', () => {
  it('renders navigation tabs and quick-load controls', () => {
    render(
      <NoticeProvider>
        <Sidebar />
      </NoticeProvider>
    );

    expect(screen.getByText('1. Ingestion & OCR')).toBeInTheDocument();
    expect(screen.getByText('2. Grounded Facts')).toBeInTheDocument();
    expect(screen.getByText('3. Summary & Actions')).toBeInTheDocument();
    expect(screen.getByText('4. Revision Ledger')).toBeInTheDocument();
    expect(screen.getByText('5. Eligibility Check')).toBeInTheDocument();
    expect(screen.getByText('6. Follow-Up Q&A')).toBeInTheDocument();
    expect(screen.getByText(/Competition Demo/i)).toBeInTheDocument();
    expect(screen.getByText(/Load Selected Notice/i)).toBeInTheDocument();
    expect(screen.getByText(/Reset Workspace/i)).toBeInTheDocument();
  });

  it('renders subtle citizen account access in the sidebar for guests', () => {
    render(
      <NoticeProvider>
        <Sidebar />
      </NoticeProvider>
    );

    const accountButton = screen.getByRole('button', { name: /Sign In to citizen account/i });
    expect(accountButton).toBeInTheDocument();
    expect(accountButton).toHaveTextContent(/Sign In \/ Register/i);
    expect(accountButton).toHaveTextContent(/Save notices & progress/i);
  });
});
