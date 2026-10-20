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
        return <Target className="w-4 h-4 text-blue-400" />;
      case 'deadline':
        return <Calendar className="w-4 h-4 text-emerald-400" />;
      case 'eligibility':
        return <UserCheck className="w-4 h-4 text-indigo-400" />;
      case 'actions':
        return <CheckSquare className="w-4 h-4 text-sky-400" />;
      default:
        return <HelpCircle className="w-4 h-4 text-slate-400" />;
    }
  };

  const getStatusBadge = () => {
    if (!fact) return null;
    if (fact.status === 'stated') {
      return (
        <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800">
          Stated
        </span>
      );
    }
    if (fact.status === 'not_stated') {
      return (
        <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
          Not Stated
        </span>
      );
    }
    return (
      <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-amber-950/80 text-amber-400 border border-amber-800">
        Needs Confirmation
      </span>
    );
  };

  const displayValue = fact?.value || 'Pending notice analysis...';

  return (
    <div className="bg-[#0D1528] border border-[#1D2D4E] hover:border-blue-500/50 transition-all rounded-xl p-4 flex flex-col justify-between shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {getIcon()}
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
            {label}
          </span>
        </div>
        {getStatusBadge()}
      </div>
      <div className="text-sm font-semibold text-slate-100 line-clamp-2 mt-1">
        {displayValue}
      </div>
    </div>
  );
};
