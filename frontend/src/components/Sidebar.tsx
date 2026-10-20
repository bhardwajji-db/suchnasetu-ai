import React, { useState } from 'react';
import { useNotice } from '../context/NoticeContext';
import {
  FileText,
  Search,
  ListTodo,
  MessageSquare,
  Sparkles,
  RotateCcw,
  Activity,
  ChevronDown,
  ChevronUp,
  Download,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const {
    activeTab,
    setActiveTab,
    samples,
    loadSampleFixture,
    resetSession,
    systemHealth,
    structuredNotice,
  } = useNotice();

  const [selectedSample, setSelectedSample] = useState<string>('sample_scholarship_notice.txt');
  const [showDiagnostics, setShowDiagnostics] = useState<boolean>(false);

  const navItems = [
    { id: 0, label: '1. Ingestion & OCR', icon: FileText },
    { id: 1, label: '2. Grounded Facts', icon: Search, badge: structuredNotice ? '8 Facts' : undefined },
    { id: 2, label: '3. Summary & Actions', icon: ListTodo, badge: structuredNotice ? 'Ready' : undefined },
    { id: 3, label: '4. Follow-Up Q&A', icon: MessageSquare },
  ];

  const handleCompetitionDemo = () => {
    loadSampleFixture('synthetic_scholarship_notice.txt');
  };

  const handleLoadSelectedSample = () => {
    if (selectedSample) {
      loadSampleFixture(selectedSample);
    }
  };

  return (
    <aside className="w-68 bg-[#090F1F] border-r border-[#1D2D4E] flex flex-col justify-between h-[calc(100vh-61px)] overflow-y-auto">
      <div className="p-4 space-y-6">
        {/* Navigation Group */}
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-2 px-1">
            Navigation
          </span>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-bold'
                      : 'text-slate-300 hover:bg-[#121B33] hover:text-white'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`text-[10px] font-mono uppercase px-1.5 py-0.5 rounded ${
                        isActive
                          ? 'bg-blue-800 text-blue-100'
                          : 'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Quick-Load Samples */}
        <div className="pt-2 border-t border-[#1D2D4E]">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-2.5 px-1">
            🧪 Quick-Load Samples
          </span>

          <button
            onClick={handleCompetitionDemo}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 mb-2 rounded-lg text-xs font-bold text-white bg-gradient-to-r from-blue-700 to-indigo-700 hover:from-blue-600 hover:to-indigo-600 transition shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5 text-blue-300" />
            Competition Demo (TEST-SCH)
          </button>

          <div className="space-y-2">
            <select
              value={selectedSample}
              onChange={(e) => setSelectedSample(e.target.value)}
              className="w-full bg-[#111A33] border border-[#1D2D4E] rounded-md px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            >
              {samples.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.title}
                </option>
              ))}
            </select>

            <button
              onClick={handleLoadSelectedSample}
              className="w-full flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium text-slate-200 bg-[#152244] hover:bg-[#1C2D5A] border border-[#1D2D4E] transition"
            >
              <Download className="w-3 h-3 text-blue-400" />
              Load Selected Notice
            </button>
          </div>
        </div>

        {/* System Diagnostics Drawer */}
        <div className="pt-2 border-t border-[#1D2D4E]">
          <button
            onClick={() => setShowDiagnostics(!showDiagnostics)}
            className="w-full flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2 px-1 hover:text-white"
          >
            <span className="flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-blue-400" />
              System Diagnostics
            </span>
            {showDiagnostics ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {showDiagnostics && systemHealth && (
            <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-lg p-2.5 space-y-2 text-xs">
              {systemHealth.items.map((it, idx) => (
                <div key={idx} className="pb-1.5 border-b border-slate-800/60 last:border-0 last:pb-0">
                  <div className="flex items-center gap-1.5 font-semibold text-slate-200">
                    {it.status === 'ok' ? (
                      <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                    ) : (
                      <AlertCircle className="w-3 h-3 text-amber-400" />
                    )}
                    <span>{it.name}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 pl-4">{it.details}</div>
                  {it.remedy && (
                    <div className="text-[10px] text-amber-400 pl-4 mt-0.5">Remedy: {it.remedy}</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Footer Reset Action */}
      <div className="p-4 border-t border-[#1D2D4E]">
        <button
          onClick={resetSession}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-rose-400 hover:bg-rose-950/20 border border-slate-800 hover:border-rose-900 transition"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Reset Workspace
        </button>
      </div>
    </aside>
  );
};
