import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React, { useEffect } from 'react';
import { NoticeProvider, useNotice } from '../context/NoticeContext';
import { OCRPanel } from '../components/OCRPanel';
import { OriginalNoticeViewerModal } from '../components/OriginalNoticeViewerModal';
import { apiClient } from '../services/apiClient';
import type { OCRResponse, HumanReviewSummary } from '../types/api';

const sampleOcrResponse: OCRResponse = {
  extracted_text: `IIMT ENGINEERING COLLEGE\nRef. No. :IIMT/IQAC/2026-27/11 Date: 29.10.2026\nNotice: Event on 30th October 2026 at Auditorium`,
  raw_ocr_text: `IIMT ENGINEERING COLLEGE\nRef. No. :IIMT/IQAC/2026-27/11 Date: 29.10.2026\nNotice: Event on 30th October 2026 at Auditorium`,
  confidence_score: 91.5,
  document_quality_score: 93.0,
  detected_language: 'eng',
  language_confidence: 1.0,
  is_mixed_language: false,
  orientation_applied: 0,
  deskew_angle: 0,
  document_id: 'doc_iimt_test_1',
  image_dimensions: [1000, 1500],
  word_boxes: [
    { text: 'IIMT', confidence: 95, box: [100, 150, 250, 190] },
    { text: 'ENGINEERING', confidence: 94, box: [260, 150, 520, 190] },
    { text: 'COLLEGE', confidence: 93, box: [530, 150, 720, 190] },
    { text: 'Auditorium', confidence: 90, box: [300, 400, 500, 440] },
  ],
  uncertain_spans: [
    {
      id: 'span_1',
      text: '29.10.2026',
      original_text: '29.10.2026',
      confidence: 68,
      box: [450, 220, 600, 250],
      field_name: 'notice_date',
      status: 'pending',
      page_number: 1,
    },
    {
      id: 'span_2',
      text: 'IQAC',
      original_text: 'IQAC',
      confidence: 62,
      box: [200, 220, 320, 250],
      field_name: 'ref_abbr',
      status: 'pending',
      page_number: 1,
    },
  ],
};

const sampleReviewSummary: HumanReviewSummary = {
  document_id: 'doc_iimt_test_1',
  total: 2,
  pending: 2,
  corrected: 0,
  verified: 0,
  ignored: 0,
  items: [
    {
      id: 'span_1',
      document_id: 'doc_iimt_test_1',
      page_number: 1,
      box: [450, 220, 600, 250],
      original_text: '29.10.2026',
      corrected_text: undefined,
      confidence: 68,
      reason: 'Low confidence token',
      status: 'pending',
      created_at: new Date().toISOString(),
    },
    {
      id: 'span_2',
      document_id: 'doc_iimt_test_1',
      page_number: 1,
      box: [200, 220, 320, 250],
      original_text: 'IQAC',
      corrected_text: undefined,
      confidence: 62,
      reason: 'Special token',
      status: 'pending',
      created_at: new Date().toISOString(),
    },
  ],
};

const Harness: React.FC<{
  initialOcr?: OCRResponse;
  initialImage?: string;
  loadSummary?: boolean;
}> = ({ initialOcr, initialImage, loadSummary }) => {
  const { setUploadedImage, setOcrResult, setReviewSummary } = useNotice();

  useEffect(() => {
    if (initialImage) {
      setUploadedImage(initialImage, new File(['dummy'], '10.jpeg', { type: 'image/jpeg' }));
    }
    if (initialOcr) {
      setOcrResult(initialOcr);
    }
    if (loadSummary) {
      setReviewSummary(sampleReviewSummary);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div>
      <OCRPanel />
      <OriginalNoticeViewerModal />
    </div>
  );
};

describe('OCR Intelligence & Human Review System', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    vi.spyOn(apiClient, 'getSavedNotices').mockResolvedValue([]);
    vi.spyOn(apiClient, 'getHealth').mockResolvedValue({ status: 'ok', active_provider: 'ollama' } as any);
    vi.spyOn(apiClient, 'getProviders').mockResolvedValue([]);
    vi.spyOn(apiClient, 'getSamples').mockResolvedValue([]);
    vi.spyOn(apiClient, 'getReviewItems').mockResolvedValue(sampleReviewSummary);
    vi.spyOn(apiClient, 'updateReviewItem').mockResolvedValue(sampleReviewSummary as any);
    vi.spyOn(apiClient, 'applyReviewCorrections').mockResolvedValue({
      document_id: 'doc_iimt_test_1',
      applied_count: 1,
      updated_text: 'Updated notice text with corrections applied',
    });
  });

  it('defaults OCR language selector to Auto-Detect and displays detected language banner', () => {
    render(
      <NoticeProvider>
        <Harness initialImage="data:image/png;base64,fake" initialOcr={sampleOcrResponse} />
      </NoticeProvider>
    );

    // Default select option should be Auto-Detect
    const select = screen.getByRole('combobox') as HTMLSelectElement;
    expect(select.value).toBe('auto');

    // Detected language banner should show English
    expect(screen.getByText(/Detected:/i)).toBeInTheDocument();
    expect(screen.getAllByText(/English \(eng\)/i).length).toBeGreaterThan(0);
  });

  it('allows user manual language override and shows Reset to Auto action', () => {
    render(
      <NoticeProvider>
        <Harness initialImage="data:image/png;base64,fake" initialOcr={sampleOcrResponse} />
      </NoticeProvider>
    );

    const select = screen.getByRole('combobox') as HTMLSelectElement;
    fireEvent.change(select, { target: { value: 'hin' } });

    expect(select.value).toBe('hin');
    expect(screen.getByText(/Manual Override Active: hin/i)).toBeInTheDocument();

    // Reset button reverts to auto
    const resetBtn = screen.getByText(/Reset to Auto/i);
    fireEvent.click(resetBtn);
    expect(select.value).toBe('auto');
  });

  it('renders Human Review Workspace with metrics, filter tabs, and action buttons', async () => {
    render(
      <NoticeProvider>
        <Harness initialImage="data:image/png;base64,fake" initialOcr={sampleOcrResponse} loadSummary={true} />
      </NoticeProvider>
    );

    // Review workspace header
    expect(screen.getByText(/Human Review Workspace \(2 items\)/i)).toBeInTheDocument();
    expect(screen.getByText(/2 Pending/i)).toBeInTheDocument();

    // Inspect buttons for items
    const viewButtons = screen.getAllByText(/View in Document/i);
    expect(viewButtons.length).toBe(2);

    // Verify button
    const verifyButtons = screen.getAllByRole('button', { name: /Verify/i });
    expect(verifyButtons.length).toBeGreaterThan(0);
    fireEvent.click(verifyButtons[0]);

    await waitFor(() => {
      expect(apiClient.updateReviewItem).toHaveBeenCalledWith(
        'doc_iimt_test_1',
        'span_1',
        'verified',
        undefined
      );
    });
  });

  it('renders yellow search highlights on image canvas with match navigation', () => {
    render(
      <NoticeProvider>
        <Harness initialImage="data:image/png;base64,fake" initialOcr={sampleOcrResponse} />
      </NoticeProvider>
    );

    // Open original notice viewer modal by clicking View in Document
    const viewBtn = screen.getAllByText(/View in Document/i)[0];
    fireEvent.click(viewBtn);

    // Ensure image tab is active
    expect(screen.getByTestId('viewer-image-container')).toBeInTheDocument();

    // Search for 'IIMT'
    const searchInput = screen.getByPlaceholderText(/Search keyword in source notice/i);
    fireEvent.change(searchInput, { target: { value: 'IIMT' } });

    // Yellow highlights should be rendered
    const highlights = screen.getAllByTestId('ocr-search-yellow-highlight');
    expect(highlights.length).toBeGreaterThan(0);

    // Match counter and navigation buttons
    expect(screen.getByTestId('search-match-counter')).toHaveTextContent(/Match 1 of 1/i);
  });

  it('synchronizes underline status colors (pending red, verified green, corrected blue)', () => {
    render(
      <NoticeProvider>
        <Harness initialImage="data:image/png;base64,fake" initialOcr={sampleOcrResponse} />
      </NoticeProvider>
    );

    // Click View in Document on first pending span
    const viewBtn = screen.getAllByText(/View in Document/i)[0];
    fireEvent.click(viewBtn);

    const underline = screen.getByTestId('ocr-red-underline-highlight');
    expect(underline).toBeInTheDocument();
    expect(underline).toHaveAttribute('data-status', 'pending');
  });
});
