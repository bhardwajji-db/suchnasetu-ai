import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import { Cpu, CheckCircle2, Loader2 } from 'lucide-react';

export const AnalysisProgressModal: React.FC = () => {
  const { isAnalyzing, analysisPhase, activeProvider } = useNotice();
  const { t } = useTranslation();

  if (!isAnalyzing) return null;

  const phases = [
    { num: 1, title: t('analysisPhase1') },
    { num: 2, title: t('analysisPhase2') },
    { num: 3, title: t('analysisPhase3') },
    { num: 4, title: t('analysisPhase4') },
    { num: 5, title: t('analysisPhase5') },
  ];

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="analysis-progress-title"
      aria-describedby="analysis-progress-desc"
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4"
    >
      <div className="w-full max-w-lg bg-white border border-[#E1E7EE] rounded-2xl p-6 shadow-2xl space-y-5 animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#E8F7F0] border border-[#B7E7D2] flex items-center justify-center text-[#08785D]">
            <Cpu className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 id="analysis-progress-title" className="text-base font-bold text-[#12233D]">
              {t('analyzingNoticeModalTitle')}
            </h3>
            <p id="analysis-progress-desc" className="text-xs text-[#526176]">
              {activeProvider === 'ollama' ? t('analyzingNoticeOllamaDesc') : t('analyzingNoticeProviderDesc')}
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
                    <div className="w-4 h-4 rounded-full border border-slate-300 flex items-center justify-center text-[10px] font-mono">
                      {p.num}
                    </div>
                  )}
                </div>
                <div className="text-xs">{p.title}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
