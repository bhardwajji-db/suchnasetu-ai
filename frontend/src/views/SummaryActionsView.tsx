import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { PlainLanguageSummaryView } from '../components/PlainLanguageSummaryView';
import { ActionChecklistTable } from '../components/ActionChecklistTable';
import { StaleWarningBanner } from '../components/StaleWarningBanner';
import { ListTodo, ArrowRight } from 'lucide-react';

export const SummaryActionsView: React.FC = () => {
  const { summaryEn, checklistEn, setActiveTab } = useNotice();

  if (!summaryEn && !checklistEn) {
    return (
      <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-12 text-center space-y-4">
        <div className="w-12 h-12 rounded-xl bg-blue-600/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mx-auto">
          <ListTodo className="w-6 h-6" />
        </div>
        <h2 className="text-base font-bold text-white">No Summary or Action Checklist Available</h2>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          Analyze a notice in the Ingestion tab first to synthesize an accessible plain-language summary and sequential action steps.
        </p>
        <button
          onClick={() => setActiveTab(1)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 transition shadow-sm cursor-pointer"
        >
          <span>Go to Ingestion & OCR</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <span>📋 3. Plain-Language Summary & Grounded Action Checklist</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Transform convoluted legal circulars into simplified answers and an interactive sequential checklist with iCalendar deadline export.
        </p>
      </div>

      <StaleWarningBanner />

      <PlainLanguageSummaryView />

      <ActionChecklistTable />
    </div>
  );
};
