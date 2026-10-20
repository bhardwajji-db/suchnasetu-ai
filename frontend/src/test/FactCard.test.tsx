import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FactCard } from '../components/FactCard';
import { NoticeProvider } from '../context/NoticeContext';
import type { ExtractedFact } from '../types/api';

describe('FactCard Component', () => {
  it('renders fact with verbatim quote and stated status', () => {
    const fact: ExtractedFact = {
      field_name: 'eligibility',
      value: 'Minimum 75% marks in qualifying examination',
      status: 'stated',
      evidence_quote: 'Students securing minimum 75% marks in their previous qualifying examination are eligible.',
      requires_confirmation: false,
      user_confirmed: false,
    };

    render(
      <NoticeProvider>
        <FactCard
          fact={fact}
          fieldName="eligibility"
          displayName="Eligibility Criteria"
        />
      </NoticeProvider>
    );

    expect(screen.getByText('Eligibility Criteria')).toBeInTheDocument();
    expect(screen.getByText('Minimum 75% marks in qualifying examination')).toBeInTheDocument();
    expect(screen.getByText(/"Students securing minimum 75% marks/i)).toBeInTheDocument();
  });

  it('renders confirmation button when fact is uncertain and requires confirmation', () => {
    const uncertainFact: ExtractedFact = {
      field_name: 'deadline',
      value: 'Late October 2026 (tentative)',
      status: 'uncertain',
      evidence_quote: 'Expected deadline is late October 2026.',
      requires_confirmation: true,
      user_confirmed: false,
      explanation: 'Tentative date requires official verification.',
    };

    render(
      <NoticeProvider>
        <FactCard
          fact={uncertainFact}
          fieldName="deadline"
          displayName="Closing Deadline"
        />
      </NoticeProvider>
    );

    expect(screen.getByText(/Confirm Detail/i)).toBeInTheDocument();
    expect(screen.getByText(/Tentative date requires official verification/i)).toBeInTheDocument();
  });
});
