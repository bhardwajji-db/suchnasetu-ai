import React, { useState } from 'react';
import { useNotice } from '../context/NoticeContext';
import { FileText, Image as ImageIcon, Copy, Check, X, Search } from 'lucide-react';

export const OriginalNoticeViewerModal: React.FC = () => {
  const { isOriginalNoticeOpen, closeOriginalNoticeModal, rawNoticeText, uploadedImage, ocrResult } = useNotice();
  const [activeTab, setActiveTab] = useState<'text' | 'image'>(uploadedImage ? 'image' : 'text');
  const [copied, setCopied] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');

  if (!isOriginalNoticeOpen) return null;

  const handleCopy = () => {
    if (!rawNoticeText) return;
    navigator.clipboard.writeText(rawNoticeText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lineCount = rawNoticeText ? rawNoticeText.split('\n').length : 0;
  const wordCount = rawNoticeText ? rawNoticeText.trim().split(/\s+/).filter(Boolean).length : 0;
  const charCount = rawNoticeText ? rawNoticeText.length : 0;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="original-notice-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200"
    >
      <div className="bg-[#0B132B] border border-[#1D2D4E] rounded-2xl w-full max-w-4xl max-h-[85vh] shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#1D2D4E] bg-[#070B14]/70">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <h2 id="original-notice-title" className="text-sm font-bold text-white flex items-center gap-2">
                Original Notice Document Viewer
                {uploadedImage && (
                  <span className="text-[10px] font-mono uppercase bg-purple-950 text-purple-400 border border-purple-800 px-1.5 py-0.5 rounded font-semibold">
                    OCR Scanned
                  </span>
                )}
              </h2>
              <p className="text-[11px] text-slate-400">
                Ground-truth source reference • {wordCount} words • {charCount} chars • {lineCount} lines
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {uploadedImage && (
              <div className="flex items-center rounded-lg bg-[#111A33] border border-[#1D2D4E] p-0.5">
                <button
                  type="button"
                  onClick={() => setActiveTab('text')}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold transition ${
                    activeTab === 'text' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <FileText className="w-3 h-3" />
                  Text
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('image')}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold transition ${
                    activeTab === 'image' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <ImageIcon className="w-3 h-3" />
                  Image
                </button>
              </div>
            )}

            <button
              type="button"
              onClick={handleCopy}
              disabled={!rawNoticeText}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white bg-[#111A33] border border-[#1D2D4E] hover:border-slate-700 transition"
              title="Copy original notice text"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>

            <button
              type="button"
              onClick={closeOriginalNoticeModal}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
              aria-label="Close original notice modal"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Search Bar for Notice Text */}
        {activeTab === 'text' && (
          <div className="px-6 py-2.5 border-b border-[#1D2D4E] bg-[#070B14]/40 flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-slate-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search words in notice..."
              className="bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none w-full"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                className="text-[10px] text-slate-400 hover:text-white"
              >
                Clear
              </button>
            )}
          </div>
        )}

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {activeTab === 'image' && uploadedImage ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Scanned Notice Image:</span>
                {ocrResult && (
                  <span className="text-emerald-400 font-semibold">
                    OCR Confidence: {ocrResult.confidence_score.toFixed(1)}%
                  </span>
                )}
              </div>
              <div className="rounded-xl border border-[#1D2D4E] overflow-hidden bg-black/60 flex items-center justify-center p-2 max-h-[60vh]">
                <img
                  src={uploadedImage}
                  alt="Scanned original notice"
                  className="max-h-[56vh] object-contain rounded-lg"
                />
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              {rawNoticeText ? (
                <pre className="p-4 rounded-xl bg-[#070B14] border border-[#1D2D4E] text-xs font-mono text-slate-200 whitespace-pre-wrap leading-relaxed select-text">
                  {rawNoticeText}
                </pre>
              ) : (
                <div className="py-12 text-center text-xs text-slate-500">
                  No notice document loaded yet. Please paste or upload a notice in the Ingestion tab.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-[#1D2D4E] bg-[#070B14]/70 flex items-center justify-between text-xs text-slate-500">
          <span>This viewer displays verbatim source content without modification or hallucination.</span>
          <button
            type="button"
            onClick={closeOriginalNoticeModal}
            className="px-3.5 py-1 rounded-lg text-xs font-semibold text-slate-300 hover:text-white bg-[#111A33] border border-[#1D2D4E] transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
