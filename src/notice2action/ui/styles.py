"""
Centralized Design Tokens and CSS for Notice2Action AI (PS02).
Implements the premium dark AI document-intelligence workspace.
Color Palette:
- Main background: #06101F
- Sidebar background: #071A33
- Elevated cards & header: #0B1C35
- Secondary surfaces: #102746
- Primary accent: #0875FF
- Border: #1D3D67
- Success: #10B981
- Warning: #F59E0B
- Error: #EF4444
- Text: #F2F6FF
- Secondary text: #9EB5D8
"""

THEME_CSS = """
<style>
/* ---------------- Root & Typography ---------------- */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #F2F6FF;
    background-color: #06101F;
    overflow-x: hidden !important;
    max-width: 100vw;
}

[class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

code, pre, .font-mono {
    font-family: 'JetBrains Mono', monospace !important;
}

/* ---------------- Main Layout Spacing (1366x768 / 1920x1080 responsive) ---------------- */
.main .block-container,
[data-testid="stMainBlockContainer"],
div[data-testid="stAppViewContainer"] section.main > div.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
    max-width: 1320px !important;
    background-color: #06101F !important;
}

/* ---------------- Top Platform Header ---------------- */
.platform-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1.25rem;
    background: #0B1C35;
    border: 1px solid #1D3D67;
    border-radius: 12px;
    margin-bottom: 0.85rem;
    box-shadow: 0 4px 18px rgba(3, 10, 22, 0.4);
}

.brand-title {
    font-size: 1.25rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #F2F6FF;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
}

.brand-subtitle {
    font-size: 0.78rem;
    color: #9EB5D8;
    margin-top: 0.15rem;
}

.header-status-group {
    display: flex;
    align-items: center;
    gap: 0.65rem;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.3rem 0.75rem;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.35);
    border-radius: 9999px;
    font-size: 0.725rem;
    font-weight: 600;
    color: #10B981;
}

.status-pill.warning {
    background: rgba(245, 158, 11, 0.12);
    border-color: rgba(245, 158, 11, 0.35);
    color: #F59E0B;
}

.status-pill.error {
    background: rgba(248, 113, 113, 0.12);
    border-color: rgba(248, 113, 113, 0.35);
    color: #F87171;
}

.status-pill.info {
    background: rgba(8, 117, 255, 0.12);
    border-color: rgba(8, 117, 255, 0.35);
    color: #38BDF8;
}

.pulse-dot {
    width: 6px;
    height: 6px;
    background-color: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 8px #10B981;
}

/* ---------------- Introduction & Workflow Panel ---------------- */
.intro-panel {
    background: #0B1C35;
    border: 1px solid #1D3D67;
    border-radius: 12px;
    padding: 0.85rem 1.25rem;
    margin-bottom: 0.85rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1.5rem;
}

.intro-left {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    flex: 1;
}

.intro-icon-box {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    background: rgba(8, 117, 255, 0.15);
    border: 1px solid rgba(8, 117, 255, 0.35);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.35rem;
    flex-shrink: 0;
}

.intro-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #F2F6FF;
    margin-bottom: 0.2rem;
}

.intro-desc {
    font-size: 0.8rem;
    color: #9EB5D8;
    line-height: 1.4;
}

.workflow-stepper {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    background: #102746;
    border: 1px solid #1D3D67;
    border-radius: 10px;
    padding: 0.5rem 0.85rem;
    flex-shrink: 0;
}

.workflow-step {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.725rem;
    color: #9EB5D8;
    font-weight: 600;
}

.workflow-step.active {
    color: #F2F6FF;
}

.workflow-badge {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: rgba(8, 117, 255, 0.25);
    border: 1px solid #0875FF;
    color: #60A5FA;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.65rem;
    font-weight: 700;
}

.workflow-arrow {
    color: #1D3D67;
    font-size: 0.75rem;
}

/* ---------------- Rounded Dark Workspace Panels ---------------- */
.workspace-panel {
    background: #0B1C35;
    border: 1px solid #1D3D67;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.85rem;
    box-shadow: 0 4px 16px rgba(4, 12, 28, 0.35);
}

.panel-header {
    margin-bottom: 0.85rem;
}

.panel-title {
    font-size: 1rem;
    font-weight: 700;
    color: #F2F6FF;
    display: flex;
    align-items: center;
    gap: 0.45rem;
}

.panel-subtitle {
    font-size: 0.775rem;
    color: #9EB5D8;
    margin-top: 0.15rem;
}

/* ---------------- Surface Cards ---------------- */
.dark-card {
    background: #102746;
    border: 1px solid #1D3D67;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.65rem;
    transition: all 0.15s ease-in-out;
}

.dark-card:hover {
    border-color: #0875FF;
    box-shadow: 0 4px 16px rgba(8, 117, 255, 0.15);
}

.card-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #9EB5D8;
    margin-bottom: 0.3rem;
    display: block;
}

.card-value {
    font-size: 0.925rem;
    font-weight: 600;
    color: #F2F6FF;
    line-height: 1.45;
}

.evidence-quote {
    background: rgba(7, 18, 37, 0.85);
    border-left: 3px solid #0875FF;
    padding: 0.45rem 0.7rem;
    margin-top: 0.5rem;
    border-radius: 0 6px 6px 0;
    font-size: 0.775rem;
    color: #9EB5D8;
    font-style: italic;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.4;
}

.source-line {
    font-size: 0.68rem;
    color: #60A5FA;
    font-weight: 600;
    margin-top: 0.25rem;
    display: block;
}

/* ---------------- Overview Metric Grid ---------------- */
.overview-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.65rem;
    margin-bottom: 0.85rem;
}

.overview-metric {
    background: #0E2342;
    border: 1px solid #1D3D67;
    border-radius: 10px;
    padding: 0.75rem 0.9rem;
}

.metric-title {
    font-size: 0.65rem;
    font-weight: 700;
    color: #9EB5D8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.metric-value {
    font-size: 1rem;
    font-weight: 700;
    color: #F2F6FF;
    margin-top: 0.2rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.metric-highlight {
    color: #38BDF8;
}

/* ---------------- Tabs Styling (Supports modern Streamlit 1.66 React Aria & BaseWeb) ---------------- */
[data-testid="stTabs"] [role="tablist"],
.stTabs [data-baseweb="tab-list"],
.stTabs [role="tablist"] {
    display: flex !important;
    gap: 6px !important;
    background-color: #0E2342 !important;
    padding: 5px !important;
    border-radius: 10px !important;
    border: 1px solid #1D3D67 !important;
    margin-bottom: 0.85rem !important;
    overflow-x: auto !important;
    flex-wrap: nowrap !important;
}

[data-testid="stTabs"] [role="tab"],
[data-testid="stTab"],
.stTabs [data-baseweb="tab"],
.stTabs [role="tab"] {
    border-radius: 7px !important;
    padding: 7px 16px !important;
    color: #9EB5D8 !important;
    font-weight: 600 !important;
    font-size: 0.825rem !important;
    border: 1px solid transparent !important;
    background-color: transparent !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
    white-space: nowrap !important;
}

[data-testid="stTabs"] [role="tab"]:hover,
[data-testid="stTab"]:hover,
.stTabs [data-baseweb="tab"]:hover,
.stTabs [role="tab"]:hover {
    color: #F2F6FF !important;
    background-color: rgba(255, 255, 255, 0.06) !important;
    border-color: rgba(29, 61, 103, 0.5) !important;
}

[data-testid="stTabs"] [role="tab"][aria-selected="true"],
[data-testid="stTab"][aria-selected="true"],
.stTabs [aria-selected="true"] {
    background-color: #0875FF !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 10px rgba(8, 117, 255, 0.4) !important;
    border-color: #0875FF !important;
}

/* ---------------- Action Buttons ---------------- */
.stButton>button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    transition: all 0.15s ease !important;
    padding: 0.45rem 1rem !important;
    font-size: 0.85rem !important;
}

/* Bright Blue Visually Dominant Primary Button */
.stButton>button[kind="primary"],
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0875FF 0%, #1556C0 100%) !important;
    border: 1px solid #0875FF !important;
    box-shadow: 0 4px 16px rgba(8, 117, 255, 0.45) !important;
    color: #FFFFFF !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    padding: 0.65rem 1.25rem !important;
}

.stButton>button[kind="primary"]:hover,
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2587FF 0%, #0875FF 100%) !important;
    box-shadow: 0 6px 22px rgba(8, 117, 255, 0.6) !important;
    transform: translateY(-1px);
}

/* Secondary Button (Dark Blue Surface #0E2342) */
.stButton>button[kind="secondary"],
div[data-testid="stButton"] > button[kind="secondary"] {
    background: #0E2342 !important;
    border: 1px solid #1D3D67 !important;
    color: #9EB5D8 !important;
}

.stButton>button[kind="secondary"]:hover,
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #15325C !important;
    border-color: #0875FF !important;
    color: #F2F6FF !important;
}

/* ---------------- Compact Text Area ---------------- */
div[data-baseweb="textarea"] textarea {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.825rem !important;
    line-height: 1.45 !important;
    background-color: #071225 !important;
    color: #F2F6FF !important;
    border-radius: 8px !important;
    border: 1px solid #1D3D67 !important;
}

div[data-baseweb="textarea"]:focus-within {
    border-color: #0875FF !important;
    box-shadow: 0 0 0 1px #0875FF !important;
}

/* ---------------- Sidebar Styling (#071A33, Compact 265px) ---------------- */
section[data-testid="stSidebar"],
[data-testid="stSidebar"] {
    min-width: 250px !important;
    max-width: 275px !important;
    width: 265px !important;
    background-color: #071A33 !important;
    border-right: 1px solid #1D3D67 !important;
}

section[data-testid="stSidebar"] > div {
    width: 100% !important;
}

[data-testid="stSidebar"] .block-container,
[data-testid="stSidebarUserContent"] {
    padding-top: 0.85rem !important;
    padding-bottom: 1.5rem !important;
    padding-left: 0.85rem !important;
    padding-right: 0.85rem !important;
}

.sidebar-brand {
    padding-bottom: 0.65rem;
    border-bottom: 1px solid #1D3D67;
    margin-bottom: 0.85rem;
}

/* Sidebar Specific Navigation Buttons */
[class*="st-key-sidebar_nav_"] button {
    text-align: left !important;
    justify-content: flex-start !important;
    font-size: 0.825rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 0.75rem !important;
    border-radius: 8px !important;
    margin-bottom: 0.25rem !important;
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
}

[class*="st-key-sidebar_nav_"] button[kind="primary"] {
    background: #102746 !important;
    color: #F2F6FF !important;
    border: 1px solid #0875FF !important;
    border-left: 4px solid #0875FF !important;
    box-shadow: 0 2px 10px rgba(8, 117, 255, 0.3) !important;
}

[class*="st-key-sidebar_nav_"] button[kind="secondary"] {
    background: transparent !important;
    color: #9EB5D8 !important;
    border: 1px solid rgba(29, 61, 103, 0.4) !important;
}

[class*="st-key-sidebar_nav_"] button[kind="secondary"]:hover {
    background: #0E2342 !important;
    color: #F2F6FF !important;
    border-color: #1D3D67 !important;
}

/* Sidebar Non-Navigation Action Buttons (Demo, Samples, Reset) */
[data-testid="stSidebar"] div[data-testid="stButton"]:not([class*="st-key-sidebar_nav_"]) > button {
    text-align: center !important;
    justify-content: center !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    padding: 0.45rem 0.75rem !important;
    background: #0E2342 !important;
    border: 1px solid #1D3D67 !important;
    color: #9EB5D8 !important;
    width: 100% !important;
}

[data-testid="stSidebar"] div[data-testid="stButton"]:not([class*="st-key-sidebar_nav_"]) > button:hover {
    background: #15325C !important;
    border-color: #0875FF !important;
    color: #F2F6FF !important;
}

/* Status Banner */
.status-banner {
    padding: 0.65rem 0.95rem;
    border-radius: 8px;
    margin-bottom: 0.85rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    font-weight: 600;
}

.status-banner.success {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.35);
    color: #10B981;
}

.status-banner.failed {
    background: rgba(248, 113, 113, 0.12);
    border: 1px solid rgba(248, 113, 113, 0.35);
    color: #EF4444;
}

.status-banner.ready {
    background: #102746;
    border: 1px solid #1D3D67;
    color: #9EB5D8;
}

/* Compact alerts */
.stAlert {
    padding: 0.55rem 0.85rem !important;
    border-radius: 8px !important;
}

/* ---------------- Responsive Layout Media Queries ---------------- */
@media (max-width: 900px) {
    .overview-grid {
        grid-template-columns: repeat(2, 1fr) !important;
    }
}

@media (max-width: 768px) {
    .platform-header {
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 0.75rem !important;
    }
    .header-status-group {
        flex-wrap: wrap !important;
        width: 100% !important;
    }
    .intro-panel {
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 0.75rem !important;
    }
    .workflow-stepper {
        width: 100% !important;
        flex-wrap: wrap !important;
    }
    .overview-grid {
        grid-template-columns: 1fr 1fr !important;
    }
}

@media (max-width: 480px) {
    .overview-grid {
        grid-template-columns: 1fr !important;
    }
    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    .brand-title {
        font-size: 1.05rem !important;
    }
}
</style>
"""
