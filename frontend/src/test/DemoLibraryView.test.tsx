import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { DemoLibraryView } from '../views/DemoLibraryView';
import { NoticeProvider, useNotice } from '../context/NoticeContext';
import { I18nProvider } from '../i18n';
import { apiClient } from '../services/apiClient';
import { ErrorBoundary } from '../components/ErrorBoundary';

const mockDemos = [
  {
    id: 'DEMO-01',
    title: 'National Means-cum-Merit Scholarship Scheme (NMMSS)',
    language: 'en',
    format: 'txt',
    category: 'scholarship',
    description: 'Centrally sponsored scholarship scheme notification.',
    file_path: 'tests/fixtures/demo_library/demo_01_en.txt',
    word_count: 245,
  },
  {
    id: 'DEMO-02',
    title: 'UPSC Combined Geo-Scientist Examination 2026',
    language: 'en',
    format: 'pdf',
    category: 'examination',
    description: 'Official Union Public Service Commission competitive examination notification.',
    file_path: 'tests/fixtures/demo_library/demo_02_en.pdf',
    word_count: 480,
  },
  {
    id: 'DEMO-03',
    title: 'AICTE Faculty Development & Research Promotion Scheme',
    language: 'en',
    format: 'docx',
    category: 'regulatory',
    description: 'All India Council for Technical Education institutional funding circular.',
    file_path: 'tests/fixtures/demo_library/demo_03_en.docx',
    word_count: 380,
  },
];

describe('DemoLibraryView Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders demo library view with search and filter controls', async () => {
    vi.spyOn(apiClient, 'getDemoLibrary').mockResolvedValue({
      demos: mockDemos,
      total: mockDemos.length,
    });

    render(
      <I18nProvider>
        <NoticeProvider>
          <DemoLibraryView />
        </NoticeProvider>
      </I18nProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/National Means-cum-Merit Scholarship Scheme/i)).toBeInTheDocument();
      expect(screen.getByText(/UPSC Combined Geo-Scientist Examination 2026/i)).toBeInTheDocument();
      expect(screen.getByText(/AICTE Faculty Development & Research Promotion Scheme/i)).toBeInTheDocument();
    });

    expect(screen.getByPlaceholderText(/Search title, category, keywords.../i)).toBeInTheDocument();
    expect(screen.getByText(/All Languages/i)).toBeInTheDocument();
  });

  it('renders correctly when API returns a raw JSON array of demo items', async () => {
    vi.spyOn(apiClient, 'getDemoLibrary').mockResolvedValue(mockDemos as any);

    render(
      <I18nProvider>
        <NoticeProvider>
          <DemoLibraryView />
        </NoticeProvider>
      </I18nProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/UPSC Combined Geo-Scientist Examination 2026/i)).toBeInTheDocument();
    });
  });

  it('renders safe empty state without crashing when API returns malformed or empty data', async () => {
    vi.spyOn(apiClient, 'getDemoLibrary').mockResolvedValue({} as any);

    render(
      <I18nProvider>
        <NoticeProvider>
          <DemoLibraryView />
        </NoticeProvider>
      </I18nProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/No matching demo notices found/i)).toBeInTheDocument();
    });
  });

  it('clicking Preview opens preview modal with raw_text without initiating analysis', async () => {
    vi.spyOn(apiClient, 'getDemoLibrary').mockResolvedValue({ demos: mockDemos, total: 3 });
    const loadSpy = vi.spyOn(apiClient, 'loadDemoLibraryItem').mockResolvedValue({
      id: 'DEMO-02',
      demo_id: 'DEMO-02',
      title: 'UPSC Combined Geo-Scientist Examination 2026',
      language: 'en',
      source_language: 'en',
      format: 'pdf',
      text: 'UNION PUBLIC SERVICE COMMISSION EXAMINATION NOTICE NO. 02/2026-GEO.',
      raw_text: 'UNION PUBLIC SERVICE COMMISSION EXAMINATION NOTICE NO. 02/2026-GEO.',
      char_count: 70,
      word_count: 8,
    });
    const analyzeSpy = vi.spyOn(apiClient, 'analyzeNotice');

    render(
      <I18nProvider>
        <NoticeProvider>
          <DemoLibraryView />
        </NoticeProvider>
      </I18nProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/UPSC Combined Geo-Scientist Examination 2026/i)).toBeInTheDocument();
    });

    const previewButtons = screen.getAllByRole('button', { name: /preview/i });
    fireEvent.click(previewButtons[1]); // Click Preview on DEMO-02 (PDF)

    await waitFor(() => {
      expect(loadSpy).toHaveBeenCalledWith('DEMO-02');
      expect(screen.getByText(/UNION PUBLIC SERVICE COMMISSION EXAMINATION NOTICE NO. 02\/2026-GEO./i)).toBeInTheDocument();
    });

    // Preview should NOT trigger analyzeNotice
    expect(analyzeSpy).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: /load into assistant/i })).toBeInTheDocument();
  });

  it('clicking "Load & Analyze" executes analysis workflow and handles backend payload safely', async () => {
    vi.spyOn(apiClient, 'getDemoLibrary').mockResolvedValue({ demos: mockDemos, total: 3 });
    vi.spyOn(apiClient, 'loadDemoLibraryItem').mockResolvedValue({
      id: 'DEMO-03',
      demo_id: 'DEMO-03',
      title: 'AICTE Faculty Development & Research Promotion Scheme',
      language: 'en',
      source_language: 'en',
      format: 'docx',
      text: 'ALL INDIA COUNCIL FOR TECHNICAL EDUCATION NOTIFICATION FOR RESEARCH SCHEME 2026.',
      raw_text: 'ALL INDIA COUNCIL FOR TECHNICAL EDUCATION NOTIFICATION FOR RESEARCH SCHEME 2026.',
      char_count: 80,
      word_count: 10,
    });
    const analyzeSpy = vi.spyOn(apiClient, 'analyzeNotice').mockResolvedValue({
      session_id: 'sess_123',
      fingerprint: 'fp_123',
      duration_seconds: 1.2,
      detected_language: 'en',
      structured_notice: {
        issuing_authority: { value: 'AICTE', status: 'stated', verbatim_quote: 'ALL INDIA COUNCIL FOR TECHNICAL EDUCATION', confidence: 0.95 },
        main_subject: { value: 'Research Promotion Scheme', status: 'stated', verbatim_quote: 'RESEARCH SCHEME 2026', confidence: 0.95 },
        notice_reference_number: { value: 'AICTE/FD/2026/01', status: 'stated', verbatim_quote: '2026', confidence: 0.90 },
        deadline: { value: '31 March 2026', status: 'stated', verbatim_quote: '31 March 2026', confidence: 0.95 },
        eligibility: { value: 'Full-time faculty members', status: 'stated', verbatim_quote: 'faculty members', confidence: 0.90 },
        required_actions: { value: 'Submit proposal online', status: 'stated', verbatim_quote: 'Submit proposal', confidence: 0.90 },
        fee_structure: { value: 'Nil', status: 'not_specified', verbatim_quote: null, confidence: 0.95 },
        purpose: { value: 'Promote institutional research', status: 'stated', verbatim_quote: 'RESEARCH SCHEME', confidence: 0.95 },
      },
      summary_en: 'AICTE Research Promotion Scheme notification for faculty.',
      checklist_en: [{ step: 1, action: 'Register proposal', deadline: '31 March 2026', mandatory: true }],
    } as any);

    const TabObserver = () => {
      const { activeTab } = useNotice();
      return <div data-testid="tab-observer">Tab: {activeTab}</div>;
    };

    render(
      <I18nProvider>
        <NoticeProvider>
          <TabObserver />
          <DemoLibraryView />
        </NoticeProvider>
      </I18nProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/AICTE Faculty Development & Research Promotion Scheme/i)).toBeInTheDocument();
    });

    const loadButtons = screen.getAllByRole('button', { name: /load & analyze/i });
    // Click Load & Analyze on DEMO-03 (DOCX)
    fireEvent.click(loadButtons[2]);

    await waitFor(() => {
      expect(analyzeSpy).toHaveBeenCalledWith(
        'ALL INDIA COUNCIL FOR TECHNICAL EDUCATION NOTIFICATION FOR RESEARCH SCHEME 2026.',
        expect.any(String),
        expect.any(String),
        null,
        expect.any(String)
      );
    });

    // Active tab should be 1 (Ingestion / Dual-Region Intelligence Workspace)
    expect(screen.getByTestId("tab-observer")).toHaveTextContent("Tab: 1");
  });

  it('ErrorBoundary gracefully catches child rendering exceptions without crashing or showing blank screen', () => {
    const ProblematicComponent = () => {
      throw new Error('Simulated critical React render crash');
    };

    render(
      <ErrorBoundary>
        <ProblematicComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText(/Something went wrong displaying this view/i)).toBeInTheDocument();
    expect(screen.getByText(/Simulated critical React render crash/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry view/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /reload page/i })).toBeInTheDocument();
  });
});
