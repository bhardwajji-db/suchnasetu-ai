import React, { useState, useEffect } from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import { FileText, Image as ImageIcon, Copy, Check, X, Search, ZoomIn, ZoomOut } from 'lucide-react';

export const OriginalNoticeViewerModal: React.FC = () => {
  const { isOriginalNoticeOpen, closeOriginalNoticeModal, rawNoticeText, uploadedImage } = useNotice();
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<'text' | 'image'>(uploadedImage ? 'image' : 'text');
  const [copied, setCopied] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [fontSize, setFontSize] = useState<number>(14);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOriginalNoticeOpen) {
        closeOriginalNoticeModal();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOriginalNoticeOpen, closeOriginalNoticeModal]);

  if (!isOriginalNoticeOpen) return null;

  const handleCopy = () => {
    if (!rawNoticeText) return;
    navigator.clipboard.writeText(rawNoticeText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lines = rawNoticeText ? rawNoticeText.split('\n') : [];
  const lineCount = lines.length;
  const wordCount = rawNoticeText ? rawNoticeText.trim().split(/\s+/).filter(Boolean).length : 0;
  const charCount = rawNoticeText ? rawNoticeText.length : 0;

  const matchCount = searchQuery.trim() && rawNoticeText
    ? (rawNoticeText.match(new RegExp(searchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')) || []).length
    : 0;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="original-notice-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-in fade-in duration-200"
    >
      <div className="bg-white border border-[#E1E7EE] rounded-2xl w-full max-w-4xl max-h-[88vh] shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#E1E7EE] bg-[#F8FAFC]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[#E8F7F0] border border-[#B7E7D2] text-[#08785D] flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <h2 id="original-notice-title" className="text-sm font-bold text-[#12233D] flex items-center gap-2">
                {t('originalNoticeModalTitle') || 'Original Notice Document Viewer'}
                {uploadedImage && (
                  <span className="text-[10px] font-mono uppercase bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2] px-1.5 py-0.5 rounded font-semibold">
                    OCR Scanned
                  </span>
                )}
              </h2>
              <p className="text-[11px] text-[#526176]">
                Ground-truth source reference • {wordCount} words • {charCount} chars • {lineCount} lines
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {uploadedImage && (
              <div className="flex items-center rounded-lg bg-slate-100 border border-[#E1E7EE] p-0.5">
                <button
                  type="button"
                  onClick={() => setActiveTab('text')}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold transition cursor-pointer ${
                    activeTab === 'text' ? 'bg-[#08785D] text-white' : 'text-[#526176] hover:text-[#12233D]'
                  }`}
                >
                  <FileText className="w-3 h-3" />
                  Text
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('image')}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold transition cursor-pointer ${
                    activeTab === 'image' ? 'bg-[#08785D] text-white' : 'text-[#526176] hover:text-[#12233D]'
                  }`}
                >
                  <ImageIcon className="w-3 h-3" />
                  Image
                </button>
              </div>
            )}

            {/* Font size adjustments */}
            <div className="hidden sm:flex items-center gap-1 bg-slate-100 border border-[#E1E7EE] rounded-lg p-0.5">
              <button
                type="button"
                onClick={() => setFontSize(Math.max(12, fontSize - 1))}
                className="p-1 rounded text-[#526176] hover:text-[#12233D] hover:bg-white transition cursor-pointer"
                title="Decrease font size"
                aria-label="Decrease font size"
              >
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
              <span className="text-[10px] font-mono px-1 text-[#68778B]">{fontSize}px</span>
              <button
                type="button"
                onClick={() => setFontSize(Math.min(20, fontSize + 1))}
                className="p-1 rounded text-[#526176] hover:text-[#12233D] hover:bg-white transition cursor-pointer"
                title="Increase font size"
                aria-label="Increase font size"
              >
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
            </div>

            <button
              type="button"
              onClick={handleCopy}
              disabled={!rawNoticeText}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold text-[#12233D] hover:text-[#08785D] bg-white border border-[#E1E7EE] hover:border-[#B7E7D2] transition cursor-pointer"
              title="Copy original notice text"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-[#08785D]" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>

            <button
              type="button"
              onClick={closeOriginalNoticeModal}
              className="text-[#68778B] hover:text-[#12233D] p-1.5 rounded-lg hover:bg-slate-100 transition cursor-pointer"
              aria-label="Close original notice modal"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Toolbar: Search inside Notice */}
        <div className="flex items-center justify-between px-6 py-2.5 bg-white border-b border-[#E1E7EE] gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="w-3.5 h-3.5 text-[#68778B] absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search keyword in source notice..."
              className="w-full bg-[#F8FAFC] border border-[#E1E7EE] focus:border-[#08785D] focus:outline-hidden rounded-lg pl-8 pr-3 py-1 text-xs text-[#12233D] placeholder-[#68778B]"
            />
          </div>
          {searchQuery.trim() && (
            <span className="text-xs font-medium text-[#526176]">
              {matchCount} {matchCount === 1 ? 'match' : 'matches'} found
            </span>
          )}
        </div>

        {/* Body Viewer */}
        <div className="flex-1 overflow-y-auto p-6 bg-[#F8FAFC]">
          {activeTab === 'image' && uploadedImage ? (
            <div className="flex items-center justify-center p-4 bg-white rounded-xl border border-[#E1E7EE]">
              <img
                src={uploadedImage}
                alt="Original scanned notice preview"
                className="max-w-full max-h-[60vh] object-contain rounded-lg shadow-xs"
              />
            </div>
          ) : (
            <div
              className="bg-white border border-[#E1E7EE] rounded-xl p-5 shadow-xs font-mono leading-relaxed select-text"
              style={{ fontSize: `${fontSize}px` }}
            >
              {lines.map((line, index) => {
                const isMatch = searchQuery.trim() && line.toLowerCase().includes(searchQuery.toLowerCase());
                return (
                  <div
                    key={index}
                    className={`flex items-start gap-4 py-0.5 rounded px-1.5 transition ${
                      isMatch ? 'bg-[#FFF4D6] text-[#92500A] font-semibold' : 'text-[#12233D]'
                    }`}
                  >
                    <span className="text-[11px] text-[#CBD5E1] select-none w-8 text-right shrink-0 pt-0.5">
                      {index + 1}
                    </span>
                    <span className="flex-1 whitespace-pre-wrap break-words">{line || '\u00A0'}</span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
