import React, { useState, useEffect, useCallback } from 'react';
import { useNotice } from '../context/NoticeContext';
import { apiClient } from '../services/apiClient';
import type {
  WorkspaceTimelineReport,
} from '../types/api';
import {
  Layers,
  GitBranch,
  Calendar,
  FileText,
  Plus,
  Trash2,
  Search,
  Sparkles,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react';

export const CrossNoticeTimelineView: React.FC = () => {
  const { openEvidenceInspector } = useNotice();
  const [report, setReport] = useState<WorkspaceTimelineReport | null>(null);
  const [newNoticeTitle, setNewNoticeTitle] = useState<string>('');
  const [newNoticeText, setNewNoticeText] = useState<string>('');
  const [isAddModalOpen, setIsAddModalOpen] = useState<boolean>(false);

  const fetchWorkspaceReport = useCallback(async () => {
    try {
      const data = await apiClient.getWorkspaceTimeline();
      setReport(data);
    } catch (err) {
      console.error('Failed to load workspace timeline:', err);
    }
  }, []);

  useEffect(() => {
    fetchWorkspaceReport();
  }, [fetchWorkspaceReport]);

  const handleAddNotice = async () => {
    if (!newNoticeText.trim()) return;
    try {
      await apiClient.addWorkspaceNotice(newNoticeText.trim(), newNoticeTitle.trim() || undefined);
      setNewNoticeTitle('');
      setNewNoticeText('');
      setIsAddModalOpen(false);
      fetchWorkspaceReport();
    } catch (err) {
      console.error('Failed to add notice:', err);
    }
  };

  const handleClearWorkspace = async () => {
    if (window.confirm('Clear all notices from this multi-document workspace?')) {
      await apiClient.clearWorkspace();
      fetchWorkspaceReport();
    }
  };

  const handleLoadDemoPair = async () => {
    try {
      await apiClient.clearWorkspace();
      const orig = await apiClient.getSampleText('demo_upsc_scholarship.txt');
      await apiClient.addWorkspaceNotice(orig.content, 'UPSC Central Merit Scholarship 2026 (Advt. 04/2026)');

      const corr = await apiClient.getSampleText('demo_upsc_corrigendum.txt');
      await apiClient.addWorkspaceNotice(corr.content, 'Corrigendum to Advt. 04/2026 (Deadline & Fee Revision)');

      fetchWorkspaceReport();
    } catch (err) {
      console.error('Failed to load demo pair:', err);
    }
  };

  const notices = report?.notices || [];
  const relationships = report?.relationships || [];
  const timeline = report?.timeline || [];
  const conflicts = report?.conflicts || [];

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E1E7EE]">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-[#12233D] tracking-tight flex items-center gap-2.5">
            <Layers className="w-6 h-6 text-[#08785D]" />
            <span>Cross-Notice Intelligence & Document Timeline</span>
          </h1>
          <p className="text-xs sm:text-sm text-[#526176] mt-1">
            Map relationships between original notices, corrigenda, and amendments with timeline tracking.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <button
            type="button"
            onClick={handleLoadDemoPair}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-[#08785D] bg-[#E8F7F0] hover:bg-[#D4EFE3] border border-[#B7E7D2] transition cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5 text-[#08785D]" />
            <span>Load Corrigendum Demo Pair</span>
          </button>

          <button
            type="button"
            onClick={() => setIsAddModalOpen(true)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-[#08785D] hover:bg-[#06664E] transition cursor-pointer shadow-xs"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Notice</span>
          </button>

          {notices.length > 0 && (
            <button
              type="button"
              onClick={handleClearWorkspace}
              className="p-1.5 rounded-lg text-[#B42318] hover:bg-[#FEE8E7] border border-transparent hover:border-[#FCA5A5] transition cursor-pointer"
              title="Clear workspace"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Add Document Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
          <div className="bg-white border border-[#E1E7EE] rounded-2xl p-6 w-full max-w-xl space-y-4 shadow-2xl">
            <h2 className="text-sm font-bold text-[#12233D] flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#08785D]" />
              <span>Add Notice to Workspace</span>
            </h2>

            <div className="space-y-3">
              <div>
                <label className="text-[11px] font-bold text-[#526176] uppercase block mb-1">
                  Document Title (Optional)
                </label>
                <input
                  type="text"
                  value={newNoticeTitle}
                  onChange={(e) => setNewNoticeTitle(e.target.value)}
                  placeholder="e.g., Corrigendum No. 2 to Circular 44"
                  className="w-full text-xs bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg p-2.5 text-[#12233D] placeholder-[#68778B] focus:outline-hidden focus:border-[#08785D]"
                />
              </div>

              <div>
                <label className="text-[11px] font-bold text-[#526176] uppercase block mb-1">
                  Verbatim Notice Text
                </label>
                <textarea
                  value={newNoticeText}
                  onChange={(e) => setNewNoticeText(e.target.value)}
                  placeholder="Paste official notification, corrigendum, or gazette circular text here..."
                  className="w-full text-xs font-mono bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg p-3 text-[#12233D] placeholder-[#68778B] focus:outline-hidden focus:border-[#08785D] h-44"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setIsAddModalOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-[#526176] hover:text-[#12233D] bg-slate-100 transition cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleAddNotice}
                disabled={!newNoticeText.trim()}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-white bg-[#08785D] hover:bg-[#06664E] transition disabled:opacity-50 cursor-pointer shadow-xs"
              >
                Register Notice
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Unresolved Contradictions Warning Box */}
      {conflicts.length > 0 && (
        <div className="p-5 rounded-2xl bg-[#FFF4D6] border border-[#FDE68A] space-y-3 shadow-xs">
          <div className="flex items-center gap-2 text-[#92500A] font-bold text-sm">
            <ShieldAlert className="w-5 h-5 shrink-0" />
            <span>Unresolved Cross-Notice Contradictions Detected ({conflicts.length})</span>
          </div>
          <p className="text-xs text-[#92500A]/90 leading-relaxed">
            The workspace contains multiple official circulars that state conflicting terms without an explicit
            superseding corrigendum clause. Never assume newer upload order overrides earlier documents.
          </p>

          <div className="space-y-3 pt-2">
            {conflicts.map((cnf) => (
              <div
                key={cnf.id}
                className="p-3.5 rounded-xl bg-white border border-[#FDE68A] space-y-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-[#12233D]">{cnf.field_name} Conflict</span>
                  <span className="px-2 py-0.5 rounded-md bg-[#FFF4D6] text-[#92500A] border border-[#FDE68A] text-[10px] font-bold">
                    {cnf.conflict_severity}
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px]">
                  <div className="p-2.5 rounded-lg bg-[#F8FAFC] border border-[#E1E7EE]">
                    <span className="text-[#68778B] block">Notice A Value:</span>
                    <span className="text-[#12233D] font-medium">{cnf.value_a}</span>
                    <blockquote className="text-[#526176] italic mt-1 font-mono text-[10px]">
                      "{cnf.evidence_a}"
                    </blockquote>
                  </div>
                  <div className="p-2.5 rounded-lg bg-[#F8FAFC] border border-[#E1E7EE]">
                    <span className="text-[#68778B] block">Notice B Value:</span>
                    <span className="text-[#12233D] font-medium">{cnf.value_b}</span>
                    <blockquote className="text-[#526176] italic mt-1 font-mono text-[10px]">
                      "{cnf.evidence_b}"
                    </blockquote>
                  </div>
                </div>
                <p className="text-[11px] text-[#92500A] font-medium">
                  Resolution Guidance: {cnf.resolution_guidance}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Grid: Registered Notices & Relationships */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Workspace Notices Registry */}
        <div className="bg-white border border-[#E1E7EE] rounded-2xl p-5 space-y-4 lg:col-span-1 shadow-xs">
          <div className="flex items-center justify-between pb-3 border-b border-[#E1E7EE]">
            <h2 className="text-xs font-bold uppercase tracking-wider text-[#12233D] flex items-center gap-1.5">
              <FileText className="w-4 h-4 text-[#08785D]" />
              <span>Workspace Notices ({notices.length})</span>
            </h2>
          </div>

          {notices.length === 0 ? (
            <div className="text-center py-8 text-xs text-[#68778B] space-y-2">
              <p>No notices registered in this workspace yet.</p>
              <button
                type="button"
                onClick={handleLoadDemoPair}
                className="text-[#08785D] hover:underline font-semibold cursor-pointer"
              >
                Load demo circular pair
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {notices.map((n) => (
                <div
                  key={n.id}
                  className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-2 text-xs"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-bold text-[#12233D] text-xs leading-snug">{n.title}</h3>
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2] shrink-0">
                      {n.document_type}
                    </span>
                  </div>

                  <div className="text-[11px] text-[#526176] space-y-0.5">
                    {n.issuing_authority && (
                      <div className="truncate">Authority: {n.issuing_authority}</div>
                    )}
                    {n.reference_number && (
                      <div className="font-mono text-[#12233D]">Ref: {n.reference_number}</div>
                    )}
                    {n.notice_date && <div>Date: {n.notice_date}</div>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Relationships Graph & Chronological Timeline */}
        <div className="space-y-6 lg:col-span-2">
          {/* Inter-document Relationships */}
          <div className="bg-white border border-[#E1E7EE] rounded-2xl p-5 space-y-4 shadow-xs">
            <h2 className="text-xs font-bold uppercase tracking-wider text-[#12233D] flex items-center gap-1.5 pb-3 border-b border-[#E1E7EE]">
              <GitBranch className="w-4 h-4 text-[#08785D]" />
              <span>Inter-Notice Relationship Graph</span>
            </h2>

            {relationships.length === 0 ? (
              <p className="text-xs text-[#68778B] py-4 text-center">
                Add at least two notices to map administrative relationships.
              </p>
            ) : (
              <div className="space-y-3">
                {relationships.map((rel) => {
                  const isVerified = rel.confidence_level === 'VERIFIED';
                  const isAmendment = rel.relationship_type === 'AMENDMENT' || rel.relationship_type === 'EXTENSION';

                  return (
                    <div
                      key={rel.id}
                      className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-3 text-xs"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2 font-bold text-[#12233D]">
                          <span>{rel.source_notice_id}</span>
                          <ArrowRight className="w-3.5 h-3.5 text-[#08785D]" />
                          <span>{rel.target_notice_id}</span>
                        </div>

                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase ${
                              isAmendment
                                ? 'bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]'
                                : 'bg-slate-100 text-[#526176]'
                            }`}
                          >
                            {rel.relationship_type}
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded-md text-[10px] font-semibold ${
                              isVerified
                                ? 'bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]'
                                : 'bg-slate-100 text-[#526176]'
                            }`}
                          >
                            {rel.confidence_level}
                          </span>
                        </div>
                      </div>

                      <p className="text-[#526176] text-xs leading-relaxed">{rel.rationale}</p>

                      {rel.evidence_quote && (
                        <div className="flex items-center justify-between pt-2 border-t border-slate-200">
                          <blockquote className="text-[11px] text-[#526176] italic truncate max-w-md">
                            "{rel.evidence_quote}"
                          </blockquote>
                          {openEvidenceInspector && (
                            <button
                              type="button"
                              onClick={() =>
                                openEvidenceInspector({
                                  excerpt: rel.evidence_quote,
                                  claim: `Cross-notice ${rel.relationship_type} relationship`,
                                  docTitle: 'Cross-Notice Workspace',
                                })
                              }
                              className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#08785D] hover:underline transition cursor-pointer shrink-0"
                            >
                              <Search className="w-3 h-3" />
                              <span>Inspect Citation</span>
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Chronological Timeline */}
          <div className="bg-white border border-[#E1E7EE] rounded-2xl p-5 space-y-4 shadow-xs">
            <h2 className="text-xs font-bold uppercase tracking-wider text-[#12233D] flex items-center gap-1.5 pb-3 border-b border-[#E1E7EE]">
              <Calendar className="w-4 h-4 text-[#08785D]" />
              <span>Chronological Event Evolution</span>
            </h2>

            {timeline.length === 0 ? (
              <p className="text-xs text-[#68778B] py-4 text-center">No timeline events recorded.</p>
            ) : (
              <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#E1E7EE]">
                {timeline.map((evt) => (
                  <div key={evt.id} className="relative space-y-1 text-xs">
                    <div className="absolute -left-6 top-1 w-2.5 h-2.5 rounded-full bg-[#08785D] ring-4 ring-[#E8F7F0]" />
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[#08785D] text-[11px]">{evt.date}</span>
                      <span className="text-[10px] uppercase font-bold text-[#68778B]">
                        {evt.event_type}
                      </span>
                    </div>
                    <div className="font-semibold text-[#12233D]">{evt.notice_title}</div>
                    <p className="text-[#526176] text-xs">{evt.summary}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
