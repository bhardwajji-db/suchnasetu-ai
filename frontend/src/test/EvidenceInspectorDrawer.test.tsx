import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { EvidenceInspectorDrawer } from '../components/EvidenceInspectorDrawer';
import { NoticeProvider, useNotice } from '../context/NoticeContext';
import React, { useEffect } from 'react';
import type { TrustEvidence } from '../types/api';

const TriggerDrawer: React.FC<{ status: 'VERIFIED_IN_SOURCE' | 'UNVERIFIED' | 'UNCERTAIN_OCR' }> = ({ status }) => {
  const { openEvidenceInspector } = useNotice();

  useEffect(() => {
    const evidence: TrustEvidence = {
      evidence_id: 'ev-1234',
      claim_text: 'Application deadline is 31 October 2026',
      source_doc_title: 'Central Merit Scholarship Circular',
      page_number: 1,
      line_start: 14,
      line_end: 14,
      verbatim_excerpt: 'Last date for submission is 31st October 2026 up to 17:00 hrs.',
      verification_status: status,
      confidence_rationale: 'Exact verbatim quotation verified in notice (line 14).',
      is_inert_safe: true,
    };
    openEvidenceInspector(evidence, 'Sample Notice with 31st October 2026 deadline.');
  }, [openEvidenceInspector, status]);

  return <EvidenceInspectorDrawer />;
};

describe('EvidenceInspectorDrawer Component', () => {
  it('renders verified evidence drawer with line attribution and rationale', () => {
    render(
      <NoticeProvider>
        <TriggerDrawer status="VERIFIED_IN_SOURCE" />
      </NoticeProvider>
    );

    expect(screen.getByText(/Evidence Trust Inspector/i)).toBeInTheDocument();
    expect(screen.getByText(/VERIFIED IN SOURCE TEXT/i)).toBeInTheDocument();
    expect(screen.getByText(/Application deadline is 31 October 2026/i)).toBeInTheDocument();
    expect(screen.getByText(/Exact verbatim quotation verified in notice/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Close Inspector/i })).toBeInTheDocument();
    expect(screen.getByText(/Dismiss Inspector/i)).toBeInTheDocument();
  });

  it('renders ungrounded citation badge when fact lacks source backing', () => {
    render(
      <NoticeProvider>
        <TriggerDrawer status="UNVERIFIED" />
      </NoticeProvider>
    );

    expect(screen.getByText(/UNGROUNDED \/ UNVERIFIED CITATION/i)).toBeInTheDocument();
  });
});
