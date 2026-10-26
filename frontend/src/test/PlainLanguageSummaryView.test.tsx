import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PlainLanguageSummaryView } from '../components/PlainLanguageSummaryView';
import * as NoticeContextModule from '../context/NoticeContext';
import type { PlainLanguageSummary } from '../types/api';

describe('PlainLanguageSummaryView Component & Reading Level Selector', () => {
  const mockSummary: PlainLanguageSummary = {
    about: 'Post-Matric Scholarship Scheme 2026',
    eligible: 'Engineering students with 75% aggregate marks',
    actions: 'Submit online form at scholarships.gov.in and dossier to Room 102',
    documents: 'Marksheets, bonafide certificate, and income certificate',
    deadline: '30 November 2026, 5:00 PM',
    help_contact: 'scholarship-helpdesk@dhett.gov.in',
    missing: 'Grievance appeal timeline if application is rejected',
  };

  it('renders summary title, 7 core question cards, and reading level buttons', () => {
    const mockChangeReadingLevel = vi.fn();

    vi.spyOn(NoticeContextModule, 'useNotice').mockReturnValue({
      summaryEn: mockSummary,
      summaryHi: null,
      localizedSummary: null,
      selectedLang: 'en',
      outputLang: 'en',
      readingLevel: 'standard',
      changeReadingLevel: mockChangeReadingLevel,
    } as any);

    render(<PlainLanguageSummaryView />);

    expect(screen.getByText(/Plain-Language Notice Summary/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Simple/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Standard/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Detailed/i })).toBeInTheDocument();

    // Verify 7 core answers rendered
    expect(screen.getByText('Post-Matric Scholarship Scheme 2026')).toBeInTheDocument();
    expect(screen.getByText('Engineering students with 75% aggregate marks')).toBeInTheDocument();
    expect(screen.getByText(/Submit online form at scholarships.gov.in/i)).toBeInTheDocument();
    expect(screen.getByText(/30 November 2026, 5:00 PM/i)).toBeInTheDocument();
  });

  it('triggers changeReadingLevel with "simple" when Simple button is clicked', () => {
    const mockChangeReadingLevel = vi.fn();

    vi.spyOn(NoticeContextModule, 'useNotice').mockReturnValue({
      summaryEn: mockSummary,
      summaryHi: null,
      localizedSummary: null,
      selectedLang: 'en',
      outputLang: 'en',
      readingLevel: 'standard',
      changeReadingLevel: mockChangeReadingLevel,
    } as any);

    render(<PlainLanguageSummaryView />);

    const simpleBtn = screen.getByRole('button', { name: /Simple/i });
    fireEvent.click(simpleBtn);

    expect(mockChangeReadingLevel).toHaveBeenCalledWith('simple');
  });

  it('triggers changeReadingLevel with "detailed" when Detailed button is clicked', () => {
    const mockChangeReadingLevel = vi.fn();

    vi.spyOn(NoticeContextModule, 'useNotice').mockReturnValue({
      summaryEn: mockSummary,
      summaryHi: null,
      localizedSummary: null,
      selectedLang: 'en',
      outputLang: 'en',
      readingLevel: 'standard',
      changeReadingLevel: mockChangeReadingLevel,
    } as any);

    render(<PlainLanguageSummaryView />);

    const detailedBtn = screen.getByRole('button', { name: /Detailed/i });
    fireEvent.click(detailedBtn);

    expect(mockChangeReadingLevel).toHaveBeenCalledWith('detailed');
  });

  it('visibly updates rendered content between Simple, Standard, and Detailed levels', () => {
    const simpleSummary: PlainLanguageSummary = {
      about: 'Topic: Post-Matric Merit Scheme. From: DHETT.',
      eligible: 'Who can apply: STEM students with 75% marks. Cost: Rs. 500 (fee waiver for SC/ST).',
      actions: 'Steps: Fill online form and bring copy to Room 102.',
      documents: 'Bring: Marksheets and income certificate.',
      deadline: 'Due date: 30 November 2026, 5:00 PM.',
      help_contact: 'Contact: scholarship@dhett.gov.in.',
      missing: 'Missing: Grievance appeal timeline.',
    };

    const detailedSummary: PlainLanguageSummary = {
      about: 'Notice Purpose & Directive: Post-Matric Merit Scheme. Issuing Department: DHETT. [Evidence Quote: "Ref DHETT/2026"]',
      eligible: 'Comprehensive Eligibility Criteria: STEM students with 75% marks. Mandatory Conditions, Exceptions & Waivers: SC/ST candidates 100% exempt from Rs. 500 fee. [Evidence Quote: "Fee exemption for SC/ST"]',
      actions: 'Step-by-Step Action Procedure: Complete online portal filing. Procedural & Submission Directive: Deliver physical dossier to Room 102.',
      documents: 'Document Checklist & Verification Requirements: Original marksheets and self-attested photocopies.',
      deadline: 'Official Submission Deadline: 30 November 2026, 5:00 PM. Late Submission Policy: Not specified in notice.',
      help_contact: 'Official Inquiries & Helpdesk Directory: scholarship@dhett.gov.in. Helpdesk Working Hours: Standard business hours.',
      missing: 'Omitted Administrative Details: (1) Grievance timeline. Actionable Citizen Advisory: Confirm with office before deadline.',
    };

    // 1. Render Simple
    const spy = vi.spyOn(NoticeContextModule, 'useNotice');
    spy.mockReturnValue({
      summaryEn: simpleSummary,
      summaryHi: null,
      localizedSummary: null,
      selectedLang: 'en',
      outputLang: 'en',
      readingLevel: 'simple',
      changeReadingLevel: vi.fn(),
    } as any);

    const { rerender } = render(<PlainLanguageSummaryView />);
    expect(screen.getByText('Topic: Post-Matric Merit Scheme. From: DHETT.')).toBeInTheDocument();
    expect(screen.getByText(/Who can apply: STEM students with 75% marks/i)).toBeInTheDocument();

    // 2. Switch to Detailed
    spy.mockReturnValue({
      summaryEn: detailedSummary,
      summaryHi: null,
      localizedSummary: null,
      selectedLang: 'en',
      outputLang: 'en',
      readingLevel: 'detailed',
      changeReadingLevel: vi.fn(),
    } as any);

    rerender(<PlainLanguageSummaryView />);
    expect(screen.getByText(/Notice Purpose & Directive: Post-Matric Merit Scheme/i)).toBeInTheDocument();
    expect(screen.getByText(/\[Evidence Quote: "Ref DHETT\/2026"\]/i)).toBeInTheDocument();
    expect(screen.getByText(/Mandatory Conditions, Exceptions & Waivers:/i)).toBeInTheDocument();
    expect(screen.getByText(/Document Checklist & Verification Requirements:/i)).toBeInTheDocument();

    // 3. Switch back to Simple
    spy.mockReturnValue({
      summaryEn: simpleSummary,
      summaryHi: null,
      localizedSummary: null,
      selectedLang: 'en',
      outputLang: 'en',
      readingLevel: 'simple',
      changeReadingLevel: vi.fn(),
    } as any);

    rerender(<PlainLanguageSummaryView />);
    expect(screen.getByText('Topic: Post-Matric Merit Scheme. From: DHETT.')).toBeInTheDocument();
  });

  it('renders localized summary and Hindi summary when non-English language is active', () => {
    const hindiSummary: PlainLanguageSummary = {
      about: 'विषय: पोस्ट-मैट्रिक मेरिट छात्रवृत्ति योजना २०२६',
      eligible: 'पात्रता: ७५% अंकों वाले इंजीनियरिंग छात्र (एससी/एसटी के लिए शुल्क छूट)',
      actions: 'कदम: ऑनलाइन फॉर्म भरें और कमरा १०२ में जमा करें',
      documents: 'आवश्यक दस्तावेज: अंकतालिका और आय प्रमाण पत्र',
      deadline: 'अंतिम तिथि: ३० नवंबर २०२६',
      help_contact: 'सहायता: scholarship@dhett.gov.in',
      missing: 'अनुपलब्ध जानकारी: शिकायत निवारण समय सीमा',
    };

    vi.spyOn(NoticeContextModule, 'useNotice').mockReturnValue({
      summaryEn: mockSummary,
      summaryHi: hindiSummary,
      localizedSummary: null,
      selectedLang: 'hi',
      outputLang: 'hi',
      readingLevel: 'standard',
      changeReadingLevel: vi.fn(),
    } as any);

    render(<PlainLanguageSummaryView />);
    expect(screen.getByText('विषय: पोस्ट-मैट्रिक मेरिट छात्रवृत्ति योजना २०२६')).toBeInTheDocument();
    expect(screen.getByText(/पात्रता: ७५% अंकों वाले इंजीनियरिंग छात्र/i)).toBeInTheDocument();
  });

  it('renders missing information and uncertainty warnings in summary cards', () => {
    const summaryWithWarnings: PlainLanguageSummary = {
      ...mockSummary,
      missing: 'CRITICAL WARNING: The notice does not specify the late submission appeal window.',
    };

    vi.spyOn(NoticeContextModule, 'useNotice').mockReturnValue({
      summaryEn: summaryWithWarnings,
      summaryHi: null,
      localizedSummary: null,
      selectedLang: 'en',
      outputLang: 'en',
      readingLevel: 'standard',
      changeReadingLevel: vi.fn(),
    } as any);

    render(<PlainLanguageSummaryView />);
    expect(screen.getByText(/CRITICAL WARNING: The notice does not specify the late submission appeal window/i)).toBeInTheDocument();
  });
});
