import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MetricCard } from '../components/MetricCard';
import type { ExtractedFact } from '../types/api';

describe('MetricCard Component', () => {
  it('renders metric label, stated fact value, and status badge', () => {
    const fact: ExtractedFact = {
      field_name: 'deadline',
      value: '5:00 PM on 30 October 2026',
      status: 'stated',
      evidence_quote: 'All applications must be submitted by 5:00 PM on 30 October 2026.',
      requires_confirmation: false,
      user_confirmed: false,
    };

    render(
      <MetricCard
        fact={fact}
        label="Closing Deadline"
        iconType="deadline"
      />
    );

    expect(screen.getByText('Closing Deadline')).toBeInTheDocument();
    expect(screen.getByText('5:00 PM on 30 October 2026')).toBeInTheDocument();
    expect(screen.getByText(/stated/i)).toBeInTheDocument();
  });

  it('renders pending placeholder when fact is null', () => {
    render(
      <MetricCard
        fact={null}
        label="Purpose"
        iconType="purpose"
      />
    );

    expect(screen.getByText('Purpose')).toBeInTheDocument();
    expect(screen.getByText(/Pending notice analysis/i)).toBeInTheDocument();
  });
});
