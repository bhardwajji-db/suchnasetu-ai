import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { FileDropzone } from '../components/FileDropzone';
import { NoticeProvider } from '../context/NoticeContext';
import { apiClient } from '../services/apiClient';

describe('FileDropzone Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders dropzone title and updated subtitle reflecting DOCX and 10MB limit', () => {
    render(
      <NoticeProvider>
        <FileDropzone />
      </NoticeProvider>
    );

    expect(screen.getByText(/Upload Official Notice/i)).toBeInTheDocument();
    expect(screen.getByText(/DOCX/i)).toBeInTheDocument();
    expect(screen.getByText(/10MB/i)).toBeInTheDocument();
  });

  it('has file input with comprehensive accepted file types', () => {
    render(
      <NoticeProvider>
        <FileDropzone />
      </NoticeProvider>
    );

    const input = screen.getByLabelText(/Upload notice image or document/i) as HTMLInputElement;
    expect(input).toBeInTheDocument();
    expect(input.accept).toContain('.docx');
    expect(input.accept).toContain('.pdf');
    expect(input.accept).toContain('.txt');
    expect(input.accept).toContain('.png');
    expect(input.accept).toContain('.jpg');
    expect(input.accept).toContain('.webp');
  });

  it('rejects files exceeding 10MB limit with clear error banner', async () => {
    render(
      <NoticeProvider>
        <FileDropzone />
      </NoticeProvider>
    );

    const input = screen.getByLabelText(/Upload notice image or document/i);
    // Create an 11MB dummy file
    const oversizedBlob = new Blob(['0'.repeat(1024)], { type: 'application/pdf' });
    const oversizedFile = new File([oversizedBlob], 'huge_circular.pdf', { type: 'application/pdf' });
    Object.defineProperty(oversizedFile, 'size', { value: 11 * 1024 * 1024 });

    fireEvent.change(input, { target: { files: [oversizedFile] } });

    await waitFor(() => {
      expect(screen.getByText(/File size exceeds the 10MB limit/i)).toBeInTheDocument();
    });
  });

  it('handles successful DOCX upload and updates ground truth buffer', async () => {
    const uploadSpy = vi.spyOn(apiClient, 'uploadFile').mockResolvedValue({
      source_type: 'docx',
      filename: 'guidelines.docx',
      raw_text: 'OFFICIAL UNIVERSITY GUIDELINES: Deadline 30 Nov 2026.',
      char_count: 53,
    });

    render(
      <NoticeProvider>
        <FileDropzone />
      </NoticeProvider>
    );

    const input = screen.getByLabelText(/Upload notice image or document/i);
    const docxFile = new File(['fake-docx-data'], 'guidelines.docx', {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    });

    fireEvent.change(input, { target: { files: [docxFile] } });

    await waitFor(() => {
      expect(uploadSpy).toHaveBeenCalledWith(docxFile);
    });
  });

  it('handles upload errors safely and displays error alert', async () => {
    vi.spyOn(apiClient, 'uploadFile').mockRejectedValue(new Error('Corrupt or invalid DOCX archive.'));

    render(
      <NoticeProvider>
        <FileDropzone />
      </NoticeProvider>
    );

    const input = screen.getByLabelText(/Upload notice image or document/i);
    const brokenFile = new File(['broken'], 'broken.docx', {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    });

    fireEvent.change(input, { target: { files: [brokenFile] } });

    await waitFor(() => {
      expect(screen.getByText(/Corrupt or invalid DOCX archive/i)).toBeInTheDocument();
    });
  });
});

