import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { DashboardView } from '../views/DashboardView';
import { IngestionView } from '../views/IngestionView';
import { GroundedFactsView } from '../views/GroundedFactsView';
import { SummaryActionsView } from '../views/SummaryActionsView';
import { RevisionLedgerView } from '../views/RevisionLedgerView';
import { EligibilityEngineView } from '../views/EligibilityEngineView';
import { FollowUpQAView } from '../views/FollowUpQAView';
import { PersonalizedActionNavigatorView } from '../views/PersonalizedActionNavigatorView';
import { CrossNoticeTimelineView } from '../views/CrossNoticeTimelineView';
import { NoticeHistoryView } from '../views/NoticeHistoryView';
import { SettingsView } from '../views/SettingsView';
import { DemoLibraryView } from '../views/DemoLibraryView';
import { AuthPageView } from '../views/AuthPageView';
import { ErrorBoundary } from './ErrorBoundary';
import { AnalysisProgressModal } from './AnalysisProgressModal';
import { ConfirmationModal } from './ConfirmationModal';
import { OriginalNoticeViewerModal } from './OriginalNoticeViewerModal';
import { EvidenceInspectorDrawer } from './EvidenceInspectorDrawer';
import { VoiceGuidanceBar } from './VoiceGuidanceBar';
import { MobileBottomNav } from './MobileBottomNav';

export const ApplicationLayout: React.FC = () => {
  const { activeTab, setActiveTab, authPageMode, accessibilityPrefs, theme } = useNotice();

  const textSizeClass =
    accessibilityPrefs?.textSize === 'extra-large'
      ? 'text-base'
      : accessibilityPrefs?.textSize === 'large'
      ? 'text-[15px]'
      : 'text-sm';

  const lineSpacingClass =
    accessibilityPrefs?.lineSpacing === 'loose'
      ? 'leading-loose space-y-7'
      : accessibilityPrefs?.lineSpacing === 'relaxed'
      ? 'leading-relaxed'
      : 'leading-normal';

  const themeClass = theme === 'dark'
    ? 'theme-dark bg-[#0B1220] text-[#E8EEF7]'
    : accessibilityPrefs?.highContrast
    ? 'bg-slate-900 text-white font-medium high-contrast'
    : accessibilityPrefs?.warmBackground
    ? 'bg-[#FAF6EE] text-[#1D1E20]'
    : 'bg-[#F5F8FA] text-[#12233D]';

  const motionClass = accessibilityPrefs?.reducedMotion ? 'motion-reduce' : '';

  const renderActiveView = () => {
    switch (activeTab) {
      case 0:
        return <DashboardView />;
      case 1:
        return <IngestionView />;
      case 2:
        return <GroundedFactsView />;
      case 3:
        return <SummaryActionsView />;
      case 4:
        return <RevisionLedgerView />;
      case 5:
        return <EligibilityEngineView />;
      case 6:
        return <FollowUpQAView />;
      case 7:
        return <PersonalizedActionNavigatorView />;
      case 8:
        return <CrossNoticeTimelineView />;
      case 9:
        return <NoticeHistoryView />;
      case 10:
        return <SettingsView />;
      case 11:
        return <DemoLibraryView />;
      default:
        return <DashboardView />;
    }
  };

  if (activeTab === 99) {
    return <AuthPageView initialMode={authPageMode} onComplete={() => setActiveTab(0)} />;
  }

  return (
    <div className={`min-h-screen flex flex-col font-sans selection:bg-[#08785D] selection:text-white pb-20 md:pb-12 overflow-x-hidden w-full ${themeClass} ${textSizeClass} ${lineSpacingClass} ${motionClass}`}>
      <Header />
      <div className="flex flex-1 overflow-hidden min-w-0 w-full">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-3 sm:p-5 md:p-8 max-w-7xl mx-auto w-full min-w-0">
          <ErrorBoundary key={activeTab}>
            {renderActiveView()}
          </ErrorBoundary>
        </main>
      </div>
      <MobileBottomNav />
      <AnalysisProgressModal />
      <ConfirmationModal />
      <OriginalNoticeViewerModal />
      <EvidenceInspectorDrawer />
      <VoiceGuidanceBar />
    </div>
  );
};
