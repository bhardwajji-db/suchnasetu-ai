import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { OriginalNoticeViewerModal } from '../components/OriginalNoticeViewerModal';
import { NoticeProvider, useNotice } from '../context/NoticeContext';
import React, { useEffect } from 'react';

const TriggerNoticeModal: React.FC = () => {
  const { openOriginalNoticeModal, setRawNoticeText } = useNotice();

  useEffect(() => {
    setRawNoticeText('OFFICIAL MERIT SCHOLARSHIP NOTIFICATION 2026\nEligible candidates apply by 31 Oct 2026.');
    openOriginalNoticeModal();
  }, [openOriginalNoticeModal, setRawNoticeText]);

  return <OriginalNoticeViewerModal />;
};

describe('OriginalNoticeViewerModal Component', () => {
  it('renders original notice document viewer with raw text and copy action', () => {
    render(
      <NoticeProvider>
        <TriggerNoticeModal />
      </NoticeProvider>
    );

    expect(screen.getByText(/Original Notice Document Viewer/i)).toBeInTheDocument();
    expect(screen.getByText(/OFFICIAL MERIT SCHOLARSHIP NOTIFICATION 2026/i)).toBeInTheDocument();
    expect(screen.getByText(/Copy/i)).toBeInTheDocument();
  });
});
