import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { NoticeProvider, useNotice } from '../context/NoticeContext';
import { Header } from '../components/Header';
import { Sidebar } from '../components/Sidebar';
import { MobileBottomNav } from '../components/MobileBottomNav';

const TestApp: React.FC = () => {
  const { activeTab } = useNotice();
  return (
    <div>
      <Header />
      <Sidebar />
      <MobileBottomNav />
      <div data-testid="active-tab-indicator">Active Tab: {activeTab}</div>
    </div>
  );
};

describe('Mobile Navigation & Responsive Drawer', () => {
  it('renders mobile bottom navigation bar with key tabs', () => {
    render(
      <NoticeProvider>
        <TestApp />
      </NoticeProvider>
    );

    expect(screen.getByLabelText('Mobile Bottom Navigation')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Home' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Ingest' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Facts' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Actions' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Open full tool menu' })).toBeInTheDocument();
  });

  it('switches active tab when mobile bottom navigation button is clicked', () => {
    render(
      <NoticeProvider>
        <TestApp />
      </NoticeProvider>
    );

    const ingestBtn = screen.getByRole('button', { name: 'Ingest' });
    fireEvent.click(ingestBtn);

    expect(screen.getByTestId('active-tab-indicator')).toHaveTextContent('Active Tab: 1');
  });

  it('toggles mobile slide-over drawer when hamburger button is clicked', () => {
    render(
      <NoticeProvider>
        <TestApp />
      </NoticeProvider>
    );

    const hamburgerBtn = screen.getByTitle('Open navigation drawer');
    fireEvent.click(hamburgerBtn);

    // Slide-over drawer should now be open
    const drawer = screen.getByRole('dialog', { name: 'Navigation Drawer' });
    expect(drawer).toBeInTheDocument();

    // Close button inside drawer
    const closeBtn = screen.getByLabelText('Dismiss navigation drawer');
    expect(closeBtn).toBeInTheDocument();
    fireEvent.click(closeBtn);

    // Slide-over drawer should now be closed
    expect(screen.queryByRole('dialog', { name: 'Navigation Drawer' })).not.toBeInTheDocument();
  });
});
