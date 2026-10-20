"""
Modern Accessible UI Components for Notice2Action AI (Streamlit).
Designed for high contrast, dark SaaS aesthetic (#071225, #0A1B35, #0E2342, #0875FF).
"""

from __future__ import annotations

import streamlit as st
from typing import Optional, List, Dict, Any
from notice2action.schemas import (
    CertaintyStatus,
    ExtractedFact,
    ChecklistItem,
    PlainLanguageSummary,
    ActionChecklist,
    StructuredNotice,
)
from notice2action.tts import generate_audio_bytes, get_web_speech_js


STATUS_STYLES = {
    CertaintyStatus.STATED: {
        "bg": "rgba(16, 185, 129, 0.15)",
        "text": "#10B981",
        "border": "rgba(16, 185, 129, 0.35)",
        "label": "✓ Stated",
    },
    CertaintyStatus.NOT_STATED: {
        "bg": "rgba(158, 181, 216, 0.12)",
        "text": "#9EB5D8",
        "border": "rgba(158, 181, 216, 0.25)",
        "label": "✕ Not Stated",
    },
    CertaintyStatus.UNCERTAIN: {
        "bg": "rgba(245, 158, 11, 0.15)",
        "text": "#F59E0B",
        "border": "rgba(245, 158, 11, 0.35)",
        "label": "⚠ Needs Confirmation",
    },
    CertaintyStatus.CONFLICTING: {
        "bg": "rgba(248, 113, 113, 0.15)",
        "text": "#F87171",
        "border": "rgba(248, 113, 113, 0.35)",
        "label": "⚡ Conflicting",
    },
    CertaintyStatus.UNREADABLE: {
        "bg": "rgba(100, 116, 139, 0.2)",
        "text": "#CBD5E1",
        "border": "rgba(100, 116, 139, 0.35)",
        "label": "❓ Unreadable",
    },
}


def render_status_badge(status: CertaintyStatus) -> str:
    """Returns HTML for a dark SaaS, high-contrast status badge."""
    info = STATUS_STYLES.get(status, STATUS_STYLES[CertaintyStatus.UNCERTAIN])
    return (
        f"<span style='"
        f"background: {info['bg']}; "
        f"color: {info['text']}; "
        f"border: 1px solid {info['border']}; "
        f"padding: 3px 9px; "
        f"border-radius: 9999px; "
        f"font-size: 11px; "
        f"font-weight: 700; "
        f"font-family: monospace; "
        f"display: inline-flex; "
        f"align-items: center; "
        f"letter-spacing: 0.02em;'>"
        f"{info['label']}"
        f"</span>"
    )


def render_platform_header(status: str = "ok", model_name: str = "gemma4:latest", ocr_status: str = "ok"):
    """Renders the executive top header with brand identity, live AI status, and OCR status."""
    if status == "ok":
        pill_class = "status-pill"
        dot_color = "#10B981"
        status_text = f"Local {model_name} Active"
    elif status == "warning":
        pill_class = "status-pill warning"
        dot_color = "#F59E0B"
        status_text = "System Warning: Check Preflight"
    else:
        pill_class = "status-pill error"
        dot_color = "#EF4444"
        status_text = "Ollama / Model Offline"

    ocr_badge = (
        '<div class="status-pill">'
        '<div style="width: 7px; height: 7px; background-color: #10B981; border-radius: 50%;"></div>'
        '<span>Tesseract OCR Active</span>'
        '</div>'
        if ocr_status == "ok"
        else '<div class="status-pill warning"><span>OCR Not Configured</span></div>'
    )

    header_html = f"""
    <div class="platform-header">
        <div>
            <div class="brand-title">
                <span style="color: #0875FF;">Notice2Action</span>
                <span style="color: #F2F6FF; font-weight: 500;">AI</span>
                <span style="font-size: 0.65rem; background: rgba(8, 117, 255, 0.2); color: #60A5FA; border: 1px solid rgba(8, 117, 255, 0.4); padding: 2px 7px; border-radius: 4px; font-weight: 700; font-family: monospace; vertical-align: middle;">PS02</span>
            </div>
            <div class="brand-subtitle">
                Notice-to-Action Accessibility Assistant &bull; HackDay@Meerut &bull; Best Use of Gemma 4
            </div>
        </div>
        <div class="header-status-group">
            {ocr_badge}
            <div class="{pill_class}">
                <div style="width: 7px; height: 7px; background-color: {dot_color}; border-radius: 50%; box-shadow: 0 0 8px {dot_color};"></div>
                <span>{status_text}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def render_intro_workflow_panel(current_step: int = 1):
    """Renders the top wide introduction panel with the 3-stage horizontal workflow stepper."""
    s1_class = "active" if current_step >= 1 else ""
    s2_class = "active" if current_step >= 2 else ""
    s3_class = "active" if current_step >= 3 else ""

    panel_html = f"""
    <div class="intro-panel">
        <div class="intro-left">
            <div class="intro-icon-box">
                📄
            </div>
            <div>
                <div class="intro-title">Make Every Notice Actionable</div>
                <div class="intro-desc">
                    Upload a notice or paste its text, extract key information with evidence, and receive accessible next steps.
                </div>
            </div>
        </div>
        <div class="workflow-stepper">
            <div class="workflow-step {s1_class}">
                <span class="workflow-badge">1</span>
                <span>Upload</span>
            </div>
            <span class="workflow-arrow">&rarr;</span>
            <div class="workflow-step {s2_class}">
                <span class="workflow-badge">2</span>
                <span>Extract &amp; Verify</span>
            </div>
            <span class="workflow-arrow">&rarr;</span>
            <div class="workflow-step {s3_class}">
                <span class="workflow-badge">3</span>
                <span>Summary &amp; Actions</span>
            </div>
        </div>
    </div>
    """
    st.markdown(panel_html, unsafe_allow_html=True)


def render_notice_overview(sn: StructuredNotice):
    """Renders the top-level metric overview grid for quick scanning."""
    purpose_val = sn.purpose.value[:50] + ("..." if len(sn.purpose.value) > 50 else "")
    deadline_val = sn.deadline.value[:35] + ("..." if len(sn.deadline.value) > 35 else "")
    elig_val = sn.eligibility.value[:40] + ("..." if len(sn.eligibility.value) > 40 else "")

    missing_cnt = len(sn.missing_information)
    grounding_status = f"{missing_cnt} Missing Field(s)" if missing_cnt > 0 else "100% Grounded"
    grounding_color = "#F59E0B" if missing_cnt > 0 else "#10B981"

    overview_html = f"""
    <div class="overview-grid">
        <div class="overview-metric">
            <div class="metric-title">Notice Purpose</div>
            <div class="metric-value">{purpose_val}</div>
        </div>
        <div class="overview-metric">
            <div class="metric-title">Critical Deadline</div>
            <div class="metric-value metric-highlight">{deadline_val}</div>
        </div>
        <div class="overview-metric">
            <div class="metric-title">Eligibility Criteria</div>
            <div class="metric-value">{elig_val}</div>
        </div>
        <div class="overview-metric">
            <div class="metric-title">Grounding Status</div>
            <div class="metric-value" style="color: {grounding_color};">{grounding_status}</div>
        </div>
    </div>
    """
    st.markdown(overview_html, unsafe_allow_html=True)


def render_analysis_banner(elapsed_seconds: float, model_name: str = "gemma4:latest", field_count: int = 8):
    """Renders a verified analysis summary banner with real timing and status."""
    banner_html = f"""
    <div class="status-banner success">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span>✓</span>
            <span>Gemma 4 Semantic Analysis Complete</span>
            <span style="color: #9EB5D8; font-weight: 400;">&bull; {field_count} Grounded Fields Verified</span>
        </div>
        <div style="font-family: monospace; color: #9EB5D8; font-size: 0.775rem;">
            Latency: <strong style="color: #F2F6FF;">{elapsed_seconds:.2f}s</strong> &bull; Engine: {model_name}
        </div>
    </div>
    """
    st.markdown(banner_html, unsafe_allow_html=True)


def render_recovery_box(error_msg: str, remedy: Optional[str] = None):
    """Renders a structured recovery guidance card when inference encounters an issue."""
    remedy_html = f"<div style='margin-top: 0.35rem; color: #F2F6FF; font-size: 0.8rem;'><strong>Action:</strong> {remedy}</div>" if remedy else ""
    recovery_html = f"""
    <div style="
        background: rgba(248, 113, 113, 0.12);
        border: 1px solid rgba(248, 113, 113, 0.35);
        border-radius: 8px;
        padding: 0.85rem 1.1rem;
        margin-top: 0.75rem;
        margin-bottom: 1rem;
    ">
        <div style="font-weight: 700; color: #F87171; font-size: 0.875rem; display: flex; align-items: center; gap: 0.5rem;">
            <span>⚠ Inference Recovery Protocol</span>
        </div>
        <div style="color: #CBD5E1; font-size: 0.825rem; margin-top: 0.35rem;">
            {error_msg}
        </div>
        {remedy_html}
    </div>
    """
    st.markdown(recovery_html, unsafe_allow_html=True)


def render_fact_card(fact: ExtractedFact, key_prefix: str = "fact"):
    """Renders an elevated dark fact card with quotation citation and confirmation controls."""
    badge_html = render_status_badge(fact.status)
    display_title = fact.field_name.replace("_", " ").title()

    card_header = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
        <span style="font-size: 0.75rem; font-weight: 700; color: #9EB5D8; text-transform: uppercase; letter-spacing: 0.05em;">{display_title}</span>
        {badge_html}
    </div>
    """

    with st.container(border=True):
        st.markdown(card_header, unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 0.95rem; font-weight: 600; color: #F2F6FF; line-height: 1.45;'>{fact.value}</div>", unsafe_allow_html=True)

        if fact.evidence_quote:
            loc_str = f"<span class='source-line'>Source: {fact.source_location}</span>" if fact.source_location else ""
            quote_html = f"""
            <div class="evidence-quote">
                &ldquo;{fact.evidence_quote}&rdquo;
                {loc_str}
            </div>
            """
            st.markdown(quote_html, unsafe_allow_html=True)

        if fact.explanation:
            st.caption(f"ℹ️ {fact.explanation}")

        # Confirmation Gate for uncertain details
        if fact.requires_confirmation and not fact.user_confirmed:
            st.warning("⚠️ This detail was identified as tentative or requiring verification.", icon="⚠️")
            c1, c2 = st.columns([1, 2])
            with c1:
                if st.button("Confirm detail as accurate", key=f"{key_prefix}_confirm_{fact.field_name}"):
                    fact.user_confirmed = True
                    fact.requires_confirmation = False
                    st.rerun()


def render_quick_summary_card(summary: PlainLanguageSummary, model_name: str = "gemma4:latest"):
    """Renders the Quick Summary assistance card for the right-hand dashboard region."""
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem;">
                <span class="card-label" style="margin-bottom: 0;">📌 Quick Summary</span>
                <span style="font-size: 0.65rem; background: rgba(8, 117, 255, 0.15); color: #60A5FA; border: 1px solid rgba(8, 117, 255, 0.3); padding: 1px 6px; border-radius: 4px; font-family: monospace;">{model_name}</span>
            </div>
            <div style="font-size: 0.85rem; font-weight: 600; color: #F2F6FF; margin-bottom: 0.4rem;">
                {summary.about}
            </div>
            <div style="font-size: 0.775rem; color: #9EB5D8; margin-bottom: 0.35rem;">
                <strong style="color: #F2F6FF;">Deadline:</strong> {summary.deadline}
            </div>
            <div style="font-size: 0.775rem; color: #9EB5D8; margin-bottom: 0.35rem;">
                <strong style="color: #F2F6FF;">Eligibility:</strong> {summary.eligible}
            </div>
            <div style="font-size: 0.775rem; color: #9EB5D8;">
                <strong style="color: #F2F6FF;">Documents:</strong> {summary.documents}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_checklist_widget(checklist: ActionChecklist, key_prefix: str = "widget"):
    """Renders the Action Checklist assistance card for the right-hand dashboard region."""
    with st.container(border=True):
        total_steps = len(checklist.items)
        completed_count = sum(1 for item in checklist.items if item.is_completed)

        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem;">
                <span class="card-label" style="margin-bottom: 0;">⚡ Action Checklist</span>
                <span style="font-size: 0.7rem; color: #10B981; font-weight: 700; font-family: monospace;">{completed_count}/{total_steps} Done</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for item in checklist.items:
            is_checked = st.checkbox(
                f"Step {item.step_number}: {item.action}",
                value=item.is_completed,
                key=f"{key_prefix}_check_{item.step_number}",
            )
            item.is_completed = is_checked

        st.markdown("<div style='margin-top: 0.45rem;'></div>", unsafe_allow_html=True)
        if hasattr(checklist, "to_ics_bytes"):
            ics_bytes = checklist.to_ics_bytes()
        else:
            ics_bytes = b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Notice2Action AI//EN\r\nEND:VCALENDAR"
        st.download_button(
            "📅 Download Calendar (.ics)",
            data=ics_bytes,
            file_name="notice_deadline.ics",
            mime="text/calendar",
            use_container_width=True,
            key=f"{key_prefix}_ics_download",
        )


def render_qa_shortcut():
    """Renders the Follow-Up Q&A assistance shortcut card."""
    with st.container(border=True):
        st.markdown(
            """
            <div class="card-label">💬 Follow-Up Assistant</div>
            <div style="font-size: 0.8rem; color: #9EB5D8; margin-bottom: 0.45rem;">
                Have questions about fees, submission rooms, or eligibility?
            </div>
            <div style="font-size: 0.75rem; color: #60A5FA;">
                &bull; "Is there an application fee?"<br/>
                &bull; "Where is Room 204 located?"
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_summary_section(summary: PlainLanguageSummary, lang: str = "en"):
    """Renders the 7 plain-language summary answers in clean dark cards."""
    st.markdown("#### 📋 Plain-Language Summary", help="Concise answers to the 7 core questions")

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("<span class='card-label'>📌 What is this notice about?</span>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-value'>{summary.about}</div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("<span class='card-label'>👥 Who is eligible?</span>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-value'>{summary.eligible}</div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("<span class='card-label'>🎯 What must the reader do?</span>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-value'>{summary.actions}</div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("<span class='card-label'>📁 Required documents:</span>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-value'>{summary.documents}</div>", unsafe_allow_html=True)

    with c2:
        with st.container(border=True):
            st.markdown("<span class='card-label'>⏳ Deadline:</span>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-value' style='color: #38BDF8;'>{summary.deadline}</div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("<span class='card-label'>📞 Contact & Helpdesk:</span>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-value'>{summary.help_contact}</div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("<span class='card-label'>❓ Missing Information:</span>", unsafe_allow_html=True)
            missing_color = "#F59E0B" if "missing" in summary.missing.lower() else "#9EB5D8"
            st.markdown(f"<div class='card-value' style='color: {missing_color};'>{summary.missing}</div>", unsafe_allow_html=True)

    # Read Aloud Audio
    full_summary_text = (
        f"Notice Summary. What it is about: {summary.about}. "
        f"Eligibility: {summary.eligible}. "
        f"Actions to take: {summary.actions}. "
        f"Required documents: {summary.documents}. "
        f"Deadline: {summary.deadline}. "
        f"Contact: {summary.help_contact}. "
        f"Missing information: {summary.missing}."
    )
    st.markdown("---")
    st.markdown("##### 🔊 Audio Accessibility (Read Aloud)")

    audio_key = f"audio_{lang}_{hash(full_summary_text)}"
    if audio_key not in st.session_state:
        st.session_state[audio_key] = generate_audio_bytes(full_summary_text, lang="hi" if lang == "hi" else "en")

    audio_bytes = st.session_state.get(audio_key)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")
    else:
        lang_code = "hi-IN" if lang == "hi" else "en-US"
        st.markdown(get_web_speech_js(full_summary_text, lang_code), unsafe_allow_html=True)


def render_checklist_section(checklist: ActionChecklist):
    """Renders the ordered, interactive action checklist in dark SaaS styling."""
    st.markdown("#### ✅ Grounded Action Checklist", help="Sequenced action steps verified against notice text")

    if not checklist.items:
        st.info("No actionable items were identified for this notice.")
        return

    for item in checklist.items:
        with st.container(border=True):
            col_check, col_desc = st.columns([0.08, 0.92])
            with col_check:
                is_checked = st.checkbox(
                    f"Step {item.step_number}",
                    value=item.is_completed,
                    key=f"check_item_{item.step_number}",
                    label_visibility="collapsed",
                )
                item.is_completed = is_checked

            with col_desc:
                cat_badge = f"<span class='badge-tag badge-category'>{item.category}</span>"
                mand_badge = "<span class='badge-tag badge-mandatory'>MANDATORY</span>" if item.is_mandatory else "<span class='badge-tag badge-advisory'>ADVISORY</span>"

                action_style = "text-decoration: line-through; color: #64748B;" if is_checked else "color: #F2F6FF; font-weight: 600;"
                st.markdown(
                    f"<div style='display: flex; align-items: center; justify-content: space-between;'>"
                    f"<span style='{action_style} font-size: 0.95rem;'>Step {item.step_number}: {item.action}</span>"
                    f"<div>{cat_badge} {mand_badge}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                if item.requires_confirmation:
                    st.caption("⚠️ *Requires confirmation before acting on tentative notice detail.*")
                if item.grounded_quote:
                    st.caption(f"Evidence quote: \"{item.grounded_quote}\"")
                if item.notes:
                    st.caption(f"Note: {item.notes}")


def render_qa_item(item):
    """Renders a single grounded Q&A card."""
    with st.container(border=True):
        st.markdown(
            f"<div class='qa-question'>"
            f"<span style='color: #38BDF8;'>Q:</span> {item.question}"
            f"</div>",
            unsafe_allow_html=True,
        )
        if item.is_supported:
            st.markdown(f"<div class='qa-answer'><strong style='color: #10B981;'>A:</strong> {item.answer}</div>", unsafe_allow_html=True)
            if item.evidence_quote:
                st.markdown(f"<div class='qa-evidence'>&ldquo;{item.evidence_quote}&rdquo;</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='qa-answer'><strong style='color: #F87171;'>A:</strong> {item.answer}</div>", unsafe_allow_html=True)
            st.markdown("<span style='color: #F87171; font-size: 11px; font-weight: bold; background: rgba(248, 113, 113, 0.15); padding: 2px 7px; border-radius: 4px; border: 1px solid rgba(248, 113, 113, 0.3);'>⚠️ Information not stated in the supplied notice</span>", unsafe_allow_html=True)
