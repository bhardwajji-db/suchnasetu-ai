import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ConfirmationModal } from '../components/ConfirmationModal';
import { NoticeProvider, useNotice } from '../context/NoticeContext';
import React, { useEffect } from 'react';
import type { ExtractedFact } from '../types/api';

const TriggerModal: React.FC = () => {
  const { openConfirmationModal } = useNotice();

  useEffect(() => {
    const fact: ExtractedFact = {
      field_name: 'deadline',
      value: 'Late October 2026 (tentative)',
      status: 'uncertain',
      evidence_quote: 'Deadline is late October 2026 tentatively.',
      requires_confirmation: true,
      user_confirmed: false,
      explanation: 'Tentative date needs verification.',
    };
    openConfirmationModal('deadline', 'Closing Deadline', fact);
  }, [openConfirmationModal]);

  return <ConfirmationModal />;
};

describe('ConfirmationModal Component', () => {
  it('renders modal with field name, original value, and action buttons', () => {
    render(
      <NoticeProvider>
        <TriggerModal />
      </NoticeProvider>
    );

    expect(screen.getByText(/Review & Confirm Detail/i)).toBeInTheDocument();
    expect(screen.getByText(/Closing Deadline/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Late October 2026/i)[0]).toBeInTheDocument();
    expect(screen.getByText(/Confirm As-Is/i)).toBeInTheDocument();
    expect(screen.getByText(/Save Verification/i)).toBeInTheDocument();
  });
});
