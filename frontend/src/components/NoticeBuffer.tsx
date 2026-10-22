import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { Sparkles, Trash2 } from 'lucide-react';

export const NoticeBuffer: React.FC = () => {
  const { rawNoticeText, setRawNoticeText, loadSampleFixture, clearBuffer, samples } = useNotice();

  const charCount = rawNoticeText.length;
  const lineCount = rawNoticeText ? rawNoticeText.split('\n').length : 0;
  const isPopulated = charCount > 0;

  return (
    <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-4 flex flex-col justify-between h-full space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
          ✍️ Notice Ground-Truth Buffer
        </span>
        <span
          className={`text-[11px] font-mono font-semibold px-2 py-0.5 rounded ${
            isPopulated
              ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800'
              : 'bg-slate-800 text-slate-400 border border-slate-700'
          }`}
        >
          {charCount} chars • {lineCount} lines
        </span>
      </div>

      <textarea
        value={rawNoticeText}
        onChange={(e) => setRawNoticeText(e.target.value)}
        aria-label="Official notice text content"
        rows={8}
        placeholder="Paste official notice text here, or upload a document/scanned image on the left. You can also select a synthetic demo notice below."
        className="w-full bg-[#070B14] border border-[#1D2D4E] rounded-lg p-3 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-blue-500 font-sans resize-y leading-relaxed"
      />

      {/* Quick Demo Selectors */}
      <div className="space-y-2 pt-1 border-t border-[#1D2D4E]">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-amber-400" /> Quick-Load Demo Notices:
          </span>
          <button
            onClick={clearBuffer}
            disabled={!rawNoticeText}
            className="flex items-center gap-1 px-2 py-1 rounded text-xs font-semibold text-slate-400 hover:text-rose-400 hover:bg-rose-950/20 border border-slate-800 transition disabled:opacity-40"
          >
            <Trash2 className="w-3 h-3" />
            Clear Buffer
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-1.5">
          <button
            type="button"
            onClick={() => loadSampleFixture('demo_missing_compliance.txt')}
            className="flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-bold text-white bg-blue-700 hover:bg-blue-600 transition shadow-sm"
          >
            📋 Demo 1: Compliance
          </button>
          <button
            type="button"
            onClick={() => loadSampleFixture('demo_outstanding_dues.txt')}
            className="flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-bold text-white bg-indigo-700 hover:bg-indigo-600 transition shadow-sm"
          >
            💰 Demo 2: Outstanding Dues
          </button>
          <button
            type="button"
            onClick={() => loadSampleFixture('demo_response_hearing.txt')}
            className="flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-bold text-white bg-purple-700 hover:bg-purple-600 transition shadow-sm"
          >
            ⚖️ Demo 3: Hearing
          </button>

          <button
            type="button"
            onClick={() => loadSampleFixture('synthetic_scholarship_notice.txt')}
            className="flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-semibold text-slate-200 hover:text-white bg-[#111A33] hover:bg-[#1D2D4E] border border-[#1D2D4E] transition"
          >
            🎯 Scholarship Demo
          </button>

          {samples.length > 0 && (
            <select
              aria-label="More synthetic demo notices"
              onChange={(e) => {
                if (e.target.value) {
                  loadSampleFixture(e.target.value);
                  e.target.value = '';
                }
              }}
              defaultValue=""
              className="bg-[#111A33] text-slate-300 text-[11px] border border-[#1D2D4E] rounded-md px-2 py-1 focus:outline-none cursor-pointer"
            >
              <option value="" disabled>More Samples...</option>
              {samples.map((s) => (
                <option key={s.id} value={s.id}>{s.title}</option>
              ))}
            </select>
          )}
        </div>
      </div>
    </div>
  );
};
