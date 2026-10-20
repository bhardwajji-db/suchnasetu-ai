import React, { useState } from 'react';
import { useNotice } from '../context/NoticeContext';
import { apiClient } from '../services/apiClient';
import { Volume2, VolumeX, Sparkles, AlertCircle } from 'lucide-react';

export const PlainLanguageSummaryView: React.FC = () => {
  const { summaryEn, summaryHi, selectedLang, readingLevel, changeReadingLevel } = useNotice();
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [audioError, setAudioError] = useState<string | null>(null);

  const summary = selectedLang === 'hi' ? summaryHi : summaryEn;
  if (!summary) return null;

  const handleReadAloud = async () => {
    if (isPlayingAudio) {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
      setIsPlayingAudio(false);
      return;
    }

    setAudioError(null);
    setIsPlayingAudio(true);

    const fullText = `About: ${summary.about}. Eligibility: ${summary.eligible}. Required actions: ${summary.actions}. Documents: ${summary.documents}. Deadline: ${summary.deadline}. Contact: ${summary.help_contact}.`;

    try {
      const audioBlob = await apiClient.getTTSAudio(fullText, selectedLang);
      if (audioBlob) {
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.onended = () => setIsPlayingAudio(false);
        audio.onerror = () => {
          fallbackBrowserSpeech(fullText);
        };
        await audio.play();
      } else {
        fallbackBrowserSpeech(fullText);
      }
    } catch {
      fallbackBrowserSpeech(fullText);
    }
  };

  const fallbackBrowserSpeech = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = selectedLang === 'hi' ? 'hi-IN' : 'en-US';
      utterance.onend = () => setIsPlayingAudio(false);
      utterance.onerror = () => setIsPlayingAudio(false);
      window.speechSynthesis.speak(utterance);
    } else {
      setAudioError('Text-to-speech is not supported by your browser.');
      setIsPlayingAudio(false);
    }
  };

  const questions = [
    { label: selectedLang === 'hi' ? 'यह सूचना किस बारे में है?' : 'What is this notice about?', value: summary.about, icon: '📄' },
    { label: selectedLang === 'hi' ? 'कौन पात्र है?' : 'Who is eligible to participate / apply?', value: summary.eligible, icon: '👥' },
    { label: selectedLang === 'hi' ? 'आपको क्या करना होगा?' : 'What action must the reader take?', value: summary.actions, icon: '⚡' },
    { label: selectedLang === 'hi' ? 'कौन से दस्तावेज़ आवश्यक हैं?' : 'What documents are required?', value: summary.documents, icon: '📋' },
    { label: selectedLang === 'hi' ? 'अंतिम तिथि क्या है?' : 'What is the final submission deadline?', value: summary.deadline, icon: '📅' },
    { label: selectedLang === 'hi' ? 'सहायता या संपर्क कहाँ करें?' : 'Where can the reader get official help?', value: summary.help_contact, icon: '📞' },
    { label: selectedLang === 'hi' ? 'कौन सी जानकारी उपलब्ध नहीं है?' : 'What critical information is missing?', value: summary.missing, icon: '❓' },
  ];

  return (
    <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-5 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-[#1D2D4E]">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-400" />
            {selectedLang === 'hi' ? 'सरल भाषा में सारांश' : 'Plain-Language Accessible Summary'}
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            {selectedLang === 'hi'
              ? 'जटिल नोटिस को 7 मुख्य प्रश्नों के स्पष्ट उत्तरों में बदला गया है।'
              : 'Answers to the 7 core questions, calibrated for accessible reading.'}
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Reading Level Selector */}
          <div className="hidden sm:flex items-center gap-1 bg-[#111A33] border border-[#1D2D4E] rounded-lg p-0.5">
            <span className="text-[10px] font-semibold text-slate-400 px-2 uppercase">
              Level:
            </span>
            <button
              type="button"
              onClick={() => changeReadingLevel('simple')}
              className={`px-2 py-0.5 rounded text-[11px] font-semibold transition ${
                readingLevel === 'simple'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Simple
            </button>
            <button
              type="button"
              onClick={() => changeReadingLevel('standard')}
              className={`px-2 py-0.5 rounded text-[11px] font-semibold transition ${
                readingLevel === 'standard'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Standard
            </button>
            <button
              type="button"
              onClick={() => changeReadingLevel('detailed')}
              className={`px-2 py-0.5 rounded text-[11px] font-semibold transition ${
                readingLevel === 'detailed'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Detailed
            </button>
          </div>

          <button
            onClick={handleReadAloud}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition shadow-sm ${
              isPlayingAudio
                ? 'bg-rose-600 hover:bg-rose-500 text-white'
                : 'bg-blue-600 hover:bg-blue-500 text-white'
            }`}
          >
            {isPlayingAudio ? (
              <>
                <VolumeX className="w-3.5 h-3.5" /> Stop Reading
              </>
            ) : (
              <>
                <Volume2 className="w-3.5 h-3.5" /> Listen (Read Aloud)
              </>
            )}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
        {questions.map((q, idx) => (
          <div
            key={idx}
            className="p-3.5 rounded-lg bg-[#070B14]/80 border border-[#1D2D4E]/80 space-y-1.5 hover:border-blue-500/40 transition"
          >
            <div className="text-xs font-bold text-blue-400 flex items-center gap-1.5">
              <span>{q.icon}</span>
              <span>{q.label}</span>
            </div>
            <div className="text-sm font-medium text-slate-200 leading-relaxed">
              {q.value}
            </div>
          </div>
        ))}
      </div>

      {audioError && (
        <div className="p-2.5 rounded-lg bg-amber-950/40 border border-amber-800/40 text-xs text-amber-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
          <span>{audioError}</span>
        </div>
      )}
    </div>
  );
};
