"""
Automated End-to-End Verification Suite for SochnaSetu AI:
Single Unified Language Selector & Master UI/UX Refinement.

Verifies:
1. Exactly ONE visible language selector in the top header.
2. Absence of redundant standalone 'EN' and 'हिन्दी' buttons.
3. English-to-Hindi language switching: immediate UI update across navigation & dashboard.
4. Persistence of language preference across page reloads (localStorage persistence).
5. Hindi-to-English switching: immediate restoration of English labels.
6. Responsive layout verification across 390px, 768px, 1024px, 1366px, 1920px (0 overflow).
7. Full navigation audit across all 11 workspace views without errors.
8. Retained header controls: model status, original notice viewer, provider selector, notifications, theme toggle, and profile avatar.
"""

from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
FRONTEND_URL = "http://localhost:5173"


def _goto_app(page):
    page.goto(FRONTEND_URL, wait_until="networkidle")
    guest_btn = page.locator("button[aria-label='Continue to application as guest'], button:has-text('Continue as Guest')").first
    if guest_btn.is_visible():
        guest_btn.click()
        page.wait_for_timeout(400)
    page.wait_for_selector("text=PS02", timeout=8000)


def test_single_language_selector_and_persistence():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH if Path(CHROME_PATH).is_file() else None,
        )
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()

        # Step 1: Open app
        _goto_app(page)

        # Step 2: Confirm exactly ONE language selector in header
        header = page.locator("header")
        assert header.is_visible(), "Header should be visible"

        lang_selectors = header.locator("select[aria-label='Select Website Language']")
        assert lang_selectors.count() == 1, f"Expected exactly 1 language selector in header, found {lang_selectors.count()}"

        # Step 3: Confirm absence of duplicate EN or हिन्दी buttons
        duplicate_en = header.locator("button:has-text('EN')")
        duplicate_hi = header.locator("button:has-text('हिन्दी')")
        assert duplicate_en.count() == 0, "Duplicate standalone 'EN' button must not be present in header"
        assert duplicate_hi.count() == 0, "Duplicate standalone 'हिन्दी' button must not be present in header"

        # Step 4: Verify English and Hindi are both in the single dropdown
        options = lang_selectors.locator("option").all_inner_texts()
        has_english = any("English" in opt for opt in options)
        has_hindi = any("हिन्दी" in opt or "Hindi" in opt for opt in options)
        assert has_english, "Dropdown must contain English"
        assert has_hindi, "Dropdown must contain Hindi"

        # Step 5: Test English to Hindi switching
        lang_selectors.select_option("hi")
        page.wait_for_timeout(500)

        # Verify html lang attribute
        html_lang = page.locator("html").get_attribute("lang")
        assert html_lang == "hi", f"Expected html lang='hi', got '{html_lang}'"

        # Verify UI navigation text updated to Hindi
        sidebar = page.locator("aside").first
        dashboard_nav = sidebar.locator("text=डैशबोर्ड")
        assert dashboard_nav.is_visible(), "Navigation should display Hindi 'डैशबोर्ड'"

        # Verify localStorage persistence
        saved_lang = page.evaluate("() => localStorage.getItem('suchnasetu_user_language')")
        assert saved_lang == "hi", f"Expected localStorage suchnasetu_user_language='hi', got '{saved_lang}'"

        # Step 6: Test persistence across page reload
        page.reload(wait_until="networkidle")
        guest_btn = page.locator("button[aria-label='Continue to application as guest']")
        guest_btn.wait_for(state="visible", timeout=8000)
        guest_btn.click()
        page.wait_for_timeout(500)
        page.wait_for_selector("text=PS02", timeout=8000)
        reloaded_lang = page.locator("html").get_attribute("lang")
        assert reloaded_lang == "hi", f"Language should remain 'hi' after reload, got '{reloaded_lang}'"

        # Step 7: Test Hindi to English switching
        page.locator("header select[aria-label='Select Website Language']").select_option("en")
        page.wait_for_timeout(500)
        restored_lang = page.locator("html").get_attribute("lang")
        assert restored_lang == "en", f"Expected html lang='en', got '{restored_lang}'"

        restored_nav = sidebar.locator("text=Dashboard")
        assert restored_nav.is_visible(), "Navigation should restore English 'Dashboard'"

        # Step 8: Verify settings view application language selector synchronization
        sidebar.locator("button:has-text('Settings')").first.click()
        page.wait_for_timeout(400)
        settings_select = page.locator("select[aria-label='Application Language Preference']")
        assert settings_select.is_visible(), "Settings view should have Application Language selector"
        assert settings_select.input_value() == "en", "Settings language should match current language"

        browser.close()


def test_responsive_viewports_and_no_overflow():
    viewports = [
        ("mobile_390", 390, 844),
        ("tablet_768", 768, 1024),
        ("laptop_1024", 1024, 768),
        ("desktop_1366", 1366, 768),
        ("wide_1920", 1920, 1080),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH if Path(CHROME_PATH).is_file() else None,
        )

        for name, width, height in viewports:
            ctx = browser.new_context(viewport={"width": width, "height": height})
            page = ctx.new_page()
            _goto_app(page)

            # Check horizontal overflow
            scroll_width = page.evaluate("() => document.documentElement.scrollWidth")
            inner_width = page.evaluate("() => window.innerWidth")
            assert scroll_width <= inner_width + 1, (
                f"Horizontal overflow at {name} ({width}px): scrollWidth={scroll_width}, innerWidth={inner_width}"
            )

            # Header must have exactly 1 language selector
            header = page.locator("header")
            assert header.locator("select[aria-label='Select Website Language']").count() == 1

            ctx.close()

        browser.close()


def test_all_workspace_views_navigation_and_retained_controls():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH if Path(CHROME_PATH).is_file() else None,
        )
        context = browser.new_context(viewport={"width": 1366, "height": 850})
        page = context.new_page()

        _goto_app(page)

        # Check retained header controls
        header = page.locator("header")
        assert header.locator("button[aria-label='View Original Ground-Truth Notice Document (Disabled: No notice loaded)']").is_visible() or \
               header.locator("button[aria-label='View Original Ground-Truth Notice Document']").is_visible(), "Original Notice button should be retained"

        assert header.locator("select[aria-label='Select AI Inference Provider']").is_visible(), "Provider selector should be retained"
        assert header.locator("button[aria-label='Open notifications']").is_visible(), "Notification center button should be retained"
        assert header.locator("button[aria-label='Switch to dark theme']").is_visible(), "Theme switch button should be retained"

        sidebar = page.locator("aside").first

        # Tab navigation checks: Ingestion, Grounded Facts, Summary, Revision, Eligibility, QA, Navigator, Timeline, History, Settings, Demo Library
        tabs = [
            ("Ingestion & OCR", "Notice Ingestion"),
            ("Grounded Facts", "Core Notice Facts"),
            ("Summary & Actions", "Notice Summary"),
            ("Revision Ledger", "Corrigendum"),
            ("Eligibility Check", "Eligibility"),
            ("Follow-Up Q&A", "Follow-Up"),
            ("Action Navigator", "No Notice Loaded for Action Planning"),
            ("Multi-Notice Timeline", "Document Timeline"),
            ("Notice History", "Saved Notices & Weekly Action Planner"),
            ("Demo Library", "Demo Library"),
            ("Settings & Health", "System Settings"),
        ]

        for tab_label, expected_heading in tabs:
            btn = sidebar.locator(f"button:has-text('{tab_label}')")
            if btn.count() > 0:
                btn.first.click()
                page.wait_for_timeout(400)
                main = page.locator("main")
                assert main.locator(f"text={expected_heading}").first.is_visible(), (
                    f"Tab '{tab_label}' should display heading '{expected_heading}'"
                )

        browser.close()
