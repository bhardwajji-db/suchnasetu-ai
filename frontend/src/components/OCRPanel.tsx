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
        // Fetch blob from uploadedImage URL
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
    <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-4 space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
          <Eye className="w-4 h-4 text-blue-400" />
          Notice Image Preview
        </span>
        {ocrResult && (
          <span className="flex items-center gap-1 text-[11px] font-bold text-emerald-400 bg-emerald-950/80 border border-emerald-800 px-2 py-0.5 rounded">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Confidence: {ocrResult.confidence_score.toFixed(1)}%
          </span>
        )}
      </div>

      {/* Image container */}
      <div className="relative max-h-56 overflow-hidden rounded-lg border border-[#1D2D4E] bg-black/40 flex items-center justify-center">
        <img
          src={uploadedImage}
          alt="Loaded notice preview"
          className="max-h-56 w-auto object-contain"
        />
      </div>

      {/* OCR Controls */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
        <div>
          <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wide block mb-1">
            OCR Language Pack
          </label>
          <select
            value={ocrLang}
            onChange={(e) => setOcrLang(e.target.value)}
            className="w-full bg-[#111A33] border border-[#1D2D4E] rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="eng">English (eng)</option>
            <option value="hin">Hindi (hin)</option>
            <option value="eng+hin">Bilingual (eng + hin)</option>
          </select>
        </div>

        <div className="flex items-end pb-1.5">
          <label className="flex items-center gap-2 text-xs font-medium text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={enhanceContrast}
              onChange={(e) => setEnhanceContrast(e.target.checked)}
              className="rounded border-[#1D2D4E] bg-[#111A33] text-blue-600 focus:ring-blue-500"
            />
            <span>Enhance Contrast (Adaptive)</span>
          </label>
        </div>
      </div>

      {/* OCR Action Buttons */}
      <div className="flex items-center gap-2 pt-2 border-t border-[#1D2D4E]">
        <button
          onClick={handleRunOCR}
          disabled={isProcessing}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 transition shadow-sm disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isProcessing ? 'animate-spin' : ''}`} />
          {isProcessing ? 'Running Tesseract OCR...' : 'Run Tesseract OCR'}
        </button>

        <button
          onClick={handleResetImage}
          className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-rose-400 bg-[#111A33] hover:bg-rose-950/20 border border-[#1D2D4E] transition"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Reset Image
        </button>
      </div>

      {ocrError && (
        <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-800/40 text-xs text-rose-300 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{ocrError}</span>
        </div>
      )}
    </div>
  );
};
