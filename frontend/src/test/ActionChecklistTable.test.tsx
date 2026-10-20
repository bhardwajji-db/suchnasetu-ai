import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ActionChecklistTable } from '../components/ActionChecklistTable';
import { NoticeProvider } from '../context/NoticeContext';
import * as NoticeContextModule from '../context/NoticeContext';
import type { ActionChecklist } from '../types/api';

describe('ActionChecklistTable Component', () => {
  const mockChecklist: ActionChecklist = {
    items: [
      {
        step_number: 1,
        action: 'Verify Eligibility: Minimum 75% marks required.',
        category: 'eligibility',
        is_mandatory: true,
        requires_confirmation: false,
        is_completed: false,
        grounded_quote: 'Students securing minimum 75% marks...',
      },
      {
        step_number: 2,
        action: 'Submit Application Form before deadline.',
        category: 'submission',
        is_mandatory: true,
        requires_confirmation: false,
        is_completed: true,
      },
    ],
  };

  it('renders checklist items, category badges, and export buttons', () => {
    vi.spyOn(NoticeContextModule, 'useNotice').mockReturnValue({
      checklistEn: mockChecklist,
      checklistHi: null,
      selectedLang: 'en',
      toggleChecklistItem: vi.fn(),
      structuredNotice: { purpose: { value: 'Scholarship' } } as any,
      summaryEn: null,
      summaryHi: null,
    } as any);

    render(
      <NoticeProvider>
        <ActionChecklistTable />
      </NoticeProvider>
    );

    expect(screen.getByText(/Sequential Action Checklist/i)).toBeInTheDocument();
    expect(screen.getByText('Verify Eligibility: Minimum 75% marks required.')).toBeInTheDocument();
    expect(screen.getByText('Submit Application Form before deadline.')).toBeInTheDocument();
    expect(screen.getByText(/1 \/ 2 Done \(50%\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Download Markdown/i)).toBeInTheDocument();
    expect(screen.getByText(/Add to Calendar/i)).toBeInTheDocument();
  });
});
