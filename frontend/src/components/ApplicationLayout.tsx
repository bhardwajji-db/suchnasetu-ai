import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { DashboardView } from '../views/DashboardView';
import { IngestionView } from '../views/IngestionView';
import { GroundedFactsView } from '../views/GroundedFactsView';
import { SummaryActionsView } from '../views/SummaryActionsView';
import { FollowUpQAView } from '../views/FollowUpQAView';
import { NoticeHistoryView } from '../views/NoticeHistoryView';
import { SettingsView } from '../views/SettingsView';
import { AnalysisProgressModal } from './AnalysisProgressModal';
import { ConfirmationModal } from './ConfirmationModal';
import { OriginalNoticeViewerModal } from './OriginalNoticeViewerModal';

export const ApplicationLayout: React.FC = () => {
  const { activeTab } = useNotice();

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
        return <FollowUpQAView />;
      case 5:
        return <NoticeHistoryView />;
      case 6:
        return <SettingsView />;
      default:
        return <DashboardView />;
    }
  };

  return (
    <div className="min-h-screen bg-[#070B14] text-slate-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 md:p-8 max-w-7xl mx-auto w-full">
          {renderActiveView()}
        </main>
      </div>
      <AnalysisProgressModal />
      <ConfirmationModal />
      <OriginalNoticeViewerModal />
    </div>
  );
};
