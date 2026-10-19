"""
Centralized Theme Tokens and CSS for Notice2Action AI.
Provides a modern, high-contrast dark SaaS aesthetic inspired by Linear, Raycast, and Vercel.
"""

THEME_CSS = """
<style>
/* ---------------- Root & Typography ---------------- */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #F8FAFC;
    background-color: #0B0F19;
}

code, pre, .font-mono {
    font-family: 'JetBrains Mono', monospace !important;
}

/* ---------------- Layout & Spacing ---------------- */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* ---------------- Header & Badges ---------------- */
.platform-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.25rem 1.5rem;
    background: linear-gradient(180deg, #161E2E 0%, #111827 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    margin-bottom: 1.75rem;
    box-shadow: 0 4px 24px -4px rgba(0, 0, 0, 0.4);
}

.brand-title {
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 0;
}

.brand-subtitle {
    font-size: 0.875rem;
    color: #94A3B8;
    margin-top: 0.25rem;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 0.75rem;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.25);
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #34D399;
}

.status-pill.warning {
    background: rgba(245, 158, 11, 0.1);
    border-color: rgba(245, 158, 11, 0.25);
    color: #FBBF24;
}

.status-pill.error {
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.25);
    color: #F87171;
}

.pulse-dot {
    width: 7px;
    height: 7px;
    background-color: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 8px #10B981;
}

/* ---------------- Surface Cards ---------------- */
.dark-card {
    background: #161E2E;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    transition: all 0.2s ease-in-out;
}

.dark-card:hover {
    border-color: rgba(59, 130, 246, 0.4);
    box-shadow: 0 6px 20px -4px rgba(0, 0, 0, 0.5);
}

.card-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #64748B;
    margin-bottom: 0.5rem;
}

.card-value {
    font-size: 1rem;
    font-weight: 600;
    color: #F8FAFC;
    line-height: 1.5;
}

.evidence-quote {
    background: rgba(15, 23, 42, 0.6);
    border-left: 3px solid #3B82F6;
    padding: 0.6rem 0.85rem;
    margin-top: 0.75rem;
    border-radius: 0 8px 8px 0;
    font-size: 0.825rem;
    color: #94A3B8;
    font-style: italic;
    font-family: 'JetBrains Mono', monospace;
}

.source-line {
    font-size: 0.725rem;
    color: #60A5FA;
    font-weight: 600;
    margin-top: 0.35rem;
    display: block;
}

/* ---------------- Overview Banner ---------------- */
.overview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.overview-metric {
    background: linear-gradient(180deg, #1E293B 0%, #161E2E 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1rem 1.25rem;
}

.metric-title {
    font-size: 0.725rem;
    font-weight: 700;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.metric-value {
    font-size: 1.15rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-top: 0.3rem;
}

.metric-highlight {
    color: #38BDF8;
}

/* ---------------- Tabs Styling ---------------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #111827;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 16px;
    color: #94A3B8;
    font-weight: 600;
    font-size: 0.875rem;
    border: none !important;
    background-color: transparent;
    transition: all 0.15s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #F8FAFC;
    background-color: rgba(255, 255, 255, 0.04);
}

.stTabs [aria-selected="true"] {
    background-color: #1E293B !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* ---------------- Action Checklist ---------------- */
.checklist-card {
    background: #161E2E;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.65rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    transition: border 0.15s ease;
}

.checklist-card:hover {
    border-color: rgba(99, 102, 241, 0.3);
}

.badge-tag {
    display: inline-block;
    padding: 0.2rem 0.5rem;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-family: 'JetBrains Mono', monospace;
}

.badge-mandatory {
    background: rgba(239, 68, 68, 0.15);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.badge-advisory {
    background: rgba(148, 163, 184, 0.12);
    color: #94A3B8;
    border: 1px solid rgba(148, 163, 184, 0.25);
}

.badge-category {
    background: rgba(59, 130, 246, 0.15);
    color: #60A5FA;
    border: 1px solid rgba(59, 130, 246, 0.3);
}

/* ---------------- Buttons & Inputs ---------------- */
.stButton>button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s ease !important;
    padding: 0.55rem 1.25rem !important;
}

.stButton>button[kind="primary"] {
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
    border: 1px solid #3B82F6 !important;
    box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.35) !important;
}

.stButton>button[kind="primary"]:hover {
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
    box-shadow: 0 6px 20px 0 rgba(37, 99, 235, 0.5) !important;
    transform: translateY(-1px);
}

.stButton>button[kind="secondary"] {
    background: #1E293B !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #F8FAFC !important;
}

.stButton>button[kind="secondary"]:hover {
    background: #27354A !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
}

/* ---------------- Q&A Chat Cards ---------------- */
.qa-card {
    background: #161E2E;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}

.qa-question {
    font-size: 0.95rem;
    font-weight: 700;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.qa-answer {
    font-size: 0.9rem;
    color: #CBD5E1;
    line-height: 1.5;
}

.qa-evidence {
    margin-top: 0.5rem;
    padding: 0.4rem 0.75rem;
    background: rgba(15, 23, 42, 0.7);
    border-left: 2px solid #10B981;
    font-size: 0.8rem;
    color: #6EE7B7;
    font-style: italic;
}

/* ---------------- Sidebar Styling ---------------- */
[data-testid="stSidebar"] {
    background-color: #0F172A !important;
    border-right: 1px solid rgba(255, 255, 255, 0.06);
}

[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.sidebar-brand {
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 1.25rem;
}
</style>
"""
