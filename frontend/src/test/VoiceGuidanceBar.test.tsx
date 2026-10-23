import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { VoiceGuidanceBar } from '../components/VoiceGuidanceBar';
import { NoticeProvider, useNotice } from '../context/NoticeContext';
import React, { useEffect } from 'react';

const TriggerSpeech: React.FC = () => {
  const { speakText } = useNotice();

  useEffect(() => {
    speakText('Last date for submission is 31st October 2026.');
  }, [speakText]);

  return <VoiceGuidanceBar />;
};

describe('VoiceGuidanceBar Component', () => {
  it('renders persistent audio guidance player and controls when speech is active', () => {
    render(
      <NoticeProvider>
        <TriggerSpeech />
      </NoticeProvider>
    );

    expect(screen.getByRole('region', { name: /Voice Guidance Read-Aloud/i })).toBeInTheDocument();
    expect(screen.getByText(/Voice Guidance Active/i)).toBeInTheDocument();
    expect(screen.getByText(/Last date for submission is 31st October 2026/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Stop speech and dismiss voice guidance/i)).toBeInTheDocument();
  });
});
