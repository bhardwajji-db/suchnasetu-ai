import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DashboardView } from '../views/DashboardView';
import { NoticeProvider } from '../context/NoticeContext';
import { I18nProvider } from '../i18n';
import { apiClient } from '../services/apiClient';
import * as authService from '../services/api';
import React from 'react';

const mockSavedNotices = [
  {
    document_id: 'doc_scholarship_1',
    title: 'Merit Scholarship Circular 2026',
    authority: 'Ministry of Education',
    deadline: '31 October 2026',
    raw_text: 'Official Merit Scholarship Scheme 2026 circular text.',
    created_at: 1729850000,
  },
  {
    document_id: 'doc_recruitment_2',
    title: 'NCL Junior Engineer Recruitment',
    authority: 'Northern Coalfields Limited',
    deadline: '15 November 2026',
    raw_text: 'Northern Coalfields Limited employment notification.',
    created_at: 1729860000,
  },
];

const mockWeeklyTasks = {
  due_this_week: [
    {
      task_title: 'Submit Online Application Form',
      raw_line: 'Submit Online Application Form on portal before 31 Oct',
      parsed_date: '2026-10-31',
      raw_deadline: '31 October 2026',
      is_ambiguous_date: false,
      ambiguity_reason: 'Confirmed exact deadline.',
      notice_title: 'Merit Scholarship Circular 2026',
      document_id: 'doc_scholarship_1',
      days_remaining: 3,
      status: 'DUE_THIS_WEEK',
      urgency: 'UPCOMING',
    },
  ],
  due_this_week_count: 1,
  upcoming_later: [],
  past_due: [],
  ambiguous_tasks: [
    {
      task_title: 'Document Verification Date',
      raw_line: 'Tentative date for verification will be announced',
      parsed_date: null,
      raw_deadline: 'Tentative late November',
      is_ambiguous_date: true,
      ambiguity_reason: 'Date is tentative or subject to confirmation.',
      notice_title: 'NCL Junior Engineer Recruitment',
      document_id: 'doc_recruitment_2',
      status: 'AMBIGUOUS',
    },
  ],
  total_saved_notices: 2,
  summary: 'You have 1 task due this week.',
};

const mockNotifications = {
  notifications: [
    {
      id: 'notif_1',
      user_id: 'u1',
      title: 'Upcoming Deadline This Week',
      message: 'Submit Online Application Form is due soon.',
      type: 'deadline' as const,
      document_id: 'doc_scholarship_1',
      is_read: false,
      is_dismissed: false,
      created_at: 1729870000,
    },
  ],
  unread_count: 1,
  total: 1,
};

const mockActivities = [
  {
    id: 'act_1',
    user_id: 'u1',
    activity_type: 'notice_analyzed',
    title: 'Analyzed Notice: Merit Scholarship',
    description: 'Extracted grounded facts and 4 action items.',
    document_id: 'doc_scholarship_1',
    created_at: 1729870100,
  },
];

const mockUser = {
  id: 'u1',
  email: 'citizen@example.gov.in',
  name: 'Dev Citizen',
  is_verified: true,
  created_at: '2026-10-25T00:00:00Z',
};

describe('DashboardView Upgraded Redesign Component', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    vi.spyOn(authService, 'fetchAuthMe').mockResolvedValue(mockUser);
    vi.spyOn(apiClient, 'getSavedNotices').mockResolvedValue(mockSavedNotices);
    vi.spyOn(apiClient, 'getWeeklyTasks').mockResolvedValue(mockWeeklyTasks);
    vi.spyOn(apiClient, 'getUserNotifications').mockResolvedValue(mockNotifications);
    vi.spyOn(apiClient, 'getUserActivities').mockResolvedValue(mockActivities);
    vi.spyOn(apiClient, 'toggleChecklistItemPersistent').mockResolvedValue({
      success: true,
      item_id: 'task_0',
      is_completed: true,
    });
    vi.spyOn(apiClient, 'markAllNotificationsRead').mockResolvedValue({
      status: 'success',
      marked_read: 1,
    });
    vi.spyOn(apiClient, 'dismissNotification').mockResolvedValue({
      status: 'success',
      dismissed: true,
    });
    vi.spyOn(apiClient, 'getHealth').mockResolvedValue({
      overall_status: 'ok',
      active_provider: 'ollama',
    } as any);
    vi.spyOn(apiClient, 'getProviders').mockResolvedValue([]);
    vi.spyOn(apiClient, 'getSamples').mockResolvedValue([]);
  });

  it('renders welcome banner and 4 summary metric cards with real data', async () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <DashboardView />
        </NoticeProvider>
      </I18nProvider>
    );

    // Welcome banner
    await waitFor(() => {
      expect(screen.getByText(/Welcome back, Dev Citizen/i)).toBeInTheDocument();
    });

    // 4 Summary Metric Cards
    expect(screen.getByText(/Saved Notices/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Pending Actions/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Upcoming Deadlines/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Notifications/i).length).toBeGreaterThan(0);

    // Verify metric counts (at least one metric has count 2)
    expect(screen.getAllByText('2').length).toBeGreaterThan(0);
  });

  it('renders upcoming deadlines with verified evidence badges and tentative warnings', async () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <DashboardView />
        </NoticeProvider>
      </I18nProvider>
    );

    await waitFor(() => {
      const taskMatches = screen.getAllByText(/Submit Online Application Form/i);
      expect(taskMatches.length).toBeGreaterThan(0);
    });

    // Verified badge
    expect(screen.getAllByText(/Stated \(Verified\)/i).length).toBeGreaterThan(0);

    // Ambiguous task with tentative badge
    expect(screen.getAllByText(/Document Verification Date/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Tentative Date|Tentative \/ Unconfirmed/i).length).toBeGreaterThan(0);
  });

  it('renders action plan and allows interactive task completion toggling', async () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <DashboardView />
        </NoticeProvider>
      </I18nProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Action Plan & Checklist/i)).toBeInTheDocument();
    });

    const checkboxes = screen.getAllByRole('button', { name: /Mark task/i });
    expect(checkboxes.length).toBeGreaterThan(0);

    // Toggle task
    fireEvent.click(checkboxes[0]);
    await waitFor(() => {
      expect(apiClient.toggleChecklistItemPersistent).toHaveBeenCalled();
    });
  });

  it('renders notification center with unread message and supports mark all read and dismiss', async () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <DashboardView />
        </NoticeProvider>
      </I18nProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Notification Center/i)).toBeInTheDocument();
      expect(screen.getByText(/Upcoming Deadline This Week/i)).toBeInTheDocument();
    });

    // Mark all read button
    const markAllReadBtn = screen.getByText(/Mark all read/i);
    fireEvent.click(markAllReadBtn);
    await waitFor(() => {
      expect(apiClient.markAllNotificationsRead).toHaveBeenCalled();
    });

    // Dismiss notification button
    const dismissBtn = screen.getByTitle(/Dismiss/i);
    fireEvent.click(dismissBtn);
    await waitFor(() => {
      expect(apiClient.dismissNotification).toHaveBeenCalledWith('notif_1');
    });
  });

  it('renders activity audit timeline and recent notices', async () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <DashboardView />
        </NoticeProvider>
      </I18nProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Account Activity Audit Trail|Activity Timeline/i)).toBeInTheDocument();
      expect(screen.getByText(/Analyzed Notice: Merit Scholarship/i)).toBeInTheDocument();
      expect(screen.getByText(/Recent Notices/i)).toBeInTheDocument();
    });
  });

  it('renders clean empty states when user is new with no saved notices', async () => {
    vi.spyOn(apiClient, 'getSavedNotices').mockResolvedValue([]);
    vi.spyOn(apiClient, 'getWeeklyTasks').mockResolvedValue({
      due_this_week: [],
      due_this_week_count: 0,
      upcoming_later: [],
      past_due: [],
      ambiguous_tasks: [],
      total_saved_notices: 0,
    });
    vi.spyOn(apiClient, 'getUserNotifications').mockResolvedValue({
      notifications: [],
      unread_count: 0,
      total: 0,
    });
    vi.spyOn(apiClient, 'getUserActivities').mockResolvedValue([]);

    render(
      <I18nProvider>
        <NoticeProvider>
          <DashboardView />
        </NoticeProvider>
      </I18nProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/No upcoming deadlines found in your saved notices/i)).toBeInTheDocument();
      expect(screen.getByText(/No saved notices yet/i)).toBeInTheDocument();
      expect(screen.getByText(/No recent activity yet/i)).toBeInTheDocument();
      expect(screen.getByText(/No new notifications/i)).toBeInTheDocument();
    });
  });
});
