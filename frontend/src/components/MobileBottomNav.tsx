import React from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import {
  LayoutDashboard,
  FileText,
  Search,
  ListTodo,
  Menu,
} from 'lucide-react';

export const MobileBottomNav: React.FC = () => {
  const { activeTab, setActiveTab, toggleMobileMenu, isMobileMenuOpen } = useNotice();
  const { t } = useTranslation();

  const getNavLabel = (id: number) => {
    switch (id) {
      case 0:
        return t('mobileNavHome') || 'Home';
      case 1:
        return t('mobileNavIngest') || 'Ingest';
      case 2:
        return t('mobileNavFacts') || 'Facts';
      case 3:
        return t('mobileNavActions') || 'Actions';
      default:
        return t('mobileNavMore') || 'More';
    }
  };

  const navButtons = [
    { id: 0, label: getNavLabel(0), icon: LayoutDashboard },
    { id: 1, label: getNavLabel(1), icon: FileText },
    { id: 2, label: getNavLabel(2), icon: Search },
    { id: 3, label: getNavLabel(3), icon: ListTodo },
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
        <span className="text-[10px] tracking-tight mt-0.5 truncate max-w-[55px]">
          {isMoreActive ? (t('mobileNavMoreActive') || 'More (Active)') : (t('mobileNavMenu') || 'Menu')}
        </span>
      </button>
    </nav>
  );
};
