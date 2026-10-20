import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { FactCard } from '../components/FactCard';
import { StaleWarningBanner } from '../components/StaleWarningBanner';
import { Search, AlertCircle, FileQuestion, ArrowRight } from 'lucide-react';

export const GroundedFactsView: React.FC = () => {
  const { structuredNotice, setActiveTab } = useNotice();

  if (!structuredNotice) {
    return (
      <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-12 text-center space-y-4">
        <div className="w-12 h-12 rounded-xl bg-blue-600/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mx-auto">
          <Search className="w-6 h-6" />
        </div>
        <h2 className="text-base font-bold text-white">No Grounded Facts Available Yet</h2>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          Load or paste notice text and run analysis in the Ingestion tab to extract and verify grounded semantic facts.
        </p>
        <button
          onClick={() => setActiveTab(0)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 transition shadow-sm"
        >
          <span>Go to Ingestion & OCR</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    );
  }

  const factDimensions = [
    { key: 'purpose', name: 'Notice Purpose & Program Name', fact: structuredNotice.purpose },
    { key: 'eligibility', name: 'Eligibility Criteria & Thresholds', fact: structuredNotice.eligibility },
    { key: 'deadline', name: 'Final Submission Deadline & Cutoff', fact: structuredNotice.deadline },
    { key: 'fee_or_cost', name: 'Application / Registration Fee', fact: structuredNotice.fee_or_cost },
    { key: 'required_documents', name: 'Required Documents & Verification', fact: structuredNotice.required_documents },
    { key: 'contact_details', name: 'Official Contact & Queries Helpdesk', fact: structuredNotice.contact_details },
    { key: 'required_actions', name: 'Mandatory Submission Procedure', fact: structuredNotice.required_actions },
    { key: 'important_conditions', name: 'Important Rules & Special Conditions', fact: structuredNotice.important_conditions },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <span>🔍 2. Grounded Fact Breakdown</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Discrete semantic dimensions extracted from the notice. Every stated fact references verbatim quotation proof to prevent hallucinations.
        </p>
      </div>

      <StaleWarningBanner />

      {/* 8 Fact Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {factDimensions.map((d) => (
          <FactCard
            key={d.key}
            fieldName={d.key}
            displayName={d.name}
            fact={d.fact}
          />
        ))}
      </div>

      {/* Missing Information & Uncertainty Dossiers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
        {/* Missing Information */}
        <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-amber-400 font-bold text-xs uppercase tracking-wider">
            <FileQuestion className="w-4 h-4" />
            <span>Missing Notice Details ({structuredNotice.missing_information.length})</span>
          </div>
          {structuredNotice.missing_information.length > 0 ? (
            <ul className="space-y-1.5 text-xs text-slate-300">
              {structuredNotice.missing_information.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2 bg-[#070B14] p-2 rounded border border-[#1D2D4E]">
                  <span className="text-amber-500 font-bold">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-xs text-slate-400 italic">
              All standard institutional details appear to be covered in this notice.
            </div>
          )}
        </div>

        {/* Ambiguous or Conflicting Details */}
        <div className="bg-[#0B1327] border border-[#1D2D4E] rounded-xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-rose-400 font-bold text-xs uppercase tracking-wider">
            <AlertCircle className="w-4 h-4" />
            <span>Ambiguous or Conflicting Details ({structuredNotice.uncertain_or_conflicting_details.length})</span>
          </div>
          {structuredNotice.uncertain_or_conflicting_details.length > 0 ? (
            <ul className="space-y-1.5 text-xs text-slate-300">
              {structuredNotice.uncertain_or_conflicting_details.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2 bg-[#070B14] p-2 rounded border border-[#1D2D4E]">
                  <span className="text-rose-500 font-bold">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-xs text-slate-400 italic">
              No contradictory dates, conflicting requirements, or unverified claims detected.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
