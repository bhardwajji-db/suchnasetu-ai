import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { Cpu, CheckCircle2, Loader2 } from 'lucide-react';

export const AnalysisProgressModal: React.FC = () => {
  const { isAnalyzing, analysisPhase } = useNotice();

  if (!isAnalyzing) return null;

  const phases = [
    { num: 1, title: 'Validating notice input and security boundaries' },
    { num: 2, title: 'Inspecting document format and OCR text normalization' },
    { num: 3, title: 'Querying local Gemma 4 for structured extraction' },
    { num: 4, title: 'Validating structured output and evidence quotes' },
    { num: 5, title: 'Synthesizing plain-language summary & action checklist' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg bg-[#0B1327] border border-blue-500/40 rounded-2xl p-6 shadow-2xl shadow-blue-500/10 space-y-5 animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
            <Cpu className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">
              Analyzing Notice with Local Gemma 4
            </h3>
            <p className="text-xs text-slate-400">
              100% on-device inference via Ollama • Zero cloud data leakage
            </p>
          </div>
        </div>

        {/* Progress steps */}
        <div className="space-y-3 pt-2">
          {phases.map((p) => {
            const isDone = analysisPhase > p.num;
            const isCurrent = analysisPhase === p.num;
            return (
              <div
                key={p.num}
                className={`flex items-center gap-3 p-2.5 rounded-lg border transition-all ${
                  isDone
                    ? 'bg-emerald-950/20 border-emerald-900/50 text-emerald-300'
                    : isCurrent
                    ? 'bg-blue-950/40 border-blue-500/50 text-blue-200'
                    : 'bg-slate-900/40 border-slate-800 text-slate-500'
                }`}
              >
                <div className="shrink-0">
                  {isDone ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                  ) : (
                    <span className="w-4 h-4 rounded-full border border-slate-700 flex items-center justify-center text-[10px]">
                      {p.num}
                    </span>
                  )}
                </div>
                <div className="text-xs font-semibold">
                  <span className="font-mono text-[10px] mr-1.5 opacity-70">
                    Phase {p.num}/5:
                  </span>
                  {p.title}
                </div>
              </div>
            );
          })}
        </div>

        <div className="text-[11px] text-center text-slate-500 italic">
          Local model execution typically takes ~25–40 seconds on standard GPUs.
        </div>
      </div>
    </div>
  );
};
