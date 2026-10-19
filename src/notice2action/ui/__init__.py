"""
UI components and styles package for Notice2Action AI.
"""

from notice2action.ui.styles import THEME_CSS
from notice2action.ui.components import (
    render_platform_header,
    render_notice_overview,
    render_fact_card,
    render_summary_section,
    render_checklist_section,
    render_qa_item,
    render_status_badge,
    render_analysis_banner,
    render_recovery_box,
)

__all__ = [
    "THEME_CSS",
    "render_platform_header",
    "render_notice_overview",
    "render_fact_card",
    "render_summary_section",
    "render_checklist_section",
    "render_qa_item",
    "render_status_badge",
    "render_analysis_banner",
    "render_recovery_box",
]
