import React, { useState, useEffect, useCallback } from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import {
  FileText,
  Image as ImageIcon,
  Copy,
  Check,
  X,
  Search,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Sun,
  Info,
} from 'lucide-react';

export const OriginalNoticeViewerModal: React.FC = () => {
  const { isOriginalNoticeOpen, closeOriginalNoticeModal, rawNoticeText, uploadedImage } = useNotice();
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<'text' | 'image'>(uploadedImage ? 'image' : 'text');
  const [copied, setCopied] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [highContrast, setHighContrast] = useState<boolean>(false);

  // Zoom percentage: 50% to 300%, step 25%, default 100%
  const [zoomPercent, setZoomPercent] = useState<number>(() => {
    try {
      const saved = localStorage.getItem('suchnasetu_viewer_zoom_percent');
      const parsed = saved ? parseInt(saved, 10) : 100;
      return parsed >= 50 && parsed <= 300 ? parsed : 100;
    } catch {
      return 100;
    }
  });

  const updateZoom = useCallback((newZoom: number) => {
    const clamped = Math.max(50, Math.min(300, newZoom));
    setZoomPercent(clamped);
    try {
      localStorage.setItem('suchnasetu_viewer_zoom_percent', String(clamped));
    } catch {}
  }, []);

  const zoomIn = () => updateZoom(zoomPercent + 25);
  const zoomOut = () => updateZoom(zoomPercent - 25);
  const resetZoom = () => updateZoom(100);

  // Synchronize initial tab if uploadedImage changes
  useEffect(() => {
    if (uploadedImage && !rawNoticeText) {
      setActiveTab('image');
    }
  }, [uploadedImage, rawNoticeText]);

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

  const fallbackCopy = (text: string) => {
    try {
      const el = document.createElement('textarea');
      el.value = text;
      el.setAttribute('readonly', '');
      el.style.position = 'fixed';
      el.style.left = '-9999px';
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Fallback copy failed', err);
    }
  };

  const handleCopy = () => {
    if (!rawNoticeText) return;
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard
        .writeText(rawNoticeText)
        .then(() => {
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        })
        .catch(() => fallbackCopy(rawNoticeText));
    } else {
      fallbackCopy(rawNoticeText);
    }
  };

  const lines = rawNoticeText ? rawNoticeText.split('\n') : [];
  const lineCount = lines.length;
  const wordCount = rawNoticeText ? rawNoticeText.trim().split(/\s+/).filter(Boolean).length : 0;
  const charCount = rawNoticeText ? rawNoticeText.length : 0;

  const matchCount =
    searchQuery.trim() && rawNoticeText
      ? (rawNoticeText.match(new RegExp(searchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')) || []).length
      : 0;

  const textFontSize = Math.max(10, Math.round(14 * (zoomPercent / 100)));

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="original-notice-title"
      onClick={(e) => {
        if (e.target === e.currentTarget) closeOriginalNoticeModal();
      }}
      className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200"
    >
      <div className="bg-white border border-[#E1E7EE] rounded-xl sm:rounded-2xl w-full max-w-4xl max-h-[92vh] sm:max-h-[90vh] shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-3 sm:px-6 py-3 sm:py-4 border-b border-[#E1E7EE] bg-[#F8FAFC]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[#E8F7F0] border border-[#B7E7D2] text-[#08785D] flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <h2 id="original-notice-title" className="text-sm font-bold text-[#12233D] flex items-center gap-2">
                {t('originalNoticeModalTitle') || 'Original Notice Document Viewer'}
                {uploadedImage && (
                  <span className="text-[10px] font-mono uppercase bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2] px-1.5 py-0.5 rounded font-semibold">
                    {t('ocrScanned') || 'OCR Scanned'}
                  </span>
                )}
              </h2>
              <p className="text-[11px] text-[#526176]">
                {t('sourceReference') || 'Ground-truth source reference'} • {wordCount} words • {charCount} chars • {lineCount} lines
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
                    activeTab === 'text' ? 'bg-[#08785D] text-white shadow-xs' : 'text-[#526176] hover:text-[#12233D]'
                  }`}
                  aria-pressed={activeTab === 'text'}
                >
                  <FileText className="w-3 h-3" />
                  {t('textMode') || 'Text'}
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('image')}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold transition cursor-pointer ${
                    activeTab === 'image' ? 'bg-[#08785D] text-white shadow-xs' : 'text-[#526176] hover:text-[#12233D]'
                  }`}
                  aria-pressed={activeTab === 'image'}
                >
                  <ImageIcon className="w-3 h-3" />
                  {t('imageMode') || 'Image'}
                </button>
              </div>
            )}

            {/* Document Zoom Controls */}
            <div className="flex items-center gap-1 bg-slate-100 border border-[#E1E7EE] rounded-lg p-0.5">
              <button
                type="button"
                onClick={zoomOut}
                disabled={zoomPercent <= 50}
                className="p-1 rounded text-[#526176] hover:text-[#12233D] hover:bg-white transition cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                title={t('zoomOut') || 'Zoom Out (-25%)'}
                aria-label="Zoom out document"
              >
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
              <span
                className="text-[10px] font-mono px-1.5 text-[#12233D] font-bold min-w-[45px] text-center select-none"
                data-testid="viewer-zoom-display"
              >
                {zoomPercent}%
              </span>
              <button
                type="button"
                onClick={zoomIn}
                disabled={zoomPercent >= 300}
                className="p-1 rounded text-[#526176] hover:text-[#12233D] hover:bg-white transition cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                title={t('zoomIn') || 'Zoom In (+25%)'}
                aria-label="Zoom in document"
              >
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={resetZoom}
                disabled={zoomPercent === 100}
                className="p-1 rounded text-[#526176] hover:text-[#12233D] hover:bg-white transition cursor-pointer border-l border-slate-200 disabled:opacity-40 disabled:cursor-not-allowed"
                title={t('resetZoom') || 'Reset Zoom (100%)'}
                aria-label="Reset zoom to default"
              >
                <RotateCcw className="w-3 h-3" />
              </button>
            </div>

            {/* High Contrast Toggle */}
            <button
              type="button"
              onClick={() => setHighContrast(!highContrast)}
              className={`p-1.5 rounded-lg border text-xs font-semibold transition cursor-pointer flex items-center gap-1 ${
                highContrast
                  ? 'bg-[#12233D] text-amber-300 border-amber-400'
                  : 'bg-white text-[#526176] border-[#E1E7EE] hover:text-[#12233D]'
              }`}
              title={highContrast ? 'Switch to Standard Theme' : 'Enable High-Contrast Mode for Document'}
            >
              <Sun className="w-3.5 h-3.5" />
              <span className="hidden md:inline">{highContrast ? 'Standard' : 'Contrast'}</span>
            </button>

            <button
              type="button"
              onClick={handleCopy}
              disabled={!rawNoticeText}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold text-[#12233D] hover:text-[#08785D] bg-white border border-[#E1E7EE] hover:border-[#B7E7D2] transition cursor-pointer disabled:opacity-40"
              title={t('copyNoticeText') || 'Copy original notice text'}
            >
              {copied ? <Check className="w-3.5 h-3.5 text-[#08785D]" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? (t('copied') || 'Copied') : (t('copy') || 'Copy')}</span>
            </button>

            <button
              type="button"
              onClick={closeOriginalNoticeModal}
              className="text-[#68778B] hover:text-[#12233D] p-1.5 rounded-lg hover:bg-slate-100 transition cursor-pointer"
              aria-label={t('close') || 'Close original notice modal'}
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* DOCUMENT DISTINCTION BANNER */}
        <div className="flex items-center justify-between px-6 py-2 bg-[#F1F5F9] border-b border-[#E1E7EE] text-[11px] text-[#475569]">
          <div className="flex items-center gap-2">
            <Info className="w-3.5 h-3.5 text-[#08785D] shrink-0" />
            <span>
              {activeTab === 'image'
                ? (t('imageModeDesc') || 'Displaying Original Scanned Notice Image (Visual OCR Source • Pixel-exact • Zoomable & Pannable)')
                : (t('textModeDesc') || 'Displaying Extracted Machine-Readable Notice Text (Line-wrapped • Searchable • Scalable Font)')}
            </span>
          </div>
          <span className="font-mono text-[10px] text-[#64748B] shrink-0">
            Zoom: {zoomPercent}% {highContrast && '• High-Contrast Active'}
          </span>
        </div>

        {/* Toolbar: Search inside Notice */}
        <div className="flex items-center justify-between px-6 py-2.5 bg-white border-b border-[#E1E7EE] gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="w-3.5 h-3.5 text-[#68778B] absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t('searchNotice') || 'Search keyword in source notice...'}
              className="w-full bg-[#F8FAFC] border border-[#E1E7EE] focus:border-[#08785D] focus:outline-hidden rounded-lg pl-8 pr-3 py-1 text-xs text-[#12233D] placeholder-[#68778B]"
            />
          </div>
          {searchQuery.trim() && (
            <span className="text-xs font-medium text-[#526176]">
              {matchCount} {matchCount === 1 ? (t('matchFound') || 'match found') : (t('matchesFound') || 'matches found')}
            </span>
          )}
        </div>

        {/* Body Viewer */}
        <div
          className={`flex-1 overflow-auto p-6 transition-colors ${
            highContrast ? 'bg-[#0B132B]' : 'bg-[#F8FAFC]'
          }`}
        >
          {activeTab === 'image' && uploadedImage ? (
            <div className="w-full h-full min-h-[50vh] max-h-[65vh] overflow-auto flex items-center justify-center p-2">
              <div
                style={{
                  width: `${zoomPercent}%`,
                  minWidth: `${zoomPercent}%`,
                  transition: 'width 0.15s ease-out',
                }}
                className="flex items-center justify-center m-auto"
                data-testid="viewer-image-container"
              >
                <img
                  src={uploadedImage}
                  alt="Original scanned notice preview"
                  className="w-full h-auto object-contain rounded-lg shadow-md border border-[#E1E7EE] select-none"
                  style={{ maxWidth: 'none' }}
                />
              </div>
            </div>
          ) : (
            <div
              className={`border rounded-xl p-5 shadow-xs font-mono leading-relaxed select-text transition-colors whitespace-pre-wrap break-words overflow-x-auto ${
                highContrast
                  ? 'bg-[#1C2541] border-yellow-400 text-[#F8FAFC]'
                  : 'bg-white border-[#E1E7EE] text-[#12233D]'
              }`}
              style={{ fontSize: `${textFontSize}px` }}
              data-testid="viewer-text-container"
            >
              {lines.map((line, index) => {
                const isMatch = searchQuery.trim() && line.toLowerCase().includes(searchQuery.toLowerCase());
                return (
                  <div
                    key={index}
                    className={`flex items-start gap-4 py-0.5 rounded px-1.5 transition ${
                      isMatch
                        ? highContrast
                          ? 'bg-yellow-400 text-black font-bold'
                          : 'bg-[#FFF4D6] text-[#92500A] font-semibold'
                        : highContrast
                        ? 'text-white'
                        : 'text-[#12233D]'
                    }`}
                  >
                    <span
                      className={`text-[11px] select-none w-8 text-right shrink-0 pt-0.5 ${
                        highContrast ? 'text-yellow-300 font-bold' : 'text-[#CBD5E1]'
                      }`}
                    >
                      {index + 1}
                    </span>
                    <span className="flex-1 whitespace-pre-wrap break-words overflow-x-hidden">
                      {line || '\u00A0'}
                    </span>
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
