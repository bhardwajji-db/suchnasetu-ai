import React from 'react';

interface CivicWelcomeIllustrationProps {
  className?: string;
}

export const CivicWelcomeIllustration: React.FC<CivicWelcomeIllustrationProps> = ({
  className = 'w-44 h-28 sm:w-52 sm:h-32',
}) => {
  return (
    <div
      className={`relative flex items-center justify-center shrink-0 pointer-events-none select-none ${className}`}
      aria-hidden="true"
    >
      <svg
        viewBox="0 0 220 140"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full drop-shadow-sm"
      >
        <defs>
          {/* Subtle Ambient Glow */}
          <radialGradient
            id="civic-ambient"
            cx="0"
            cy="0"
            r="1"
            gradientUnits="userSpaceOnUse"
            gradientTransform="translate(110 70) rotate(90) scale(65 95)"
          >
            <stop stopColor="#08785D" stopOpacity="0.12" />
            <stop offset="1" stopColor="#08785D" stopOpacity="0" />
          </radialGradient>

          {/* Document Fill Gradient */}
          <linearGradient id="doc-surface" x1="50" y1="20" x2="150" y2="120" gradientUnits="userSpaceOnUse">
            <stop stopColor="#FFFFFF" stopOpacity="0.95" />
            <stop offset="1" stopColor="#F1F5F9" stopOpacity="0.85" />
          </linearGradient>

          {/* Accent Teal Gradient */}
          <linearGradient id="civic-accent" x1="0" y1="0" x2="1" y2="1">
            <stop stopColor="#08785D" />
            <stop offset="1" stopColor="#14B8A6" />
          </linearGradient>

          {/* Deadline Tag Gradient */}
          <linearGradient id="deadline-tag" x1="0" y1="0" x2="1" y2="1">
            <stop stopColor="#F59E0B" />
            <stop offset="1" stopColor="#D97706" />
          </linearGradient>
        </defs>

        {/* Ambient Glow Backdrop */}
        <ellipse cx="110" cy="70" rx="90" ry="55" fill="url(#civic-ambient)" />

        {/* Background Document Shadow Plate */}
        <rect
          x="62"
          y="28"
          width="88"
          height="92"
          rx="10"
          fill="#0F172A"
          fillOpacity="0.06"
          transform="rotate(6 106 74)"
        />

        {/* Secondary Document Behind */}
        <rect
          x="56"
          y="22"
          width="88"
          height="92"
          rx="10"
          fill="url(#doc-surface)"
          stroke="#CBD5E1"
          strokeWidth="1.5"
          transform="rotate(-4 100 68)"
        />

        {/* Main Document Body */}
        <rect
          x="64"
          y="20"
          width="92"
          height="96"
          rx="10"
          fill="url(#doc-surface)"
          stroke="#94A3B8"
          strokeWidth="1.5"
        />

        {/* Document Header Bar */}
        <rect x="74" y="30" width="38" height="6" rx="3" fill="url(#civic-accent)" />
        <circle cx="144" cy="33" r="4" fill="#08785D" fillOpacity="0.25" />
        <circle cx="144" cy="33" r="2" fill="#08785D" />

        {/* Document Text Skeleton Lines */}
        <rect x="74" y="44" width="72" height="4" rx="2" fill="#94A3B8" fillOpacity="0.45" />
        <rect x="74" y="53" width="60" height="4" rx="2" fill="#94A3B8" fillOpacity="0.35" />
        <rect x="74" y="62" width="68" height="4" rx="2" fill="#94A3B8" fillOpacity="0.35" />
        <rect x="74" y="71" width="46" height="4" rx="2" fill="#94A3B8" fillOpacity="0.3" />

        {/* Grounded Evidence Badge on Document */}
        <g transform="translate(74, 84)">
          <rect x="0" y="0" width="44" height="18" rx="5" fill="#E8F7F0" stroke="#08785D" strokeWidth="1" strokeOpacity="0.5" />
          <path
            d="M8 9.5L11 12.5L16 6.5"
            stroke="#08785D"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <text x="20" y="12.5" fill="#08785D" fontSize="7.5" fontWeight="bold" fontFamily="sans-serif">
            VERIFIED
          </text>
        </g>

        {/* Floating Mini Deadline Radar Pill (Right Side) */}
        <g transform="translate(138, 72)">
          <rect
            x="0"
            y="0"
            width="68"
            height="34"
            rx="8"
            fill="#FFFFFF"
            stroke="#E2E8F0"
            strokeWidth="1.25"
            filter="drop-shadow(0 4px 6px rgba(0,0,0,0.06))"
          />
          {/* Calendar Mini Header */}
          <rect x="0" y="0" width="68" height="10" rx="6" fill="url(#deadline-tag)" />
          <circle cx="10" cy="5" r="1.5" fill="#FFFFFF" />
          <circle cx="58" cy="5" r="1.5" fill="#FFFFFF" />
          <text x="9" y="24" fill="#1E293B" fontSize="9" fontWeight="800" fontFamily="sans-serif">
            15 NOV
          </text>
          <text x="44" y="24" fill="#D97706" fontSize="7.5" fontWeight="bold" fontFamily="sans-serif">
            DUE
          </text>
        </g>

        {/* Floating Civic Sparkle / AI Node (Top Left) */}
        <g transform="translate(36, 42)">
          <circle cx="12" cy="12" r="14" fill="#08785D" fillOpacity="0.08" />
          <path
            d="M12 4L13.8 9.8L19.6 11.6L13.8 13.4L12 19.2L10.2 13.4L4.4 11.6L10.2 9.8L12 4Z"
            fill="url(#civic-accent)"
          />
        </g>

        {/* Secondary Sparkle Node (Bottom Left) */}
        <g transform="translate(48, 88)">
          <path
            d="M8 2L9.2 6.2L13.4 7.4L9.2 8.6L8 12.8L6.8 8.6L2.6 7.4L6.8 6.2L8 2Z"
            fill="#14B8A6"
            fillOpacity="0.75"
          />
        </g>

        {/* Connecting Neural Pulse Line */}
        <path
          d="M48 54C54 62 60 70 72 74"
          stroke="#14B8A6"
          strokeWidth="1.2"
          strokeDasharray="2 2"
          strokeOpacity="0.6"
        />
      </svg>
    </div>
  );
};
