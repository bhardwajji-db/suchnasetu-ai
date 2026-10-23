import React, { useState } from 'react';
import { useNotice, type HistoryRecord } from '../context/NoticeContext';
import {
  Bookmark,
  Search,
  Filter,
  Trash2,
  Clock,
  Building,
  ArrowRight,
  Download,
  Compass,
} from 'lucide-react';

export const NoticeHistoryView: React.FC = () => {
  const {
    history,
    loadFromHistory,
    clearHistory,
    setActiveTab,
    savedNoticeIds,
    toggleSaveNotice,
    isNoticeSaved,
  } = useNotice();

  const [searchQuery, setSearchQuery] = useState<string>('');
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'BOOKMARKED' | 'DUE_THIS_WEEK' | 'APPROACHING' | 'PENDING'>('ALL');

  const handleDownloadNoticeText = (item: HistoryRecord) => {
    const blob = new Blob([item.rawText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `notice_${item.id}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Filter history based on search query and time-based filters
  const filteredHistory = history.filter((item) => {
    // 1. Text Search matching title, authority, deadline, referenceNumber, or text
    const q = searchQuery.toLowerCase().trim();
    if (q) {
      const matchText = (
        item.title.toLowerCase().includes(q) ||
        item.authority.toLowerCase().includes(q) ||
        item.deadline.toLowerCase().includes(q) ||
        item.referenceNumber.toLowerCase().includes(q) ||
        item.rawText.toLowerCase().includes(q)
      );
      if (!matchText) return false;
    }

    // 2. Filter tabs
    if (activeFilter === 'BOOKMARKED') {
      return isNoticeSaved(item.id);
    }

    if (activeFilter === 'DUE_THIS_WEEK') {
      // Check if deadline mentions upcoming month or contains a 2026 date
      const dl = item.deadline.toLowerCase();
      return dl.includes('2026') && !dl.includes('not stated');
    }

    if (activeFilter === 'APPROACHING') {
      const dl = item.deadline.toLowerCase();
      return !dl.includes('not stated') && !dl.includes('expired');
    }

    if (activeFilter === 'PENDING') {
      // Has deadline and not cleared
      return item.deadline && item.deadline !== 'Not Stated';
    }

    return true;
  });

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E1E7EE]">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-[#12233D] tracking-tight flex items-center gap-2.5">
            <Bookmark className="w-5 h-5 text-[#08785D]" />
            <span>Saved Notices & Personal Task Search</span>
          </h1>
          <p className="text-xs sm:text-sm text-[#526176] mt-1">
            Search saved circulars, bookmark important notices, and query tasks by timeframe.
          </p>
        </div>

        {history.length > 0 && (
          <button
            type="button"
            onClick={clearHistory}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-[#B42318] hover:bg-[#FEE8E7] border border-transparent hover:border-[#FCA5A5] transition self-start sm:self-auto cursor-pointer"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear History</span>
          </button>
        )}
      </div>

      {/* Search and Time-Based Filter Bar */}
      {history.length > 0 && (
        <div className="bg-white border border-[#E1E7EE] rounded-xl p-4 space-y-3 shadow-xs">
          {/* Search Box */}
          <div className="relative">
            <Search className="w-4 h-4 text-[#68778B] absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by subject, notice title, course, deadline, or keywords..."
              className="w-full pl-10 pr-4 py-2 rounded-lg bg-[#F8FAFC] border border-[#CBD5E1] text-xs text-[#12233D] focus:border-[#08785D] focus:outline-hidden transition"
            />
          </div>

          {/* Time-Based Filter Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
            <span className="font-bold text-[#526176] flex items-center gap-1 mr-1 shrink-0">
              <Filter className="w-3.5 h-3.5 text-[#08785D]" /> Filter:
            </span>
            {[
              { key: 'ALL', label: `All Notices (${history.length})` },
              { key: 'BOOKMARKED', label: `Saved / Bookmarked (${savedNoticeIds.length})` },
              { key: 'DUE_THIS_WEEK', label: 'Due This Week' },
              { key: 'APPROACHING', label: 'Approaching Deadlines' },
              { key: 'PENDING', label: 'Pending Tasks' },
            ].map((f) => (
              <button
                key={f.key}
                type="button"
                onClick={() => setActiveFilter(f.key as any)}
                className={`px-3 py-1.5 rounded-xl font-semibold transition cursor-pointer shrink-0 ${
                  activeFilter === f.key
                    ? 'bg-[#08785D] text-white shadow-xs'
                    : 'bg-[#F8FAFC] text-[#526176] hover:text-[#12233D] border border-[#CBD5E1]'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Notices List */}
      {filteredHistory.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredHistory.map((item) => {
            const isSaved = isNoticeSaved(item.id);
            return (
              <div
                key={item.id}
                className={`bg-white border rounded-xl p-5 space-y-3 transition shadow-xs flex flex-col justify-between ${
                  isSaved ? 'border-[#08785D] ring-1 ring-[#08785D]/20' : 'border-[#E1E7EE] hover:border-[#B7E7D2]'
                }`}
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="text-sm font-bold text-[#12233D] leading-snug line-clamp-2">
                      {item.title}
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0">
                      <button
                        type="button"
                        onClick={() => toggleSaveNotice(item.id)}
                        className={`p-1.5 rounded-lg border transition cursor-pointer ${
                          isSaved
                            ? 'bg-[#E8F7F0] border-[#B7E7D2] text-[#08785D]'
                            : 'bg-[#F8FAFC] border-[#CBD5E1] text-[#68778B] hover:text-[#08785D]'
                        }`}
                        title={isSaved ? 'Remove from Saved' : 'Save Notice'}
                        aria-label={isSaved ? 'Unsave Notice' : 'Save Notice'}
                      >
                        <Bookmark className={`w-3.5 h-3.5 ${isSaved ? 'fill-[#08785D]' : ''}`} />
                      </button>

                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-[#F8FAFC] text-[#526176] border border-[#CBD5E1]">
                        {item.charCount} chars
                      </span>
                    </div>
                  </div>

                  <div className="space-y-1 text-xs text-[#526176]">
                    <div className="flex items-center gap-2 truncate">
                      <Building className="w-3.5 h-3.5 text-[#08785D] shrink-0" />
                      <span className="truncate">{item.authority}</span>
                    </div>
                    <div className="flex items-center gap-2 truncate">
                      <Clock className="w-3.5 h-3.5 text-[#92500A] shrink-0" />
                      <span className="truncate">Deadline: {item.deadline}</span>
                    </div>
                    <div className="text-[11px] text-[#68778B] pt-1">
                      Recorded: {item.timestamp} · Ref: {item.referenceNumber}
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-[#E1E7EE] flex items-center justify-between gap-2">
                  <button
                    type="button"
                    onClick={() => handleDownloadNoticeText(item)}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium text-[#526176] hover:text-[#12233D] bg-[#F8FAFC] hover:bg-slate-200 border border-[#E1E7EE] transition cursor-pointer"
                    title="Download raw notice text"
                  >
                    <Download className="w-3 h-3 text-[#68778B]" />
                    <span>Download Text</span>
                  </button>

                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        loadFromHistory(item);
                        setActiveTab(7);
                      }}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-[#08785D] bg-[#E8F7F0] hover:bg-[#D4EFE3] border border-[#B7E7D2] transition cursor-pointer"
                      title="View Action Plan"
                    >
                      <Compass className="w-3.5 h-3.5" />
                      <span>Roadmap</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => loadFromHistory(item)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs cursor-pointer"
                    >
                      <span>Open</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : history.length > 0 ? (
        <div className="bg-white border border-[#E1E7EE] rounded-2xl p-10 text-center space-y-3 shadow-xs">
          <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-500 flex items-center justify-center mx-auto">
            <Search className="w-5 h-5" />
          </div>
          <h2 className="text-sm font-bold text-[#12233D]">No Matching Notices or Tasks Found</h2>
          <p className="text-xs text-[#526176] max-w-md mx-auto">
            No saved notices or tasks match your current query or timeframe filter. Try clearing your search term or switching to "All Notices".
          </p>
          <button
            type="button"
            onClick={() => {
              setSearchQuery('');
              setActiveFilter('ALL');
            }}
            className="px-3.5 py-1.5 rounded-lg text-xs font-semibold text-[#08785D] bg-[#E8F7F0] border border-[#B7E7D2] hover:bg-[#D4EFE3] transition cursor-pointer"
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <div className="bg-white border border-[#E1E7EE] rounded-2xl p-12 text-center space-y-4 shadow-xs">
          <div className="w-12 h-12 rounded-xl bg-[#E8F7F0] border border-[#B7E7D2] text-[#08785D] flex items-center justify-center mx-auto">
            <Bookmark className="w-6 h-6" />
          </div>
          <h2 className="text-base font-bold text-[#12233D]">No Saved Notices in This Session</h2>
          <p className="text-xs text-[#526176] max-w-md mx-auto">
            Notices analyzed or bookmarked during your session will appear here for fast retrieval and time-based task search.
          </p>
          <button
            type="button"
            onClick={() => setActiveTab(1)}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-[#08785D] hover:bg-[#06664E] transition shadow-xs cursor-pointer"
          >
            <span>Analyze a Notice Now</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </div>
  );
};
