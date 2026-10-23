import React, { useState, useEffect, useCallback } from 'react';
import { useNotice } from '../context/NoticeContext';
import { apiClient } from '../services/apiClient';
import type { ActionItem, ActionItemStatus } from '../types/api';
import {
  Compass,
  Clock,
  AlertOctagon,
  CreditCard,
  Download,
  ExternalLink,
  Volume2,
  Search,
  Filter,
  RefreshCw,
  CheckSquare,
  Info,
} from 'lucide-react';

export const PersonalizedActionNavigatorView: React.FC = () => {
  const {
    rawNoticeText,
    sessionId,
    applicantProfile,
    savedEligibility,
    actionPlan,
    setActionPlan,
    openEvidenceInspector,
    speakText,
    setActiveTab,
  } = useNotice();

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);
  const [tempNote, setTempNote] = useState<string>('');

  const fetchOrGeneratePlan = useCallback(async () => {
    if (!rawNoticeText) return;
    setIsLoading(true);
    try {
      const plan = await apiClient.generateActionPlan({
        sessionId: sessionId || undefined,
        noticeText: rawNoticeText,
        profile: applicantProfile,
        eligibility: savedEligibility || undefined,
      });
      setActionPlan(plan);
    } catch (err) {
      console.error('Failed to generate action plan:', err);
    } finally {
      setIsLoading(false);
    }
  }, [rawNoticeText, sessionId, applicantProfile, savedEligibility, setActionPlan]);

  useEffect(() => {
    if (!actionPlan && rawNoticeText) {
      fetchOrGeneratePlan();
    }
  }, [actionPlan, rawNoticeText, fetchOrGeneratePlan]);

  const handleToggleStatus = async (item: ActionItem) => {
    if (!actionPlan) return;
    const newStatus: ActionItemStatus = item.status === 'COMPLETED' ? 'PENDING' : 'COMPLETED';
    try {
      const updated = await apiClient.updateActionStatus(actionPlan, item.id, newStatus);
      setActionPlan(updated);
    } catch (err) {
      console.error('Failed to update action status:', err);
    }
  };

  const handleSaveNote = async (item: ActionItem) => {
    if (!actionPlan) return;
    try {
      const updated = await apiClient.updateActionStatus(actionPlan, item.id, item.status, tempNote);
      setActionPlan(updated);
      setEditingNoteId(null);
    } catch (err) {
      console.error('Failed to save action note:', err);
    }
  };

  const exportMarkdown = () => {
    if (!actionPlan) return;
    let md = `# Personalized Notice-to-Action Plan\n\n`;
    md += `**Document:** ${actionPlan.notice_title}\n`;
    md += `**Progress:** ${actionPlan.completed_count}/${actionPlan.total_count} (${actionPlan.overall_progress_percentage}% Completed)\n`;
    md += `**Last Updated:** ${actionPlan.last_updated}\n\n`;
    md += `## Action Roadmap\n\n`;

    actionPlan.items.forEach((item, idx) => {
      const statusMark = item.status === 'COMPLETED' ? '[x]' : '[ ]';
      md += `### ${idx + 1}. ${statusMark} ${item.title} (${item.status})\n`;
      md += `- **Explanation**: ${item.explanation}\n`;
      md += `- **Category**: ${item.category}\n`;
      if (item.deadline) md += `- **Deadline**: ${item.deadline}\n`;
      if (item.fee_amount) md += `- **Fee Payable**: ${item.fee_amount}\n`;
      if (item.official_portal_url) md += `- **Portal URL**: ${item.official_portal_url}\n`;
      if (item.user_notes) md += `- **Personal Notes**: ${item.user_notes}\n`;
      md += `\n`;
    });

    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Action_Plan_${actionPlan.notice_title ? actionPlan.notice_title.replace(/\s+/g, '_') : 'Notice'}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!rawNoticeText) {
    return (
      <div className="bg-white border border-[#E1E7EE] rounded-2xl p-12 text-center space-y-4 shadow-xs">
        <div className="w-12 h-12 rounded-xl bg-[#E8F7F0] border border-[#B7E7D2] text-[#08785D] flex items-center justify-center mx-auto">
          <Compass className="w-6 h-6" />
        </div>
        <h2 className="text-base font-bold text-[#12233D]">No Notice Loaded for Action Planning</h2>
        <p className="text-xs text-[#526176] max-w-md mx-auto">
          Please upload or paste an official notice first to synthesize your customized step-by-step preparation plan.
        </p>
        <div>
          <button
            type="button"
            onClick={() => setActiveTab(1)}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs cursor-pointer"
          >
            <span>Go to Notice Ingestion</span>
          </button>
        </div>
      </div>
    );
  }

  const items = actionPlan?.items || [];
  const filteredItems = selectedCategory === 'ALL'
    ? items
    : items.filter((i) => i.category === selectedCategory);

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E1E7EE]">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-[#12233D] tracking-tight flex items-center gap-2.5">
            <Compass className="w-6 h-6 text-[#08785D]" />
            <span>Personalized Notice Action Navigator</span>
          </h1>
          <p className="text-xs sm:text-sm text-[#526176] mt-1">
            Personal sequential roadmap tailored to your eligibility profile with live deadline tracking.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <button
            type="button"
            onClick={fetchOrGeneratePlan}
            disabled={isLoading}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-[#12233D] bg-white border border-[#CBD5E1] hover:bg-[#F8FAFC] transition cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-[#08785D] ${isLoading ? 'animate-spin' : ''}`} />
            <span>Regenerate Plan</span>
          </button>

          {actionPlan && (
            <button
              type="button"
              onClick={exportMarkdown}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export Checklist (.md)</span>
            </button>
          )}
        </div>
      </div>

      {/* Progress & Document Overview Banner */}
      {actionPlan && (
        <div className="bg-white border border-[#E1E7EE] rounded-2xl p-5 shadow-xs space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#08785D] block">
                Target Notice Document
              </span>
              <h2 className="text-sm font-bold text-[#12233D]">{actionPlan.notice_title}</h2>
            </div>

            <div className="text-right">
              <span className="text-xs font-mono font-bold text-[#12233D]">
                {actionPlan.completed_count} / {actionPlan.total_count} Completed ({actionPlan.overall_progress_percentage}%)
              </span>
            </div>
          </div>

          <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden border border-slate-200">
            <div
              className="h-full bg-[#08785D] transition-all duration-300 rounded-full"
              style={{ width: `${actionPlan.overall_progress_percentage}%` }}
            />
          </div>
        </div>
      )}

      {/* Official Submission Disclaimer */}
      <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] flex items-center gap-2.5 text-xs text-[#526176]">
        <Info className="w-4 h-4 text-[#08785D] shrink-0" />
        <span>
          <strong>Disclaimer:</strong> Completing items in this personal preparation roadmap does not constitute official submission to the issuing authority. Always submit via authorized official portals.
        </span>
      </div>

      {/* Category Filter Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        <span className="font-bold text-[#526176] flex items-center gap-1 mr-1">
          <Filter className="w-3.5 h-3.5 text-[#08785D]" /> Category:
        </span>
        {[
          { key: 'ALL', label: 'All Actions' },
          { key: 'ELIGIBILITY_CHECK', label: 'Eligibility' },
          { key: 'DOCUMENT_PREPARATION', label: 'Documents' },
          { key: 'FEE_PAYMENT', label: 'Fees' },
          { key: 'APPLICATION_SUBMISSION', label: 'Submission' },
          { key: 'POST_SUBMISSION', label: 'Post-Submission' },
        ].map((f) => (
          <button
            key={f.key}
            type="button"
            onClick={() => setSelectedCategory(f.key)}
            className={`px-3 py-1.5 rounded-xl font-semibold transition cursor-pointer shrink-0 ${
              selectedCategory === f.key
                ? 'bg-[#08785D] text-white shadow-xs'
                : 'bg-white text-[#526176] hover:text-[#12233D] border border-[#CBD5E1]'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Action Items List */}
      <div className="space-y-3">
        {filteredItems.map((item) => {
          const isDone = item.status === 'COMPLETED';
          const isBlocked = item.status === 'BLOCKED';

          return (
            <div
              key={item.id}
              className={`p-4 rounded-xl border transition flex flex-col space-y-3 shadow-xs ${
                isDone
                  ? 'bg-slate-50/80 border-slate-200 text-[#68778B]'
                  : isBlocked
                  ? 'bg-[#FEE8E7]/30 border-[#FCA5A5]'
                  : 'bg-white border-[#E1E7EE] hover:border-[#B7E7D2]'
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 min-w-0">
                  <button
                    type="button"
                    onClick={() => handleToggleStatus(item)}
                    disabled={isBlocked}
                    className={`mt-0.5 shrink-0 w-5 h-5 rounded-md flex items-center justify-center transition border cursor-pointer ${
                      isDone
                        ? 'bg-[#08785D] border-[#08785D] text-white'
                        : isBlocked
                        ? 'bg-slate-100 border-slate-300 text-slate-400 cursor-not-allowed'
                        : 'bg-white border-[#CBD5E1] hover:border-[#08785D] text-transparent'
                    }`}
                    aria-label={`Mark ${item.title} as ${isDone ? 'incomplete' : 'completed'}`}
                  >
                    <CheckSquare className="w-3.5 h-3.5 fill-current" />
                  </button>

                  <div className="space-y-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-[11px] font-mono text-[#68778B]">{item.id}</span>
                      <h3
                        className={`text-sm font-bold ${
                          isDone ? 'line-through text-[#68778B]' : 'text-[#12233D]'
                        }`}
                      >
                        {item.title}
                      </h3>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-md uppercase tracking-wider bg-slate-100 text-[#526176]">
                        {item.category.replace('_', ' ')}
                      </span>
                      {isBlocked && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-[#FEE8E7] text-[#B42318] border border-[#FCA5A5] flex items-center gap-1">
                          <AlertOctagon className="w-3 h-3" />
                          <span>BLOCKED</span>
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-[#526176] leading-relaxed">{item.explanation}</p>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 shrink-0">
                  {speakText && (
                    <button
                      type="button"
                      onClick={() => speakText(`${item.title}. ${item.explanation}`)}
                      className="p-1.5 rounded-lg text-[#68778B] hover:text-[#08785D] hover:bg-slate-100 transition cursor-pointer"
                      title="Read action aloud"
                    >
                      <Volume2 className="w-4 h-4" />
                    </button>
                  )}

                  {item.evidence && openEvidenceInspector && (
                    <button
                      type="button"
                      onClick={() => openEvidenceInspector(item.evidence!)}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-semibold text-[#08785D] bg-[#E8F7F0] hover:bg-[#D4EFE3] border border-[#B7E7D2] transition cursor-pointer"
                    >
                      <Search className="w-3 h-3" />
                      <span>Evidence</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Extra Details Row: Deadlines, Fees, Links, Dependencies */}
              <div className="pt-2 border-t border-slate-100 flex flex-wrap items-center gap-4 text-xs text-[#526176]">
                {item.deadline && (
                  <div className="flex flex-wrap items-center gap-2 font-medium">
                    <div className="flex items-center gap-1.5 text-[#92500A]">
                      <Clock className="w-3.5 h-3.5 text-[#92500A]" />
                      <span>Deadline: </span>
                      {item.superseded_deadline && (
                        <span className="line-through text-slate-400 mr-1 text-[11px]">
                          {item.superseded_deadline}
                        </span>
                      )}
                      <span className="font-bold text-[#12233D]">{item.deadline}</span>
                    </div>

                    {item.remaining_time && (
                      <span className="text-[11px] font-mono text-[#526176]">
                        ({item.remaining_time})
                      </span>
                    )}

                    {item.deadline_status && (
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${
                          item.deadline_status === 'Due today'
                            ? 'bg-[#FEE8E7] text-[#B42318] border-[#FCA5A5] animate-pulse'
                            : item.deadline_status === 'Due soon'
                            ? 'bg-[#FFF4D6] text-[#92500A] border-[#FDE68A]'
                            : item.deadline_status === 'Upcoming'
                            ? 'bg-[#E8F7F0] text-[#08785D] border-[#B7E7D2]'
                            : item.deadline_status === 'Superseded by a verified newer notice'
                            ? 'bg-[#EAF2FF] text-[#245DC1] border-[#BFDBFE]'
                            : 'bg-slate-100 text-slate-600 border-slate-300'
                        }`}
                      >
                        {item.deadline_status}
                      </span>
                    )}
                  </div>
                )}

                {item.fee_amount && (
                  <div className="flex items-center gap-1.5 text-[#08785D] font-medium">
                    <CreditCard className="w-3.5 h-3.5 text-[#08785D]" />
                    <span>Fee: {item.fee_amount}</span>
                  </div>
                )}

                {item.official_portal_url && (
                  <a
                    href={item.official_portal_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-[#245DC1] hover:underline font-medium"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span>Official Portal</span>
                  </a>
                )}

                {item.dependencies.length > 0 && (
                  <div className="text-[11px] text-[#68778B]">
                    Prerequisites: {item.dependencies.join(', ')}
                  </div>
                )}

                {item.completed_at && (
                  <div className="text-[11px] text-[#08785D]">
                    Completed at: {item.completed_at}
                  </div>
                )}
              </div>

              {/* User Notes Section */}
              {editingNoteId === item.id ? (
                <div className="space-y-2 pt-2">
                  <textarea
                    value={tempNote}
                    onChange={(e) => setTempNote(e.target.value)}
                    placeholder="Add personal application notes, reference numbers, or submission remarks..."
                    className="w-full text-xs bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg p-2 text-[#12233D] placeholder-[#68778B] focus:outline-hidden focus:border-[#08785D]"
                    rows={2}
                  />
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => handleSaveNote(item)}
                      className="px-3 py-1 rounded-lg text-xs font-semibold text-white bg-[#08785D] hover:bg-[#06664E] transition cursor-pointer"
                    >
                      Save Note
                    </button>
                    <button
                      type="button"
                      onClick={() => setEditingNoteId(null)}
                      className="px-3 py-1 rounded-lg text-xs font-semibold text-[#526176] hover:text-[#12233D] bg-slate-100 transition cursor-pointer"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : item.user_notes ? (
                <div
                  onClick={() => {
                    setEditingNoteId(item.id);
                    setTempNote(item.user_notes || '');
                  }}
                  className="p-2.5 rounded-lg bg-[#F8FAFC] border border-[#E1E7EE] text-xs text-[#526176] cursor-pointer hover:border-[#CBD5E1] transition flex items-center justify-between"
                >
                  <div>
                    <span className="text-[10px] font-bold text-[#68778B] block uppercase">Your Notes</span>
                    <span>{item.user_notes}</span>
                  </div>
                  <span className="text-[11px] text-[#08785D]">Edit</span>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => {
                    setEditingNoteId(item.id);
                    setTempNote('');
                  }}
                  className="text-[11px] text-[#68778B] hover:text-[#08785D] transition self-start cursor-pointer"
                >
                  + Add personal note / tracking number
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
