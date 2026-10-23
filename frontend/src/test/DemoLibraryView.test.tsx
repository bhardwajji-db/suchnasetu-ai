import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { DemoLibraryView } from '../views/DemoLibraryView';
import { NoticeProvider } from '../context/NoticeContext';
import { I18nProvider } from '../i18n';
import { apiClient } from '../services/apiClient';

describe('DemoLibraryView Component', () => {
  it('renders demo library view with search and filter controls', async () => {
    vi.spyOn(apiClient, 'getDemoLibrary').mockResolvedValue({
      demos: [
        {
          id: 'demo_01_en',
          title: 'AICTE PG Scholarship 2026',
          language: 'en',
          format: 'txt',
          category: 'scholarship',
          description: 'Official AICTE post-graduate scholarship notification.',
          file_path: 'tests/fixtures/demo_library/demo_01_en.txt',
          word_count: 245,
        },
        {
          id: 'demo_04_hi',
          title: 'राष्ट्रीय छात्रवृत्ति पोर्टल दिशा-निर्देश',
          language: 'hi',
          format: 'txt',
          category: 'scholarship',
          description: 'छात्रवृत्ति आवेदन दिशा-निर्देश।',
          file_path: 'tests/fixtures/demo_library/demo_04_hi.txt',
          word_count: 230,
        },
      ],
      total: 2,
    });

    render(
      <I18nProvider>
        <NoticeProvider>
          <DemoLibraryView />
        </NoticeProvider>
      </I18nProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/AICTE PG Scholarship 2026/i)).toBeInTheDocument();
      expect(screen.getByText(/राष्ट्रीय छात्रवृत्ति पोर्टल दिशा-निर्देश/i)).toBeInTheDocument();
    });

    expect(screen.getByPlaceholderText(/Search title, category, keywords.../i)).toBeInTheDocument();
    expect(screen.getByText(/All Languages/i)).toBeInTheDocument();
  });
});
