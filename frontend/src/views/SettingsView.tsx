import React, { useState } from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
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
  Trash2,
  Eye,
  Type,
  Volume2,
} from 'lucide-react';

export const SettingsView: React.FC = () => {
  const {
    systemHealth,
    refreshHealth,
    providers,
    activeProvider,
    switchProvider,
    resetSession,
    clearAllData,
    accessibilityPrefs,
    updateAccessibilityPrefs,
    resetAccessibilityPrefs,
    speakText,
    theme,
    setTheme,
  } = useNotice();
  const { t } = useTranslation();

  const [isRefreshing, setIsRefreshing] = useState(false);
  const [switchMessage, setSwitchMessage] = useState<string | null>(null);
  const [purgeSuccess, setPurgeSuccess] = useState(false);

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

  const handlePurgeAll = () => {
    if (window.confirm('Are you sure you want to purge all local history, uploaded notice buffers, and cached sessions? This action is irreversible.')) {
      clearAllData();
      setPurgeSuccess(true);
      setTimeout(() => setPurgeSuccess(false), 4000);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E1E7EE]">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-[#12233D] tracking-tight flex items-center gap-2">
            <Settings className="w-5 h-5 text-[#08785D]" />
            <span>{t('settingsTitle') || 'Settings & System Diagnostics'}</span>
          </h1>
          <p className="text-xs sm:text-sm text-[#526176] mt-1">
            Inspect real-time system dependencies, manage inference providers, and view privacy safeguards.
          </p>
        </div>

        <button
          type="button"
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-[#12233D] bg-white hover:bg-[#F8FAFC] border border-[#CBD5E1] transition disabled:opacity-50 self-start sm:self-auto cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-[#08785D] ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>Refresh Health</span>
        </button>
      </div>

      {switchMessage && (
        <div className="p-3.5 rounded-xl bg-[#EAF2FF] border border-[#BFDBFE] text-xs text-[#245DC1] flex items-center gap-2">
          <Activity className="w-4 h-4 text-[#245DC1] animate-spin" />
          <span>{switchMessage}</span>
        </div>
      )}

      {/* 1. Live Preflight Diagnostics */}
      <div className="bg-white border border-[#E1E7EE] rounded-xl p-5 space-y-4 shadow-xs">
        <h2 className="text-sm font-bold uppercase tracking-wider text-[#12233D] flex items-center gap-2">
          <Activity className="w-4 h-4 text-[#08785D]" />
          <span>Live Preflight Diagnostics</span>
        </h2>

        {systemHealth ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            {systemHealth.items.map((item, idx) => {
              const isOk = item.status === 'ok';
              return (
                <div
                  key={idx}
                  className="bg-[#F8FAFC] border border-[#E1E7EE] rounded-xl p-4 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#12233D]">{item.name}</span>
                    <span
                      className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-md ${
                        isOk
                          ? 'bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]'
                          : 'bg-[#FFF4D6] text-[#92500A] border border-[#FDE68A]'
                      }`}
                    >
                      {isOk ? <CheckCircle2 className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                      <span>{isOk ? 'Operational' : 'Attention'}</span>
                    </span>
                  </div>
                  <p className="text-xs text-[#526176] font-mono break-words">
                    {item.details}
                  </p>
                  {item.remedy && (
                    <p className="text-[11px] text-[#92500A] font-medium">Remedy: {item.remedy}</p>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="py-6 text-center text-xs text-[#68778B]">Loading system preflight diagnostics...</div>
        )}
      </div>

      {/* 2. AI Inference Provider Management */}
      <div className="bg-white border border-[#E1E7EE] rounded-xl p-5 space-y-4 shadow-xs">
        <h2 className="text-sm font-bold uppercase tracking-wider text-[#12233D] flex items-center gap-2">
          <Server className="w-4 h-4 text-[#08785D]" />
          <span>Active LLM Provider Configuration</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {providers.map((p) => {
            const isActive = activeProvider === p.id;
            return (
              <div
                key={p.id}
                className={`rounded-xl p-4.5 border transition flex flex-col justify-between space-y-3 ${
                  isActive
                    ? 'bg-[#E8F7F0]/40 border-[#08785D] shadow-xs'
                    : 'bg-[#F8FAFC] border-[#E1E7EE] hover:border-slate-300'
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-[#12233D] flex items-center gap-1.5">
                      {p.is_local ? '🔒' : '☁️'} {p.name}
                    </span>
                    {isActive ? (
                      <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-[#08785D] text-white">
                        ACTIVE
                      </span>
                    ) : (
                      <span className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-slate-100 text-[#526176]">
                        {p.is_local ? 'Default Local' : 'Cloud Adapter'}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-[#526176]">
                    Model: <span className="font-mono text-[#12233D] font-semibold">{p.model}</span>
                  </div>
                  <div className="text-[11px] text-[#68778B] truncate">
                    Endpoint: {p.endpoint}
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-200 flex items-center justify-between">
                  <span className="text-[11px] text-[#68778B]">
                    {p.requires_api_key
                      ? p.key_configured
                        ? 'Key Configured (in .env)'
                        : 'No Key Configured (in .env)'
                      : 'Zero Key Required (Offline)'}
                  </span>
                  {!isActive && (
                    <button
                      type="button"
                      onClick={() => handleProviderChange(p.id)}
                      className="px-3 py-1 rounded-lg text-xs font-semibold text-[#08785D] bg-white hover:bg-[#E8F7F0] border border-[#B7E7D2] transition cursor-pointer"
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
      <div className="bg-white border border-[#E1E7EE] rounded-xl p-5 space-y-3 shadow-xs">
        <h2 className="text-sm font-bold uppercase tracking-wider text-[#12233D] flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-[#08785D]" />
          <span>Security & Credential Privacy Safeguards</span>
        </h2>

        <div className="space-y-2 text-xs text-[#526176] leading-relaxed">
          <div className="flex items-start gap-2.5">
            <Lock className="w-4 h-4 text-[#08785D] shrink-0 mt-0.5" />
            <p>
              <strong>Zero Secret Exposure:</strong> SuchnaSetu AI strictly loads credentials on the backend via
              the process environment (<code className="font-mono text-[#08785D]">.env</code>). API keys are never
              transmitted to, requested by, or stored inside the client browser.
            </p>
          </div>
          <div className="flex items-start gap-2.5">
            <Cpu className="w-4 h-4 text-[#08785D] shrink-0 mt-0.5" />
            <p>
              <strong>100% Offline by Default:</strong> When using the default local provider (Ollama + Gemma 4)
              and Tesseract OCR, no document data, images, or extracted facts ever leave your local machine.
            </p>
          </div>
        </div>
      </div>

      {/* 3. Personalized Accessibility Mode (Low Vision & Accessibility) */}
      <div className="bg-white border border-[#E1E7EE] rounded-xl p-5 space-y-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#E1E7EE]">
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-[#12233D] flex items-center gap-2">
              <Eye className="w-4 h-4 text-[#08785D]" />
              <span>Personalized Accessibility Mode (WCAG & Low Vision Controls)</span>
            </h2>
            <p className="text-xs text-[#526176] mt-0.5">
              Customize typography, contrast, spacing, and speech guidance across all views.
            </p>
          </div>

          <button
            type="button"
            onClick={resetAccessibilityPrefs}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-[#526176] bg-[#F8FAFC] hover:bg-slate-200 border border-[#CBD5E1] transition cursor-pointer self-start sm:self-auto"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset to Defaults</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Text Size Control */}
          <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-2">
            <span className="text-xs font-bold text-[#12233D] flex items-center gap-1.5">
              <Type className="w-3.5 h-3.5 text-[#08785D]" />
              <span>Text Size</span>
            </span>
            <div className="grid grid-cols-3 gap-1.5">
              {(['normal', 'large', 'extra-large'] as const).map((size) => (
                <button
                  key={size}
                  type="button"
                  onClick={() => updateAccessibilityPrefs({ textSize: size })}
                  className={`px-2 py-1.5 rounded-lg text-xs font-semibold capitalize border transition cursor-pointer ${
                    accessibilityPrefs?.textSize === size
                      ? 'bg-[#08785D] text-white border-[#08785D] shadow-xs'
                      : 'bg-white text-[#526176] border-[#CBD5E1] hover:bg-slate-100'
                  }`}
                >
                  {size.replace('-', ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Line & Paragraph Spacing */}
          <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-2">
            <span className="text-xs font-bold text-[#12233D]">Line & Paragraph Spacing</span>
            <div className="grid grid-cols-3 gap-1.5">
              {(['normal', 'relaxed', 'loose'] as const).map((spacing) => (
                <button
                  key={spacing}
                  type="button"
                  onClick={() => updateAccessibilityPrefs({ lineSpacing: spacing })}
                  className={`px-2 py-1.5 rounded-lg text-xs font-semibold capitalize border transition cursor-pointer ${
                    accessibilityPrefs?.lineSpacing === spacing
                      ? 'bg-[#08785D] text-white border-[#08785D] shadow-xs'
                      : 'bg-white text-[#526176] border-[#CBD5E1] hover:bg-slate-100'
                  }`}
                >
                  {spacing}
                </button>
              ))}
            </div>
          </div>

          {/* High Contrast Mode */}
          <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-[#12233D] block">High Contrast Mode</span>
              <span className="text-[11px] text-[#68778B] block mt-0.5">Dark background, stark borders</span>
            </div>
            <button
              type="button"
              onClick={() =>
                updateAccessibilityPrefs({
                  highContrast: !accessibilityPrefs?.highContrast,
                  warmBackground: false,
                })
              }
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition border cursor-pointer ${
                accessibilityPrefs?.highContrast
                  ? 'bg-slate-900 text-white border-white'
                  : 'bg-white text-[#526176] border-[#CBD5E1] hover:bg-slate-100'
              }`}
            >
              {accessibilityPrefs?.highContrast ? 'ON' : 'OFF'}
            </button>
          </div>

          {/* Warm Paper Reading Background */}
          <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-[#12233D] block">Warm Reading Tone</span>
              <span className="text-[11px] text-[#68778B] block mt-0.5">Sepia tint to reduce glare</span>
            </div>
            <button
              type="button"
              onClick={() =>
                updateAccessibilityPrefs({
                  warmBackground: !accessibilityPrefs?.warmBackground,
                  highContrast: false,
                })
              }
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition border cursor-pointer ${
                accessibilityPrefs?.warmBackground
                  ? 'bg-[#92500A] text-white border-[#92500A]'
                  : 'bg-white text-[#526176] border-[#CBD5E1] hover:bg-slate-100'
              }`}
            >
              {accessibilityPrefs?.warmBackground ? 'ON' : 'OFF'}
            </button>
          </div>

          {/* Highlight Key Information */}
          <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-[#12233D] block">Highlight Key Information</span>
              <span className="text-[11px] text-[#68778B] block mt-0.5">Accentuates deadlines and fees</span>
            </div>
            <button
              type="button"
              onClick={() =>
                updateAccessibilityPrefs({ highlightKeyInfo: !accessibilityPrefs?.highlightKeyInfo })
              }
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition border cursor-pointer ${
                accessibilityPrefs?.highlightKeyInfo
                  ? 'bg-[#08785D] text-white border-[#08785D]'
                  : 'bg-white text-[#526176] border-[#CBD5E1] hover:bg-slate-100'
              }`}
            >
              {accessibilityPrefs?.highlightKeyInfo ? 'ON' : 'OFF'}
            </button>
          </div>

          {/* Reduced Motion */}
          <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-[#12233D] block">Reduced Motion</span>
              <span className="text-[11px] text-[#68778B] block mt-0.5">Disables pulsing and animations</span>
            </div>
            <button
              type="button"
              onClick={() =>
                updateAccessibilityPrefs({ reducedMotion: !accessibilityPrefs?.reducedMotion })
              }
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition border cursor-pointer ${
                accessibilityPrefs?.reducedMotion
                  ? 'bg-[#08785D] text-white border-[#08785D]'
                  : 'bg-white text-[#526176] border-[#CBD5E1] hover:bg-slate-100'
              }`}
            >
              {accessibilityPrefs?.reducedMotion ? 'ON' : 'OFF'}
            </button>
          </div>

          {/* Theme Option */}
          <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-2">
            <div>
              <span className="text-xs font-bold text-[#12233D] block">Application Theme</span>
              <span className="text-[11px] text-[#68778B] block mt-0.5">Slate Green (Light) or Midnight Teal (Dark)</span>
            </div>
            <div className="grid grid-cols-2 gap-2 pt-1">
              <button
                type="button"
                onClick={() => setTheme('light')}
                className={`flex items-center justify-center gap-1.5 px-2 py-1.5 rounded-lg text-xs font-semibold border transition cursor-pointer ${
                  theme === 'light'
                    ? 'bg-white text-[#12233D] border-[#08785D] shadow-xs font-bold ring-1 ring-[#08785D]'
                    : 'bg-white text-[#526176] border-[#CBD5E1] hover:bg-slate-100'
                }`}
              >
                <span className="w-2.5 h-2.5 rounded-full bg-[#08785D] shrink-0" />
                <span>Slate Green</span>
              </button>
              <button
                type="button"
                onClick={() => setTheme('dark')}
                className={`flex items-center justify-center gap-1.5 px-2 py-1.5 rounded-lg text-xs font-semibold border transition cursor-pointer ${
                  theme === 'dark'
                    ? 'bg-[#17243A] text-[#14B8A6] border-[#14B8A6] shadow-xs font-bold ring-1 ring-[#14B8A6]'
                    : 'bg-white text-[#526176] border-[#CBD5E1] hover:bg-slate-100'
                }`}
              >
                <span className="w-2.5 h-2.5 rounded-full bg-[#14B8A6] shrink-0" />
                <span>Midnight Teal</span>
              </button>
            </div>
          </div>
        </div>

        {/* Read-Aloud Voice Guidance Test */}
        <div className="p-3.5 rounded-xl bg-[#E8F7F0] border border-[#B7E7D2] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-[#08785D]">
          <div className="flex items-center gap-2">
            <Volume2 className="w-4 h-4 text-[#08785D] shrink-0" />
            <span>
              <strong>Air-Gapped Speech Guidance:</strong> Powered by your browser's local Web Speech API. 100% offline with zero cloud audio telemetry.
            </span>
          </div>
          <button
            type="button"
            onClick={() => speakText('SuchnaSetu accessibility mode test: Web Speech API audio guidance is active and fully offline.')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold bg-[#08785D] text-white hover:bg-[#06664E] transition shadow-xs cursor-pointer shrink-0"
          >
            <Volume2 className="w-3.5 h-3.5" />
            <span>Test Speech Playback</span>
          </button>
        </div>
      </div>

      {/* 4. Privacy & Data Storage Controls */}
      <div className="bg-white border border-[#E1E7EE] rounded-xl p-5 space-y-4 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-sm font-bold text-[#12233D] flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#92500A]" />
              <span>Privacy & Local Data Storage</span>
            </h2>
            <p className="text-xs text-[#526176] mt-1 max-w-2xl leading-relaxed">
              SuchnaSetu stores notice summaries and user-confirmed facts locally in your browser's <code className="font-mono text-[#12233D]">localStorage</code> for quick retrieval across sessions. On shared or sensitive terminals, you can permanently wipe all stored history and active buffers.
            </p>
          </div>

          <button
            type="button"
            onClick={handlePurgeAll}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-[#B42318] bg-[#FEE8E7] hover:bg-rose-200 border border-[#FCA5A5] transition self-start sm:self-auto cursor-pointer"
          >
            <Trash2 className="w-3.5 h-3.5 text-[#B42318]" />
            <span>Purge All Stored Data</span>
          </button>
        </div>

        {purgeSuccess && (
          <div className="p-3 rounded-xl bg-[#E8F7F0] border border-[#B7E7D2] text-xs text-[#08785D] flex items-center gap-2 animate-fadeIn">
            <CheckCircle2 className="w-4 h-4 text-[#08785D] shrink-0" />
            <span>All local browser storage, history entries, and active notice buffers have been securely purged.</span>
          </div>
        )}
      </div>

      {/* 5. Reset Session Workspace */}
      <div className="bg-white border border-[#E1E7EE] rounded-xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xs">
        <div>
          <h2 className="text-sm font-bold text-[#12233D]">Reset Active Workspace Buffer</h2>
          <p className="text-xs text-[#526176] mt-0.5">
            Clears the current notice buffer, analysis results, and conversational Q&amp;A history without deleting saved history.
          </p>
        </div>

        <button
          type="button"
          onClick={resetSession}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-[#526176] hover:text-[#12233D] bg-[#F8FAFC] hover:bg-slate-200 border border-[#CBD5E1] transition self-start sm:self-auto cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Buffer</span>
        </button>
      </div>
    </div>
  );
};
