import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Global fetch mock for deterministic unit testing in jsdom
globalThis.fetch = vi.fn((url: string | URL | Request) => {
  const urlStr = typeof url === 'string' ? url : url.toString();

  if (urlStr.includes('/api/health')) {
    return Promise.resolve({
      ok: true,
      status: 200,
      json: async () => ({
        overall_status: 'ok',
        model_name: 'gemma4:latest',
        is_ready_for_inference: true,
        items: [
          { name: 'Python Runtime', status: 'ok', details: 'Python 3.11.15' },
          { name: 'Tesseract OCR', status: 'ok', details: 'v5.4.0' },
          { name: 'Ollama Server', status: 'ok', details: 'Connected' },
        ],
      }),
    } as Response);
  }

  if (urlStr.includes('/api/samples')) {
    return Promise.resolve({
      ok: true,
      status: 200,
      json: async () => [
        {
          id: 'synthetic_scholarship_notice.txt',
          title: '🎯 Competition Demo (TEST-SCH-2026-001)',
          type: 'text',
          language: 'en',
        },
      ],
    } as Response);
  }

  return Promise.resolve({
    ok: true,
    status: 200,
    json: async () => ({}),
    blob: async () => new Blob(['mock data']),
    text: async () => 'mock response text',
  } as Response);
}) as any;

// Mock Web Speech API for Vitest jsdom
if (typeof window !== 'undefined') {
  (window as any).speechSynthesis = {
    speak: vi.fn((utterance: any) => {
      if (utterance && utterance.onstart) {
        utterance.onstart();
      }
    }),
    cancel: vi.fn(),
    pause: vi.fn(),
    resume: vi.fn(),
    paused: false,
    speaking: false,
    pending: false,
    getVoices: () => [],
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  };

  (globalThis as any).SpeechSynthesisUtterance = class {
    text: string;
    lang: string = '';
    rate: number = 1;
    onstart: any = null;
    onend: any = null;
    onerror: any = null;
    constructor(text: string) {
      this.text = text;
    }
  };
}
