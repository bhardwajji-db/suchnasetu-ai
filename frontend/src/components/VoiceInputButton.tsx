import React, { useState, useCallback } from 'react';
import { Mic, MicOff, Loader2 } from 'lucide-react';
import { useNotice } from '../context/NoticeContext';

interface VoiceInputButtonProps {
  onTranscript: (text: string) => void;
  lang?: string;
  className?: string;
}

export const VoiceInputButton: React.FC<VoiceInputButtonProps> = ({
  onTranscript,
  lang = 'en',
  className = '',
}) => {
  const { isVoiceInputSupported } = useNotice();
  const [isListening, setIsListening] = useState(false);
  const [recognitionInstance, setRecognitionInstance] = useState<any>(null);

  const startListening = useCallback(() => {
    if (!isVoiceInputSupported) {
      alert('Voice input (Speech Recognition) is not supported by your current browser.');
      return;
    }

    try {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.lang = lang === 'hi' ? 'hi-IN' : 'en-IN';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          onTranscript(transcript);
        }
      };

      recognition.onerror = (event: any) => {
        console.warn('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.start();
      setRecognitionInstance(recognition);
    } catch (err) {
      console.error('Failed to initialize speech recognition:', err);
      setIsListening(false);
    }
  }, [isVoiceInputSupported, lang, onTranscript]);

  const stopListening = useCallback(() => {
    if (recognitionInstance) {
      recognitionInstance.stop();
      setIsListening(false);
    }
  }, [recognitionInstance]);

  if (!isVoiceInputSupported) {
    return (
      <button
        type="button"
        disabled
        title="Voice speech-to-text is not supported in this browser."
        className={`p-2 rounded-lg text-slate-600 bg-slate-900 border border-slate-800 cursor-not-allowed opacity-50 ${className}`}
        aria-label="Voice input unsupported"
      >
        <MicOff className="w-4 h-4" />
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={isListening ? stopListening : startListening}
      title={isListening ? 'Listening... click to stop' : 'Ask question by voice (Speech-to-Text)'}
      className={`p-2 rounded-lg transition flex items-center justify-center cursor-pointer ${
        isListening
          ? 'bg-rose-600 text-white animate-pulse shadow-lg shadow-rose-600/30 ring-2 ring-rose-400'
          : 'bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 border border-slate-700'
      } ${className}`}
      aria-label={isListening ? 'Stop listening' : 'Start voice input'}
    >
      {isListening ? <Loader2 className="w-4 h-4 animate-spin" /> : <Mic className="w-4 h-4" />}
    </button>
  );
};
