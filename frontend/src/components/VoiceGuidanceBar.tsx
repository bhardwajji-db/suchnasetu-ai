import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import { Volume2, Play, Pause, Square, Sparkles } from 'lucide-react';

export const VoiceGuidanceBar: React.FC = () => {
  const { speechState, pauseSpeech, resumeSpeech, stopSpeech } = useNotice();
  const { t } = useTranslation();
  const { isSpeaking, isPaused, currentText } = speechState;

  if (!isSpeaking && !isPaused) return null;

  return (
    <aside
      aria-label="Voice Guidance Read-Aloud"
      className="fixed bottom-16 md:bottom-4 left-1/2 -translate-x-1/2 z-40 w-[95%] max-w-2xl bg-white/95 border border-[#B7E7D2] shadow-2xl backdrop-blur-md rounded-2xl p-3 sm:p-3.5 flex items-center justify-between gap-3 sm:gap-4 animate-fadeIn"
      role="region"
    >
      <div className="flex items-center gap-3 min-w-0">
        <div className="p-2 rounded-xl bg-[#E8F7F0] text-[#08785D] shrink-0 border border-[#B7E7D2]">
          <Volume2 className={`w-5 h-5 ${isSpeaking && !isPaused ? 'animate-pulse' : ''}`} />
        </div>
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#08785D] flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              <span>{t('voiceGuidanceActive')}</span>
            </span>
            {isPaused && (
              <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-[#FFF4D6] text-[#92500A] border border-[#FDE68A]">
                {t('voicePause')}
              </span>
            )}
          </div>
          <p
            className="text-xs text-[#12233D] truncate font-medium mt-0.5"
            aria-live="polite"
            role="status"
          >
            {currentText || t('readingNoticeContentAloud')}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        {isPaused ? (
          <button
            onClick={resumeSpeech}
            className="p-2 rounded-lg bg-[#08785D] hover:bg-[#06664E] text-white transition shadow-xs cursor-pointer"
            aria-label={t('resumeSpeech')}
          >
            <Play className="w-4 h-4 fill-white" />
          </button>
        ) : (
          <button
            onClick={pauseSpeech}
            className="p-2 rounded-lg bg-[#F8FAFC] hover:bg-slate-100 border border-[#CBD5E1] text-[#12233D] transition cursor-pointer"
            aria-label={t('pauseSpeech')}
          >
            <Pause className="w-4 h-4" />
          </button>
        )}

        <button
          onClick={stopSpeech}
          className="p-2 rounded-lg bg-[#FEE8E7] hover:bg-[#FCD4D2] border border-[#FCA5A5] text-[#B42318] transition cursor-pointer"
          aria-label={t('stopSpeech')}
        >
          <Square className="w-4 h-4 fill-[#B42318]" />
        </button>
      </div>
    </aside>
  );
};
