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
      <div className="bg-white border border-[#E1E7EE] rounded-2xl p-12 text-center space-y-4 shadow-xs">
        <div className="w-12 h-12 rounded-xl bg-[#E8F7F0] border border-[#B7E7D2] text-[#08785D] flex items-center justify-center mx-auto">
          <ListTodo className="w-6 h-6" />
        </div>
        <h2 className="text-base font-bold text-[#12233D]">No Summary or Action Checklist Available</h2>
        <p className="text-xs text-[#526176] max-w-md mx-auto">
          Analyze a notice in the Notice Workspace tab first to synthesize an accessible plain-language summary and sequential action steps.
        </p>
        <button
          type="button"
          onClick={() => setActiveTab(1)}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs cursor-pointer"
        >
          <span>Go to Notice Workspace</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-[#12233D] tracking-tight flex items-center gap-2">
          <span>📋 3. Plain-Language Summary & Grounded Action Checklist</span>
        </h1>
        <p className="text-xs text-[#526176] mt-1">
          Transform convoluted legal circulars into simplified answers and an interactive sequential checklist with iCalendar deadline export.
        </p>
      </div>

      <StaleWarningBanner />

      <PlainLanguageSummaryView />

      <ActionChecklistTable />
    </div>
  );
};
