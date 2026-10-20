import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { FileDropzone } from '../components/FileDropzone';
import { OCRPanel } from '../components/OCRPanel';
import { NoticeBuffer } from '../components/NoticeBuffer';
import { StaleWarningBanner } from '../components/StaleWarningBanner';
import { MetricCard } from '../components/MetricCard';
import {
  Search,
  ListTodo,
  MessageSquare,
  CheckCircle2,
  AlertTriangle,
  Play,
} from 'lucide-react';

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
  } = useNotice();

  return (
    <div className="space-y-6">
      {/* View Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <span>📥 1. Notice Ingestion & Document Processing</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Ingest institutional circulars via high-accuracy Tesseract OCR, upload text files, or paste notice text directly into the ground-truth buffer.
        </p>
      </div>

      <StaleWarningBanner />

      {/* Two-Column Balanced Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 items-start">
        {/* Left Column: Upload & OCR */}
        <div className="space-y-4">
          <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-4 space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300 block">
              📁 1. Upload Scanned Notice or Text File
            </span>
            <FileDropzone />
          </div>

          {uploadedImage && <OCRPanel />}
        </div>

        {/* Right Column: Ground-Truth Buffer */}
        <div className="h-full">
          <NoticeBuffer />
        </div>
      </div>

      {/* Dominant Primary Analyze Button */}
      <div className="pt-2">
        <button
          onClick={runAnalysis}
          disabled={!rawNoticeText.trim() || isAnalyzing}
          className="w-full flex items-center justify-center gap-2.5 py-3.5 px-6 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:from-blue-500 hover:to-indigo-500 transition shadow-lg shadow-blue-600/25 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          <Play className="w-4 h-4 fill-white" />
          <span>🚀 Analyze Notice with Local Gemma 4</span>
        </button>
      </div>

      {/* Analysis Error Recovery */}
      {analysisError && (
        <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-800/80 text-xs text-rose-300 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <div className="font-bold text-rose-200">Analysis Pipeline Notice</div>
            <div>{analysisError}</div>
            <div className="text-[11px] text-rose-400/80">
              Check that Ollama is running (`ollama serve`) and the model is loaded.
            </div>
          </div>
        </div>
      )}

      {/* Analysis Success Banner & Jump Actions */}
      {structuredNotice && (
        <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-800/60 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-bold text-emerald-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>
                Notice Analyzed ({analysisDuration ? `${analysisDuration.toFixed(2)}s` : 'Complete'}) • 8 Dimensions Grounded • Ready to Review
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-1">
            <button
              onClick={() => setActiveTab(2)}
              className="flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-bold text-slate-200 bg-[#0D1528] hover:bg-[#152244] border border-[#1D2D4E] hover:border-blue-500 transition cursor-pointer"
            >
              <Search className="w-3.5 h-3.5 text-blue-400" />
              View Grounded Facts
            </button>
            <button
              onClick={() => setActiveTab(3)}
              className="flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-bold text-slate-200 bg-[#0D1528] hover:bg-[#152244] border border-[#1D2D4E] hover:border-blue-500 transition cursor-pointer"
            >
              <ListTodo className="w-3.5 h-3.5 text-blue-400" />
              View Summary & Actions
            </button>
            <button
              onClick={() => setActiveTab(4)}
              className="flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-bold text-slate-200 bg-[#0D1528] hover:bg-[#152244] border border-[#1D2D4E] hover:border-blue-500 transition cursor-pointer"
            >
              <MessageSquare className="w-3.5 h-3.5 text-blue-400" />
              Ask Follow-Up Q&A
            </button>
          </div>
        </div>
      )}

      {/* Fast Assistance & Metric Cards */}
      {structuredNotice && (
        <div className="space-y-3 pt-2">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300">
              ⚡ Fast Assistance & Overview Metrics
            </h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
            <MetricCard fact={structuredNotice.purpose} label="Purpose" iconType="purpose" />
            <MetricCard fact={structuredNotice.deadline} label="Closing Deadline" iconType="deadline" />
            <MetricCard fact={structuredNotice.eligibility} label="Eligibility Criteria" iconType="eligibility" />
            <MetricCard fact={structuredNotice.required_actions} label="Required Actions" iconType="actions" />
          </div>
        </div>
      )}
    </div>
  );
};
