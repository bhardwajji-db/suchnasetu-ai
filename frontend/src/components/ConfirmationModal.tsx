import React, { useState, useEffect } from 'react';
import { useNotice } from '../context/NoticeContext';
import { ShieldAlert, Quote, Check, X, AlertTriangle } from 'lucide-react';

export const ConfirmationModal: React.FC = () => {
  const { confirmingFact, closeConfirmationModal, saveConfirmation } = useNotice();
  const [correctedValue, setCorrectedValue] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    if (confirmingFact) {
      setCorrectedValue(
        confirmingFact.fact.confirmed_value || confirmingFact.fact.value || ''
      );
    }
  }, [confirmingFact]);

  if (!confirmingFact) return null;

  const { fieldName, displayName, fact } = confirmingFact;

  const handleConfirmAsIs = async () => {
    setIsSubmitting(true);
    try {
      await saveConfirmation(fieldName, fact.value);
      closeConfirmationModal();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSaveCorrection = async () => {
    if (!correctedValue.trim()) return;
    setIsSubmitting(true);
    try {
      await saveConfirmation(fieldName, correctedValue.trim());
      closeConfirmationModal();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200"
    >
      <div className="bg-[#0B132B] border border-[#1D2D4E] rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#1D2D4E] bg-[#070B14]/60">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <div>
              <h2 id="confirm-modal-title" className="text-sm font-bold text-white">
                Review & Confirm Detail
              </h2>
              <p className="text-[11px] text-slate-400">
                Ground-truth verification for {displayName}
              </p>
            </div>
          </div>
          <button
            onClick={closeConfirmationModal}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
            aria-label="Close modal"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 text-xs">
          {/* Notice Extraction */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-300 uppercase tracking-wider text-[10px]">
                Original Extraction from Notice:
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950/80 text-amber-400 border border-amber-800/80 uppercase">
                {fact.status}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-[#070B14] border border-[#1D2D4E] text-slate-200 font-medium">
              {fact.value}
            </div>
          </div>

          {/* Evidence Quote */}
          {fact.evidence_quote && (
            <div className="space-y-1">
              <span className="font-semibold text-slate-400 uppercase tracking-wider text-[10px] flex items-center gap-1">
                <Quote className="w-3 h-3 text-blue-400" /> Grounded Evidence Quote:
              </span>
              <div className="p-2.5 rounded-lg bg-[#070B14]/80 border-l-2 border-blue-500 text-slate-300 font-mono italic">
                "{fact.evidence_quote}"
              </div>
            </div>
          )}

          {/* Explanation if uncertain */}
          {fact.explanation && (
            <div className="p-2.5 rounded-lg bg-amber-950/30 border border-amber-900/40 text-amber-300 flex items-start gap-2">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
              <span>{fact.explanation}</span>
            </div>
          )}

          {/* User Confirmed / Corrected Input */}
          <div className="space-y-1.5 pt-1">
            <label htmlFor="confirmed-value-input" className="block font-semibold text-slate-300">
              Verified Value (Confirm or Rectify):
            </label>
            <textarea
              id="confirmed-value-input"
              value={correctedValue}
              onChange={(e) => setCorrectedValue(e.target.value)}
              rows={2}
              className="w-full bg-[#070B14] border border-[#1D2D4E] focus:border-blue-500 focus:outline-none rounded-lg p-2.5 text-white placeholder-slate-500 transition resize-none"
              placeholder="Enter verified or corrected value..."
            />
            <p className="text-[11px] text-slate-500">
              Preserves the original notice extraction while updating your action checklist and summaries with this verified value.
            </p>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-2.5 px-6 py-4 border-t border-[#1D2D4E] bg-[#070B14]/60">
          <button
            type="button"
            onClick={closeConfirmationModal}
            className="px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleConfirmAsIs}
            disabled={isSubmitting}
            className="px-3.5 py-1.5 rounded-lg text-xs font-semibold text-blue-400 hover:text-blue-300 bg-blue-950/60 border border-blue-800/80 transition"
          >
            Confirm As-Is
          </button>
          <button
            type="button"
            onClick={handleSaveCorrection}
            disabled={isSubmitting || !correctedValue.trim()}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 transition shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Check className="w-3.5 h-3.5" />
            {isSubmitting ? 'Saving...' : 'Save Verification'}
          </button>
        </div>
      </div>
    </div>
  );
};
