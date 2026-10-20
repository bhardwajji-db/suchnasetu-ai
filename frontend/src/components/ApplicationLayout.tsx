import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { IngestionView } from '../views/IngestionView';
import { GroundedFactsView } from '../views/GroundedFactsView';
import { SummaryActionsView } from '../views/SummaryActionsView';
import { FollowUpQAView } from '../views/FollowUpQAView';
import { AnalysisProgressModal } from './AnalysisProgressModal';

export const ApplicationLayout: React.FC = () => {
  const { activeTab } = useNotice();

  const renderActiveView = () => {
    switch (activeTab) {
      case 0:
        return <IngestionView />;
      case 1:
        return <GroundedFactsView />;
      case 2:
        return <SummaryActionsView />;
      case 3:
        return <FollowUpQAView />;
      default:
        return <IngestionView />;
    }
  };

  return (
    <div className="min-h-screen bg-[#070B14] text-slate-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6 md:p-8 max-w-7xl mx-auto w-full">
          {renderActiveView()}
        </main>
      </div>
      <AnalysisProgressModal />
    </div>
  );
};
