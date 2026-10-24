import React from 'react';
import { useNotice } from '../context/NoticeContext';
import {
  LayoutDashboard,
  FileText,
  Search,
  ListTodo,
  Menu,
} from 'lucide-react';

export const MobileBottomNav: React.FC = () => {
  const { activeTab, setActiveTab, toggleMobileMenu, isMobileMenuOpen } = useNotice();

  const navButtons = [
    { id: 0, label: 'Home', icon: LayoutDashboard },
    { id: 1, label: 'Ingest', icon: FileText },
    { id: 2, label: 'Facts', icon: Search },
    { id: 3, label: 'Actions', icon: ListTodo },
  ];

  const isMoreActive = activeTab >= 4;

  return (
    <nav
      aria-label="Mobile Bottom Navigation"
      className="md:hidden fixed bottom-0 left-0 right-0 z-30 bg-white/95 backdrop-blur-md border-t border-[#E1E7EE] px-1 py-1 flex items-center justify-around shadow-lg select-none"
    >
      {navButtons.map((btn) => {
        const Icon = btn.icon;
        const isActive = activeTab === btn.id && !isMobileMenuOpen;
        return (
          <button
            key={btn.id}
            type="button"
            onClick={() => setActiveTab(btn.id)}
            className={`flex flex-col items-center justify-center flex-1 py-1 px-1 rounded-xl transition cursor-pointer ${
              isActive
                ? 'text-[#08785D] font-bold'
                : 'text-[#68778B] hover:text-[#12233D]'
            }`}
            aria-label={btn.label}
            aria-current={isActive ? 'page' : undefined}
          >
            <div
              className={`p-1 rounded-lg transition ${
                isActive ? 'bg-[#E8F7F0] text-[#08785D]' : ''
              }`}
            >
              <Icon className="w-4 h-4" />
            </div>
            <span className="text-[10px] tracking-tight mt-0.5">{btn.label}</span>
          </button>
        );
      })}

      {/* Menu / All Tools Button */}
      <button
        type="button"
        onClick={toggleMobileMenu}
        className={`flex flex-col items-center justify-center flex-1 py-1 px-1 rounded-xl transition cursor-pointer ${
          isMobileMenuOpen || isMoreActive
            ? 'text-[#08785D] font-bold'
            : 'text-[#68778B] hover:text-[#12233D]'
        }`}
        aria-label="Open full tool menu"
      >
        <div
          className={`p-1 rounded-lg transition ${
            isMobileMenuOpen || isMoreActive ? 'bg-[#E8F7F0] text-[#08785D]' : ''
          }`}
        >
          <Menu className="w-4 h-4" />
        </div>
        <span className="text-[10px] tracking-tight mt-0.5">
          {isMoreActive ? 'More (Active)' : 'Menu'}
        </span>
      </button>
    </nav>
  );
};
