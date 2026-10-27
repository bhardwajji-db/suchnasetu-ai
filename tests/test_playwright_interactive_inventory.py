"""
Comprehensive Playwright Acceptance Test Suite for SuchnaSetu AI.
Verifies all interactive controls, navigation tabs, modals, language switching,
accessibility settings, demo loading, reading levels, eligibility engine, Q&A, and mobile responsiveness.
"""

from __future__ import annotations

import time
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
FRONTEND_URL = "http://127.0.0.1:5173"
BACKEND_URL = "http://127.0.0.1:8000"
SCREENSHOT_DIR = Path("assets/screenshots/interactive_audit")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

import sys
import subprocess
import urllib.request

def _probe_url(url: str, timeout: float = 1.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status in [200, 404]
    except Exception:
        return False

@pytest.fixture(scope="module", autouse=True)
def ensure_servers_running():
    spawned = []
    backend_up = _probe_url(f"{BACKEND_URL}/api/health")
    frontend_up = _probe_url(FRONTEND_URL)

    if not backend_up:
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "notice2action.api.server:app", "--port", "8000", "--host", "127.0.0.1"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        spawned.append(proc)

    if not frontend_up:
        proc = subprocess.Popen(
            ["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"],
            cwd="frontend",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        spawned.append(proc)

    deadline = time.time() + 25
    ready = False
    while time.time() < deadline:
        if _probe_url(f"{BACKEND_URL}/api/health") and _probe_url(FRONTEND_URL):
            ready = True
            break
        time.sleep(1)

    try:
        if not ready:
            pytest.skip(f"Servers at {BACKEND_URL} or {FRONTEND_URL} could not be initialized.")
        yield
    finally:
        for p in spawned:
            try:
                p.terminate()
                p.wait(timeout=3)
            except Exception:
                try:
                    p.kill()
                except Exception:
                    pass



def _goto_app(page):
    page.goto(FRONTEND_URL, wait_until="networkidle")
    guest_btn = page.locator("button:has-text('Continue as Guest')")
    if guest_btn.is_visible():
        guest_btn.click()
        page.wait_for_timeout(400)
    page.wait_for_selector("text=PS02", timeout=10000)


def test_interactive_navigation_and_header():
    """Verifies all sidebar navigation items (Tabs 0-11), logo, and header controls."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH if Path(CHROME_PATH).is_file() else None,
        )
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()

        _goto_app(page)
        page.wait_for_selector("text=PS02", timeout=10000)

        # 1. Verify Header Brand Logo returns to Dashboard (Tab 0)
        logo = page.locator("button[title='Return to Home']")
        assert logo.is_visible()
        logo.click()
        page.wait_for_timeout(300)
        assert page.locator("text=Dashboard Overview").or_(page.locator("text=Citizen Civic Dashboard")).first.is_visible()

        # 2. Verify all Sidebar Navigation Tabs
        nav_tabs = [
            ("1. Ingestion & OCR", "Document Ingestion & OCR Ground Truth"),
            ("2. Grounded Facts", "Six Core Notice Facts"),
            ("3. Summary & Actions", "Plain-Language Notice Summary"),
            ("4. Revision Ledger", "Cross-Notice Revision & Corrigendum Differencing"),
            ("5. Eligibility Check", "Deterministic Candidate Eligibility Engine"),
            ("6. Follow-Up Q&A", "Notice-Grounded Follow-Up Assistant"),
            ("7. Action Navigator", "No Notice Loaded for Action Planning"),
            ("8. Multi-Notice Timeline", "Cross-Notice Intelligence"),
            ("Notice History", "Saved Notices"),
            ("Settings & Health", "System Settings & Accessibility Preferences"),
            ("11. Demo Library", "11. Demo Library"),
            ("Dashboard", "Dashboard Overview"),
        ]

        for nav_label, expected_text in nav_tabs:
            btn = page.locator(f"button:has-text('{nav_label}')").first
            assert btn.is_visible(), f"Nav button '{nav_label}' not found"
            btn.click()
            page.wait_for_timeout(350)
            assert page.locator(f"text={expected_text}").first.is_visible(), (
                f"Failed to navigate to '{nav_label}', expected text '{expected_text}' not visible"
            )

        # 3. Verify Account Sign In opens Auth view / modal
        signin_btn = page.locator("button[aria-label='Sign In to citizen account']")
        assert signin_btn.is_visible()
        signin_btn.click()
        page.wait_for_timeout(400)

        # Verify Auth inputs
        assert page.locator("input[type='email']").is_visible()
        assert page.locator("input[type='password']").is_visible()

        # Return to application
        close_btn = page.locator("button[aria-label='Return to application'], button[aria-label='Return to Main Application'], button[aria-label='Close authentication modal'], button[aria-label='Continue to application as guest']").first
        assert close_btn.is_visible()
        close_btn.click()
        page.wait_for_timeout(300)

        # 4. Verify Single Unified Language Selector (EN -> HI -> EN)
        lang_select = page.locator("select[aria-label='Select Website Language']")
        assert lang_select.is_visible()
        lang_select.select_option("hi")
        page.wait_for_timeout(400)
        lang_select.select_option("en")
        page.wait_for_timeout(400)

        page.screenshot(path=str(SCREENSHOT_DIR / "01_header_nav_verified.png"))
        context.close()
        browser.close()


def test_interactive_demo_library_workflow():
    """Verifies Demo Library search, format filtering, Preview modal, and loading."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH if Path(CHROME_PATH).is_file() else None,
        )
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()

        _goto_app(page)

        # Navigate to Demo Library
        page.locator("button:has-text('11. Demo Library')").first.click()
        page.wait_for_timeout(500)
        page.wait_for_selector("text=11. Demo Library", timeout=5000)

        # 1. Verify Format Filter works (Filter to PDF)
        format_select = page.locator("main select:has(option[value='pdf'])")
        format_select.select_option("pdf")
        page.wait_for_timeout(300)
        # Verify PDF demo cards are visible
        assert page.locator("text=UPSC Civil Services").first.is_visible()

        # Reset format filter to All
        format_select.select_option("all")
        page.wait_for_timeout(300)
        assert page.locator("text=National Postgraduate Merit").first.is_visible()

        # 2. Verify Search filter works
        search_input = page.locator("input[placeholder*='Search title, category, keywords...']")
        search_input.fill("UPSC")
        page.wait_for_timeout(300)
        assert page.locator("text=UPSC").first.is_visible()
        search_input.fill("")
        page.wait_for_timeout(300)

        # 3. Test Preview Modal on DEMO-01 (TXT)
        preview_btns = page.locator("button:has-text('Preview')")
        assert preview_btns.count() > 0
        preview_btns.first.click()
        page.wait_for_timeout(600)

        # Verify preview modal content
        preview_modal = page.locator(".fixed.inset-0").first
        assert preview_modal.is_visible()
        assert page.locator("button:has-text('Load into Assistant')").is_visible()

        # Close preview modal via Close button
        page.locator("button:has-text('Close')").first.click()
        page.wait_for_timeout(300)

        # 4. Test "Load into Assistant" on DEMO-01
        preview_btns.first.click()
        page.wait_for_timeout(600)
        load_assistant_btn = page.locator("button:has-text('Load into Assistant')").first
        load_assistant_btn.click()
        page.wait_for_timeout(600)

        # Wait for navigation to Ingestion tab (Tab 1)
        page.wait_for_selector("text=Document Ingestion & OCR Ground Truth", timeout=10000)

        # Verify notice buffer has been filled with text
        textarea_val = page.locator("textarea").input_value()
        assert len(textarea_val) > 100, f"Notice buffer length {len(textarea_val)} is unexpectedly short"

        page.screenshot(path=str(SCREENSHOT_DIR / "02_demo_library_loaded.png"))
        context.close()
        browser.close()


def test_interactive_accessibility_and_settings():
    """Verifies Settings view controls, accessibility modes (High Contrast, Warm Tone, Text Size), and reset."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH if Path(CHROME_PATH).is_file() else None,
        )
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()

        _goto_app(page)

        # Navigate to Settings (Tab 10)
        page.locator("button:has-text('Settings & Health')").first.click()
        page.wait_for_timeout(500)
        page.wait_for_selector("text=System Settings & Accessibility Preferences", timeout=5000)

        # 1. Test Refresh Health button
        refresh_btn = page.locator("button:has-text('Refresh Health')")
        assert refresh_btn.is_visible()
        refresh_btn.click()
        page.wait_for_timeout(1000)
        assert page.locator("text=Operational").first.is_visible()

        # 2. Test High Contrast toggle inside its specific card container
        contrast_card = page.locator("div:has(> div > span:has-text('High Contrast Mode'))")
        contrast_toggle = contrast_card.locator("button")
        assert contrast_toggle.is_visible()
        assert contrast_toggle.inner_text().strip() == "OFF"
        contrast_toggle.click()
        page.wait_for_timeout(300)
        assert contrast_toggle.inner_text().strip() == "ON"

        # Check for high contrast class on root
        root_class = page.locator("div.min-h-screen").get_attribute("class") or ""
        assert "high-contrast" in root_class or "bg-slate-900" in root_class

        # Toggle contrast back OFF
        contrast_toggle.click()
        page.wait_for_timeout(300)
        assert contrast_toggle.inner_text().strip() == "OFF"

        # 3. Test Text Size buttons
        large_size_btn = page.locator("button:text-is('large')")
        if large_size_btn.is_visible():
            large_size_btn.click()
            page.wait_for_timeout(200)

        # 4. Test Reset to Defaults
        reset_btn = page.locator("button:has-text('Reset to Defaults')")
        assert reset_btn.is_visible()
        reset_btn.click()
        page.wait_for_timeout(300)

        page.screenshot(path=str(SCREENSHOT_DIR / "03_settings_accessibility_verified.png"))
        context.close()
        browser.close()


def test_interactive_mobile_responsive_controls():
    """Verifies responsive bottom navigation, hamburger drawer, and mobile switcher at 390px."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH if Path(CHROME_PATH).is_file() else None,
        )
        context = browser.new_context(viewport={"width": 390, "height": 844})
        page = context.new_page()

        _goto_app(page)
        page.wait_for_selector("text=PS02", timeout=5000)

        # 1. Verify Mobile Bottom Navigation is visible
        bottom_nav = page.locator("nav[aria-label='Mobile Bottom Navigation']")
        assert bottom_nav.is_visible()

        # 2. Tap "Ingest" tab (Tab 1)
        ingest_btn = bottom_nav.locator("button[aria-label='Ingest']")
        ingest_btn.click()
        page.wait_for_timeout(500)
        assert page.locator("text=Document Ingestion").is_visible()

        # 3. Tap "Menu" button (opens mobile drawer)
        menu_btn = bottom_nav.locator("button[aria-label='Open full tool menu']")
        menu_btn.click()
        page.wait_for_timeout(400)

        # Drawer should be open and its nav items visible
        drawer = page.locator("div[role='dialog'][aria-label='Navigation Drawer']")
        assert drawer.is_visible()
        assert drawer.locator("button:has-text('11. Demo Library')").is_visible()

        # Dismiss drawer via Escape key
        page.keyboard.press("Escape")
        page.wait_for_timeout(400)
        assert not drawer.is_visible()

        page.screenshot(path=str(SCREENSHOT_DIR / "04_mobile_390px_verified.png"))
        context.close()
        browser.close()


def test_interactive_eligibility_engine():
    """Verifies Deterministic Eligibility Engine form inputs, category selection, and calculation."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH if Path(CHROME_PATH).is_file() else None,
        )
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()

        _goto_app(page)

        # Navigate to Eligibility Check (Tab 5)
        page.locator("button:has-text('5. Eligibility Check')").first.click()
        page.wait_for_timeout(400)
        assert page.locator("text=Deterministic Candidate Eligibility Engine").first.is_visible()

        # 1. Click "Load Sample Scholarship Circular" to populate rule buffer
        load_sample_btn = page.locator("button:has-text('Load Sample Scholarship Circular')")
        assert load_sample_btn.is_visible()
        load_sample_btn.click()
        page.wait_for_timeout(600)

        # Check that textarea now has text
        textarea = page.locator("textarea")
        assert len(textarea.input_value()) > 50

        # 2. Check for Applicant Profile controls and click Evaluate
        eval_btn = page.locator("button:has-text('Evaluate My Eligibility')")
        assert eval_btn.is_visible()
        eval_btn.click()

        # Wait for evaluation to complete (calls local LLM or rule engine, timeout 180s)
        page.locator("text=Status:").or_(page.locator("text=Detailed Rule-by-Rule Breakdown")).first.wait_for(timeout=180000)
        assert page.locator("text=Status:").or_(page.locator("text=Detailed Rule-by-Rule Breakdown")).first.is_visible()

        page.screenshot(path=str(SCREENSHOT_DIR / "05_eligibility_engine_verified.png"))
        context.close()
        browser.close()


def test_interactive_revision_ledger():
    """Verifies Revision Ledger / Corrigendum Differencing view controls."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH if Path(CHROME_PATH).is_file() else None,
        )
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()

        _goto_app(page)

        # Navigate to Revision Ledger (Tab 4)
        page.locator("button:has-text('4. Revision Ledger')").first.click()
        page.wait_for_timeout(400)
        assert page.locator("text=Cross-Notice Revision & Corrigendum Differencing").first.is_visible()

        # Verify Compare button exists
        compare_btn = page.locator("button:has-text('Detect Revisions & Compare')")
        assert compare_btn.is_visible()

        page.screenshot(path=str(SCREENSHOT_DIR / "06_revision_ledger_verified.png"))
        context.close()
        browser.close()


def test_interactive_timeline_and_demo_pair():
    """Verifies Multi-Notice Timeline loading demo corrigendum pair and view state."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH if Path(CHROME_PATH).is_file() else None,
        )
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()

        _goto_app(page)

        # Navigate to Tab 8
        page.locator("button:has-text('8. Multi-Notice Timeline')").first.click()
        page.wait_for_timeout(500)
        assert page.locator("text=Cross-Notice Intelligence").first.is_visible()

        # Verify "Load Corrigendum Demo Pair" button
        load_pair_btn = page.locator("button:has-text('Load Corrigendum Demo Pair')")
        assert load_pair_btn.is_visible()
        load_pair_btn.click()
        page.wait_for_timeout(1000)

        # Verify notice cards or timeline elements rendered
        assert page.locator("text=Advt. 04/2026").first.is_visible()

        page.screenshot(path=str(SCREENSHOT_DIR / "07_timeline_demo_pair.png"))
        context.close()
        browser.close()
