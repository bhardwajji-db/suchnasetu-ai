"""
Streamlit App Interaction and UI Rendering Tests for Notice2Action AI (PS02).
Uses Streamlit's official AppTest framework to verify UI components, tabs,
and session state rendering without requiring a running browser.
"""

from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_ui_render_synthetic_notice_tabs():
    """Verifies that the Streamlit application renders all tabs and cards properly."""
    txt_path = Path("tests/fixtures/synthetic_scholarship_notice.txt")
    assert txt_path.is_file()
    sample_text = txt_path.read_text(encoding="utf-8")

    at = AppTest.from_file("../app.py")
    at.run()
    assert not at.exception, f"Initial render failed: {at.exception}"

    # Load notice into session state and re-run
    at.session_state.raw_notice_text = sample_text
    at.run()
    assert not at.exception, f"Render with notice text failed: {at.exception}"

    # Check that main UI elements exist
    assert len(at.tabs) == 4
    assert "Notice Ingestion & OCR" in at.tabs[0].label
    assert "Grounded Fact Breakdown" in at.tabs[1].label
    assert "Summary & Action Checklist" in at.tabs[2].label
    assert "Follow-Up Q&A" in at.tabs[3].label
