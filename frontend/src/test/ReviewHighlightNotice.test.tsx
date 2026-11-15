import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React, { useEffect } from 'react';
import { NoticeProvider, useNotice } from '../context/NoticeContext';
import { FactCard } from '../components/FactCard';
import { OriginalNoticeViewerModal } from '../components/OriginalNoticeViewerModal';
import { apiClient } from '../services/apiClient';
import type { ExtractedFact, OCRResponse } from '../types/api';

const sampleNoticeText = `GOVERNMENT SCHOLARSHIP NOTIFICATION 2026
Department of Higher Education, New Delhi.

--- Page 1 ---
The closing date for submission of online applications is 31 October 2026.
Late applications will be rejected.

--- Page 2 ---
Candidates must possess a minimum of 75 percent marks in qualifying degree.
All applications must be verified by the institutional head.`;

const TestHarness: React.FC<{
  initialImage?: string;
  initialOcrResult?: OCRResponse;
  facts: Array<{ fieldName: string; displayName: string; fact: ExtractedFact }>;
}> = ({ initialImage, initialOcrResult, facts }) => {
  const { setRawNoticeText, setUploadedImage, setOcrResult } = useNotice();

  useEffect(() => {
    setRawNoticeText(sampleNoticeText);
    if (initialImage) {
      setUploadedImage(initialImage, new File(['dummy'], 'test.png', { type: 'image/png' }));
    }
    if (initialOcrResult) {
      setOcrResult(initialOcrResult);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div>
      <div data-testid="facts-grid">
        {facts.map((f) => (
          <FactCard
            key={f.fieldName}
            fieldName={f.fieldName}
            displayName={f.displayName}
            fact={f.fact}
          />
        ))}
      </div>
      <OriginalNoticeViewerModal />
    </div>
  );
};

describe('Click-to-Review Red Underline for OCR Notice Text', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    vi.spyOn(apiClient, 'getSavedNotices').mockResolvedValue([]);
    vi.spyOn(apiClient, 'getHealth').mockResolvedValue({ status: 'ok', active_provider: 'ollama' } as any);
    vi.spyOn(apiClient, 'getProviders').mockResolvedValue([]);
    vi.spyOn(apiClient, 'getSamples').mockResolvedValue([]);
  });

  it('navigates to original notice preview and renders red underline when clicking Review on a flagged field', () => {
    const facts = [
      {
        fieldName: 'deadline',
        displayName: 'Closing Deadline',
        fact: {
          field_name: 'deadline',
          value: '31 October 2026',
          status: 'uncertain' as const,
          evidence_quote: 'The closing date for submission of online applications is 31 October 2026.',
          requires_confirmation: true,
          user_confirmed: false,
        },
      },
      {
        fieldName: 'eligibility',
        displayName: 'Eligibility Criteria',
        fact: {
          field_name: 'eligibility',
          value: '75 percent marks',
          status: 'uncertain' as const,
          evidence_quote: 'Candidates must possess a minimum of 75 percent marks in qualifying degree.',
          requires_confirmation: true,
          user_confirmed: false,
        },
      },
    ];

    render(
      <NoticeProvider>
        <TestHarness facts={facts} />
      </NoticeProvider>
    );

    // Initial state: modal is closed
    expect(screen.queryByTestId('review-highlight-bar')).not.toBeInTheDocument();

    // 1. Click Review for deadline
    const reviewDeadlineBtn = screen.getByTestId('review-btn-deadline');
    fireEvent.click(reviewDeadlineBtn);

    // Modal opens with review highlight control bar
    expect(screen.getByTestId('review-highlight-bar')).toBeInTheDocument();
    expect(screen.getByText(/Reviewing: Closing Deadline/i)).toBeInTheDocument();

    // Red underline highlight is rendered on matching text
    const redUnderlines = screen.getAllByTestId('text-red-underline-highlight');
    expect(redUnderlines.length).toBeGreaterThan(0);
    expect(redUnderlines[0]).toHaveClass('border-red-600');
  });

  it('switches highlight to new field and removes previous selection when another field is selected', () => {
    const facts = [
      {
        fieldName: 'deadline',
        displayName: 'Closing Deadline',
        fact: {
          field_name: 'deadline',
          value: '31 October 2026',
          status: 'uncertain' as const,
          evidence_quote: 'The closing date for submission of online applications is 31 October 2026.',
          requires_confirmation: true,
          user_confirmed: false,
        },
      },
      {
        fieldName: 'eligibility',
        displayName: 'Eligibility Criteria',
        fact: {
          field_name: 'eligibility',
          value: '75 percent marks',
          status: 'uncertain' as const,
          evidence_quote: 'Candidates must possess a minimum of 75 percent marks in qualifying degree.',
          requires_confirmation: true,
          user_confirmed: false,
        },
      },
    ];

    render(
      <NoticeProvider>
        <TestHarness facts={facts} />
      </NoticeProvider>
    );

    // Click Review on deadline
    fireEvent.click(screen.getByTestId('review-btn-deadline'));
    expect(screen.getByText(/Reviewing: Closing Deadline/i)).toBeInTheDocument();

    // Click Review on eligibility (switching selection)
    fireEvent.click(screen.getByTestId('review-btn-eligibility'));

    // Highlight switches to eligibility and previous deadline highlight bar is replaced
    expect(screen.getByText(/Reviewing: Eligibility Criteria/i)).toBeInTheDocument();
    expect(screen.queryByText(/Reviewing: Closing Deadline/i)).not.toBeInTheDocument();

    // Matching text is now eligibility text
    const redUnderlines = screen.getAllByTestId('text-red-underline-highlight');
    expect(redUnderlines.length).toBeGreaterThan(0);
  });

  it('identifies page number and displays page badge for multi-page notice', () => {
    const facts = [
      {
        fieldName: 'eligibility',
        displayName: 'Eligibility Criteria',
        fact: {
          field_name: 'eligibility',
          value: '75 percent marks',
          status: 'uncertain' as const,
          evidence_quote: 'Candidates must possess a minimum of 75 percent marks in qualifying degree.',
          requires_confirmation: true,
          user_confirmed: false,
        },
      },
    ];

    render(
      <NoticeProvider>
        <TestHarness facts={facts} />
      </NoticeProvider>
    );

    fireEvent.click(screen.getByTestId('review-btn-eligibility'));

    // Page indicator badge should display Page 2
    expect(screen.getByTestId('review-page-indicator')).toHaveTextContent('Page 2');
  });

  it('displays “Could not locate this text in the original notice” and no red underline when text cannot be found', () => {
    const facts = [
      {
        fieldName: 'missing_field',
        displayName: 'Missing Dimension',
        fact: {
          field_name: 'missing_field',
          value: 'NonExistentGibberishVal12345',
          status: 'uncertain' as const,
          evidence_quote: 'Unverifiable text quote that does not appear anywhere in this document.',
          requires_confirmation: true,
          user_confirmed: false,
        },
      },
    ];

    render(
      <NoticeProvider>
        <TestHarness facts={facts} />
      </NoticeProvider>
    );

    fireEvent.click(screen.getByTestId('review-btn-missing_field'));

    // Displays clear not found message
    expect(screen.getByTestId('review-not-found-message')).toHaveTextContent(
      'Could not locate this text in the original notice'
    );

    // No text red underline elements are rendered
    expect(screen.queryByTestId('text-red-underline-highlight')).not.toBeInTheDocument();
  });

  it('renders red underline OCR overlays in image mode with accurate bounding boxes', () => {
    const initialOcrResult: OCRResponse = {
      extracted_text: sampleNoticeText,
      raw_ocr_text: sampleNoticeText,
      confidence_score: 90,
      document_quality_score: 92,
      deskew_angle: 0,
      orientation_applied: 0,
      detected_language: 'hin+eng',
      image_dimensions: [1000, 1500],
      uncertain_spans: [
        {
          text: '31 October 2026',
          confidence: 72,
          line_num: 3,
          box: [120, 200, 480, 240],
          field_name: 'deadline',
          status: 'flagged',
        },
      ],
      word_boxes: [
        {
          text: '31 October 2026',
          box: [120, 200, 480, 240],
        },
      ],
    };

    const facts = [
      {
        fieldName: 'deadline',
        displayName: 'Closing Deadline',
        fact: {
          field_name: 'deadline',
          value: '31 October 2026',
          status: 'uncertain' as const,
          evidence_quote: '31 October 2026',
          requires_confirmation: true,
          user_confirmed: false,
        },
      },
    ];

    render(
      <NoticeProvider>
        <TestHarness
          initialImage="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
          initialOcrResult={initialOcrResult}
          facts={facts}
        />
      </NoticeProvider>
    );

    fireEvent.click(screen.getByTestId('review-btn-deadline'));

    // OCR red underline overlays are rendered on the image
    const ocrOverlays = screen.getAllByTestId('ocr-red-underline-highlight');
    expect(ocrOverlays.length).toBeGreaterThan(0);
    expect(ocrOverlays[0]).toHaveClass('border-red-600');
    expect(ocrOverlays[0]).toHaveClass('bg-red-500/15');
  });

  it('allows exiting highlight mode via Exit Highlight button and keyboard Escape key', () => {
    const facts = [
      {
        fieldName: 'deadline',
        displayName: 'Closing Deadline',
        fact: {
          field_name: 'deadline',
          value: '31 October 2026',
          status: 'uncertain' as const,
          evidence_quote: '31 October 2026',
          requires_confirmation: true,
          user_confirmed: false,
        },
      },
    ];

    render(
      <NoticeProvider>
        <TestHarness facts={facts} />
      </NoticeProvider>
    );

    // Open highlight
    fireEvent.click(screen.getByTestId('review-btn-deadline'));
    expect(screen.getByTestId('review-highlight-bar')).toBeInTheDocument();

    // Click Exit Highlight button
    const exitBtn = screen.getByTestId('exit-review-highlight-btn');
    fireEvent.click(exitBtn);

    // Highlight bar is cleared, but modal stays open
    expect(screen.queryByTestId('review-highlight-bar')).not.toBeInTheDocument();
    expect(screen.getByText(/Original Notice Document Viewer/i)).toBeInTheDocument();

    // Re-trigger highlight
    fireEvent.click(screen.getByTestId('review-btn-deadline'));
    expect(screen.getByTestId('review-highlight-bar')).toBeInTheDocument();

    // Press Escape key -> exits highlight
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(screen.queryByTestId('review-highlight-bar')).not.toBeInTheDocument();
    expect(screen.getByText(/Original Notice Document Viewer/i)).toBeInTheDocument();

    // Press Escape key again -> closes modal
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(screen.queryByText(/Original Notice Document Viewer/i)).not.toBeInTheDocument();
  });
});
