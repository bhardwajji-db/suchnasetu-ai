import React, { useState, useRef } from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import { apiClient } from '../services/apiClient';
import { UploadCloud, AlertCircle } from 'lucide-react';

export const FileDropzone: React.FC = () => {
  const { setRawNoticeText, setUploadedImage } = useNotice();
  const { t } = useTranslation();
  const [isDragging, setIsDragging] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    setUploadError(null);

    // Max 25MB limit supported by backend
    if (file.size > 25 * 1024 * 1024) {
      setUploadError('File size exceeds the 25MB limit.');
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
            ? 'border-[#08785D] bg-[#E8F7F0] shadow-md shadow-[#08785D]/10'
            : 'border-[#CBD5E1] hover:border-[#08785D] bg-[#F8FAFC]'
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
        <div className="flex flex-col items-center justify-center gap-2.5">
          <div className="w-12 h-12 rounded-xl bg-[#E8F7F0] border border-[#B7E7D2] flex items-center justify-center text-[#08785D]">
            <UploadCloud className="w-6 h-6" />
          </div>
          <div>
            <div className="text-sm font-bold text-[#12233D]">
              {t('dropzoneTitle') || 'Drag & Drop notice document, image, or PDF'}
            </div>
            <div className="text-xs text-[#526176] mt-1">
              {t('dropzoneSubtitle') || 'Supports PDF, PNG, JPG, WEBP, TXT up to 25MB'}
            </div>
          </div>
        </div>
      </div>

      {uploadError && (
        <div className="p-3 rounded-xl bg-[#FEE8E7] border border-[#FCA5A5] text-xs text-[#B42318] flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-[#B42318] shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}
    </div>
  );
};
