import React, { useState } from 'react';
import { useNotice } from '../context/NoticeContext';
import {
  Settings,
  Activity,
  Cpu,
  Server,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  RotateCcw,
  RefreshCw,
  Lock,
} from 'lucide-react';

export const SettingsView: React.FC = () => {
  const {
    systemHealth,
    refreshHealth,
    providers,
    activeProvider,
    switchProvider,
    resetSession,
  } = useNotice();

  const [isRefreshing, setIsRefreshing] = useState(false);
  const [switchMessage, setSwitchMessage] = useState<string | null>(null);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await refreshHealth();
    setIsRefreshing(false);
  };

  const handleProviderChange = async (providerId: string) => {
    setSwitchMessage(`Switching provider to ${providerId}...`);
    await switchProvider(providerId);
    setSwitchMessage(null);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Settings className="w-5 h-5 text-amber-400" />
            <span>Settings & System Diagnostics</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Inspect real-time system dependencies, manage inference providers, and view privacy safeguards.
          </p>
        </div>

        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-200 bg-[#121E3B] hover:bg-[#182A52] border border-[#233B6E] transition disabled:opacity-50 self-start sm:self-auto cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-blue-400 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>Refresh Health</span>
        </button>
      </div>

      {switchMessage && (
        <div className="p-3 rounded-lg bg-blue-950/40 border border-blue-800 text-xs text-blue-300 flex items-center gap-2">
          <Activity className="w-4 h-4 text-blue-400 animate-spin" />
          <span>{switchMessage}</span>
        </div>
      )}

      {/* 1. Live Preflight Diagnostics */}
      <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <Activity className="w-4 h-4 text-blue-400" />
          <span>Live Preflight Diagnostics</span>
        </h2>

        {systemHealth ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {systemHealth.items.map((item, idx) => {
              const isOk = item.status === 'ok';
              return (
                <div
                  key={idx}
                  className="bg-[#080E1E] border border-slate-800/80 rounded-lg p-3.5 space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{item.name}</span>
                    <span
                      className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                        isOk
                          ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/60'
                          : 'bg-amber-950/60 text-amber-400 border border-amber-800/60'
                      }`}
                    >
                      {isOk ? <CheckCircle2 className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                      <span>{isOk ? 'Operational' : 'Attention'}</span>
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 font-mono text-[11px] break-words">
                    {item.details}
                  </p>
                  {item.remedy && (
                    <p className="text-[11px] text-amber-400 font-medium">Remedy: {item.remedy}</p>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="py-6 text-center text-xs text-slate-400">Loading system preflight diagnostics...</div>
        )}
      </div>

      {/* 2. AI Inference Provider Management */}
      <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <Server className="w-4 h-4 text-blue-400" />
          <span>Active LLM Provider Configuration</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {providers.map((p) => {
            const isActive = activeProvider === p.id;
            return (
              <div
                key={p.id}
                className={`rounded-xl p-4 border transition flex flex-col justify-between space-y-3 ${
                  isActive
                    ? 'bg-[#101D3D] border-blue-500 shadow-md shadow-blue-600/10'
                    : 'bg-[#080E1E] border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-white flex items-center gap-1.5">
                      {p.is_local ? '🔒' : '☁️'} {p.name}
                    </span>
                    {isActive ? (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-600 text-white">
                        ACTIVE
                      </span>
                    ) : (
                      <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                        {p.is_local ? 'Default Local' : 'Cloud Adapter'}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-slate-400">
                    Model: <span className="font-mono text-slate-300">{p.model}</span>
                  </div>
                  <div className="text-[11px] text-slate-500 truncate">
                    Endpoint: {p.endpoint}
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-[11px] text-slate-400">
                    {p.requires_api_key
                      ? p.key_configured
                        ? 'Key Configured (in .env)'
                        : 'No Key Configured (in .env)'
                      : 'Zero Key Required (Offline)'}
                  </span>
                  {!isActive && (
                    <button
                      onClick={() => handleProviderChange(p.id)}
                      className="px-2.5 py-1 rounded text-xs font-semibold text-blue-400 hover:text-white bg-blue-950/40 hover:bg-blue-600 border border-blue-900 transition"
                    >
                      Select
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 3. Security & Cloud Provider Privacy Notice */}
      <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-5 space-y-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Security & Credential Privacy Safeguards</span>
        </h2>

        <div className="space-y-2 text-xs text-slate-300 leading-relaxed">
          <div className="flex items-start gap-2.5">
            <Lock className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <p>
              <strong>Zero Secret Exposure:</strong> Notice2Action AI strictly loads credentials on the backend via
              the process environment (<code className="font-mono text-blue-300">.env</code>). API keys are never
              transmitted to, requested by, or stored inside the client browser.
            </p>
          </div>
          <div className="flex items-start gap-2.5">
            <Cpu className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
            <p>
              <strong>100% Offline by Default:</strong> When using the default local provider (Ollama + Gemma 4)
              and Tesseract OCR, no document data, images, or extracted facts ever leave your local machine.
            </p>
          </div>
        </div>
      </div>

      {/* 4. Reset Session Workspace */}
      <div className="bg-[#0B1327] border border-rose-950/60 rounded-xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold text-white">Reset Session Workspace</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Clears active notice buffer, analysis results, and conversational question history.
          </p>
        </div>

        <button
          onClick={resetSession}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-rose-400 hover:text-white bg-rose-950/30 hover:bg-rose-900/60 border border-rose-900/60 transition self-start sm:self-auto cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Workspace</span>
        </button>
      </div>
    </div>
  );
};
