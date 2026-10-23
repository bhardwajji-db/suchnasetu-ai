import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { VoiceInputButton } from '../components/VoiceInputButton';
import { NoticeProvider } from '../context/NoticeContext';

describe('VoiceInputButton Component', () => {
  it('renders microphone button with accessibility title and label', () => {
    const handleTranscript = vi.fn();

    render(
      <NoticeProvider>
        <VoiceInputButton onTranscript={handleTranscript} lang="en" />
      </NoticeProvider>
    );

    const btn = screen.getByRole('button');
    expect(btn).toBeInTheDocument();
    expect(btn).toHaveAttribute('aria-label');
  });
});
