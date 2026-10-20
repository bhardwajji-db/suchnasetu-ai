import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { GroundedQAChat } from '../components/GroundedQAChat';
import { NoticeProvider } from '../context/NoticeContext';
import * as NoticeContextModule from '../context/NoticeContext';

describe('GroundedQAChat Component', () => {
  it('renders suggested questions and input box when notice text is present', () => {
    vi.spyOn(NoticeContextModule, 'useNotice').mockReturnValue({
      rawNoticeText: 'Valid official notice text.',
      followUpHistory: [
        {
          question: 'What is the deadline?',
          answer: 'The deadline is 30 October 2026.',
          is_supported: true,
          evidence_quote: 'Deadline is 30 October 2026.',
        },
      ],
      askQuestion: vi.fn(),
      clearFollowUpHistory: vi.fn(),
    } as any);

    render(
      <NoticeProvider>
        <GroundedQAChat />
      </NoticeProvider>
    );

    expect(screen.getByText(/Notice-Grounded Q&A Assistant/i)).toBeInTheDocument();
    expect(screen.getByText('📋 Required Documents?')).toBeInTheDocument();
    expect(screen.getByText('What is the deadline?')).toBeInTheDocument();
    expect(screen.getByText('The deadline is 30 October 2026.')).toBeInTheDocument();
    expect(screen.getByText(/"Deadline is 30 October 2026."/i)).toBeInTheDocument();
  });

  it('renders empty prompt when no notice text is loaded', () => {
    vi.spyOn(NoticeContextModule, 'useNotice').mockReturnValue({
      rawNoticeText: '',
      followUpHistory: [],
      askQuestion: vi.fn(),
      clearFollowUpHistory: vi.fn(),
    } as any);

    render(
      <NoticeProvider>
        <GroundedQAChat />
      </NoticeProvider>
    );

    expect(screen.getByText(/No Notice Loaded in Buffer/i)).toBeInTheDocument();
  });
});
