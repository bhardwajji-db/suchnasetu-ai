import React from 'react';
import { useNotice, type HistoryRecord } from '../context/NoticeContext';
import {
  History,
  Trash2,
  Clock,
  Building,
  ArrowRight,
  Download,
} from 'lucide-react';

export const NoticeHistoryView: React.FC = () => {
  const { history, loadFromHistory, clearHistory, setActiveTab } = useNotice();

  const handleDownloadNoticeText = (item: HistoryRecord) => {
    const blob = new Blob([item.rawText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `notice_${item.id}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <History className="w-5 h-5 text-purple-400" />
            <span>Notice History & Session Archive</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Access previous legal notice analyses preserved in your secure local session.
          </p>
        </div>

        {history.length > 0 && (
          <button
            onClick={clearHistory}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-rose-400 hover:text-white bg-rose-950/30 hover:bg-rose-900/60 border border-rose-900/60 transition self-start sm:self-auto"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear History</span>
          </button>
        )}
      </div>

      {history.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {history.map((item) => (
            <div
              key={item.id}
              className="bg-[#0B1327] border border-[#1D2D4E] hover:border-blue-500/50 rounded-xl p-5 space-y-3 transition shadow-sm flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <div className="text-sm font-bold text-white leading-snug line-clamp-2">
                    {item.title}
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 shrink-0">
                    {item.charCount} chars
                  </span>
                </div>

                <div className="space-y-1 text-xs text-slate-400">
                  <div className="flex items-center gap-2 truncate">
                    <Building className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                    <span className="truncate">{item.authority}</span>
                  </div>
                  <div className="flex items-center gap-2 truncate">
                    <Clock className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    <span className="truncate">Deadline: {item.deadline}</span>
                  </div>
                  <div className="text-[11px] text-slate-500 pt-1">
                    Recorded: {item.timestamp} · Ref: {item.referenceNumber}
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-center justify-between gap-2">
                <button
                  onClick={() => handleDownloadNoticeText(item)}
                  className="flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 transition"
                  title="Download raw notice text"
                >
                  <Download className="w-3 h-3 text-slate-400" />
                  <span>Download Text</span>
                </button>

                <button
                  onClick={() => loadFromHistory(item)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 transition shadow-sm shadow-blue-600/30"
                >
                  <span>Open in Workspace</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-12 text-center space-y-4">
          <div className="w-12 h-12 rounded-xl bg-purple-600/10 border border-purple-500/20 text-purple-400 flex items-center justify-center mx-auto">
            <History className="w-6 h-6" />
          </div>
          <h2 className="text-base font-bold text-white">No Document History Yet</h2>
          <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
            Notices analyzed during your active session will be automatically archived here.
            You can reopen any analyzed notice at any time to review facts and export checklists.
          </p>
          <div className="pt-2">
            <button
              onClick={() => setActiveTab(1)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 transition shadow-sm"
            >
              <span>Upload Your First Notice</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
