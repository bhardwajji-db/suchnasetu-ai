import React from 'react';
import type { ExtractedFact } from '../types/api';
import { Target, Calendar, UserCheck, CheckSquare, HelpCircle } from 'lucide-react';

interface MetricCardProps {
  fact?: ExtractedFact | null;
  label: string;
  iconType: 'purpose' | 'deadline' | 'eligibility' | 'actions';
}

export const MetricCard: React.FC<MetricCardProps> = ({ fact, label, iconType }) => {
  const getIcon = () => {
    switch (iconType) {
      case 'purpose':
        return <Target className="w-4 h-4 text-[#08785D]" />;
      case 'deadline':
        return <Calendar className="w-4 h-4 text-[#08785D]" />;
      case 'eligibility':
        return <UserCheck className="w-4 h-4 text-[#08785D]" />;
      case 'actions':
        return <CheckSquare className="w-4 h-4 text-[#08785D]" />;
      default:
        return <HelpCircle className="w-4 h-4 text-[#68778B]" />;
    }
  };

  const getStatusBadge = () => {
    if (!fact) return null;
    if (fact.status === 'stated') {
      return (
        <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-md bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]">
          Stated
        </span>
      );
    }
    if (fact.status === 'not_stated') {
      return (
        <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-md bg-slate-100 text-[#526176] border border-slate-200">
          Not Stated
        </span>
      );
    }
    return (
      <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-md bg-[#FFF4D6] text-[#92500A] border border-[#FDE68A]">
        Needs Confirmation
      </span>
    );
  };

  const displayValue = fact?.value || 'Pending notice analysis...';

  return (
    <div className="bg-white border border-[#E1E7EE] hover:border-[#B7E7D2] transition-all rounded-xl p-4 flex flex-col justify-between shadow-xs">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {getIcon()}
          <span className="text-xs font-bold uppercase tracking-wider text-[#526176]">
            {label}
          </span>
        </div>
        {getStatusBadge()}
      </div>
      <div className="text-sm font-semibold text-[#12233D] line-clamp-2 mt-1">
        {displayValue}
      </div>
    </div>
  );
};
