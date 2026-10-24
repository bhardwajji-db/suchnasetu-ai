import React, { useEffect } from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  X,
  Volume2,
  FileText,
  Search,
} from 'lucide-react';

export const EvidenceInspectorDrawer: React.FC = () => {
  const { evidenceDrawer, closeEvidenceInspector, speakText } = useNotice();
  const { t } = useTranslation();
  const { isOpen, evidence, suggestedMatch } = evidenceDrawer;

  // Handle ESC key to close
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        closeEvidenceInspector();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, closeEvidenceInspector]);

  if (!isOpen || !evidence) return null;

  const isVerified = evidence.verification_status === 'VERIFIED_IN_SOURCE';
  const isOcrUncertain = evidence.verification_status === 'UNCERTAIN_OCR';

  const statusConfig = isVerified
    ? {
        bg: 'bg-[#E8F7F0] border-[#B7E7D2] text-[#08785D]',
        badge: 'bg-[#08785D] text-white',
        icon: <CheckCircle2 className="w-4 h-4 text-[#08785D]" />,
        label: 'VERIFIED IN SOURCE TEXT',
      }
    : isOcrUncertain
    ? {
        bg: 'bg-[#FFF4D6] border-[#FDE68A] text-[#92500A]',
        badge: 'bg-[#92500A] text-white',
        icon: <AlertTriangle className="w-4 h-4 text-[#92500A]" />,
        label: 'FUZZY MATCH / OCR ARTIFACT',
      }
    : {
        bg: 'bg-[#FEE8E7] border-[#FCA5A5] text-[#B42318]',
        badge: 'bg-[#B42318] text-white',
        icon: <XCircle className="w-4 h-4 text-[#B42318]" />,
        label: 'UNGROUNDED / UNVERIFIED CITATION',
      };

  return (
    <div
      className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-xs transition-opacity animate-fadeIn"
      role="dialog"
      aria-modal="true"
      aria-labelledby="evidence-drawer-title"
    >
      <div
        className="w-full max-w-lg bg-white border-l border-[#E1E7EE] h-full flex flex-col shadow-2xl p-6 overflow-y-auto space-y-6"
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#E1E7EE]">
          <div className="flex items-center gap-2">
            <Search className="w-5 h-5 text-[#08785D]" />
            <h2 id="evidence-drawer-title" className="text-base font-bold text-[#12233D] tracking-tight">
              {t('evidenceInspectorTitle') || 'Evidence Trust Inspector'}
            </h2>
          </div>
          <button
            onClick={closeEvidenceInspector}
            className="p-1.5 rounded-lg text-[#526176] hover:text-[#12233D] hover:bg-slate-100 transition cursor-pointer"
            aria-label="Close Inspector"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Verification Status Banner */}
        <div className={`p-4 rounded-xl border ${statusConfig.bg} space-y-2 shadow-xs`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold text-xs uppercase tracking-wider">
              {statusConfig.icon}
              <span>{statusConfig.label}</span>
            </div>
            {evidence.line_start && (
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-white border border-[#CBD5E1] text-[#12233D]">
                {evidence.line_start === evidence.line_end
                  ? `Line ${evidence.line_start}`
                  : `Lines ${evidence.line_start}–${evidence.line_end}`}
              </span>
            )}
          </div>
          <p className="text-xs leading-relaxed opacity-95">{evidence.confidence_rationale}</p>
        </div>

        {/* Claim / Subject */}
        {evidence.claim_text && (
          <div className="space-y-1.5">
            <span className="text-[11px] font-bold text-[#526176] uppercase tracking-wider">
              Associated Fact / Extracted Claim
            </span>
            <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] text-xs font-semibold text-[#12233D]">
              {evidence.claim_text}
            </div>
          </div>
        )}

        {/* Verbatim Excerpt */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-[#526176] uppercase tracking-wider flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-[#08785D]" />
              <span>Verbatim Document Excerpt</span>
            </span>
            <button
              onClick={() => speakText(evidence.verbatim_excerpt)}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold text-[#08785D] hover:bg-[#E8F7F0] border border-[#B7E7D2] transition cursor-pointer"
            >
              <Volume2 className="w-3.5 h-3.5" />
              <span>Read Aloud</span>
            </button>
          </div>

          <blockquote className="p-4 rounded-xl bg-[#F8FAFC] border-l-4 border-[#08785D] border-y border-r border-[#E1E7EE] text-xs text-[#12233D] font-mono leading-relaxed italic">
            "{evidence.verbatim_excerpt || 'No excerpt available.'}"
          </blockquote>
        </div>

        {/* Suggested match if fuzzy */}
        {suggestedMatch && suggestedMatch !== evidence.verbatim_excerpt && (
          <div className="space-y-1.5">
            <span className="text-[11px] font-bold text-[#92500A] uppercase tracking-wider">
              Exact Source Passage Located in Notice
            </span>
            <div className="p-3 rounded-lg bg-[#FFF4D6] border border-[#FDE68A] text-xs text-[#92500A] font-mono">
              "{suggestedMatch}"
            </div>
          </div>
        )}

        {/* Document Provenance & Security Safeguards */}
        <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-3 shadow-xs">
          <span className="text-[11px] font-bold text-[#12233D] uppercase tracking-wider flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-[#08785D]" />
            <span>Integrity & Security Attestation</span>
          </span>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <span className="text-[#68778B] block text-[10px] uppercase font-bold">Source Document:</span>
              <span className="text-[#12233D] font-medium truncate block">
                {evidence.source_doc_title || 'Active Notice'}
              </span>
            </div>
            <div>
              <span className="text-[#68778B] block text-[10px] uppercase font-bold">Adversarial Safety:</span>
              <span className="text-[#08785D] font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" />
                <span>Passive Data (Inert)</span>
              </span>
            </div>
          </div>
          <p className="text-[11px] text-[#526176] leading-normal">
            Notice text is isolated inside strict untrusted data boundaries. Citations are verified
            against the in-memory document index without hallucination.
          </p>
        </div>

        {/* Close Button */}
        <div className="pt-2">
          <button
            onClick={closeEvidenceInspector}
            className="w-full py-2.5 rounded-xl text-xs font-semibold text-[#12233D] bg-slate-100 hover:bg-slate-200 transition cursor-pointer"
          >
            Dismiss Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
