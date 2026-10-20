import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type {
  StructuredNotice,
  SixCoreFields,
  PlainLanguageSummary,
  ActionChecklist,
  FollowUpAnswer,
  PreflightReport,
  SampleFixture,
  OCRResponse,
  LLMProviderStatus,
} from '../types/api';
import { apiClient } from '../services/apiClient';

interface NoticeContextType {
  sessionId: string | null;
  rawNoticeText: string;
  setRawNoticeText: (text: string) => void;
  uploadedImage: string | null;
  uploadedFile: File | null;
  setUploadedImage: (url: string | null, file?: File | null) => void;
  ocrResult: OCRResponse | null;
  setOcrResult: (res: OCRResponse | null) => void;
  structuredNotice: StructuredNotice | null;
  sixCoreFields: SixCoreFields | null;
  summaryEn: PlainLanguageSummary | null;
  summaryHi: PlainLanguageSummary | null;
  checklistEn: ActionChecklist | null;
  checklistHi: ActionChecklist | null;
  selectedLang: 'en' | 'hi';
  setSelectedLang: (lang: 'en' | 'hi') => void;
  readingLevel: 'simple' | 'standard' | 'detailed';
  setReadingLevel: (level: 'simple' | 'standard' | 'detailed') => void;
  changeReadingLevel: (level: 'simple' | 'standard' | 'detailed') => Promise<void>;
  isOriginalNoticeOpen: boolean;
  openOriginalNoticeModal: () => void;
  closeOriginalNoticeModal: () => void;
  confirmingFact: { fieldName: string; displayName: string; fact: any } | null;
  openConfirmationModal: (fieldName: string, displayName: string, fact: any) => void;
  closeConfirmationModal: () => void;
  saveConfirmation: (fieldName: string, confirmedValue: string) => Promise<void>;
  analyzedFingerprint: string | null;
  isNoticeStale: boolean;
  isAnalyzing: boolean;
  analysisPhase: number;
  analysisDuration: number | null;
  analysisError: string | null;
  followUpHistory: FollowUpAnswer[];
  systemHealth: PreflightReport | null;
  providers: LLMProviderStatus[];
  activeProvider: string;
  switchProvider: (providerId: string) => Promise<void>;
  samples: SampleFixture[];
  activeTab: number;
  setActiveTab: (tab: number) => void;
  // Actions
  loadSampleFixture: (filename: string) => Promise<void>;
  clearBuffer: () => void;
  resetSession: () => void;
  runAnalysis: () => Promise<void>;
  confirmUncertainFact: (fieldName: string) => void;
  toggleChecklistItem: (stepNumber: number) => void;
  askQuestion: (question: string) => Promise<void>;
  clearFollowUpHistory: () => void;
  refreshHealth: () => Promise<void>;
}

const NoticeContext = createContext<NoticeContextType | undefined>(undefined);

export const NoticeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [rawNoticeText, setRawNoticeText] = useState<string>('');
  const [uploadedImage, setUploadedImageState] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [ocrResult, setOcrResult] = useState<OCRResponse | null>(null);

  const [structuredNotice, setStructuredNotice] = useState<StructuredNotice | null>(null);
  const [sixCoreFields, setSixCoreFields] = useState<SixCoreFields | null>(null);
  const [summaryEn, setSummaryEn] = useState<PlainLanguageSummary | null>(null);
  const [summaryHi, setSummaryHi] = useState<PlainLanguageSummary | null>(null);
  const [checklistEn, setChecklistEn] = useState<ActionChecklist | null>(null);
  const [checklistHi, setChecklistHi] = useState<ActionChecklist | null>(null);

  const [selectedLang, setSelectedLang] = useState<'en' | 'hi'>('en');
  const [readingLevel, setReadingLevel] = useState<'simple' | 'standard' | 'detailed'>('standard');
  const [isOriginalNoticeOpen, setIsOriginalNoticeOpen] = useState<boolean>(false);
  const [confirmingFact, setConfirmingFact] = useState<{ fieldName: string; displayName: string; fact: any } | null>(null);
  const [analyzedFingerprint, setAnalyzedFingerprint] = useState<string | null>(null);
  const [currentFingerprint, setCurrentFingerprint] = useState<string>('');

  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysisPhase, setAnalysisPhase] = useState<number>(0);
  const [analysisDuration, setAnalysisDuration] = useState<number | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const [followUpHistory, setFollowUpHistory] = useState<FollowUpAnswer[]>([]);
  const [systemHealth, setSystemHealth] = useState<PreflightReport | null>(null);
  const [providers, setProviders] = useState<LLMProviderStatus[]>([]);
  const [activeProvider, setActiveProvider] = useState<string>('ollama');
  const [samples, setSamples] = useState<SampleFixture[]>([]);
  const [activeTab, setActiveTab] = useState<number>(0);

  // Compute SHA-256 hash using Web Crypto API
  useEffect(() => {
    let isCancelled = false;
    async function hashText() {
      const clean = rawNoticeText.trim();
      if (!clean) {
        if (!isCancelled) setCurrentFingerprint('');
        return;
      }
      const encoder = new TextEncoder();
      const data = encoder.encode(clean);
      const hashBuffer = await crypto.subtle.digest('SHA-256', data);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
      if (!isCancelled) {
        setCurrentFingerprint(hashHex);
      }
    }
    hashText();
    return () => {
      isCancelled = true;
    };
  }, [rawNoticeText]);

  const isNoticeStale = Boolean(
    structuredNotice !== null &&
    analyzedFingerprint !== null &&
    currentFingerprint !== '' &&
    currentFingerprint !== analyzedFingerprint
  );

  const setUploadedImage = (url: string | null, file?: File | null) => {
    setUploadedImageState(url);
    setUploadedFile(file || null);
  };

  const refreshHealth = useCallback(async () => {
    try {
      const health = await apiClient.getHealth();
      setSystemHealth(health);
      if (health.active_provider) {
        setActiveProvider(health.active_provider);
      }
      const provs = await apiClient.getProviders();
      setProviders(provs);
    } catch (e) {
      console.error('Failed to load system health or providers', e);
    }
  }, []);

  const switchProvider = useCallback(async (providerId: string) => {
    try {
      await apiClient.selectProvider(providerId);
      setActiveProvider(providerId);
      refreshHealth();
    } catch (e: any) {
      setAnalysisError(`Failed to switch provider: ${e.message}`);
    }
  }, [refreshHealth]);

  useEffect(() => {
    refreshHealth();
    apiClient.getSamples().then(setSamples).catch(console.error);
  }, [refreshHealth]);

  const clearBuffer = () => {
    setRawNoticeText('');
    setUploadedImageState(null);
    setUploadedFile(null);
    setOcrResult(null);
    setStructuredNotice(null);
    setSixCoreFields(null);
    setSummaryEn(null);
    setSummaryHi(null);
    setChecklistEn(null);
    setChecklistHi(null);
    setAnalyzedFingerprint(null);
    setAnalysisDuration(null);
    setAnalysisError(null);
    setFollowUpHistory([]);
    setIsOriginalNoticeOpen(false);
    setConfirmingFact(null);
    setReadingLevel('standard');
    setSessionId(null);
  };

  const resetSession = () => {
    clearBuffer();
    setSelectedLang('en');
    setActiveTab(0);
  };

  const loadSampleFixture = async (filename: string) => {
    try {
      if (filename.endsWith('.png') || filename.endsWith('.jpg')) {
        const blob = await apiClient.getSampleImage(filename);
        const url = URL.createObjectURL(blob);
        const file = new File([blob], filename, { type: 'image/png' });
        setUploadedImage(url, file);
        setRawNoticeText('');
      } else {
        const data = await apiClient.getSampleText(filename);
        setRawNoticeText(data.content);
        setUploadedImageState(null);
        setUploadedFile(null);
      }
      setStructuredNotice(null);
      setSixCoreFields(null);
      setSummaryEn(null);
      setSummaryHi(null);
      setChecklistEn(null);
      setChecklistHi(null);
      setAnalyzedFingerprint(null);
      setAnalysisDuration(null);
      setAnalysisError(null);
      setFollowUpHistory([]);

      if (filename.includes('hindi')) {
        setSelectedLang('hi');
      }
      setActiveTab(0);
    } catch (err: any) {
      setAnalysisError(`Failed to load fixture: ${err.message}`);
    }
  };

  const runAnalysis = async () => {
    if (!rawNoticeText.trim()) {
      setAnalysisError('Please enter notice text or upload a notice document first.');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisError(null);
    setAnalysisPhase(1);

    const timer = setInterval(() => {
      setAnalysisPhase((p) => (p < 5 ? p + 1 : 5));
    }, 1200);

    try {
      const res = await apiClient.analyzeNotice(
        rawNoticeText,
        selectedLang,
        readingLevel,
        sessionId,
        activeProvider
      );
      if (res.session_id) {
        setSessionId(res.session_id);
      }
      setStructuredNotice(res.structured_notice);
      if (res.six_core_fields) {
        setSixCoreFields(res.six_core_fields);
      }
      setSummaryEn(res.summary_en);
      setSummaryHi(res.summary_hi);
      setChecklistEn(res.checklist_en);
      setChecklistHi(res.checklist_hi);
      setAnalyzedFingerprint(res.fingerprint);
      setAnalysisDuration(res.duration_seconds);
      setAnalysisPhase(5);
    } catch (err: any) {
      setAnalysisError(err.message || 'Analysis failed. Please verify provider configuration or local Ollama.');
    } finally {
      clearInterval(timer);
      setIsAnalyzing(false);
    }
  };

  const openOriginalNoticeModal = useCallback(() => setIsOriginalNoticeOpen(true), []);
  const closeOriginalNoticeModal = useCallback(() => setIsOriginalNoticeOpen(false), []);

  const openConfirmationModal = useCallback((fieldName: string, displayName: string, fact: any) => {
    setConfirmingFact({ fieldName, displayName, fact });
  }, []);

  const closeConfirmationModal = useCallback(() => setConfirmingFact(null), []);

  const saveConfirmation = useCallback(async (fieldName: string, confirmedValue: string) => {
    if (!structuredNotice) return;
    try {
      const res = await apiClient.confirmFact(
        fieldName,
        confirmedValue,
        structuredNotice,
        readingLevel,
        sessionId
      );
      setStructuredNotice(res.structured_notice);
      if (res.six_core_fields) {
        setSixCoreFields(res.six_core_fields);
      }
      setSummaryEn(res.summary_en);
      setSummaryHi(res.summary_hi);
      setChecklistEn(res.checklist_en);
      setChecklistHi(res.checklist_hi);
    } catch {
      // Local fallback
      const updated = { ...structuredNotice };
      const fact = (updated as any)[fieldName];
      if (fact) {
        fact.user_confirmed = true;
        fact.confirmed_value = confirmedValue;
        fact.requires_confirmation = false;
        setStructuredNotice(updated);
      }
    }
  }, [structuredNotice, readingLevel, sessionId]);

  const changeReadingLevel = useCallback(async (level: 'simple' | 'standard' | 'detailed') => {
    setReadingLevel(level);
    if (!structuredNotice) return;
    try {
      const res = await apiClient.getReadingLevelSummary(structuredNotice, level);
      setSummaryEn(res.summary_en);
      setSummaryHi(res.summary_hi);
    } catch (e) {
      console.error('Failed to change reading level', e);
    }
  }, [structuredNotice]);

  const confirmUncertainFact = (fieldName: string) => {
    if (!structuredNotice) return;
    const fact = (structuredNotice as any)[fieldName];
    if (fact) {
      openConfirmationModal(fieldName, fieldName.replace('_', ' ').toUpperCase(), fact);
    }
  };

  const toggleChecklistItem = (stepNumber: number) => {
    const updateChecklist = (cl: ActionChecklist | null) => {
      if (!cl) return null;
      return {
        ...cl,
        items: cl.items.map((it) =>
          it.step_number === stepNumber ? { ...it, is_completed: !it.is_completed } : it
        ),
      };
    };
    setChecklistEn(updateChecklist(checklistEn));
    setChecklistHi(updateChecklist(checklistHi));
  };

  const askQuestion = async (question: string) => {
    if (!question.trim() || !rawNoticeText.trim()) return;
    try {
      const answer = await apiClient.askFollowUp(question, rawNoticeText, sessionId, selectedLang);
      setFollowUpHistory((prev) => [answer, ...prev]);
    } catch (err: any) {
      setFollowUpHistory((prev) => [
        {
          question,
          answer: `Could not process query: ${err.message}`,
          is_supported: false,
        },
        ...prev,
      ]);
    }
  };

  const clearFollowUpHistory = () => {
    setFollowUpHistory([]);
  };

  return (
    <NoticeContext.Provider
      value={{
        sessionId,
        rawNoticeText,
        setRawNoticeText,
        uploadedImage,
        uploadedFile,
        setUploadedImage,
        ocrResult,
        setOcrResult,
        structuredNotice,
        sixCoreFields,
        summaryEn,
        summaryHi,
        checklistEn,
        checklistHi,
        selectedLang,
        setSelectedLang,
        readingLevel,
        setReadingLevel,
        changeReadingLevel,
        isOriginalNoticeOpen,
        openOriginalNoticeModal,
        closeOriginalNoticeModal,
        confirmingFact,
        openConfirmationModal,
        closeConfirmationModal,
        saveConfirmation,
        analyzedFingerprint,
        isNoticeStale,
        isAnalyzing,
        analysisPhase,
        analysisDuration,
        analysisError,
        followUpHistory,
        systemHealth,
        providers,
        activeProvider,
        switchProvider,
        samples,
        activeTab,
        setActiveTab,
        loadSampleFixture,
        clearBuffer,
        resetSession,
        runAnalysis,
        confirmUncertainFact,
        toggleChecklistItem,
        askQuestion,
        clearFollowUpHistory,
        refreshHealth,
      }}
    >
      {children}
    </NoticeContext.Provider>
  );
};

export const useNotice = () => {
  const context = useContext(NoticeContext);
  if (!context) {
    throw new Error('useNotice must be used within a NoticeProvider');
  }
  return context;
};
