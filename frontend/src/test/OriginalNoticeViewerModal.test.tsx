import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { OriginalNoticeViewerModal } from '../components/OriginalNoticeViewerModal';
import { NoticeProvider, useNotice } from '../context/NoticeContext';
import { apiClient } from '../services/apiClient';
import React, { useEffect } from 'react';

const TriggerNoticeModal: React.FC<{ initialImage?: string }> = ({ initialImage }) => {
  const { openOriginalNoticeModal, setRawNoticeText, setUploadedImage } = useNotice();

  useEffect(() => {
    setRawNoticeText('OFFICIAL MERIT SCHOLARSHIP NOTIFICATION 2026\nEligible candidates apply by 31 Oct 2026.');
    if (initialImage) {
      setUploadedImage(initialImage, new File(['dummy'], 'notice.png', { type: 'image/png' }));
    }
    openOriginalNoticeModal();
    // Run once on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return <OriginalNoticeViewerModal />;
};

describe('OriginalNoticeViewerModal Component', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    vi.spyOn(apiClient, 'getSavedNotices').mockResolvedValue([]);
    vi.spyOn(apiClient, 'getHealth').mockResolvedValue({ status: 'ok', active_provider: 'ollama' } as any);
    vi.spyOn(apiClient, 'getProviders').mockResolvedValue([]);
    vi.spyOn(apiClient, 'getSamples').mockResolvedValue([]);
  });

  it('renders original notice document viewer with raw text and copy action', () => {
    render(
      <NoticeProvider>
        <TriggerNoticeModal />
      </NoticeProvider>
    );

    expect(screen.getByText(/Original Notice Document Viewer/i)).toBeInTheDocument();
    expect(screen.getByText(/OFFICIAL MERIT SCHOLARSHIP NOTIFICATION 2026/i)).toBeInTheDocument();
    expect(screen.getByText(/Copy/i)).toBeInTheDocument();
    expect(screen.getByTestId('viewer-zoom-display')).toHaveTextContent('100%');
  });

  it('handles zoom in, zoom out, and reset zoom actions correctly', () => {
    render(
      <NoticeProvider>
        <TriggerNoticeModal />
      </NoticeProvider>
    );

    const zoomInBtn = screen.getByLabelText(/Zoom in document/i);
    const zoomOutBtn = screen.getByLabelText(/Zoom out document/i);
    const resetZoomBtn = screen.getByLabelText(/Reset zoom to default/i);
    const zoomDisplay = screen.getByTestId('viewer-zoom-display');

    expect(zoomDisplay).toHaveTextContent('100%');

    // Click Zoom In -> 125%
    fireEvent.click(zoomInBtn);
    expect(zoomDisplay).toHaveTextContent('125%');

    // Click Zoom In -> 150%
    fireEvent.click(zoomInBtn);
    expect(zoomDisplay).toHaveTextContent('150%');

    // Click Zoom Out -> 125%
    fireEvent.click(zoomOutBtn);
    expect(zoomDisplay).toHaveTextContent('125%');

    // Click Reset -> 100%
    fireEvent.click(resetZoomBtn);
    expect(zoomDisplay).toHaveTextContent('100%');
  });

  it('scales image container width when zooming in Image mode', () => {
    render(
      <NoticeProvider>
        <TriggerNoticeModal initialImage="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" />
      </NoticeProvider>
    );

    // Switch to Image mode
    const imageTabBtn = screen.getByRole('button', { name: /Image/i });
    fireEvent.click(imageTabBtn);

    const imageContainer = screen.getByTestId('viewer-image-container');
    expect(imageContainer).toHaveStyle({ width: '100%' });

    // Zoom in
    const zoomInBtn = screen.getByLabelText(/Zoom in document/i);
    fireEvent.click(zoomInBtn);

    expect(imageContainer).toHaveStyle({ width: '125%' });
  });

  it('filters text with the search input', () => {
    render(
      <NoticeProvider>
        <TriggerNoticeModal />
      </NoticeProvider>
    );

    const searchInput = screen.getByPlaceholderText(/Search keyword in source notice/i);
    fireEvent.change(searchInput, { target: { value: 'SCHOLARSHIP' } });

    expect(screen.getByText(/1 match found/i)).toBeInTheDocument();
  });
});
