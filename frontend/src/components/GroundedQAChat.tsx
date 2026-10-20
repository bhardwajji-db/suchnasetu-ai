import React, { useState } from 'react';
import { useNotice } from '../context/NoticeContext';
import {
  MessageSquare,
  Send,
  Trash2,
  Quote,
  AlertCircle,
  Sparkles,
} from 'lucide-react';

export const GroundedQAChat: React.FC = () => {
  const { rawNoticeText, followUpHistory, askQuestion, clearFollowUpHistory } = useNotice();
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
      <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-10 text-center space-y-3">
        <div className="w-12 h-12 rounded-xl bg-blue-600/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mx-auto">
          <MessageSquare className="w-6 h-6" />
        </div>
        <h3 className="text-base font-bold text-white">No Notice Loaded in Buffer</h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          Please load or upload a notice first in the Ingestion tab to start grounded interactive Q&A.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-5 space-y-5">
      <div>
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-blue-400" />
          Notice-Grounded Q&A Assistant
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Ask questions about the notice. Answers are verified against notice text; unstated items are explicitly refused.
        </p>
      </div>

      {/* Suggested Inquiries */}
      <div>
        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-2">
          💡 Suggested Inquiries
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2">
          {suggestedQuestions.map((s, idx) => (
            <button
              key={idx}
              onClick={() => handleAsk(s.text)}
              disabled={isSubmitting}
              className="text-left px-3 py-2 rounded-lg text-xs font-medium text-slate-200 bg-[#0D1528] hover:bg-[#152244] border border-[#1D2D4E] hover:border-blue-500/50 transition flex items-center justify-between"
            >
              <span>{s.label}</span>
              <Sparkles className="w-3 h-3 text-blue-400 shrink-0" />
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
        className="flex gap-2"
      >
        <input
          type="text"
          value={inputQuestion}
          onChange={(e) => setInputQuestion(e.target.value)}
          placeholder="e.g. Is there any application fee required?"
          className="flex-1 bg-[#070B14] border border-[#1D2D4E] rounded-lg px-3.5 py-2.5 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-blue-500"
        />
        <button
          type="submit"
          disabled={!inputQuestion.trim() || isSubmitting}
          className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 transition shadow-sm disabled:opacity-50"
        >
          <Send className="w-3.5 h-3.5" />
          {isSubmitting ? 'Asking...' : 'Ask Assistant'}
        </button>
      </form>

      {/* History and Conversation */}
      {followUpHistory.length > 0 && (
        <div className="pt-3 border-t border-[#1D2D4E] space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              💬 Conversation History ({followUpHistory.length})
            </h3>
            <button
              onClick={clearFollowUpHistory}
              className="flex items-center gap-1 text-[11px] font-semibold text-slate-400 hover:text-rose-400 transition"
            >
              <Trash2 className="w-3 h-3" /> Clear History
            </button>
          </div>

          <div className="space-y-3">
            {followUpHistory.map((item, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-[#0D1528] border border-[#1D2D4E] space-y-2.5 shadow-sm"
              >
                {/* User question */}
                <div className="flex items-start gap-2 text-xs font-bold text-white">
                  <span className="w-4 h-4 rounded-full bg-blue-600/30 text-blue-400 flex items-center justify-center text-[10px] shrink-0 mt-0.5">
                    Q
                  </span>
                  <span>{item.question}</span>
                </div>

                {/* Grounded Answer */}
                <div className="text-xs text-slate-200 pl-6 leading-relaxed">
                  {item.answer}
                </div>

                {/* Grounded quote or unsupported explanation */}
                {item.is_supported && item.evidence_quote ? (
                  <div className="ml-6 p-2.5 rounded-lg bg-[#070B14] border-l-2 border-blue-500 text-xs text-slate-300 font-mono italic">
                    <div className="flex items-center gap-1 text-[10px] font-sans font-bold text-blue-400 mb-0.5">
                      <Quote className="w-3 h-3" /> Supporting Quote from Notice
                    </div>
                    "{item.evidence_quote}"
                  </div>
                ) : (
                  <div className="ml-6 p-2 rounded-lg bg-amber-950/30 border border-amber-800/40 text-[11px] text-amber-300 flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
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
