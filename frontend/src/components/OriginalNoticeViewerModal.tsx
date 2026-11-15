import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
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
  AlertCircle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

export const OriginalNoticeViewerModal: React.FC = () => {
  const {
    isOriginalNoticeOpen,
    closeOriginalNoticeModal,
    rawNoticeText,
    uploadedImage,
    ocrResult,
    reviewHighlight,
    clearReviewHighlight,
    openConfirmationModal,
  } = useNotice();

  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<'text' | 'image'>(uploadedImage ? 'image' : 'text');
  const [prevHighlight, setPrevHighlight] = useState(reviewHighlight);

  if (reviewHighlight !== prevHighlight) {
    setPrevHighlight(reviewHighlight);
    if (reviewHighlight?.active) {
      if (uploadedImage && reviewHighlight.boxes && reviewHighlight.boxes.length > 0) {
        setActiveTab('image');
      } else {
        setActiveTab('text');
      }
    } else if (uploadedImage && !rawNoticeText) {
      setActiveTab('image');
    }
  }

  const [copied, setCopied] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [activeSearchIndex, setActiveSearchIndex] = useState<number>(0);
  const [highContrast, setHighContrast] = useState<boolean>(false);
  const [imgDims, setImgDims] = useState<{ width: number; height: number } | null>(null);

  const firstMatchRef = useRef<HTMLDivElement | null>(null);
  const imageContainerRef = useRef<HTMLDivElement | null>(null);
  const activeMatchRef = useRef<HTMLDivElement | null>(null);

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

  // Escape key listener:
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOriginalNoticeOpen) {
        if (reviewHighlight?.active) {
          clearReviewHighlight();
        } else {
          closeOriginalNoticeModal();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOriginalNoticeOpen, closeOriginalNoticeModal, reviewHighlight, clearReviewHighlight]);

  // Auto-scroll to matching text in text mode
  useEffect(() => {
    if (activeTab === 'text' && reviewHighlight?.active && !reviewHighlight.notFound) {
      const timer = setTimeout(() => {
        if (firstMatchRef.current && typeof firstMatchRef.current.scrollIntoView === 'function') {
          firstMatchRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [activeTab, reviewHighlight]);

  // Search match computation
  const cleanSearchQuery = searchQuery.trim().toLowerCase();

  const imageSearchMatches = useMemo(() => {
    if (!cleanSearchQuery || !ocrResult?.word_boxes) return [];
    return ocrResult.word_boxes.filter(
      (wb) => wb.text && wb.text.toLowerCase().includes(cleanSearchQuery) && wb.box && wb.box.length === 4
    );
  }, [cleanSearchQuery, ocrResult]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setActiveSearchIndex(0);
  };

  const handlePrevSearchMatch = () => {
    if (imageSearchMatches.length <= 1) return;
    setActiveSearchIndex((prev) => (prev <= 0 ? imageSearchMatches.length - 1 : prev - 1));
  };

  const handleNextSearchMatch = () => {
    if (imageSearchMatches.length <= 1) return;
    setActiveSearchIndex((prev) => (prev >= imageSearchMatches.length - 1 ? 0 : prev + 1));
  };

  // Scroll active match into view in image canvas
  useEffect(() => {
    if (activeTab === 'image' && imageSearchMatches.length > 0 && activeMatchRef.current && typeof activeMatchRef.current.scrollIntoView === 'function') {
      activeMatchRef.current.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
    }
  }, [activeTab, activeSearchIndex, imageSearchMatches.length]);

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

  const textMatchCount =
    cleanSearchQuery && rawNoticeText
      ? (rawNoticeText.match(new RegExp(cleanSearchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')) || []).length
      : 0;

  const textFontSize = Math.max(10, Math.round(14 * (zoomPercent / 100)));

  // Target text for review highlight
  const highlightTarget = (reviewHighlight?.evidenceQuote || reviewHighlight?.targetText || '').trim().toLowerCase();

  // Helper to test if a line matches the review highlight
  const checkLineHighlight = (line: string): { isMatch: boolean; matchSubstring?: string } => {
    if (!reviewHighlight?.active || reviewHighlight.notFound || !highlightTarget) {
      return { isMatch: false };
    }
    const lineLower = line.toLowerCase();
    if (lineLower.includes(highlightTarget)) {
      return { isMatch: true, matchSubstring: highlightTarget };
    }

    const words = highlightTarget.split(/\s+/).filter((w) => w.length > 2);
    if (words.length > 0) {
      const matchingWords = words.filter((w) => lineLower.includes(w));
      if (matchingWords.length >= Math.max(1, Math.ceil(words.length * 0.6))) {
        return { isMatch: true };
      }
    }
    return { isMatch: false };
  };

  // Find index of first matching line for auto-scroll ref
  let firstMatchingLineIndex = -1;
  if (reviewHighlight?.active && !reviewHighlight.notFound) {
    for (let i = 0; i < lines.length; i++) {
      if (checkLineHighlight(lines[i]).isMatch) {
        firstMatchingLineIndex = i;
        break;
      }
    }
  }

  // Resolved image dimensions for overlay calculations
  const naturalImgWidth = imgDims?.width || ocrResult?.image_dimensions?.[0] || 1000;
  const naturalImgHeight = imgDims?.height || ocrResult?.image_dimensions?.[1] || 1000;

  // Status theme styling helper
  const getStatusTheme = (status?: string) => {
    switch (status) {
      case 'verified':
        return {
          barBg: 'bg-emerald-50/95 border-emerald-200 text-emerald-950',
          dotBg: 'bg-emerald-500',
          badgeBg: 'bg-emerald-100 text-emerald-900 border-emerald-300',
          underlineBorder: 'border-emerald-600',
          underlineBg: 'bg-emerald-500/15',
          underlineRing: 'ring-emerald-400/40',
          wavyColor: '#059669',
          label: 'Verified',
        };
      case 'corrected':
        return {
          barBg: 'bg-blue-50/95 border-blue-200 text-blue-950',
          dotBg: 'bg-blue-500',
          badgeBg: 'bg-blue-100 text-blue-900 border-blue-300',
          underlineBorder: 'border-blue-600',
          underlineBg: 'bg-blue-500/15',
          underlineRing: 'ring-blue-400/40',
          wavyColor: '#2563EB',
          label: 'Corrected',
        };
      case 'ignored':
        return {
          barBg: 'bg-slate-50/95 border-slate-200 text-slate-900',
          dotBg: 'bg-slate-500',
          badgeBg: 'bg-slate-100 text-slate-700 border-slate-300',
          underlineBorder: 'border-slate-500',
          underlineBg: 'bg-slate-500/15',
          underlineRing: 'ring-slate-300/40',
          wavyColor: '#64748B',
          label: 'Ignored',
        };
      default:
        return {
          barBg: 'bg-red-50/95 border-red-200 text-red-950 shadow-inner',
          dotBg: 'bg-red-500',
          badgeBg: 'bg-red-100 text-red-900 border-red-300',
          underlineBorder: 'border-red-600',
          underlineBg: 'bg-red-500/15',
          underlineRing: 'ring-red-400/40',
          wavyColor: '#DC2626',
          label: 'Uncertain / Pending',
        };
    }
  };

  const statusTheme = getStatusTheme(reviewHighlight?.status);

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

        {/* CLICK-TO-REVIEW SYNCHRONIZED HIGHLIGHT CONTROL BAR */}
        {reviewHighlight?.active && (
          <div
            data-testid="review-highlight-bar"
            className={`px-4 sm:px-6 py-2.5 border-b flex flex-wrap items-center justify-between gap-3 transition-colors ${
              reviewHighlight.notFound
                ? 'bg-amber-50 border-amber-200 text-amber-900'
                : statusTheme.barBg
            }`}
          >
            <div className="flex items-center gap-2.5 flex-1 min-w-[240px]">
              <span className="relative flex h-2.5 w-2.5 shrink-0">
                <span
                  className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                    reviewHighlight.notFound ? 'bg-amber-400' : statusTheme.dotBg
                  }`}
                />
                <span
                  className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                    reviewHighlight.notFound ? 'bg-amber-500' : statusTheme.dotBg
                  }`}
                />
              </span>

              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-bold text-xs uppercase tracking-wide">
                  Reviewing: {reviewHighlight.displayName}
                </span>
                {reviewHighlight.status && (
                  <span
                    data-testid="review-status-indicator"
                    className={`text-[10px] font-bold px-2 py-0.5 rounded border ${statusTheme.badgeBg}`}
                  >
                    {statusTheme.label}
                  </span>
                )}
                {reviewHighlight.pageNumber && (
                  <span
                    data-testid="review-page-indicator"
                    className="text-[10px] font-mono px-2 py-0.5 rounded bg-white border border-slate-200 font-bold text-slate-700 shadow-2xs"
                  >
                    Page {reviewHighlight.pageNumber}
                  </span>
                )}
              </div>

              {reviewHighlight.notFound ? (
                <span
                  data-testid="review-not-found-message"
                  className="text-xs font-semibold text-amber-900 bg-amber-100/90 px-2.5 py-1 rounded-md border border-amber-300 flex items-center gap-1.5"
                >
                  <AlertCircle className="w-3.5 h-3.5 text-amber-700 shrink-0" />
                  Could not locate this text in the original notice
                </span>
              ) : (
                <span className="text-xs italic truncate max-w-sm sm:max-w-md bg-white/70 px-2 py-0.5 rounded border border-slate-200">
                  "{reviewHighlight.targetText}"
                </span>
              )}
            </div>

            <div className="flex items-center gap-2 shrink-0">
              {reviewHighlight.fact && (
                <button
                  type="button"
                  onClick={() => {
                    openConfirmationModal(
                      reviewHighlight.fieldName,
                      reviewHighlight.displayName,
                      reviewHighlight.fact
                    );
                  }}
                  className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-white border border-slate-200 text-[#12233D] hover:bg-slate-100 transition shadow-2xs cursor-pointer flex items-center gap-1"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-[#08785D]" />
                  <span>Confirm / Edit</span>
                </button>
              )}
              <button
                type="button"
                onClick={clearReviewHighlight}
                data-testid="exit-review-highlight-btn"
                className="px-2.5 py-1 text-xs font-bold rounded-lg bg-red-600 hover:bg-red-700 text-white transition shadow-2xs cursor-pointer flex items-center gap-1"
                title="Exit highlight mode (Esc)"
              >
                <X className="w-3.5 h-3.5" />
                <span>Exit Highlight</span>
              </button>
            </div>
          </div>
        )}

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

        {/* Toolbar: Search inside Notice with Yellow Highlights on Image */}
        <div className="flex items-center justify-between px-6 py-2.5 bg-white border-b border-[#E1E7EE] gap-4 flex-wrap">
          <div className="relative flex-1 max-w-sm min-w-[200px]">
            <Search className="w-3.5 h-3.5 text-[#68778B] absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder={t('searchNotice') || 'Search keyword in source notice...'}
              className="w-full bg-[#F8FAFC] border border-[#E1E7EE] focus:border-[#08785D] focus:outline-hidden rounded-lg pl-8 pr-3 py-1 text-xs text-[#12233D] placeholder-[#68778B]"
            />
          </div>

          {cleanSearchQuery && (
            <div className="flex items-center gap-2">
              {activeTab === 'image' ? (
                imageSearchMatches.length > 0 ? (
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-amber-800 bg-yellow-100 border border-yellow-300 px-2 py-0.5 rounded" data-testid="search-match-counter">
                      Match {activeSearchIndex + 1} of {imageSearchMatches.length}
                    </span>
                    <div className="flex items-center border border-slate-200 rounded-md bg-white">
                      <button
                        type="button"
                        onClick={handlePrevSearchMatch}
                        disabled={imageSearchMatches.length <= 1}
                        data-testid="search-prev-btn"
                        className="p-1 text-slate-600 hover:text-slate-900 disabled:opacity-30 cursor-pointer"
                        title="Previous match"
                      >
                        <ChevronLeft className="w-3.5 h-3.5" />
                      </button>
                      <button
                        type="button"
                        onClick={handleNextSearchMatch}
                        disabled={imageSearchMatches.length <= 1}
                        data-testid="search-next-btn"
                        className="p-1 text-slate-600 hover:text-slate-900 border-l border-slate-200 disabled:opacity-30 cursor-pointer"
                        title="Next match"
                      >
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ) : textMatchCount > 0 ? (
                  <span
                    data-testid="search-no-box-warning"
                    className="text-xs font-semibold text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200"
                  >
                    Found in text ({textMatchCount} matches), no visual image box available
                  </span>
                ) : (
                  <span className="text-xs font-medium text-[#526176]">0 matches found</span>
                )
              ) : (
                <span className="text-xs font-medium text-[#526176]">
                  {textMatchCount} {textMatchCount === 1 ? (t('matchFound') || 'match found') : (t('matchesFound') || 'matches found')}
                </span>
              )}
            </div>
          )}
        </div>

        {/* Body Viewer */}
        <div
          ref={imageContainerRef}
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
                <div className="relative inline-block max-w-full">
                  <img
                    src={uploadedImage}
                    alt="Original scanned notice preview"
                    onLoad={(e) => {
                      const img = e.currentTarget;
                      setImgDims({ width: img.naturalWidth, height: img.naturalHeight });
                    }}
                    className="w-full h-auto object-contain rounded-lg shadow-md border border-[#E1E7EE] select-none block"
                    style={{ maxWidth: 'none' }}
                  />

                  {/* Yellow Search Highlights on Image Canvas */}
                  {cleanSearchQuery &&
                    imageSearchMatches.map((wb, idx) => {
                      const [l, t, r, b] = wb.box;
                      const leftPct = (l / naturalImgWidth) * 100;
                      const topPct = (t / naturalImgHeight) * 100;
                      const widthPct = Math.max(0.5, ((r - l) / naturalImgWidth) * 100);
                      const heightPct = Math.max(0.5, ((b - t) / naturalImgHeight) * 100);
                      const isActiveMatch = idx === activeSearchIndex;

                      return (
                        <div
                          key={`search_box_${idx}`}
                          ref={isActiveMatch ? activeMatchRef : undefined}
                          data-testid="ocr-search-yellow-highlight"
                          className={`absolute pointer-events-none rounded-xs transition-all ${
                            isActiveMatch
                              ? 'bg-yellow-300/80 border-2 border-amber-600 ring-2 ring-amber-400 z-20 shadow-md animate-pulse'
                              : 'bg-yellow-400/40 border border-yellow-500 z-10'
                          }`}
                          style={{
                            left: `${leftPct}%`,
                            top: `${topPct}%`,
                            width: `${widthPct}%`,
                            height: `${heightPct}%`,
                          }}
                          title={`Search match: ${wb.text}`}
                        />
                      );
                    })}

                  {/* Synchronized Underline Overlay for OCR Review Highlights */}
                  {reviewHighlight?.active &&
                    !reviewHighlight.notFound &&
                    reviewHighlight.boxes &&
                    reviewHighlight.boxes.length > 0 &&
                    reviewHighlight.boxes.map((box, idx) => {
                      const leftPct = (box[0] / naturalImgWidth) * 100;
                      const topPct = (box[1] / naturalImgHeight) * 100;
                      const widthPct = Math.max(0.5, ((box[2] - box[0]) / naturalImgWidth) * 100);
                      const heightPct = Math.max(0.5, ((box[3] - box[1]) / naturalImgHeight) * 100);

                      return (
                        <div
                          key={`review_box_${idx}`}
                          data-testid="ocr-red-underline-highlight"
                          data-status={reviewHighlight.status || 'pending'}
                          className={`absolute border-b-[3px] ${statusTheme.underlineBorder} ${statusTheme.underlineBg} ring-2 ${statusTheme.underlineRing} pointer-events-none rounded-xs transition-all shadow-xs z-30`}
                          style={{
                            left: `${leftPct}%`,
                            top: `${topPct}%`,
                            width: `${widthPct}%`,
                            height: `${heightPct}%`,
                          }}
                          title={`Reviewing: ${reviewHighlight.displayName} (${statusTheme.label})`}
                        />
                      );
                    })}
                </div>
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
                const isSearchMatch = cleanSearchQuery && line.toLowerCase().includes(cleanSearchQuery);
                const lineHighlight = checkLineHighlight(line);
                const isFirstMatch = index === firstMatchingLineIndex;
                const isPageMarker = /---\s*Page\s*\d+\s*---/i.test(line);

                if (isPageMarker) {
                  return (
                    <div
                      key={index}
                      data-testid="viewer-page-marker"
                      className="my-3 py-1.5 px-3 rounded-lg bg-slate-100 border border-slate-200 text-center text-xs font-bold font-mono text-[#08785D]"
                    >
                      {line}
                    </div>
                  );
                }

                // If line contains review highlight
                if (lineHighlight.isMatch) {
                  return (
                    <div
                      key={index}
                      ref={isFirstMatch ? firstMatchRef : undefined}
                      data-testid="text-red-underline-highlight-row"
                      className={`flex items-start gap-4 py-1.5 rounded-lg px-2 my-1 transition-all border-b-[3px] ${statusTheme.underlineBorder} ${statusTheme.barBg} shadow-xs ring-1 ring-slate-300 ${
                        highContrast ? 'bg-slate-900 text-white' : ''
                      }`}
                    >
                      <span className="text-[11px] select-none w-8 text-right shrink-0 pt-0.5 font-bold opacity-75">
                        {index + 1}
                      </span>
                      <span className="flex-1 whitespace-pre-wrap break-words overflow-x-hidden">
                        {lineHighlight.matchSubstring ? (
                          (() => {
                            const matchStart = line.toLowerCase().indexOf(lineHighlight.matchSubstring.toLowerCase());
                            if (matchStart === -1) return line;
                            const before = line.slice(0, matchStart);
                            const matchedPart = line.slice(matchStart, matchStart + lineHighlight.matchSubstring.length);
                            const after = line.slice(matchStart + lineHighlight.matchSubstring.length);

                            return (
                              <>
                                {before}
                                <span
                                  data-testid="text-red-underline-highlight"
                                  className={`border-b-[3px] ${statusTheme.underlineBorder} font-bold px-0.5 rounded-xs`}
                                  style={{ textDecoration: `underline wavy ${statusTheme.wavyColor} 2px` }}
                                >
                                  {matchedPart}
                                </span>
                                {after}
                              </>
                            );
                          })()
                        ) : (
                          <span
                            data-testid="text-red-underline-highlight"
                            className={`border-b-[3px] ${statusTheme.underlineBorder} font-bold px-0.5 rounded-xs`}
                            style={{ textDecoration: `underline wavy ${statusTheme.wavyColor} 2px` }}
                          >
                            {line}
                          </span>
                        )}
                      </span>
                    </div>
                  );
                }

                return (
                  <div
                    key={index}
                    className={`flex items-start gap-4 py-0.5 rounded px-1.5 transition ${
                      isSearchMatch
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
