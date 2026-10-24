import React, { useState } from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import { apiClient } from '../services/apiClient';
import type { ApplicantProfile, EligibilityAssessment, EvaluationStatus } from '../types/api';
import {
  UserCheck,
  CheckCircle2,
  XCircle,
  HelpCircle,
  AlertCircle,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  RefreshCw,
  Edit3,
  Search,
} from 'lucide-react';

export const EligibilityEngineView: React.FC = () => {
  const {
    rawNoticeText,
    sessionId,
    setSavedEligibility,
    setApplicantProfile,
    openEvidenceInspector,
    setActiveTab,
  } = useNotice();
  const { t } = useTranslation();
  const [activeNoticeText, setActiveNoticeText] = useState<string>(rawNoticeText || '');
  const [isEvaluating, setIsEvaluating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [assessment, setAssessment] = useState<EligibilityAssessment | null>(null);

  // Applicant Profile Form State
  const [dob, setDob] = useState<string>('2001-05-14');
  const [degree, setDegree] = useState<string>('B.Sc Computer Science');
  const [percentage, setPercentage] = useState<string>('62.5');
  const [category, setCategory] = useState<string>('OBC');
  const [notes, setNotes] = useState<string>('');

  const handleLoadSampleNotice = async () => {
    try {
      setError(null);
      const data = await apiClient.getSampleText('demo_upsc_scholarship.txt');
      setActiveNoticeText(data.content);
    } catch (e: any) {
      setError(`Failed to load sample notice: ${e.message}`);
    }
  };

  const handleEvaluate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    if (!activeNoticeText.trim()) {
      setError('Please provide notice text or select a sample notice to extract eligibility rules.');
      return;
    }

    setIsEvaluating(true);
    setError(null);

    const profile: ApplicantProfile = {
      date_of_birth: dob.trim() || undefined,
      degree: degree.trim() || undefined,
      marks_percentage: percentage.trim() ? parseFloat(percentage) : undefined,
      category: category.trim() || 'General',
      notes: notes.trim() || undefined,
    };

    try {
      const res = await apiClient.evaluateEligibility(
        profile,
        sessionId || undefined,
        activeNoticeText.trim()
      );
      setAssessment(res);
      if (setSavedEligibility) {
        setSavedEligibility(res);
      }
      if (setApplicantProfile) {
        setApplicantProfile(profile);
      }
    } catch (err: any) {
      setError(err.message || 'Evaluation failed. Please verify notice content.');
    } finally {
      setIsEvaluating(false);
    }
  };

  const getStatusBadge = (status: EvaluationStatus) => {
    switch (status) {
      case 'PASS':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-bold bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]">
            <CheckCircle2 className="w-3.5 h-3.5 text-[#08785D]" />
            PASS
          </span>
        );
      case 'FAIL':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-bold bg-[#FEE8E7] text-[#B42318] border border-[#FCA5A5]">
            <XCircle className="w-3.5 h-3.5 text-[#B42318]" />
            FAIL
          </span>
        );
      case 'UNKNOWN':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-bold bg-[#FFF4D6] text-[#92500A] border border-[#FDE68A]">
            <HelpCircle className="w-3.5 h-3.5 text-[#92500A]" />
            UNKNOWN
          </span>
        );
      default:
        return null;
    }
  };

  const getOverallBanner = () => {
    if (!assessment) return null;
    switch (assessment.overall_status) {
      case 'ELIGIBLE':
        return {
          title: 'All Stated Eligibility Criteria Satisfied',
          desc: 'Based on explicit notice rules, your profile satisfies all evaluated qualifications, age boundaries, and percentage marks.',
          color: 'bg-[#E8F7F0] border-[#B7E7D2] text-[#08785D]',
          icon: <ShieldCheck className="w-6 h-6 text-[#08785D]" />,
        };
      case 'NOT_ELIGIBLE':
        return {
          title: 'One or More Mandatory Criteria Not Met',
          desc: 'One or more mandatory requirements (e.g. minimum marks or age limit) do not appear to be satisfied based on the official circular.',
          color: 'bg-[#FEE8E7] border-[#FCA5A5] text-[#B42318]',
          icon: <XCircle className="w-6 h-6 text-[#B42318]" />,
        };
      default:
        return {
          title: 'Evaluation Inconclusive / Missing Information',
          desc: 'Certain conditions require manual confirmation or missing details before qualification can be verified.',
          color: 'bg-[#FFF4D6] border-[#FDE68A] text-[#92500A]',
          icon: <AlertCircle className="w-6 h-6 text-[#92500A]" />,
        };
    }
  };

  const banner = getOverallBanner();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-[#E1E7EE]">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-[#12233D] flex items-center gap-2.5">
            <UserCheck className="w-6 h-6 text-[#08785D]" />
            {t('eligibilityTitle') || 'Explainable Applicant Eligibility Engine'}
          </h1>
          <p className="text-xs sm:text-sm text-[#526176] mt-1">
            {t('eligibilitySubtitle') || 'Compare your qualifications, marks, age, and category against official notice rules with deterministic Python verification.'}
          </p>
        </div>

        <button
          type="button"
          onClick={handleLoadSampleNotice}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#E8F7F0] border border-[#B7E7D2] text-[#08785D] hover:bg-[#D4EFE3] transition cursor-pointer"
        >
          <Sparkles className="w-3.5 h-3.5" />
          Load Sample Scholarship Circular
        </button>
      </div>

      {/* Grid: Form & Notice Source */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left Column: Applicant Profile Form (5 cols) */}
        <div className="lg:col-span-5 bg-white border border-[#E1E7EE] rounded-xl p-5 space-y-4 shadow-xs">
          <div className="flex items-center justify-between pb-2 border-b border-[#E1E7EE]">
            <h2 className="text-sm font-bold text-[#12233D] flex items-center gap-2">
              <Edit3 className="w-4 h-4 text-[#08785D]" />
              Applicant Profile Parameters
            </h2>
            <span className="text-[11px] text-[#68778B]">Privacy: Zero PII Stored</span>
          </div>

          <form onSubmit={handleEvaluate} className="space-y-3.5">
            {/* Date of Birth */}
            <div>
              <label htmlFor="dob-input" className="text-xs font-bold text-[#526176] block mb-1">
                Date of Birth (YYYY-MM-DD)
              </label>
              <input
                id="dob-input"
                type="date"
                value={dob}
                onChange={(e) => setDob(e.target.value)}
                className="w-full bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg px-3 py-2 text-xs text-[#12233D] focus:border-[#08785D] focus:outline-hidden transition"
              />
            </div>

            {/* Educational Qualification */}
            <div>
              <label htmlFor="degree-input" className="text-xs font-bold text-[#526176] block mb-1">
                Educational Qualification / Degree
              </label>
              <input
                id="degree-input"
                type="text"
                value={degree}
                onChange={(e) => setDegree(e.target.value)}
                placeholder="e.g. B.Sc, B.Tech, 12th Standard"
                className="w-full bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg px-3 py-2 text-xs text-[#12233D] focus:border-[#08785D] focus:outline-hidden transition"
              />
            </div>

            {/* Percentage / Marks */}
            <div>
              <label htmlFor="percentage-input" className="text-xs font-bold text-[#526176] block mb-1">
                Aggregate Marks Percentage (%)
              </label>
              <input
                id="percentage-input"
                type="number"
                step="0.01"
                min="0"
                max="100"
                value={percentage}
                onChange={(e) => setPercentage(e.target.value)}
                placeholder="e.g. 62.5"
                className="w-full bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg px-3 py-2 text-xs text-[#12233D] focus:border-[#08785D] focus:outline-hidden transition"
              />
            </div>

            {/* Reservation Category */}
            <div>
              <label htmlFor="category-select" className="text-xs font-bold text-[#526176] block mb-1">
                Reservation Category
              </label>
              <select
                id="category-select"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg px-3 py-2 text-xs text-[#12233D] focus:border-[#08785D] focus:outline-hidden transition"
              >
                <option value="General">General / Open</option>
                <option value="OBC">OBC (Other Backward Classes)</option>
                <option value="SC">SC (Scheduled Castes)</option>
                <option value="ST">ST (Scheduled Tribes)</option>
                <option value="EWS">EWS (Economically Weaker Section)</option>
                <option value="PwD">PwD (Persons with Disabilities)</option>
              </select>
            </div>

            {/* Extra notes */}
            <div>
              <label htmlFor="notes-input" className="text-xs font-bold text-[#526176] block mb-1">
                Additional Notes / Profile Details
              </label>
              <input
                id="notes-input"
                type="text"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="e.g. Domicile state, special certificates..."
                className="w-full bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg px-3 py-2 text-xs text-[#12233D] focus:border-[#08785D] focus:outline-hidden transition"
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isEvaluating}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs disabled:opacity-50 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isEvaluating ? 'animate-spin' : ''}`} />
              {isEvaluating ? 'Evaluating Profile Rules...' : 'Evaluate My Eligibility'}
            </button>
          </form>
        </div>

        {/* Right Column: Notice Text Buffer (7 cols) */}
        <div className="lg:col-span-7 bg-white border border-[#E1E7EE] rounded-xl p-5 flex flex-col justify-between space-y-3 shadow-xs">
          <div className="flex items-center justify-between pb-2 border-b border-[#E1E7EE]">
            <span className="text-xs font-bold text-[#12233D]">
              Official Circular Rules Source
            </span>
            <span className="text-[11px] text-[#68778B] font-mono">
              {activeNoticeText.length} chars
            </span>
          </div>

          <textarea
            value={activeNoticeText}
            onChange={(e) => setActiveNoticeText(e.target.value)}
            placeholder="Paste notice text with eligibility criteria here..."
            rows={12}
            className="w-full bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg p-3 text-xs text-[#12233D] font-mono focus:border-[#08785D] focus:outline-hidden transition resize-y leading-relaxed"
          />

          <div className="text-[11px] text-[#68778B] italic">
            Deterministic rule parser extracts age limits, marks cutoff, and degree requirements directly from the document.
          </div>
        </div>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-[#FEE8E7] border border-[#FCA5A5] text-xs text-[#B42318] flex items-center gap-2.5">
          <AlertCircle className="w-4 h-4 text-[#B42318] shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Assessment Output Display */}
      {assessment && banner && (
        <div className="space-y-5 animate-in fade-in">
          {/* Overall Verdict Banner */}
          <div className={`p-5 rounded-2xl border flex items-start gap-3.5 shadow-xs ${banner.color}`}>
            <div className="shrink-0 mt-0.5">{banner.icon}</div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-[#12233D]">{banner.title}</h3>
                <span className="px-2.5 py-0.5 rounded-md text-[10px] font-mono font-bold uppercase bg-white text-[#12233D] border border-[#CBD5E1]">
                  Status: {assessment.overall_status}
                </span>
              </div>
              <p className="text-xs leading-relaxed opacity-90">{banner.desc}</p>
              <div className="text-[11px] pt-1">
                <strong>Executive Summary:</strong> {assessment.summary}
              </div>
            </div>
          </div>

          {/* Individual Criteria Evaluation Breakdown */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-[#12233D] flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#08785D]" />
              Detailed Rule-by-Rule Breakdown ({assessment.results.length} Criteria Evaluated)
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {assessment.results.map((evalItem, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl bg-white border border-[#E1E7EE] hover:border-[#B7E7D2] transition space-y-2.5 shadow-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded-md bg-[#F8FAFC] text-[#526176] border border-[#E1E7EE]">
                      {evalItem.criterion_type}
                    </span>
                    {getStatusBadge(evalItem.status)}
                  </div>

                  <h4 className="text-xs font-bold text-[#12233D]">
                    {evalItem.description}
                  </h4>

                  <div className="grid grid-cols-2 gap-2 text-[11px]">
                    <div className="p-2 rounded-lg bg-[#F8FAFC] border border-[#E1E7EE]">
                      <span className="text-[10px] uppercase font-bold text-[#68778B] block">Provided</span>
                      <span className="font-semibold text-[#12233D]">{evalItem.applicant_value}</span>
                    </div>
                    <div className="p-2 rounded-lg bg-[#F8FAFC] border border-[#E1E7EE]">
                      <span className="text-[10px] uppercase font-bold text-[#08785D] block">Required</span>
                      <span className="font-semibold text-[#12233D]">{evalItem.requirement_value}</span>
                    </div>
                  </div>

                  <p className="text-xs text-[#526176] leading-relaxed">
                    {evalItem.explanation}
                  </p>

                  {/* Supporting Citation Quote */}
                  {evalItem.evidence_quote && (
                    <div className="space-y-1.5">
                      <div className="p-2.5 rounded-lg bg-[#F8FAFC] border-l-3 border-[#08785D] text-[11px] text-[#526176] font-mono italic">
                        "{evalItem.evidence_quote}"
                      </div>
                      <button
                        type="button"
                        onClick={() =>
                          openEvidenceInspector(
                            {
                              excerpt: evalItem.evidence_quote,
                              claim: `${evalItem.description} (${evalItem.status})`,
                              docTitle: 'Eligibility Rule Notice',
                            },
                            activeNoticeText
                          )
                        }
                        className="inline-flex items-center gap-1.5 px-2 py-1 rounded text-[11px] font-semibold text-[#08785D] hover:bg-[#E8F7F0] transition cursor-pointer"
                      >
                        <Search className="w-3 h-3" />
                        <span>Inspect Verbatim Evidence</span>
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Action Navigator CTA */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 rounded-xl bg-gradient-to-r from-[#E8F7F0] via-white to-[#E8F7F0] border border-[#B7E7D2]">
            <div className="space-y-0.5">
              <div className="text-xs font-bold text-[#12233D] flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-[#08785D]" />
                Build Personalized Action Roadmap
              </div>
              <p className="text-[11px] text-[#526176]">
                Transform your evaluated eligibility status and profile into a dependency-ordered action roadmap.
              </p>
            </div>
            <button
              type="button"
              onClick={() => setActiveTab(7)}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-bold bg-[#08785D] hover:bg-[#06664E] text-white transition shadow-xs cursor-pointer shrink-0"
            >
              <span>Open Action Navigator</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
