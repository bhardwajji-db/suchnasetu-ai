/**
 * SuchnaSetu AI — Typed API Client
 * Communicates with FastAPI backend (/api routes)
 */

import type {
  PreflightReport,
  SampleFixture,
  IngestTextResponse,
  OCRResponse,
  AnalyzeResponse,
  FollowUpAnswer,
  StructuredNotice,
  PlainLanguageSummary,
  ActionChecklist,
  ConfirmFactResponse,
  ReadingLevelResponse,
  LLMProviderStatus,
  EvidenceCitation,
  NoticeRelationship,
  RevisionLedger,
  EligibilityCriterion,
  ApplicantProfile,
  EligibilityAssessment,
  VerifyEvidenceResponse,
  PersonalImpactReport,
  PersonalizedActionPlan,
  ActionItemStatus,
  NoticeMetadata,
  WorkspaceTimelineReport,
  DemoLibraryResponse,
  NotificationsResponse,
  UserActivity,
  TranslateNoticeRequest,
  TranslateNoticeResponse,
} from '../types/api';

const getBaseUrl = (): string => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL.replace(/\/+$/, '');
  }
  if (typeof window !== 'undefined' && window.location?.origin && window.location.origin !== 'null') {
    return '';
  }
  return 'http://127.0.0.1:8000';
};

const BASE_URL = getBaseUrl();

export class APIError extends Error {
  status: number;
  data: any;
  errorType?: string;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
    this.errorType = data?.error_type;
  }
}

async function apiFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const defaultInit: RequestInit = {
    credentials: 'include',
  };
  return fetch(input, { ...defaultInit, ...init });
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errMessage = `HTTP ${res.status}: ${res.statusText}`;
    let errData = null;
    try {
      errData = await res.json();
      if (errData && errData.detail) {
        errMessage = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
      }
    } catch {
      // not JSON
    }
    throw new APIError(errMessage, res.status, errData);
  }
  return res.json() as Promise<T>;
}

export const apiClient = {
  /**
   * Diagnostic and preflight check for Ollama, Tesseract, and Python
   */
  async getHealth(): Promise<PreflightReport> {
    const res = await apiFetch(`${BASE_URL}/api/health`);
    return handleResponse<PreflightReport>(res);
  },

  /**
   * List all available LLM providers and their configuration status
   */
  async getProviders(): Promise<LLMProviderStatus[]> {
    const res = await apiFetch(`${BASE_URL}/api/providers`);
    return handleResponse<LLMProviderStatus[]>(res);
  },

  /**
   * Select active LLM provider (ollama, openrouter, gemini, huggingface)
   */
  async selectProvider(provider: string): Promise<any> {
    const res = await apiFetch(`${BASE_URL}/api/providers/select`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider }),
    });
    return handleResponse<any>(res);
  },

  /**
   * List available synthetic demo fixtures
   */
  async getSamples(): Promise<SampleFixture[]> {
    const res = await apiFetch(`${BASE_URL}/api/samples`);
    return handleResponse<SampleFixture[]>(res);
  },

  /**
   * Fetch sample fixture content
   */
  async getSampleText(filename: string): Promise<{ filename: string; content: string; fingerprint: string }> {
    const res = await apiFetch(`${BASE_URL}/api/samples/${encodeURIComponent(filename)}`);
    return handleResponse<{ filename: string; content: string; fingerprint: string }>(res);
  },

  /**
   * Fetch sample image fixture as Blob
   */
  async getSampleImage(filename: string): Promise<Blob> {
    const res = await apiFetch(`${BASE_URL}/api/samples/${encodeURIComponent(filename)}`);
    if (!res.ok) {
      throw new APIError(`Failed to fetch image: HTTP ${res.status}`, res.status);
    }
    return res.blob();
  },

  /**
   * Ingest, sanitize and compute SHA-256 fingerprint of pasted text
   */
  async ingestText(text: string): Promise<IngestTextResponse> {
    const res = await apiFetch(`${BASE_URL}/api/ingest/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    return handleResponse<IngestTextResponse>(res);
  },

  /**
   * Ingest uploaded file (txt or image)
   */
  async uploadFile(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiFetch(`${BASE_URL}/api/ingest/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<any>(res);
  },

  /**
   * Execute OCR on an image file
   */
  async runOCR(
    file: File | Blob,
    filename: string = 'notice_image.png',
    targetLang: string = 'eng',
    enhanceContrast: boolean = true,
    engine?: string
  ): Promise<OCRResponse> {
    const formData = new FormData();
    formData.append('file', file, filename);
    formData.append('target_lang', targetLang);
    formData.append('enhance_contrast', String(enhanceContrast));
    if (engine) {
      formData.append('engine', engine);
    }

    const res = await apiFetch(`${BASE_URL}/api/ocr`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<OCRResponse>(res);
  },

  /**
   * Execute structured analysis via configured LLM
   */
  async analyzeNotice(
    noticeText: string,
    targetLanguage: string = 'en',
    readingLevel: string = 'standard',
    sessionId?: string | null,
    provider?: string | null,
    sourceLanguage?: string | null
  ): Promise<AnalyzeResponse> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 180000);
    try {
      const res = await apiFetch(`${BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          notice_text: noticeText,
          target_language: targetLanguage,
          output_language: targetLanguage,
          source_language: sourceLanguage || undefined,
          reading_level: readingLevel,
          session_id: sessionId || undefined,
          provider: provider || undefined,
        }),
      });
      return await handleResponse<AnalyzeResponse>(res);
    } catch (err: any) {
      if (err.name === 'AbortError') {
        throw new APIError(
          'Analysis timed out after 3 minutes. The local Gemma 4 model took longer than expected to process this document. Please verify system resources or retry with a shorter notice.',
          504
        );
      }
      throw err;
    } finally {
      clearTimeout(timeoutId);
    }
  },

  /**
   * Translate extracted notice package on-demand when language changes
   */
  async translateNotice(payload: TranslateNoticeRequest): Promise<TranslateNoticeResponse> {
    const res = await apiFetch(`${BASE_URL}/api/translate-notice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<TranslateNoticeResponse>(res);
  },

  /**
   * Search grounded citations within the active notice text
   */
  async searchEvidence(query: string, noticeText: string, maxResults: number = 5): Promise<EvidenceCitation[]> {
    const res = await apiFetch(`${BASE_URL}/api/evidence/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        notice_text: noticeText,
        max_results: maxResults,
      }),
    });
    return handleResponse<EvidenceCitation[]>(res);
  },

  /**
   * Confirm or correct an uncertain notice fact and refresh dependent summary and checklist
   */
  async confirmFact(
    fieldName: string,
    confirmedValue: string,
    structuredNotice: StructuredNotice,
    readingLevel: string = 'standard',
    sessionId?: string | null
  ): Promise<ConfirmFactResponse> {
    const res = await apiFetch(`${BASE_URL}/api/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        field_name: fieldName,
        confirmed_value: confirmedValue,
        structured_notice: structuredNotice,
        reading_level: readingLevel,
        session_id: sessionId || undefined,
      }),
    });
    return handleResponse<ConfirmFactResponse>(res);
  },

  /**
   * Request plain language summary at a specific reading level (simple, standard, detailed)
   */
  async getReadingLevelSummary(
    structuredNotice: StructuredNotice,
    readingLevel: string = 'standard',
    targetLanguage: string = 'en',
    sessionId?: string
  ): Promise<ReadingLevelResponse> {
    const res = await apiFetch(`${BASE_URL}/api/summary/reading-level`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        structured_notice: structuredNotice,
        reading_level: readingLevel,
        target_language: targetLanguage,
        output_language: targetLanguage,
        session_id: sessionId || undefined,
      }),
    });
    return handleResponse<ReadingLevelResponse>(res);
  },

  /**
   * Ask follow-up question grounded strictly in active notice text
   */
  async askFollowUp(
    question: string,
    noticeText: string,
    sessionId?: string | null,
    targetLanguage: string = 'en'
  ): Promise<FollowUpAnswer> {
    const res = await apiFetch(`${BASE_URL}/api/followup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        notice_text: noticeText,
        session_id: sessionId || undefined,
        target_language: targetLanguage,
        output_language: targetLanguage,
      }),
    });
    return handleResponse<FollowUpAnswer>(res);
  },

  /**
   * Export notice dossier as formatted Markdown
   */
  async exportMarkdown(
    structuredNotice: StructuredNotice,
    summary?: PlainLanguageSummary,
    checklist?: ActionChecklist
  ): Promise<Blob> {
    const res = await apiFetch(`${BASE_URL}/api/export/markdown`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        structured_notice: structuredNotice,
        summary,
        checklist,
      }),
    });
    if (!res.ok) {
      throw new APIError('Failed to generate Markdown export', res.status);
    }
    return res.blob();
  },

  /**
   * Export action checklist as RFC 5545 iCalendar (.ics) file
   */
  async exportIcs(checklist: ActionChecklist, title: string = 'Notice Action Plan'): Promise<Blob> {
    const res = await apiFetch(`${BASE_URL}/api/export/ics`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        checklist,
        title,
      }),
    });
    if (!res.ok) {
      throw new APIError('Failed to generate iCalendar export', res.status);
    }
    return res.blob();
  },

  /**
   * Fetch TTS audio bytes (MP3) or return null if offline
   */
  async getTTSAudio(text: string, lang: string = 'en', allowCloud: boolean = false): Promise<Blob | null> {
    try {
      const res = await apiFetch(`${BASE_URL}/api/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, lang, allow_cloud: allowCloud }),
      });
      if (res.status === 204 || !res.ok) {
        return null;
      }
      return res.blob();
    } catch {
      return null;
    }
  },

  /**
   * Detect administrative relationship (AMENDMENT, EXTENSION, CANCELLATION, etc.) between two notices
   */
  async detectRelationship(
    sourceSessionId?: string,
    targetSessionId?: string,
    sourceText?: string,
    targetText?: string
  ): Promise<NoticeRelationship> {
    const res = await apiFetch(`${BASE_URL}/api/relationships/detect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_session_id: sourceSessionId || undefined,
        target_session_id: targetSessionId || undefined,
        source_text: sourceText || undefined,
        target_text: targetText || undefined,
      }),
    });
    return handleResponse<NoticeRelationship>(res);
  },

  /**
   * Build field-by-field revision ledger comparing two notices
   */
  async compareRevisionLedger(
    sourceSessionId?: string,
    targetSessionId?: string,
    sourceText?: string,
    targetText?: string,
    targetLanguage: string = 'en'
  ): Promise<RevisionLedger> {
    const res = await apiFetch(`${BASE_URL}/api/revision-ledger/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_session_id: sourceSessionId || undefined,
        target_session_id: targetSessionId || undefined,
        source_text: sourceText || undefined,
        target_text: targetText || undefined,
        target_language: targetLanguage,
        output_language: targetLanguage,
      }),
    });
    return handleResponse<RevisionLedger>(res);
  },

  /**
   * Extract machine-evaluable eligibility criteria from notice
   */
  async extractEligibilityCriteria(
    sessionId?: string,
    noticeText?: string,
    targetLanguage: string = 'en'
  ): Promise<EligibilityCriterion[]> {
    const res = await apiFetch(`${BASE_URL}/api/eligibility/extract-criteria`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId || undefined,
        notice_text: noticeText || undefined,
        target_language: targetLanguage,
        output_language: targetLanguage,
      }),
    });
    return handleResponse<EligibilityCriterion[]>(res);
  },

  /**
   * Evaluate applicant profile against notice eligibility criteria
   */
  async evaluateEligibility(
    profile: ApplicantProfile,
    sessionId?: string,
    noticeText?: string,
    targetLanguage: string = 'en'
  ): Promise<EligibilityAssessment> {
    const res = await apiFetch(`${BASE_URL}/api/eligibility/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId || undefined,
        notice_text: noticeText || undefined,
        applicant_profile: profile,
        target_language: targetLanguage,
        output_language: targetLanguage,
      }),
    });
    return handleResponse<EligibilityAssessment>(res);
  },

  /**
   * Verify an evidence quote against source notice text
   */
  async verifyEvidence(
    noticeText: string,
    excerpt: string,
    claimText?: string,
    docTitle?: string
  ): Promise<VerifyEvidenceResponse> {
    const res = await apiFetch(`${BASE_URL}/api/trust/verify-evidence`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        notice_text: noticeText,
        excerpt,
        claim_text: claimText,
        source_doc_title: docTitle,
      }),
    });
    return handleResponse<VerifyEvidenceResponse>(res);
  },

  /**
   * Evaluate personal impact of notice revisions on an applicant profile
   */
  async evaluatePersonalImpact(params: {
    revisionLedger?: RevisionLedger;
    sourceText?: string;
    targetText?: string;
    profile?: ApplicantProfile;
  }): Promise<PersonalImpactReport> {
    const res = await apiFetch(`${BASE_URL}/api/impact/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        revision_ledger: params.revisionLedger,
        source_text: params.sourceText,
        target_text: params.targetText,
        applicant_profile: params.profile,
      }),
    });
    return handleResponse<PersonalImpactReport>(res);
  },

  /**
   * Generate personalized, dependency-aware action roadmap
   */
  async generateActionPlan(params: {
    sessionId?: string;
    noticeText?: string;
    profile?: ApplicantProfile;
    eligibility?: EligibilityAssessment;
    revisionLedger?: RevisionLedger;
    targetLanguage?: string;
  }): Promise<PersonalizedActionPlan> {
    const res = await apiFetch(`${BASE_URL}/api/actions/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: params.sessionId,
        notice_text: params.noticeText,
        applicant_profile: params.profile,
        eligibility_assessment: params.eligibility,
        revision_ledger: params.revisionLedger,
        target_language: params.targetLanguage || 'en',
        output_language: params.targetLanguage || 'en',
      }),
    });
    return handleResponse<PersonalizedActionPlan>(res);
  },

  /**
   * Update status or notes for an action item
   */
  async updateActionStatus(
    plan: PersonalizedActionPlan,
    actionId: string,
    status: ActionItemStatus,
    userNotes?: string
  ): Promise<PersonalizedActionPlan> {
    const res = await apiFetch(`${BASE_URL}/api/actions/update-status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        plan,
        action_id: actionId,
        status,
        user_notes: userNotes,
      }),
    });
    return handleResponse<PersonalizedActionPlan>(res);
  },

  /**
   * Multi-document workspace API
   */
  async getWorkspaceNotices(): Promise<NoticeMetadata[]> {
    const res = await apiFetch(`${BASE_URL}/api/workspace/notices`);
    return handleResponse<NoticeMetadata[]>(res);
  },

  async addWorkspaceNotice(text: string, title?: string, docId?: string): Promise<NoticeMetadata> {
    const res = await apiFetch(`${BASE_URL}/api/workspace/notices`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, title, doc_id: docId }),
    });
    return handleResponse<NoticeMetadata>(res);
  },

  async getWorkspaceTimeline(activeId?: string): Promise<WorkspaceTimelineReport> {
    const url = activeId
      ? `${BASE_URL}/api/workspace/timeline?active_id=${encodeURIComponent(activeId)}`
      : `${BASE_URL}/api/workspace/timeline`;
    const res = await apiFetch(url);
    return handleResponse<WorkspaceTimelineReport>(res);
  },

  async clearWorkspace(): Promise<void> {
    await apiFetch(`${BASE_URL}/api/workspace/clear`, { method: 'POST' });
  },

  /**
   * Demo Library APIs
   */
  async getDemoLibrary(language?: string, format?: string, category?: string): Promise<DemoLibraryResponse> {
    const params = new URLSearchParams();
    if (language) params.append('language', language);
    if (format) params.append('format', format);
    if (category) params.append('category', category);
    const query = params.toString() ? `?${params.toString()}` : '';
    const res = await apiFetch(`${BASE_URL}/api/demo-library${query}`);
    return handleResponse<DemoLibraryResponse>(res);
  },

  async loadDemoLibraryItem(id: string): Promise<{
    id: string;
    demo_id: string;
    title: string;
    language: string;
    source_language: string;
    format: string;
    category?: string;
    text: string;
    raw_text: string;
    file_path?: string;
    document_id?: string;
    fingerprint?: string;
    char_count: number;
    word_count: number;
    line_count?: number;
    ground_truth?: any;
    expected_key_actions?: any;
  }> {
    const res = await apiFetch(`${BASE_URL}/api/demo-library/${encodeURIComponent(id)}/load`, {
      method: 'POST',
    });
    const data = await handleResponse<any>(res);
    const resolvedText = data.raw_text || data.text || '';
    const resolvedLang = data.source_language || data.language || data.detected_language || 'en';
    const resolvedId = data.demo_id || data.id || id;
    const computedCharCount = typeof data.char_count === 'number' ? data.char_count : resolvedText.length;
    const computedWordCount =
      typeof data.word_count === 'number'
        ? data.word_count
        : (resolvedText.trim() ? resolvedText.trim().split(/\s+/).length : 0);

    return {
      ...data,
      id: resolvedId,
      demo_id: resolvedId,
      title: data.title || '',
      language: resolvedLang,
      source_language: resolvedLang,
      format: data.format || '',
      text: resolvedText,
      raw_text: resolvedText,
      char_count: computedCharCount,
      word_count: computedWordCount,
      document_id: data.document_id,
      fingerprint: data.fingerprint,
      line_count: data.line_count,
    };
  },

  /**
   * Language detection API
   */
  async detectLanguage(text: string): Promise<{
    detected_language: string;
    confidence: number;
    is_mixed: boolean;
    secondary_languages: string[];
    script: string;
    details: Record<string, any>;
  }> {
    const res = await apiFetch(`${BASE_URL}/api/language/detect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    return handleResponse<any>(res);
  },

  /**
   * Persistently toggle a checklist item in SQLite database
   */
  async toggleChecklistItemPersistent(itemId: string, isCompleted: boolean): Promise<{ success: boolean; item_id: string; is_completed: boolean }> {
    const res = await apiFetch(`${BASE_URL}/api/checklist/${encodeURIComponent(itemId)}/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completed: isCompleted, is_completed: isCompleted }),
    });
    return handleResponse<any>(res);
  },

  /**
   * Fetch all persistently stored documents
   */
  async getPersistedDocuments(): Promise<{ documents: any[]; total: number }> {
    const res = await apiFetch(`${BASE_URL}/api/documents`);
    return handleResponse<any>(res);
  },

  /**
   * List saved notices for current user
   */
  async getSavedNotices(q?: string): Promise<any[]> {
    const url = q ? `${BASE_URL}/api/user/saved-notices?q=${encodeURIComponent(q)}` : `${BASE_URL}/api/user/saved-notices`;
    const res = await apiFetch(url, { credentials: 'include' });
    return handleResponse<any[]>(res);
  },

  /**
   * Save notice for current user
   */
  async saveUserNotice(documentId: string, metadata: { title: string; authority?: string; deadline?: string; raw_text?: string; assignment_title?: string }): Promise<any> {
    const res = await apiFetch(`${BASE_URL}/api/user/saved-notices/${encodeURIComponent(documentId)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(metadata),
    });
    return handleResponse<any>(res);
  },

  /**
   * Unsave notice for current user
   */
  async unsaveUserNotice(documentId: string): Promise<any> {
    const res = await apiFetch(`${BASE_URL}/api/user/saved-notices/${encodeURIComponent(documentId)}`, {
      method: 'DELETE',
      credentials: 'include',
    });
    return handleResponse<any>(res);
  },

  /**
   * Get 7-day weekly task action plan
   */
  async getWeeklyTasks(refDate?: string): Promise<any> {
    const url = refDate ? `${BASE_URL}/api/user/weekly-tasks?ref_date=${encodeURIComponent(refDate)}` : `${BASE_URL}/api/user/weekly-tasks`;
    const res = await apiFetch(url, { credentials: 'include' });
    return handleResponse<any>(res);
  },

  /**
   * Query weekly tasks with natural language query
   */
  async queryWeeklyTasks(query: string): Promise<any> {
    const res = await apiFetch(`${BASE_URL}/api/user/weekly-tasks/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ query }),
    });
    return handleResponse<any>(res);
  },

  /**
   * User Notifications API
   */
  async getUserNotifications(): Promise<NotificationsResponse> {
    const res = await apiFetch(`${BASE_URL}/api/user/notifications`, { credentials: 'include' });
    return handleResponse<NotificationsResponse>(res);
  },

  async markNotificationRead(notificationId: string): Promise<{ status: string; updated: boolean }> {
    const res = await apiFetch(`${BASE_URL}/api/user/notifications/${encodeURIComponent(notificationId)}/read`, {
      method: 'PUT',
      credentials: 'include',
    });
    return handleResponse<any>(res);
  },

  async markAllNotificationsRead(): Promise<{ status: string; marked_read: number }> {
    const res = await apiFetch(`${BASE_URL}/api/user/notifications/mark-all-read`, {
      method: 'POST',
      credentials: 'include',
    });
    return handleResponse<any>(res);
  },

  async dismissNotification(notificationId: string): Promise<{ status: string; dismissed: boolean }> {
    const res = await apiFetch(`${BASE_URL}/api/user/notifications/${encodeURIComponent(notificationId)}`, {
      method: 'DELETE',
      credentials: 'include',
    });
    return handleResponse<any>(res);
  },

  /**
   * User Activity Audit Trail API
   */
  async getUserActivities(limit: number = 20): Promise<UserActivity[]> {
    const res = await apiFetch(`${BASE_URL}/api/user/activities?limit=${limit}`, { credentials: 'include' });
    return handleResponse<UserActivity[]>(res);
  },

  /**
   * User Preferences API (Language, Accessibility, Theme)
   */
  async getUserPreferences(): Promise<Record<string, any>> {
    try {
      const res = await apiFetch(`${BASE_URL}/api/user/preferences`, { credentials: 'include' });
      if (!res.ok) return {};
      const data = await handleResponse<{ status: string; preferences: Record<string, any> }>(res);
      return data.preferences || {};
    } catch {
      return {};
    }
  },

  async saveUserPreferences(preferences: Record<string, any>): Promise<any> {
    try {
      const res = await apiFetch(`${BASE_URL}/api/user/preferences`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ preferences }),
      });
      return handleResponse<any>(res);
    } catch {
      return null;
    }
  },

  /**
   * User Checklist Progress API (Isolated per Authenticated Citizen)
   */
  async getUserChecklistProgress(): Promise<Record<string, boolean>> {
    try {
      const res = await apiFetch(`${BASE_URL}/api/user/checklist-progress`, { credentials: 'include' });
      if (!res.ok) return {};
      const data = await handleResponse<{ status: string; progress: Record<string, boolean> }>(res);
      return data.progress || {};
    } catch {
      return {};
    }
  },

  async toggleUserChecklistProgress(itemId: string, completed: boolean): Promise<any> {
    const res = await apiFetch(`${BASE_URL}/api/user/checklist/${encodeURIComponent(itemId)}/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ completed, is_completed: completed }),
    });
    return handleResponse<any>(res);
  },
};
