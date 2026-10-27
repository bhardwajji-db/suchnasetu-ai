import React, { useState, useEffect } from 'react';
import { useNotice } from '../context/NoticeContext';
import { apiClient } from '../services/apiClient';
import { useTranslation } from '../i18n';
import { Eye, RefreshCw, Trash2, AlertTriangle, ShieldCheck, Compass, FileCheck, CheckCircle2 } from 'lucide-react';

export const OCRPanel: React.FC = () => {
  const { uploadedImage, uploadedFile, setUploadedImage, setRawNoticeText, setOcrResult, ocrResult } = useNotice();
  const { t } = useTranslation();
  const [ocrLang, setOcrLang] = useState<string>('hin+eng');
  const [enhanceContrast, setEnhanceContrast] = useState<boolean>(true);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [ocrError, setOcrError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'repaired' | 'raw'>('repaired');
  const [cooldownSec, setCooldownSec] = useState<number>(0);
  const [isRateLimited, setIsRateLimited] = useState<boolean>(false);

  useEffect(() => {
    if (cooldownSec <= 0) {
      if (isRateLimited) setIsRateLimited(false);
      return;
    }
    const timer = setInterval(() => {
      setCooldownSec((prev) => {
        if (prev <= 1) {
          setIsRateLimited(false);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [cooldownSec, isRateLimited]);

  if (!uploadedImage) return null;

  const handleRunOCR = async () => {
    if (isProcessing || cooldownSec > 0) return;
    setIsProcessing(true);
    setOcrError(null);

    try {
      let fileToUpload = uploadedFile;
      if (!fileToUpload) {
        const blob = await fetch(uploadedImage).then((r) => r.blob());
        fileToUpload = new File([blob], 'notice_preview.png', { type: blob.type || 'image/png' });
      }

      const res = await apiClient.runOCR(fileToUpload, fileToUpload.name, ocrLang, enhanceContrast);
      if (res.error) {
        setOcrError(res.error);
      } else {
        setRawNoticeText(res.extracted_text);
        setOcrResult(res);
        setViewMode('repaired');
      }
    } catch (err: any) {
      if (err.status === 429 || /rate limit|quota/i.test(err.message || '')) {
        setIsRateLimited(true);
        setOcrError(err.message || t('error'));
        setCooldownSec(15);
      } else {
        setOcrError(err.message || t('invalidCredentialsError'));
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

  const qualityScore = ocrResult?.document_quality_score ?? ocrResult?.confidence_score ?? 0;
  const isHighQuality = qualityScore >= 80;
  const isModerateQuality = qualityScore >= 65 && qualityScore < 80;

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

      {/* OCR Controls */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
        <div>
          <label className="text-[11px] font-bold text-[#526176] uppercase tracking-wide block mb-1">
            {t('ocrLanguagePack')}
          </label>
          <select
            value={ocrLang}
            onChange={(e) => setOcrLang(e.target.value)}
            className="w-full bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg px-3 py-1.5 text-xs text-[#12233D] focus:border-[#08785D] focus:outline-hidden font-medium"
          >
            <option value="hin+eng">Bilingual (Hindi + English - Hybrid Fusion)</option>
            <option value="hin">Hindi (hin)</option>
            <option value="eng">English (eng)</option>
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
                  className="bg-white p-2 rounded-lg border border-[#E1E7EE] flex flex-col justify-between"
                >
                  <div className="flex items-center justify-between text-[10px] text-[#526176] mb-1">
                    <span className="font-semibold truncate max-w-[140px]">{label}</span>
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

      {/* Low-confidence / uncertain span warnings */}
      {(() => {
        const unresolved = ocrResult?.uncertain_spans?.filter(s => s.status !== 'repaired') || [];
        const repaired = ocrResult?.uncertain_spans?.filter(s => s.status === 'repaired') || [];

        return (
          <>
            {unresolved.length > 0 && (
              <div className="p-3 rounded-lg bg-[#FFFAEB] border border-[#FEDF89] text-xs text-[#B54708] space-y-1">
                <div className="flex items-center gap-1.5 font-bold">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <span>{t('humanReviewAdvised')} ({unresolved.length})</span>
                </div>
                <p className="text-[11px] text-[#7A271A]">
                  {t('humanReviewAdvisedDesc')}
                </p>
                <div className="flex flex-wrap gap-1.5 mt-1.5 pt-1 border-t border-[#FEDF89]/50">
                  {unresolved.slice(0, 5).map((span, idx) => (
                    <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono bg-amber-100 text-amber-900 border border-amber-300">
                      "{span.text}" ({span.confidence}%)
                    </span>
                  ))}
                  {unresolved.length > 5 && (
                    <span className="text-[10px] text-amber-700 self-center">+{unresolved.length - 5} more</span>
                  )}
                </div>
              </div>
            )}
            {repaired.length > 0 && (
              <div className="p-2.5 rounded-lg bg-[#F0FDF4] border border-[#BBF7D0] text-xs text-[#166534] flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-[#16A34A] shrink-0" />
                  <span>{repaired.length} OCR artifacts auto-repaired & verified</span>
                </div>
              </div>
            )}
          </>
        );
      })()}

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
