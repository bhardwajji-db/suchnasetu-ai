import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export const StaleWarningBanner: React.FC = () => {
  const { isNoticeStale, runAnalysis, isAnalyzing } = useNotice();
  const { t } = useTranslation();

  if (!isNoticeStale) return null;

  return (
    <div className="mb-4 p-3.5 rounded-xl bg-[#FFF4D6] border border-[#FDE68A] flex items-center justify-between gap-3 text-[#92500A] shadow-xs">
      <div className="flex items-center gap-2.5">
        <AlertTriangle className="w-5 h-5 text-[#92500A] shrink-0" />
        <div className="text-xs">
          <span className="font-bold">{t('staleBufferNotice')}</span> {t('staleWarningDesc')}
        </div>
      </div>
      <button
        type="button"
        onClick={runAnalysis}
        disabled={isAnalyzing}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-[#92500A] hover:bg-[#783E07] transition shrink-0 disabled:opacity-50 cursor-pointer"
      >
        <RefreshCw className={`w-3.5 h-3.5 ${isAnalyzing ? 'animate-spin' : ''}`} />
        {t('reAnalyzeNotice')}
      </button>
    </div>
  );
};
