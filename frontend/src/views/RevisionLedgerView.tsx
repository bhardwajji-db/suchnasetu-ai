import React, { useState } from 'react';
import { useNotice } from '../context/NoticeContext';
import { apiClient } from '../services/apiClient';
import type { RevisionLedger, ChangeCategory, PersonalImpactReport, PersonalImpactItem } from '../types/api';
import {
  GitCompare,
  FileText,
  AlertCircle,
  ArrowRight,
  Sparkles,
  Download,
  Filter,
  RefreshCw,
  UserCheck,
  Volume2,
  ArrowUpRight,
  Search,
} from 'lucide-react';

export const RevisionLedgerView: React.FC = () => {
  const { rawNoticeText, sessionId, applicantProfile, speakText, openEvidenceInspector, setActiveTab } = useNotice();
  const [personalImpact, setPersonalImpact] = useState<PersonalImpactReport | null>(null);
  const [sourceText, setSourceText] = useState<string>(rawNoticeText || '');
  const [targetText, setTargetText] = useState<string>('');
  const [isComparing, setIsComparing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [ledger, setLedger] = useState<RevisionLedger | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<ChangeCategory | 'ALL'>('ALL');

  const handleLoadDemo = async () => {
    try {
      setError(null);
      const base = await apiClient.getSampleText('demo_upsc_scholarship.txt');
      const corr = await apiClient.getSampleText('demo_upsc_corrigendum.txt');
      setSourceText(base.content);
      setTargetText(corr.content);
    } catch (e: any) {
      setError(`Failed to load demo fixtures: ${e.message}`);
    }
  };

  const handleCompare = async () => {
    if (!sourceText.trim() || !targetText.trim()) {
      setError('Please provide text for both the original notice and the revised circular.');
      return;
    }

    setIsComparing(true);
    setError(null);

    try {
      const res = await apiClient.compareRevisionLedger(
        sessionId || undefined,
        undefined,
        sourceText.trim(),
        targetText.trim()
      );
      setLedger(res);
      if (applicantProfile) {
        try {
          const impactRes = await apiClient.evaluatePersonalImpact({
            profile: applicantProfile,
            revisionLedger: res,
          });
          setPersonalImpact(impactRes);
        } catch (impactErr) {
          console.warn('Personal impact evaluation skipped:', impactErr);
        }
      }
    } catch (e: any) {
      setError(e.message || 'Comparison failed. Please verify local AI connection.');
    } finally {
      setIsComparing(false);
    }
  };

  const handleExportMarkdown = () => {
    if (!ledger) return;
    const lines = [
      `# Notice Revision Ledger: ${ledger.source_title} vs ${ledger.target_title}`,
      `Generated: ${ledger.created_at}`,
      `Relationship: ${ledger.relationship.relationship_type} (${ledger.relationship.confidence} confidence)`,
      `Evidence: "${ledger.relationship.evidence_quote}"`,
      '',
      `## Summary of Changes`,
      ledger.summary_of_changes,
      '',
      `## Field-by-Field Revision Delta`,
      '| Field | Original Value | Revised Value | Category | Verification Note |',
      '| :--- | :--- | :--- | :--- | :--- |',
    ];

    ledger.entries.forEach((e) => {
      lines.push(
        `| **${e.display_name}** | ${e.old_value.replace(/\|/g, '-')} | ${e.new_value.replace(/\|/g, '-')} | \`${e.change_category}\` | ${e.explanation} |`
      );
    });

    const blob = new Blob([lines.join('\n')], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'notice_revision_ledger.md';
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredEntries = ledger?.entries.filter((entry) => {
    if (selectedFilter === 'ALL') return true;
    return entry.change_category === selectedFilter;
  }) || [];

  const getCategoryBadge = (cat: ChangeCategory) => {
    switch (cat) {
      case 'MODIFIED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-bold bg-[#FFF4D6] text-[#92500A] border border-[#FDE68A]">
            MODIFIED
          </span>
        );
      case 'ADDED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-bold bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]">
            ADDED
          </span>
        );
      case 'REMOVED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-bold bg-[#FEE8E7] text-[#B42318] border border-[#FCA5A5]">
            REMOVED
          </span>
        );
      case 'UNCHANGED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-bold bg-slate-100 text-[#526176] border border-slate-200">
            UNCHANGED
          </span>
        );
      case 'UNCERTAIN':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-bold bg-[#FFF4D6] text-[#92500A] border border-[#FDE68A]">
            UNCERTAIN
          </span>
        );
      default:
        return null;
    }
  };

  const getRelationshipColor = (relType: string) => {
    switch (relType) {
      case 'AMENDMENT':
        return 'border-[#B7E7D2] bg-[#E8F7F0] text-[#08785D]';
      case 'EXTENSION':
        return 'border-[#BFDBFE] bg-[#EAF2FF] text-[#245DC1]';
      case 'CANCELLATION':
        return 'border-[#FCA5A5] bg-[#FEE8E7] text-[#B42318]';
      case 'REPLACEMENT':
        return 'border-[#DDD6FE] bg-[#F5F3FF] text-[#6D28D9]';
      default:
        return 'border-[#E1E7EE] bg-[#F8FAFC] text-[#526176]';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-[#E1E7EE]">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-[#12233D] flex items-center gap-2.5">
            <GitCompare className="w-6 h-6 text-[#08785D]" />
            Multi-Notice Revision Ledger
          </h1>
          <p className="text-xs sm:text-sm text-[#526176] mt-1">
            Compare official advertisements with addenda, corrigenda, and extension notices with line-by-line verification.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleLoadDemo}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#E8F7F0] border border-[#B7E7D2] text-[#08785D] hover:bg-[#D4EFE3] transition cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Load Sample Corrigendum Demo
          </button>
          {ledger && (
            <button
              type="button"
              onClick={handleExportMarkdown}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-white border border-[#CBD5E1] hover:bg-[#F8FAFC] text-[#12233D] transition shadow-xs cursor-pointer"
            >
              <Download className="w-3.5 h-3.5 text-[#08785D]" />
              Export Markdown Ledger
            </button>
          )}
        </div>
      </div>

      {/* Input Split Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Notice A: Original */}
        <div className="bg-white border border-[#E1E7EE] rounded-xl p-4 flex flex-col space-y-2 shadow-xs">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold text-[#12233D] flex items-center gap-1.5">
              <FileText className="w-4 h-4 text-[#08785D]" />
              Original Notice (Base Circular)
            </label>
            <span className="text-[11px] text-[#68778B] font-mono">{sourceText.length} chars</span>
          </div>
          <textarea
            value={sourceText}
            onChange={(e) => setSourceText(e.target.value)}
            placeholder="Paste text of the original notification or base advertisement..."
            rows={7}
            className="w-full bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg p-3 text-xs text-[#12233D] font-mono focus:border-[#08785D] focus:outline-hidden transition resize-y"
          />
        </div>

        {/* Notice B: Corrigendum / Revised */}
        <div className="bg-white border border-[#E1E7EE] rounded-xl p-4 flex flex-col space-y-2 shadow-xs">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold text-[#12233D] flex items-center gap-1.5">
              <GitCompare className="w-4 h-4 text-[#08785D]" />
              Revised Circular / Corrigendum / Extension
            </label>
            <span className="text-[11px] text-[#68778B] font-mono">{targetText.length} chars</span>
          </div>
          <textarea
            value={targetText}
            onChange={(e) => setTargetText(e.target.value)}
            placeholder="Paste text of the corrigendum, addendum, or extension notice..."
            rows={7}
            className="w-full bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg p-3 text-xs text-[#12233D] font-mono focus:border-[#08785D] focus:outline-hidden transition resize-y"
          />
        </div>
      </div>

      {/* Action Button */}
      <div className="flex justify-center">
        <button
          type="button"
          onClick={handleCompare}
          disabled={isComparing}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold text-sm transition shadow-xs ${
            isComparing
              ? 'bg-[#08785D]/60 text-white cursor-not-allowed'
              : 'bg-[#08785D] hover:bg-[#06664E] text-white cursor-pointer'
          }`}
        >
          {isComparing ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Analyzing & Diffing Circulars...
            </>
          ) : (
            <>
              <GitCompare className="w-4 h-4" />
              Compare Notice Versions & Build Ledger
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-[#FEE8E7] border border-[#FCA5A5] text-xs text-[#B42318] flex items-center gap-2.5">
          <AlertCircle className="w-4 h-4 text-[#B42318] shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Results Workspace */}
      {ledger && (
        <div className="space-y-5">
          {/* Relationship Badge Card */}
          <div className={`p-4 rounded-xl border ${getRelationshipColor(ledger.relationship.relationship_type)}`}>
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <span className="text-xs font-bold uppercase tracking-wider text-[#526176]">
                  Detected Relationship:
                </span>
                <span className="px-3 py-1 rounded-full text-xs font-extrabold uppercase bg-[#08785D] text-white shadow-xs">
                  {ledger.relationship.relationship_type}
                </span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-white text-[#12233D] border border-[#CBD5E1]">
                  Confidence: {ledger.relationship.confidence}
                </span>
              </div>
              <span className="text-xs text-[#526176] italic">{ledger.relationship.explanation}</span>
            </div>

            {ledger.relationship.evidence_quote && (
              <div className="mt-3 pt-3 border-t border-slate-200 text-xs">
                <span className="font-semibold text-[#526176]">Verbatim Citation: </span>
                <span className="font-mono text-[#12233D]">"{ledger.relationship.evidence_quote}"</span>
              </div>
            )}
          </div>

          {/* Change Summary Card */}
          <div className="p-4 rounded-xl bg-white border border-[#E1E7EE] flex items-center justify-between shadow-xs">
            <div className="space-y-1">
              <span className="text-xs font-bold uppercase tracking-wider text-[#08785D]">
                Revision Overview
              </span>
              <p className="text-sm font-semibold text-[#12233D]">{ledger.summary_of_changes}</p>
            </div>
            <div className="hidden md:flex items-center gap-2">
              <span className="text-xs text-[#68778B]">Total Fields: {ledger.entries.length}</span>
            </div>
          </div>

          {/* Personal Impact Change Tracker Panel */}
          {personalImpact && (
            <div className="bg-white border-2 border-[#08785D]/30 shadow-xs rounded-2xl p-5 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#E1E7EE]">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-xl bg-[#E8F7F0] text-[#08785D]">
                    <UserCheck className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-sm font-bold text-[#12233D] tracking-tight">
                        Personal Impact Change Tracker
                      </h2>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-md uppercase tracking-wider ${
                          personalImpact.impact_level === 'HIGH'
                            ? 'bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]'
                            : 'bg-[#EAF2FF] text-[#245DC1] border border-[#BFDBFE]'
                        }`}
                      >
                        {personalImpact.impact_level} IMPACT
                      </span>
                    </div>
                    <p className="text-xs text-[#526176] mt-0.5">
                      {personalImpact.overall_impact_summary}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-start sm:self-auto">
                  {speakText && (
                    <button
                      type="button"
                      onClick={() => speakText(personalImpact.overall_impact_summary)}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold text-[#526176] bg-[#F8FAFC] hover:bg-slate-200 transition cursor-pointer"
                    >
                      <Volume2 className="w-3.5 h-3.5" />
                      <span>Listen</span>
                    </button>
                  )}

                  <button
                    type="button"
                    onClick={() => setActiveTab(7)}
                    className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-[#08785D] hover:bg-[#06664E] transition cursor-pointer shadow-xs"
                  >
                    <span>Open Action Navigator</span>
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Personal Impact Items */}
              {personalImpact.impact_items.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                  {personalImpact.impact_items.map((item: PersonalImpactItem) => {
                    const isBeneficial = item.impact_type === 'BENEFICIAL';
                    const isAdverse = item.impact_type === 'ADVERSE';

                    return (
                      <div
                        key={item.id}
                        className={`p-3.5 rounded-xl border space-y-2 text-xs transition ${
                          isBeneficial
                            ? 'bg-[#E8F7F0]/40 border-[#B7E7D2]'
                            : isAdverse
                            ? 'bg-[#FEE8E7]/40 border-[#FCA5A5]'
                            : 'bg-[#F8FAFC] border-[#E1E7EE]'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded-md uppercase tracking-wider ${
                              isBeneficial
                                ? 'bg-[#E8F7F0] text-[#08785D]'
                                : isAdverse
                                ? 'bg-[#FEE8E7] text-[#B42318]'
                                : 'bg-slate-100 text-[#526176]'
                            }`}
                          >
                            {item.impact_type}
                          </span>
                          <span className="font-mono text-[10px] text-[#68778B]">{item.field_name}</span>
                        </div>

                        <h3 className="font-bold text-[#12233D] text-xs">{item.headline}</h3>
                        <p className="text-[#526176] leading-relaxed text-[11px]">{item.explanation}</p>

                        {item.required_user_action && (
                          <div className="pt-2 border-t border-slate-200 flex items-start justify-between gap-2">
                            <span className="text-[11px] font-semibold text-[#08785D]">
                              Action: {item.required_user_action}
                            </span>
                          </div>
                        )}

                        {item.evidence_new && openEvidenceInspector && (
                          <button
                            type="button"
                            onClick={() =>
                              openEvidenceInspector(
                                {
                                  excerpt: item.evidence_new!,
                                  claim: item.headline,
                                  docTitle: 'Corrigendum Notice',
                                },
                                targetText
                              )
                            }
                            className="inline-flex items-center gap-1 text-[10px] font-semibold text-[#08785D] hover:underline transition cursor-pointer pt-1"
                          >
                            <Search className="w-3 h-3" />
                            <span>Verify Citation in Corrigendum</span>
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-xs text-[#526176] py-2">
                  No personal eligibility or deadline conflicts detected against your active profile.
                </p>
              )}
            </div>
          )}

          {/* Filter Bar */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-bold text-[#526176] flex items-center gap-1.5 mr-1">
              <Filter className="w-3.5 h-3.5 text-[#08785D]" /> Filter Changes:
            </span>
            {(['ALL', 'MODIFIED', 'ADDED', 'REMOVED', 'UNCHANGED', 'UNCERTAIN'] as const).map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setSelectedFilter(cat)}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition cursor-pointer ${
                  selectedFilter === cat
                    ? 'bg-[#08785D] text-white shadow-xs'
                    : 'bg-white border border-[#CBD5E1] text-[#526176] hover:text-[#12233D]'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Comparison Cards / Table */}
          <div className="space-y-3">
            {filteredEntries.map((entry, idx) => (
              <div
                key={idx}
                className="bg-white border border-[#E1E7EE] rounded-xl p-4 space-y-3 hover:border-[#B7E7D2] transition shadow-xs"
              >
                <div className="flex items-center justify-between pb-2 border-b border-[#E1E7EE]">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-[#12233D]">{entry.display_name}</span>
                    {getCategoryBadge(entry.change_category)}
                  </div>
                  {entry.requires_review && (
                    <span className="text-xs font-semibold text-[#92500A] flex items-center gap-1">
                      <AlertCircle className="w-3.5 h-3.5" /> Requires Verification
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Original Value */}
                  <div className="p-3 rounded-lg bg-[#F8FAFC] border border-[#E1E7EE] space-y-1.5">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[#526176] block">
                      Original Notice Value
                    </span>
                    <p className="text-xs font-medium text-[#12233D]">{entry.old_value}</p>
                    {entry.old_evidence_quote && (
                      <div className="text-[11px] text-[#526176] italic pt-1 border-t border-slate-200 flex items-center justify-between">
                        <span className="truncate max-w-xs">"{entry.old_evidence_quote}"</span>
                        {openEvidenceInspector && (
                          <button
                            type="button"
                            onClick={() =>
                              openEvidenceInspector(
                                {
                                  excerpt: entry.old_evidence_quote!,
                                  claim: `${entry.display_name} in base notice`,
                                  docTitle: 'Original Notice',
                                },
                                sourceText
                              )
                            }
                            className="text-[10px] text-[#08785D] hover:underline shrink-0 ml-1 cursor-pointer"
                          >
                            Verify
                          </button>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Revised Value */}
                  <div className="p-3 rounded-lg bg-[#F8FAFC] border border-[#E1E7EE] space-y-1.5">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[#08785D] block">
                      Revised / Amended Value
                    </span>
                    <p className="text-xs font-bold text-[#12233D]">{entry.new_value}</p>
                    {entry.new_evidence_quote && (
                      <div className="text-[11px] text-[#526176] italic pt-1 border-t border-slate-200 flex items-center justify-between">
                        <span className="truncate max-w-xs">"{entry.new_evidence_quote}"</span>
                        {openEvidenceInspector && (
                          <button
                            type="button"
                            onClick={() =>
                              openEvidenceInspector(
                                {
                                  excerpt: entry.new_evidence_quote!,
                                  claim: `${entry.display_name} in corrigendum`,
                                  docTitle: 'Revised Notice',
                                },
                                targetText
                              )
                            }
                            className="text-[10px] text-[#08785D] hover:underline shrink-0 ml-1 cursor-pointer"
                          >
                            Verify
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {entry.explanation && (
                  <p className="text-xs text-[#526176] pt-1 flex items-center gap-1.5">
                    <ArrowRight className="w-3.5 h-3.5 text-[#08785D] shrink-0" />
                    <span>{entry.explanation}</span>
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
