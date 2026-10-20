/**
 * Notice2Action AI — Typed API Client
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
} from '../types/api';

const getBaseUrl = (): string => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  if (typeof window !== 'undefined' && window.location?.origin && window.location.origin !== 'null') {
    return '';
  }
  return 'http://127.0.0.1:8000';
};

const BASE_URL = getBaseUrl();

class APIError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
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
    const res = await fetch(`${BASE_URL}/api/health`);
    return handleResponse<PreflightReport>(res);
  },

  /**
   * List available synthetic demo fixtures
   */
  async getSamples(): Promise<SampleFixture[]> {
    const res = await fetch(`${BASE_URL}/api/samples`);
    return handleResponse<SampleFixture[]>(res);
  },

  /**
   * Fetch sample fixture content
   */
  async getSampleText(filename: string): Promise<{ filename: string; content: string; fingerprint: string }> {
    const res = await fetch(`${BASE_URL}/api/samples/${encodeURIComponent(filename)}`);
    return handleResponse<{ filename: string; content: string; fingerprint: string }>(res);
  },

  /**
   * Fetch sample image fixture as Blob
   */
  async getSampleImage(filename: string): Promise<Blob> {
    const res = await fetch(`${BASE_URL}/api/samples/${encodeURIComponent(filename)}`);
    if (!res.ok) {
      throw new APIError(`Failed to fetch image: HTTP ${res.status}`, res.status);
    }
    return res.blob();
  },

  /**
   * Ingest, sanitize and compute SHA-256 fingerprint of pasted text
   */
  async ingestText(text: string): Promise<IngestTextResponse> {
    const res = await fetch(`${BASE_URL}/api/ingest/text`, {
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
    const res = await fetch(`${BASE_URL}/api/ingest/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<any>(res);
  },

  /**
   * Execute Tesseract OCR on an image file
   */
  async runOCR(
    file: File | Blob,
    filename: string = 'notice_image.png',
    targetLang: string = 'eng',
    enhanceContrast: boolean = true
  ): Promise<OCRResponse> {
    const formData = new FormData();
    formData.append('file', file, filename);
    formData.append('target_lang', targetLang);
    formData.append('enhance_contrast', String(enhanceContrast));

    const res = await fetch(`${BASE_URL}/api/ocr`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<OCRResponse>(res);
  },

  /**
   * Execute full 5-phase structured analysis via local Gemma 4
   */
  async analyzeNotice(noticeText: string, targetLanguage: string = 'en'): Promise<AnalyzeResponse> {
    const res = await fetch(`${BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        notice_text: noticeText,
        target_language: targetLanguage,
      }),
    });
    return handleResponse<AnalyzeResponse>(res);
  },

  /**
   * Ask follow-up question grounded strictly in active notice text
   */
  async askFollowUp(question: string, noticeText: string): Promise<FollowUpAnswer> {
    const res = await fetch(`${BASE_URL}/api/followup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        notice_text: noticeText,
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
    const res = await fetch(`${BASE_URL}/api/export/markdown`, {
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
    const res = await fetch(`${BASE_URL}/api/export/ics`, {
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
  async getTTSAudio(text: string, lang: string = 'en'): Promise<Blob | null> {
    try {
      const res = await fetch(`${BASE_URL}/api/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, lang }),
      });
      if (res.status === 204 || !res.ok) {
        return null;
      }
      return res.blob();
    } catch {
      return null;
    }
  },
};
