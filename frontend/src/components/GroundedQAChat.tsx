import React, { useState } from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import { VoiceInputButton } from './VoiceInputButton';
import {
  MessageSquare,
  Send,
  Trash2,
  Quote,
  AlertCircle,
  Sparkles,
  Volume2,
  Search,
} from 'lucide-react';

export const GroundedQAChat: React.FC = () => {
  const {
    rawNoticeText,
    followUpHistory,
    askQuestion,
    clearFollowUpHistory,
    speakText,
    openEvidenceInspector,
    selectedLang,
  } = useNotice();
  const { t } = useTranslation();

  const [inputQuestion, setInputQuestion] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const suggestedQuestions = [
    { label: '📋 Required Documents?', text: 'What documents are needed to apply?' },
    { label: '👥 Eligibility Criteria?', text: 'Who is eligible for this opportunity?' },
    { label: '⏳ Late Submissions?', text: 'Can I submit the application late?' },
    { label: '📅 Exact Deadline?', text: 'What is the final deadline to submit?' },
  ];

  const handleAsk = async (q: string) => {
    const query = q.trim();
    if (!query) return;
    setIsSubmitting(true);
    try {
      await askQuestion(query);
      setInputQuestion('');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!rawNoticeText.trim()) {
    return (
      <div className="bg-white border border-[#E1E7EE] rounded-xl p-10 text-center space-y-3 shadow-xs">
        <div className="w-12 h-12 rounded-xl bg-[#E8F7F0] border border-[#B7E7D2] text-[#08785D] flex items-center justify-center mx-auto">
          <MessageSquare className="w-6 h-6" />
        </div>
        <h3 className="text-base font-bold text-[#12233D]">{t('noNoticeLoadedTitle')}</h3>
        <p className="text-xs text-[#526176] max-w-md mx-auto">
          {t('noNoticeLoadedDesc')}
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-[#E1E7EE] rounded-xl p-6 space-y-5 shadow-xs">
      <div>
        <h2 className="text-base font-bold text-[#12233D] flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-[#08785D]" />
          {t('qaChatTitle')}
        </h2>
        <p className="text-xs text-[#526176] mt-0.5">
          {t('qaChatSubtitle')}
        </p>
      </div>

      {/* Suggested Inquiries */}
      <div>
        <span className="text-[11px] font-bold uppercase tracking-wider text-[#68778B] block mb-2">
          💡 {t('suggestedInquiries')}
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2">
          {suggestedQuestions.map((s, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleAsk(s.text)}
              disabled={isSubmitting}
              className="text-left px-3 py-2.5 rounded-xl text-xs font-medium text-[#12233D] bg-[#F8FAFC] hover:bg-[#E8F7F0] border border-[#E1E7EE] hover:border-[#B7E7D2] transition flex items-center justify-between cursor-pointer"
            >
              <span>{s.label}</span>
              <Sparkles className="w-3.5 h-3.5 text-[#08785D] shrink-0" />
            </button>
          ))}
        </div>
      </div>

      {/* Question Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleAsk(inputQuestion);
        }}
        className="flex items-center gap-2"
      >
        <input
          type="text"
          value={inputQuestion}
          onChange={(e) => setInputQuestion(e.target.value)}
          aria-label="Ask a question about the notice"
          placeholder={t('qaPlaceholder')}
          className="flex-1 bg-[#F8FAFC] border border-[#CBD5E1] rounded-xl px-4 py-2.5 text-xs text-[#12233D] placeholder-[#68778B] focus:outline-hidden focus:border-[#08785D] focus:ring-1 focus:ring-[#08785D]"
        />

        <VoiceInputButton
          onTranscript={(txt) => setInputQuestion(txt)}
          lang={selectedLang}
        />

        <button
          type="submit"
          disabled={!inputQuestion.trim() || isSubmitting}
          className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-bold text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs disabled:opacity-50 cursor-pointer"
        >
          <Send className="w-3.5 h-3.5" />
          {isSubmitting ? t('askingAssistant') : t('askAssistantBtn')}
        </button>
      </form>

      {/* History and Conversation */}
      {followUpHistory.length > 0 && (
        <div className="pt-3 border-t border-[#E1E7EE] space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#12233D]">
              💬 {t('conversationHistory')} ({followUpHistory.length})
            </h3>
            <button
              type="button"
              onClick={clearFollowUpHistory}
              className="flex items-center gap-1 text-[11px] font-semibold text-[#68778B] hover:text-[#B42318] transition cursor-pointer"
            >
              <Trash2 className="w-3 h-3" /> {t('qaClearHistory')}
            </button>
          </div>

          <div className="space-y-3">
            {followUpHistory.map((item, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-2.5 shadow-xs"
              >
                {/* User question */}
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-start gap-2 text-xs font-bold text-[#12233D]">
                    <span className="w-5 h-5 rounded-full bg-[#E8F7F0] text-[#08785D] flex items-center justify-center text-[10px] shrink-0 mt-0.5 font-bold">
                      Q
                    </span>
                    <span>{item.question}</span>
                  </div>
                  {speakText && (
                    <button
                      type="button"
                      onClick={() => speakText(item.answer, selectedLang)}
                      className="p-1 rounded-md text-[#68778B] hover:text-[#08785D] hover:bg-white transition cursor-pointer shrink-0"
                      title={t('voicePlay')}
                    >
                      <Volume2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                {/* Grounded Answer */}
                <div className="text-xs text-[#12233D] pl-7 leading-relaxed">
                  {item.answer}
                </div>

                {/* Grounded quote or unsupported explanation */}
                {item.is_supported && item.evidence_quote ? (
                  <div className="ml-7 p-3 rounded-lg bg-white border-l-3 border-[#08785D] text-xs text-[#526176] font-mono italic flex items-center justify-between gap-2 shadow-xs">
                    <div>
                      <div className="flex items-center gap-1 text-[10px] font-sans font-bold text-[#08785D] mb-0.5">
                        <Quote className="w-3 h-3" /> {t('groundedEvidenceQuote')}
                      </div>
                      "{item.evidence_quote}"
                    </div>
                    {openEvidenceInspector && (
                      <button
                        type="button"
                        onClick={() =>
                          openEvidenceInspector({
                            excerpt: item.evidence_quote!,
                            claim: item.question,
                            docTitle: 'Active Notice',
                          })
                        }
                        className="inline-flex items-center gap-1 text-[10px] font-semibold text-[#08785D] hover:underline transition cursor-pointer shrink-0"
                      >
                        <Search className="w-3 h-3" />
                        <span>{t('viewEvidence')}</span>
                      </button>
                    )}
                  </div>
                ) : (
                  <div className="ml-7 p-2.5 rounded-lg bg-[#FFF4D6] border border-[#FDE68A] text-[11px] text-[#92500A] flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5 text-[#92500A] shrink-0" />
                    <span>
                      {item.unsupported_message || 'This detail is unstated in the notice text.'}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
