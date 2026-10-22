import React, { useState, useRef } from 'react';
import { useNotice } from '../context/NoticeContext';
import { apiClient } from '../services/apiClient';
import { UploadCloud, AlertCircle } from 'lucide-react';

export const FileDropzone: React.FC = () => {
  const { setRawNoticeText, setUploadedImage } = useNotice();
  const [isDragging, setIsDragging] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    setUploadError(null);

    // Max 10MB
    if (file.size > 10 * 1024 * 1024) {
      setUploadError('File size exceeds the 10MB limit.');
      return;
    }

    try {
      const res = await apiClient.uploadFile(file);
      if (res.source_type === 'text' || res.source_type === 'pdf') {
        setRawNoticeText(res.raw_text);
        setUploadedImage(null, null);
      } else if (res.source_type === 'image') {
        const url = URL.createObjectURL(file);
        setUploadedImage(url, file);
      }
    } catch (err: any) {
      setUploadError(err.message || 'Failed to upload document.');
    }
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div className="space-y-2">
      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
          isDragging
            ? 'border-blue-500 bg-blue-950/20 shadow-lg shadow-blue-500/10'
            : 'border-[#1D2D4E] hover:border-blue-500/50 bg-[#0B1327]/60'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".png,.jpg,.jpeg,.webp,.txt,.pdf,application/pdf"
          className="hidden"
          aria-label="Upload notice image or document"
          onChange={(e) => handleFiles(e.target.files)}
        />
        <div className="flex flex-col items-center justify-center gap-2">
          <div className="w-12 h-12 rounded-xl bg-[#111A33] border border-[#1D2D4E] flex items-center justify-center text-blue-400">
            <UploadCloud className="w-6 h-6" />
          </div>
          <div>
            <div className="text-sm font-bold text-slate-200">
              Drag & Drop notice document, image, or PDF
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Supports <span className="text-blue-400 font-mono">PDF (Digital/Scanned), PNG, JPG, WEBP, TXT</span> up to 10MB
            </div>
          </div>
        </div>
      </div>

      {uploadError && (
        <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-800/40 text-xs text-rose-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}
    </div>
  );
};
