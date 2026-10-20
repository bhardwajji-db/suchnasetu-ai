import React from 'react';
import { useNotice } from '../context/NoticeContext';
import {
  UploadCloud,
  Sparkles,
  FileSearch,
  CheckSquare,
  MessageSquare,
  Activity,
  History,
  CheckCircle2,
  Clock,
  Building,
  ShieldCheck,
  ArrowRight,
  FileText,
} from 'lucide-react';

export const DashboardView: React.FC = () => {
  const {
    setActiveTab,
    loadSampleFixture,
    structuredNotice,
    rawNoticeText,
    systemHealth,
    activeProvider,
    history,
    loadFromHistory,
  } = useNotice();

  const handleLoadDemo = () => {
    loadSampleFixture('synthetic_scholarship_notice.txt');
  };

  const getSystemStatus = () => {
    if (!systemHealth) return { text: 'Checking system...', color: 'text-amber-400 bg-amber-950/40 border-amber-800' };
    if (systemHealth.overall_status === 'ok') {
      return {
        text: `System Ready · ${activeProvider === 'ollama' ? 'Local Ollama' : activeProvider}`,
        color: 'text-emerald-400 bg-emerald-950/40 border-emerald-800',
      };
    }
    return { text: 'Diagnostics Warning', color: 'text-amber-400 bg-amber-950/40 border-amber-800' };
  };

  const status = getSystemStatus();

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#0C1733] via-[#0F1E42] to-[#0B132B] border border-[#1E325A] p-6 sm:p-8 shadow-xl">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 rounded-full bg-blue-600/10 blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold border backdrop-blur-sm ${status.color}">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>{status.text}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Legal Notice-to-Action Accessibility Assistant
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed">
              Transform convoluted government notifications, court summonses, and institutional circulars into
              evidence-grounded facts, accessible summaries, and sequential action checklists.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={() => setActiveTab(1)}
              className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm text-white bg-blue-600 hover:bg-blue-500 transition shadow-lg shadow-blue-600/25 cursor-pointer"
            >
              <UploadCloud className="w-4 h-4" />
              <span>Upload Notice</span>
            </button>
            <button
              onClick={handleLoadDemo}
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-sm text-slate-200 bg-[#142347] hover:bg-[#1A2E5C] border border-[#233B6E] transition cursor-pointer"
            >
              <Sparkles className="w-4 h-4 text-blue-400" />
              <span>Try Demo Notice</span>
            </button>
          </div>
        </div>
      </div>

      {/* Genuine Processing Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-4.5 space-y-1.5 shadow-sm">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400">
            <span>Notice Buffer Status</span>
            <FileText className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-lg font-bold text-white truncate">
            {rawNoticeText ? (
              <span className="text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" /> Loaded ({rawNoticeText.length} chars)
              </span>
            ) : (
              <span className="text-slate-500">No Document Loaded</span>
            )}
          </div>
          <p className="text-[11px] text-slate-400">
            {structuredNotice ? 'Analyzed and verified' : 'Ready for ingestion or demo load'}
          </p>
        </div>

        {/* Metric 2 */}
        <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-4.5 space-y-1.5 shadow-sm">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400">
            <span>Issuing Authority</span>
            <Building className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-lg font-bold text-white truncate">
            {structuredNotice?.issuing_authority?.value || (structuredNotice ? 'Unspecified' : '—')}
          </div>
          <p className="text-[11px] text-slate-400">
            {structuredNotice ? 'From Six Core Notice Fields' : 'Awaiting document analysis'}
          </p>
        </div>

        {/* Metric 3 */}
        <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-4.5 space-y-1.5 shadow-sm">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400">
            <span>Closing Deadline</span>
            <Clock className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-lg font-bold text-white truncate">
            {structuredNotice?.deadline?.value || (structuredNotice ? 'None specified' : '—')}
          </div>
          <p className="text-[11px] text-slate-400">
            {structuredNotice?.deadline?.status ? `Status: ${structuredNotice.deadline.status}` : 'Pending analysis'}
          </p>
        </div>

        {/* Metric 4 */}
        <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-4.5 space-y-1.5 shadow-sm">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400">
            <span>Local AI Model</span>
            <ShieldCheck className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-lg font-bold text-white truncate">
            {systemHealth?.model_name || 'gemma4:latest'}
          </div>
          <p className="text-[11px] text-slate-400">100% On-Device & Private</p>
        </div>
      </div>

      {/* Quick Navigation Cards */}
      <div className="space-y-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 px-1">
          Application Workflows
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Card 1 */}
          <div
            onClick={() => setActiveTab(1)}
            className="group bg-[#0B1327] hover:bg-[#0F1A36] border border-[#1D2D4E] hover:border-blue-500/50 rounded-xl p-5 cursor-pointer transition shadow-sm"
          >
            <div className="w-10 h-10 rounded-lg bg-blue-600/10 text-blue-400 flex items-center justify-center mb-3 group-hover:scale-105 transition">
              <UploadCloud className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white group-hover:text-blue-400 transition flex items-center justify-between">
              <span>1. Upload & Ingest Notice</span>
              <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-blue-400 transition group-hover:translate-x-1" />
            </h3>
            <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
              Drag-and-drop document scans, images (.png, .jpg), or paste notice text directly into the ground-truth buffer.
            </p>
          </div>

          {/* Card 2 */}
          <div
            onClick={() => setActiveTab(2)}
            className="group bg-[#0B1327] hover:bg-[#0F1A36] border border-[#1D2D4E] hover:border-blue-500/50 rounded-xl p-5 cursor-pointer transition shadow-sm"
          >
            <div className="w-10 h-10 rounded-lg bg-indigo-600/10 text-indigo-400 flex items-center justify-center mb-3 group-hover:scale-105 transition">
              <FileSearch className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white group-hover:text-blue-400 transition flex items-center justify-between">
              <span>2. Notice Analysis</span>
              <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-blue-400 transition group-hover:translate-x-1" />
            </h3>
            <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
              Inspect the Six Core Legal Notice Fields, certainty indicators, verbatim citations, and human-in-the-loop review.
            </p>
          </div>

          {/* Card 3 */}
          <div
            onClick={() => setActiveTab(3)}
            className="group bg-[#0B1327] hover:bg-[#0F1A36] border border-[#1D2D4E] hover:border-blue-500/50 rounded-xl p-5 cursor-pointer transition shadow-sm"
          >
            <div className="w-10 h-10 rounded-lg bg-emerald-600/10 text-emerald-400 flex items-center justify-center mb-3 group-hover:scale-105 transition">
              <CheckSquare className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white group-hover:text-blue-400 transition flex items-center justify-between">
              <span>3. Action Center & Exports</span>
              <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-blue-400 transition group-hover:translate-x-1" />
            </h3>
            <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
              Explore sequential action items, completion states, plain summaries (Simple/Detailed), and RFC 5545 calendar export.
            </p>
          </div>

          {/* Card 4 */}
          <div
            onClick={() => setActiveTab(4)}
            className="group bg-[#0B1327] hover:bg-[#0F1A36] border border-[#1D2D4E] hover:border-blue-500/50 rounded-xl p-5 cursor-pointer transition shadow-sm"
          >
            <div className="w-10 h-10 rounded-lg bg-sky-600/10 text-sky-400 flex items-center justify-center mb-3 group-hover:scale-105 transition">
              <MessageSquare className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white group-hover:text-blue-400 transition flex items-center justify-between">
              <span>4. Ask AI Assistant</span>
              <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-blue-400 transition group-hover:translate-x-1" />
            </h3>
            <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
              Ask follow-up questions answered strictly using verified notice facts in English or Hindi, with truthful absent reporting.
            </p>
          </div>

          {/* Card 5 */}
          <div
            onClick={() => setActiveTab(5)}
            className="group bg-[#0B1327] hover:bg-[#0F1A36] border border-[#1D2D4E] hover:border-blue-500/50 rounded-xl p-5 cursor-pointer transition shadow-sm"
          >
            <div className="w-10 h-10 rounded-lg bg-purple-600/10 text-purple-400 flex items-center justify-center mb-3 group-hover:scale-105 transition">
              <History className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white group-hover:text-blue-400 transition flex items-center justify-between">
              <span>5. Notice History</span>
              <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-blue-400 transition group-hover:translate-x-1" />
            </h3>
            <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
              View previously analyzed notices stored safely in isolated local sessions, with instant reload capability.
            </p>
          </div>

          {/* Card 6 */}
          <div
            onClick={() => setActiveTab(6)}
            className="group bg-[#0B1327] hover:bg-[#0F1A36] border border-[#1D2D4E] hover:border-blue-500/50 rounded-xl p-5 cursor-pointer transition shadow-sm"
          >
            <div className="w-10 h-10 rounded-lg bg-amber-600/10 text-amber-400 flex items-center justify-center mb-3 group-hover:scale-105 transition">
              <Activity className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white group-hover:text-blue-400 transition flex items-center justify-between">
              <span>6. System Settings & Health</span>
              <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-blue-400 transition group-hover:translate-x-1" />
            </h3>
            <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
              Inspect live backend diagnostics, local Ollama connectivity, active provider selection, and cloud guides.
            </p>
          </div>
        </div>
      </div>

      {/* Recent Notices Snapshot */}
      <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <History className="w-4 h-4 text-blue-400" />
              <span>Recent Document Sessions</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Notices processed during your active session.
            </p>
          </div>
          {history.length > 0 && (
            <button
              onClick={() => setActiveTab(5)}
              className="text-xs font-semibold text-blue-400 hover:text-blue-300 transition"
            >
              View All ({history.length})
            </button>
          )}
        </div>

        {history.length > 0 ? (
          <div className="divide-y divide-slate-800">
            {history.slice(0, 3).map((item) => (
              <div key={item.id} className="py-3 flex items-center justify-between gap-4">
                <div className="space-y-1 min-w-0">
                  <div className="text-sm font-semibold text-white truncate">{item.title}</div>
                  <div className="text-xs text-slate-400 flex items-center gap-3">
                    <span>{item.authority}</span>
                    <span>•</span>
                    <span>Ref: {item.referenceNumber}</span>
                    <span>•</span>
                    <span>{item.timestamp}</span>
                  </div>
                </div>
                <button
                  onClick={() => loadFromHistory(item)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold text-blue-400 hover:text-white bg-blue-950/40 hover:bg-blue-600 border border-blue-900/60 transition shrink-0"
                >
                  Open Notice
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-8 text-center text-slate-400 space-y-2">
            <p className="text-xs">No notice documents analyzed in this session yet.</p>
            <div className="flex justify-center gap-2">
              <button
                onClick={() => setActiveTab(1)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-blue-400 bg-blue-950/40 hover:bg-blue-900/50 border border-blue-900/60 transition"
              >
                Upload a Notice
              </button>
              <button
                onClick={handleLoadDemo}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 bg-slate-800/60 hover:bg-slate-700/60 border border-slate-700 transition"
              >
                Load Scholarship Demo
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
