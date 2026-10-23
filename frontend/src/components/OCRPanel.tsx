import React, { useState } from 'react';
import { useNotice } from '../context/NoticeContext';
import { apiClient } from '../services/apiClient';
import { Eye, RefreshCw, Trash2, CheckCircle2, AlertTriangle } from 'lucide-react';

export const OCRPanel: React.FC = () => {
  const { uploadedImage, uploadedFile, setUploadedImage, setRawNoticeText, setOcrResult, ocrResult } = useNotice();
  const [ocrLang, setOcrLang] = useState<string>('eng');
  const [enhanceContrast, setEnhanceContrast] = useState<boolean>(true);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [ocrError, setOcrError] = useState<string | null>(null);

  if (!uploadedImage) return null;

  const handleRunOCR = async () => {
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
      }
    } catch (err: any) {
      setOcrError(err.message || 'OCR processing failed.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleResetImage = () => {
    setUploadedImage(null, null);
    setOcrResult(null);
  };

  return (
    <div className="bg-white border border-[#E1E7EE] rounded-xl p-5 space-y-4 shadow-xs">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-[#12233D] flex items-center gap-1.5">
          <Eye className="w-4 h-4 text-[#08785D]" />
          Notice Image Preview
        </span>
        {ocrResult && (
          <span className="flex items-center gap-1 text-[11px] font-bold text-[#08785D] bg-[#E8F7F0] border border-[#B7E7D2] px-2.5 py-0.5 rounded-md">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Confidence: {ocrResult.confidence_score.toFixed(1)}%
          </span>
        )}
      </div>

      {/* Image container */}
      <div className="relative max-h-56 overflow-hidden rounded-xl border border-[#E1E7EE] bg-[#F8FAFC] flex items-center justify-center p-2">
        <img
          src={uploadedImage}
          alt="Loaded notice preview"
          className="max-h-52 w-auto object-contain rounded-lg shadow-xs"
        />
      </div>

      {/* OCR Controls */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
        <div>
          <label className="text-[11px] font-bold text-[#526176] uppercase tracking-wide block mb-1">
            OCR Language Pack
          </label>
          <select
            value={ocrLang}
            onChange={(e) => setOcrLang(e.target.value)}
            className="w-full bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg px-3 py-1.5 text-xs text-[#12233D] focus:border-[#08785D] focus:outline-hidden"
          >
            <option value="eng">English (eng)</option>
            <option value="hin">Hindi (hin)</option>
            <option value="eng+hin">Bilingual (eng + hin)</option>
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
            <span>Enhance Contrast (Adaptive)</span>
          </label>
        </div>
      </div>

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
          Remove Image
        </button>

        <button
          type="button"
          onClick={handleRunOCR}
          disabled={isProcessing}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs disabled:opacity-50 cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isProcessing ? 'animate-spin' : ''}`} />
          {isProcessing ? 'Extracting Text...' : 'Run Tesseract OCR'}
        </button>
      </div>
    </div>
  );
};
