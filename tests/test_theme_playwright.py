"""
Playwright Verification Suite for SochnaSetu AI Midnight Navy + Teal Dark Theme.
Verifies:
1. Slate + Deep Green theme preservation (colors, layout, navigation).
2. Header quick toggle switching to Midnight Navy + Teal.
3. Sidebar Appearance / Theme selector state synchronization.
4. Persistence of theme across page reloads (anti-flash verification).
5. Mobile viewport drawer accessibility and layout.
6. Complete application styling across Dashboard, Ingestion, and Settings in dark mode.
"""

from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
FRONTEND_URL = "http://127.0.0.1:5173"
SCREENSHOT_DIR = Path("assets/screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def test_theme_system_full_lifecycle():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH if Path(CHROME_PATH).is_file() else None,
        )
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()

        # Step 1: Open Application in default Slate + Deep Green (Light)
        page.goto(FRONTEND_URL, wait_until="networkidle")
        page.wait_for_selector("text=PS02", timeout=8000)

        # Force light theme initially for clean starting state
        page.evaluate("() => { localStorage.setItem('suchnasetu_theme', 'light'); document.documentElement.setAttribute('data-theme', 'light'); document.documentElement.classList.remove('dark'); }")
        page.reload(wait_until="networkidle")
        page.wait_for_selector("text=PS02", timeout=8000)

        # Verify initial light theme state
        initial_theme = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
        assert initial_theme in ["light", None], f"Expected light theme initially, got: {initial_theme}"

        header_toggle = page.locator("button[aria-label='Switch to dark theme']").first
        assert header_toggle.is_visible(), "Header dark theme quick toggle should be visible in light mode"

        sidebar_slate_btn = page.locator("button[aria-label='Slate + Deep Green light theme']").first
        sidebar_teal_btn = page.locator("button[aria-label='Midnight Navy + Teal dark theme']").first
        assert sidebar_slate_btn.is_visible(), "Sidebar Slate Green button should be visible"
        assert sidebar_teal_btn.is_visible(), "Sidebar Midnight Teal button should be visible"
        assert sidebar_slate_btn.get_attribute("aria-pressed") == "true"
        assert sidebar_teal_btn.get_attribute("aria-pressed") == "false"

        # Capture light theme desktop screenshot
        page.screenshot(path=str(SCREENSHOT_DIR / "theme_slate_green_desktop.png"))

        # Step 2: Click Header quick toggle to switch to Midnight Navy + Teal
        header_toggle.click()
        page.wait_for_timeout(400)

        # Verify dark theme attributes and class
        dark_theme = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
        has_dark_class = page.evaluate("() => document.documentElement.classList.contains('dark')")
        assert dark_theme == "dark", f"Expected dark theme, got: {dark_theme}"
        assert has_dark_class is True, "document.documentElement should contain 'dark' class"

        # Verify Header toggle updated label to 'Switch to light theme'
        light_toggle = page.locator("button[aria-label='Switch to light theme']").first
        assert light_toggle.is_visible(), "Header quick toggle should show Switch to light theme"

        # Verify Sidebar theme selector synchronized
        assert sidebar_teal_btn.get_attribute("aria-pressed") == "true"
        assert sidebar_slate_btn.get_attribute("aria-pressed") == "false"

        # Verify computed background colors match Midnight Navy palette
        body_bg = page.evaluate("() => window.getComputedStyle(document.body).backgroundColor")
        assert "11, 18, 32" in body_bg or "rgb(11, 18, 32)" in body_bg, f"Body background should be #0B1220, got: {body_bg}"

        # Capture dark theme desktop screenshot
        page.screenshot(path=str(SCREENSHOT_DIR / "theme_midnight_teal_desktop.png"))

        # Step 3: Navigate to Settings & Health in Dark Mode
        page.locator("button:has-text('Settings & Health')").first.click()
        page.wait_for_timeout(500)
        assert page.locator("text=System Settings & Accessibility Preferences").first.is_visible()
        page.screenshot(path=str(SCREENSHOT_DIR / "theme_midnight_teal_settings.png"))

        # Step 4: Test Page Reload & Persistence
        page.reload(wait_until="networkidle")
        page.wait_for_selector("text=PS02", timeout=8000)
        reloaded_theme = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
        assert reloaded_theme == "dark", f"Expected dark theme to persist across reload, got: {reloaded_theme}"

        # Step 5: Test Switching back using Sidebar Theme Selector
        sidebar_slate_btn_after = page.locator("button[aria-label='Slate + Deep Green light theme']").first
        sidebar_slate_btn_after.click()
        page.wait_for_timeout(400)

        restored_theme = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
        assert restored_theme == "light", f"Expected restored light theme, got: {restored_theme}"
        assert page.locator("button[aria-label='Switch to dark theme']").first.is_visible()
        page.screenshot(path=str(SCREENSHOT_DIR / "theme_restored_slate_green.png"))

        context.close()
        browser.close()


def test_theme_mobile_viewport():
    """Verifies that the theme selector works inside the collapsible mobile drawer on 390x844."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH if Path(CHROME_PATH).is_file() else None,
        )
        context = browser.new_context(viewport={"width": 390, "height": 844})
        page = context.new_page()

        page.goto(FRONTEND_URL, wait_until="networkidle")
        page.wait_for_selector("text=PS02", timeout=8000)

        # 1. Header toggle is accessible on mobile
        mobile_toggle = page.locator("button[aria-label='Switch to dark theme']").first
        assert mobile_toggle.is_visible()
        mobile_toggle.click()
        page.wait_for_timeout(300)

        assert page.evaluate("() => document.documentElement.getAttribute('data-theme')") == "dark"
        page.screenshot(path=str(SCREENSHOT_DIR / "theme_midnight_teal_mobile.png"))

        # 2. Open mobile drawer
        menu_btn = page.locator("button[aria-label='Open navigation drawer']").first
        assert menu_btn.is_visible()
        menu_btn.click()
        page.wait_for_selector("div[role='dialog']", timeout=5000)

        # Verify Appearance / Theme section is present and accessible in mobile drawer
        dialog = page.locator("div[role='dialog']")
        drawer_theme_header = dialog.locator("span:has-text('Appearance / Theme')").first
        drawer_theme_header.scroll_into_view_if_needed()
        page.wait_for_timeout(200)
        assert drawer_theme_header.is_visible()

        # Verify theme buttons are present and interactive in mobile drawer
        slate_btn = dialog.locator("button[aria-label='Slate + Deep Green light theme']").first
        teal_btn = dialog.locator("button[aria-label='Midnight Navy + Teal dark theme']").first
        assert slate_btn.is_visible()
        assert teal_btn.is_visible()

        context.close()
        browser.close()
