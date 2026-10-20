import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { Sparkles, Trash2 } from 'lucide-react';

export const NoticeBuffer: React.FC = () => {
  const { rawNoticeText, setRawNoticeText, loadSampleFixture, clearBuffer } = useNotice();

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
        rows={8}
        placeholder="Paste official notice text here, or upload a document/scanned image on the left. You can also click 'Load Demo Notice' below."
        className="w-full bg-[#070B14] border border-[#1D2D4E] rounded-lg p-3 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-blue-500 font-sans resize-y leading-relaxed"
      />

      <div className="flex items-center justify-between gap-2 pt-1 border-t border-[#1D2D4E]">
        <button
          onClick={() => loadSampleFixture('synthetic_scholarship_notice.txt')}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-gradient-to-r from-blue-700 to-indigo-700 hover:from-blue-600 hover:to-indigo-600 transition shadow-sm"
        >
          <Sparkles className="w-3.5 h-3.5 text-blue-300" />
          Load Demo Notice (TEST-SCH)
        </button>

        <button
          onClick={clearBuffer}
          disabled={!rawNoticeText}
          className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-rose-400 hover:bg-rose-950/20 border border-slate-800 transition disabled:opacity-40"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Clear Buffer
        </button>
      </div>
    </div>
  );
};
