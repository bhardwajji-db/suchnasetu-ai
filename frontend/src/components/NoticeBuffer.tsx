import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import { Sparkles, Trash2, FileText } from 'lucide-react';

export const NoticeBuffer: React.FC = () => {
  const { rawNoticeText, setRawNoticeText, loadSampleFixture, clearBuffer, samples } = useNotice();
  const { t } = useTranslation();

  const charCount = rawNoticeText.length;
  const lineCount = rawNoticeText ? rawNoticeText.split('\n').length : 0;
  const isPopulated = charCount > 0;

  return (
    <div className="bg-white border border-[#E1E7EE] rounded-xl p-5 flex flex-col justify-between h-full space-y-4 shadow-xs">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-[#12233D] flex items-center gap-2">
          <FileText className="w-4 h-4 text-[#08785D]" />
          {t('bufferTitle') || 'Notice Ground-Truth Buffer'}
        </span>
        <span
          className={`text-[11px] font-mono font-semibold px-2.5 py-0.5 rounded-md ${
            isPopulated
              ? 'bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]'
              : 'bg-slate-100 text-[#68778B] border border-slate-200'
          }`}
        >
          {charCount} chars • {lineCount} lines
        </span>
      </div>

      <textarea
        value={rawNoticeText}
        onChange={(e) => setRawNoticeText(e.target.value)}
        aria-label="Official notice text content"
        rows={9}
        placeholder={t('bufferPlaceholder') || 'Paste official notice text here, or upload a document/scanned image on the left. You can also select a synthetic demo notice below.'}
        className="w-full bg-[#F8FAFC] border border-[#CBD5E1] focus:border-[#08785D] focus:ring-1 focus:ring-[#08785D] focus:outline-hidden rounded-xl p-3.5 text-sm text-[#12233D] placeholder-[#68778B] font-mono resize-y leading-relaxed"
      />

      {/* Quick Demo Selectors */}
      <div className="space-y-2.5 pt-2 border-t border-[#E1E7EE]">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-bold text-[#526176] uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-[#08785D]" /> {t('sampleNotices') || 'Sample Notice Presets'}:
          </span>
          <button
            type="button"
            onClick={clearBuffer}
            disabled={!rawNoticeText}
            className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold text-[#B42318] hover:bg-[#FEE8E7] border border-transparent hover:border-[#FCA5A5] transition disabled:opacity-40 cursor-pointer"
          >
            <Trash2 className="w-3.5 h-3.5" />
            {t('clearBuffer') || 'Clear Buffer'}
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Default load demo button */}
          <button
            type="button"
            onClick={() => loadSampleFixture('synthetic_scholarship_notice.txt')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5 text-white" />
            Load Demo Notice
          </button>

          <button
            type="button"
            onClick={() => loadSampleFixture('demo_missing_compliance.txt')}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium text-[#12233D] bg-[#F8FAFC] hover:bg-[#E8F7F0] hover:text-[#08785D] border border-[#E1E7EE] transition cursor-pointer"
          >
            Compliance Notice
          </button>

          <button
            type="button"
            onClick={() => loadSampleFixture('demo_outstanding_dues.txt')}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium text-[#12233D] bg-[#F8FAFC] hover:bg-[#E8F7F0] hover:text-[#08785D] border border-[#E1E7EE] transition cursor-pointer"
          >
            Dues Circular
          </button>

          <button
            type="button"
            onClick={() => loadSampleFixture('demo_response_hearing.txt')}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium text-[#12233D] bg-[#F8FAFC] hover:bg-[#E8F7F0] hover:text-[#08785D] border border-[#E1E7EE] transition cursor-pointer"
          >
            Hearing Notice
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
              className="bg-white text-[#12233D] text-xs font-medium border border-[#CBD5E1] rounded-lg px-2.5 py-1.5 focus:border-[#08785D] focus:outline-hidden cursor-pointer"
            >
              <option value="" disabled>More Samples...</option>
              {samples.map((s) => (
                <option key={s.id || s.filename} value={s.filename || s.id}>
                  {s.title || s.filename}
                </option>
              ))}
            </select>
          )}
        </div>
      </div>
    </div>
  );
};
