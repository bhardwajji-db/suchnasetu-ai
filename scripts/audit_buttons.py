import os, re

files = [
    'frontend/src/views/DashboardView.tsx',
    'frontend/src/views/IngestionView.tsx',
    'frontend/src/views/GroundedFactsView.tsx',
    'frontend/src/views/SummaryActionsView.tsx',
    'frontend/src/views/RevisionLedgerView.tsx',
    'frontend/src/views/EligibilityEngineView.tsx',
    'frontend/src/views/FollowUpQAView.tsx',
    'frontend/src/views/PersonalizedActionNavigatorView.tsx',
    'frontend/src/views/CrossNoticeTimelineView.tsx',
    'frontend/src/views/NoticeHistoryView.tsx',
    'frontend/src/views/SettingsView.tsx',
    'frontend/src/components/Header.tsx',
    'frontend/src/components/Sidebar.tsx',
    'frontend/src/components/NoticeBuffer.tsx',
    'frontend/src/components/ActionChecklistTable.tsx',
    'frontend/src/components/GroundedQAChat.tsx',
    'frontend/src/components/OriginalNoticeViewerModal.tsx',
    'frontend/src/components/ConfirmationModal.tsx',
    'frontend/src/components/EvidenceInspectorDrawer.tsx',
    'frontend/src/components/VoiceGuidanceBar.tsx',
    'frontend/src/components/VoiceInputButton.tsx',
    'frontend/src/components/OCRPanel.tsx',
    'frontend/src/components/PlainLanguageSummaryView.tsx',
]

tab_names = {
    0: 'Dashboard',
    1: 'Ingestion & OCR',
    2: 'Grounded Facts',
    3: 'Summary & Actions',
    4: 'Revision Ledger',
    5: 'Eligibility Check',
    6: 'Follow-Up Q&A',
    7: 'Action Navigator',
    8: 'Cross-Notice Timeline',
    9: 'Notice History',
    10: 'Settings & Health',
}

print("=== TAB NAVIGATION AUDIT ===")
for filepath in files:
    if not os.path.exists(filepath): continue
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    for m in re.finditer(r'<button\b([^>]*)>(.*?)</button>', text, re.DOTALL):
        attrs, inner = m.group(1), m.group(2)
        inner_clean = re.sub(r'<[^>]+>', ' ', inner).strip()
        inner_clean = re.sub(r'\s+', ' ', inner_clean)[:45]
        m_tab = re.search(r'setActiveTab\((\d+)\)', attrs)
        if m_tab:
            tab_id = int(m_tab.group(1))
            dest = tab_names.get(tab_id, f'UNKNOWN({tab_id})')
            print(f'{os.path.basename(filepath)}: "{inner_clean}" -> tab {tab_id} ({dest})')
