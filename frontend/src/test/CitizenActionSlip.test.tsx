import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { CitizenActionSlip } from '../components/CitizenActionSlip';
import type { StructuredNotice, ActionChecklist, PlainLanguageSummary } from '../types/api';

const mockNotice: StructuredNotice = {
  purpose: {
    field_name: 'purpose',
    value: 'Post-Matric Merit Scholarship Scheme 2026',
    status: 'stated',
    evidence_quote: 'Post-Matric Merit Scholarship Scheme 2026',
    requires_confirmation: false,
    user_confirmed: false,
  },
  deadline: {
    field_name: 'deadline',
    value: '30 November 2026, 5:00 PM',
    status: 'stated',
    evidence_quote: 'Applications must be submitted by 30 November 2026, 5:00 PM.',
    requires_confirmation: false,
    user_confirmed: false,
  },
  eligibility: {
    field_name: 'eligibility',
    value: 'Minimum 75% marks in qualifying degree',
    status: 'stated',
    evidence_quote: 'Students with minimum 75% marks.',
    requires_confirmation: false,
    user_confirmed: false,
  },
  fee_or_cost: {
    field_name: 'fee_or_cost',
    value: 'No application fee required',
    status: 'not_stated',
    evidence_quote: null,
    requires_confirmation: false,
    user_confirmed: false,
  },
  required_documents: {
    field_name: 'required_documents',
    value: 'Marksheet, Domicile Certificate, Bank Passbook',
    status: 'stated',
    evidence_quote: 'Marksheet, Domicile Certificate, Bank Passbook',
    requires_confirmation: false,
    user_confirmed: false,
  },
  contact_details: {
    field_name: 'contact_details',
    value: 'Scholarship Directorate Helpdesk: 011-23380000',
    status: 'stated',
    evidence_quote: 'Contact Helpdesk: 011-23380000',
    requires_confirmation: false,
    user_confirmed: false,
  },
  required_actions: {
    field_name: 'required_actions',
    value: 'Complete online form and upload certificates',
    status: 'stated',
    evidence_quote: 'Complete online form and upload certificates',
    requires_confirmation: false,
    user_confirmed: false,
  },
  important_conditions: {
    field_name: 'important_conditions',
    value: 'Incomplete applications will be rejected',
    status: 'stated',
    evidence_quote: 'Incomplete applications will be rejected',
    requires_confirmation: false,
    user_confirmed: false,
  },
  missing_information: [],
  uncertain_or_conflicting_details: [],
  raw_notice_text: 'Official Scholarship Notice Raw Text',
};

const mockSummary: PlainLanguageSummary = {
  about: 'This notice invites applications for the 2026 Post-Matric Merit Scholarship.',
  eligible: 'Eligible students with 75% marks.',
  actions: 'Submit application online.',
  documents: 'Marksheet and domicile.',
  deadline: '30 November 2026.',
  help_contact: '011-23380000',
  missing: 'None',
};

const mockChecklist: ActionChecklist = {
  items: [
    {
      step_number: 1,
      action: 'Verify qualifying degree marksheet marks exceed 75%',
      category: 'eligibility',
      is_mandatory: true,
      requires_confirmation: false,
      is_completed: false,
    },
    {
      step_number: 2,
      action: 'Submit online application before 30 November 2026',
      category: 'submission',
      is_mandatory: true,
      requires_confirmation: false,
      is_completed: false,
    },
  ],
};

describe('CitizenActionSlip Component', () => {
  it('renders official header, key grounded fields, and checklist items', () => {
    render(
      <CitizenActionSlip
        notice={mockNotice}
        summary={mockSummary}
        checklist={mockChecklist}
        documentId="doc_scholarship_2026"
        fingerprint="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        currentLanguage="en"
      />
    );

    expect(screen.getByText(/SUCHNASETU AI • सूचना \+ सेतु/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Citizen Action Dossier/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/Post-Matric Merit Scholarship Scheme 2026/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/30 November 2026, 5:00 PM/i)).toBeInTheDocument();
    expect(screen.getByText(/Minimum 75% marks in qualifying degree/i)).toBeInTheDocument();
    expect(screen.getByText(/Verify qualifying degree marksheet marks exceed 75%/i)).toBeInTheDocument();
    expect(screen.getByText(/Official Citizen Advisory/i)).toBeInTheDocument();
  });
});
