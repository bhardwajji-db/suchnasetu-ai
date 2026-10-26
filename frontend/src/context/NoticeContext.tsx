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
  ApplicantProfile,
  EligibilityAssessment,
  PersonalizedActionPlan,
  TrustEvidence,
  AccessibilityPreferences,
  UserProfile,
} from '../types/api';
import { apiClient } from '../services/apiClient';
import { fetchAuthMe, logoutAccount } from '../services/api';
import { useTranslation } from '../i18n';

export type AppTheme = 'light' | 'dark';

export interface HistoryRecord {
  id: string;
  title: string;
  referenceNumber: string;
  authority: string;
  deadline: string;
  timestamp: string;
  charCount: number;
  rawText: string;
}

export interface EvidenceDrawerState {
  isOpen: boolean;
  evidence: TrustEvidence | null;
  rawNoticeOverride?: string;
  suggestedMatch?: string | null;
}

export interface SpeechGuidanceState {
  isSpeaking: boolean;
  isPaused: boolean;
  currentText: string;
  rate: number;
}

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
  localizedSummary: PlainLanguageSummary | null;
  localizedChecklist: ActionChecklist | null;
  selectedLang: string;
  setSelectedLang: (lang: string) => void;
  outputLang: string;
  setOutputLang: (lang: string) => void;
  sourceLang: string;
  setSourceLang: (lang: string) => void;
  detectedLangMeta: { detected_language: string; confidence: number; is_mixed: boolean } | null;
  setDetectedLangMeta: (meta: { detected_language: string; confidence: number; is_mixed: boolean } | null) => void;
  documentId: string | null;
  setDocumentId: (id: string | null) => void;
  theme: AppTheme;
  setTheme: (theme: AppTheme) => void;
  toggleTheme: () => void;
  loadDemoItem: (demoId: string, autoAnalyze?: boolean) => Promise<void>;
  detectDocumentLanguage: () => Promise<void>;
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
  clearAnalysisError: () => void;
  currentUser: UserProfile | null;
  setCurrentUser: (user: UserProfile | null) => void;
  isAuthLoading: boolean;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<UserProfile | null>;
  isAuthModalOpen: boolean;
  setIsAuthModalOpen: (open: boolean) => void;
  openAuthModal: () => void;
  closeAuthModal: () => void;
  openAuthPage: (initialMode?: 'login' | 'signup') => void;
  authPageMode: 'login' | 'signup';
  setAuthPageMode: (mode: 'login' | 'signup') => void;
  followUpHistory: FollowUpAnswer[];
  systemHealth: PreflightReport | null;
  providers: LLMProviderStatus[];
  activeProvider: string;
  switchProvider: (providerId: string) => Promise<void>;
  samples: SampleFixture[];
  activeTab: number;
  setActiveTab: (tab: number) => void;
  isMobileMenuOpen: boolean;
  setIsMobileMenuOpen: (open: boolean) => void;
  toggleMobileMenu: () => void;
  history: HistoryRecord[];
  loadFromHistory: (item: HistoryRecord) => void;
  clearHistory: () => void;
  clearAllData: () => void;

  // Feature C: Saved Notices & Task Search
  savedNoticeIds: string[];
  toggleSaveNotice: (id: string, metadata?: { title?: string; authority?: string; deadline?: string; rawText?: string }) => void;
  isNoticeSaved: (id: string) => boolean;

  // Feature D: Accessibility Mode Preferences
  accessibilityPrefs: AccessibilityPreferences;
  updateAccessibilityPrefs: (prefs: Partial<AccessibilityPreferences>) => void;
  resetAccessibilityPrefs: () => void;

  // New Feature 1 & 3: Applicant Profile & Eligibility & Actions
  applicantProfile: ApplicantProfile;
  setApplicantProfile: React.Dispatch<React.SetStateAction<ApplicantProfile>>;
  savedEligibility: EligibilityAssessment | null;
  setSavedEligibility: (elig: EligibilityAssessment | null) => void;
  actionPlan: PersonalizedActionPlan | null;
  setActionPlan: (plan: PersonalizedActionPlan | null) => void;

  // New Feature 2: Universal Evidence Trust Inspector
  evidenceDrawer: EvidenceDrawerState;
  openEvidenceInspector: (
    evidenceOrQuote: TrustEvidence | { excerpt: string; claim?: string; docTitle?: string },
    rawNoticeOverride?: string
  ) => Promise<void>;
  closeEvidenceInspector: () => void;

  // New Feature 5: Accessibility-First Voice Guidance
  speechState: SpeechGuidanceState;
  speakText: (text: string, lang?: string) => void;
  pauseSpeech: () => void;
  resumeSpeech: () => void;
  stopSpeech: () => void;
  isVoiceInputSupported: boolean;

  // Actions
  loadSampleFixture: (filename: string) => Promise<void>;
  clearBuffer: () => void;
  resetSession: () => void;
  runAnalysis: (overrideText?: string | unknown, overrideLang?: string) => Promise<void>;
  confirmUncertainFact: (fieldName: string) => void;
  toggleChecklistItem: (stepNumber: number) => void;
  askQuestion: (question: string) => Promise<void>;
  clearFollowUpHistory: () => void;
  refreshHealth: () => Promise<void>;
}

const NoticeContext = createContext<NoticeContextType | undefined>(undefined);

const restoreCompletedSteps = (checklist: ActionChecklist | null, fp: string | null): ActionChecklist | null => {
  if (!checklist || !fp || !Array.isArray(checklist.items)) return checklist;
  try {
    const saved = localStorage.getItem('suchnasetu_checklist_completed_' + fp);
    if (!saved) return checklist;
    const completedSteps: number[] = JSON.parse(saved);
    if (!Array.isArray(completedSteps)) return checklist;
    return {
      ...checklist,
      items: checklist.items.map((it) => ({
        ...it,
        is_completed: completedSteps.includes(it.step_number) || it.is_completed,
      })),
    };
  } catch {
    return checklist;
  }
};

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
  const [localizedSummary, setLocalizedSummary] = useState<PlainLanguageSummary | null>(null);
  const [localizedChecklist, setLocalizedChecklist] = useState<ActionChecklist | null>(null);

  const i18n = useTranslation();
  const [localLang, setLocalLang] = useState<string>(() => {
    try {
      return localStorage.getItem('suchnasetu_user_language') || 'en';
    } catch {
      return 'en';
    }
  });

  const selectedLang = i18n?.language || localLang;
  const setSelectedLang = useCallback((lang: string) => {
    setLocalLang(lang);
    if (i18n?.setLanguage) {
      i18n.setLanguage(lang as any);
    }
    try {
      localStorage.setItem('suchnasetu_user_language', lang);
      document.documentElement.lang = lang;
      document.documentElement.dir = lang === 'ur' ? 'rtl' : 'ltr';
    } catch {}
      if (currentUser) {
        apiClient.saveUserPreferences({ language: lang }).catch(() => {});
      }
  }, [i18n]);

  const [outputLang, setOutputLang] = useState<string>('en');
  const [sourceLang, setSourceLang] = useState<string>('auto');
  const [detectedLangMeta, setDetectedLangMeta] = useState<{
    detected_language: string;
    confidence: number;
    is_mixed: boolean;
  } | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [readingLevel, setReadingLevel] = useState<'simple' | 'standard' | 'detailed'>('standard');
  const [isOriginalNoticeOpen, setIsOriginalNoticeOpen] = useState<boolean>(false);
  const [confirmingFact, setConfirmingFact] = useState<{ fieldName: string; displayName: string; fact: any } | null>(null);
  const [analyzedFingerprint, setAnalyzedFingerprint] = useState<string | null>(null);
  const [currentFingerprint, setCurrentFingerprint] = useState<string>('');

  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysisPhase, setAnalysisPhase] = useState<number>(0);
  const [analysisDuration, setAnalysisDuration] = useState<number | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState<boolean>(false);
  const [authPageMode, setAuthPageMode] = useState<'login' | 'signup'>('login');
  const openAuthModal = useCallback(() => setIsAuthModalOpen(true), []);
  const closeAuthModal = useCallback(() => setIsAuthModalOpen(false), []);
  const openAuthPage = useCallback((initialMode?: 'login' | 'signup') => {
    setAuthPageMode(initialMode || 'login');
    setActiveTab(99);
  }, []);
  const clearAnalysisError = useCallback(() => setAnalysisError(null), []);

  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);

  const [theme, setThemeState] = useState<AppTheme>(() => {
    try {
      const saved = localStorage.getItem('suchnasetu_theme');
      if (saved === 'dark' || saved === 'light') return saved;
      return 'light';
    } catch {
      return 'light';
    }
  });

  const setTheme = useCallback((newTheme: AppTheme) => {
    setThemeState(newTheme);
    try {
      localStorage.setItem('suchnasetu_theme', newTheme);
      document.documentElement.setAttribute('data-theme', newTheme);
      if (newTheme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    } catch {}
    if (currentUser) {
      apiClient.saveUserPreferences({ theme: newTheme }).catch(() => {});
    }
  }, [currentUser]);

  const toggleTheme = useCallback(() => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  }, [theme, setTheme]);

  useEffect(() => {
    try {
      document.documentElement.setAttribute('data-theme', theme);
      if (theme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    } catch {}
  }, [theme]);
  const [isAuthLoading, setIsAuthLoading] = useState<boolean>(true);

  const refreshAuth = useCallback(async (): Promise<UserProfile | null> => {
    try {
      const user = await fetchAuthMe();
      setCurrentUser(user);
      if (user) {
        try {
          const prefData = await apiClient.getUserPreferences();
          if (prefData?.preferences) {
            const p = prefData.preferences;
            if (p.language) {
              setLocalLang(p.language);
              if (i18n?.setLanguage) {
                i18n.setLanguage(p.language as any);
              }
              try {
                localStorage.setItem('suchnasetu_user_language', p.language);
                document.documentElement.lang = p.language;
                document.documentElement.dir = p.language === 'ur' ? 'rtl' : 'ltr';
              } catch {}
            }
            if (p.reading_level && ['simple', 'standard', 'detailed'].includes(p.reading_level)) {
              setReadingLevel(p.reading_level);
            }
            if (p.theme && ['light', 'dark'].includes(p.theme)) {
              setThemeState(p.theme as AppTheme);
              try {
                localStorage.setItem('suchnasetu_theme', p.theme);
                document.documentElement.setAttribute('data-theme', p.theme);
                if (p.theme === 'dark') {
                  document.documentElement.classList.add('dark');
                } else {
                  document.documentElement.classList.remove('dark');
                }
              } catch {}
            }
          }
        } catch {}
      }
      return user;
    } catch {
      setCurrentUser(null);
      return null;
    } finally {
      setIsAuthLoading(false);
    }
  }, [i18n]);

  useEffect(() => {
    refreshAuth();
  }, [refreshAuth]);

  const logout = useCallback(async () => {
    try {
      await logoutAccount();
    } finally {
      setCurrentUser(null);
    }
  }, []);

  const [followUpHistory, setFollowUpHistory] = useState<FollowUpAnswer[]>([]);
  const [systemHealth, setSystemHealth] = useState<PreflightReport | null>(null);
  const [providers, setProviders] = useState<LLMProviderStatus[]>([]);
  const [activeProvider, setActiveProvider] = useState<string>('ollama');
  const [samples, setSamples] = useState<SampleFixture[]>([]);
  const [activeTab, setActiveTabState] = useState<number>(0);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState<boolean>(false);
  const toggleMobileMenu = useCallback(() => setIsMobileMenuOpen((prev) => !prev), []);
  const setActiveTab = useCallback((tab: number) => {
    setActiveTabState(tab);
    setIsMobileMenuOpen(false);
  }, []);
  const [history, setHistory] = useState<HistoryRecord[]>(() => {
    try {
      const saved = localStorage.getItem('notice2action_history');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Feature C: Saved Notices (with SQLite & Cross-User Backend Sync)
  const [savedNoticeIds, setSavedNoticeIds] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('suchnasetu_saved_notice_ids');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Sync saved notices with backend on mount
  useEffect(() => {
    let isMounted = true;
    apiClient.getSavedNotices()
      .then((records) => {
        if (isMounted && Array.isArray(records)) {
          const docIds = records.map((r: any) => r.document_id).filter(Boolean);
          if (docIds.length > 0) {
            setSavedNoticeIds((prev) => {
              const combined = Array.from(new Set([...prev, ...docIds]));
              try {
                localStorage.setItem('suchnasetu_saved_notice_ids', JSON.stringify(combined));
              } catch {}
              return combined;
            });

            // Hydrate backend saved notices into local history
            setHistory((prev) => {
              const existingIds = new Set(prev.map((h) => h.id));
              const newRecords: HistoryRecord[] = records
                .filter((r: any) => r.document_id && !existingIds.has(r.document_id))
                .map((r: any) => ({
                  id: r.document_id,
                  title: r.title || 'Saved Notice',
                  referenceNumber: r.reference_number || r.document_id,
                  authority: r.authority || 'Official Authority',
                  deadline: r.deadline || 'Not stated',
                  timestamp: r.created_at || new Date().toISOString(),
                  charCount: r.raw_text ? r.raw_text.length : 0,
                  rawText: r.raw_text || '',
                }));
              if (newRecords.length === 0) return prev;
              const merged = [...prev, ...newRecords];
              try {
                localStorage.setItem('notice2action_history', JSON.stringify(merged));
              } catch {}
              return merged;
            });
          }
        }
      })
      .catch(() => {});
    return () => { isMounted = false; };
  }, []);

  const toggleSaveNotice = useCallback((id: string, metadata?: { title?: string; authority?: string; deadline?: string; rawText?: string }) => {
    setSavedNoticeIds((prev) => {
      const isCurrentlySaved = prev.includes(id);
      const updated = isCurrentlySaved ? prev.filter((x) => x !== id) : [...prev, id];
      try {
        localStorage.setItem('suchnasetu_saved_notice_ids', JSON.stringify(updated));
      } catch (e) {
        console.error('Failed to save to localStorage', e);
      }

      // Sync with backend SQLite
      if (isCurrentlySaved) {
        apiClient.unsaveUserNotice(id).catch(() => {});
      } else {
        apiClient.saveUserNotice(id, {
          title: metadata?.title || 'Notice',
          authority: metadata?.authority || '',
          deadline: metadata?.deadline || '',
          raw_text: metadata?.rawText || '',
          assignment_title: metadata?.title || 'Notice Action',
        }).catch(() => {});
      }

      return updated;
    });
  }, []);

  const isNoticeSaved = useCallback(
    (id: string) => savedNoticeIds.includes(id),
    [savedNoticeIds]
  );

  // Feature D: Accessibility Mode Preferences
  const DEFAULT_ACCESSIBILITY_PREFS: AccessibilityPreferences = {
    textSize: 'normal',
    lineSpacing: 'normal',
    highContrast: false,
    warmBackground: false,
    highlightKeyInfo: false,
    reducedMotion: false,
  };

  const [accessibilityPrefs, setAccessibilityPrefs] = useState<AccessibilityPreferences>(() => {
    try {
      const saved = localStorage.getItem('suchnasetu_accessibility_prefs');
      return saved ? JSON.parse(saved) : DEFAULT_ACCESSIBILITY_PREFS;
    } catch {
      return DEFAULT_ACCESSIBILITY_PREFS;
    }
  });

  const updateAccessibilityPrefs = useCallback((prefs: Partial<AccessibilityPreferences>) => {
    setAccessibilityPrefs((prev) => {
      const updated = { ...prev, ...prefs };
      try {
        localStorage.setItem('suchnasetu_accessibility_prefs', JSON.stringify(updated));
      } catch (e) {
        console.error('Failed to save accessibility prefs', e);
      }
      return updated;
    });
  }, []);

  const resetAccessibilityPrefs = useCallback(() => {
    setAccessibilityPrefs(DEFAULT_ACCESSIBILITY_PREFS);
    try {
      localStorage.setItem('suchnasetu_accessibility_prefs', JSON.stringify(DEFAULT_ACCESSIBILITY_PREFS));
    } catch (e) {
      console.error('Failed to reset accessibility prefs', e);
    }
  }, []);

  // Feature 1 & 3: Applicant Profile, Eligibility, Action Plan
  const [applicantProfile, setApplicantProfile] = useState<ApplicantProfile>({
    category: 'General',
    marks_percentage: undefined,
    degree: '',
    date_of_birth: '',
  });
  const [savedEligibility, setSavedEligibility] = useState<EligibilityAssessment | null>(null);
  const [actionPlan, setActionPlan] = useState<PersonalizedActionPlan | null>(null);

  // Feature 2: Universal Evidence Trust Drawer
  const [evidenceDrawer, setEvidenceDrawer] = useState<EvidenceDrawerState>({
    isOpen: false,
    evidence: null,
  });

  const openEvidenceInspector = useCallback(
    async (
      evidenceOrQuote: TrustEvidence | { excerpt: string; claim?: string; docTitle?: string },
      rawNoticeOverride?: string
    ) => {
      if ('evidence_id' in evidenceOrQuote) {
        setEvidenceDrawer({
          isOpen: true,
          evidence: evidenceOrQuote,
          rawNoticeOverride,
        });
        return;
      }

      // Verify on the fly
      const source = rawNoticeOverride || rawNoticeText;
      try {
        const res = await apiClient.verifyEvidence(
          source,
          evidenceOrQuote.excerpt,
          evidenceOrQuote.claim,
          evidenceOrQuote.docTitle
        );
        setEvidenceDrawer({
          isOpen: true,
          evidence: res.evidence,
          rawNoticeOverride,
          suggestedMatch: res.suggested_match,
        });
      } catch {
        setEvidenceDrawer({
          isOpen: true,
          evidence: {
            evidence_id: 'err',
            claim_text: evidenceOrQuote.claim || '',
            verbatim_excerpt: evidenceOrQuote.excerpt,
            verification_status: 'UNVERIFIED',
            confidence_rationale: 'Could not communicate with verification service.',
            is_inert_safe: true,
          },
          rawNoticeOverride,
        });
      }
    },
    [rawNoticeText]
  );

  const closeEvidenceInspector = useCallback(() => {
    setEvidenceDrawer((prev) => ({ ...prev, isOpen: false }));
  }, []);

  // Feature 5: Voice Guidance
  const [speechState, setSpeechState] = useState<SpeechGuidanceState>({
    isSpeaking: false,
    isPaused: false,
    currentText: '',
    rate: 1.0,
  });

  const speakText = useCallback((text: string, lang: string = 'en') => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;

    window.speechSynthesis.cancel();
    if (!text || !text.trim()) {
      setSpeechState((prev) => ({ ...prev, isSpeaking: false, isPaused: false, currentText: '' }));
      return;
    }

    const clean = text.replace(/[*#_`]/g, '').trim();
    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.lang = lang === 'hi' ? 'hi-IN' : 'en-IN';
    utterance.rate = 0.95;

    utterance.onstart = () => {
      setSpeechState({ isSpeaking: true, isPaused: false, currentText: clean, rate: 0.95 });
    };

    utterance.onend = () => {
      setSpeechState((prev) => ({ ...prev, isSpeaking: false, isPaused: false, currentText: '' }));
    };

    utterance.onerror = () => {
      setSpeechState((prev) => ({ ...prev, isSpeaking: false, isPaused: false, currentText: '' }));
    };

    window.speechSynthesis.speak(utterance);
  }, []);

  const pauseSpeech = useCallback(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.pause();
      setSpeechState((prev) => ({ ...prev, isPaused: true }));
    }
  }, []);

  const resumeSpeech = useCallback(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.resume();
      setSpeechState((prev) => ({ ...prev, isPaused: false }));
    }
  }, []);

  const stopSpeech = useCallback(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setSpeechState({ isSpeaking: false, isPaused: false, currentText: '', rate: 1.0 });
    }
  }, []);

  const isVoiceInputSupported = typeof window !== 'undefined' &&
    Boolean((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);

  const loadFromHistory = useCallback((item: HistoryRecord) => {
    setRawNoticeText(item.rawText);
    setActiveTab(2); // Jump to Grounded Facts view
  }, []);

  const clearHistory = useCallback(() => {
    setHistory([]);
    try {
      localStorage.removeItem('notice2action_history');
    } catch {}
  }, []);

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

  const setUploadedImage = useCallback((url: string | null, file?: File | null) => {
    setUploadedImageState(url);
    setUploadedFile(file || null);
  }, []);

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
    let isMounted = true;
    const initialize = async () => {
      try {
        await refreshHealth();
        const sampleList = await apiClient.getSamples();
        if (isMounted) {
          setSamples(sampleList);
        }
      } catch (err) {
        console.error('Initialization error:', err);
      }
    };
    initialize();
    return () => {
      isMounted = false;
    };
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
    setLocalizedSummary(null);
    setLocalizedChecklist(null);
    setDocumentId(null);
    setDetectedLangMeta(null);
    setSourceLang('auto');
    if (analyzedFingerprint) {
      try {
        localStorage.removeItem(`suchnasetu_checklist_completed_${analyzedFingerprint}`);
      } catch {}
    }
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
    setActiveTab(0);
  };

  const clearAllData = useCallback(() => {
    clearBuffer();
    setHistory([]);
    try {
      localStorage.removeItem('notice2action_history');
    } catch {}
    setActiveTab(0);
  }, []);

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
      setActiveTab(1);
    } catch (err: any) {
      setAnalysisError(`Failed to load fixture: ${err.message}`);
    }
  };

  const runAnalysis = useCallback(
    async (overrideText?: string | unknown, overrideLang?: string) => {
      const textToAnalyze = (typeof overrideText === "string" ? overrideText : rawNoticeText).trim();
      if (isAnalyzing) return; // Prevent duplicate concurrent inference requests
      if (!textToAnalyze) {
        setAnalysisError('Please enter notice text or upload a notice document first.');
        return;
      }

      setIsAnalyzing(true);
      setAnalysisError(null);
      setAnalysisPhase(1);

      const p1Timer = setTimeout(() => setAnalysisPhase(2), 1000);
      const p2Timer = setTimeout(() => setAnalysisPhase(3), 2500);

      try {
        const targetLang = overrideLang || outputLang || selectedLang || 'en';
        const res = await apiClient.analyzeNotice(
          textToAnalyze,
          targetLang,
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
        const fp = res.fingerprint || currentFingerprint;
        setSummaryEn(res.summary_en);
        setSummaryHi(res.summary_hi);
        if (res.checklist_en) {
          setChecklistEn(restoreCompletedSteps(res.checklist_en, fp));
        } else {
          setChecklistEn(null);
        }
        if (res.checklist_hi) {
          setChecklistHi(restoreCompletedSteps(res.checklist_hi, fp));
        } else {
          setChecklistHi(null);
        }
        if (res.localized_summary) {
          setLocalizedSummary(res.localized_summary);
        }
        if (res.localized_checklist) {
          setLocalizedChecklist(restoreCompletedSteps(res.localized_checklist, fp));
        }
        if (res.document_id) {
          setDocumentId(res.document_id);
        }
        if (res.detected_language) {
          setDetectedLangMeta({
            detected_language: res.detected_language,
            confidence: res.language_confidence ?? 1.0,
            is_mixed: res.is_mixed_language ?? false,
          });
          if (sourceLang === 'auto') {
            setSourceLang(res.detected_language);
          }
        }
        setAnalyzedFingerprint(res.fingerprint);
        setAnalysisDuration(res.duration_seconds);
        setAnalysisPhase(5);

        // Record to recent notice history
        const historyItem: HistoryRecord = {
          id: res.session_id || res.fingerprint || `hist_${Date.now()}`,
          title:
            res.structured_notice?.main_subject?.value ||
            res.structured_notice?.purpose?.value ||
            'Official Notice',
          referenceNumber: res.structured_notice?.notice_reference_number?.value || 'Not specified',
          authority: res.structured_notice?.issuing_authority?.value || 'Authority Unspecified',
          deadline: res.structured_notice?.deadline?.value || 'No deadline specified',
          timestamp:
            new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) +
            ' · ' +
            new Date().toLocaleDateString(),
          charCount: textToAnalyze.length,
          rawText: textToAnalyze,
        };
        setHistory((prev) => {
          const filtered = prev.filter((h) => h.id !== historyItem.id);
          const updated = [historyItem, ...filtered].slice(0, 15);
          try {
            localStorage.setItem('notice2action_history', JSON.stringify(updated));
          } catch {}
          return updated;
        });
      } catch (err: any) {
        clearTimeout(p1Timer);
        clearTimeout(p2Timer);
        setAnalysisError(err.message || 'Analysis failed. Please verify provider configuration or local Ollama.');
      } finally {
        clearTimeout(p1Timer);
        clearTimeout(p2Timer);
        setIsAnalyzing(false);
      }
    },
    [
      isAnalyzing,
      rawNoticeText,
      outputLang,
      selectedLang,
      readingLevel,
      sessionId,
      activeProvider,
      currentFingerprint,
      sourceLang,
    ]
  );

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
      setChecklistEn(restoreCompletedSteps(res.checklist_en, analyzedFingerprint));
      setChecklistHi(restoreCompletedSteps(res.checklist_hi, analyzedFingerprint));
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
    if (currentUser) {
      apiClient.saveUserPreferences({ reading_level: level }).catch(() => {});
    }
    if (!structuredNotice) return;
    try {
      const targetLang = outputLang || selectedLang || 'en';
      const res = await apiClient.getReadingLevelSummary(
        structuredNotice,
        level,
        targetLang,
        sessionId || undefined
      );
      setSummaryEn(res.summary_en);
      setSummaryHi(res.summary_hi);
      if (res.localized_summary) {
        setLocalizedSummary(res.localized_summary);
      }
    } catch (e) {
      console.error('Failed to change reading level', e);
    }
  }, [structuredNotice, outputLang, selectedLang, sessionId]);

  const confirmUncertainFact = (fieldName: string) => {
    if (!structuredNotice) return;
    const fact = (structuredNotice as any)[fieldName];
    if (fact) {
      openConfirmationModal(fieldName, fieldName.replaceAll('_', ' ').toUpperCase(), fact);
    }
  };

  const toggleChecklistItem = (stepNumber: number) => {
    const fp = analyzedFingerprint || currentFingerprint || 'active';
    let newCompletedSteps: number[] = [];
    const updateChecklist = (cl: ActionChecklist | null) => {
      if (!cl) return null;
      const updated = cl.items.map((it) =>
        it.step_number === stepNumber ? { ...it, is_completed: !it.is_completed } : it
      );
      newCompletedSteps = updated.filter((it) => it.is_completed).map((it) => it.step_number);
      return {
        ...cl,
        items: updated,
      };
    };
    setChecklistEn(updateChecklist(checklistEn));
    setChecklistHi(updateChecklist(checklistHi));
    try {
      localStorage.setItem(`suchnasetu_checklist_completed_${fp}`, JSON.stringify(newCompletedSteps));
      const stepItem = checklistEn?.items.find((it) => it.step_number === stepNumber);
      if (stepItem) {
        const itemId = `${fp}_step_${stepNumber}`;
        apiClient.toggleChecklistItemPersistent(itemId, !stepItem.is_completed).catch(() => {});
      }
    } catch (e) {
      console.error('Failed to save checklist state to localStorage', e);
    }
  };

  const detectDocumentLanguage = useCallback(async () => {
    if (!rawNoticeText.trim()) return;
    try {
      const det = await apiClient.detectLanguage(rawNoticeText);
      setDetectedLangMeta({
        detected_language: det.detected_language,
        confidence: det.confidence,
        is_mixed: det.is_mixed,
      });
      if (sourceLang === 'auto') {
        setSourceLang(det.detected_language);
      }
    } catch (e) {
      console.error('Failed to detect language', e);
    }
  }, [rawNoticeText, sourceLang]);

  const loadDemoItem = useCallback(
    async (demoId: string, autoAnalyze: boolean = true) => {
      try {
        setAnalysisError(null);
        const demo = await apiClient.loadDemoLibraryItem(demoId);
        const rawText = demo.raw_text || demo.text || '';
        const lang = demo.source_language || demo.language || 'en';

        setRawNoticeText(rawText);
        setSourceLang(lang);
        setDetectedLangMeta({
          detected_language: lang,
          confidence: 0.99,
          is_mixed: false,
        });
        setUploadedImageState(null);
        setUploadedFile(null);
        setStructuredNotice(null);
        setSixCoreFields(null);
        setSummaryEn(null);
        setSummaryHi(null);
        setChecklistEn(null);
        setChecklistHi(null);
        setLocalizedSummary(null);
        setLocalizedChecklist(null);
        setAnalyzedFingerprint(null);
        setAnalysisDuration(null);
        setFollowUpHistory([]);

        // Jump to Notice Ingestion tab (Dual-Region Intelligence Workspace)
        setActiveTab(1);

        if (autoAnalyze && rawText.trim()) {
          await runAnalysis(rawText, lang);
        }
      } catch (err: any) {
        setAnalysisError(`Failed to load demo notice: ${err.message}`);
        setActiveTab(1);
      }
    },
    [runAnalysis, setActiveTab]
  );

  const askQuestion = async (question: string) => {
    if (!question.trim() || !rawNoticeText.trim()) return;
    try {
      const langForQuery = outputLang || selectedLang || 'en';
      const answer = await apiClient.askFollowUp(question, rawNoticeText, sessionId, langForQuery);
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
        localizedSummary,
        localizedChecklist,
        selectedLang,
        setSelectedLang,
        outputLang,
        setOutputLang,
        sourceLang,
        setSourceLang,
        detectedLangMeta,
        setDetectedLangMeta,
        documentId,
        setDocumentId,
        loadDemoItem,
        detectDocumentLanguage,
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
        clearAnalysisError,
        currentUser,
        setCurrentUser,
        isAuthLoading,
        logout,
        refreshAuth,
        isAuthModalOpen,
        setIsAuthModalOpen,
        openAuthModal,
        closeAuthModal,
        openAuthPage,
        authPageMode,
        setAuthPageMode,
        followUpHistory,
        systemHealth,
        providers,
        activeProvider,
        switchProvider,
        samples,
        activeTab,
        setActiveTab,
        isMobileMenuOpen,
        setIsMobileMenuOpen,
        toggleMobileMenu,
        history,
        loadFromHistory,
        clearHistory,
        clearAllData,
        savedNoticeIds,
        toggleSaveNotice,
        isNoticeSaved,
        accessibilityPrefs,
        updateAccessibilityPrefs,
        resetAccessibilityPrefs,
        applicantProfile,
        setApplicantProfile,
        savedEligibility,
        setSavedEligibility,
        actionPlan,
        setActionPlan,
        evidenceDrawer,
        openEvidenceInspector,
        closeEvidenceInspector,
        speechState,
        speakText,
        pauseSpeech,
        resumeSpeech,
        stopSpeech,
        isVoiceInputSupported,
        loadSampleFixture,
        clearBuffer,
        resetSession,
        runAnalysis,
        confirmUncertainFact,
        toggleChecklistItem,
        askQuestion,
        clearFollowUpHistory,
        refreshHealth,
        theme,
        setTheme,
        toggleTheme,
      }}
    >
      {children}
    </NoticeContext.Provider>
  );
};

// oxlint-disable-next-line react/only-export-components
export const useNotice = () => {
  const context = useContext(NoticeContext);
  if (!context) {
    throw new Error('useNotice must be used within a NoticeProvider');
  }
  return context;
};
