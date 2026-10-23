import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { Cpu, CheckCircle2, Loader2 } from 'lucide-react';

export const AnalysisProgressModal: React.FC = () => {
  const { isAnalyzing, analysisPhase, activeProvider } = useNotice();

  if (!isAnalyzing) return null;

  const phases = [
    { num: 1, title: 'Validating notice input and security boundaries' },
    { num: 2, title: 'Inspecting document format and OCR text normalization' },
    { num: 3, title: `Querying AI engine (${activeProvider}) for structured extraction` },
    { num: 4, title: 'Validating structured output and evidence quotes' },
    { num: 5, title: 'Synthesizing plain-language summary & action checklist' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
      <div className="w-full max-w-lg bg-white border border-[#E1E7EE] rounded-2xl p-6 shadow-2xl space-y-5 animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#E8F7F0] border border-[#B7E7D2] flex items-center justify-center text-[#08785D]">
            <Cpu className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-base font-bold text-[#12233D]">
              Analyzing Notice with SuchnaSetu AI
            </h3>
            <p className="text-xs text-[#526176]">
              {activeProvider === 'ollama' ? '100% on-device inference via Ollama • Zero cloud data leakage' : 'Inference via configured provider'}
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
                className={`flex items-center gap-3 p-3 rounded-xl border transition-all ${
                  isDone
                    ? 'bg-[#E8F7F0] border-[#B7E7D2] text-[#08785D]'
                    : isCurrent
                    ? 'bg-[#E8F7F0]/40 border-[#08785D] text-[#08785D] font-bold'
                    : 'bg-[#F8FAFC] border-[#E1E7EE] text-[#68778B]'
                }`}
              >
                <div className="shrink-0">
                  {isDone ? (
                    <CheckCircle2 className="w-4 h-4 text-[#08785D]" />
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 text-[#08785D] animate-spin" />
                  ) : (
                    <span className="w-4 h-4 rounded-full border border-[#CBD5E1] flex items-center justify-center text-[10px] font-mono">
                      {p.num}
                    </span>
                  )}
                </div>
                <div className="text-xs">
                  <span className="font-mono text-[10px] mr-1.5 opacity-70">
                    Phase {p.num}/5:
                  </span>
                  {p.title}
                </div>
              </div>
            );
          })}
        </div>

        <div className="text-[11px] text-center text-[#68778B] italic">
          Grounded character alignment and validation ensures verifiable accuracy.
        </div>
      </div>
    </div>
  );
};
