"""
Notice2Action AI (PS02)
Notice-to-Action Accessibility Assistant powered by Gemma 4.
HackDay@Meerut × E-Cell IIMT University | Hacktoberfest 2026.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src/ is on python module path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import time
import json
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

from notice2action.config import config, run_preflight_diagnostics
from notice2action.schemas import (
    CertaintyStatus,
    StructuredNotice,
    PlainLanguageSummary,
    ActionChecklist,
)
from notice2action.ingestion import ingest_uploaded_file, ingest_pasted_text
from notice2action.ocr import extract_text_from_image, get_available_tesseract_languages
from notice2action.llm.ollama_client import OllamaClient
from notice2action.analysis import NoticeAnalyzer
from notice2action.summary import generate_accessible_summary, generate_deterministic_summary
from notice2action.checklist import generate_action_checklist
from notice2action.translation import translate_summary_to_hindi, translate_checklist_to_hindi
from notice2action.followup import FollowUpAssistant
from notice2action.ui.styles import THEME_CSS
from notice2action.ui.components import (
    render_platform_header,
    render_intro_workflow_panel,
    render_notice_overview,
    render_analysis_banner,
    render_recovery_box,
    render_fact_card,
    render_quick_summary_card,
    render_checklist_widget,
    render_qa_shortcut,
    render_summary_section,
    render_checklist_section,
    render_qa_item,
)

# Streamlit Page Setup
st.set_page_config(
    page_title="Notice2Action AI — PS02 Assistant",
    page_icon="📢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Centralized Dark Theme Tokens & CSS
st.markdown(THEME_CSS, unsafe_allow_html=True)


TAB_NAMES = [
    "📥 Notice Ingestion & OCR",
    "🔍 Grounded Fact Breakdown",
    "📋 Summary & Action Checklist",
    "💬 Follow-Up Q&A",
]


def set_active_tab(target_idx: int):
    """Sets the active dashboard tab index."""
    st.session_state.active_tab_index = target_idx


def set_qa_inquiry(question_text: str):
    """Sets the active Q&A input question buffer."""
    st.session_state.qa_input_text_box = question_text


def init_session_state():
    """Initializes session state to ensure clean data isolation."""
    if "raw_notice_text" not in st.session_state:
        st.session_state.raw_notice_text = ""
    if "ocr_confidence" not in st.session_state:
        st.session_state.ocr_confidence = None
    if "uploaded_image" not in st.session_state:
        st.session_state.uploaded_image = None
    if "structured_notice" not in st.session_state:
        st.session_state.structured_notice = None
    if "summary_en" not in st.session_state:
        st.session_state.summary_en = None
    if "summary_hi" not in st.session_state:
        st.session_state.summary_hi = None
    if "checklist_en" not in st.session_state:
        st.session_state.checklist_en = None
    if "checklist_hi" not in st.session_state:
        st.session_state.checklist_hi = None
    if "followup_history" not in st.session_state:
        st.session_state.followup_history = []
    if "selected_lang" not in st.session_state:
        st.session_state.selected_lang = "en"
    if "analysis_duration" not in st.session_state:
        st.session_state.analysis_duration = None
    if "analysis_error" not in st.session_state:
        st.session_state.analysis_error = None
    if "active_tab_index" not in st.session_state:
        st.session_state.active_tab_index = 0
    if "qa_input_text_box" not in st.session_state:
        st.session_state.qa_input_text_box = ""


init_session_state()

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div style="font-size: 1.15rem; font-weight: 800; color: #F2F6FF; display: flex; align-items: center; gap: 0.45rem;">
                <span style="color: #0875FF;">Notice2Action</span>
                <span>AI</span>
                <span style="font-size: 0.65rem; background: #0875FF; color: white; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-family: monospace;">PS02</span>
            </div>
            <div style="font-size: 0.75rem; color: #9EB5D8; margin-top: 3px;">
                Notice-to-Action Accessibility Assistant
            </div>
            <div style="font-size: 0.7rem; color: #64748B; margin-top: 2px;">
                HackDay@Meerut &bull; Best Use of Gemma 4
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Interactive Sidebar Navigation
    st.markdown("<span class='card-label'>🧭 Navigation</span>", unsafe_allow_html=True)
    nav_tabs = [
        (0, "📥 1. Process Notice"),
        (1, "🔍 2. Extracted Facts"),
        (2, "📋 3. Summary & Actions"),
        (3, "💬 4. Follow-Up Q&A"),
    ]
    cur_idx = st.session_state.get("active_tab_index", 0)
    for idx, label in nav_tabs:
        btn_type = "primary" if cur_idx == idx else "secondary"
        st.button(
            label,
            key=f"sidebar_nav_{idx}",
            type=btn_type,
            use_container_width=True,
            on_click=set_active_tab,
            args=(idx,),
        )

    st.markdown("<div style='margin-bottom: 0.65rem;'></div>", unsafe_allow_html=True)

    # Diagnostics Drawer & System Status
    st.markdown("<span class='card-label'>⚡ System Status</span>", unsafe_allow_html=True)
    diag = run_preflight_diagnostics()
    if diag.overall_status == "ok":
        st.success(f"System Ready • {config.ollama_model}", icon="✅")
    elif diag.overall_status == "warning":
        st.warning("Warning • Check Preflight", icon="⚠️")
    else:
        st.error("Error • Ollama Offline", icon="❌")

    with st.expander("🔍 Diagnostics Ledger"):
        for item in diag.items:
            icon = "✓" if item.status == "ok" else ("⚠" if item.status == "warning" else "✕")
            st.markdown(f"**{icon} {item.name}**")
            st.caption(item.details)
            if item.remedy:
                st.info(f"Remedy: {item.remedy}")

    st.markdown("---")

    # Quick-load Synthetic Demo Fixtures
    st.markdown("<span class='card-label'>🧪 Quick-Load Samples</span>", unsafe_allow_html=True)
    fixtures_dir = config.synthetic_fixtures_dir

    if st.button("🎯 Competition Demo (TEST-SCH-2026-001)", type="secondary", use_container_width=True):
        p = fixtures_dir / "synthetic_scholarship_notice.txt"
        if p.is_file():
            st.session_state.raw_notice_text = p.read_text(encoding="utf-8")
            st.session_state.uploaded_image = None
            st.session_state.structured_notice = None
            st.session_state.analysis_error = None
            st.session_state.followup_history = []
            st.rerun()

    sample_dict = {
        "📄 Scholarship Notice (EN)": "sample_scholarship_notice.txt",
        "🏛️ College Circular (EN)": "synthetic_scholarship_notice.txt",
        "🇮🇳 Notice (Hindi)": "sample_hindi_notice.txt",
        "🖼️ Scanned Notice (OCR Demo)": "synthetic_notice_ocr.png",
        "⚠️ Tentative Dates Notice": "sample_uncertain_notice.txt",
        "❓ Missing Fields Notice": "sample_missing_fields_notice.txt",
    }
    selected_sample_key = st.selectbox(
        "Other Notice Fixtures",
        options=list(sample_dict.keys()),
        index=0,
        label_visibility="collapsed",
        key="sample_fixture_select",
    )
    if st.button("📥 Load Selected Sample", use_container_width=True, key="btn_load_sample"):
        fname = sample_dict[selected_sample_key]
        p = fixtures_dir / fname
        if p.is_file():
            if fname.endswith(".png"):
                st.session_state.uploaded_image = Image.open(p)
                st.session_state.raw_notice_text = ""
            else:
                st.session_state.raw_notice_text = p.read_text(encoding="utf-8")
                st.session_state.uploaded_image = None
            st.session_state.structured_notice = None
            st.session_state.analysis_error = None
            st.session_state.followup_history = []
            if "Hindi" in selected_sample_key:
                st.session_state.selected_lang = "hi"
            st.rerun()

    st.markdown("---")

    # Language Selector
    lang_choice = st.radio(
        "🌐 Output Language",
        options=["English", "हिन्दी (Hindi)"],
        index=0 if st.session_state.selected_lang == "en" else 1,
    )
    st.session_state.selected_lang = "hi" if "Hindi" in lang_choice else "en"

    st.markdown("---")
    if st.button("🔄 Reset Session", use_container_width=True):
        st.session_state.raw_notice_text = ""
        st.session_state.uploaded_image = None
        st.session_state.structured_notice = None
        st.session_state.summary_en = None
        st.session_state.summary_hi = None
        st.session_state.checklist_en = None
        st.session_state.checklist_hi = None
        st.session_state.analysis_duration = None
        st.session_state.analysis_error = None
        st.session_state.followup_history = []
        st.rerun()

    st.markdown(
        """
        <div style="font-size: 0.68rem; color: #64748B; margin-top: 1.5rem; text-align: center; border-top: 1px solid #1D3D67; padding-top: 0.75rem;">
            <strong>About PS02</strong><br/>
            Notice-to-Action Accessibility Assistant.<br/>
            100% on-device local AI for student privacy.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------- MAIN INTERFACE -----------------
render_platform_header(status=diag.overall_status, model_name=config.ollama_model, ocr_status="ok")
step_val = 3 if st.session_state.structured_notice else (2 if st.session_state.raw_notice_text else 1)
render_intro_workflow_panel(current_step=step_val)


cur_tab_idx = st.session_state.get("active_tab_index", 0)
if cur_tab_idx < 0 or cur_tab_idx >= len(TAB_NAMES):
    cur_tab_idx = 0


def on_main_tabs_change():
    """Callback when a tab is directly clicked in the main dashboard tab strip."""
    sel = st.session_state.get(f"main_dashboard_tabs_{cur_tab_idx}")
    if sel in TAB_NAMES:
        st.session_state.active_tab_index = TAB_NAMES.index(sel)


tab_input, tab_structured, tab_summary, tab_followup = st.tabs(
    TAB_NAMES,
    key=f"main_dashboard_tabs_{cur_tab_idx}",
    default=TAB_NAMES[cur_tab_idx],
    on_change=on_main_tabs_change,
)

# ----------------- TAB 1: INGESTION & OCR -----------------
with tab_input:
    st.markdown(
        """
        <div class="panel-header">
            <div class="panel-title">1 Add Your Notice</div>
            <div class="panel-subtitle">Upload a document or paste the text of the notice.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_upload, col_paste = st.columns([1, 1.25], gap="medium")

    with col_upload:
        st.markdown(
            """
            <div style="margin-bottom: 0.35rem;">
                <span class="card-label" style="margin-bottom: 0;">📁 1. Upload Notice Document</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Upload Notice Document",
            type=["png", "jpg", "jpeg", "webp", "txt"],
            help="Supported formats: PNG, JPG, JPEG, WEBP, TXT. Max size: 10 MB.",
            label_visibility="collapsed",
            key="file_uploader_widget",
        )
        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            ingest_res = ingest_uploaded_file(uploaded_file.name, bytes_data)
            if ingest_res.error:
                st.error(f"Upload Error: {ingest_res.error}")
            else:
                size_kb = len(bytes_data) / 1024
                st.markdown(
                    f"<div style='font-size: 0.75rem; color: #34D399; font-family: monospace; margin: 0.25rem 0 0.5rem 0;'>"
                    f"✓ Selected: {uploaded_file.name} ({size_kb:.1f} KB)"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                if ingest_res.source_type == "image":
                    st.session_state.uploaded_image = ingest_res.image
                    st.session_state.structured_notice = None
                    st.session_state.analysis_error = None
                elif ingest_res.source_type == "text":
                    st.session_state.raw_notice_text = ingest_res.raw_text
                    st.session_state.uploaded_image = None
                    st.session_state.structured_notice = None
                    st.session_state.analysis_error = None
                    st.success(f"Loaded text file '{ingest_res.filename}' ({ingest_res.char_count} chars).")
                    st.rerun()

        if st.session_state.uploaded_image is not None:
            st.image(st.session_state.uploaded_image, caption="Loaded Notice Preview", use_container_width=True)

            c_ocr1, c_ocr2 = st.columns(2)
            with c_ocr1:
                ocr_lang = st.selectbox(
                    "OCR Language",
                    ["eng (English)", "hin (Hindi)", "eng+hin (Bilingual)"],
                    index=0,
                    key="ocr_lang_select",
                )
            with c_ocr2:
                apply_prep = st.checkbox("Enhance Contrast", value=True, key="ocr_prep_chk")

            c_btn_ocr1, c_btn_ocr2 = st.columns([1.5, 1])
            with c_btn_ocr1:
                if st.button("⚙️ Run Tesseract OCR", type="primary", use_container_width=True, key="btn_run_ocr"):
                    with st.spinner("Extracting text via Tesseract OCR..."):
                        lang_code = "hin" if "hin" in ocr_lang and "+" not in ocr_lang else ("eng+hin" if "+" in ocr_lang else "eng")
                        ocr_res = extract_text_from_image(st.session_state.uploaded_image, target_lang=lang_code, apply_preprocessing=apply_prep)
                        if ocr_res.error:
                            st.error(ocr_res.error)
                        else:
                            st.session_state.raw_notice_text = ocr_res.extracted_text
                            st.session_state.ocr_confidence = ocr_res.confidence_score
                            st.session_state.structured_notice = None
                            st.session_state.analysis_error = None
                            if ocr_res.warning:
                                st.warning(ocr_res.warning)
                            st.success(f"Extracted {ocr_res.line_count} lines (Confidence: {ocr_res.confidence_score}%)")
                            st.rerun()
            with c_btn_ocr2:
                if st.button("🗑️ Reset Image", use_container_width=True, key="btn_reset_ocr_img"):
                    st.session_state.uploaded_image = None
                    st.session_state.raw_notice_text = ""
                    st.session_state.ocr_confidence = None
                    st.rerun()

    with col_paste:
        char_count = len(st.session_state.raw_notice_text)
        line_count = len(st.session_state.raw_notice_text.splitlines()) if st.session_state.raw_notice_text else 0
        buf_color = "#34D399" if char_count > 0 else "#64748B"

        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                <span class="card-label" style="margin-bottom: 0;">✍️ 2. Notice Content / Ground-Truth Buffer</span>
                <span style="font-size: 0.725rem; font-family: monospace; color: {buf_color}; font-weight: 600;">
                    {char_count} chars &bull; {line_count} lines
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        edited_text = st.text_area(
            "Notice Content for Analysis",
            value=st.session_state.raw_notice_text,
            height=200,
            label_visibility="collapsed",
            placeholder="Paste notice text here, or upload a notice image/file on the left. You can also click '⚡ Load Demo Notice' below.",
            help="This buffer serves as the authoritative ground truth for all evidence citations and grounding checks.",
        )
        if edited_text != st.session_state.raw_notice_text:
            st.session_state.raw_notice_text = edited_text

        col_act1, col_act2 = st.columns([1.5, 1])
        with col_act1:
            if st.button("⚡ Load Demo Notice (TEST-SCH-2026-001)", type="secondary", use_container_width=True):
                p = fixtures_dir / "synthetic_scholarship_notice.txt"
                if p.is_file():
                    st.session_state.raw_notice_text = p.read_text(encoding="utf-8")
                    st.session_state.uploaded_image = None
                    st.session_state.structured_notice = None
                    st.session_state.analysis_error = None
                    st.session_state.followup_history = []
                    st.rerun()
        with col_act2:
            if st.button("🗑️ Clear Buffer", use_container_width=True):
                st.session_state.raw_notice_text = ""
                st.session_state.uploaded_image = None
                st.session_state.structured_notice = None
                st.session_state.analysis_error = None
                st.session_state.followup_history = []
                st.rerun()

    # Dominant Primary Analyze Button spanning below both columns
    st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
    analyze_btn = st.button("🚀 Analyze Notice with Gemma 4", type="primary", use_container_width=True)

    # Success Banner with interactive jump buttons if notice has been analyzed
    if st.session_state.structured_notice is not None:
        dur = f"{st.session_state.analysis_duration:.2f}s" if st.session_state.analysis_duration else "complete"
        st.markdown(
            f"""
            <div style="margin-top: 0.65rem; padding: 0.55rem 0.85rem; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px;">
                <div style="font-size: 0.85rem; font-weight: 700; color: #34D399; margin-bottom: 0.4rem;">
                    ✅ Notice Analyzed ({dur}) &bull; 8 Key Fields Grounded &bull; Ready to Review
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_jump1, col_jump2, col_jump3 = st.columns(3)
        with col_jump1:
            st.button(
                "🔍 View Grounded Facts (Tab 2)",
                type="secondary",
                use_container_width=True,
                key="btn_jump_tab2",
                on_click=set_active_tab,
                args=(1,),
            )
        with col_jump2:
            st.button(
                "📋 View Summary & Checklist (Tab 3)",
                type="secondary",
                use_container_width=True,
                key="btn_jump_tab3",
                on_click=set_active_tab,
                args=(2,),
            )
        with col_jump3:
            st.button(
                "💬 Ask Follow-Up Q&A (Tab 4)",
                type="secondary",
                use_container_width=True,
                key="btn_jump_tab4",
                on_click=set_active_tab,
                args=(3,),
            )

    # Recovery box if previous analysis failed
    if st.session_state.analysis_error:
        render_recovery_box(
            st.session_state.analysis_error,
            remedy="Ensure Ollama is running ('ollama serve') and model 'gemma4:latest' is pulled. You can click 'Analyze Notice with Gemma 4' to retry."
        )

    if analyze_btn:
        if not st.session_state.raw_notice_text.strip():
            st.error("Please supply notice text or upload a notice document first.")
        else:
            with st.status("Analyzing notice with local Gemma 4...", expanded=True) as status_box:
                start_t = time.time()
                st.write("🔍 **Phase 1/5:** Validating notice input and security boundaries...")
                time.sleep(0.04)

                st.write("📄 **Phase 2/5:** Inspecting document format and OCR text normalization...")
                time.sleep(0.04)

                analyzer = NoticeAnalyzer()
                try:
                    st.write("🤖 **Phase 3/5:** Calling local Gemma 4 for structured fact extraction...")
                    structured = analyzer.analyze_notice(st.session_state.raw_notice_text)
                    st.session_state.structured_notice = structured

                    st.write("🔬 **Phase 4/5:** Validating structured output and verbatim evidence quotes...")
                    time.sleep(0.04)

                    st.write("📋 **Phase 5/5:** Synthesizing plain-language summary & action checklist...")
                    st.session_state.summary_en = generate_deterministic_summary(structured)
                    st.session_state.checklist_en = generate_action_checklist(structured)

                    # Deterministic multilingual translation with entity audit
                    st.session_state.summary_hi = translate_summary_to_hindi(st.session_state.summary_en, client=None)
                    st.session_state.checklist_hi = translate_checklist_to_hindi(st.session_state.checklist_en, client=None)

                    elapsed = time.time() - start_t
                    st.session_state.analysis_duration = elapsed
                    st.session_state.analysis_error = None

                    status_box.update(label=f"✅ Analysis complete in {elapsed:.2f}s! Proceed to Tab 2 or Tab 3.", state="complete", expanded=False)
                    st.rerun()
                except Exception as e:
                    st.session_state.analysis_error = str(e)
                    status_box.update(label="❌ Analysis Failed", state="error", expanded=True)
                    st.error(f"Analysis failed: {e}")

    # Two-column assistance dashboard (approx 65% / 35%) when notice is analyzed
    if st.session_state.structured_notice is not None:
        st.markdown("<hr style='border: none; border-top: 1px solid #1D3D67; margin: 1.5rem 0;'>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="margin-bottom: 0.75rem;">
                <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">⚡ Fast Assistance & Overview</div>
                <div style="font-size: 0.8rem; color: #94A3B8;">Immediate extraction results. Full grounded breakdown and interactive checklist are available in Tabs 2, 3, and 4.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_res_main, col_res_side = st.columns([1.6, 1], gap="medium")
        with col_res_main:
            render_notice_overview(st.session_state.structured_notice)
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                render_fact_card(st.session_state.structured_notice.purpose, key_prefix="dash_purpose")
                render_fact_card(st.session_state.structured_notice.deadline, key_prefix="dash_deadline")
            with c_f2:
                render_fact_card(st.session_state.structured_notice.eligibility, key_prefix="dash_elig")
                render_fact_card(st.session_state.structured_notice.required_actions, key_prefix="dash_act")
        with col_res_side:
            if st.session_state.summary_en:
                render_quick_summary_card(st.session_state.summary_en, config.ollama_model)
            if st.session_state.checklist_en:
                render_checklist_widget(st.session_state.checklist_en, key_prefix="dash_widget")
            render_qa_shortcut()
            st.button(
                "💬 Open Follow-Up Q&A Assistant",
                use_container_width=True,
                key="btn_open_qa_dash",
                on_click=set_active_tab,
                args=(3,),
            )

            # Export structured data options
            st.download_button(
                "💾 Download Structured Notice (JSON)",
                data=json.dumps(st.session_state.structured_notice.model_dump(), indent=2),
                file_name="structured_notice.json",
                mime="application/json",
                use_container_width=True,
                key="dash_json_download",
            )


# ----------------- TAB 2: STRUCTURED BREAKDOWN -----------------
with tab_structured:
    st.markdown(
        """
        <div style="margin-bottom: 0.85rem;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">2. Grounded Fact Breakdown</div>
            <div style="font-size: 0.8rem; color: #94A3B8;">Structured extraction of 8 key notice fields. Every fact cites an exact verbatim quotation.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.structured_notice is None:
        st.markdown(
            """
            <div class="dark-card" style="text-align: center; padding: 2rem 1rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.35rem;">🔍</div>
                <div style="font-size: 1rem; font-weight: 700; color: #FFFFFF;">No Notice Analyzed Yet</div>
                <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.2rem;">
                    Upload or paste a notice in Tab 1, or click <strong>⚡ Quick-Load Samples</strong> in the sidebar.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        sn: StructuredNotice = st.session_state.structured_notice

        # High-level overview banner
        if st.session_state.analysis_duration:
            render_analysis_banner(st.session_state.analysis_duration, config.ollama_model, 8)

        render_notice_overview(sn)

        # Alert banner for missing or uncertain information
        if sn.missing_information:
            st.warning(f"⚠️ **Missing Information Identified:** {', '.join(sn.missing_information)}", icon="⚠️")
        if sn.uncertain_or_conflicting_details:
            st.info(f"ℹ️ **Uncertain / Tentative Details Flagged:** {', '.join(sn.uncertain_or_conflicting_details)}", icon="ℹ️")

        col_left, col_right = st.columns(2, gap="medium")
        with col_left:
            render_fact_card(sn.purpose, key_prefix="card_purpose")
            render_fact_card(sn.eligibility, key_prefix="card_eligibility")
            render_fact_card(sn.deadline, key_prefix="card_deadline")
            render_fact_card(sn.fee_or_cost, key_prefix="card_fee")

        with col_right:
            render_fact_card(sn.required_documents, key_prefix="card_docs")
            render_fact_card(sn.contact_details, key_prefix="card_contact")
            render_fact_card(sn.required_actions, key_prefix="card_actions")
            render_fact_card(sn.important_conditions, key_prefix="card_conditions")


# ----------------- TAB 3: SUMMARY & CHECKLIST -----------------
with tab_summary:
    st.markdown(
        """
        <div style="margin-bottom: 0.85rem;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">3. Summary & Action Checklist</div>
            <div style="font-size: 0.8rem; color: #94A3B8;">Plain-language synthesis answering 7 core questions, with an ordered execution checklist.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.structured_notice is None:
        st.markdown(
            """
            <div class="dark-card" style="text-align: center; padding: 2rem 1rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.35rem;">📋</div>
                <div style="font-size: 1rem; font-weight: 700; color: #FFFFFF;">Summary Unavailable</div>
                <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.2rem;">
                    Analyze a notice in Tab 1 to generate the plain-language summary and interactive checklist.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        is_hindi = st.session_state.selected_lang == "hi"

        # Display Summary
        cur_summary = st.session_state.summary_hi if is_hindi else st.session_state.summary_en
        if cur_summary:
            render_summary_section(cur_summary, lang=st.session_state.selected_lang)

        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

        # Display Checklist
        cur_checklist = st.session_state.checklist_hi if is_hindi else st.session_state.checklist_en
        if cur_checklist:
            render_checklist_section(cur_checklist)

        # Export Report Option
        st.markdown("---")
        st.markdown("##### 📥 Export Action Plan & Calendar")
        export_text = (
            f"# Notice2Action AI — Action Report\n\n"
            f"**Notice Purpose**: {st.session_state.structured_notice.purpose.value}\n"
            f"**Deadline**: {st.session_state.structured_notice.deadline.value}\n"
            f"**Eligibility**: {st.session_state.structured_notice.eligibility.value}\n\n"
            f"## Plain-Language Summary\n"
            f"- About: {cur_summary.about if cur_summary else ''}\n"
            f"- Eligibility: {cur_summary.eligible if cur_summary else ''}\n"
            f"- Action Steps: {cur_summary.actions if cur_summary else ''}\n"
            f"- Documents: {cur_summary.documents if cur_summary else ''}\n"
            f"- Deadline: {cur_summary.deadline if cur_summary else ''}\n"
            f"- Contact: {cur_summary.help_contact if cur_summary else ''}\n"
            f"- Missing Info: {cur_summary.missing if cur_summary else ''}\n\n"
            f"## Grounded Action Checklist\n"
        )
        if cur_checklist:
            for item in cur_checklist.items:
                mand = "MANDATORY" if item.is_mandatory else "ADVISORY"
                export_text += f"{item.step_number}. [{mand}] ({item.category}) {item.action}\n"
                if item.grounded_quote:
                    export_text += f"   - Quote: \"{item.grounded_quote}\"\n"

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label="📄 Download Action Plan (Markdown)",
                data=export_text,
                file_name="notice2action_plan.md",
                mime="text/markdown",
                use_container_width=True,
                key="btn_dl_markdown_tab3",
            )
        with col_dl2:
            if cur_checklist and hasattr(cur_checklist, "to_ics_bytes"):
                ics_data = cur_checklist.to_ics_bytes()
            else:
                ics_data = b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Notice2Action AI//EN\r\nEND:VCALENDAR\r\n"
            st.download_button(
                label="📅 Add Deadline to Calendar (.ics)",
                data=ics_data,
                file_name="notice_deadline.ics",
                mime="text/calendar",
                use_container_width=True,
                key="btn_dl_ics_tab3",
            )


# ----------------- TAB 4: FOLLOW-UP Q&A -----------------
with tab_followup:
    st.markdown(
        """
        <div style="margin-bottom: 0.85rem;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">4. Follow-Up Q&A Assistant</div>
            <div style="font-size: 0.8rem; color: #94A3B8;">Ask clarification questions about this notice. Answers are strictly grounded in notice text without fabrication.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.raw_notice_text.strip():
        st.markdown(
            """
            <div class="dark-card" style="text-align: center; padding: 2rem 1rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.35rem;">💬</div>
                <div style="font-size: 1rem; font-weight: 700; color: #FFFFFF;">No Notice Loaded</div>
                <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.2rem;">
                    Load or analyze a notice first to enable grounded interactive Q&A.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Pre-set quick questions
        st.markdown("<span class='card-label'>💡 Suggested Inquiries</span>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.button(
            "📋 Required Documents?",
            use_container_width=True,
            key="qa_sug_docs",
            on_click=set_qa_inquiry,
            args=("What documents are needed to apply?",),
        )
        c2.button(
            "👥 Eligibility Criteria?",
            use_container_width=True,
            key="qa_sug_elig",
            on_click=set_qa_inquiry,
            args=("Who is eligible for this opportunity?",),
        )
        c3.button(
            "⏳ Late Submissions?",
            use_container_width=True,
            key="qa_sug_late",
            on_click=set_qa_inquiry,
            args=("Can I submit the application late?",),
        )
        c4.button(
            "📅 Exact Deadline?",
            use_container_width=True,
            key="qa_sug_dl",
            on_click=set_qa_inquiry,
            args=("What is the final deadline to submit?",),
        )

        user_q = st.text_input(
            "Enter your question:",
            placeholder="e.g. Is there any application fee required?",
            label_visibility="collapsed",
            key="qa_input_text_box",
        )

        c_ask1, c_ask2 = st.columns([1.2, 3])
        with c_ask1:
            ask_btn = st.button("💬 Ask Assistant", type="primary", use_container_width=True, key="btn_ask_qa")
        with c_ask2:
            if st.session_state.followup_history:
                if st.button("🗑️ Clear Q&A History", type="secondary", use_container_width=False, key="btn_clear_qa"):
                    st.session_state.followup_history = []
                    st.session_state.qa_input_text_box = ""
                    st.rerun()

        if ask_btn:
            target_question = (user_q or st.session_state.get("qa_input_text_box", "")).strip()
            if target_question:
                with st.spinner("Finding grounded answer in notice text..."):
                    assistant = FollowUpAssistant()
                    ans = assistant.answer_question(target_question, st.session_state.raw_notice_text)
                    st.session_state.followup_history.insert(0, ans)
                    st.rerun()

        # Render History
        if st.session_state.followup_history:
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            st.markdown("#### 💬 Conversation History")
            for item in st.session_state.followup_history:
                render_qa_item(item)
