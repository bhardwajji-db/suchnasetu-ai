"""
Scenario 14 Playwright Acceptance Test:
Confirm top-bar Sign In button is removed and sidebar replacement account entry works.
"""

from pathlib import Path
import time
import sys
import subprocess
import urllib.request
import pytest
from playwright.sync_api import sync_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
FRONTEND_URL = "http://127.0.0.1:5173"
BACKEND_URL = "http://127.0.0.1:8000"


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
        time.sleep(0.5)

    assert ready, "Servers failed to become healthy within timeout"
    yield
    for p in spawned:
        try:
            p.terminate()
            p.wait(timeout=3)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass


def test_scenario_14_topbar_cleaned_and_sidebar_account_entry():
    """
    Verifies Phase 4 & Phase 5:
    1. Standalone top-bar Sign In button is removed from <header>.
    2. Subtle Account / Sign In entry is rendered in <aside> sidebar.
    3. Clicking sidebar sign in opens full-page auth view.
    4. Return button safely returns back to dashboard.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH if Path(CHROME_PATH).is_file() else None,
        )
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # Step 1: Open Application & wait for React mount
        page.goto(FRONTEND_URL, wait_until="networkidle", timeout=30000)
        page.wait_for_selector("text=PS02", timeout=10000)

        # Step 2: Verify Top Header is Clean (No Standalone Sign In button in header)
        header = page.locator("header")
        assert header.is_visible(), "Top header not visible"
        header_signin_btn = header.locator("button:has-text('Sign In'), button[aria-label='Sign In to citizen account']")
        assert header_signin_btn.count() == 0, "Top navigation header should NOT contain standalone Sign In button"

        # Step 3: Verify Top Header Preserves Branding, Health, Provider & Languages
        assert header.locator("text=PS02").first.is_visible()
        assert header.locator("button:has-text('EN')").is_visible()
        assert header.locator("button:has-text('हिन्दी')").is_visible()

        # Step 4: Verify Sidebar Contains Accessible Citizen Account Entry for Guests
        sidebar = page.locator("aside.hidden.md\\:flex, aside").first
        assert sidebar.is_visible(), "Sidebar not visible"
        
        sidebar_account_btn = sidebar.locator("button[aria-label='Sign In to citizen account']").first
        assert sidebar_account_btn.is_visible(), "Sidebar must display subtle citizen account entry"
        assert "Sign In" in sidebar_account_btn.inner_text()
        assert "Save notices & progress" in sidebar_account_btn.inner_text()

        # Step 5: Click Sidebar Account Entry to Open Auth Page View
        sidebar_account_btn.click()
        page.wait_for_timeout(600)

        # Step 6: Verify Dedicated Auth Page View Renders with Accessible Controls
        assert page.locator("input[type='email']").is_visible()
        assert page.locator("input[type='password']").is_visible()
        assert page.locator("button[type='submit']").is_visible()

        # Step 7: Verify Return to Application Button
        return_btn = page.locator("button[aria-label='Return to application'], button[aria-label='Return to Main Application']").first
        assert return_btn.is_visible(), "Return to application button must be visible on auth page"
        return_btn.click()
        page.wait_for_timeout(500)

        # Step 8: Verify Returned Safely to Main Dashboard View
        assert page.locator("h1:has-text('Dashboard Overview'), h1:has-text('Citizen Civic Dashboard')").is_visible()

        browser.close()
