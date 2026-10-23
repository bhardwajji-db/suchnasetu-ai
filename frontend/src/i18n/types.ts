export type LanguageCode =
  | 'en'
  | 'hi'
  | 'bn'
  | 'ta'
  | 'te'
  | 'mr'
  | 'gu'
  | 'pa'
  | 'kn'
  | 'ur';

export type TextDirection = 'ltr' | 'rtl';

export interface LanguageMeta {
  code: LanguageCode;
  name: string;
  nativeName: string;
  dir: TextDirection;
  script: string;
}

export interface TranslationDictionary {
  // App brand & Global
  appTitle: string;
  appSubtitle: string;
  loading: string;
  save: string;
  cancel: string;
  close: string;
  confirm: string;
  clear: string;
  copy: string;
  copied: string;
  download: string;
  search: string;
  filter: string;
  status: string;
  actions: string;
  back: string;
  next: string;
  error: string;
  success: string;
  warning: string;
  info: string;
  offline: string;
  active: string;
  notStated: string;
  needsConfirmation: string;
  stated: string;
  uncertain: string;
  conflicting: string;
  unreadable: string;

  // Header
  providerLabel: string;
  languageLabel: string;
  viewOriginalNotice: string;
  offlineBadge: string;
  healthReady: string;
  healthError: string;

  // Sidebar & Navigation
  navDashboard: string;
  navIngestion: string;
  navFacts: string;
  navSummary: string;
  navRevision: string;
  navEligibility: string;
  navQA: string;
  navActionNavigator: string;
  navTimeline: string;
  navHistory: string;
  navSettings: string;
  navDemoLibrary?: string;
  sidebarTitle: string;
  sampleNotices: string;
  loadSample: string;

  // Ingestion & OCR
  ingestionTitle: string;
  ingestionSubtitle: string;
  dropzoneTitle: string;
  dropzoneSubtitle: string;
  dropzoneBrowse: string;
  bufferTitle: string;
  bufferPlaceholder: string;
  clearBuffer: string;
  runOCR: string;
  ocrConfidence: string;
  enhanceContrast: string;
  analyzeNotice: string;
  analyzingNotice: string;
  charsCount: string;
  linesCount: string;
  competitionDemo: string;
  staleWarningTitle: string;
  staleWarningDesc: string;

  // Grounded Facts
  factsTitle: string;
  factsSubtitle: string;
  issuingAuthority: string;
  noticeReference: string;
  noticeDate: string;
  recipient: string;
  mainSubject: string;
  requiredActionDeadline: string;
  deadline: string;
  fee: string;
  eligibility: string;
  requiredDocuments: string;
  contactDetails: string;
  missingInfoTitle: string;
  evidenceQuote: string;
  sourceLocation: string;
  confirmFact: string;

  // Summary & Actions
  summaryTitle: string;
  summarySubtitle: string;
  readingLevel: string;
  simpleLevel: string;
  standardLevel: string;
  detailedLevel: string;
  checklistTitle: string;
  checklistSubtitle: string;
  downloadMarkdown: string;
  addToCalendar: string;
  progressCompleted: string;
  step: string;
  mandatory: string;
  advisory: string;

  // Revision Ledger
  revisionTitle: string;
  revisionSubtitle: string;
  sourceNotice: string;
  targetNotice: string;
  compareNotices: string;
  changeCategory: string;
  added: string;
  modified: string;
  superseded: string;
  removed: string;
  criticalImpact: string;

  // Eligibility Engine
  eligibilityTitle: string;
  eligibilitySubtitle: string;
  applicantProfile: string;
  candidateCategory: string;
  candidateAge: string;
  candidateDegree: string;
  candidatePercentage: string;
  evaluateEligibility: string;
  eligible: string;
  notEligible: string;
  inconclusive: string;
  relaxationsApplied: string;

  // Follow-up Q&A
  qaTitle: string;
  qaSubtitle: string;
  askPlaceholder: string;
  askButton: string;
  suggestedQuestions: string;
  qDeadline: string;
  qFee: string;
  qDocuments: string;
  qEligibility: string;
  qExemptions: string;
  qContact: string;
  supportingQuote: string;
  unsupportedWarning: string;

  // Action Navigator
  navActionTitle: string;
  navActionSubtitle: string;

  // Timeline & History
  timelineTitle: string;
  timelineSubtitle: string;
  historyTitle: string;
  historySubtitle: string;
  clearHistory: string;
  noHistory: string;

  // Settings
  settingsTitle: string;
  highContrast: string;
  textSize: string;
  reducedMotion: string;
  lineSpacing: string;
  voiceGuidance: string;
  purgeAllData: string;

  // Modals & Drawers
  originalNoticeModalTitle: string;
  confirmFactModalTitle: string;
  evidenceInspectorTitle: string;
  voiceGuidanceActive: string;
  stopSpeech: string;
}
