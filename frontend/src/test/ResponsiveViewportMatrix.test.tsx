import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { I18nProvider } from '../i18n';
import { NoticeProvider } from '../context/NoticeContext';
import { ApplicationLayout } from '../components/ApplicationLayout';

const VIEWPORTS = [
  { name: 'Small phone', width: 320, height: 568, isMobile: true },
  { name: 'Typical phone', width: 360, height: 800, isMobile: true },
  { name: 'Modern phone', width: 390, height: 844, isMobile: true },
  { name: 'Large phone', width: 430, height: 932, isMobile: true },
  { name: 'Tablet portrait', width: 768, height: 1024, isMobile: false },
  { name: 'Tablet landscape', width: 1024, height: 768, isMobile: false },
  { name: 'Laptop', width: 1366, height: 768, isMobile: false },
  { name: 'Desktop', width: 1920, height: 1080, isMobile: false },
];

describe('Responsive Viewport Matrix Verification', () => {
  for (const vp of VIEWPORTS) {
    it(`renders flawlessly on ${vp.name} (${vp.width}x${vp.height})`, () => {
      // Set viewport dimensions
      act(() => {
        window.innerWidth = vp.width;
        window.innerHeight = vp.height;
        window.dispatchEvent(new Event('resize'));
      });

      const { container } = render(
        <I18nProvider>
          <NoticeProvider>
            <ApplicationLayout />
          </NoticeProvider>
        </I18nProvider>
      );

      // Verify the main container is rendered and has no overflow breaking classes
      const rootLayout = container.querySelector('.min-h-screen');
      expect(rootLayout).toBeInTheDocument();
      expect(rootLayout).toHaveClass('overflow-x-hidden');

      // Verify header branding
      expect(screen.getAllByText(/Suchna/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/PS02/i).length).toBeGreaterThan(0);

      // Verify mobile bottom navigation is rendered in the DOM
      const bottomNav = screen.getByLabelText('Mobile Bottom Navigation');
      expect(bottomNav).toBeInTheDocument();
      expect(bottomNav).toHaveClass('md:hidden');

      // Verify mobile hamburger drawer button exists
      const hamburger = screen.getByTitle(/Open navigation drawer/i);
      expect(hamburger).toBeInTheDocument();
      expect(hamburger).toHaveClass('md:hidden');

      // Toggle drawer on mobile
      if (vp.isMobile) {
        act(() => {
          fireEvent.click(hamburger);
        });

        // Drawer dialog should be open
        const drawer = screen.getByRole('dialog', { name: 'Navigation Drawer' });
        expect(drawer).toBeInTheDocument();

        // Dismiss drawer
        const dismissBtn = screen.getByLabelText('Dismiss navigation drawer');
        act(() => {
          fireEvent.click(dismissBtn);
        });
        expect(screen.queryByRole('dialog', { name: 'Navigation Drawer' })).not.toBeInTheDocument();
      }
    });
  }
});
