import React, { useState, useEffect, useMemo } from 'react';
import { useNotice } from '../context/NoticeContext';
import { useTranslation, SUPPORTED_LANGUAGES } from '../i18n';
import { apiClient } from '../services/apiClient';
import type { DemoLibraryItem } from '../types/api';
import {
  BookOpen,
  Search,
  Filter,
  FileText,
  ArrowRight,
  FileCode,
  Image as ImageIcon,
  Globe,
  Eye,
  X,
} from 'lucide-react';

export const DemoLibraryView: React.FC = () => {
  const { loadDemoItem } = useNotice();
  const { t } = useTranslation();

  const [demos, setDemos] = useState<DemoLibraryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('all');
  const [selectedFormat, setSelectedFormat] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const [previewItem, setPreviewItem] = useState<DemoLibraryItem | null>(null);
  const [previewContent, setPreviewContent] = useState<string>('');
  const [loadingPreview, setLoadingPreview] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    async function fetchDemos() {
      try {
        setLoading(true);
        const res = await apiClient.getDemoLibrary();
        if (isMounted) {
          setDemos(res.demos);
          setError(null);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to load demo library');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }
    fetchDemos();
    return () => {
      isMounted = false;
    };
  }, []);

  const categories = useMemo(() => {
    const set = new Set<string>();
    demos.forEach((d) => set.add(d.category));
    return Array.from(set).sort();
  }, [demos]);

  const filteredDemos = useMemo(() => {
    return demos.filter((demo) => {
      if (selectedLanguage !== 'all' && demo.language !== selectedLanguage) {
        return false;
      }
      if (selectedFormat !== 'all' && demo.format !== selectedFormat) {
        return false;
      }
      if (selectedCategory !== 'all' && demo.category !== selectedCategory) {
        return false;
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchTitle = demo.title.toLowerCase().includes(q);
        const matchDesc = demo.description.toLowerCase().includes(q);
        const matchCat = demo.category.toLowerCase().includes(q);
        const matchId = demo.id.toLowerCase().includes(q);
        if (!matchTitle && !matchDesc && !matchCat && !matchId) {
          return false;
        }
      }
      return true;
    });
  }, [demos, selectedLanguage, selectedFormat, selectedCategory, searchQuery]);

  const handleOpenPreview = async (item: DemoLibraryItem) => {
    setPreviewItem(item);
    setLoadingPreview(true);
    try {
      const data = await apiClient.loadDemoLibraryItem(item.id);
      setPreviewContent(data.text);
    } catch {
      setPreviewContent('Failed to load notice preview.');
    } finally {
      setLoadingPreview(false);
    }
  };

  const getFormatIcon = (format: string) => {
    switch (format.toLowerCase()) {
      case 'pdf':
        return <FileCode className="w-4 h-4 text-red-600" />;
      case 'docx':
        return <FileText className="w-4 h-4 text-blue-600" />;
      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'webp':
      case 'tif':
      case 'tiff':
        return <ImageIcon className="w-4 h-4 text-emerald-600" />;
      default:
        return <FileText className="w-4 h-4 text-slate-600" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* View Header */}
      <div className="bg-white rounded-2xl p-6 border border-[#E1E7EE] shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2.5">
              <div className="p-2.5 rounded-xl bg-[#E8F7F0] text-[#08785D]">
                <BookOpen className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-xl font-extrabold text-[#12233D] tracking-tight">
                  {t('navDemoLibrary') || 'Saved Demo Notice Library'}
                </h1>
                <p className="text-xs text-[#526176]">
                  Searchable, persistent repository of 32 official notices across 10 constitutional languages and 7 file formats.
                </p>
              </div>
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="flex items-center gap-3 bg-[#F8FAFC] p-2.5 rounded-xl border border-[#E1E7EE] text-xs font-semibold">
            <div className="text-center px-2">
              <span className="block text-base font-extrabold text-[#08785D]">{demos.length}</span>
              <span className="text-[10px] text-[#68778B] uppercase">Notices</span>
            </div>
            <div className="w-px h-6 bg-[#E1E7EE]" />
            <div className="text-center px-2">
              <span className="block text-base font-extrabold text-[#12233D]">10</span>
              <span className="text-[10px] text-[#68778B] uppercase">Languages</span>
            </div>
            <div className="w-px h-6 bg-[#E1E7EE]" />
            <div className="text-center px-2">
              <span className="block text-base font-extrabold text-[#12233D]">7</span>
              <span className="text-[10px] text-[#68778B] uppercase">Formats</span>
            </div>
          </div>
        </div>

        {/* Search & Filter Toolbar */}
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-4 border-t border-[#E1E7EE]">
          {/* Keyword Search */}
          <div className="relative">
            <Search className="w-4 h-4 text-[#68778B] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search title, category, keywords..."
              className="w-full bg-[#F8FAFC] border border-[#E1E7EE] rounded-xl pl-9 pr-3 py-2 text-xs text-[#12233D] placeholder-[#68778B] outline-hidden focus:border-[#08785D] focus:bg-white"
            />
          </div>

          {/* Language Filter */}
          <div className="relative">
            <Globe className="w-4 h-4 text-[#68778B] absolute left-3 top-1/2 -translate-y-1/2" />
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="w-full bg-[#F8FAFC] border border-[#E1E7EE] rounded-xl pl-9 pr-3 py-2 text-xs font-medium text-[#12233D] outline-hidden focus:border-[#08785D] cursor-pointer"
            >
              <option value="all">All Languages (10)</option>
              {Object.entries(SUPPORTED_LANGUAGES).map(([code, meta]) => (
                <option key={code} value={code}>
                  {meta.nativeName} ({meta.name})
                </option>
              ))}
            </select>
          </div>

          {/* Format Filter */}
          <div className="relative">
            <FileText className="w-4 h-4 text-[#68778B] absolute left-3 top-1/2 -translate-y-1/2" />
            <select
              value={selectedFormat}
              onChange={(e) => setSelectedFormat(e.target.value)}
              className="w-full bg-[#F8FAFC] border border-[#E1E7EE] rounded-xl pl-9 pr-3 py-2 text-xs font-medium text-[#12233D] outline-hidden focus:border-[#08785D] cursor-pointer"
            >
              <option value="all">All File Formats</option>
              <option value="txt">Plain Text (.txt)</option>
              <option value="pdf">PDF Document (.pdf)</option>
              <option value="docx">Word Document (.docx)</option>
              <option value="png">PNG Image (.png)</option>
              <option value="jpg">JPEG Image (.jpg)</option>
              <option value="webp">WebP Image (.webp)</option>
              <option value="tif">TIFF Scanned Image (.tif)</option>
            </select>
          </div>

          {/* Category Filter */}
          <div className="relative">
            <Filter className="w-4 h-4 text-[#68778B] absolute left-3 top-1/2 -translate-y-1/2" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full bg-[#F8FAFC] border border-[#E1E7EE] rounded-xl pl-9 pr-3 py-2 text-xs font-medium text-[#12233D] outline-hidden focus:border-[#08785D] cursor-pointer"
            >
              <option value="all">All Categories ({categories.length})</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat.charAt(0).toUpperCase() + cat.slice(1).replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      {loading ? (
        <div className="flex items-center justify-center p-12 bg-white rounded-2xl border border-[#E1E7EE]">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-3 border-[#08785D] border-t-transparent rounded-full animate-spin" />
            <span className="text-xs font-semibold text-[#526176]">Loading demo library records...</span>
          </div>
        </div>
      ) : error ? (
        <div className="p-6 bg-red-50 text-red-700 rounded-2xl border border-red-200 text-xs">
          {error}
        </div>
      ) : filteredDemos.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-12 bg-white rounded-2xl border border-[#E1E7EE] text-center">
          <BookOpen className="w-10 h-10 text-slate-300 mb-2" />
          <h3 className="text-sm font-bold text-[#12233D]">No matching demo notices found</h3>
          <p className="text-xs text-[#526176] mt-1">Try resetting the language, format, or search query filter.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDemos.map((demo) => {
            const langMeta = (SUPPORTED_LANGUAGES as any)[demo.language] || {
              nativeName: demo.language.toUpperCase(),
              name: demo.language,
            };

            return (
              <div
                key={demo.id}
                className="bg-white rounded-2xl p-5 border border-[#E1E7EE] hover:border-[#B7E7D2] hover:shadow-md transition-all flex flex-col justify-between group"
              >
                <div className="space-y-3">
                  {/* Badges row */}
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-[#E8F7F0] text-[#08785D] border border-[#B7E7D2]">
                        {langMeta.nativeName}
                      </span>
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-mono font-bold bg-slate-100 text-slate-700 uppercase">
                        {getFormatIcon(demo.format)}
                        {demo.format}
                      </span>
                      <span className="text-[10px] font-medium text-[#68778B] bg-[#F8FAFC] px-1.5 py-0.5 rounded-md border border-[#E1E7EE]">
                        {demo.category.replace(/_/g, ' ')}
                      </span>
                    </div>

                    <span className="text-[10px] font-mono text-[#68778B] shrink-0">
                      {demo.word_count} words
                    </span>
                  </div>

                  {/* Title & Description */}
                  <div>
                    <h3 className="text-sm font-bold text-[#12233D] group-hover:text-[#08785D] transition-colors leading-snug">
                      {demo.title}
                    </h3>
                    <p className="text-xs text-[#526176] mt-1.5 line-clamp-3 leading-relaxed">
                      {demo.description}
                    </p>
                  </div>
                </div>

                {/* Actions row */}
                <div className="mt-4 pt-3 border-t border-[#E1E7EE] flex items-center justify-between gap-2">
                  <button
                    type="button"
                    onClick={() => handleOpenPreview(demo)}
                    className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-[#526176] hover:text-[#12233D] hover:bg-slate-100 transition cursor-pointer"
                    title="Preview extracted notice content"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>Preview</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => loadDemoItem(demo.id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-[#08785D] hover:bg-[#06664E] shadow-xs cursor-pointer transition-all"
                  >
                    <span>Load & Analyze</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Preview Modal */}
      {previewItem && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[80vh] flex flex-col shadow-2xl border border-[#E1E7EE]">
            <div className="flex items-center justify-between p-4 border-b border-[#E1E7EE]">
              <div>
                <h3 className="text-sm font-bold text-[#12233D]">{previewItem.title}</h3>
                <span className="text-xs text-[#68778B]">
                  {previewItem.id} • {previewItem.format.toUpperCase()} • {previewItem.language.toUpperCase()}
                </span>
              </div>
              <button
                type="button"
                onClick={() => setPreviewItem(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-4 overflow-y-auto flex-1 font-mono text-xs bg-[#F8FAFC] whitespace-pre-wrap leading-relaxed text-[#12233D]">
              {loadingPreview ? 'Loading notice text...' : previewContent}
            </div>
            <div className="p-3 border-t border-[#E1E7EE] flex justify-end gap-2 bg-white">
              <button
                type="button"
                onClick={() => setPreviewItem(null)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-[#526176] hover:bg-slate-100 cursor-pointer"
              >
                Close
              </button>
              <button
                type="button"
                onClick={() => {
                  loadDemoItem(previewItem.id);
                  setPreviewItem(null);
                }}
                className="px-3.5 py-1.5 rounded-lg text-xs font-bold text-white bg-[#08785D] hover:bg-[#06664E] cursor-pointer"
              >
                Load into Assistant
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
