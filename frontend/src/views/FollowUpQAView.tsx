import React from 'react';
import { GroundedQAChat } from '../components/GroundedQAChat';
import { StaleWarningBanner } from '../components/StaleWarningBanner';

export const FollowUpQAView: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <span>💬 4. Notice-Grounded Follow-Up Q&A</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Ask clarification questions. The assistant answers strictly using verbatim facts in the notice and explicitly flags unstated topics.
        </p>
      </div>

      <StaleWarningBanner />

      <GroundedQAChat />
    </div>
  );
};
