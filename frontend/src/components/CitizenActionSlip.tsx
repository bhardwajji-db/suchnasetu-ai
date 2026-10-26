import React from 'react';
import type { StructuredNotice, ActionChecklist, PlainLanguageSummary, ExtractedFact } from '../types/api';
import { useTranslation } from '../i18n';
import {
  Calendar,
  AlertTriangle,
  Phone,
  UserCheck,
  Target,
  FileCheck2,
  ShieldAlert,
  Printer,
  X,
} from 'lucide-react';

interface CitizenActionSlipProps {
  notice: StructuredNotice;
  summary?: PlainLanguageSummary | null;
  checklist?: ActionChecklist | null;
  documentId?: string | null;
  fingerprint?: string | null;
  currentLanguage?: string;
  onClose?: () => void;
}

export const CitizenActionSlip: React.FC<CitizenActionSlipProps> = ({
  notice,
  summary,
  checklist,
  documentId,
  fingerprint,
  currentLanguage = 'en',
  onClose,
}) => {
  const { t } = useTranslation();

  const formatFactValue = (fact?: ExtractedFact): string => {
    if (!fact) return t('notStated');
    if (fact.user_confirmed && fact.confirmed_value) {
      return fact.confirmed_value;
    }
    return fact.value || t('notStated');
  };

  const getStatusBadge = (fact?: ExtractedFact) => {
    if (!fact) return null;

    if (fact.user_confirmed) {
      return (
        <span className="slip-badge slip-badge-confirmed">
          ✓ {t('userConfirmedBadge')}
        </span>
      );
    }

    if (fact.requires_confirmation || fact.status === 'uncertain') {
      return (
        <span className="slip-badge slip-badge-warning">
          ⚠ {t('needsVerificationBadge')}
        </span>
      );
    }

    if (fact.status === 'not_stated') {
      return (
        <span className="slip-badge slip-badge-missing">
          {t('factStatusNotStated')}
        </span>
      );
    }

    return (
      <span className="slip-badge slip-badge-found">
        {t('foundInNoticeBadge')}
      </span>
    );
  };

  const [todayStr] = React.useState(() => {
    return new Date().toLocaleDateString(currentLanguage === 'en' ? 'en-IN' : `${currentLanguage}-IN`, {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  });

  const handlePrint = () => {
    window.print();
  };

  const noticeTitle =
    notice.main_subject?.value ||
    notice.purpose?.value ||
    t('officialGovNotice');

  return (
    <div className="citizen-action-slip" id="citizen-action-slip" aria-label="Citizen Action Slip">
      {/* Action Bar for On-Screen View */}
      <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-200 print:hidden">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200">
            {t('slipDossierTitle')}
          </span>
          <span className="text-xs text-slate-500 font-mono">
            {fingerprint ? `FP: ${fingerprint.slice(0, 10)}...` : documentId || ''}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handlePrint}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-[#08785D] hover:bg-[#06664E] text-white text-xs font-semibold rounded-lg shadow-sm cursor-pointer transition"
          >
            <Printer size={14} />
            <span>{t('printSlip')}</span>
          </button>
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 cursor-pointer"
              aria-label={t('close')}
            >
              <X size={16} />
            </button>
          )}
        </div>
      </div>

      {/* Header Banner */}
      <header className="slip-header">
        <div className="slip-brand">
          <div className="slip-logo-mark">
            <span className="slip-logo-icon">🏛️</span>
            <div>
              <h1 className="slip-app-title">SUCHNASETU AI • सूचना + सेतु</h1>
              <span className="slip-app-subtitle">
                {t('dossierSubtitle')}
              </span>
            </div>
          </div>
        </div>
        <div className="slip-doc-meta">
          <div>{t('statedDate')}: <strong>{todayStr}</strong></div>
          {fingerprint && (
            <div>
              {t('viewEvidence')}:{' '}
              <code>{fingerprint.slice(0, 16)}</code>
            </div>
          )}
        </div>
      </header>

      {/* Notice Title Banner */}
      <div className="slip-notice-title-box">
        <span className="slip-kicker">
          {notice.issuing_authority?.value || t('advisory')}
        </span>
        <h2 className="slip-notice-title">{noticeTitle}</h2>
        {notice.notice_reference_number?.value && (
          <div className="text-[11px] font-mono text-slate-600 mt-1">
            Ref: {notice.notice_reference_number.value}
          </div>
        )}
      </div>

      {/* Plain Language Summary Section */}
      {summary && (
        <section className="slip-section">
          <div className="slip-section-title">
            1. {t('summaryTitle')}
          </div>
          <div className="slip-summary-box">
            <p className="slip-summary-text">{summary.about}</p>
          </div>
        </section>
      )}

      {/* Six Key Information Fields Grid */}
      <section className="slip-section">
        <div className="slip-section-title">
          2. {t('factsTitle')}
        </div>
        <div className="slip-fields-grid">
          {/* Purpose */}
          <div className="slip-field-cell">
            <div className="slip-field-label">
              <Target size={12} className="text-emerald-700" />
              <span>{t('mainSubject')}</span>
              {getStatusBadge(notice.purpose)}
            </div>
            <div className="slip-field-val">{formatFactValue(notice.purpose)}</div>
          </div>

          {/* Deadline */}
          <div className="slip-field-cell slip-cell-highlight">
            <div className="slip-field-label">
              <Calendar size={12} className="text-blue-700" />
              <span>{t('upcomingDeadlinesTitle')}</span>
              {getStatusBadge(notice.deadline)}
            </div>
            <div className="slip-field-val slip-val-deadline">
              {formatFactValue(notice.deadline)}
            </div>
          </div>

          {/* Eligibility */}
          <div className="slip-field-cell">
            <div className="slip-field-label">
              <UserCheck size={12} className="text-emerald-700" />
              <span>{t('eligibilityTitle')}</span>
              {getStatusBadge(notice.eligibility)}
            </div>
            <div className="slip-field-val">{formatFactValue(notice.eligibility)}</div>
          </div>

          {/* Fee / Cost */}
          <div className="slip-field-cell">
            <div className="slip-field-label">
              <AlertTriangle size={12} className="text-amber-700" />
              <span>{t('fee')}</span>
              {getStatusBadge(notice.fee_or_cost)}
            </div>
            <div className="slip-field-val">{formatFactValue(notice.fee_or_cost)}</div>
          </div>

          {/* Required Documents */}
          <div className="slip-field-cell">
            <div className="slip-field-label">
              <FileCheck2 size={12} className="text-emerald-700" />
              <span>{t('requiredDocuments')}</span>
              {getStatusBadge(notice.required_documents)}
            </div>
            <div className="slip-field-val">{formatFactValue(notice.required_documents)}</div>
          </div>

          {/* Contact Details */}
          <div className="slip-field-cell">
            <div className="slip-field-label">
              <Phone size={12} className="text-emerald-700" />
              <span>{t('contactDetails')}</span>
              {getStatusBadge(notice.contact_details)}
            </div>
            <div className="slip-field-val">{formatFactValue(notice.contact_details)}</div>
          </div>
        </div>
      </section>

      {/* Action Checklist */}
      {checklist && checklist.items && checklist.items.length > 0 && (
        <section className="slip-section">
          <div className="slip-section-title">
            3. {t('actionPlanTitle')}
          </div>
          <div className="slip-checklist">
            {checklist.items.map((item, idx) => (
              <div key={item.step_number || idx} className="slip-checklist-item">
                <div className="slip-step-num">{item.step_number || idx + 1}</div>
                <div className="slip-step-content">
                  <div className="slip-step-action">{item.action}</div>
                  <div className="slip-step-meta">
                    {item.category && (
                      <span className="font-semibold text-blue-700 capitalize">
                        {item.category}
                      </span>
                    )}
                    {item.is_mandatory && (
                      <span className="text-red-700 font-semibold">
                        {t('mandatory')}
                      </span>
                    )}
                    {item.requires_confirmation && (
                      <span className="text-amber-800 font-bold">
                        ⚠ {t('needsVerificationBadge')}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Official Disclaimer */}
      <footer className="slip-disclaimer">
        <div className="flex items-center gap-1.5 font-bold text-slate-700 mb-1">
          <ShieldAlert size={14} className="text-emerald-700" />
          <span>{t('dossierAdvisory')}</span>
        </div>
        <p>
          {t('dossierAdvisoryText')}
        </p>
      </footer>
    </div>
  );
};
