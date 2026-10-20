import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export const StaleWarningBanner: React.FC = () => {
  const { isNoticeStale, runAnalysis, isAnalyzing } = useNotice();

  if (!isNoticeStale) return null;

  return (
    <div className="mb-4 p-3.5 rounded-lg bg-amber-950/60 border border-amber-500/40 flex items-center justify-between gap-3 text-amber-200">
      <div className="flex items-center gap-2.5">
        <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
        <div className="text-xs">
          <span className="font-bold">Notice Buffer Modified:</span> The text in the ground-truth buffer has changed since last analysis. Results displayed reflect an earlier version.
        </div>
      </div>
      <button
        onClick={runAnalysis}
        disabled={isAnalyzing}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold text-white bg-amber-600 hover:bg-amber-500 transition shrink-0 disabled:opacity-50"
      >
        <RefreshCw className={`w-3.5 h-3.5 ${isAnalyzing ? 'animate-spin' : ''}`} />
        Re-Analyze Notice
      </button>
    </div>
  );
};
