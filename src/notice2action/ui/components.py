"""
Reusable Accessible UI Components for Notice2Action AI (Streamlit).
Designed for high contrast, keyboard accessibility, and clear status visualization.
"""

from __future__ import annotations

import streamlit as st
from typing import Optional, Callable
from notice2action.schemas import (
    CertaintyStatus,
    ExtractedFact,
    ChecklistItem,
    PlainLanguageSummary,
    ActionChecklist,
)
from notice2action.tts import generate_audio_bytes, get_web_speech_js


STATUS_COLORS = {
    CertaintyStatus.STATED: {"bg": "#dcfce7", "text": "#166534", "border": "#86efac", "icon": "✓ Stated"},
    CertaintyStatus.NOT_STATED: {"bg": "#f1f5f9", "text": "#475569", "border": "#cbd5e1", "icon": "✕ Not Stated"},
    CertaintyStatus.UNCERTAIN: {"bg": "#fef3c7", "text": "#92400e", "border": "#fcd34d", "icon": "⚠ Needs Confirmation"},
    CertaintyStatus.CONFLICTING: {"bg": "#ffe4e6", "text": "#9f1239", "border": "#f43f5e", "icon": "⚡ Conflicting"},
    CertaintyStatus.UNREADABLE: {"bg": "#f3f4f6", "text": "#374151", "border": "#9ca3af", "icon": "❓ Unreadable"},
}


def render_status_badge(status: CertaintyStatus) -> str:
    """Returns HTML for an accessible, color-coded status badge."""
    info = STATUS_COLORS.get(status, STATUS_COLORS[CertaintyStatus.UNCERTAIN])
    return (
        f"<span style='"
        f"background-color: {info['bg']}; "
        f"color: {info['text']}; "
        f"border: 1px solid {info['border']}; "
        f"padding: 3px 8px; "
        f"border-radius: 9999px; "
        f"font-size: 11px; "
        f"font-weight: 700; "
        f"font-family: monospace;'>"
        f"{info['icon']}"
        f"</span>"
    )


def render_fact_card(fact: ExtractedFact, key_prefix: str = "fact"):
    """Renders a single structured fact card with evidence quotation and confirmation controls."""
    badge_html = render_status_badge(fact.status)
    display_title = fact.field_name.replace("_", " ").title()

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(
                f"<div style='font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 4px;'>"
                f"{display_title} &nbsp; {badge_html}"
                f"</div>",
                unsafe_allow_html=True,
            )
        with col2:
            if fact.user_confirmed:
                st.markdown("<span style='color: #16a34a; font-weight: 600; font-size: 12px;'>✓ Confirmed by User</span>", unsafe_allow_html=True)

        st.markdown(f"**Value:** {fact.value}")

        if fact.evidence_quote:
            loc_str = f" ({fact.source_location})" if fact.source_location else ""
            st.markdown(
                f"<div style='border-left: 3px solid #3b82f6; padding-left: 10px; margin-top: 6px; color: #475569; font-style: italic; font-size: 13px;'>"
                f"\"{fact.evidence_quote}\"{loc_str}"
                f"</div>",
                unsafe_allow_html=True,
            )

        if fact.explanation:
            st.caption(f"ℹ️ {fact.explanation}")

        # Confirmation Gate for uncertain details
        if fact.requires_confirmation and not fact.user_confirmed:
            st.warning("⚠️ This detail was identified as tentative, incomplete, or needing verification.", icon="⚠️")
            c1, c2 = st.columns([1, 2])
            with c1:
                if st.button("Confirm detail as accurate", key=f"{key_prefix}_confirm_{fact.field_name}"):
                    fact.user_confirmed = True
                    fact.requires_confirmation = False
                    st.rerun()


def render_summary_section(summary: PlainLanguageSummary, lang: str = "en"):
    """Renders the 7 plain-language summary answers."""
    st.subheader("📋 Plain-Language Summary", divider="blue")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**📌 What is this notice about?**\n\n{summary.about}")
        st.markdown(f"**👥 Who is eligible?**\n\n{summary.eligible}")
        st.markdown(f"**🎯 What must the reader do?**\n\n{summary.actions}")
        st.markdown(f"**📁 Required documents:**\n\n{summary.documents}")

    with c2:
        st.markdown(f"**⏳ Deadline:**\n\n{summary.deadline}")
        st.markdown(f"**📞 Where to get help / Contact:**\n\n{summary.help_contact}")
        st.markdown(f"**❓ Missing critical information:**\n\n{summary.missing}")

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
    col_audio, col_btn = st.columns([2, 1])
    with col_audio:
        audio_bytes = generate_audio_bytes(full_summary_text, lang="hi" if lang == "hi" else "en")
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
        else:
            lang_code = "hi-IN" if lang == "hi" else "en-US"
            st.markdown(get_web_speech_js(full_summary_text, lang_code), unsafe_allow_html=True)


def render_checklist_section(checklist: ActionChecklist):
    """Renders the ordered, interactive action checklist."""
    st.subheader("✅ Action Checklist", divider="green")

    if not checklist.items:
        st.info("No actionable items were identified for this notice.")
        return

    for item in checklist.items:
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
            cat_badge = f"<span style='background: #e0f2fe; color: #0369a1; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold;'>{item.category.upper()}</span>"
            mand_badge = "<span style='background: #fee2e2; color: #b91c1c; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold;'>MANDATORY</span>" if item.is_mandatory else "<span style='background: #f1f5f9; color: #475569; padding: 2px 6px; border-radius: 4px; font-size: 11px;'>ADVISORY</span>"

            action_text = f"<s>{item.action}</s>" if is_checked else f"**Step {item.step_number}:** {item.action}"

            st.markdown(f"{action_text} &nbsp; {cat_badge} {mand_badge}", unsafe_allow_html=True)

            if item.requires_confirmation:
                st.caption("⚠️ *Requires confirmation before acting on tentative notice detail.*")
            if item.grounded_quote:
                st.caption(f"Evidence quote: \"{item.grounded_quote}\"")
            if item.notes:
                st.caption(f"Note: {item.notes}")
