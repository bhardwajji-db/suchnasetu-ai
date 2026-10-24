import React, { useState } from 'react';
import { useNotice } from '../context/NoticeContext';
import { FileDropzone } from '../components/FileDropzone';
import { OCRPanel } from '../components/OCRPanel';
import { NoticeBuffer } from '../components/NoticeBuffer';
import {
  UploadCloud,
  Sparkles,
  FileSearch,
  CheckSquare,
  CheckCircle2,
  ShieldCheck,
  Volume2,
  GitCompare,
  ChevronDown,
  ChevronUp,
  Globe2,
} from 'lucide-react';

export const DashboardView: React.FC = () => {
  const {
    setActiveTab,
    loadSampleFixture,
    rawNoticeText,
    systemHealth,
    activeProvider,
    runAnalysis,
    isAnalyzing,
    uploadedImage,
  } = useNotice();

  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

  const handleLoadDemo = () => {
    loadSampleFixture('synthetic_scholarship_notice.txt');
    setActiveTab(1);
  };

  const getSystemStatus = () => {
    if (!systemHealth) {
      return {
        text: 'Checking system...',
        color: 'text-[#92500A] bg-[#FFF4D6] border-[#FDE68A]',
      };
    }
    if (systemHealth.overall_status === 'ok') {
      return {
        text: `System Ready · ${activeProvider === 'ollama' ? 'Local Ollama' : activeProvider}`,
        color: 'text-[#08785D] bg-[#E8F7F0] border-[#B7E7D2]',
      };
    }
    return {
      text: 'Diagnostics Warning',
      color: 'text-[#92500A] bg-[#FFF4D6] border-[#FDE68A]',
    };
  };

  const status = getSystemStatus();

  const faqs = [
    {
      q: 'How does SuchnaSetu AI ensure extracted facts are accurate?',
      a: 'SuchnaSetu AI employs a strict evidence-grounding engine. Every extracted deadline, fee, and requirement is matched against exact character offsets in the raw document text. If a detail cannot be verified with verbatim evidence, it is explicitly flagged as unstated or uncertain rather than hallucinated.',
    },
    {
      q: 'Does completing the action checklist submit my official application?',
      a: 'No. The action checklist is a personal preparation tool to help you organize documents, deadlines, and eligibility criteria. Official submissions must always be completed directly on the authorized government or institutional portal.',
    },
    {
      q: 'Can SuchnaSetu AI operate completely offline?',
      a: 'Yes. With a local Ollama instance (such as Gemma 4 or Qwen 2.5) and host Tesseract OCR installed, the entire ingestion, OCR, extraction, and Q&A pipeline runs 100% locally on your machine with zero cloud connectivity required.',
    },
    {
      q: 'What document formats and file sizes are supported?',
      a: 'The application supports digital and scanned PDFs, images (PNG, JPG, JPEG, WEBP), and plain text documents (TXT) up to 25MB in size.',
    },
    {
      q: 'How does the Change Tracker compare revisions and corrigenda?',
      a: 'The Change Tracker analyzes original notices alongside revised circulars or corrigenda, producing a field-by-field delta that highlights additions, modifications, cancellations, and extensions with exact source citations.',
    },
  ];

  return (
    <div className="space-y-8 sm:space-y-12 animate-fadeIn pb-8 sm:pb-12">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-2xl sm:rounded-3xl bg-white border border-[#E1E7EE] p-4 sm:p-8 md:p-10 shadow-xs">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 sm:gap-8 items-center">
          {/* Left Column: Value Proposition & CTAs */}
          <div className="lg:col-span-7 space-y-5 sm:space-y-6">
            <div className="space-y-2.5 sm:space-y-3">
              <div
                className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold border ${status.color}`}
              >
                <span className="w-2 h-2 rounded-full bg-[#08785D] animate-pulse" />
                <span>{status.text}</span>
              </div>
              <div className="text-xs font-bold uppercase tracking-wider text-[#08785D]">
                Notice Intelligence for Everyone
              </div>
              <h1 className="text-2xl sm:text-4xl md:text-5xl font-extrabold text-[#12233D] tracking-tight leading-tight">
                From complex notices to <span className="text-[#08785D]">clear next steps.</span>
              </h1>
              <p className="text-base text-[#526176] leading-relaxed max-w-xl">
                Transform convoluted government circulars, scholarships, public notifications, and legal summonses into source-grounded facts, plain-language summaries, and actionable personal checklists.
              </p>
            </div>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <button
                type="button"
                onClick={() => setActiveTab(1)}
                className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-bold text-sm text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs cursor-pointer"
              >
                <UploadCloud className="w-4 h-4" />
                <span>Analyze a Notice</span>
              </button>
              <button
                type="button"
                onClick={handleLoadDemo}
                className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl font-semibold text-sm text-[#12233D] bg-[#F8FAFC] hover:bg-[#E8F7F0] hover:text-[#08785D] border border-[#CBD5E1] transition cursor-pointer"
              >
                <Sparkles className="w-4 h-4 text-[#08785D]" />
                <span>Explore Demo Notice</span>
              </button>
            </div>

            {/* 3 Compact Trust Statements */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-4 border-t border-[#E1E7EE]">
              <div className="flex items-start gap-2">
                <ShieldCheck className="w-4 h-4 text-[#08785D] shrink-0 mt-0.5" />
                <div className="text-xs text-[#526176]">
                  <strong className="text-[#12233D] block font-semibold">Source-Backed Facts</strong>
                  Anchored to exact quotes
                </div>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#08785D] shrink-0 mt-0.5" />
                <div className="text-xs text-[#526176]">
                  <strong className="text-[#12233D] block font-semibold">Transparent Uncertainty</strong>
                  Explicitly flags missing info
                </div>
              </div>
              <div className="flex items-start gap-2">
                <Globe2 className="w-4 h-4 text-[#08785D] shrink-0 mt-0.5" />
                <div className="text-xs text-[#526176]">
                  <strong className="text-[#12233D] block font-semibold">Accessible Guidance</strong>
                  Bilingual EN/HI & Read-Aloud
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Realistic Product Preview (Synthetic Demo) */}
          <div className="lg:col-span-5">
            <div className="bg-[#F8FAFC] border border-[#E1E7EE] rounded-2xl p-5 shadow-xs space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#E1E7EE]">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-400" />
                  <div className="w-3 h-3 rounded-full bg-amber-400" />
                  <div className="w-3 h-3 rounded-full bg-emerald-400" />
                  <span className="text-xs font-mono font-bold text-[#526176] ml-2">
                    Notice Intelligence Preview
                  </span>
                </div>
                <span className="text-[10px] font-mono uppercase bg-[#FFF4D6] text-[#92500A] border border-[#FDE68A] px-2 py-0.5 rounded-md font-semibold">
                  Synthetic Demonstration Data
                </span>
              </div>

              {/* Sample Document Title & Badges */}
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-[#08785D] uppercase tracking-wider">
                  National Merit Scholarship 2026
                </span>
                <h4 className="text-sm font-bold text-[#12233D] leading-snug">
                  Department of Higher Education Circular #NMS-2026/88
                </h4>
              </div>

              {/* Sample Verified Fact */}
              <div className="p-3 rounded-xl bg-white border border-[#E1E7EE] space-y-1.5 shadow-2xs">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-[#526176]">Closing Deadline</span>
                  <span className="px-2 py-0.2 rounded-md text-[10px] font-bold bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]">
                    Stated (Verified)
                  </span>
                </div>
                <div className="text-xs font-semibold text-[#12233D]">
                  31 October 2026, 5:00 PM IST
                </div>
                <div className="text-[11px] text-[#68778B] font-mono italic bg-[#F8FAFC] p-1.5 rounded-md border-l-2 border-[#08785D]">
                  "Last date for submission is 31st October 2026 up to 17:00 hrs."
                </div>
              </div>

              {/* Sample Action Item */}
              <div className="p-3 rounded-xl bg-white border border-[#E1E7EE] space-y-1.5 shadow-2xs">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-[#526176]">Action Plan Preview</span>
                  <span className="px-2 py-0.2 rounded-md text-[10px] font-bold bg-[#EAF2FF] text-[#245DC1] border border-[#BFDBFE]">
                    Step 1 of 4
                  </span>
                </div>
                <div className="text-xs text-[#12233D] flex items-center gap-2">
                  <CheckSquare className="w-4 h-4 text-[#08785D]" />
                  <span>Obtain Family Income Certificate (&lt; ₹2.5 Lakhs)</span>
                </div>
              </div>

              <div className="text-[10px] text-center text-[#68778B] italic">
                Demonstration output based on standard PS02 scholarship benchmark notice.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Analysis Entry Point: Upload & Buffer */}
      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-bold text-[#12233D] tracking-tight">
            Analyze a Notice Now
          </h2>
          <p className="text-xs text-[#526176] mt-0.5">
            Drop an official document, scanned photo, or paste raw text to initiate local analysis.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 items-start">
          <div className="bg-white border border-[#E1E7EE] rounded-xl p-5 space-y-4 shadow-xs">
            <span className="text-xs font-bold uppercase tracking-wider text-[#12233D] block">
              📁 Option 1: Upload Document or Photo
            </span>
            <FileDropzone />
            {uploadedImage && <OCRPanel />}
          </div>

          <div className="h-full">
            <NoticeBuffer />
          </div>
        </div>

        {/* Primary Action Button */}
        <div className="pt-2">
          <button
            type="button"
            onClick={runAnalysis}
            disabled={!rawNoticeText.trim() || isAnalyzing}
            className="w-full flex items-center justify-center gap-2.5 py-4 px-6 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-[#08785D] to-[#06664E] hover:from-[#06664E] hover:to-[#054E3C] transition shadow-xs disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            <Sparkles className="w-4 h-4 text-white" />
            <span>Analyze Notice with SuchnaSetu AI</span>
          </button>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="bg-white border border-[#E1E7EE] rounded-2xl p-6 sm:p-8 space-y-6 shadow-xs">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-[#08785D] block mb-1">
            Methodology
          </span>
          <h2 className="text-xl font-bold text-[#12233D] tracking-tight">
            How SuchnaSetu AI Works
          </h2>
          <p className="text-xs text-[#526176] mt-0.5">
            From raw institutional publication to verifiable citizen action in four structured phases.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-2">
            <div className="w-8 h-8 rounded-lg bg-[#E8F7F0] text-[#08785D] flex items-center justify-center font-bold text-xs">
              01
            </div>
            <h3 className="text-sm font-bold text-[#12233D]">Ingestion & OCR</h3>
            <p className="text-xs text-[#526176] leading-relaxed">
              Extracts text from digital PDFs or runs bilingual Tesseract OCR with adaptive contrast enhancement on photos.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-2">
            <div className="w-8 h-8 rounded-lg bg-[#E8F7F0] text-[#08785D] flex items-center justify-center font-bold text-xs">
              02
            </div>
            <h3 className="text-sm font-bold text-[#12233D]">Evidence Grounding</h3>
            <p className="text-xs text-[#526176] leading-relaxed">
              Aligns extracted facts with exact character offsets. Discards unsupported claims or flags them as unstated.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-2">
            <div className="w-8 h-8 rounded-lg bg-[#E8F7F0] text-[#08785D] flex items-center justify-center font-bold text-xs">
              03
            </div>
            <h3 className="text-sm font-bold text-[#12233D]">Plain Synthesis</h3>
            <p className="text-xs text-[#526176] leading-relaxed">
              Translates bureaucratic jargon into concise, accessible answers to 7 core citizen questions in English and Hindi.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-2">
            <div className="w-8 h-8 rounded-lg bg-[#E8F7F0] text-[#08785D] flex items-center justify-center font-bold text-xs">
              04
            </div>
            <h3 className="text-sm font-bold text-[#12233D]">Action Planning</h3>
            <p className="text-xs text-[#526176] leading-relaxed">
              Synthesizes a prioritized checklist with deadline countdowns, required documentation, and calendar export (.ics).
            </p>
          </div>
        </div>
      </section>

      {/* Key Capabilities Grid */}
      <section className="space-y-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-[#08785D] block mb-1">
            Features
          </span>
          <h2 className="text-xl font-bold text-[#12233D] tracking-tight">
            Key Capabilities Built for Public Service
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="bg-white border border-[#E1E7EE] rounded-xl p-5 space-y-3 shadow-xs">
            <div className="w-9 h-9 rounded-xl bg-[#E8F7F0] text-[#08785D] flex items-center justify-center">
              <FileSearch className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-[#12233D]">Ground-Truth Evidence Ledger</h3>
            <p className="text-xs text-[#526176] leading-relaxed">
              Every critical deadline, eligibility rule, fee, and quota is hyperlinked to its exact citation quote in the original notice.
            </p>
          </div>

          <div className="bg-white border border-[#E1E7EE] rounded-xl p-5 space-y-3 shadow-xs">
            <div className="w-9 h-9 rounded-xl bg-[#E8F7F0] text-[#08785D] flex items-center justify-center">
              <GitCompare className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-[#12233D]">Personal Impact Change Tracker</h3>
            <p className="text-xs text-[#526176] leading-relaxed">
              Compares base notices against amendments and corrigenda, tracking date extensions, fee revisions, and qualification changes.
            </p>
          </div>

          <div className="bg-white border border-[#E1E7EE] rounded-xl p-5 space-y-3 shadow-xs">
            <div className="w-9 h-9 rounded-xl bg-[#E8F7F0] text-[#08785D] flex items-center justify-center">
              <Volume2 className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-[#12233D]">Read-Aloud Accessibility</h3>
            <p className="text-xs text-[#526176] leading-relaxed">
              One-click bilingual audio playback with adjustable speech rate for citizens with visual impairments or reading difficulties.
            </p>
          </div>
        </div>
      </section>

      {/* Frequently Asked Questions */}
      <section className="bg-white border border-[#E1E7EE] rounded-2xl p-6 sm:p-8 space-y-5 shadow-xs">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-[#08785D] block mb-1">
            Questions
          </span>
          <h2 className="text-xl font-bold text-[#12233D] tracking-tight">
            Frequently Asked Questions
          </h2>
        </div>

        <div className="space-y-2.5">
          {faqs.map((faq, index) => {
            const isExpanded = expandedFaq === index;
            return (
              <div
                key={index}
                className="border border-[#E1E7EE] rounded-xl overflow-hidden transition"
              >
                <button
                  type="button"
                  onClick={() => setExpandedFaq(isExpanded ? null : index)}
                  className="w-full flex items-center justify-between p-4 text-left font-semibold text-xs text-[#12233D] hover:bg-[#F8FAFC] cursor-pointer"
                >
                  <span>{faq.q}</span>
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4 text-[#08785D] shrink-0" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-[#68778B] shrink-0" />
                  )}
                </button>
                {isExpanded && (
                  <div className="px-4 pb-4 pt-1 text-xs text-[#526176] leading-relaxed bg-[#F8FAFC] border-t border-[#E1E7EE]">
                    {faq.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* Footer */}
      <footer className="pt-6 border-t border-[#E1E7EE] text-center space-y-2 text-xs text-[#68778B]">
        <div className="flex items-center justify-center gap-4 text-xs font-medium text-[#526176]">
          <button type="button" onClick={() => setActiveTab(10)} className="hover:text-[#08785D] cursor-pointer">
            Settings & Diagnostics
          </button>
          <span>•</span>
          <button type="button" onClick={() => setActiveTab(1)} className="hover:text-[#08785D] cursor-pointer">
            Notice Workspace
          </button>
          <span>•</span>
          <button type="button" onClick={() => setActiveTab(4)} className="hover:text-[#08785D] cursor-pointer">
            Revision Ledger
          </button>
        </div>
        <p className="text-[11px]">
          SuchnaSetu AI • HackDay 2026 PS02 • Open, Grounded, Accessible Civic Technology
        </p>
      </footer>
    </div>
  );
};
