import React, { useState, useEffect, useRef } from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import { ShieldAlert, Quote, Check, X, AlertTriangle } from 'lucide-react';

interface DialogProps {
  fieldName: string;
  displayName: string;
  fact: any;
  onClose: () => void;
  onSave: (field: string, val: string) => Promise<void>;
}

const ConfirmationModalDialog: React.FC<DialogProps> = ({
  fieldName,
  displayName,
  fact,
  onClose,
  onSave,
}) => {
  const { t } = useTranslation();
  const [correctedValue, setCorrectedValue] = useState<string>(
    fact.confirmed_value || fact.value || ''
  );
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  const handleConfirmAsIs = async () => {
    setIsSubmitting(true);
    try {
      await onSave(fieldName, fact.value);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSaveCorrection = async () => {
    if (!correctedValue.trim()) return;
    setIsSubmitting(true);
    try {
      await onSave(fieldName, correctedValue.trim());
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-in fade-in duration-200"
    >
      <div
        ref={modalRef}
        className="bg-white border border-[#E1E7EE] rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#E1E7EE] bg-[#F8FAFC]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#FFF4D6] border border-[#FDE68A] text-[#92500A] flex items-center justify-center">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <div>
              <h2 id="confirm-modal-title" className="text-sm font-bold text-[#12233D]">
                {t('confirmFactModalTitle') || 'Review & Confirm Detail'}
              </h2>
              <p className="text-[11px] text-[#526176]">
                Ground-truth verification for {displayName}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-[#68778B] hover:text-[#12233D] p-1.5 rounded-lg hover:bg-slate-100 transition cursor-pointer"
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
              <span className="font-semibold text-[#526176] uppercase tracking-wider text-[10px]">
                Original Extraction from Notice:
              </span>
              <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-[#FFF4D6] text-[#92500A] border border-[#FDE68A] uppercase">
                {fact.status}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] text-[#12233D] font-medium">
              {fact.value}
            </div>
          </div>

          {/* Evidence Quote */}
          {fact.evidence_quote && (
            <div className="space-y-1">
              <span className="font-semibold text-[#68778B] uppercase tracking-wider text-[10px] flex items-center gap-1">
                <Quote className="w-3 h-3 text-[#08785D]" /> Grounded Evidence Quote:
              </span>
              <div className="p-3 rounded-xl bg-[#F8FAFC] border-l-3 border-[#08785D] text-[#526176] font-mono italic">
                "{fact.evidence_quote}"
              </div>
            </div>
          )}

          {/* Explanation if uncertain */}
          {fact.explanation && (
            <div className="p-3 rounded-xl bg-[#FFF4D6]/60 border border-[#FDE68A] text-[#92500A] flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-[#92500A] shrink-0 mt-0.5" />
              <span className="leading-relaxed">{fact.explanation}</span>
            </div>
          )}

          {/* User Confirmed / Corrected Input */}
          <div className="space-y-1.5 pt-1">
            <label htmlFor="confirmed-value-input" className="block font-semibold text-[#12233D]">
              Verified Value (Confirm or Rectify):
            </label>
            <textarea
              id="confirmed-value-input"
              value={correctedValue}
              onChange={(e) => setCorrectedValue(e.target.value)}
              rows={2}
              className="w-full bg-white border border-[#CBD5E1] focus:border-[#08785D] focus:ring-1 focus:ring-[#08785D] focus:outline-hidden rounded-xl p-3 text-[#12233D] placeholder-[#68778B] transition resize-none text-xs"
              placeholder="Enter verified or corrected value..."
            />
            <p className="text-[11px] text-[#68778B]">
              Preserves the original notice extraction while updating your action checklist and summaries with this verified value.
            </p>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-2.5 px-6 py-4 border-t border-[#E1E7EE] bg-[#F8FAFC]">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-[#526176] hover:text-[#12233D] hover:bg-slate-200 transition cursor-pointer"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleConfirmAsIs}
            disabled={isSubmitting}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-[#08785D] bg-[#E8F7F0] hover:bg-[#D4EFE3] border border-[#B7E7D2] transition cursor-pointer"
          >
            Confirm As-Is
          </button>
          <button
            type="button"
            onClick={handleSaveCorrection}
            disabled={isSubmitting || !correctedValue.trim()}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            <Check className="w-3.5 h-3.5" />
            {isSubmitting ? 'Saving...' : 'Save Verification'}
          </button>
        </div>
      </div>
    </div>
  );
};

export const ConfirmationModal: React.FC = () => {
  const { confirmingFact, closeConfirmationModal, saveConfirmation } = useNotice();

  if (!confirmingFact) return null;

  return (
    <ConfirmationModalDialog
      key={confirmingFact.fieldName}
      fieldName={confirmingFact.fieldName}
      displayName={confirmingFact.displayName}
      fact={confirmingFact.fact}
      onClose={closeConfirmationModal}
      onSave={saveConfirmation}
    />
  );
};
