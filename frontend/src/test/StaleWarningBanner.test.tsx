import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { StaleWarningBanner } from '../components/StaleWarningBanner';
import { NoticeProvider } from '../context/NoticeContext';
import * as NoticeContextModule from '../context/NoticeContext';

describe('StaleWarningBanner Component', () => {
  it('renders warning banner when isNoticeStale is true', () => {
    vi.spyOn(NoticeContextModule, 'useNotice').mockReturnValue({
      isNoticeStale: true,
      runAnalysis: vi.fn(),
      isAnalyzing: false,
    } as any);

    render(
      <NoticeProvider>
        <StaleWarningBanner />
      </NoticeProvider>
    );

    expect(screen.getByText(/Notice Buffer Modified:/i)).toBeInTheDocument();
    expect(screen.getByText(/Re-Analyze Notice/i)).toBeInTheDocument();
  });

  it('renders nothing when isNoticeStale is false', () => {
    vi.spyOn(NoticeContextModule, 'useNotice').mockReturnValue({
      isNoticeStale: false,
      runAnalysis: vi.fn(),
      isAnalyzing: false,
    } as any);

    const { container } = render(
      <NoticeProvider>
        <StaleWarningBanner />
      </NoticeProvider>
    );

    expect(container).toBeEmptyDOMElement();
  });
});
