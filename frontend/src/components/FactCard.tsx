import React from 'react';
import type { ExtractedFact } from '../types/api';
import { useNotice } from '../context/NoticeContext';
import { Quote, AlertCircle, CheckCircle, Check, Edit3 } from 'lucide-react';

interface FactCardProps {
  fact: ExtractedFact;
  fieldName: string;
  displayName: string;
}

export const FactCard: React.FC<FactCardProps> = ({ fact, fieldName, displayName }) => {
  const { openConfirmationModal } = useNotice();

  const getStatusBadge = () => {
    switch (fact.status) {
      case 'stated':
        return (
          <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800">
            Stated
          </span>
        );
      case 'not_stated':
        return (
          <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
            Not Stated
          </span>
        );
      case 'uncertain':
        return (
          <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-amber-950/80 text-amber-400 border border-amber-800">
            Uncertain
          </span>
        );
      case 'conflicting':
        return (
          <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-rose-950/80 text-rose-400 border border-rose-800">
            Conflicting
          </span>
        );
      default:
        return (
          <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-400">
            {fact.status}
          </span>
        );
    }
  };

  const hasCorrection = Boolean(fact.user_confirmed && fact.confirmed_value && fact.confirmed_value !== fact.value);
  const displayValue = fact.user_confirmed && fact.confirmed_value ? fact.confirmed_value : fact.value;

  return (
    <div className="bg-[#0D1528] border border-[#1D2D4E] hover:border-slate-700 transition rounded-xl p-5 flex flex-col justify-between shadow-sm">
      <div>
        <div className="flex items-center justify-between mb-2.5">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wide">
            {displayName}
          </h3>
          <div className="flex items-center gap-2">
            {fact.user_confirmed && (
              <span className="flex items-center gap-1 text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-blue-950/80 text-blue-400 border border-blue-800">
                <Check className="w-3 h-3" /> {hasCorrection ? 'Corrected' : 'Verified'}
              </span>
            )}
            {getStatusBadge()}
            {fact.uncertainty_type && !fact.user_confirmed && (
              <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-amber-950/50 text-amber-300 border border-amber-800/60" title={`Uncertainty cause: ${fact.uncertainty_type}`}>
                {fact.uncertainty_type.replace('_', ' ')}
              </span>
            )}
          </div>
        </div>

        {/* Fact Value */}
        <div className="text-base font-semibold text-white mb-2 leading-relaxed">
          {displayValue}
        </div>

        {/* Original Value if Corrected */}
        {hasCorrection && (
          <div className="text-[11px] text-slate-400 mb-2 italic">
            <span className="font-semibold text-slate-500 uppercase text-[9px] not-italic mr-1">
              Original:
            </span>
            "{fact.value}"
          </div>
        )}

        {/* Verbatim Evidence Quote */}
        {fact.evidence_quote && (
          <div className="mt-2.5 p-3 rounded-lg bg-[#070B14]/80 border-l-4 border-blue-500 text-xs text-slate-300 font-mono italic leading-relaxed">
            <div className="flex items-center gap-1 text-blue-400 font-sans font-bold text-[10px] uppercase mb-1">
              <Quote className="w-3 h-3" /> Grounded Evidence Quote
            </div>
            "{fact.evidence_quote}"
          </div>
        )}

        {/* Explanation / Uncertainty Warning */}
        {fact.explanation && (
          <div className="mt-2 p-2.5 rounded-lg bg-amber-950/40 border border-amber-800/40 text-xs text-amber-300 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div>{fact.explanation}</div>
          </div>
        )}
      </div>

      {/* Confirmation Actions */}
      <div className="mt-4 pt-3 border-t border-[#1D2D4E] flex items-center justify-between">
        {fact.requires_confirmation && !fact.user_confirmed ? (
          <>
            <span className="text-xs text-amber-400 font-medium">
              ⚠️ Needs review before action steps.
            </span>
            <button
              type="button"
              onClick={() => openConfirmationModal(fieldName, displayName, fact)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 transition shadow-sm"
            >
              <CheckCircle className="w-3.5 h-3.5" /> Review & Confirm Detail
            </button>
          </>
        ) : fact.user_confirmed ? (
          <>
            <span className="text-[11px] text-emerald-400 font-medium flex items-center gap-1">
              <Check className="w-3 h-3" /> Verified by user
            </span>
            <button
              type="button"
              onClick={() => openConfirmationModal(fieldName, displayName, fact)}
              className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-white transition"
            >
              <Edit3 className="w-3 h-3" /> Edit
            </button>
          </>
        ) : (
          <>
            <span className="text-[11px] text-slate-500">
              Verified ground truth
            </span>
            <button
              type="button"
              onClick={() => openConfirmationModal(fieldName, displayName, fact)}
              className="text-[11px] text-slate-400 hover:text-white transition"
            >
              Verify / Edit
            </button>
          </>
        )}
      </div>
    </div>
  );
};
