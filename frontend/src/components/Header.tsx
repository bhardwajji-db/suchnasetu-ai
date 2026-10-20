import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { Cpu, Globe, CheckCircle2, AlertTriangle, XCircle, Eye } from 'lucide-react';

export const Header: React.FC = () => {
  const { systemHealth, selectedLang, setSelectedLang, openOriginalNoticeModal, rawNoticeText } = useNotice();

  const getStatusBadge = () => {
    if (!systemHealth) {
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-gray-800 text-gray-300 border border-gray-700">
          <span className="w-2 h-2 rounded-full bg-gray-500 animate-pulse"></span>
          Checking System...
        </span>
      );
    }
    if (systemHealth.overall_status === 'ok') {
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800/80">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          System Online • {systemHealth.model_name}
        </span>
      );
    }
    if (systemHealth.overall_status === 'warning') {
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-950/80 text-amber-400 border border-amber-800/80">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
          Preflight Warning
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-950/80 text-rose-400 border border-rose-800/80">
        <XCircle className="w-3.5 h-3.5 text-rose-400" />
        Ollama Offline
      </span>
    );
  };

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between px-6 py-3.5 bg-[#0B132B]/95 backdrop-blur border-b border-[#1D2D4E]">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20 font-black text-white text-base">
            N
          </div>
          <span className="text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
            Notice<span className="text-blue-500">2Action</span> AI
            <span className="text-[10px] font-mono uppercase bg-blue-600/30 text-blue-400 border border-blue-500/40 px-1.5 py-0.5 rounded font-semibold ml-1">
              PS02
            </span>
          </span>
        </div>
        <span className="hidden md:inline-block text-xs text-slate-400 border-l border-slate-700 pl-3">
          Notice-to-Action Accessibility Assistant
        </span>
      </div>

      <div className="flex items-center gap-3">
        {/* Original Notice Document Viewer Button */}
        <button
          type="button"
          onClick={openOriginalNoticeModal}
          disabled={!rawNoticeText}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold text-slate-300 hover:text-white bg-[#111A33] border border-[#1D2D4E] hover:border-slate-700 transition disabled:opacity-40 disabled:cursor-not-allowed"
          title="View Original Ground-Truth Notice Document"
        >
          <Eye className="w-3.5 h-3.5 text-blue-400" />
          <span className="hidden sm:inline">Original Notice</span>
        </button>

        {/* On-device badge */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium text-slate-300 bg-[#111A33] border border-[#1D2D4E]">
          <Cpu className="w-3.5 h-3.5 text-blue-400" />
          <span>Local Gemma 4 (100% Privacy)</span>
        </div>

        {/* System Health */}
        {getStatusBadge()}

        {/* Language switcher */}
        <div className="flex items-center rounded-lg bg-[#111A33] border border-[#1D2D4E] p-0.5">
          <button
            onClick={() => setSelectedLang('en')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold transition-all ${
              selectedLang === 'en'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Globe className="w-3 h-3" />
            EN
          </button>
          <button
            onClick={() => setSelectedLang('hi')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold transition-all ${
              selectedLang === 'hi'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            हिन्दी
          </button>
        </div>
      </div>
    </header>
  );
};
