import React, { useState } from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import { Volume2, VolumeX, Sparkles, AlertCircle, Loader2 } from 'lucide-react';

export const PlainLanguageSummaryView: React.FC = () => {
  const {
    summaryEn,
    summaryHi,
    localizedSummary,
    selectedLang,
    outputLang,
    readingLevel,
    changeReadingLevel,
    isTranslatingNotice,
    noticeTranslationError,
  } = useNotice();
  const { t } = useTranslation();
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [audioError, setAudioError] = useState<string | null>(null);

  const activeLang = (selectedLang || outputLang || 'en').toLowerCase().trim();
  const summary = (activeLang === 'hi')
    ? (summaryHi || localizedSummary || summaryEn)
    : (activeLang === 'en')
    ? (summaryEn || localizedSummary || summaryHi)
    : (localizedSummary || summaryEn || summaryHi);
  if (!summary) return null;

  const handleReadAloud = () => {
    if (isPlayingAudio) {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
      setIsPlayingAudio(false);
      return;
    }

    setAudioError(null);

    if (!('speechSynthesis' in window)) {
      setAudioError('Text-to-speech is not supported by your browser.');
      return;
    }

    const fullText = `About: ${summary.about}. Eligibility: ${summary.eligible}. Required actions: ${summary.actions}. Documents: ${summary.documents}. Deadline: ${summary.deadline}. Contact: ${summary.help_contact}.`;

    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(fullText);
      const speechLangMap: Record<string, string> = {
        hi: 'hi-IN',
        bn: 'bn-IN',
        ta: 'ta-IN',
        te: 'te-IN',
        mr: 'mr-IN',
        gu: 'gu-IN',
        pa: 'pa-IN',
        kn: 'kn-IN',
        ur: 'ur-PK',
        en: 'en-US',
      };
      utterance.lang = speechLangMap[activeLang] || 'en-US';
      utterance.rate = 0.95;
      utterance.onstart = () => setIsPlayingAudio(true);
      utterance.onend = () => setIsPlayingAudio(false);
      utterance.onerror = () => {
        setIsPlayingAudio(false);
        setAudioError('Speech synthesis playback encountered an error.');
      };
      window.speechSynthesis.speak(utterance);
    } catch (e: any) {
      setAudioError(`Playback error: ${e.message}`);
      setIsPlayingAudio(false);
    }
  };

  const questions = [
    { label: t('mainSubject'), value: summary.about, icon: '📄' },
    { label: t('eligibility'), value: summary.eligible, icon: '👥' },
    { label: t('actions'), value: summary.actions, icon: '⚡' },
    { label: t('requiredDocuments'), value: summary.documents, icon: '📋' },
    { label: t('deadline'), value: summary.deadline, icon: '📅' },
    { label: t('contactDetails'), value: summary.help_contact, icon: '📞' },
    { label: t('missingInfoTitle'), value: summary.missing, icon: '❓' },
  ];

  return (
    <div className="bg-white border border-[#E1E7EE] rounded-xl p-6 space-y-5 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#E1E7EE]">
        <div>
          <h2 className="text-base font-bold text-[#12233D] flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[#08785D]" />
            <span>{t('summaryTitle')}</span>
            {isTranslatingNotice && (
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200 animate-pulse ml-2">
                <Loader2 className="w-3 h-3 animate-spin" />
                Translating notice...
              </span>
            )}
          </h2>
          <p className="text-xs text-[#526176] mt-0.5">
            {t('summarySubtitle')}
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          {/* Reading Level Selector */}
          <div className="flex items-center gap-1 bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg p-0.5">
            <span className="text-[10px] font-semibold text-[#68778B] px-1.5 uppercase">
              {t('readingLevel') || 'Level'}:
            </span>
            <button
              type="button"
              onClick={() => changeReadingLevel('simple')}
              className={`px-2 py-0.5 rounded-md text-[11px] font-semibold transition cursor-pointer ${
                readingLevel === 'simple'
                  ? 'bg-[#08785D] text-white shadow-xs'
                  : 'text-[#526176] hover:text-[#12233D]'
              }`}
            >
              {t('simpleLevel') || 'Simple'}
            </button>
            <button
              type="button"
              onClick={() => changeReadingLevel('standard')}
              className={`px-2 py-0.5 rounded-md text-[11px] font-semibold transition cursor-pointer ${
                readingLevel === 'standard'
                  ? 'bg-[#08785D] text-white shadow-xs'
                  : 'text-[#526176] hover:text-[#12233D]'
              }`}
            >
              {t('standardLevel') || 'Standard'}
            </button>
            <button
              type="button"
              onClick={() => changeReadingLevel('detailed')}
              className={`px-2 py-0.5 rounded-md text-[11px] font-semibold transition cursor-pointer ${
                readingLevel === 'detailed'
                  ? 'bg-[#08785D] text-white shadow-xs'
                  : 'text-[#526176] hover:text-[#12233D]'
              }`}
            >
              {t('detailedLevel') || 'Detailed'}
            </button>
          </div>

          {/* Audio Listen Aloud Button */}
          <button
            type="button"
            onClick={handleReadAloud}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition shadow-xs cursor-pointer ${
              isPlayingAudio
                ? 'bg-[#B42318] text-white hover:bg-[#991B1B]'
                : 'bg-[#E8F7F0] text-[#08785D] hover:bg-[#D4EFE3] border border-[#B7E7D2]'
            }`}
            title="Read summary aloud"
            aria-label="Play plain language summary audio"
          >
            {isPlayingAudio ? (
              <>
                <VolumeX className="w-3.5 h-3.5" />
                <span>{t('stopAudio')}</span>
              </>
            ) : (
              <>
                <Volume2 className="w-3.5 h-3.5" />
                <span>{t('listenAloud')}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {noticeTranslationError && (
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-amber-600" />
          <span>{noticeTranslationError}</span>
        </div>
      )}

      {audioError && (
        <div className="p-3 rounded-xl bg-[#FFF4D6] border border-[#FDE68A] text-xs text-[#92500A] flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-[#92500A] shrink-0" />
          <span>{audioError}</span>
        </div>
      )}

      {/* 7 Questions Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
        {questions.map((q, idx) => (
          <div
            key={idx}
            className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] hover:border-[#B7E7D2] transition-all space-y-1.5 shadow-xs"
          >
            <div className="flex items-center gap-2 text-xs font-bold text-[#12233D]">
              <span className="text-sm">{q.icon}</span>
              <span>{q.label}</span>
            </div>
            <div className="text-xs text-[#526176] leading-relaxed pl-6">
              {q.value || 'Not specified in this notice.'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
