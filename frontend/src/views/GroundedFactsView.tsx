import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import { FactCard } from '../components/FactCard';
import { StaleWarningBanner } from '../components/StaleWarningBanner';
import { Search, ArrowRight, ShieldCheck, FileText } from 'lucide-react';

export const GroundedFactsView: React.FC = () => {
  const { structuredNotice, sixCoreFields, setActiveTab } = useNotice();
  const { t } = useTranslation();

  if (!structuredNotice) {
    return (
      <div className="bg-white border border-[#E1E7EE] rounded-2xl p-12 text-center space-y-4 shadow-xs">
        <div className="w-12 h-12 rounded-xl bg-[#E8F7F0] border border-[#B7E7D2] text-[#08785D] flex items-center justify-center mx-auto">
          <Search className="w-6 h-6" />
        </div>
        <h2 className="text-base font-bold text-[#12233D]">{t('factsTitle') || 'No Grounded Facts Available Yet'}</h2>
        <p className="text-xs text-[#526176] max-w-md mx-auto">
          {t('factsSubtitle') || 'Load or paste notice text and run analysis in the Notice Workspace tab to extract and verify grounded semantic facts.'}
        </p>
        <button
          type="button"
          onClick={() => setActiveTab(1)}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs cursor-pointer"
        >
          <span>{t('navIngestion') || 'Go to Notice Workspace'}</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    );
  }

  // 1. The Six Core Structured Fields
  const sixFields = [
    {
      key: 'issuing_authority',
      name: `1. ${t('issuingAuthority') || 'Issuing Authority or Department'}`,
      fact: structuredNotice.issuing_authority || sixCoreFields?.issuing_authority || structuredNotice.purpose,
    },
    {
      key: 'notice_reference_number',
      name: `2. ${t('noticeReference') || 'Notice / Reference Number'}`,
      fact: structuredNotice.notice_reference_number || sixCoreFields?.notice_reference_number,
    },
    {
      key: 'notice_date',
      name: `3. ${t('noticeDate') || 'Notice Issuance Date'}`,
      fact: structuredNotice.notice_date || sixCoreFields?.notice_date,
    },
    {
      key: 'recipient',
      name: `4. ${t('recipient') || 'Recipient or Concerned Party'}`,
      fact: structuredNotice.recipient || sixCoreFields?.recipient || structuredNotice.eligibility,
    },
    {
      key: 'main_subject',
      name: `5. ${t('mainSubject') || 'Main Issue, Allegation, or Subject'}`,
      fact: structuredNotice.main_subject || sixCoreFields?.main_subject || structuredNotice.purpose,
    },
    {
      key: 'required_action_and_deadline',
      name: `6. ${t('requiredActionDeadline') || 'Required Action and Deadline'}`,
      fact: structuredNotice.required_action_and_deadline || sixCoreFields?.required_action_and_deadline || structuredNotice.deadline,
    },
  ];

  // 2. Procedural & Operational Dimensions
  const proceduralDimensions = [
    { key: 'eligibility', name: t('eligibility') || 'Eligibility Criteria & Thresholds', fact: structuredNotice.eligibility },
    { key: 'deadline', name: t('deadline') || 'Final Submission Deadline & Cutoff', fact: structuredNotice.deadline },
    { key: 'fee_or_cost', name: t('fee') || 'Application / Penalty / Costs', fact: structuredNotice.fee_or_cost },
    { key: 'required_documents', name: t('requiredDocuments') || 'Required Documents & Verification', fact: structuredNotice.required_documents },
    { key: 'contact_details', name: t('contactDetails') || 'Official Contact & Helpdesk', fact: structuredNotice.contact_details },
    { key: 'important_conditions', name: t('info') || 'Important Rules & Conditions', fact: structuredNotice.important_conditions },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-[#12233D] tracking-tight flex items-center gap-2">
          <span>🔍 {t('factsTitle') || '2. Grounded Fact Breakdown'}</span>
        </h1>
        <p className="text-xs text-[#526176] mt-1">
          {t('factsSubtitle') || 'Discrete semantic dimensions extracted from the notice. Every stated fact references verbatim quotation proof to prevent hallucinations.'}
        </p>
      </div>

      <StaleWarningBanner />

      {/* SECTION 1: Six Core Notice Fields */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-[#08785D] font-bold text-xs uppercase tracking-wider">
          <ShieldCheck className="w-4 h-4" />
          <span>Six Core Notice Fields (Structured Legal Extraction)</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sixFields.map((d) =>
            d.fact ? (
              <FactCard
                key={d.key}
                fieldName={d.key}
                displayName={d.name}
                fact={d.fact}
              />
            ) : null
          )}
        </div>
      </div>

      {/* SECTION 2: Procedural Dimensions */}
      <div className="space-y-3 pt-4 border-t border-[#E1E7EE]">
        <div className="flex items-center gap-2 text-[#08785D] font-bold text-xs uppercase tracking-wider">
          <FileText className="w-4 h-4" />
          <span>Procedural & Operational Dimensions</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {proceduralDimensions.map((d) =>
            d.fact ? (
              <FactCard
                key={d.key}
                fieldName={d.key}
                displayName={d.name}
                fact={d.fact}
              />
            ) : null
          )}
        </div>
      </div>
    </div>
  );
};
