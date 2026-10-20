/**
 * Notice2Action AI — Typed Domain Schemas & API Types
 * Mirroring backend Pydantic models from notice2action.schemas
 */

export type CertaintyStatus =
  | 'stated'
  | 'not_stated'
  | 'uncertain'
  | 'conflicting'
  | 'unreadable';

export interface ExtractedFact {
  field_name: string;
  value: string;
  status: CertaintyStatus;
  evidence_quote?: string | null;
  source_location?: string | null;
  requires_confirmation: boolean;
  user_confirmed: boolean;
  confirmed_value?: string | null;
  explanation?: string | null;
  uncertainty_type?: 'ocr_quality' | 'document_ambiguity' | 'missing_in_text' | 'conflict' | string | null;
}

export interface SixCoreFields {
  issuing_authority: ExtractedFact;
  notice_reference_number: ExtractedFact;
  notice_date: ExtractedFact;
  recipient: ExtractedFact;
  main_subject: ExtractedFact;
  required_action_and_deadline: ExtractedFact;
}

export interface StructuredNotice {
  issuing_authority?: ExtractedFact;
  notice_reference_number?: ExtractedFact;
  notice_date?: ExtractedFact;
  recipient?: ExtractedFact;
  main_subject?: ExtractedFact;
  required_action_and_deadline?: ExtractedFact;
  purpose: ExtractedFact;
  eligibility: ExtractedFact;
  deadline: ExtractedFact;
  fee_or_cost: ExtractedFact;
  required_documents: ExtractedFact;
  contact_details: ExtractedFact;
  required_actions: ExtractedFact;
  important_conditions: ExtractedFact;
  missing_information: string[];
  uncertain_or_conflicting_details: string[];
  raw_notice_text: string;
}

export interface PlainLanguageSummary {
  about: string;
  eligible: string;
  actions: string;
  documents: string;
  deadline: string;
  help_contact: string;
  missing: string;
}

export interface ChecklistItem {
  step_number: number;
  action: string;
  category: 'eligibility' | 'documents' | 'application' | 'submission' | 'clarification' | string;
  is_mandatory: boolean;
  requires_confirmation: boolean;
  is_completed: boolean;
  grounded_quote?: string | null;
  notes?: string | null;
}

export interface ActionChecklist {
  items: ChecklistItem[];
}

export interface FollowUpAnswer {
  question: string;
  answer: string;
  is_supported: boolean;
  evidence_quote?: string | null;
  unsupported_message?: string | null;
}

export interface DiagnosticItem {
  name: string;
  status: 'ok' | 'warning' | 'error';
  details: string;
  remedy?: string | null;
}

export interface PreflightReport {
  overall_status: 'ok' | 'warning' | 'error';
  active_provider?: string;
  model_name: string;
  is_ready_for_inference: boolean;
  items: DiagnosticItem[];
}

export interface LLMProviderStatus {
  id: string;
  name: string;
  is_active: boolean;
  is_local: boolean;
  requires_api_key: boolean;
  model: string;
  endpoint?: string;
  key_configured: boolean;
}

export interface EvidenceCitation {
  line_number: number;
  quote: string;
  relevance_score: number;
}

export interface SampleFixture {
  id: string;
  title: string;
  type: 'text' | 'image';
  language: 'en' | 'hi';
}

export interface IngestTextResponse {
  raw_text: string;
  char_count: number;
  line_count: number;
  security_warning?: string | null;
  fingerprint: string;
}

export interface OCRResponse {
  extracted_text: string;
  confidence_score: number;
  languages_used: string;
  line_count: number;
  char_count: number;
  is_preprocessed: boolean;
  engine_used?: string;
  is_uncertain?: boolean;
  uncertainty_reason?: string | null;
  warning?: string | null;
  error?: string | null;
  fingerprint: string;
}

export interface AnalyzeResponse {
  session_id?: string;
  structured_notice: StructuredNotice;
  six_core_fields?: SixCoreFields;
  summary_en: PlainLanguageSummary;
  summary_hi: PlainLanguageSummary;
  checklist_en: ActionChecklist;
  checklist_hi: ActionChecklist;
  fingerprint: string;
  duration_seconds: number;
}

export interface ConfirmFactResponse {
  structured_notice: StructuredNotice;
  six_core_fields?: SixCoreFields;
  summary_en: PlainLanguageSummary;
  summary_hi: PlainLanguageSummary;
  checklist_en: ActionChecklist;
  checklist_hi: ActionChecklist;
}

export interface ReadingLevelResponse {
  summary_en: PlainLanguageSummary;
  summary_hi: PlainLanguageSummary;
  reading_level: string;
}
