import React, { useState, useEffect, useCallback } from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation } from '../i18n';
import { FileDropzone } from '../components/FileDropzone';
import { OCRPanel } from '../components/OCRPanel';
import { NoticeBuffer } from '../components/NoticeBuffer';
import { CivicWelcomeIllustration } from '../components/CivicWelcomeIllustration';
import { apiClient } from '../services/apiClient';
import type { UserNotification, UserActivity } from '../types/api';
import {
  UploadCloud,
  Sparkles,
  BookMarked,
  CheckSquare,
  Clock,
  Calendar,
  Bell,
  CheckCircle2,
  AlertTriangle,
  Info,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  Trash2,
  ChevronRight,
  RefreshCw,
  X,
  FileSearch,
} from 'lucide-react';

export const DashboardView: React.FC = () => {
  const {
    setActiveTab,
    loadSampleFixture,
    rawNoticeText,
    setRawNoticeText,
    setDocumentId,
    systemHealth,
    activeProvider,
    runAnalysis,
    isAnalyzing,
    uploadedImage,
    structuredNotice,
    checklistEn,
    savedNoticeIds,
    toggleSaveNotice,
    openEvidenceInspector,
    clearBuffer,  resetSession,
    currentUser,
    setUnreadNotificationsCount,
  } = useNotice();

  const { t } = useTranslation();

  // Local state for dashboard data
  const [savedNotices, setSavedNotices] = useState<any[]>([]);
  const [weeklyPlan, setWeeklyPlan] = useState<any | null>(null);
  const [notifications, setNotifications] = useState<UserNotification[]>([]);
  const [unreadNotifsCount, setUnreadNotifsCount] = useState<number>(0);
  const [activities, setActivities] = useState<UserActivity[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  // UI Interactive state
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);
  const [deadlineFilter, setDeadlineFilter] = useState<'all' | 'due_this_week' | 'tentative'>('all');
  const [actionFilter, setActionFilter] = useState<'all' | 'pending' | 'completed'>('all');
  const [isQuickIngestOpen, setIsQuickIngestOpen] = useState<boolean>(false);
  const [completedTaskIds, setCompletedTaskIds] = useState<Record<string, boolean>>({});

  // Detect whether active buffer/notice contains synthetic demo fixture
  const isDemoActive = Boolean(
    rawNoticeText &&
      (rawNoticeText.includes('DEMO-') ||
        rawNoticeText.includes('Synthetic') ||
        rawNoticeText.includes('National Merit Scholarship 2026') ||
        rawNoticeText.includes('PS02 scholarship'))
  );

  // Fetch all real dashboard data from backend APIs
  const fetchDashboardData = useCallback(async () => {
    setIsLoading(true);
    setLoadError(null);
    try {
      const activeUser = currentUser;

      // Fetch public / guest-compatible dashboard resources
      const calls: Promise<any>[] = [
        apiClient.getSavedNotices(),
        apiClient.getWeeklyTasks(),
        apiClient.getUserNotifications(),
        apiClient.getUserActivities(15),
      ];

      // Strictly isolated user checklist is only requested for authenticated citizens
      if (activeUser) {
        calls.push(apiClient.getUserChecklistProgress());
      }

      const results = await Promise.allSettled(calls);
      const savedRes = results[0];
      const weeklyRes = results[1];
      const notifsRes = results[2];
      const actsRes = results[3];
      const checklistRes = activeUser ? results[4] : null;
      if (savedRes.status === 'fulfilled') {
        setSavedNotices(savedRes.value || []);
      }
      if (weeklyRes.status === 'fulfilled') {
        setWeeklyPlan(weeklyRes.value || null);
      }
      if (notifsRes.status === 'fulfilled') {
        setNotifications(notifsRes.value?.notifications || []);
        const unread = notifsRes.value?.unread_count || 0;
        setUnreadNotifsCount(unread);
        setUnreadNotificationsCount?.(unread);
      }
      if (actsRes.status === 'fulfilled') {
        setActivities(actsRes.value || []);
      }
      if (checklistRes && checklistRes.status === 'fulfilled') {
        const progress = (checklistRes as PromiseFulfilledResult<any>).value?.checklist_progress || {};
        setCompletedTaskIds((prev) => ({ ...prev, ...progress }));
      }
    } catch (err: any) {
      setLoadError(err.message || 'Failed to refresh dashboard data.');
    } finally {
      setIsLoading(false);
    }
  }, [currentUser, setUnreadNotificationsCount]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData, savedNoticeIds.length]);

  // Handlers
  const handleLoadDemo = () => {
    loadSampleFixture('synthetic_scholarship_notice.txt');
    setActiveTab(1);
  };

  const handleDashboardAnalyze = () => {
    setActiveTab(1);
    runAnalysis();
  };

  const handleMarkAllRead = async () => {
    try {
      await apiClient.markAllNotificationsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadNotifsCount(0);
      setUnreadNotificationsCount?.(0);
    } catch (err) {
      console.error('Failed to mark all notifications read:', err);
    }
  };

  const handleDismissNotification = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await apiClient.dismissNotification(id);
      setNotifications((prev) => {
        const target = prev.find((n) => n.id === id);
        if (target && !target.is_read) {
          setUnreadNotifsCount((c) => Math.max(0, c - 1));
        setUnreadNotificationsCount?.((c: number) => Math.max(0, c - 1));
        }
        return prev.filter((n) => n.id !== id);
      });
    } catch (err) {
      console.error('Failed to dismiss notification:', err);
    }
  };

  const handleNotificationClick = async (notif: UserNotification) => {
    if (!notif.is_read) {
      try {
        await apiClient.markNotificationRead(notif.id);
        setNotifications((prev) =>
          prev.map((n) => (n.id === notif.id ? { ...n, is_read: true } : n))
        );
        setUnreadNotifsCount((c) => Math.max(0, c - 1));
        setUnreadNotificationsCount?.((c: number) => Math.max(0, c - 1));
      } catch (err) {
        console.error('Failed to mark notification read:', err);
      }
    }
    if (notif.document_id) {
      const matched = savedNotices.find((s) => s.document_id === notif.document_id);
      if (matched && matched.raw_text) {
        setRawNoticeText(matched.raw_text);
        setDocumentId(matched.document_id);
        setActiveTab(1);
      }
    }
  };

  const handleOpenNoticeInWorkspace = (notice: any) => {
    if (notice.raw_text) {
      setRawNoticeText(notice.raw_text);
    }
    if (notice.document_id) {
      setDocumentId(notice.document_id);
    }
    setActiveTab(1);
  };

  const handleViewNoticeEvidence = (notice: any) => {
    openEvidenceInspector(
      {
        excerpt: notice.deadline || notice.submission_date || notice.title,
        claim: notice.title,
        docTitle: notice.authority || 'Official Authority',
      },
      notice.raw_text
    );
  };

  const handleUnsaveNotice = async (documentId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await apiClient.unsaveUserNotice(documentId);
      toggleSaveNotice(documentId);
      setSavedNotices((prev) => prev.filter((s) => s.document_id !== documentId));
    } catch (err) {
      console.error('Failed to unsave notice:', err);
    }
  };

  const handleToggleTask = async (taskId: string, currentCompleted: boolean) => {
    const nextCompleted = !currentCompleted;
    setCompletedTaskIds((prev) => ({ ...prev, [taskId]: nextCompleted }));
    try {
      await Promise.allSettled([
        apiClient.toggleUserChecklistProgress(taskId, nextCompleted),
        apiClient.toggleChecklistItemPersistent(taskId, nextCompleted),
      ]);
    } catch {
      // Revert on complete failure
      setCompletedTaskIds((prev) => ({ ...prev, [taskId]: currentCompleted }));
    }
  };

  // Compute tasks from weekly plan and active checklist
  const allWeeklyTasks: any[] = [
    ...(weeklyPlan?.due_this_week || []),
    ...(weeklyPlan?.upcoming_later || []),
    ...(weeklyPlan?.past_due || []),
    ...(weeklyPlan?.ambiguous_tasks || []),
  ];

  // De-duplicate tasks
  const uniqueTasks = Array.from(
    new Map(allWeeklyTasks.map((t) => [`${t.document_id || ''}-${t.task_title}`, t])).values()
  );

  // If user has analyzed a current notice with checklist items, combine them
  const activeChecklistTasks = (checklistEn?.items || []).map((item, idx) => ({
    task_title: item.action,
    raw_line: item.notes || item.action,
    parsed_date: (item as any).deadline || null,
    raw_deadline: item.notes || 'Per notice timeline',
    is_ambiguous_date: false,
    ambiguity_reason: 'Extracted from active notice checklist.',
    notice_title: structuredNotice?.main_subject?.value || 'Current Analyzed Notice',
    document_id: 'current',
    step_number: item.step_number || idx + 1,
    status: 'ACTIVE_NOTICE',
    id: `cl_step_${item.step_number || idx + 1}`,
  }));

  const combinedTasks = uniqueTasks.length > 0 ? uniqueTasks : activeChecklistTasks;

  // Filter deadlines
  const filteredDeadlines = combinedTasks.filter((t) => {
    if (deadlineFilter === 'due_this_week') {
      return t.status === 'DUE_THIS_WEEK' || (t.days_remaining !== undefined && t.days_remaining >= 0 && t.days_remaining <= 7);
    }
    if (deadlineFilter === 'tentative') {
      return Boolean(t.is_ambiguous_date);
    }
    return true;
  });

  // Filter action tasks
  const filteredActions = combinedTasks.filter((t) => {
    const isDone = completedTaskIds[t.id || t.task_title] ?? false;
    if (actionFilter === 'pending') return !isDone;
    if (actionFilter === 'completed') return isDone;
    return true;
  });

  const pendingActionsCount = combinedTasks.filter(
    (t) => !(completedTaskIds[t.id || t.task_title] ?? false)
  ).length;

  const upcomingDeadlinesCount = (weeklyPlan?.due_this_week_count || 0) + (weeklyPlan?.ambiguous_tasks?.length || 0);

  // System status badge
  const getSystemStatus = () => {
    if (!systemHealth) {
      return {
        text: 'Checking system...',
        color: 'text-[#92500A] bg-[#FFF4D6] border-[#FDE68A]',
      };
    }
    if (systemHealth.overall_status === 'ok') {
      return {
        text: `System Ready · ${activeProvider === 'ollama' ? 'Local Gemma 4 (Ollama)' : activeProvider}`,
        color: 'text-[#08785D] bg-[#E8F7F0] border-[#B7E7D2]',
      };
    }
    return {
      text: 'Diagnostics Warning',
      color: 'text-[#92500A] bg-[#FFF4D6] border-[#FDE68A]',
    };
  };

  const status = getSystemStatus();

  // FAQs
  const faqs = [
    {
      q: t('faq1Q') || 'How does SuchnaSetu AI ensure extracted facts are accurate?',
      a: t('faq1A') || 'SuchnaSetu AI employs a strict evidence-grounding engine. Every extracted deadline, fee, and requirement is matched against exact character offsets in the raw document text. If a detail cannot be verified with verbatim evidence, it is explicitly flagged as unstated or uncertain rather than hallucinated.',
    },
    {
      q: t('faq2Q') || 'Does completing the action checklist submit my official application?',
      a: t('faq2A') || 'No. The action checklist is a personal preparation tool to help you organize documents, deadlines, and eligibility criteria. Official submissions must always be completed directly on the authorized government or institutional portal.',
    },
    {
      q: t('faq3Q') || 'Can SuchnaSetu AI operate completely offline?',
      a: t('faq3A') || 'Yes. With a local Ollama instance (such as Gemma 4 or Qwen 2.5) and host Tesseract OCR installed, the entire ingestion, OCR, extraction, and Q&A pipeline runs 100% locally on your machine with zero cloud connectivity required.',
    },
    {
      q: t('faq4Q') || 'What document formats and file sizes are supported?',
      a: t('faq4A') || 'The application supports digital and scanned PDFs, Word documents (DOCX), images (PNG, JPG, JPEG, WEBP), and plain text documents (TXT) up to 10MB in size.',
    },
    {
      q: t('faq5Q') || 'How does the Change Tracker compare revisions and corrigenda?',
      a: t('faq5A') || 'The Change Tracker analyzes original notices alongside revised circulars or corrigenda, producing a field-by-field delta that highlights additions, modifications, cancellations, and extensions with exact source citations.',
    },
  ];

  return (
    <div className="space-y-6 sm:space-y-8 animate-fadeIn pb-10">
      {/* 1. Header Banner & Citizen Welcome Strip */}
      <section className="relative overflow-hidden rounded-2xl sm:rounded-3xl bg-white border border-[#E1E7EE] p-5 sm:p-7 shadow-xs">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full text-xs font-semibold border ${status.color}`}>
                <span className="w-2 h-2 rounded-full bg-[#08785D] animate-pulse" />
                <span>{status.text}</span>
              </span>
              {currentUser ? (
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-[#12233D] border border-slate-200">
                  {currentUser.email}
                </span>
              ) : (
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-[#526176] border border-slate-200">
                  {t('guestUser') || 'Guest Citizen Access'}
                </span>
              )}
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-[#12233D] tracking-tight">
              {currentUser ? `Welcome back, ${currentUser.name}` : (t('dashboardOverview') || 'Citizen Civic Dashboard')}
            </h1>
            <p className="text-xs sm:text-sm text-[#526176] max-w-2xl leading-relaxed">
              {t('dashboardSubtitle') ||
                'Your civic intelligence hub: track saved circulars, verified deadlines, pending actions, and notifications in real time.'}
            </p>
          </div>

          {/* Tasteful Civic Notice & Deadline Vector Illustration */}
          <div className="hidden lg:flex shrink-0 items-center justify-center py-1">
            <CivicWelcomeIllustration className="w-36 h-28 drop-shadow-xs" />
          </div>

          {/* Action CTAs */}
          <div className="flex items-center gap-2.5 flex-wrap w-full md:w-auto">
            <button
              type="button"
              onClick={() => setIsQuickIngestOpen(!isQuickIngestOpen)}
              className="flex-1 md:flex-initial inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs cursor-pointer"
            >
              <UploadCloud className="w-4 h-4" />
              <span>{isQuickIngestOpen ? 'Close Quick Ingest' : (t('navIngestion') || 'Quick Ingest & Analyze')}</span>
            </button>
            <button
              type="button"
              onClick={handleLoadDemo}
              className="flex-1 md:flex-initial inline-flex items-center justify-center gap-2 px-3.5 py-2.5 rounded-xl font-semibold text-xs text-[#12233D] bg-[#F8FAFC] hover:bg-[#E8F7F0] hover:text-[#08785D] border border-[#CBD5E1] transition cursor-pointer"
            >
              <Sparkles className="w-4 h-4 text-[#08785D]" />
              <span>{t('competitionDemo') || 'Explore Demo'}</span>
            </button>
            <button
              type="button"
              onClick={fetchDashboardData}
              disabled={isLoading}
              className="p-2.5 rounded-xl text-[#526176] hover:text-[#12233D] bg-[#F8FAFC] border border-[#CBD5E1] hover:bg-slate-100 transition cursor-pointer"
              title="Refresh Dashboard Data"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-[#08785D]' : ''}`} />
            </button>
          </div>
        </div>
      </section>

      {/* Network / Load Error Banner */}
      {loadError && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-3.5 flex items-center justify-between text-xs text-red-800">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-600 shrink-0" />
            <span>{loadError}</span>
          </div>
          <button
            type="button"
            onClick={fetchDashboardData}
            className="font-bold underline hover:text-red-950 cursor-pointer"
          >
            Retry
          </button>
        </div>
      )}

      {/* 2. Demo Mode Active Warning & Switcher Banner */}
      {isDemoActive && (
        <div className="rounded-xl border border-amber-300 bg-[#FFFBEB] p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-2xs">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-amber-100 border border-amber-200 text-amber-800 flex items-center justify-center shrink-0 mt-0.5">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-amber-900 uppercase tracking-wide">
                  {t('demoNoticeActive') || 'Synthetic Demonstration Mode Active'}
                </span>
                <span className="text-[10px] bg-amber-200/80 text-amber-900 px-2 py-0.2 rounded font-semibold font-mono">
                  BENCHMARK FIXTURE
                </span>
              </div>
              <p className="text-xs text-amber-800 mt-0.5">
                {t('demoNoticeNotice') ||
                  'You are currently previewing demonstration data. Upload a real notice or clear demo data to view your live personal data.'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0 self-end sm:self-auto">
            <button
              type="button"
              onClick={() => {
                clearBuffer();
                resetSession();
                setActiveTab(1);
              }}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-amber-900 border border-amber-300 hover:bg-amber-100 transition cursor-pointer"
            >
              {t('switchRealUpload') || 'Upload Real Notice'}
            </button>
            <button
              type="button"
              onClick={() => {
                clearBuffer();
                resetSession();
              }}
              className="px-2.5 py-1.5 rounded-lg text-xs font-semibold text-amber-800 hover:text-amber-950 transition cursor-pointer"
            >
              {t('clearDemo') || 'Clear Demo'}
            </button>
          </div>
        </div>
      )}

      {/* 3. Summary Metric Cards (4 Modern Cards) */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Saved Notices */}
        <div
          onClick={() => setActiveTab(9)}
          className="bg-white border border-[#E1E7EE] hover:border-[#08785D] rounded-2xl p-4 sm:p-5 shadow-xs transition hover:shadow-sm cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-[#68778B]">
              {t('summarySavedNotices') || 'Saved Notices'}
            </span>
            <div className="w-8 h-8 rounded-xl bg-[#E8F7F0] text-[#08785D] flex items-center justify-center group-hover:scale-105 transition-transform">
              <BookMarked className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-[#12233D] tracking-tight">
              {savedNotices.length}
            </span>
            <span className="text-xs text-[#526176]">circulars</span>
          </div>
          <div className="mt-2 flex items-center justify-between text-xs text-[#526176]">
            <span>{t('metricInPersonalTracker')}</span>
            <span className="text-[#08785D] font-semibold inline-flex items-center gap-0.5 group-hover:translate-x-0.5 transition-transform">
              {t('historyTitle')} <ChevronRight className="w-3 h-3" />
            </span>
          </div>
        </div>

        {/* Card 2: Pending Actions */}
        <div
          onClick={() => {
            const el = document.getElementById('action-plan-section');
            el?.scrollIntoView({ behavior: 'smooth' });
          }}
          className="bg-white border border-[#E1E7EE] hover:border-[#245DC1] rounded-2xl p-4 sm:p-5 shadow-xs transition hover:shadow-sm cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-[#68778B]">
              {t('summaryPendingActions') || 'Pending Actions'}
            </span>
            <div className="w-8 h-8 rounded-xl bg-[#EAF2FF] text-[#245DC1] flex items-center justify-center group-hover:scale-105 transition-transform">
              <CheckSquare className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-[#12233D] tracking-tight">
              {pendingActionsCount}
            </span>
            <span className="text-xs text-[#526176]">{t('metricTasksPending')}</span>
          </div>
          <div className="mt-2 flex items-center justify-between text-xs text-[#526176]">
            <span>{t('statusAwaitingCompletion')}</span>
            <span className="text-[#245DC1] font-semibold inline-flex items-center gap-0.5 group-hover:translate-x-0.5 transition-transform">
              {t('checklistTitle')} <ChevronRight className="w-3 h-3" />
            </span>
          </div>
        </div>

        {/* Card 3: Upcoming Deadlines */}
        <div
          onClick={() => {
            const el = document.getElementById('upcoming-deadlines-section');
            el?.scrollIntoView({ behavior: 'smooth' });
          }}
          className="bg-white border border-[#E1E7EE] hover:border-amber-400 rounded-2xl p-4 sm:p-5 shadow-xs transition hover:shadow-sm cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-[#68778B]">
              {t('summaryUpcomingDeadlines') || 'Upcoming Deadlines'}
            </span>
            <div className="w-8 h-8 rounded-xl bg-[#FFF4D6] text-[#92500A] flex items-center justify-center group-hover:scale-105 transition-transform">
              <Calendar className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-[#12233D] tracking-tight">
              {upcomingDeadlinesCount}
            </span>
            <span className="text-xs text-[#526176]">{t('metricDueWithinWindow')}</span>
          </div>
          <div className="mt-2 flex items-center justify-between text-xs text-[#526176]">
            <span>{weeklyPlan?.ambiguous_tasks?.length ? `${weeklyPlan.ambiguous_tasks.length} tentative` : 'Dates verified'}</span>
            <span className="text-[#92500A] font-semibold inline-flex items-center gap-0.5 group-hover:translate-x-0.5 transition-transform">
              {t('calendarLink')} <ChevronRight className="w-3 h-3" />
            </span>
          </div>
        </div>

        {/* Card 4: Notifications */}
        <div
          onClick={() => {
            const el = document.getElementById('notification-center-section');
            el?.scrollIntoView({ behavior: 'smooth' });
          }}
          className="bg-white border border-[#E1E7EE] hover:border-purple-400 rounded-2xl p-4 sm:p-5 shadow-xs transition hover:shadow-sm cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-[#68778B]">
              {t('summaryNotifications') || 'Notifications'}
            </span>
            <div className="w-8 h-8 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center group-hover:scale-105 transition-transform">
              <Bell className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-[#12233D] tracking-tight">
              {unreadNotifsCount}
            </span>
            <span className="text-xs text-[#526176]">{t('metricUnread')}</span>
          </div>
          <div className="mt-2 flex items-center justify-between text-xs text-[#526176]">
            <span>{notifications.length} total messages</span>
            <span className="text-purple-600 font-semibold inline-flex items-center gap-0.5 group-hover:translate-x-0.5 transition-transform">
              {t('summaryNotifications')} <ChevronRight className="w-3 h-3" />
            </span>
          </div>
        </div>
      </section>

      {/* Quick Ingest Collapsible Workspace */}
      {isQuickIngestOpen && (
        <section className="bg-white border border-[#E1E7EE] rounded-2xl p-5 sm:p-6 space-y-4 shadow-xs animate-fadeIn">
          <div className="flex items-center justify-between pb-3 border-b border-[#E1E7EE]">
            <div>
              <h2 className="text-sm font-bold text-[#12233D] uppercase tracking-wide flex items-center gap-2">
                <UploadCloud className="w-4 h-4 text-[#08785D]" />
                <span>Quick Notice Ingestion & Ground-Truth Buffer</span>
              </h2>
              <p className="text-xs text-[#526176]">
                Drop or paste any official document to extract verified text and run local Gemma 4 analysis.
              </p>
            </div>
            <button
              type="button"
              onClick={() => setIsQuickIngestOpen(false)}
              className="text-[#526176] hover:text-[#12233D] p-1 rounded-md"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 items-start">
            <div className="space-y-4">
              <FileDropzone />
              {uploadedImage && <OCRPanel />}
            </div>
            <div>
              <NoticeBuffer />
            </div>
          </div>

          <div className="pt-2">
            <button
              type="button"
              onClick={handleDashboardAnalyze}
              disabled={!rawNoticeText.trim() || isAnalyzing}
              className="w-full flex items-center justify-center gap-2 py-3 px-6 rounded-xl font-bold text-xs text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs disabled:opacity-50 cursor-pointer"
            >
              <Sparkles className="w-4 h-4" />
              <span>{isAnalyzing ? (t('analyzingNotice') || 'Analyzing Notice with SuchnaSetu AI...') : (t('analyzeNotice') || 'Analyze Notice with SuchnaSetu AI')}</span>
            </button>
          </div>
        </section>
      )}

      {/* 4. Main Dashboard Responsive Grid (8 Cols Left, 4 Cols Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column (8 of 12 cols): Deadlines, Actions, and Overview */}
        <div className="lg:col-span-8 space-y-6">
          {/* Section A: Upcoming Deadlines & Calendar Radar */}
          <section id="upcoming-deadlines-section" className="bg-white border border-[#E1E7EE] rounded-2xl p-5 sm:p-6 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-[#E1E7EE]">
              <div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-[#08785D]" />
                  <h2 className="text-base font-bold text-[#12233D] tracking-tight">
                    {t('upcomingDeadlinesTitle') || 'Upcoming Deadlines'}
                  </h2>
                </div>
                <p className="text-xs text-[#526176] mt-0.5">
                  {t('upcomingDeadlinesSubtitle') ||
                    'Chronological calendar of deadlines extracted from your notices with grounded evidence.'}
                </p>
              </div>

              {/* Filter Pills */}
              <div className="flex items-center gap-1 bg-[#F8FAFC] border border-[#E1E7EE] p-0.5 rounded-lg text-xs font-semibold">
                <button
                  type="button"
                  onClick={() => setDeadlineFilter('all')}
                  className={`px-2.5 py-1 rounded-md transition cursor-pointer ${
                    deadlineFilter === 'all' ? 'bg-[#08785D] text-white shadow-xs' : 'text-[#526176] hover:text-[#12233D]'
                  }`}
                >
                  All ({combinedTasks.length})
                </button>
                <button
                  type="button"
                  onClick={() => setDeadlineFilter('due_this_week')}
                  className={`px-2.5 py-1 rounded-md transition cursor-pointer ${
                    deadlineFilter === 'due_this_week' ? 'bg-[#08785D] text-white shadow-xs' : 'text-[#526176] hover:text-[#12233D]'
                  }`}
                >
                  This Week ({weeklyPlan?.due_this_week_count || 0})
                </button>
                <button
                  type="button"
                  onClick={() => setDeadlineFilter('tentative')}
                  className={`px-2.5 py-1 rounded-md transition cursor-pointer ${
                    deadlineFilter === 'tentative' ? 'bg-[#08785D] text-white shadow-xs' : 'text-[#526176] hover:text-[#12233D]'
                  }`}
                >
                  Tentative ({weeklyPlan?.ambiguous_tasks?.length || 0})
                </button>
              </div>
            </div>

            {/* Deadlines List */}
            {filteredDeadlines.length === 0 ? (
              <div className="text-center py-8 px-4 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-3">
                <div className="w-12 h-12 rounded-2xl bg-[#FFF4D6] text-[#92500A] flex items-center justify-center mx-auto shadow-2xs">
                  <Calendar className="w-6 h-6" />
                </div>
                <div className="space-y-1">
                  <h3 className="text-xs font-bold text-[#12233D]">
                    {t('noDeadlines') || 'No upcoming deadlines found in your saved notices.'}
                  </h3>
                  <p className="text-[11px] text-[#64748B] max-w-sm mx-auto">
                    Ingest or bookmark official circulars with dates to see your timeline radar populate here.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setActiveTab(1)}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-[#08785D] bg-[#E8F7F0] hover:bg-[#d5f0e3] transition cursor-pointer"
                >
                  <UploadCloud className="w-3.5 h-3.5" />
                  <span>Ingest Notice</span>
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {filteredDeadlines.map((task, idx) => {
                  const isAmbiguous = Boolean(task.is_ambiguous_date);
                  const days = task.days_remaining;
                  const dayBadge =
                    days !== undefined
                      ? days === 0
                        ? { label: t('badgeDueToday'), color: 'bg-red-100 text-red-800 border-red-200' }
                        : days === 1
                        ? { label: t('badgeDueTomorrow'), color: 'bg-amber-100 text-amber-900 border-amber-200' }
                        : days > 1 && days <= 7
                        ? { label: t('badgeDueInDays').replace('{n}', String(days)), color: 'bg-[#E8F7F0] text-[#08785D] border-[#B7E7D2]' }
                        : days < 0
                        ? { label: t('badgeOverdue'), color: 'bg-slate-100 text-slate-700 border-slate-200' }
                        : { label: t('badgeDueInDays').replace('{n}', String(days)), color: 'bg-blue-50 text-blue-800 border-blue-200' }
                      : { label: t('statedDate'), color: 'bg-slate-100 text-slate-700 border-slate-200' };

                  return (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl border border-[#E1E7EE] hover:border-[#CBD5E1] bg-white transition space-y-2"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-[#08785D]">
                              {task.notice_title || 'Official Circular'}
                            </span>
                            <span className={`px-2 py-0.2 rounded text-[10px] font-bold border ${dayBadge.color}`}>
                              {dayBadge.label}
                            </span>
                            {isAmbiguous ? (
                              <span className="px-2 py-0.2 rounded text-[10px] font-bold bg-[#FFF4D6] text-[#92500A] border border-[#FDE68A] flex items-center gap-1">
                                <AlertTriangle className="w-2.5 h-2.5" />
                                {t('tentativeDate') || 'Tentative / Unconfirmed'}
                              </span>
                            ) : (
                              <span className="px-2 py-0.2 rounded text-[10px] font-bold bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2] flex items-center gap-1">
                                <ShieldCheck className="w-2.5 h-2.5" />
                                {t('statedDate') || 'Stated (Verified)'}
                              </span>
                            )}
                          </div>
                          <h4 className="text-xs sm:text-sm font-bold text-[#12233D]">{task.task_title}</h4>
                        </div>
                        <div className="text-right shrink-0">
                          <div className="text-xs font-mono font-bold text-[#12233D]">
                            {task.parsed_date || task.raw_deadline || 'Per notice schedule'}
                          </div>
                          {task.authority && (
                            <div className="text-[10px] text-[#64748B]">{task.authority}</div>
                          )}
                        </div>
                      </div>

                      {/* Evidence citation or ambiguity note */}
                      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pt-1.5 border-t border-slate-100 text-[11px]">
                        <div className="text-[#64748B] italic font-mono truncate max-w-md">
                          "{task.raw_line?.slice(0, 90) || task.task_title}..."
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <button
                            type="button"
                            onClick={() =>
                              openEvidenceInspector(
                                {
                                  excerpt: task.raw_line || task.task_title,
                                  claim: task.task_title,
                                  docTitle: task.notice_title,
                                },
                                task.raw_line
                              )
                            }
                            className="text-[11px] font-semibold text-[#08785D] hover:underline inline-flex items-center gap-1 cursor-pointer"
                          >
                            <FileSearch className="w-3 h-3" />
                            <span>{t('viewEvidence') || 'Inspect Quote'}</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          {/* Section B: Interactive Action Plan & Checklist */}
          <section id="action-plan-section" className="bg-white border border-[#E1E7EE] rounded-2xl p-5 sm:p-6 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-[#E1E7EE]">
              <div>
                <div className="flex items-center gap-2">
                  <CheckSquare className="w-4 h-4 text-[#245DC1]" />
                  <h2 className="text-base font-bold text-[#12233D] tracking-tight">
                    {t('actionPlanWidgetTitle') || 'Action Plan & Checklist'}
                  </h2>
                </div>
                <p className="text-xs text-[#526176] mt-0.5">
                  {t('actionPlanWidgetSubtitle') ||
                    'Personalized task sequence across your notices with one-click completion tracking.'}
                </p>
              </div>

              {/* Action Filter Pills */}
              <div className="flex items-center gap-1 bg-[#F8FAFC] border border-[#E1E7EE] p-0.5 rounded-lg text-xs font-semibold">
                <button
                  type="button"
                  onClick={() => setActionFilter('all')}
                  className={`px-2.5 py-1 rounded-md transition cursor-pointer ${
                    actionFilter === 'all' ? 'bg-[#245DC1] text-white shadow-xs' : 'text-[#526176] hover:text-[#12233D]'
                  }`}
                >
                  All ({combinedTasks.length})
                </button>
                <button
                  type="button"
                  onClick={() => setActionFilter('pending')}
                  className={`px-2.5 py-1 rounded-md transition cursor-pointer ${
                    actionFilter === 'pending' ? 'bg-[#245DC1] text-white shadow-xs' : 'text-[#526176] hover:text-[#12233D]'
                  }`}
                >
                  Pending ({pendingActionsCount})
                </button>
                <button
                  type="button"
                  onClick={() => setActionFilter('completed')}
                  className={`px-2.5 py-1 rounded-md transition cursor-pointer ${
                    actionFilter === 'completed' ? 'bg-[#245DC1] text-white shadow-xs' : 'text-[#526176] hover:text-[#12233D]'
                  }`}
                >
                  Completed ({combinedTasks.length - pendingActionsCount})
                </button>
              </div>
            </div>

            {/* Checklist List */}
            {filteredActions.length === 0 ? (
              <div className="text-center py-8 px-4 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-3">
                <div className="w-12 h-12 rounded-2xl bg-[#EAF2FF] text-[#245DC1] flex items-center justify-center mx-auto shadow-2xs">
                  <CheckSquare className="w-6 h-6" />
                </div>
                <div className="space-y-1">
                  <h3 className="text-xs font-bold text-[#12233D]">
                    {t('noPendingActions') || 'No pending actions right now. All tasks are completed!'}
                  </h3>
                  <p className="text-[11px] text-[#64748B] max-w-sm mx-auto">
                    Ingest an official circular to automatically synthesize step-by-step citizen action items.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleLoadDemo}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-[#245DC1] bg-[#EAF2FF] hover:bg-[#d8e6fd] transition cursor-pointer"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Load Demo Notice</span>
                </button>
              </div>
            ) : (
              <div className="space-y-2.5">
                {filteredActions.map((task, idx) => {
                  const taskId = task.id || `task_${idx}`;
                  const isDone = completedTaskIds[taskId] ?? false;

                  return (
                    <div
                      key={taskId}
                      className={`flex items-start gap-3 p-3 rounded-xl border transition ${
                        isDone
                          ? 'bg-[#F8FAFC] border-[#E1E7EE] opacity-60'
                          : 'bg-white border-[#E1E7EE] hover:border-[#CBD5E1]'
                      }`}
                    >
                      <button
                        type="button"
                        onClick={() => handleToggleTask(taskId, isDone)}
                        className={`w-5 h-5 rounded-md border flex items-center justify-center shrink-0 mt-0.5 transition cursor-pointer ${
                          isDone
                            ? 'bg-[#08785D] border-[#08785D] text-white'
                            : 'border-[#CBD5E1] hover:border-[#08785D] bg-white'
                        }`}
                        aria-label={`Mark task ${task.task_title} as ${isDone ? 'incomplete' : 'completed'}`}
                      >
                        {isDone && <CheckCircle2 className="w-3.5 h-3.5 text-white" />}
                      </button>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2">
                          <span
                            className={`text-xs font-bold ${
                              isDone ? 'line-through text-[#64748B]' : 'text-[#12233D]'
                            }`}
                          >
                            {task.task_title}
                          </span>
                          <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-slate-100 text-[#526176] shrink-0">
                            {task.parsed_date || task.raw_deadline || 'Standard Step'}
                          </span>
                        </div>
                        <p className="text-[11px] text-[#64748B] mt-0.5 truncate">
                          Source: {task.notice_title}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          {/* Section C: Methodology & How It Works (Preserved) */}
          <section className="bg-white border border-[#E1E7EE] rounded-2xl p-5 sm:p-6 space-y-4 shadow-xs">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#08785D] block mb-0.5">
                Methodology
              </span>
              <h3 className="text-base font-bold text-[#12233D]">{t('methodologyHeading')}</h3>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-1">
                <span className="w-6 h-6 rounded-md bg-[#E8F7F0] text-[#08785D] font-bold text-[11px] flex items-center justify-center">01</span>
                <h4 className="text-xs font-bold text-[#12233D]">{t('methodologyStep1Title')}</h4>
                <p className="text-[11px] text-[#526176] leading-relaxed">{t('methodologyStep1Desc')}</p>
              </div>
              <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-1">
                <span className="w-6 h-6 rounded-md bg-[#E8F7F0] text-[#08785D] font-bold text-[11px] flex items-center justify-center">02</span>
                <h4 className="text-xs font-bold text-[#12233D]">{t('methodologyStep3Title')}</h4>
                <p className="text-[11px] text-[#526176] leading-relaxed">{t('methodologyStep3Desc')}</p>
              </div>
              <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-1">
                <span className="w-6 h-6 rounded-md bg-[#E8F7F0] text-[#08785D] font-bold text-[11px] flex items-center justify-center">03</span>
                <h4 className="text-xs font-bold text-[#12233D]">{t('methodologyStep2Title')}</h4>
                <p className="text-[11px] text-[#526176] leading-relaxed">{t('methodologyStep2Desc')}</p>
              </div>
              <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-1">
                <span className="w-6 h-6 rounded-md bg-[#E8F7F0] text-[#08785D] font-bold text-[11px] flex items-center justify-center">04</span>
                <h4 className="text-xs font-bold text-[#12233D]">{t('methodologyStep4Title')}</h4>
                <p className="text-[11px] text-[#526176] leading-relaxed">{t('methodologyStep4Desc')}</p>
              </div>
            </div>
          </section>
        </div>

        {/* Right Column (4 of 12 cols): Notification Center, Recent Notices, and Timeline */}
        <div className="lg:col-span-4 space-y-6">
          {/* Section D: Notification Center */}
          <section id="notification-center-section" className="bg-white border border-[#E1E7EE] rounded-2xl p-5 shadow-xs space-y-3.5">
            <div className="flex items-center justify-between pb-2.5 border-b border-[#E1E7EE]">
              <div className="flex items-center gap-2">
                <Bell className="w-4 h-4 text-purple-600" />
                <h3 className="text-xs font-bold text-[#12233D] uppercase tracking-wider">
                  {t('notificationCenterTitle') || 'Notification Center'}
                </h3>
              </div>
              {unreadNotifsCount > 0 && (
                <button
                  type="button"
                  onClick={handleMarkAllRead}
                  className="text-[10px] font-bold text-purple-700 hover:text-purple-900 cursor-pointer"
                >
                  {t('markAllRead') || 'Mark all read'}
                </button>
              )}
            </div>

            {notifications.length === 0 ? (
              <div className="text-center py-6 px-3 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-2.5">
                <div className="w-10 h-10 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center mx-auto shadow-2xs">
                  <Bell className="w-5 h-5" />
                </div>
                <div className="space-y-0.5">
                  <div className="text-xs font-bold text-[#12233D]">
                    {t('noNotifications') || 'No new notifications.'}
                  </div>
                  <p className="text-[10px] text-[#64748B]">
                    Impending deadlines and notice alerts will appear here.
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
                {notifications.map((n) => {
                  const typeIcon =
                    n.type === 'deadline' ? (
                      <Clock className="w-3.5 h-3.5 text-amber-600" />
                    ) : n.type === 'warning' ? (
                      <AlertTriangle className="w-3.5 h-3.5 text-red-600" />
                    ) : (
                      <Info className="w-3.5 h-3.5 text-blue-600" />
                    );

                  return (
                    <div
                      key={n.id}
                      onClick={() => handleNotificationClick(n)}
                      className={`p-3 rounded-xl border transition cursor-pointer relative group ${
                        n.is_read
                          ? 'bg-[#F8FAFC] border-[#E1E7EE]'
                          : 'bg-purple-50/40 border-purple-200'
                      }`}
                    >
                      <div className="flex items-start gap-2.5">
                        <div className="mt-0.5 shrink-0">{typeIcon}</div>
                        <div className="flex-1 min-w-0 pr-4">
                          <div className="flex items-center gap-1.5">
                            <h5 className="text-xs font-bold text-[#12233D] truncate">{n.title}</h5>
                            {!n.is_read && <span className="w-1.5 h-1.5 rounded-full bg-purple-600 shrink-0" />}
                          </div>
                          <p className="text-[11px] text-[#526176] mt-0.5 leading-relaxed">{n.message}</p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={(e) => handleDismissNotification(n.id, e)}
                        className="absolute right-2 top-2 p-1 text-[#94A3B8] hover:text-[#12233D] rounded hover:bg-slate-200/60 opacity-0 group-hover:opacity-100 transition cursor-pointer"
                        title={t('dismiss') || 'Dismiss'}
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          {/* Section E: Recent Notices */}
          <section className="bg-white border border-[#E1E7EE] rounded-2xl p-5 shadow-xs space-y-3.5">
            <div className="flex items-center justify-between pb-2.5 border-b border-[#E1E7EE]">
              <div className="flex items-center gap-2">
                <BookMarked className="w-4 h-4 text-[#08785D]" />
                <h3 className="text-xs font-bold text-[#12233D] uppercase tracking-wider">
                  {t('recentNoticesTitle') || 'Recent Notices'}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setActiveTab(9)}
                className="text-[10px] font-bold text-[#08785D] hover:underline cursor-pointer"
              >
                View all ({savedNotices.length})
              </button>
            </div>

            {savedNotices.length === 0 ? (
              <div className="text-center py-6 px-3 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-2.5">
                <div className="w-10 h-10 rounded-2xl bg-[#E8F7F0] text-[#08785D] flex items-center justify-center mx-auto shadow-2xs">
                  <BookMarked className="w-5 h-5" />
                </div>
                <div className="text-xs font-bold text-[#12233D]">
                  {t('noRecentNotices') || 'No saved notices yet.'}
                </div>
                <p className="text-[11px] text-[#64748B] max-w-xs mx-auto leading-relaxed">
                  Start by uploading your first official notice or explore the 32 real-world government circulars in the Demo Library.
                </p>
                <div className="flex items-center justify-center gap-2 pt-1">
                  <button
                    type="button"
                    onClick={() => setActiveTab(1)}
                    className="px-2.5 py-1 text-xs font-semibold text-white bg-[#08785D] hover:bg-[#06664E] rounded-lg shadow-2xs transition cursor-pointer"
                  >
                    Upload Notice
                  </button>
                  <button
                    type="button"
                    onClick={() => setActiveTab(11)}
                    className="px-2.5 py-1 text-xs font-semibold text-[#12233D] bg-white hover:bg-[#E8F7F0] hover:text-[#08785D] border border-[#CBD5E1] rounded-lg transition cursor-pointer"
                  >
                    Explore 32 Demos
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-2.5">
                {savedNotices.slice(0, 4).map((notice) => (
                  <div
                    key={notice.document_id}
                    className="p-3 rounded-xl border border-[#E1E7EE] hover:border-[#CBD5E1] bg-white transition space-y-2"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="text-[10px] font-bold text-[#08785D] uppercase tracking-wide block">
                          {notice.authority || 'Government Authority'}
                        </span>
                        <h4 className="text-xs font-bold text-[#12233D] line-clamp-1">{notice.title}</h4>
                      </div>
                      <button
                        type="button"
                        onClick={(e) => handleUnsaveNotice(notice.document_id, e)}
                        className="text-[#94A3B8] hover:text-red-600 p-1 rounded cursor-pointer"
                        title="Remove bookmark"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>

                    <div className="flex items-center justify-between text-[11px] pt-1 border-t border-slate-100">
                      <span className="text-[#64748B]">
                        {notice.deadline ? `Deadline: ${notice.deadline}` : 'Standard circular'}
                      </span>
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => handleViewNoticeEvidence(notice)}
                          className="font-semibold text-[#08785D] hover:underline cursor-pointer"
                        >
                          Evidence
                        </button>
                        <span>•</span>
                        <button
                          type="button"
                          onClick={() => handleOpenNoticeInWorkspace(notice)}
                          className="font-semibold text-[#12233D] hover:text-[#08785D] cursor-pointer"
                        >
                          Open
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Section F: Account Activity Audit Trail */}
          <section className="bg-white border border-[#E1E7EE] rounded-2xl p-5 shadow-xs space-y-3.5">
            <div className="flex items-center gap-2 pb-2.5 border-b border-[#E1E7EE]">
              <Clock className="w-4 h-4 text-[#526176]" />
              <h3 className="text-xs font-bold text-[#12233D] uppercase tracking-wider">
                {t('activityTimelineTitle') || 'Activity Timeline'}
              </h3>
            </div>

            {activities.length === 0 ? (
              <div className="text-center py-6 px-3 rounded-xl bg-[#F8FAFC] border border-[#E1E7EE] space-y-2.5">
                <div className="w-10 h-10 rounded-2xl bg-slate-100 text-[#526176] flex items-center justify-center mx-auto shadow-2xs">
                  <Clock className="w-5 h-5" />
                </div>
                <div className="text-xs font-bold text-[#12233D]">
                  {t('noRecentActivities') || 'No recent activity yet.'}
                </div>
                <p className="text-[10px] text-[#64748B]">
                  Your analyses, saved notices, and exports will generate an audit trail here.
                </p>
              </div>
            ) : (
              <div className="space-y-3 relative pl-3 before:absolute before:left-1 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                {activities.slice(0, 5).map((act) => (
                  <div key={act.id} className="relative pl-3 space-y-0.5 text-xs">
                    <span className="absolute -left-3 top-1 w-2 h-2 rounded-full bg-[#08785D] ring-2 ring-white" />
                    <div className="font-bold text-[#12233D]">{act.title}</div>
                    <div className="text-[11px] text-[#64748B]">{act.description}</div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>

      {/* 5. Frequently Asked Questions (Preserved) */}
      <section className="bg-white border border-[#E1E7EE] rounded-2xl p-5 sm:p-7 space-y-4 shadow-xs">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-[#08785D] block mb-0.5">
            {t('faqSectionBadge') || 'Questions'}
          </span>
          <h2 className="text-base font-bold text-[#12233D] tracking-tight">
            {t('faqSectionTitle') || 'Frequently Asked Questions'}
          </h2>
        </div>

        <div className="space-y-2">
          {faqs.map((faq, index) => {
            const isExpanded = expandedFaq === index;
            return (
              <div key={index} className="border border-[#E1E7EE] rounded-xl overflow-hidden transition">
                <button
                  type="button"
                  onClick={() => setExpandedFaq(isExpanded ? null : index)}
                  className="w-full flex items-center justify-between p-3.5 text-left font-semibold text-xs text-[#12233D] hover:bg-[#F8FAFC] cursor-pointer"
                >
                  <span>{faq.q}</span>
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4 text-[#08785D] shrink-0" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-[#68778B] shrink-0" />
                  )}
                </button>
                {isExpanded && (
                  <div className="px-3.5 pb-3.5 pt-1 text-xs text-[#526176] leading-relaxed bg-[#F8FAFC] border-t border-[#E1E7EE]">
                    {faq.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* Footer */}
      <footer className="pt-4 border-t border-[#E1E7EE] text-center space-y-2 text-xs text-[#68778B]">
        <div className="flex items-center justify-center gap-4 text-xs font-medium text-[#526176]">
          <button type="button" onClick={() => setActiveTab(10)} className="hover:text-[#08785D] cursor-pointer">
            Settings & Diagnostics
          </button>
          <span>•</span>
          <button type="button" onClick={() => setActiveTab(1)} className="hover:text-[#08785D] cursor-pointer">
            Notice Workspace
          </button>
          <span>•</span>
          <button type="button" onClick={() => setActiveTab(4)} className="hover:text-[#08785D] cursor-pointer">
            Revision Ledger
          </button>
        </div>
        <p className="text-[11px]">
          SuchnaSetu AI • HackDay 2026 PS02 • Open, Grounded, Accessible Civic Technology
        </p>
      </footer>
    </div>
  );
};
