import React, { useState, useMemo, useRef, useEffect } from 'react';
import { useNotice } from '../context/NoticeContext';
import { FileDropzone } from '../components/FileDropzone';
import { OCRPanel } from '../components/OCRPanel';
import { NoticeBuffer } from '../components/NoticeBuffer';
import { StaleWarningBanner } from '../components/StaleWarningBanner';
import { MetricCard } from '../components/MetricCard';
import { ActionChecklistTable } from '../components/ActionChecklistTable';
import { GroundedQAChat } from '../components/GroundedQAChat';
import type { ExtractedFact } from '../types/api';
import {
  FileText,
  Search,
  CheckSquare,
  UserCheck,
  ShieldCheck,
  ListTodo,
  MessageSquare,
  GitCompare,
  Copy,
  Check,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Minimize2,
  ChevronDown,
  ChevronUp,
  Play,
  Sparkles,
  AlertTriangle,
  Volume2,
  ArrowRight,
  ExternalLink,
  Layers,
  FolderOpen,
  Info,
  Calendar,
  Building2,
  Hash,
  Clock,
  HelpCircle,
  X,
  Globe,
  RefreshCw,
} from 'lucide-react';
import { SUPPORTED_LANGUAGES, LANGUAGE_CODES } from '../i18n';

export const IngestionView: React.FC = () => {
  const {
    rawNoticeText,
    runAnalysis,
    isAnalyzing,
    analysisError,
    structuredNotice,
    analysisDuration,
    setActiveTab,
    uploadedImage,
    ocrResult,
    summaryEn,
    summaryHi,
    localizedSummary,
    selectedLang,
    setSelectedLang,
    outputLang,
    setOutputLang,
    sourceLang,
    setSourceLang,
    detectedLangMeta,
    detectDocumentLanguage,
    readingLevel,
    changeReadingLevel,
    speakText,
    openEvidenceInspector,
    openConfirmationModal,
  } = useNotice();

  // Workspace View State
  const [activeAnalysisTab, setActiveAnalysisTab] = useState<
    'overview' | 'facts' | 'eligibility' | 'evidence' | 'actions' | 'qa' | 'changes'
  >('overview');
  const [mobileTab, setMobileTab] = useState<'source' | 'analysis'>('analysis');
  const [isIngestionDrawerOpen, setIsIngestionDrawerOpen] = useState<boolean>(true);
  const [isSourceExpanded, setIsSourceExpanded] = useState<boolean>(false);

  // Source Viewer Controls
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [fontSizeLevel, setFontSizeLevel] = useState<1 | 2 | 3>(2); // 1: text-xs, 2: text-sm, 3: text-base
  const [hasCopied, setHasCopied] = useState<boolean>(false);
  const [highlightedSnippet, setHighlightedSnippet] = useState<string | null>(null);

  const sourceContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (uploadedImage && !rawNoticeText.trim()) {
      setIsIngestionDrawerOpen(true);
    }
  }, [uploadedImage, rawNoticeText]);

  // Compute text lines
  const lines = useMemo(() => {
    if (!rawNoticeText) return [];
    return rawNoticeText.split('\n');
  }, [rawNoticeText]);

  const charCount = rawNoticeText.length;
  const wordCount = rawNoticeText.trim() ? rawNoticeText.trim().split(/\s+/).length : 0;
  const lineCount = lines.length;

  // Search match counts
  const searchMatchesCount = useMemo(() => {
    if (!searchQuery.trim() || !rawNoticeText) return 0;
    const escaped = searchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const matches = rawNoticeText.match(new RegExp(escaped, 'gi'));
    return matches ? matches.length : 0;
  }, [searchQuery, rawNoticeText]);

  const handleCopySource = () => {
    if (!rawNoticeText) return;
    navigator.clipboard.writeText(rawNoticeText);
    setHasCopied(true);
    setTimeout(() => setHasCopied(false), 2000);
  };

  const handleHighlightInSource = (snippet: string) => {
    setHighlightedSnippet(snippet);
    setMobileTab('source');
    // Scroll left container to highlight
    if (sourceContainerRef.current) {
      sourceContainerRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  };

  // Font size class mapping
  const fontSizeClass =
    fontSizeLevel === 1 ? 'text-xs' : fontSizeLevel === 3 ? 'text-base' : 'text-sm';

  const currentSummary = useMemo(() => {
    if (outputLang && outputLang !== 'en' && localizedSummary) {
      return localizedSummary;
    }
    if (selectedLang === 'hi' || outputLang === 'hi') {
      return summaryHi || localizedSummary || summaryEn;
    }
    return summaryEn || localizedSummary || summaryHi;
  }, [outputLang, localizedSummary, selectedLang, summaryHi, summaryEn]);

  // Render individual fact row
  const renderFactItem = (
    label: string,
    fact?: ExtractedFact,
    categoryName?: string
  ) => {
    if (!fact) return null;
    const isStated = fact.status === 'stated';
    const isUncertain = fact.status === 'uncertain';
    const isNotStated = fact.status === 'not_stated';

    return (
      <div
        key={label}
        className="p-4 rounded-xl bg-white border border-[#E1E7EE] hover:border-[#B7E7D2] transition space-y-3 shadow-xs"
      >
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-[#12233D]">{label}</span>
            {categoryName && (
              <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-md bg-[#F8FAFC] text-[#526176] border border-[#E1E7EE]">
                {categoryName}
              </span>
            )}
          </div>
          <div>
            {isStated && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-[11px] font-bold bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]">
                <Check className="w-3 h-3" /> Grounded
              </span>
            )}
            {isUncertain && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-[11px] font-bold bg-[#FFF4D6] text-[#92500A] border border-[#FDE68A]">
                <AlertTriangle className="w-3 h-3" /> Uncertain
              </span>
            )}
            {isNotStated && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-[11px] font-medium bg-slate-100 text-[#526176] border border-slate-200">
                Not Stated
              </span>
            )}
          </div>
        </div>

        {/* Fact Value */}
        <p className="text-xs font-semibold text-[#12233D] leading-relaxed">
          {fact.value || (
            <span className="italic text-[#68778B]">Not explicitly mentioned in circular.</span>
          )}
        </p>

        {/* Verbatim Source Quote if available */}
        {fact.evidence_quote && (
          <div className="space-y-1.5 pt-1">
            <div className="p-2.5 rounded-lg bg-[#F8FAFC] border-l-3 border-[#08785D] text-[11px] text-[#526176] font-mono italic leading-relaxed">
              "{fact.evidence_quote}"
            </div>
            <div className="flex items-center gap-2 pt-0.5">
              <button
                type="button"
                onClick={() => handleHighlightInSource(fact.evidence_quote!)}
                className="inline-flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-semibold text-[#08785D] bg-[#E8F7F0] hover:bg-[#D1F0E2] transition cursor-pointer"
              >
                <Search className="w-3 h-3" />
                <span>Locate in Source</span>
              </button>
              <button
                type="button"
                onClick={() =>
                  openEvidenceInspector(
                    {
                      excerpt: fact.evidence_quote!,
                      claim: `${label}: ${fact.value}`,
                      docTitle: 'Official Notice Circular',
                    },
                    rawNoticeText
                  )
                }
                className="inline-flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-semibold text-[#245DC1] bg-[#EAF2FF] hover:bg-[#D9E8FF] transition cursor-pointer"
              >
                <ShieldCheck className="w-3 h-3" />
                <span>Evidence Inspector</span>
              </button>
              {isUncertain && fact.requires_confirmation && (
                <button
                  type="button"
                  onClick={() => openConfirmationModal(fact.field_name, label, fact)}
                  className="inline-flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-semibold text-[#92500A] bg-[#FFF4D6] hover:bg-[#FDE68A] transition cursor-pointer"
                >
                  <span>Confirm Value</span>
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-5">
      {/* Workspace Breadcrumb & Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-[#E1E7EE]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]">
              CIVIC NOTICE INTELLIGENCE
            </span>
            {structuredNotice && (
              <>
                <span className="text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-[#EAF2FF] text-[#245DC1] border border-[#BFDBFE]">
                  GROUNDED & VERIFIED
                </span>
                <span className="text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]">
                  Notice Analyzed
                </span>
              </>
            )}
          </div>
          <h1 className="text-xl font-bold text-[#12233D] tracking-tight flex items-center gap-2">
            <Layers className="w-5 h-5 text-[#08785D]" />
            <span>Notice Intelligence Workspace</span>
          </h1>
          <p className="text-xs text-[#526176] mt-0.5 max-w-2xl">
            Ingest and review official circulars, scholarships, and administrative notifications.
            Inspect source text side-by-side with grounded facts, eligibility rules, and actionable steps.
          </p>
        </div>

        {/* Primary Action Buttons */}
        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          <button
            type="button"
            onClick={() => setIsIngestionDrawerOpen(!isIngestionDrawerOpen)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold text-[#12233D] bg-white border border-[#CBD5E1] hover:bg-[#F8FAFC] transition shadow-xs cursor-pointer"
          >
            <FolderOpen className="w-3.5 h-3.5 text-[#08785D]" />
            <span>{isIngestionDrawerOpen ? 'Hide Ingestion Tools' : 'Upload / OCR Source'}</span>
            {isIngestionDrawerOpen ? (
              <ChevronUp className="w-3.5 h-3.5 text-[#68778B]" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5 text-[#68778B]" />
            )}
          </button>

          <button
            type="button"
            onClick={runAnalysis}
            disabled={!rawNoticeText.trim() || isAnalyzing}
            className="flex items-center gap-2 py-2 px-4 rounded-xl font-bold text-xs text-white bg-[#08785D] hover:bg-[#06664E] active:scale-[0.98] transition shadow-xs disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            <Play className={`w-3.5 h-3.5 fill-white ${isAnalyzing ? 'animate-spin' : ''}`} />
            <span>
              {isAnalyzing
                ? 'Grounding with Gemma 4...'
                : structuredNotice
                ? 'Re-Analyze Notice'
                : 'Analyze Notice with Local Gemma 4'} {analysisDuration ? ' (' + analysisDuration.toFixed(1) + 's)' : ''}
            </span>
          </button>
        </div>
      </div>

      {/* Multilingual Source & Output Language Separation Bar */}
      <div className="bg-white rounded-2xl p-4 border border-[#E1E7EE] shadow-xs grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Source Language Card */}
        <div className="flex flex-col gap-2 p-3 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-xs font-bold text-[#12233D]">
              <Globe className="w-3.5 h-3.5 text-[#08785D]" />
              <span>Document Source Language</span>
            </div>
            {detectedLangMeta ? (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]">
                Detected: {(SUPPORTED_LANGUAGES as any)[detectedLangMeta.detected_language]?.nativeName || detectedLangMeta.detected_language.toUpperCase()} ({(detectedLangMeta.confidence * 100).toFixed(0)}%)
                {detectedLangMeta.is_mixed ? ' • Mixed' : ''}
              </span>
            ) : (
              <button
                type="button"
                onClick={detectDocumentLanguage}
                disabled={!rawNoticeText.trim()}
                className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold text-[#08785D] hover:bg-[#E8F7F0] disabled:opacity-40 transition cursor-pointer"
              >
                <RefreshCw className="w-2.5 h-2.5" />
                <span>Auto-Detect</span>
              </button>
            )}
          </div>
          <div className="flex items-center gap-2">
            <select
              value={sourceLang}
              onChange={(e) => setSourceLang(e.target.value)}
              aria-label="Document Source Language Override"
              className="flex-1 bg-white border border-[#CBD5E1] rounded-lg px-2.5 py-1.5 text-xs font-medium text-[#12233D] outline-hidden focus:border-[#08785D] cursor-pointer"
            >
              <option value="auto">Auto-Detect Language (Default)</option>
              {LANGUAGE_CODES.map((code) => (
                <option key={code} value={code}>
                  {SUPPORTED_LANGUAGES[code].nativeName} ({SUPPORTED_LANGUAGES[code].name})
                </option>
              ))}
            </select>
          </div>
          <span className="text-[10px] text-[#68778B]">
            Original script used in the uploaded notice. Auto-detected or manually specified.
          </span>
        </div>

        {/* Output Explanation Language Card */}
        <div className="flex flex-col gap-2 p-3 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-xs font-bold text-[#12233D]">
              <Sparkles className="w-3.5 h-3.5 text-[#245DC1]" />
              <span>AI Output Explanation Language</span>
            </div>
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#EAF2FF] text-[#245DC1] border border-[#BFDBFE]">
              Target: {(SUPPORTED_LANGUAGES as any)[outputLang]?.nativeName || outputLang.toUpperCase()}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={outputLang}
              onChange={(e) => setOutputLang(e.target.value)}
              aria-label="AI Output Explanation Language"
              className="flex-1 bg-white border border-[#CBD5E1] rounded-lg px-2.5 py-1.5 text-xs font-bold text-[#12233D] outline-hidden focus:border-[#245DC1] cursor-pointer"
            >
              {LANGUAGE_CODES.map((code) => (
                <option key={code} value={code}>
                  {SUPPORTED_LANGUAGES[code].nativeName} ({SUPPORTED_LANGUAGES[code].name})
                </option>
              ))}
            </select>
          </div>
          <span className="text-[10px] text-[#68778B]">
            AI explanations, summaries, and action checklists are synthesized into this language.
          </span>
        </div>
      </div>

      <StaleWarningBanner />

      {/* Analysis Error Alert */}
      {analysisError && (
        <div className="p-4 rounded-xl bg-[#FEE8E7] border border-[#FCA5A5] text-xs text-[#B42318] flex items-start gap-3 shadow-xs">
          <AlertTriangle className="w-5 h-5 text-[#B42318] shrink-0 mt-0.5" />
          <div className="space-y-1">
            <div className="font-bold text-[#B42318]">Analysis Pipeline Diagnostic</div>
            <div>{analysisError}</div>
            <div className="text-[11px] text-[#526176]">
              Ensure Ollama is running (`ollama serve`) and the Gemma 4 / local LLM model is pulled.
            </div>
          </div>
        </div>
      )}

      {/* Collapsible Ingestion & OCR Drawer */}
      {isIngestionDrawerOpen && (
        <div className="bg-white border border-[#E1E7EE] rounded-2xl p-5 shadow-xs space-y-4 animate-in fade-in duration-200">
          <div className="flex items-center justify-between pb-2 border-b border-[#E1E7EE]">
            <span className="text-xs font-bold uppercase tracking-wider text-[#12233D] flex items-center gap-2">
              <FolderOpen className="w-4 h-4 text-[#08785D]" />
              Document Ingestion & OCR Ground Truth
            </span>
            <span className="text-[11px] text-[#526176]">
              PDF documents, scanned circular images, or plain text
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 items-start">
            {/* Left: File Upload & Tesseract OCR */}
            <div className="space-y-4">
              <div className="border border-[#E1E7EE] rounded-xl p-4 bg-[#F8FAFC] space-y-3">
                <span className="text-xs font-bold uppercase tracking-wider text-[#12233D] block">
                  📁 Upload Document or Scanned Circular
                </span>
                <FileDropzone />
              </div>
              {uploadedImage && <OCRPanel />}
            </div>

            {/* Right: Ground Truth Buffer */}
            <div className="h-full">
              <NoticeBuffer />
            </div>
          </div>
        </div>
      )}

      {/* Mobile Screen Segmented Switcher */}
      <div className="flex lg:hidden items-center p-1 bg-white border border-[#E1E7EE] rounded-xl shadow-xs">
        <button
          type="button"
          onClick={() => setMobileTab('source')}
          className={`flex-1 py-2 text-xs font-bold rounded-lg transition cursor-pointer flex items-center justify-center gap-1.5 ${
            mobileTab === 'source'
              ? 'bg-[#08785D] text-white shadow-xs'
              : 'text-[#526176] hover:text-[#12233D]'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Original Source ({lineCount} lines)</span>
        </button>
        <button
          type="button"
          onClick={() => setMobileTab('analysis')}
          className={`flex-1 py-2 text-xs font-bold rounded-lg transition cursor-pointer flex items-center justify-center gap-1.5 ${
            mobileTab === 'analysis'
              ? 'bg-[#08785D] text-white shadow-xs'
              : 'text-[#526176] hover:text-[#12233D]'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Notice Analysis {structuredNotice ? '• Ready' : ''}</span>
        </button>
      </div>

      {/* Main Dual-Region Document Intelligence Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* =========================================================================
            LEFT REGION: ORIGINAL SOURCE VIEWER (Document Intelligence)
           ========================================================================= */}
        <div
          ref={sourceContainerRef}
          className={`bg-white border border-[#E1E7EE] rounded-2xl shadow-xs overflow-hidden flex flex-col transition-all duration-300 ${
            mobileTab === 'source' ? 'block' : 'hidden lg:flex'
          } ${
            isSourceExpanded
              ? 'lg:col-span-12'
              : structuredNotice
              ? 'lg:col-span-5'
              : 'lg:col-span-6'
          }`}
        >
          {/* Source Document Header & Metadata */}
          <div className="p-4 border-b border-[#E1E7EE] bg-[#F8FAFC] space-y-3">
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 truncate">
                <FileText className="w-4 h-4 text-[#08785D] shrink-0" />
                <span className="text-xs font-bold text-[#12233D] truncate">
                  {structuredNotice?.notice_reference_number?.value ||
                    structuredNotice?.issuing_authority?.value ||
                    'Official Notice Ground Truth'}
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => setIsSourceExpanded(!isSourceExpanded)}
                  title={isSourceExpanded ? 'Split View' : 'Expand Source Panel'}
                  className="p-1.5 rounded-lg text-[#526176] hover:text-[#12233D] hover:bg-slate-200 transition cursor-pointer"
                >
                  {isSourceExpanded ? (
                    <Minimize2 className="w-3.5 h-3.5" />
                  ) : (
                    <Maximize2 className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            </div>

            {/* Document Metadata Badges */}
            <div className="flex flex-wrap items-center gap-2 text-[11px] text-[#526176]">
              <span className="font-mono bg-white px-2 py-0.5 rounded-md border border-[#E1E7EE]">
                {charCount} chars • {wordCount} words • {lineCount} lines
              </span>
              {ocrResult && (
                <span
                  className={`font-mono px-2 py-0.5 rounded-md border ${
                    ocrResult.confidence_score >= 80
                      ? 'bg-[#E8F7F0] text-[#08785D] border-[#B7E7D2]'
                      : 'bg-[#FFF4D6] text-[#92500A] border-[#FDE68A]'
                  }`}
                >
                  OCR: {ocrResult.confidence_score.toFixed(0)}% confidence
                </span>
              )}
            </div>

            {/* Reading Controls Toolbar: Search, Zoom, Copy */}
            <div className="flex items-center justify-between gap-2 pt-1 border-t border-[#E1E7EE]">
              {/* Search Inside Source */}
              <div className="relative flex-1">
                <Search className="w-3.5 h-3.5 text-[#68778B] absolute left-2.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search in source..."
                  className="w-full pl-8 pr-16 py-1.5 rounded-lg text-xs bg-white border border-[#CBD5E1] text-[#12233D] placeholder-[#68778B] focus:border-[#08785D] focus:outline-hidden"
                />
                {searchQuery && (
                  <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                    <span className="text-[10px] font-mono text-[#526176]">
                      {searchMatchesCount}
                    </span>
                    <button
                      type="button"
                      onClick={() => setSearchQuery('')}
                      className="p-0.5 text-[#68778B] hover:text-[#12233D]"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                )}
              </div>

              {/* Font Size Zoom Controls */}
              <div className="flex items-center bg-white border border-[#CBD5E1] rounded-lg p-0.5 shrink-0">
                <button
                  type="button"
                  onClick={() => setFontSizeLevel((prev) => (prev > 1 ? ((prev - 1) as any) : 1))}
                  title="Decrease font size"
                  className="p-1 text-[#526176] hover:text-[#12233D] hover:bg-slate-100 rounded cursor-pointer"
                >
                  <ZoomOut className="w-3.5 h-3.5" />
                </button>
                <span className="text-[10px] font-mono px-1.5 text-[#526176]">
                  {fontSizeLevel === 1 ? '12px' : fontSizeLevel === 2 ? '14px' : '16px'}
                </span>
                <button
                  type="button"
                  onClick={() => setFontSizeLevel((prev) => (prev < 3 ? ((prev + 1) as any) : 3))}
                  title="Increase font size"
                  className="p-1 text-[#526176] hover:text-[#12233D] hover:bg-slate-100 rounded cursor-pointer"
                >
                  <ZoomIn className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Copy Source Button */}
              <button
                type="button"
                onClick={handleCopySource}
                title="Copy full source text"
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-[#12233D] bg-white border border-[#CBD5E1] hover:bg-slate-100 transition shrink-0 cursor-pointer"
              >
                {hasCopied ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-[#08785D]" />
                    <span className="text-[#08785D]">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 text-[#68778B]" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* OCR Limitation Warning */}
          {ocrResult && ocrResult.confidence_score < 75 && (
            <div className="p-3 bg-[#FFF4D6] border-b border-[#FDE68A] flex items-start gap-2 text-xs text-[#92500A]">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>
                Low OCR confidence detected ({ocrResult.confidence_score.toFixed(0)}%). Some table borders or Hindi characters may be misrecognized. Please compare against original paper circular.
              </span>
            </div>
          )}

          {/* Source Document Text with Line Numbers */}
          <div className="p-4 max-h-[720px] overflow-y-auto font-mono text-[#12233D] leading-relaxed bg-[#FFFFFF]">
            {lines.length === 0 ? (
              <div className="py-12 text-center text-[#68778B] text-xs font-sans space-y-2">
                <p>No document loaded in ground-truth buffer.</p>
                <button
                  type="button"
                  onClick={() => setIsIngestionDrawerOpen(true)}
                  className="text-[#08785D] font-bold hover:underline"
                >
                  Click here to upload or paste a notice
                </button>
              </div>
            ) : (
              <div className="space-y-0.5">
                {lines.map((lineText, idx) => {
                  const lineNum = idx + 1;
                  const isHighlighted =
                    highlightedSnippet &&
                    lineText.toLowerCase().includes(highlightedSnippet.toLowerCase().trim());

                  const isSearchMatch =
                    searchQuery.trim() &&
                    lineText.toLowerCase().includes(searchQuery.toLowerCase().trim());

                  return (
                    <div
                      key={lineNum}
                      className={`flex items-start rounded-xs transition-colors py-0.5 px-1 ${
                        isHighlighted
                          ? 'bg-[#E8F7F0] border-l-2 border-[#08785D]'
                          : isSearchMatch
                          ? 'bg-[#FEF08A]/40'
                          : 'hover:bg-[#F8FAFC]'
                      }`}
                    >
                      {/* Line Number Gutter */}
                      <span className="w-10 shrink-0 text-right pr-3 select-none text-[11px] text-[#94A3B8] font-sans">
                        {lineNum}
                      </span>

                      {/* Line Content */}
                      <span
                        className={`flex-1 break-words whitespace-pre-wrap ${fontSizeClass} ${
                          isHighlighted ? 'font-semibold text-[#08785D]' : 'text-[#12233D]'
                        }`}
                      >
                        {searchQuery.trim() && isSearchMatch ? (
                          <span>
                            {lineText.split(new RegExp(`(${searchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')).map((part, pIdx) =>
                              part.toLowerCase() === searchQuery.toLowerCase() ? (
                                <mark
                                  key={pIdx}
                                  className="bg-amber-200 text-[#12233D] rounded-xs px-0.5"
                                >
                                  {part}
                                </mark>
                              ) : (
                                part
                              )
                            )}
                          </span>
                        ) : (
                          lineText || '\u00A0'
                        )}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* =========================================================================
            RIGHT REGION: NOTICE ANALYSIS WORKSPACE
           ========================================================================= */}
        <div
          className={`space-y-4 ${
            mobileTab === 'analysis' ? 'block' : 'hidden lg:block'
          } ${
            isSourceExpanded
              ? 'hidden'
              : structuredNotice
              ? 'lg:col-span-7'
              : 'lg:col-span-6'
          }`}
        >
          {/* Analysis Section Tabs Navigation */}
          <div className="bg-white border border-[#E1E7EE] rounded-2xl shadow-xs overflow-hidden">
            <div className="flex items-center overflow-x-auto no-scrollbar border-b border-[#E1E7EE] bg-[#F8FAFC] p-1.5 gap-1">
              <button
                type="button"
                onClick={() => setActiveAnalysisTab('overview')}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition whitespace-nowrap cursor-pointer ${
                  activeAnalysisTab === 'overview'
                    ? 'bg-[#08785D] text-white shadow-xs'
                    : 'text-[#526176] hover:bg-white hover:text-[#12233D]'
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Overview</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveAnalysisTab('facts')}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition whitespace-nowrap cursor-pointer ${
                  activeAnalysisTab === 'facts'
                    ? 'bg-[#08785D] text-white shadow-xs'
                    : 'text-[#526176] hover:bg-white hover:text-[#12233D]'
                }`}
              >
                <CheckSquare className="w-3.5 h-3.5" />
                <span>Key Facts</span>
                {structuredNotice && (
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-white/20 text-inherit">
                    8
                  </span>
                )}
              </button>

              <button
                type="button"
                onClick={() => setActiveAnalysisTab('eligibility')}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition whitespace-nowrap cursor-pointer ${
                  activeAnalysisTab === 'eligibility'
                    ? 'bg-[#08785D] text-white shadow-xs'
                    : 'text-[#526176] hover:bg-white hover:text-[#12233D]'
                }`}
              >
                <UserCheck className="w-3.5 h-3.5" />
                <span>Eligibility</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveAnalysisTab('evidence')}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition whitespace-nowrap cursor-pointer ${
                  activeAnalysisTab === 'evidence'
                    ? 'bg-[#08785D] text-white shadow-xs'
                    : 'text-[#526176] hover:bg-white hover:text-[#12233D]'
                }`}
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Evidence</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveAnalysisTab('actions')}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition whitespace-nowrap cursor-pointer ${
                  activeAnalysisTab === 'actions'
                    ? 'bg-[#08785D] text-white shadow-xs'
                    : 'text-[#526176] hover:bg-white hover:text-[#12233D]'
                }`}
              >
                <ListTodo className="w-3.5 h-3.5" />
                <span>Action Plan</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveAnalysisTab('qa')}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition whitespace-nowrap cursor-pointer ${
                  activeAnalysisTab === 'qa'
                    ? 'bg-[#08785D] text-white shadow-xs'
                    : 'text-[#526176] hover:bg-white hover:text-[#12233D]'
                }`}
              >
                <MessageSquare className="w-3.5 h-3.5" />
                <span>Ask Q&A</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveAnalysisTab('changes')}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition whitespace-nowrap cursor-pointer ${
                  activeAnalysisTab === 'changes'
                    ? 'bg-[#08785D] text-white shadow-xs'
                    : 'text-[#526176] hover:bg-white hover:text-[#12233D]'
                }`}
              >
                <GitCompare className="w-3.5 h-3.5" />
                <span>Related Changes</span>
              </button>
            </div>

            {/* TAB CONTENTS CONTAINER */}
            <div className="p-5">
              {!structuredNotice ? (
                /* Unanalyzed Ready State */
                <div className="py-12 px-4 text-center space-y-4">
                  <div className="w-12 h-12 rounded-xl bg-[#E8F7F0] border border-[#B7E7D2] text-[#08785D] flex items-center justify-center mx-auto">
                    <Sparkles className="w-6 h-6" />
                  </div>
                  <h3 className="text-base font-bold text-[#12233D]">
                    Notice Ready for Gemma 4 Grounding
                  </h3>
                  <p className="text-xs text-[#526176] max-w-md mx-auto leading-relaxed">
                    Click <strong>"Analyze with Local Gemma 4"</strong> in the top header to extract
                    the 8 procedural dimensions, verify exact verbatim quotes, and evaluate citizen action steps.
                  </p>
                  <button
                    type="button"
                    onClick={runAnalysis}
                    disabled={!rawNoticeText.trim() || isAnalyzing}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-xs text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs disabled:opacity-50 cursor-pointer"
                  >
                    <Play className="w-3.5 h-3.5 fill-white" />
                    <span>Run Local AI Analysis</span>
                  </button>
                </div>
              ) : (
                /* Analyzed Structured View */
                <div>
                  {/* TAB 1: OVERVIEW */}
                  {activeAnalysisTab === 'overview' && (
                    <div className="space-y-5 animate-in fade-in duration-150">
                      {/* Metric Cards Row */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <MetricCard
                          fact={structuredNotice.purpose}
                          label="Purpose & Benefit"
                          iconType="purpose"
                        />
                        <MetricCard
                          fact={structuredNotice.deadline}
                          label="Closing Deadline"
                          iconType="deadline"
                        />
                        <MetricCard
                          fact={structuredNotice.eligibility}
                          label="Eligibility Rules"
                          iconType="eligibility"
                        />
                        <MetricCard
                          fact={structuredNotice.required_actions}
                          label="Required Actions"
                          iconType="actions"
                        />
                      </div>

                      {/* Document Identity Card */}
                      <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-3">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-[#526176] block">
                          Official Notice Metadata
                        </span>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                          <div className="flex items-start gap-2">
                            <Building2 className="w-4 h-4 text-[#08785D] shrink-0 mt-0.5" />
                            <div>
                              <span className="text-[10px] uppercase font-bold text-[#68778B] block">
                                Issuing Authority
                              </span>
                              <span className="font-semibold text-[#12233D]">
                                {structuredNotice.issuing_authority?.value || 'Official Department'}
                              </span>
                            </div>
                          </div>

                          <div className="flex items-start gap-2">
                            <Hash className="w-4 h-4 text-[#08785D] shrink-0 mt-0.5" />
                            <div>
                              <span className="text-[10px] uppercase font-bold text-[#68778B] block">
                                Reference Number
                              </span>
                              <span className="font-semibold font-mono text-[#12233D]">
                                {structuredNotice.notice_reference_number?.value || 'Not Stated'}
                              </span>
                            </div>
                          </div>

                          <div className="flex items-start gap-2">
                            <Calendar className="w-4 h-4 text-[#08785D] shrink-0 mt-0.5" />
                            <div>
                              <span className="text-[10px] uppercase font-bold text-[#68778B] block">
                                Notice Date
                              </span>
                              <span className="font-semibold text-[#12233D]">
                                {structuredNotice.notice_date?.value || 'Not Stated'}
                              </span>
                            </div>
                          </div>

                          <div className="flex items-start gap-2">
                            <Clock className="w-4 h-4 text-[#08785D] shrink-0 mt-0.5" />
                            <div>
                              <span className="text-[10px] uppercase font-bold text-[#68778B] block">
                                Application Deadline
                              </span>
                              <span className="font-semibold text-[#B42318]">
                                {structuredNotice.deadline?.value || 'Not Stated'}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Plain Language Summary */}
                      {currentSummary && (
                        <div className="p-4 rounded-xl bg-white border border-[#E1E7EE] space-y-3.5 shadow-xs">
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-[#E1E7EE]">
                            <div className="flex items-center gap-2">
                              <Sparkles className="w-4 h-4 text-[#08785D]" />
                              <h3 className="text-xs font-bold text-[#12233D] uppercase tracking-wider">
                                Plain Language Summary
                              </h3>
                            </div>

                            {/* Controls: Language, Reading Level, Read Aloud */}
                            <div className="flex items-center gap-2">
                              <div className="flex items-center bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg p-0.5 text-[11px]">
                                <button
                                  type="button"
                                  onClick={() => setSelectedLang('en')}
                                  className={`px-2 py-0.5 rounded font-bold transition cursor-pointer ${
                                    selectedLang === 'en'
                                      ? 'bg-white text-[#08785D] shadow-xs'
                                      : 'text-[#526176]'
                                  }`}
                                >
                                  English
                                </button>
                                <button
                                  type="button"
                                  onClick={() => setSelectedLang('hi')}
                                  className={`px-2 py-0.5 rounded font-bold transition cursor-pointer ${
                                    selectedLang === 'hi'
                                      ? 'bg-white text-[#08785D] shadow-xs'
                                      : 'text-[#526176]'
                                  }`}
                                >
                                  हिंदी
                                </button>
                              </div>

                              <div className="flex items-center bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg p-0.5 text-[11px]">
                                {(['simple', 'standard', 'detailed'] as const).map((level) => (
                                  <button
                                    key={level}
                                    type="button"
                                    onClick={() => changeReadingLevel(level)}
                                    className={`px-2 py-0.5 rounded capitalize font-medium transition cursor-pointer ${
                                      readingLevel === level
                                        ? 'bg-white text-[#08785D] font-bold shadow-xs'
                                        : 'text-[#526176]'
                                    }`}
                                  >
                                    {level}
                                  </button>
                                ))}
                              </div>

                              <button
                                type="button"
                                onClick={() =>
                                  speakText(
                                    `${currentSummary.about}. ${currentSummary.eligible}. ${currentSummary.actions}`,
                                    selectedLang
                                  )
                                }
                                title="Read summary aloud"
                                className="p-1.5 rounded-lg text-[#526176] hover:text-[#08785D] hover:bg-[#E8F7F0] transition cursor-pointer"
                              >
                                <Volume2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </div>

                          <div className="space-y-2 text-xs text-[#12233D] leading-relaxed">
                            <p>
                              <strong>What this is about:</strong> {currentSummary.about}
                            </p>
                            <p>
                              <strong>Who is eligible:</strong> {currentSummary.eligible}
                            </p>
                            <p>
                              <strong>What you must do:</strong> {currentSummary.actions}
                            </p>
                            {currentSummary.documents && (
                              <p>
                                <strong>Documents needed:</strong> {currentSummary.documents}
                              </p>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Limitations and Missing Information Disclosure */}
                      {structuredNotice.missing_information &&
                        structuredNotice.missing_information.length > 0 && (
                          <div className="p-3.5 rounded-xl bg-[#FFF4D6] border border-[#FDE68A] text-xs text-[#92500A] space-y-2">
                            <div className="flex items-center gap-1.5 font-bold">
                              <HelpCircle className="w-4 h-4 text-[#92500A]" />
                              <span>Missing Information / Limitations in Circular</span>
                            </div>
                            <ul className="list-disc list-inside space-y-1 text-[11px] opacity-90 pl-1">
                              {structuredNotice.missing_information.map((item, idx) => (
                                <li key={idx}>{item}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                    </div>
                  )}

                  {/* TAB 2: KEY FACTS */}
                  {activeAnalysisTab === 'facts' && (
                    <div className="space-y-4 animate-in fade-in duration-150">
                      <div className="flex items-center justify-between pb-2 border-b border-[#E1E7EE]">
                        <div>
                          <h3 className="text-sm font-bold text-[#12233D]">
                            Mandatory Structured Dimensions & Grounded Facts
                          </h3>
                          <p className="text-xs text-[#526176]">
                            Gemma 4 extracted values with exact citation references.
                          </p>
                        </div>
                        <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded-md bg-[#E8F7F0] text-[#08785D]">
                          100% Grounded
                        </span>
                      </div>

                      <div className="space-y-3">
                        {renderFactItem('Purpose of Notice', structuredNotice.purpose, 'Intent')}
                        {renderFactItem('Closing Deadline', structuredNotice.deadline, 'Timeline')}
                        {renderFactItem(
                          'Eligibility Criteria',
                          structuredNotice.eligibility,
                          'Qualifications'
                        )}
                        {renderFactItem(
                          'Required Actions',
                          structuredNotice.required_actions,
                          'Checklist'
                        )}
                        {renderFactItem(
                          'Required Documents',
                          structuredNotice.required_documents,
                          'Verification'
                        )}
                        {renderFactItem(
                          'Fees or Payments',
                          structuredNotice.fee_or_cost,
                          'Financial'
                        )}
                        {renderFactItem(
                          'Contact & Helpdesk',
                          structuredNotice.contact_details,
                          'Support'
                        )}
                        {renderFactItem(
                          'Important Conditions',
                          structuredNotice.important_conditions,
                          'Rules'
                        )}
                      </div>
                    </div>
                  )}

                  {/* TAB 3: ELIGIBILITY */}
                  {activeAnalysisTab === 'eligibility' && (
                    <div className="space-y-4 animate-in fade-in duration-150">
                      <div className="flex items-center justify-between pb-2 border-b border-[#E1E7EE]">
                        <div>
                          <h3 className="text-sm font-bold text-[#12233D] flex items-center gap-2">
                            <UserCheck className="w-4 h-4 text-[#08785D]" />
                            Eligibility Rules & Applicant Matching
                          </h3>
                          <p className="text-xs text-[#526176]">
                            Check whether your profile satisfies the stated criteria in this circular.
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={() => setActiveTab(5)}
                          className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold text-[#08785D] bg-[#E8F7F0] hover:bg-[#D1F0E2] transition cursor-pointer"
                        >
                          <span>Full Engine</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      <div className="p-4 rounded-xl bg-white border border-[#E1E7EE] space-y-3 shadow-xs">
                        <span className="text-xs font-bold text-[#12233D] block">
                          Stated Eligibility Criteria
                        </span>
                        <p className="text-xs text-[#12233D] leading-relaxed">
                          {structuredNotice.eligibility?.value ||
                            'No specific eligibility conditions explicitly declared.'}
                        </p>
                        {structuredNotice.eligibility?.evidence_quote && (
                          <div className="p-3 rounded-lg bg-[#F8FAFC] border-l-3 border-[#08785D] text-xs text-[#526176] font-mono italic">
                            "{structuredNotice.eligibility.evidence_quote}"
                          </div>
                        )}
                      </div>

                      <div className="p-4 rounded-xl bg-[#EAF2FF] border border-[#BFDBFE] flex items-start gap-3">
                        <Info className="w-4 h-4 text-[#245DC1] shrink-0 mt-0.5" />
                        <div className="text-xs text-[#245DC1] space-y-1">
                          <span className="font-bold">Applicant Profile Evaluation</span>
                          <p className="text-[11px] opacity-90">
                            Configure your degree, category (General/OBC/SC/ST/EWS), and percentage in
                            the <strong>Eligibility Check</strong> module for an automated pass/fail assessment.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* TAB 4: EVIDENCE */}
                  {activeAnalysisTab === 'evidence' && (
                    <div className="space-y-4 animate-in fade-in duration-150">
                      <div className="flex items-center justify-between pb-2 border-b border-[#E1E7EE]">
                        <div>
                          <h3 className="text-sm font-bold text-[#12233D] flex items-center gap-2">
                            <ShieldCheck className="w-4 h-4 text-[#08785D]" />
                            Evidence Grounding Ledger
                          </h3>
                          <p className="text-xs text-[#526176]">
                            Verifiable verbatim quotations supporting all extracted claims.
                          </p>
                        </div>
                      </div>

                      <div className="space-y-3">
                        {[
                          { label: 'Purpose', fact: structuredNotice.purpose },
                          { label: 'Deadline', fact: structuredNotice.deadline },
                          { label: 'Eligibility', fact: structuredNotice.eligibility },
                          { label: 'Required Actions', fact: structuredNotice.required_actions },
                          { label: 'Documents', fact: structuredNotice.required_documents },
                          { label: 'Fees / Cost', fact: structuredNotice.fee_or_cost },
                        ]
                          .filter((item) => item.fact && item.fact.evidence_quote)
                          .map((item, idx) => (
                            <div
                              key={idx}
                              className="p-3.5 rounded-xl bg-white border border-[#E1E7EE] hover:border-[#B7E7D2] transition space-y-2 shadow-xs"
                            >
                              <div className="flex items-center justify-between">
                                <span className="text-xs font-bold text-[#12233D]">
                                  {item.label} Claim
                                </span>
                                <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]">
                                  VERIFIED
                                </span>
                              </div>
                              <p className="text-xs text-[#526176] font-mono italic p-2 rounded bg-[#F8FAFC] border-l-2 border-[#08785D]">
                                "{item.fact.evidence_quote}"
                              </p>
                              <div className="flex items-center justify-end gap-2 pt-1">
                                <button
                                  type="button"
                                  onClick={() => handleHighlightInSource(item.fact.evidence_quote!)}
                                  className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-semibold text-[#08785D] hover:bg-[#E8F7F0] transition cursor-pointer"
                                >
                                  <Search className="w-3 h-3" />
                                  <span>View in Source</span>
                                </button>
                                <button
                                  type="button"
                                  onClick={() =>
                                    openEvidenceInspector(
                                      {
                                        excerpt: item.fact.evidence_quote!,
                                        claim: item.label,
                                        docTitle: 'Notice Verification',
                                      },
                                      rawNoticeText
                                    )
                                  }
                                  className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-semibold text-[#245DC1] hover:bg-[#EAF2FF] transition cursor-pointer"
                                >
                                  <ExternalLink className="w-3 h-3" />
                                  <span>Inspect</span>
                                </button>
                              </div>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}

                  {/* TAB 5: ACTION PLAN */}
                  {activeAnalysisTab === 'actions' && (
                    <div className="space-y-4 animate-in fade-in duration-150">
                      <div className="flex items-center justify-between pb-2 border-b border-[#E1E7EE]">
                        <div>
                          <h3 className="text-sm font-bold text-[#12233D] flex items-center gap-2">
                            <ListTodo className="w-4 h-4 text-[#08785D]" />
                            Step-by-Step Action Plan & Deadlines
                          </h3>
                          <p className="text-xs text-[#526176]">
                            Interactive preparation checklist with calendar (.ics) and Markdown export.
                          </p>
                        </div>
                      </div>

                      <ActionChecklistTable />
                    </div>
                  )}

                  {/* TAB 6: ASK Q&A */}
                  {activeAnalysisTab === 'qa' && (
                    <div className="space-y-4 animate-in fade-in duration-150">
                      <div className="pb-2 border-b border-[#E1E7EE]">
                        <h3 className="text-sm font-bold text-[#12233D] flex items-center gap-2">
                          <MessageSquare className="w-4 h-4 text-[#08785D]" />
                          Ask Questions About This Notice
                        </h3>
                        <p className="text-xs text-[#526176]">
                          Answers are grounded strictly in this circular with verbatim citations.
                        </p>
                      </div>

                      <GroundedQAChat />
                    </div>
                  )}

                  {/* TAB 7: RELATED CHANGES */}
                  {activeAnalysisTab === 'changes' && (
                    <div className="space-y-4 animate-in fade-in duration-150">
                      <div className="flex items-center justify-between pb-2 border-b border-[#E1E7EE]">
                        <div>
                          <h3 className="text-sm font-bold text-[#12233D] flex items-center gap-2">
                            <GitCompare className="w-4 h-4 text-[#08785D]" />
                            Multi-Notice Revision & Amendment Tracking
                          </h3>
                          <p className="text-xs text-[#526176]">
                            Track changes, deadline extensions, and fee modifications between circular revisions.
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={() => setActiveTab(4)}
                          className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold text-[#08785D] bg-[#E8F7F0] hover:bg-[#D1F0E2] transition cursor-pointer"
                        >
                          <span>Open Revision Ledger</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      <div className="p-4 rounded-xl bg-white border border-[#E1E7EE] space-y-3 shadow-xs">
                        <span className="text-xs font-bold text-[#12233D] block">
                          Revision Intelligence Overview
                        </span>
                        <p className="text-xs text-[#526176] leading-relaxed">
                          When government departments publish corrigendums or subsequent notices,
                          SuchnaSetu AI performs field-by-field delta comparison to highlight modified
                          dates, added criteria, and personal impacts on applicant qualifications.
                        </p>
                        <div className="pt-2">
                          <button
                            type="button"
                            onClick={() => setActiveTab(4)}
                            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs cursor-pointer"
                          >
                            <GitCompare className="w-3.5 h-3.5" />
                            <span>Launch Corrigendum Comparison</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
