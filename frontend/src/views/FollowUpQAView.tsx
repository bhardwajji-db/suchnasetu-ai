import { MessageSquare } from 'lucide-react';
import React from 'react';
import { useTranslation } from '../i18n';
import { GroundedQAChat } from '../components/GroundedQAChat';
import { StaleWarningBanner } from '../components/StaleWarningBanner';

export const FollowUpQAView: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-[#12233D] tracking-tight flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-[#08785D]" />
          <span>{t('qaTitle') || '4. Notice-Grounded Follow-Up Q&A'}</span>
        </h1>
        <p className="text-xs text-[#526176] mt-1">
          {t('qaSubtitle') || 'Ask clarification questions. The assistant answers strictly using verbatim facts in the notice and explicitly flags unstated topics.'}
        </p>
      </div>

      <StaleWarningBanner />

      <GroundedQAChat />
    </div>
  );
};
