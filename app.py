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
import streamlit as st
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
    render_notice_overview,
    render_fact_card,
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


init_session_state()

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div style="font-size: 1.25rem; font-weight: 800; color: #FFFFFF; display: flex; align-items: center; gap: 0.5rem;">
                <span>📢 Notice2Action</span>
                <span style="font-size: 0.65rem; background: #3B82F6; color: white; padding: 2px 7px; border-radius: 4px; font-weight: 700; font-family: monospace;">PS02</span>
            </div>
            <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 4px;">
                Notice-to-Action Accessibility Assistant
            </div>
            <div style="font-size: 0.72rem; color: #64748B; margin-top: 2px;">
                HackDay@Meerut × E-Cell IIMTU | Gemma 4
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Diagnostics Drawer
    st.markdown("##### ⚡ System Health")
    diag = run_preflight_diagnostics()
    if diag.overall_status == "ok":
        st.success(f"System Ready • Local {config.ollama_model}", icon="✅")
    elif diag.overall_status == "warning":
        st.warning("System Warning • Check Preflight", icon="⚠️")
    else:
        st.error("System Error • Ollama Offline", icon="❌")

    with st.expander("🔍 Diagnostics Ledger"):
        for item in diag.items:
            icon = "✅" if item.status == "ok" else ("⚠️" if item.status == "warning" else "❌")
            st.markdown(f"**{icon} {item.name}**")
            st.caption(item.details)
            if item.remedy:
                st.info(f"Remedy: {item.remedy}")

    st.markdown("---")

    # Quick-load Synthetic Demo Fixtures
    st.markdown("##### 🧪 Quick-Load Samples")
    fixtures_dir = config.synthetic_fixtures_dir

    if st.button("🎯 Test Notice: TEST-SCH-2026-001", type="primary", use_container_width=True):
        p = fixtures_dir / "synthetic_scholarship_notice.txt"
        if p.is_file():
            st.session_state.raw_notice_text = p.read_text(encoding="utf-8")
            st.session_state.uploaded_image = None
            st.session_state.structured_notice = None
            st.session_state.followup_history = []
            st.rerun()

    c_s1, c_s2 = st.columns(2)
    with c_s1:
        if st.button("📄 Sample 1", use_container_width=True, help="Full Scholarship Notice"):
            p = fixtures_dir / "sample_scholarship_notice.txt"
            if p.is_file():
                st.session_state.raw_notice_text = p.read_text(encoding="utf-8")
                st.session_state.uploaded_image = None
                st.session_state.structured_notice = None
                st.session_state.followup_history = []
                st.rerun()
    with c_s2:
        if st.button("🇮🇳 Sample 2", use_container_width=True, help="Hindi Notice"):
            p = fixtures_dir / "sample_hindi_notice.txt"
            if p.is_file():
                st.session_state.raw_notice_text = p.read_text(encoding="utf-8")
                st.session_state.uploaded_image = None
                st.session_state.structured_notice = None
                st.session_state.followup_history = []
                st.session_state.selected_lang = "hi"
                st.rerun()

    c_s3, c_s4 = st.columns(2)
    with c_s3:
        if st.button("⚠️ Sample 3", use_container_width=True, help="Tentative Notice"):
            p = fixtures_dir / "sample_uncertain_notice.txt"
            if p.is_file():
                st.session_state.raw_notice_text = p.read_text(encoding="utf-8")
                st.session_state.uploaded_image = None
                st.session_state.structured_notice = None
                st.session_state.followup_history = []
                st.rerun()
    with c_s4:
        if st.button("❓ Sample 4", use_container_width=True, help="Missing Fields Notice"):
            p = fixtures_dir / "sample_missing_fields_notice.txt"
            if p.is_file():
                st.session_state.raw_notice_text = p.read_text(encoding="utf-8")
                st.session_state.uploaded_image = None
                st.session_state.structured_notice = None
                st.session_state.followup_history = []
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
    if st.button("🔄 Reset / Clear Session", use_container_width=True):
        st.session_state.raw_notice_text = ""
        st.session_state.uploaded_image = None
        st.session_state.structured_notice = None
        st.session_state.summary_en = None
        st.session_state.summary_hi = None
        st.session_state.checklist_en = None
        st.session_state.checklist_hi = None
        st.session_state.followup_history = []
        st.rerun()


# ----------------- MAIN INTERFACE -----------------
render_platform_header(status=diag.overall_status, model_name=config.ollama_model)

tab_input, tab_structured, tab_summary, tab_followup = st.tabs([
    "📥 Notice Ingestion & OCR",
    "🔍 Grounded Fact Breakdown",
    "📋 Summary & Action Checklist",
    "💬 Follow-Up Q&A",
])

# ----------------- TAB 1: INGESTION & OCR -----------------
with tab_input:
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF;">1. Supply Notice Document</div>
            <div style="font-size: 0.85rem; color: #94A3B8;">Upload a photo, scan, or digital notice, or paste raw text into the workspace below.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_img, col_paste = st.columns([1, 1], gap="medium")

    with col_img:
        st.markdown("<span class='card-label'>📁 Upload Notice File</span>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload Notice Document",
            type=["png", "jpg", "jpeg", "webp", "txt"],
            help="Supported formats: PNG, JPG, JPEG, WEBP, TXT. Max size: 10 MB.",
            label_visibility="collapsed",
        )
        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            ingest_res = ingest_uploaded_file(uploaded_file.name, bytes_data)
            if ingest_res.error:
                st.error(f"Upload Error: {ingest_res.error}")
            else:
                if ingest_res.source_type == "image":
                    st.session_state.uploaded_image = ingest_res.image
                    st.image(ingest_res.image, caption="Uploaded Notice Preview", use_container_width=True)

                    c_ocr1, c_ocr2 = st.columns(2)
                    with c_ocr1:
                        ocr_lang = st.selectbox("OCR Language", ["eng (English)", "hin (Hindi)", "eng+hin (Bilingual)"], index=0)
                    with c_ocr2:
                        apply_prep = st.checkbox("Preprocess & Enhance", value=True)

                    if st.button("⚙️ Run Tesseract OCR", use_container_width=True):
                        with st.spinner("Extracting text via Tesseract OCR..."):
                            lang_code = "hin" if "hin" in ocr_lang and "+" not in ocr_lang else ("eng+hin" if "+" in ocr_lang else "eng")
                            ocr_res = extract_text_from_image(ingest_res.image, target_lang=lang_code, apply_preprocessing=apply_prep)
                            if ocr_res.error:
                                st.error(ocr_res.error)
                            else:
                                st.session_state.raw_notice_text = ocr_res.extracted_text
                                st.session_state.ocr_confidence = ocr_res.confidence_score
                                if ocr_res.warning:
                                    st.warning(ocr_res.warning)
                                st.success(f"Extracted {ocr_res.line_count} lines (Confidence: {ocr_res.confidence_score}%)")
                                st.rerun()

                elif ingest_res.source_type == "text":
                    st.session_state.raw_notice_text = ingest_res.raw_text
                    st.success(f"Loaded text file '{ingest_res.filename}' ({ingest_res.char_count} chars).")

    with col_paste:
        st.markdown("<span class='card-label'>✍️ Paste Raw Text</span>", unsafe_allow_html=True)
        pasted = st.text_area(
            "Paste Notice Text",
            height=240,
            placeholder="Paste text of the circular, announcement, or poster here...",
            label_visibility="collapsed",
        )
        if st.button("📥 Load Pasted Content", use_container_width=True):
            ingest_res = ingest_pasted_text(pasted)
            if ingest_res.error:
                st.error(ingest_res.error)
            else:
                st.session_state.raw_notice_text = ingest_res.raw_text
                st.session_state.uploaded_image = None
                st.session_state.structured_notice = None
                st.success("Pasted notice loaded into session!")
                st.rerun()

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("#### 📝 Extracted Notice Content (Review & Edit)")
    st.caption("Inspect and correct any OCR errors below before initiating Gemma 4 semantic analysis.")

    char_count = len(st.session_state.raw_notice_text)
    line_count = len(st.session_state.raw_notice_text.splitlines()) if st.session_state.raw_notice_text else 0

    st.markdown(
        f"<div style='font-size: 0.75rem; color: #64748B; font-family: monospace; margin-bottom: 0.35rem;'>"
        f"BUFFER: {char_count} characters &bull; {line_count} lines"
        f"</div>",
        unsafe_allow_html=True,
    )

    edited_text = st.text_area(
        "Notice Content for Analysis",
        value=st.session_state.raw_notice_text,
        height=200,
        label_visibility="collapsed",
        help="This text serves as the ground truth for all evidence quotes and fact verification.",
    )
    if edited_text != st.session_state.raw_notice_text:
        st.session_state.raw_notice_text = edited_text

    col_btn1, col_btn2 = st.columns([1, 2])
    with col_btn1:
        analyze_btn = st.button("🚀 Analyze Notice with Gemma 4", type="primary", use_container_width=True)

    if analyze_btn:
        if not st.session_state.raw_notice_text.strip():
            st.error("Please supply notice text or upload a notice document first.")
        else:
            with st.status("Analyzing notice with local Gemma 4...", expanded=True) as status_box:
                start_t = time.time()
                st.write("🔍 **Phase 1/3:** Ingesting & normalizing document text...")
                time.sleep(0.1)

                analyzer = NoticeAnalyzer()
                try:
                    st.write("🤖 **Phase 2/3:** Extracting 8 grounded key fields with strict evidence citation...")
                    structured = analyzer.analyze_notice(st.session_state.raw_notice_text)
                    st.session_state.structured_notice = structured

                    st.write("📋 **Phase 3/3:** Synthesizing plain-language summary & action checklist...")
                    st.session_state.summary_en = generate_accessible_summary(structured, analyzer.client)
                    st.session_state.checklist_en = generate_action_checklist(structured)

                    # Multilingual translation
                    st.session_state.summary_hi = translate_summary_to_hindi(st.session_state.summary_en, analyzer.client)
                    st.session_state.checklist_hi = translate_checklist_to_hindi(st.session_state.checklist_en, analyzer.client)

                    elapsed = time.time() - start_t
                    status_box.update(label=f"✅ Analysis complete in {elapsed:.2f}s! Proceed to Tab 2 or Tab 3.", state="complete", expanded=False)
                    st.rerun()
                except Exception as e:
                    status_box.update(label="❌ Analysis Failed", state="error", expanded=True)
                    st.error(f"Analysis failed: {e}")


# ----------------- TAB 2: STRUCTURED BREAKDOWN -----------------
with tab_structured:
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF;">2. Grounded Fact Breakdown</div>
            <div style="font-size: 0.85rem; color: #94A3B8;">Structured extraction of 8 key notice fields. Every fact cites an exact verbatim quotation.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.structured_notice is None:
        st.markdown(
            """
            <div class="dark-card" style="text-align: center; padding: 2.5rem 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔍</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #FFFFFF;">No Notice Analyzed Yet</div>
                <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 0.25rem;">
                    Upload or paste a notice in Tab 1, or click <strong>⚡ Quick-Load Samples</strong> in the sidebar.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        sn: StructuredNotice = st.session_state.structured_notice

        # High-level overview banner
        render_notice_overview(sn)

        # Alert banner for missing or uncertain information
        if sn.missing_information:
            st.warning(f"⚠️ **Missing Critical Information Identified:** {', '.join(sn.missing_information)}", icon="⚠️")
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
        <div style="margin-bottom: 1.25rem;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF;">3. Summary & Action Checklist</div>
            <div style="font-size: 0.85rem; color: #94A3B8;">Plain-language synthesis answering 7 core questions, with an ordered execution checklist.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.structured_notice is None:
        st.markdown(
            """
            <div class="dark-card" style="text-align: center; padding: 2.5rem 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📋</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #FFFFFF;">Summary Unavailable</div>
                <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 0.25rem;">
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

        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

        # Display Checklist
        cur_checklist = st.session_state.checklist_hi if is_hindi else st.session_state.checklist_en
        if cur_checklist:
            render_checklist_section(cur_checklist)

        # Export Report Option
        st.markdown("---")
        st.markdown("##### 📥 Export Action Plan")
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

        st.download_button(
            label="📄 Download Action Plan (Markdown)",
            data=export_text,
            file_name="notice2action_plan.md",
            mime="text/markdown",
            use_container_width=False,
        )


# ----------------- TAB 4: FOLLOW-UP Q&A -----------------
with tab_followup:
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF;">4. Follow-Up Q&A Assistant</div>
            <div style="font-size: 0.85rem; color: #94A3B8;">Ask clarification questions about this notice. Answers are strictly grounded in notice text without fabrication.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.raw_notice_text.strip():
        st.markdown(
            """
            <div class="dark-card" style="text-align: center; padding: 2.5rem 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">💬</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #FFFFFF;">No Notice Loaded</div>
                <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 0.25rem;">
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
        sample_q = None
        if c1.button("📋 Required Documents?", use_container_width=True):
            sample_q = "What documents are needed to apply?"
        if c2.button("👥 Eligibility Criteria?", use_container_width=True):
            sample_q = "Who is eligible for this opportunity?"
        if c3.button("⏳ Late Submissions?", use_container_width=True):
            sample_q = "Can I submit the application late?"
        if c4.button("📅 Exact Deadline?", use_container_width=True):
            sample_q = "What is the final deadline to submit?"

        user_q = st.text_input(
            "Enter your question:",
            value=sample_q or "",
            placeholder="e.g. Is there any application fee required?",
            label_visibility="collapsed",
        )
        c_ask1, _ = st.columns([1, 3])
        with c_ask1:
            ask_btn = st.button("💬 Ask Assistant", type="primary", use_container_width=True)

        if ask_btn:
            if user_q.strip():
                with st.spinner("Finding grounded answer in notice text..."):
                    assistant = FollowUpAssistant()
                    ans = assistant.answer_question(user_q, st.session_state.raw_notice_text)
                    st.session_state.followup_history.insert(0, ans)

        # Render History
        if st.session_state.followup_history:
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            st.markdown("#### 💬 Conversation History")
            for item in st.session_state.followup_history:
                render_qa_item(item)
