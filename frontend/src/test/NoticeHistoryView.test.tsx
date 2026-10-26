import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { NoticeHistoryView } from '../views/NoticeHistoryView';
import { NoticeProvider } from '../context/NoticeContext';
import { I18nProvider } from '../i18n';
import { apiClient } from '../services/apiClient';
import React from 'react';

const mockSavedNotices = [
  {
    document_id: 'doc_scholarship_1',
    title: 'Merit Scholarship Circular 2026',
    authority: 'Ministry of Education',
    deadline: '31 October 2026',
    raw_text: 'Official Merit Scholarship Scheme 2026 circular text.',
    created_at: '2026-10-20T10:00:00Z',
  },
  {
    document_id: 'doc_recruitment_2',
    title: 'NCL Junior Engineer Recruitment',
    authority: 'Northern Coalfields Limited',
    deadline: '15 November 2026',
    raw_text: 'Northern Coalfields Limited employment notification.',
    created_at: '2026-10-21T11:00:00Z',
  },
];

describe('NoticeHistoryView Component', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    vi.spyOn(apiClient, 'getSavedNotices').mockResolvedValue(mockSavedNotices);
    vi.spyOn(apiClient, 'getHealth').mockResolvedValue({ status: 'ok', active_provider: 'ollama' } as any);
    vi.spyOn(apiClient, 'getProviders').mockResolvedValue([]);
    vi.spyOn(apiClient, 'getSamples').mockResolvedValue([]);
  });

  it('renders history view header, search input, and weekly action button', async () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <NoticeHistoryView />
        </NoticeProvider>
      </I18nProvider>
    );

    expect(screen.getByText(/Saved Notices & Weekly Action Planner/i)).toBeInTheDocument();
    expect(screen.getByText(/What do I need to complete this week\?/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Search by subject/i)).toBeInTheDocument();
    });
  });

  it('hydrates saved notices from backend into view', async () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <NoticeHistoryView />
        </NoticeProvider>
      </I18nProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Merit Scholarship Circular 2026/i)).toBeInTheDocument();
      expect(screen.getByText(/NCL Junior Engineer Recruitment/i)).toBeInTheDocument();
    });
  });

  it('filters notices based on search query', async () => {
    render(
      <I18nProvider>
        <NoticeProvider>
          <NoticeHistoryView />
        </NoticeProvider>
      </I18nProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Merit Scholarship Circular 2026/i)).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/Search by subject/i);
    fireEvent.change(searchInput, { target: { value: 'Coalfields' } });

    expect(screen.queryByText(/Merit Scholarship Circular 2026/i)).not.toBeInTheDocument();
    expect(screen.getByText(/NCL Junior Engineer Recruitment/i)).toBeInTheDocument();
  });

  it('handles weekly task action plan query trigger', async () => {
    vi.spyOn(apiClient, 'queryWeeklyTasks').mockResolvedValue({
      summary: 'You have 1 priority task due this week: NCL application deadline.',
      due_this_week_count: 1,
      tasks: [
        {
          task_title: 'Submit NCL Online Form',
          raw_deadline: '15 Nov 2026',
          parsed_date: '2026-11-15',
          urgency: 'CRITICAL',
          notice_title: 'NCL Junior Engineer Recruitment',
        },
      ],
      week_window: {
        start_date: '2026-10-26',
        end_date: '2026-11-02',
      },
    });

    render(
      <I18nProvider>
        <NoticeProvider>
          <NoticeHistoryView />
        </NoticeProvider>
      </I18nProvider>
    );

    const weeklyBtn = screen.getByText(/What do I need to complete this week\?/i);
    fireEvent.click(weeklyBtn);

    await waitFor(() => {
      expect(screen.getByText(/Weekly Action Schedule/i)).toBeInTheDocument();
      expect(screen.getByText(/You have 1 priority task due this week/i)).toBeInTheDocument();
      expect(screen.getByText(/Submit NCL Online Form/i)).toBeInTheDocument();
    });
  });
});
