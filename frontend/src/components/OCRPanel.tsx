import React, { useState, useEffect } from 'react';
import { useNotice } from '../context/NoticeContext';
import { apiClient } from '../services/apiClient';
import { useTranslation } from '../i18n';
import {
  Eye,
  RefreshCw,
  Trash2,
  AlertTriangle,
  ShieldCheck,
  Compass,
  FileCheck,
  CheckCircle2,
  Check,
  Save,
  Languages,
  Sparkles,
  ChevronDown,
  ChevronUp,
  XCircle,
  ExternalLink,
} from 'lucide-react';
import type { HumanReviewItem } from '../types/api';

export const OCRPanel: React.FC = () => {
  const {
    uploadedImage,
    uploadedFile,
    setUploadedImage,
    setRawNoticeText,
    setOcrResult,
    ocrResult,
    openReviewHighlight,
    reviewSummary,
    updateReviewItem,
    applyReviewCorrections,
    detectedLangMeta,
    documentId,
  } = useNotice();
  const { t } = useTranslation();

  const [ocrLang, setOcrLang] = useState<string>('auto');
  const [isManualOverride, setIsManualOverride] = useState<boolean>(false);
  const [enhanceContrast, setEnhanceContrast] = useState<boolean>(true);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [isApplyingCorrections, setIsApplyingCorrections] = useState<boolean>(false);
  const [applySuccessMessage, setApplySuccessMessage] = useState<string | null>(null);
  const [ocrError, setOcrError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'repaired' | 'raw'>('repaired');
  const [cooldownSec, setCooldownSec] = useState<number>(0);
  const [isReviewOpen, setIsReviewOpen] = useState<boolean>(true);
  const [reviewFilter, setReviewFilter] = useState<'all' | 'pending' | 'corrected' | 'verified' | 'ignored'>('all');
  const [draftEdits, setDraftEdits] = useState<Record<string, string>>({});

  useEffect(() => {
    if (cooldownSec <= 0) return;
    const timer = setInterval(() => {
      setCooldownSec((prev) => (prev <= 1 ? 0 : prev - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, [cooldownSec]);

  if (!uploadedImage) return null;

  const handleRunOCR = async () => {
    if (isProcessing || cooldownSec > 0) return;
    setIsProcessing(true);
    setOcrError(null);
    setApplySuccessMessage(null);

    try {
      let fileToUpload = uploadedFile;
      if (!fileToUpload) {
        const blob = await fetch(uploadedImage).then((r) => r.blob());
        fileToUpload = new File([blob], 'notice_preview.png', { type: blob.type || 'image/png' });
      }

      const res = await apiClient.runOCR(
        fileToUpload,
        fileToUpload.name,
        ocrLang,
        enhanceContrast,
        documentId || undefined
      );

      if (res.error) {
        setOcrError(res.error);
      } else {
        setRawNoticeText(res.extracted_text);
        setOcrResult(res);
        setViewMode('repaired');
      }
    } catch (err: any) {
      if (err.status === 429 || /rate limit|quota/i.test(err.message || '')) {
        setOcrError(err.message || t('error'));
        setCooldownSec(15);
      } else {
        setOcrError(err.message || 'OCR processing failed. Check connection or document.');
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const handleToggleViewMode = (mode: 'repaired' | 'raw') => {
    setViewMode(mode);
    if (!ocrResult) return;
    if (mode === 'raw' && ocrResult.raw_ocr_text) {
      setRawNoticeText(ocrResult.raw_ocr_text);
    } else if (mode === 'repaired') {
      setRawNoticeText(ocrResult.extracted_text);
    }
  };

  const handleResetImage = () => {
    setUploadedImage(null, null);
    setOcrResult(null);
  };

  const handleLanguageChange = (newLang: string) => {
    setOcrLang(newLang);
    setIsManualOverride(newLang !== 'auto');
  };

  const handleResetToAuto = () => {
    setOcrLang('auto');
    setIsManualOverride(false);
  };

  const handleDraftChange = (itemId: string, text: string) => {
    setDraftEdits((prev) => ({ ...prev, [itemId]: text }));
  };

  const handleSaveCorrection = async (item: HumanReviewItem) => {
    const textToSave = draftEdits[item.id] !== undefined ? draftEdits[item.id] : item.corrected_text || item.original_text;
    try {
      await updateReviewItem(item.id, 'corrected', textToSave);
    } catch (e: any) {
      setOcrError(`Failed to save correction: ${e.message}`);
    }
  };

  const handleVerifyItem = async (item: HumanReviewItem) => {
    try {
      await updateReviewItem(item.id, 'verified');
    } catch (e: any) {
      setOcrError(`Failed to verify item: ${e.message}`);
    }
  };

  const handleIgnoreItem = async (item: HumanReviewItem) => {
    try {
      await updateReviewItem(item.id, 'ignored');
    } catch (e: any) {
      setOcrError(`Failed to ignore item: ${e.message}`);
    }
  };

  const handleApplyAllCorrections = async () => {
    if (isApplyingCorrections) return;
    setIsApplyingCorrections(true);
    setApplySuccessMessage(null);
    try {
      await applyReviewCorrections();
      setApplySuccessMessage('All reviewed corrections applied to canonical document text.');
      setTimeout(() => setApplySuccessMessage(null), 4000);
    } catch (e: any) {
      setOcrError(`Failed to apply corrections: ${e.message}`);
    } finally {
      setIsApplyingCorrections(false);
    }
  };

  const qualityScore = ocrResult?.document_quality_score ?? ocrResult?.confidence_score ?? 0;
  const isHighQuality = qualityScore >= 80;
  const isModerateQuality = qualityScore >= 65 && qualityScore < 80;

  // Review items source: DB review summary or fallback to OCR uncertain spans
  const activeReviewItems: HumanReviewItem[] = reviewSummary?.items || (
    ocrResult?.uncertain_spans ? ocrResult.uncertain_spans.map((s, idx) => ({
      id: s.id || `span_${idx}`,
      document_id: documentId || 'temp',
      page_number: s.page_number || 1,
      box: s.box,
      original_text: s.original_text || s.text,
      corrected_text: s.corrected_text,
      confidence: s.confidence,
      reason: s.reason || 'Uncertain token',
      status: (s.status as any) || 'pending',
      created_at: '',
    })) : []
  );

  const filteredItems = activeReviewItems.filter((item) => {
    if (reviewFilter === 'all') return true;
    return item.status === reviewFilter;
  });

  const pendingCount = reviewSummary?.pending ?? activeReviewItems.filter(i => i.status === 'pending').length;
  const correctedCount = reviewSummary?.corrected ?? activeReviewItems.filter(i => i.status === 'corrected').length;
  const verifiedCount = reviewSummary?.verified ?? activeReviewItems.filter(i => i.status === 'verified').length;
  const ignoredCount = reviewSummary?.ignored ?? activeReviewItems.filter(i => i.status === 'ignored').length;
  const totalReviewItems = reviewSummary?.total ?? activeReviewItems.length;

  const detectedLang = ocrResult?.detected_language || detectedLangMeta?.detected_language;
  const detectedConfidence = ocrResult?.language_confidence ?? detectedLangMeta?.confidence ?? 1.0;
  const isMixed = ocrResult?.is_mixed_language ?? detectedLangMeta?.is_mixed ?? false;

  const getLanguageLabel = (code?: string) => {
    switch (code) {
      case 'en':
      case 'eng':
        return 'English (eng)';
      case 'hi':
      case 'hin':
        return 'Hindi (hin)';
      case 'hin+eng':
      case 'en+hi':
        return 'Bilingual (Hindi + English)';
      case 'mr':
        return 'Marathi (mr)';
      default:
        return code ? code.toUpperCase() : 'Unknown';
    }
  };

  return (
    <div className="bg-white border border-[#E1E7EE] rounded-xl p-5 space-y-4 shadow-xs">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-[#12233D] flex items-center gap-1.5">
          <Eye className="w-4 h-4 text-[#08785D]" />
          {t('imagePreview')}
        </span>
        {ocrResult && (
          <div className="flex items-center gap-1.5 flex-wrap">
            <span
              className={`flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-md border ${
                isHighQuality
                  ? 'text-[#08785D] bg-[#E8F7F0] border-[#B7E7D2]'
                  : isModerateQuality
                  ? 'text-[#B54708] bg-[#FFFAEB] border-[#FEDF89]'
                  : 'text-[#B42318] bg-[#FEE8E7] border-[#FCA5A5]'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              {t('qualityScore')}: {qualityScore.toFixed(1)}% {isHighQuality ? t('qualityHigh') : isModerateQuality ? t('qualityModerate') : t('qualityUncertain')}
            </span>
          </div>
        )}
      </div>

      {/* Image container */}
      <div className="relative max-h-56 overflow-hidden rounded-xl border border-[#E1E7EE] bg-[#F8FAFC] flex items-center justify-center p-2">
        <img
          src={uploadedImage}
          alt={t('imagePreview')}
          className="max-h-52 w-auto object-contain rounded-lg shadow-xs"
        />
      </div>

      {/* Alignment / Deskew indicator badges */}
      {ocrResult && (ocrResult.deskew_angle || ocrResult.orientation_applied) ? (
        <div className="flex items-center gap-2 text-[11px] text-[#526176] bg-[#F8FAFC] px-3 py-1.5 rounded-lg border border-[#E1E7EE]">
          <Compass className="w-3.5 h-3.5 text-[#08785D]" />
          {ocrResult.orientation_applied ? <span>{t('rotation')}: {ocrResult.orientation_applied}°</span> : null}
          {ocrResult.deskew_angle ? <span>{t('deskew')}: {ocrResult.deskew_angle > 0 ? `+${ocrResult.deskew_angle}` : ocrResult.deskew_angle}°</span> : null}
        </div>
      ) : null}

      {/* OCR Controls & Auto-Language Detection */}
      <div className="space-y-2 pt-1">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="text-[11px] font-bold text-[#526176] uppercase tracking-wide flex items-center justify-between mb-1">
              <span className="flex items-center gap-1">
                <Languages className="w-3.5 h-3.5 text-[#08785D]" />
                {t('ocrLanguagePack')}
              </span>
              {isManualOverride && (
                <button
                  type="button"
                  onClick={handleResetToAuto}
                  className="text-[10px] text-[#08785D] hover:underline font-semibold cursor-pointer"
                >
                  Reset to Auto
                </button>
              )}
            </label>
            <select
              value={ocrLang}
              onChange={(e) => handleLanguageChange(e.target.value)}
              className="w-full bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg px-3 py-1.5 text-xs text-[#12233D] focus:border-[#08785D] focus:outline-hidden font-medium"
            >
              <option value="auto">Auto-Detect Language (Recommended)</option>
              <option value="eng">English (eng)</option>
              <option value="hin">Hindi (hin)</option>
              <option value="hin+eng">Bilingual (Hindi + English - Hybrid Fusion)</option>
              <option value="mr">Marathi (mr)</option>
            </select>
          </div>

          <div className="flex items-end pb-1.5">
            <label className="flex items-center gap-2 text-xs font-medium text-[#12233D] cursor-pointer">
              <input
                type="checkbox"
                checked={enhanceContrast}
                onChange={(e) => setEnhanceContrast(e.target.checked)}
                className="rounded border-[#CBD5E1] text-[#08785D] focus:ring-[#08785D]"
              />
              <span>{t('adaptiveContrast')}</span>
            </label>
          </div>
        </div>

        {/* Detected Language Indicator Banner */}
        {detectedLang && (
          <div className="flex items-center justify-between px-3 py-1.5 bg-[#E8F7F0]/60 border border-[#B7E7D2] rounded-lg text-xs text-[#08785D]">
            <div className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-[#08785D] shrink-0" />
              <span className="font-semibold">
                Detected: <span className="font-bold">{getLanguageLabel(detectedLang)}</span>
                {isMixed && ' (Mixed Hindi+English)'}
              </span>
              <span className="text-[10px] bg-white/80 border border-[#B7E7D2] px-1.5 py-0.5 rounded font-mono font-bold">
                {(detectedConfidence * 100).toFixed(0)}% confidence
              </span>
            </div>
            {isManualOverride ? (
              <span className="text-[10px] font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                Manual Override Active: {ocrLang}
              </span>
            ) : (
              <span className="text-[10px] font-semibold text-[#08785D]">
                Auto-Selected for OCR
              </span>
            )}
          </div>
        )}
      </div>

      {/* Switcher between Repaired and Raw OCR */}
      {ocrResult && ocrResult.raw_ocr_text && (
        <div className="flex items-center justify-between p-2.5 bg-[#F8FAFC] border border-[#E1E7EE] rounded-lg text-xs">
          <span className="font-semibold text-[#12233D] flex items-center gap-1.5">
            <FileCheck className="w-3.5 h-3.5 text-[#08785D]" />
            {t('viewingBufferMode')}
          </span>
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => handleToggleViewMode('repaired')}
              className={`px-2.5 py-1 rounded-md text-xs font-bold transition cursor-pointer ${
                viewMode === 'repaired'
                  ? 'bg-[#08785D] text-white shadow-2xs'
                  : 'bg-white border border-[#CBD5E1] text-[#526176] hover:bg-slate-50'
              }`}
            >
              {t('repairedText')}
            </button>
            <button
              type="button"
              onClick={() => handleToggleViewMode('raw')}
              className={`px-2.5 py-1 rounded-md text-xs font-bold transition cursor-pointer ${
                viewMode === 'raw'
                  ? 'bg-[#08785D] text-white shadow-2xs'
                  : 'bg-white border border-[#CBD5E1] text-[#526176] hover:bg-slate-50'
              }`}
            >
              {t('rawOcr')}
            </button>
          </div>
        </div>
      )}

      {/* Verified Critical Fields Card */}
      {ocrResult && ocrResult.critical_fields && Object.keys(ocrResult.critical_fields).length > 0 && (
        <div className="bg-[#F8FAFC] border border-[#CBD5E1] rounded-xl p-3.5 space-y-2.5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 font-bold text-xs text-[#12233D]">
              <CheckCircle2 className="w-4 h-4 text-[#08785D]" />
              <span>Verified Statutory Fields</span>
              {ocrResult.field_accuracy_score != null && (
                <span className="ml-1 text-[10px] font-semibold bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2] px-2 py-0.5 rounded-full">
                  {ocrResult.field_accuracy_score.toFixed(0)}% accuracy
                </span>
              )}
            </div>
            <span className="text-[10px] text-[#526176] font-medium">
              {Object.keys(ocrResult.critical_fields).length} fields detected
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-48 overflow-y-auto pr-1 text-xs">
            {Object.entries(ocrResult.critical_fields).map(([key, item]: [string, any]) => {
              const label = key
                .replace(/_/g, ' ')
                .replace(/\b\w/g, (c) => c.toUpperCase());
              return (
                <div
                  key={key}
                  onClick={() => openReviewHighlight(key, label, null, item.value)}
                  className="bg-white p-2 rounded-lg border border-[#E1E7EE] hover:border-[#B7E7D2] flex flex-col justify-between cursor-pointer transition group"
                  title="Click to view and highlight in original notice"
                >
                  <div className="flex items-center justify-between text-[10px] text-[#526176] mb-1">
                    <span className="font-semibold truncate max-w-[140px] group-hover:text-[#08785D]">{label}</span>
                    <span
                      className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                        item.status === 'verified'
                          ? 'bg-[#E8F7F0] text-[#08785D]'
                          : 'bg-[#FFFAEB] text-[#B54708]'
                      }`}
                    >
                      {item.confidence ? `${item.confidence.toFixed(0)}%` : 'verified'}
                    </span>
                  </div>
                  <div className="text-xs font-medium text-[#12233D] select-all break-words">
                    {item.value}
                  </div>
                  {item.source && (
                    <div className="text-[9px] text-[#94A3B8] mt-1 italic">
                      via {item.source.replace(/_/g, ' ')}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* PERSISTENT HUMAN REVIEW DRAWER */}
      {totalReviewItems > 0 && (
        <div className="bg-white border border-[#CBD5E1] rounded-xl overflow-hidden shadow-xs transition-all">
          {/* Header */}
          <div
            onClick={() => setIsReviewOpen(!isReviewOpen)}
            className="flex items-center justify-between p-3.5 bg-gradient-to-r from-amber-50/80 to-slate-50 border-b border-[#E1E7EE] cursor-pointer hover:bg-amber-50 transition"
          >
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <span className="font-bold text-xs text-[#12233D]">
                Human Review Workspace ({totalReviewItems} items)
              </span>
              <div className="flex items-center gap-1 ml-2">
                {pendingCount > 0 && (
                  <span className="text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300 px-1.5 py-0.5 rounded-full">
                    {pendingCount} Pending
                  </span>
                )}
                {correctedCount > 0 && (
                  <span className="text-[10px] font-bold bg-blue-100 text-blue-900 border border-blue-300 px-1.5 py-0.5 rounded-full">
                    {correctedCount} Corrected
                  </span>
                )}
                {verifiedCount > 0 && (
                  <span className="text-[10px] font-bold bg-emerald-100 text-emerald-900 border border-emerald-300 px-1.5 py-0.5 rounded-full">
                    {verifiedCount} Verified
                  </span>
                )}
                {ignoredCount > 0 && (
                  <span className="text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-300 px-1.5 py-0.5 rounded-full">
                    {ignoredCount} Ignored
                  </span>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {isReviewOpen ? (
                <ChevronUp className="w-4 h-4 text-[#526176]" />
              ) : (
                <ChevronDown className="w-4 h-4 text-[#526176]" />
              )}
            </div>
          </div>

          {isReviewOpen && (
            <div className="p-3.5 space-y-3">
              {/* Filter Tabs & Apply Button */}
              <div className="flex items-center justify-between flex-wrap gap-2 border-b border-[#E1E7EE] pb-2.5">
                <div className="flex items-center gap-1">
                  {(['all', 'pending', 'corrected', 'verified', 'ignored'] as const).map((filter) => (
                    <button
                      key={filter}
                      type="button"
                      onClick={() => setReviewFilter(filter)}
                      className={`px-2.5 py-1 rounded-md text-[11px] font-bold capitalize transition cursor-pointer ${
                        reviewFilter === filter
                          ? 'bg-[#12233D] text-white shadow-2xs'
                          : 'bg-[#F8FAFC] text-[#526176] hover:bg-slate-100 border border-[#E1E7EE]'
                      }`}
                    >
                      {filter}
                      {filter === 'all' && ` (${totalReviewItems})`}
                      {filter === 'pending' && ` (${pendingCount})`}
                      {filter === 'corrected' && ` (${correctedCount})`}
                      {filter === 'verified' && ` (${verifiedCount})`}
                      {filter === 'ignored' && ` (${ignoredCount})`}
                    </button>
                  ))}
                </div>

                <button
                  type="button"
                  onClick={handleApplyAllCorrections}
                  disabled={isApplyingCorrections || correctedCount === 0}
                  className="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-bold bg-[#08785D] hover:bg-[#06664E] text-white transition disabled:opacity-40 disabled:cursor-not-allowed shadow-2xs cursor-pointer"
                  title="Apply corrected text to canonical document"
                >
                  <Save className={`w-3.5 h-3.5 ${isApplyingCorrections ? 'animate-spin' : ''}`} />
                  <span>{isApplyingCorrections ? 'Applying...' : 'Apply Corrections to Notice'}</span>
                </button>
              </div>

              {applySuccessMessage && (
                <div className="p-2 rounded-lg bg-[#E8F7F0] border border-[#B7E7D2] text-xs font-semibold text-[#08785D] flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-[#08785D]" />
                  <span>{applySuccessMessage}</span>
                </div>
              )}

              {/* Items List */}
              <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                {filteredItems.length === 0 ? (
                  <div className="py-6 text-center text-xs text-[#526176]">
                    No items in this category.
                  </div>
                ) : (
                  filteredItems.map((item) => {
                    const draftVal = draftEdits[item.id] !== undefined ? draftEdits[item.id] : item.corrected_text || item.original_text;
                    const isCorrected = item.status === 'corrected';
                    const isVerified = item.status === 'verified';
                    const isIgnored = item.status === 'ignored';

                    return (
                      <div
                        key={item.id}
                        className={`p-2.5 rounded-lg border text-xs transition ${
                          isVerified
                            ? 'bg-emerald-50/60 border-emerald-200'
                            : isCorrected
                            ? 'bg-blue-50/60 border-blue-200'
                            : isIgnored
                            ? 'bg-slate-50 border-slate-200 opacity-60'
                            : 'bg-[#FFFAEB]/80 border-[#FEDF89]'
                        }`}
                      >
                        <div className="flex items-center justify-between gap-2 mb-1.5">
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-[10px] font-bold text-slate-500 bg-white px-1.5 py-0.5 rounded border border-slate-200">
                              P.{item.page_number}
                            </span>
                            <span className="font-semibold text-[#12233D] font-mono text-xs">
                              Original: "{item.original_text}"
                            </span>
                            {item.confidence != null && (
                              <span className="text-[10px] text-amber-800 bg-amber-100 border border-amber-300 px-1 rounded">
                                {item.confidence}%
                              </span>
                            )}
                          </div>

                          <div className="flex items-center gap-1.5">
                            <button
                              type="button"
                              onClick={() =>
                                openReviewHighlight(
                                  'human_review',
                                  `Review: ${item.original_text}`,
                                  {
                                    box: item.box,
                                    status: item.status,
                                    page_number: item.page_number,
                                    confidence: item.confidence,
                                  },
                                  item.corrected_text || item.original_text
                                )
                              }
                              className="flex items-center gap-1 text-[11px] text-[#08785D] hover:underline font-semibold cursor-pointer"
                              title="Inspect on document with synchronized underline"
                            >
                              <ExternalLink className="w-3 h-3" />
                              View in Document
                            </button>
                          </div>
                        </div>

                        {/* Correction Input & Action Buttons */}
                        <div className="flex items-center gap-2 mt-1">
                          <div className="flex-1">
                            <input
                              type="text"
                              value={draftVal}
                              onChange={(e) => handleDraftChange(item.id, e.target.value)}
                              placeholder="Type correct text..."
                              className="w-full bg-white border border-[#CBD5E1] rounded px-2 py-1 text-xs text-[#12233D] focus:border-[#08785D] focus:outline-hidden font-medium"
                            />
                          </div>

                          <button
                            type="button"
                            onClick={() => handleSaveCorrection(item)}
                            className="flex items-center gap-1 px-2 py-1 rounded text-[11px] font-bold bg-blue-600 hover:bg-blue-700 text-white transition cursor-pointer"
                            title="Save corrected text"
                          >
                            <Save className="w-3 h-3" />
                            Save
                          </button>

                          <button
                            type="button"
                            onClick={() => handleVerifyItem(item)}
                            className="flex items-center gap-1 px-2 py-1 rounded text-[11px] font-bold bg-emerald-600 hover:bg-emerald-700 text-white transition cursor-pointer"
                            title="Mark as verified (original text is correct)"
                          >
                            <Check className="w-3 h-3" />
                            Verify
                          </button>

                          <button
                            type="button"
                            onClick={() => handleIgnoreItem(item)}
                            className="flex items-center gap-1 px-2 py-1 rounded text-[11px] font-semibold bg-slate-200 hover:bg-slate-300 text-slate-700 transition cursor-pointer"
                            title="Ignore this token"
                          >
                            <XCircle className="w-3 h-3" />
                            Ignore
                          </button>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error alert */}
      {ocrError && (
        <div className="p-3 rounded-lg bg-[#FEE8E7] border border-[#FCA5A5] text-xs text-[#B42318] flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{ocrError}</span>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-2 border-t border-[#E1E7EE]">
        <button
          type="button"
          onClick={handleResetImage}
          className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold text-[#B42318] hover:bg-[#FEE8E7] transition cursor-pointer"
        >
          <Trash2 className="w-3.5 h-3.5" />
          {t('removeImage')}
        </button>

        <button
          type="button"
          onClick={handleRunOCR}
          disabled={isProcessing || cooldownSec > 0}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs disabled:opacity-50 cursor-pointer disabled:cursor-not-allowed"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isProcessing ? 'animate-spin' : ''}`} />
          {isProcessing ? t('extractingText') : cooldownSec > 0 ? `Please wait (${cooldownSec}s)...` : t('runOcr')}
        </button>
      </div>
    </div>
  );
};
