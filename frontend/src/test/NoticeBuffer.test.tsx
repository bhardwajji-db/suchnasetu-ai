import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { NoticeBuffer } from '../components/NoticeBuffer';
import { NoticeProvider } from '../context/NoticeContext';

describe('NoticeBuffer Component', () => {
  it('renders buffer textarea and handles text input', () => {
    render(
      <NoticeProvider>
        <NoticeBuffer />
      </NoticeProvider>
    );

    const textarea = screen.getByPlaceholderText(/Paste official notice text here/i);
    expect(textarea).toBeInTheDocument();

    fireEvent.change(textarea, { target: { value: 'New official scholarship circular.' } });
    expect(screen.getByText(/34/i)).toBeInTheDocument();
    expect(screen.getByText(/chars •/i)).toBeInTheDocument();
  });

  it('renders load demo and clear buttons', () => {
    render(
      <NoticeProvider>
        <NoticeBuffer />
      </NoticeProvider>
    );

    expect(screen.getByText(/Load Demo Notice/i)).toBeInTheDocument();
    expect(screen.getByText(/Clear Buffer/i)).toBeInTheDocument();
  });
});
