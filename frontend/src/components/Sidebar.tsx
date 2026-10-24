import React, { useState, useEffect } from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import {
  LayoutDashboard,
  FileText,
  Search,
  ListTodo,
  GitCompare,
  UserCheck,
  MessageSquare,
  History,
  Settings,
  Sparkles,
  RotateCcw,
  Activity,
  ChevronDown,
  ChevronUp,
  Compass,
  Layers,
  BookOpen,
  X,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { t } = useTranslation();
  const {
    activeTab,
    setActiveTab,
    isMobileMenuOpen,
    setIsMobileMenuOpen,
    samples,
    loadSampleFixture,
    resetSession,
    systemHealth,
    structuredNotice,
    history,
  } = useNotice();

  const [selectedSample, setSelectedSample] = useState<string>('sample_scholarship_notice.txt');
  const [showDiagnostics, setShowDiagnostics] = useState<boolean>(false);

  // Close mobile drawer on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isMobileMenuOpen) {
        setIsMobileMenuOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isMobileMenuOpen, setIsMobileMenuOpen]);

  const navItems = [
    { id: 0, label: t('navDashboard') || 'Dashboard', icon: LayoutDashboard },
    { id: 1, label: t('navIngestion') || '1. Ingestion & OCR', icon: FileText },
    { id: 2, label: t('navFacts') || '2. Grounded Facts', icon: Search, badge: structuredNotice ? '8 Facts' : undefined },
    { id: 3, label: t('navSummary') || '3. Summary & Actions', icon: ListTodo, badge: structuredNotice ? 'Ready' : undefined },
    { id: 4, label: t('navRevision') || '4. Revision Ledger', icon: GitCompare, badge: 'Impact' },
    { id: 5, label: t('navEligibility') || '5. Eligibility Check', icon: UserCheck, badge: 'Rules' },
    { id: 6, label: t('navQA') || '6. Follow-Up Q&A', icon: MessageSquare },
    { id: 7, label: t('navActionNavigator') || '7. Action Navigator', icon: Compass, badge: 'Roadmap' },
    { id: 8, label: t('navTimeline') || '8. Multi-Notice Timeline', icon: Layers, badge: 'Graph' },
    { id: 9, label: t('navHistory') || 'Notice History', icon: History, badge: history.length > 0 ? `${history.length}` : undefined },
    { id: 10, label: t('navSettings') || 'Settings & Health', icon: Settings },
    { id: 11, label: t('navDemoLibrary') || '11. Demo Library', icon: BookOpen, badge: '32 Demos' },
  ];

  const handleSelectTab = (id: number) => {
    setActiveTab(id);
    setIsMobileMenuOpen(false);
  };

  const handleCompetitionDemo = () => {
    loadSampleFixture('synthetic_scholarship_notice.txt');
    handleSelectTab(1);
  };

  const handleLoadSelectedSample = () => {
    if (selectedSample) {
      loadSampleFixture(selectedSample);
      handleSelectTab(1);
    }
  };

  const renderSidebarContent = () => (
    <>
      <div className="p-4 space-y-6">
        {/* Navigation Group */}
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#68778B] block mb-2 px-1">
            {t('sidebarTitle') || 'Navigation'}
          </span>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => handleSelectTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                    isActive
                      ? 'bg-[#08785D] text-white shadow-xs font-bold'
                      : 'text-[#526176] hover:bg-[#E8F7F0] hover:text-[#08785D]'
                  }`}
                >
                  <div className="flex items-center gap-2.5 truncate">
                    <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : 'text-[#68778B]'}`} />
                    <span className="truncate">{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`text-[10px] font-mono uppercase px-1.5 py-0.5 rounded-md shrink-0 ${
                        isActive
                          ? 'bg-[#06664E] text-[#E8F7F0]'
                          : 'bg-white text-[#08785D] border border-[#B7E7D2]'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Quick Demo Notices Group */}
        <div className="pt-2 border-t border-[#E1E7EE] space-y-3">
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#68778B] block px-1">
            {t('sampleNotices') || 'Demo Notices'}
          </span>

          {/* Golden Benchmark / Competition Demo Button */}
          <button
            type="button"
            onClick={handleCompetitionDemo}
            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-[#08785D] to-[#06664E] hover:from-[#06664E] hover:to-[#054E3C] shadow-xs cursor-pointer transition-all"
            title="Load the official UPSC National Scholarship evaluation notice"
          >
            <Sparkles className="w-3.5 h-3.5 text-white" />
            <span>{t('competitionDemo') || 'Competition Demo (UPSC)'}</span>
          </button>

          {/* Sample Fixtures Dropdown */}
          <div className="space-y-1.5">
            <label htmlFor="sample-selector" className="text-[11px] font-medium text-[#68778B] px-1 block">
              {t('sampleNotices') || 'Sample Notices'}:
            </label>
            <select
              id="sample-selector"
              value={selectedSample}
              onChange={(e) => setSelectedSample(e.target.value)}
              className="w-full bg-white text-[#12233D] border border-[#E1E7EE] rounded-lg px-2.5 py-1.5 text-xs font-medium outline-hidden focus:border-[#08785D] cursor-pointer"
            >
              {samples.length > 0 ? (
                samples.map((s) => (
                  <option key={s.id || s.filename} value={s.filename || s.id}>
                    {s.title || s.filename}
                  </option>
                ))
              ) : (
                <>
                  <option value="synthetic_scholarship_notice.txt">National Merit Scholarship 2026</option>
                  <option value="sample_scholarship_notice.txt">State Post-Matric Circular</option>
                  <option value="demo_response_hearing.txt">Judicial Notice / Summons</option>
                </>
              )}
            </select>
            <button
              type="button"
              onClick={handleLoadSelectedSample}
              className="w-full py-1.5 px-3 rounded-lg text-xs font-semibold text-[#12233D] bg-white hover:bg-[#E8F7F0] hover:text-[#08785D] border border-[#E1E7EE] hover:border-[#B7E7D2] transition cursor-pointer"
            >
              {t('loadSample') || 'Load Selected Notice'}
            </button>
          </div>

          {/* Reset Workspace Action */}
          <button
            type="button"
            onClick={resetSession}
            className="w-full flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-[#B42318] hover:bg-[#FEE8E7] border border-transparent hover:border-[#FCA5A5] transition cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Workspace</span>
          </button>
        </div>
      </div>

      {/* Diagnostics Accordion / Status Footer */}
      <div className="p-3 bg-white border-t border-[#E1E7EE] space-y-2">
        <button
          type="button"
          onClick={() => setShowDiagnostics(!showDiagnostics)}
          className="w-full flex items-center justify-between text-xs font-medium text-[#526176] hover:text-[#12233D] px-1 py-1 cursor-pointer"
        >
          <div className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-[#08785D]" />
            <span>{t('status') || 'Preflight Diagnostics'}</span>
          </div>
          {showDiagnostics ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
        </button>

        {showDiagnostics && (
          <div className="text-[11px] space-y-1 bg-[#F8FAFC] p-2.5 rounded-lg border border-[#E1E7EE] font-mono">
            <div className="flex justify-between items-center">
              <span className="text-[#68778B]">Ollama Daemon:</span>
              <span className={systemHealth?.ollama_connected ? 'text-[#08785D] font-bold' : 'text-[#92500A]'}>
                {systemHealth?.ollama_connected ? 'Connected' : 'Offline (Mock)'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[#68778B]">Tesseract OCR:</span>
              <span className={systemHealth?.tesseract_available ? 'text-[#08785D] font-bold' : 'text-[#92500A]'}>
                {systemHealth?.tesseract_available ? 'Installed' : 'Unavailable'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[#68778B]">Model:</span>
              <span className="text-[#12233D] truncate max-w-[110px]" title={systemHealth?.model_name}>
                {systemHealth?.model_name || 'gemma2:2b'}
              </span>
            </div>
          </div>
        )}

        <div className="text-[10px] text-center text-[#68778B] pt-1">
          HackDay 2026 • PS02 Team
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Desktop / Large Screen Docked Sidebar */}
      <aside className="hidden md:flex flex-col w-64 lg:w-68 bg-[#F8FAFC] border-r border-[#E1E7EE] justify-between h-[calc(100vh-61px)] overflow-y-auto shrink-0 shadow-xs">
        {renderSidebarContent()}
      </aside>

      {/* Mobile / Tablet Slide-Over Drawer with Backdrop */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex" role="dialog" aria-modal="true" aria-label="Navigation Drawer">
          {/* Dark Backdrop */}
          <div
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity"
            onClick={() => setIsMobileMenuOpen(false)}
            aria-hidden="true"
          />

          {/* Slide-over Panel */}
          <aside className="relative z-10 w-72 max-w-[85vw] bg-[#F8FAFC] border-r border-[#E1E7EE] flex flex-col justify-between h-full overflow-y-auto shadow-2xl animate-in slide-in-from-left duration-200">
            {/* Drawer Header */}
            <div className="flex items-center justify-between p-3.5 border-b border-[#E1E7EE] bg-white shrink-0">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#08785D] to-[#06664E] flex items-center justify-center font-black text-white text-sm">
                  स
                </div>
                <div className="flex flex-col leading-none">
                  <span className="font-extrabold text-[#12233D] text-sm">SuchnaSetu AI</span>
                  <span className="text-[10px] text-[#68778B] mt-0.5">Navigation Menu</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsMobileMenuOpen(false)}
                className="p-1.5 rounded-lg text-[#526176] hover:text-[#B42318] hover:bg-[#FEE8E7] transition cursor-pointer"
                aria-label="Dismiss navigation drawer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Inner Content */}
            <div className="flex-1 overflow-y-auto flex flex-col justify-between">
              {renderSidebarContent()}
            </div>
          </aside>
        </div>
      )}
    </>
  );
};
