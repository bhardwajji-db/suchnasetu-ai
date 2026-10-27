import React from 'react';
import { useTranslation } from '../i18n';

interface BrandLogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  isHindi?: boolean;
}

export const BrandLogo: React.FC<BrandLogoProps> = ({
  size = 'md',
  showText = true,
}) => {
  const { t } = useTranslation();
  const iconDimensions = {
    sm: 28,
    md: 32,
    lg: 44,
  }[size];

  return (
    <div className={`brand-mark-container size-${size} flex items-center gap-1.5 sm:gap-2.5 min-w-0 shrink`}>
      {/* Information Bridge (सूचना + सेतु) Brand Mark */}
      <svg
        width={iconDimensions}
        height={iconDimensions}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="brand-logo-svg shrink-0"
        aria-hidden="true"
      >
        {/* Rounded Container */}
        <rect width="48" height="48" rx="12" fill="url(#brandGradient)" />

        {/* Bridge Arch Structure (Symmetric Base) */}
        <path
          d="M6 38C12 28 20 22 24 22C28 22 36 28 42 38"
          stroke="#5eead4"
          strokeWidth="3.5"
          strokeLinecap="round"
        />

        {/* Suspension Cables & Pier Pillars */}
        <path
          d="M14 26.5V36M24 22V36M34 26.5V36"
          stroke="#a7f3d0"
          strokeWidth="2"
          strokeLinecap="round"
        />

        {/* Dynamic AI Information Wave (The Node Hub) */}
        <path
          d="M8 20C12 15 18 13 24 13C30 13 36 15 40 20"
          stroke="#ffffff"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeDasharray="1 0"
        />

        {/* Connecting Data Network Beams */}
        <circle cx="24" cy="13" r="3" fill="#ffffff" />
        <circle cx="12" cy="18" r="2" fill="#5eead4" />
        <circle cx="36" cy="18" r="2" fill="#5eead4" />

        <line x1="12" y1="15.5" x2="12" y2="21" stroke="#5eead4" strokeWidth="1.5" strokeDasharray="1.5 1.5" />
        <line x1="24" y1="14" x2="24" y2="21" stroke="#ffffff" strokeWidth="1.5" />
        <line x1="36" y1="15.5" x2="36" y2="21" stroke="#5eead4" strokeWidth="1.5" strokeDasharray="1.5 1.5" />

        <defs>
          <linearGradient id="brandGradient" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">
            <stop stopColor="#047857" />
            <stop offset="0.6" stopColor="#065f46" />
            <stop offset="1" stopColor="#0f766e" />
          </linearGradient>
        </defs>
      </svg>

      {showText && (
        <div className="brand-text-block min-w-0">
          <div className="brand-primary-line flex items-center gap-1 sm:gap-1.5 flex-nowrap">
            <span className="brand-name text-xs xs:text-sm sm:text-base md:text-lg font-black tracking-tight text-[#12233D] dark:text-[#E8EEF7] truncate">
              Suchna<span className="text-[#08785D] dark:text-[#14B8A6]">Setu</span>
            </span>
            <span className="brand-ai-chip text-[9px] sm:text-[10px] font-extrabold uppercase px-1 py-0.2 bg-[#E8F7F0] dark:bg-[#14B8A6]/20 text-[#08785D] dark:text-[#2DD4BF] rounded border border-[#B7E7D2] dark:border-[#2DD4BF]/30 hidden xs:inline-block">
              AI
            </span>
            <span className="brand-ps-badge text-[9px] font-mono font-bold uppercase px-1 py-0.2 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded border border-slate-200 dark:border-slate-700 hidden md:inline-block">
              PS02
            </span>
            <span className="brand-hindi-pill text-[10px] font-bold px-1.5 py-0.2 bg-[#E8F7F0] dark:bg-[#14B8A6]/15 text-[#08785D] dark:text-[#2DD4BF] rounded hidden lg:inline-block">
              सूचना + सेतु
            </span>
          </div>
          <p className="brand-tagline text-[10px] text-[#526176] dark:text-[#94A3B8] font-medium hidden sm:block truncate">
            {t('authSubtitle')}
          </p>
        </div>
      )}
    </div>
  );
};
