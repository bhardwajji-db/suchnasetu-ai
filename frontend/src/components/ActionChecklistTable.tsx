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
} from 'lucide-react';

export const ActionChecklistTable: React.FC = () => {
  const { checklistEn, checklistHi, selectedLang, toggleChecklistItem, structuredNotice, summaryEn, summaryHi } = useNotice();
  const [isExporting, setIsExporting] = useState(false);

  const checklist = selectedLang === 'hi' ? checklistHi : checklistEn;
  const summary = selectedLang === 'hi' ? summaryHi : summaryEn;
  if (!checklist || checklist.items.length === 0) return null;

  const totalItems = checklist.items.length;
  const completedItems = checklist.items.filter((i) => i.is_completed).length;
  const progressPercent = Math.round((completedItems / totalItems) * 100);

  const handleDownloadMarkdown = async () => {
    if (!structuredNotice) return;
    setIsExporting(true);
    try {
      const blob = await apiClient.exportMarkdown(structuredNotice, summary || undefined, checklist);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'notice2action_plan.md';
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to export Markdown', err);
    } finally {
      setIsExporting(false);
    }
  };

  const handleDownloadIcs = async () => {
    setIsExporting(true);
    try {
      const blob = await apiClient.exportIcs(checklist, structuredNotice?.purpose.value || 'Notice Deadline');
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
      eligibility: 'bg-indigo-950/80 text-indigo-400 border-indigo-800',
      documents: 'bg-blue-950/80 text-blue-400 border-blue-800',
      application: 'bg-sky-950/80 text-sky-400 border-sky-800',
      submission: 'bg-emerald-950/80 text-emerald-400 border-emerald-800',
      clarification: 'bg-amber-950/80 text-amber-400 border-amber-800',
    };
    const style = colors[cat] || 'bg-slate-800 text-slate-400 border-slate-700';
    return (
      <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${style}`}>
        {cat}
      </span>
    );
  };

  return (
    <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-5 space-y-4">
      {/* Header and Progress */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#1D2D4E]">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <CheckSquare className="w-4 h-4 text-blue-400" />
            {selectedLang === 'hi' ? 'कार्रवाई योग्य चेकलिस्ट' : 'Sequential Action Checklist'}
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            {selectedLang === 'hi'
              ? 'सत्यापित सूचना तथ्यों से प्राप्त आवश्यक चरण।'
              : 'Actionable steps derived strictly from verified facts.'}
          </p>
        </div>

        {/* Progress Tracker */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-xs font-mono font-bold text-slate-200">
              {completedItems} / {totalItems} Done ({progressPercent}%)
            </div>
            <div className="w-32 h-2 bg-slate-800 rounded-full overflow-hidden mt-1">
              <div
                className="h-full bg-blue-500 transition-all duration-300"
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
            onClick={() => toggleChecklistItem(item.step_number)}
            className={`p-3.5 rounded-lg border transition-all cursor-pointer flex items-start gap-3 select-none ${
              item.is_completed
                ? 'bg-[#070B14]/40 border-slate-800/80 text-slate-500'
                : 'bg-[#0D1528] border-[#1D2D4E] hover:border-blue-500/50 text-slate-200'
            }`}
          >
            <div className="pt-0.5 shrink-0 text-blue-400">
              {item.is_completed ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
              ) : (
                <Square className="w-5 h-5 text-slate-500 hover:text-blue-400 transition" />
              )}
            </div>

            <div className="flex-1 space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-xs font-bold text-slate-400">
                  Step {item.step_number}
                </span>
                {getCategoryBadge(item.category)}
                <span
                  className={`text-[10px] font-bold uppercase px-1.5 py-0.2 rounded ${
                    item.is_mandatory
                      ? 'bg-rose-950/60 text-rose-400 border border-rose-900/50'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {item.is_mandatory ? 'Mandatory' : 'Advisory'}
                </span>
              </div>

              <div
                className={`text-sm font-semibold transition ${
                  item.is_completed ? 'line-through text-slate-500' : 'text-slate-100'
                }`}
              >
                {item.action}
              </div>

              {item.grounded_quote && !item.is_completed && (
                <div className="text-xs text-slate-400 italic flex items-center gap-1 font-mono pt-0.5">
                  <Quote className="w-3 h-3 text-blue-400 shrink-0" />
                  "{item.grounded_quote}"
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Export Action Bar */}
      <div className="pt-3 border-t border-[#1D2D4E] flex flex-wrap items-center justify-between gap-3">
        <span className="text-xs text-slate-400">
          Save action steps or sync closing deadlines to your digital calendar.
        </span>

        <div className="flex items-center gap-2">
          <button
            onClick={handleDownloadMarkdown}
            disabled={isExporting}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-200 bg-[#111A33] hover:bg-[#1A264A] border border-[#1D2D4E] transition"
          >
            <FileDown className="w-3.5 h-3.5 text-blue-400" />
            Download Markdown (.md)
          </button>

          <button
            onClick={handleDownloadIcs}
            disabled={isExporting}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 transition shadow-sm"
          >
            <Calendar className="w-3.5 h-3.5" />
            Add to Calendar (.ics)
          </button>
        </div>
      </div>
    </div>
  );
};
