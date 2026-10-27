/**
 * SuchnaSetu AI — Typed Domain Schemas & API Types
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
  ollama_connected?: boolean;
  tesseract_available?: boolean;
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
  status?: string;
}

export interface EvidenceCitation {
  line_number: number;
  quote: string;
  relevance_score: number;
}

export interface SampleFixture {
  id: string;
  filename?: string;
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
  document_id?: string | null;
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
  raw_ocr_text?: string | null;
  document_quality_score?: number | null;
  deskew_angle?: number | null;
  orientation_applied?: number | null;
  uncertain_spans?: Array<{ text: string; confidence: number; box: number[] }> | null;
  critical_fields?: Record<string, { value: string; confidence: number; status: string; source: string }> | null;
  field_accuracy_score?: number | null;
}

export interface AnalyzeResponse {
  session_id?: string;
  document_id?: string;
  source_language?: string;
  detected_language?: string;
  language_confidence?: number;
  is_mixed_language?: boolean;
  structured_notice: StructuredNotice;
  six_core_fields?: SixCoreFields;
  summary_en: PlainLanguageSummary;
  summary_hi: PlainLanguageSummary;
  checklist_en: ActionChecklist;
  checklist_hi: ActionChecklist;
  target_language?: string;
  localized_summary?: PlainLanguageSummary;
  localized_checklist?: ActionChecklist;
  fingerprint: string;
  duration_seconds: number;
}

export interface TranslateNoticeRequest {
  session_id?: string;
  fingerprint?: string;
  target_language: string;
  reading_level?: 'simple' | 'standard' | 'detailed';
  structured_notice?: StructuredNotice;
  summary_en?: PlainLanguageSummary;
  checklist_en?: ActionChecklist;
}

export interface TranslateNoticeResponse {
  target_language: string;
  target_language_name: string;
  summary: PlainLanguageSummary;
  checklist: ActionChecklist;
  structured_notice?: StructuredNotice | null;
  six_core_fields?: SixCoreFields | null;
  cached: boolean;
  status: string;
}

export interface DemoLibraryItem {
  id: string;
  title: string;
  language: string;
  format: string;
  category: string;
  description: string;
  file_path: string;
  word_count: number;
}

export interface DemoLibraryResponse {
  demos: DemoLibraryItem[];
  total: number;
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
  target_language?: string;
  localized_summary?: PlainLanguageSummary | null;
}


// =========================================================
// Multi-Notice Revision Ledger Types
// =========================================================

export type RelationshipType =
  | 'AMENDMENT'
  | 'EXTENSION'
  | 'CANCELLATION'
  | 'REPLACEMENT'
  | 'RELATED'
  | 'UNRESOLVED';

export type ChangeCategory =
  | 'ADDED'
  | 'REMOVED'
  | 'MODIFIED'
  | 'UNCHANGED'
  | 'UNCERTAIN';

export interface NoticeRelationship {
  source_notice_id: string;
  target_notice_id: string;
  relationship_type: RelationshipType;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  is_explicit: boolean;
  evidence_quote: string;
  source_reference?: string | null;
  explanation: string;
}

export interface RevisionEntry {
  field_name: string;
  display_name: string;
  old_value: string;
  new_value: string;
  change_category: ChangeCategory;
  old_evidence_quote?: string | null;
  new_evidence_quote?: string | null;
  old_page?: number | null;
  new_page?: number | null;
  requires_review: boolean;
  explanation: string;
}

export interface RevisionLedger {
  source_notice_id: string;
  target_notice_id: string;
  source_title: string;
  target_title: string;
  relationship: NoticeRelationship;
  entries: RevisionEntry[];
  summary_of_changes: string;
  created_at: string;
}

// =========================================================
// Explainable Applicant Eligibility Engine Types
// =========================================================

export type CriterionType =
  | 'AGE'
  | 'QUALIFICATION'
  | 'PERCENTAGE'
  | 'CATEGORY'
  | 'DOCUMENT'
  | 'OTHER';

export type EvaluationStatus = 'PASS' | 'FAIL' | 'UNKNOWN';

export interface EligibilityCriterion {
  id: string;
  criterion_type: CriterionType;
  description: string;
  operator: string;
  threshold_value: string;
  cutoff_date?: string | null;
  category_relaxations?: Record<string, string>;
  evidence_quote: string;
  page_number?: number | null;
}

export interface ApplicantProfile {
  date_of_birth?: string | null;
  age_years?: number | null;
  degree?: string | null;
  course?: string | null;
  academic_year?: string | null;
  department?: string | null;
  income_annual?: number | null;
  enrollment_status?: string | null;
  marks_percentage?: number | null;
  category?: string | null;
  documents_available?: string[];
  notes?: string | null;
}

export interface CriterionEvaluationResult {
  criterion_id: string;
  criterion_type: CriterionType;
  description: string;
  status: EvaluationStatus;
  applicant_value: string;
  requirement_value: string;
  evidence_quote: string;
  page_number?: number | null;
  explanation: string;
  missing_info?: string | null;
}

export interface EligibilityAssessment {
  session_id?: string | null;
  overall_status: 'ELIGIBLE' | 'NOT_ELIGIBLE' | 'INCONCLUSIVE';
  results: CriterionEvaluationResult[];
  summary: string;
  disclaimer: string;
}

// =========================================================
// Evidence-First Trust Engine Types
// =========================================================

export type EvidenceVerificationStatus =
  | 'VERIFIED_IN_SOURCE'
  | 'UNVERIFIED'
  | 'UNCERTAIN_OCR'
  | 'DERIVED_DETERMINISTIC'
  | 'AI_INTERPRETATION'
  | 'HUMAN_CONFIRMED';

export interface TrustEvidence {
  evidence_id: string;
  claim_id?: string | null;
  claim_text: string;
  source_doc_id?: string | null;
  source_doc_title?: string | null;
  page_number?: number | null;
  line_start?: number | null;
  line_end?: number | null;
  verbatim_excerpt: string;
  normalized_value?: string | null;
  verification_status: EvidenceVerificationStatus;
  confidence_rationale: string;
  is_inert_safe: boolean;
}

export interface VerifyEvidenceResponse {
  is_valid: boolean;
  evidence: TrustEvidence;
  suggested_match?: string | null;
}

// =========================================================
// Personal Impact Change Tracker Types
// =========================================================

export type ImpactType =
  | 'BENEFICIAL'
  | 'ADVERSE'
  | 'NEUTRAL'
  | 'ACTION_REQUIRED'
  | 'UNRESOLVED';

export interface PersonalImpactItem {
  id: string;
  field_name: string;
  change_category: ChangeCategory;
  previous_value: string;
  new_value: string;
  previous_status?: string | null;
  new_status?: string | null;
  impact_type: ImpactType;
  headline: string;
  explanation: string;
  evidence_old?: string | null;
  evidence_new?: string | null;
  required_user_action?: string | null;
}

export interface PersonalImpactReport {
  overall_impact_summary: string;
  impact_level: 'HIGH' | 'MODERATE' | 'LOW' | 'NEUTRAL';
  impact_items: PersonalImpactItem[];
  recalculated_eligibility?: EligibilityAssessment | null;
  recommended_next_actions: string[];
  disclaimer: string;
}

// =========================================================
// Personalized Action Navigator Types
// =========================================================

export type ActionCategory =
  | 'ELIGIBILITY_CHECK'
  | 'DOCUMENT_PREPARATION'
  | 'FEE_PAYMENT'
  | 'APPLICATION_SUBMISSION'
  | 'HEARING_APPEARANCE'
  | 'POST_SUBMISSION'
  | 'CORRIGENDUM_REVIEW';

export type ActionItemStatus =
  | 'PENDING'
  | 'COMPLETED'
  | 'BLOCKED'
  | 'NEEDS_VERIFICATION';

export interface ActionItem {
  id: string;
  title: string;
  explanation: string;
  category: ActionCategory;
  status: ActionItemStatus;
  deadline?: string | null;
  deadline_evidence?: string | null;
  deadline_status?: string | null;
  remaining_time?: string | null;
  superseded_deadline?: string | null;
  fee_amount?: string | null;
  dependencies: string[];
  blocked_by: string[];
  official_portal_url?: string | null;
  url_verified: boolean;
  evidence?: TrustEvidence | null;
  is_user_custom: boolean;
  completed_at?: string | null;
  user_notes?: string | null;
}

export interface PersonalizedActionPlan {
  plan_id: string;
  session_id?: string | null;
  notice_title: string;
  overall_progress_percentage: number;
  completed_count: number;
  total_count: number;
  items: ActionItem[];
  next_recommended_action_id?: string | null;
  last_updated: string;
}

// =========================================================
// Cross-Notice Intelligence & Workspace Types
// =========================================================

export type RelationshipConfidence =
  | 'VERIFIED'
  | 'STRONG_CANDIDATE'
  | 'POSSIBLE'
  | 'CONFLICTING'
  | 'UNKNOWN';

export interface NoticeMetadata {
  id: string;
  title: string;
  reference_number?: string | null;
  issuing_authority?: string | null;
  notice_date?: string | null;
  ingested_at: string;
  char_count: number;
  raw_text: string;
  fingerprint: string;
  document_type: string;
}

export interface CrossNoticeRelationship {
  id: string;
  source_notice_id: string;
  target_notice_id: string;
  relationship_type: RelationshipType;
  confidence_level: RelationshipConfidence;
  evidence_quote: string;
  rationale: string;
  precedence_status: string;
  user_confirmed: boolean;
}

export interface TimelineEvent {
  id: string;
  date: string;
  notice_id: string;
  notice_title: string;
  event_type: string;
  summary: string;
  evidence_quote: string;
  is_active: boolean;
}

export interface CrossNoticeConflict {
  id: string;
  notice_a_id: string;
  notice_b_id: string;
  field_name: string;
  value_a: string;
  value_b: string;
  evidence_a: string;
  evidence_b: string;
  conflict_severity: 'CRITICAL' | 'MODERATE' | 'INFORMATIONAL';
  resolution_guidance: string;
  status: string;
}

export interface WorkspaceTimelineReport {
  workspace_id: string;
  notices: NoticeMetadata[];
  relationships: CrossNoticeRelationship[];
  timeline: TimelineEvent[];
  conflicts: CrossNoticeConflict[];
  active_notice_id?: string | null;
}

export interface AccessibilityPreferences {
  textSize: 'normal' | 'large' | 'extra-large';
  lineSpacing: 'normal' | 'relaxed' | 'loose';
  highContrast: boolean;
  warmBackground: boolean;
  highlightKeyInfo: boolean;
  reducedMotion: boolean;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  username?: string;
  is_verified: boolean;
  created_at: string;
}

export interface GuestStatus {
  is_guest: boolean;
  ip: string;
  remaining_analyses: number;
  limit_window_minutes: number;
}

export type AuthPageView = 'login' | 'signup' | 'verify-email' | 'forgot-password' | 'reset-password' | 'verify_email' | 'forgot_password' | 'reset_password';

export interface UserNotification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  type: 'deadline' | 'action' | 'system' | 'warning' | 'info';
  document_id?: string | null;
  is_read: boolean;
  is_dismissed: boolean;
  created_at: number;
}

export interface NotificationsResponse {
  notifications: UserNotification[];
  unread_count: number;
  total: number;
}

export interface UserActivity {
  id: string;
  user_id: string;
  activity_type: string;
  title: string;
  description: string;
  document_id?: string | null;
  created_at: number;
}
