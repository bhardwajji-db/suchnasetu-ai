import React, { useState } from 'react';
import { useNotice } from '../context/NoticeContext';
import { apiClient } from '../services/apiClient';
import {
  CheckSquare,
  Square,
  Calendar,
  FileDown,
  Quote,
  CheckCircle2,
  Info,
} from 'lucide-react';

export const ActionChecklistTable: React.FC = () => {
  const {
    checklistEn,
    checklistHi,
    localizedChecklist,
    selectedLang,
    outputLang,
    toggleChecklistItem,
    structuredNotice,
    summaryEn,
    summaryHi,
    localizedSummary,
  } = useNotice();
  const [isExporting, setIsExporting] = useState(false);

  const checklist = (outputLang && outputLang !== 'en' && localizedChecklist)
    ? localizedChecklist
    : (selectedLang === 'hi' || outputLang === 'hi')
    ? (checklistHi || localizedChecklist || checklistEn)
    : (checklistEn || localizedChecklist || checklistHi);

  const summary = (outputLang && outputLang !== 'en' && localizedSummary)
    ? localizedSummary
    : (selectedLang === 'hi' || outputLang === 'hi')
    ? (summaryHi || localizedSummary || summaryEn)
    : (summaryEn || localizedSummary || summaryHi);
  if (!checklist || checklist.items.length === 0) return null;

  const totalItems = checklist.items.length;
  const completedItems = checklist.items.filter((i) => i.is_completed).length;
  const progressPercent = Math.round((completedItems / totalItems) * 100);

  const handleDownloadMarkdown = async () => {
    setIsExporting(true);
    try {
      if (structuredNotice) {
        const blob = await apiClient.exportMarkdown(structuredNotice, summary || undefined, checklist);
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'notice2action_plan.md';
        a.click();
        URL.revokeObjectURL(url);
      } else {
        const lines = [
          '# Sequential Action Checklist',
          '',
          ...checklist.items.map((it) => `${it.step_number}. [${it.is_completed ? 'x' : ' '}] ${it.action} (${it.category})`),
        ];
        const blob = new Blob([lines.join('\n')], { type: 'text/markdown;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'notice2action_checklist.md';
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error('Failed to export Markdown', err);
    } finally {
      setIsExporting(false);
    }
  };

  const handleDownloadIcs = async () => {
    setIsExporting(true);
    try {
      const blob = await apiClient.exportIcs(checklist, structuredNotice?.purpose?.value || 'Notice Deadline');
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'notice_deadline.ics';
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to export iCalendar', err);
    } finally {
      setIsExporting(false);
    }
  };

  const getCategoryBadge = (cat: string) => {
    const colors: Record<string, string> = {
      eligibility: 'bg-[#E8F7F0] text-[#08785D] border-[#B7E7D2]',
      documents: 'bg-[#EAF2FF] text-[#245DC1] border-[#BFDBFE]',
      application: 'bg-[#E8F7F0] text-[#08785D] border-[#B7E7D2]',
      submission: 'bg-[#EAF2FF] text-[#245DC1] border-[#BFDBFE]',
      clarification: 'bg-[#FFF4D6] text-[#92500A] border-[#FDE68A]',
    };
    const style = colors[cat] || 'bg-slate-100 text-[#526176] border-slate-200';
    return (
      <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-md border ${style}`}>
        {cat}
      </span>
    );
  };

  return (
    <div className="bg-white border border-[#E1E7EE] rounded-xl p-6 space-y-5 shadow-xs">
      {/* Header and Progress */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#E1E7EE]">
        <div>
          <h2 className="text-base font-bold text-[#12233D] flex items-center gap-2">
            <CheckSquare className="w-4 h-4 text-[#08785D]" />
            {selectedLang === 'hi' ? 'कार्रवाई योग्य चेकलिस्ट' : 'Sequential Action Checklist'}
          </h2>
          <p className="text-xs text-[#526176] mt-0.5">
            {selectedLang === 'hi'
              ? 'सत्यापित सूचना तथ्यों से प्राप्त आवश्यक चरण।'
              : 'Actionable steps derived strictly from verified facts.'}
          </p>
        </div>

        {/* Progress Tracker */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-xs font-mono font-bold text-[#12233D]">
              {completedItems} / {totalItems} Done ({progressPercent}%)
            </div>
            <div className="w-32 h-2.5 bg-slate-100 rounded-full overflow-hidden mt-1 border border-slate-200">
              <div
                className="h-full bg-[#08785D] transition-all duration-300 rounded-full"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Checklist items list */}
      <div className="space-y-2.5">
        {checklist.items.map((item) => (
          <div
            key={item.step_number}
            role="checkbox"
            tabIndex={0}
            aria-checked={item.is_completed}
            aria-label={`Step ${item.step_number}: ${item.action}`}
            onClick={() => toggleChecklistItem(item.step_number)}
            onKeyDown={(e) => {
              if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                toggleChecklistItem(item.step_number);
              }
            }}
            className={`p-4 rounded-xl border transition-all cursor-pointer flex items-start gap-3 select-none focus:outline-hidden focus:ring-2 focus:ring-[#08785D] ${
              item.is_completed
                ? 'bg-slate-50/80 border-slate-200 text-[#68778B]'
                : 'bg-[#F8FAFC] border-[#E1E7EE] hover:border-[#B7E7D2] text-[#12233D]'
            }`}
          >
            <div className="pt-0.5 shrink-0 text-[#08785D]">
              {item.is_completed ? (
                <CheckCircle2 className="w-5 h-5 text-[#08785D]" />
              ) : (
                <Square className="w-5 h-5 text-[#CBD5E1] hover:text-[#08785D] transition" />
              )}
            </div>

            <div className="flex-1 space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-xs font-bold text-[#526176]">
                  Step {item.step_number}
                </span>
                {getCategoryBadge(item.category)}
                <span
                  className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-md ${
                    item.is_mandatory
                      ? 'bg-[#FEE8E7] text-[#B42318] border border-[#FCA5A5]'
                      : 'bg-slate-100 text-[#526176] border border-slate-200'
                  }`}
                >
                  {item.is_mandatory ? 'Mandatory' : 'Advisory'}
                </span>
              </div>

              <div
                className={`text-sm font-semibold transition ${
                  item.is_completed ? 'line-through text-[#68778B]' : 'text-[#12233D]'
                }`}
              >
                {item.action}
              </div>

              {item.grounded_quote && !item.is_completed && (
                <div className="text-xs text-[#526176] italic flex items-center gap-1 font-mono pt-0.5">
                  <Quote className="w-3 h-3 text-[#08785D] shrink-0" />
                  "{item.grounded_quote}"
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Official Submission Disclaimer */}
      <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] flex items-center gap-2 text-xs text-[#526176]">
        <Info className="w-4 h-4 text-[#08785D] shrink-0" />
        <span>
          <strong>Notice:</strong> Completing tasks in this preparation checklist does not constitute official submission to the issuing authority. Always submit via designated official portals.
        </span>
      </div>

      {/* Export Action Bar */}
      <div className="pt-3 border-t border-[#E1E7EE] flex flex-wrap items-center justify-between gap-3">
        <span className="text-xs text-[#526176]">
          Save action steps or sync closing deadlines to your digital calendar.
        </span>

        <div className="flex items-center gap-2.5">
          <button
            type="button"
            onClick={handleDownloadMarkdown}
            disabled={isExporting}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-[#12233D] bg-white hover:bg-[#F8FAFC] border border-[#CBD5E1] transition cursor-pointer"
          >
            <FileDown className="w-3.5 h-3.5 text-[#08785D]" />
            Download Markdown (.md)
          </button>

          <button
            type="button"
            onClick={handleDownloadIcs}
            disabled={isExporting}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs cursor-pointer"
          >
            <Calendar className="w-3.5 h-3.5" />
            Add to Calendar (.ics)
          </button>
        </div>
      </div>
    </div>
  );
};
