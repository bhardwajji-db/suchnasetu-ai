import React from 'react';
import type { ExtractedFact } from '../types/api';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import { Quote, AlertCircle, CheckCircle, Check, Edit3 } from 'lucide-react';

interface FactCardProps {
  fact: ExtractedFact;
  fieldName: string;
  displayName: string;
}

export const FactCard: React.FC<FactCardProps> = ({ fact, fieldName, displayName }) => {
  const { openConfirmationModal } = useNotice();
  const { t } = useTranslation();

  const getStatusBadge = () => {
    switch (fact.status) {
      case 'stated':
        return (
          <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-md bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]">
            {t('factStatusStated')}
          </span>
        );
      case 'not_stated':
        return (
          <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-md bg-slate-100 text-[#526176] border border-slate-200">
            {t('factStatusNotStated')}
          </span>
        );
      case 'uncertain':
        return (
          <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-md bg-[#FFF4D6] text-[#92500A] border border-[#FDE68A]">
            {t('factStatusUncertain')}
          </span>
        );
      case 'conflicting':
        return (
          <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-md bg-[#FEE8E7] text-[#B42318] border border-[#FCA5A5]">
            {t('factStatusConflicting')}
          </span>
        );
      default:
        return (
          <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-md bg-slate-100 text-[#526176] border border-slate-200">
            {fact.status}
          </span>
        );
    }
  };

  const hasCorrection = Boolean(fact.user_confirmed && fact.confirmed_value && fact.confirmed_value !== fact.value);
  const displayValue = fact.user_confirmed && fact.confirmed_value ? fact.confirmed_value : fact.value;

  return (
    <div className="bg-white border border-[#E1E7EE] hover:border-[#B7E7D2] transition rounded-xl p-5 flex flex-col justify-between shadow-xs">
      <div>
        <div className="flex items-center justify-between mb-2.5">
          <h3 className="text-sm font-bold text-[#12233D] uppercase tracking-wide">
            {displayName}
          </h3>
          <div className="flex items-center gap-2">
            {fact.user_confirmed && (
              <span className="flex items-center gap-1 text-[10px] font-bold uppercase px-2 py-0.5 rounded-md bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]">
                <Check className="w-3 h-3" /> {hasCorrection ? t('correctedBadge') : t('verifiedBadge')}
              </span>
            )}
            {getStatusBadge()}
            {fact.uncertainty_type && !fact.user_confirmed && (
              <span
                className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded-md bg-[#FFF4D6] text-[#92500A] border border-[#FDE68A]"
                title={`Uncertainty cause: ${fact.uncertainty_type}`}
              >
                {fact.uncertainty_type.replace('_', ' ')}
              </span>
            )}
          </div>
        </div>

        {/* Fact Value */}
        <div className="text-base font-semibold text-[#12233D] mb-2 leading-relaxed">
          {displayValue}
        </div>

        {/* Original Value if Corrected */}
        {hasCorrection && (
          <div className="text-xs text-[#526176] mb-2 italic">
            <span className="font-semibold text-[#68778B] uppercase text-[9px] not-italic mr-1">
              {t('originalLabel')}
            </span>
            "{fact.value}"
          </div>
        )}

        {/* Verbatim Evidence Quote (Preserved in Original Source Language) */}
        {fact.evidence_quote && (
          <div className="mt-2.5 p-3 rounded-lg bg-[#F8FAFC] border-l-3 border-[#08785D] text-xs text-[#526176] font-mono italic leading-relaxed">
            <div className="flex items-center justify-between text-[#08785D] font-sans font-bold text-[10px] uppercase mb-1">
              <span className="flex items-center gap-1">
                <Quote className="w-3 h-3" /> {t('groundedEvidenceQuote')}
              </span>
              <span className="text-[9px] font-medium text-[#68778B] lowercase px-1.5 py-0.5 bg-slate-200/70 rounded">
                original source quotation
              </span>
            </div>
            "{fact.evidence_quote}"
          </div>
        )}

        {/* Explanation / Uncertainty Warning */}
        {fact.explanation && (
          <div className="mt-2.5 p-3 rounded-lg bg-[#FFF4D6]/70 border border-[#FDE68A] text-xs text-[#92500A] flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-[#92500A] shrink-0 mt-0.5" />
            <div className="leading-relaxed">{fact.explanation}</div>
          </div>
        )}
      </div>

      {/* Confirmation Actions */}
      <div className="mt-4 pt-3 border-t border-[#E1E7EE] flex items-center justify-between">
        {fact.requires_confirmation && !fact.user_confirmed ? (
          <>
            <span className="text-xs text-[#92500A] font-medium">
              ⚠️ {t('needsReviewBeforeAction')}
            </span>
            <button
              type="button"
              onClick={() => openConfirmationModal(fieldName, displayName, fact)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs cursor-pointer"
            >
              <CheckCircle className="w-3.5 h-3.5" /> {t('reviewConfirmDetail')}
            </button>
          </>
        ) : fact.user_confirmed ? (
          <>
            <span className="text-[11px] text-[#08785D] font-medium flex items-center gap-1">
              <Check className="w-3 h-3" /> {t('verifiedByUser')}
            </span>
            <button
              type="button"
              onClick={() => openConfirmationModal(fieldName, displayName, fact)}
              className="flex items-center gap-1 text-xs text-[#526176] hover:text-[#08785D] transition cursor-pointer"
            >
              <Edit3 className="w-3 h-3" /> {t('editBtn')}
            </button>
          </>
        ) : (
          <>
            <span className="text-[11px] text-[#68778B]">
              {t('verifiedGroundTruth')}
            </span>
            <button
              type="button"
              onClick={() => openConfirmationModal(fieldName, displayName, fact)}
              className="text-xs text-[#526176] hover:text-[#08785D] transition cursor-pointer"
            >
              {t('verifyEditBtn')}
            </button>
          </>
        )}
      </div>
    </div>
  );
};
