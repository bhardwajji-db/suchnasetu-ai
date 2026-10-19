"""
Notice2Action AI (PS02)
Notice-to-Action Accessibility Assistant powered by Gemma 4.
Hacktoberfest 2026 HackDay@Meerut × E-Cell IIMT University.
"""

import sys
from pathlib import Path

# Ensure src/ is on python module path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import streamlit as st
from PIL import Image
import time

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
from notice2action.ui.components import (
    render_fact_card,
    render_summary_section,
    render_checklist_section,
)

# Streamlit Page Setup
st.set_page_config(
    page_title="Notice2Action AI | PS02 Assistant",
    page_icon="📢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-Contrast Accessible CSS
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .notice-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        font-family: monospace;
        font-size: 13px;
        line-height: 1.5;
        white-space: pre-wrap;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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
    st.markdown("### 📢 Notice2Action AI")
    st.caption("PS02 — Notice-to-Action Accessibility Assistant")
    st.caption("HackDay@Meerut × E-Cell IIMTU | Gemma 4 Track")

    st.markdown("---")

    # Diagnostics Drawer
    diag = run_preflight_diagnostics()
    if diag.overall_status == "ok":
        st.success("🟢 System Ready (Gemma 4 & OCR Live)", icon="✅")
    elif diag.overall_status == "warning":
        st.warning("🟡 System Warning (Check Preflight)", icon="⚠️")
    else:
        st.error("🔴 System Error (Ollama/Model Missing)", icon="❌")

    with st.expander("🛠️ Preflight Diagnostic Details"):
        for item in diag.items:
            icon = "✅" if item.status == "ok" else ("⚠️" if item.status == "warning" else "❌")
            st.markdown(f"**{icon} {item.name}**")
            st.caption(item.details)
            if item.remedy:
                st.info(f"Remedy: {item.remedy}")

    st.markdown("---")

    # Quick-load Synthetic Demo Fixtures
    st.markdown("##### 🧪 Quick-Load Sample Notices")
    fixtures_dir = config.synthetic_fixtures_dir

    if st.button("📄 Sample 1: Scholarship Notice (Full)"):
        p = fixtures_dir / "sample_scholarship_notice.txt"
        if p.is_file():
            st.session_state.raw_notice_text = p.read_text(encoding="utf-8")
            st.session_state.uploaded_image = None
            st.session_state.structured_notice = None
            st.session_state.followup_history = []
            st.success("Loaded Sample 1!")
            st.rerun()

    if st.button("🇮🇳 Sample 2: Hindi Scholarship Notice"):
        p = fixtures_dir / "sample_hindi_notice.txt"
        if p.is_file():
            st.session_state.raw_notice_text = p.read_text(encoding="utf-8")
            st.session_state.uploaded_image = None
            st.session_state.structured_notice = None
            st.session_state.followup_history = []
            st.session_state.selected_lang = "hi"
            st.success("Loaded Sample 2 (Hindi)!")
            st.rerun()

    if st.button("⚠️ Sample 3: Uncertain / Tentative Notice"):
        p = fixtures_dir / "sample_uncertain_notice.txt"
        if p.is_file():
            st.session_state.raw_notice_text = p.read_text(encoding="utf-8")
            st.session_state.uploaded_image = None
            st.session_state.structured_notice = None
            st.session_state.followup_history = []
            st.success("Loaded Sample 3 (Uncertain)!")
            st.rerun()

    if st.button("❓ Sample 4: Missing Fields Notice"):
        p = fixtures_dir / "sample_missing_fields_notice.txt"
        if p.is_file():
            st.session_state.raw_notice_text = p.read_text(encoding="utf-8")
            st.session_state.uploaded_image = None
            st.session_state.structured_notice = None
            st.session_state.followup_history = []
            st.success("Loaded Sample 4 (Missing Fields)!")
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
st.markdown("<div class='main-title'>📢 Notice2Action AI</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-title'>"
    "Transforming complex college notices, scholarships, and announcements into verified, accessible next steps. "
    "Powered by local <strong>Gemma 4</strong> with strict evidence grounding."
    "</div>",
    unsafe_allow_html=True,
)

tab_input, tab_structured, tab_summary, tab_followup = st.tabs([
    "📥 1. Notice Ingestion & OCR",
    "🔍 2. Grounded Fact Breakdown",
    "📋 3. Summary & Action Checklist",
    "💬 4. Follow-Up Q&A",
])

# ----------------- TAB 1: INGESTION & OCR -----------------
with tab_input:
    st.subheader("1. Supply Notice Document", divider="gray")
    st.markdown("Upload a photo, scan, or screenshot of a notice, or paste the text directly below.")

    col_img, col_paste = st.columns([1, 1])

    with col_img:
        uploaded_file = st.file_uploader(
            "Upload Notice Image or Text File",
            type=["png", "jpg", "jpeg", "webp", "txt"],
            help="Supported formats: PNG, JPG, JPEG, WEBP, TXT. Max size: 10 MB.",
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
                        ocr_lang = st.selectbox("OCR Language Engine", ["eng (English)", "hin (Hindi)", "eng+hin (Bilingual)"], index=0)
                    with c_ocr2:
                        apply_prep = st.checkbox("Enhance Contrast & Sharpen", value=True)

                    if st.button("⚙️ Run OCR Extraction", use_container_width=True):
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
        pasted = st.text_area(
            "Or Paste Notice Text Directly",
            height=280,
            placeholder="Paste text of the circular, announcement, or poster here...",
        )
        if st.button("📥 Use Pasted Text"):
            ingest_res = ingest_pasted_text(pasted)
            if ingest_res.error:
                st.error(ingest_res.error)
            else:
                st.session_state.raw_notice_text = ingest_res.raw_text
                st.session_state.uploaded_image = None
                st.session_state.structured_notice = None
                st.success("Pasted notice loaded into session!")
                st.rerun()

    st.markdown("---")
    st.markdown("#### 📝 Extracted Notice Text (Review & Edit)")
    st.caption("You can edit or correct any OCR misreadings below before running semantic analysis.")

    edited_text = st.text_area(
        "Notice Content for Analysis",
        value=st.session_state.raw_notice_text,
        height=220,
        help="This text is used as the ground truth for all evidence quotes and checks.",
    )
    if edited_text != st.session_state.raw_notice_text:
        st.session_state.raw_notice_text = edited_text

    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        analyze_btn = st.button("🚀 Analyze Notice with Gemma 4", type="primary", use_container_width=True)

    if analyze_btn:
        if not st.session_state.raw_notice_text.strip():
            st.error("Please provide notice text or upload a notice first.")
        else:
            with st.spinner("Analyzing notice with local Gemma 4 and verifying evidence grounding..."):
                start_t = time.time()
                analyzer = NoticeAnalyzer()
                try:
                    structured = analyzer.analyze_notice(st.session_state.raw_notice_text)
                    st.session_state.structured_notice = structured

                    # Generate summaries & checklists
                    st.session_state.summary_en = generate_accessible_summary(structured, analyzer.client)
                    st.session_state.checklist_en = generate_action_checklist(structured)

                    # Generate Hindi versions
                    st.session_state.summary_hi = translate_summary_to_hindi(st.session_state.summary_en, analyzer.client)
                    st.session_state.checklist_hi = translate_checklist_to_hindi(st.session_state.checklist_en, analyzer.client)

                    elapsed = time.time() - start_t
                    st.success(f"Analysis complete in {elapsed:.2f}s! Proceed to Tab 2 or Tab 3 to view results.")
                except Exception as e:
                    st.error(f"Analysis failed: {e}")


# ----------------- TAB 2: STRUCTURED BREAKDOWN -----------------
with tab_structured:
    st.subheader("2. Structured Facts & Evidence Grounding", divider="blue")

    if st.session_state.structured_notice is None:
        st.info("No notice has been analyzed yet. Upload or paste a notice in Tab 1 and click 'Analyze Notice with Gemma 4'.")
    else:
        sn: StructuredNotice = st.session_state.structured_notice

        # Alert banner for missing or uncertain information
        if sn.missing_information:
            st.warning(f"⚠️ **Missing Critical Information Identified:** {', '.join(sn.missing_information)}", icon="⚠️")
        if sn.uncertain_or_conflicting_details:
            st.info(f"ℹ️ **Uncertain / Tentative Details Flagged:** {', '.join(sn.uncertain_or_conflicting_details)}", icon="ℹ️")

        col_left, col_right = st.columns(2)
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
    if st.session_state.structured_notice is None:
        st.info("Please analyze a notice in Tab 1 first.")
    else:
        is_hindi = st.session_state.selected_lang == "hi"

        # Display Summary
        cur_summary = st.session_state.summary_hi if is_hindi else st.session_state.summary_en
        if cur_summary:
            render_summary_section(cur_summary, lang=st.session_state.selected_lang)

        st.markdown("<br>", unsafe_allow_html=True)

        # Display Checklist
        cur_checklist = st.session_state.checklist_hi if is_hindi else st.session_state.checklist_en
        if cur_checklist:
            render_checklist_section(cur_checklist)


# ----------------- TAB 4: FOLLOW-UP Q&A -----------------
with tab_followup:
    st.subheader("4. Ask Notice-Grounded Follow-Up Questions", divider="violet")
    st.markdown("Ask clarification questions about the current notice. The assistant answers **strictly** from the notice text and will never fabricate unstated rules.")

    if not st.session_state.raw_notice_text.strip():
        st.info("Please load or paste a notice in Tab 1 first.")
    else:
        # Pre-set quick questions
        st.markdown("##### 💡 Suggested Questions:")
        c1, c2, c3, c4 = st.columns(4)
        sample_q = None
        if c1.button("What documents are needed?"):
            sample_q = "What documents are needed to apply?"
        if c2.button("Who is eligible?"):
            sample_q = "Who is eligible for this opportunity?"
        if c3.button("Can I submit late?"):
            sample_q = "Can I submit the application late?"
        if c4.button("What is the deadline?"):
            sample_q = "What is the final deadline to submit?"

        user_q = st.text_input("Enter your question:", value=sample_q or "", placeholder="e.g. Is there any application fee?")
        if st.button("Ask Assistant", type="primary"):
            if user_q.strip():
                with st.spinner("Finding grounded answer in notice text..."):
                    assistant = FollowUpAssistant()
                    ans = assistant.answer_question(user_q, st.session_state.raw_notice_text)
                    st.session_state.followup_history.insert(0, ans)

        # Render History
        if st.session_state.followup_history:
            st.markdown("---")
            st.markdown("#### Conversation History")
            for item in st.session_state.followup_history:
                with st.container(border=True):
                    st.markdown(f"**Q: {item.question}**")
                    if item.is_supported:
                        st.markdown(f"**A:** {item.answer}")
                        if item.evidence_quote:
                            st.caption(f"Evidence quote from notice: *\"{item.evidence_quote}\"*")
                    else:
                        st.markdown(f"**A:** {item.answer}")
                        st.markdown("<span style='color: #dc2626; font-size: 12px; font-weight: bold;'>⚠️ Information not stated in the supplied notice</span>", unsafe_allow_html=True)
