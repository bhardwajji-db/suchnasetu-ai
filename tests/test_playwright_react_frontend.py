"""
Playwright Acceptance and Multi-Viewport Test Suite for Notice2Action AI (React + FastAPI).
Tests real browser rendering, layout overflow, and complete end-to-end workflow in headless Chrome.
"""

import sys
import time
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
FRONTEND_URL = "http://127.0.0.1:5173"
SCREENSHOT_DIR = Path("assets/screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORTS = [
    {"name": "Large Desktop", "width": 1920, "height": 1080},
    {"name": "Standard Laptop", "width": 1366, "height": 768},
    {"name": "Compact Laptop", "width": 1280, "height": 720},
    {"name": "Tablet Landscape", "width": 1024, "height": 768},
    {"name": "Tablet Portrait", "width": 768, "height": 1024},
    {"name": "Mobile Smartphone", "width": 390, "height": 844},
]


def test_react_frontend_multi_viewport_and_no_overflow():
    """Verifies that the React frontend renders with zero horizontal overflow across 6 viewports."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH if Path(CHROME_PATH).is_file() else None,
        )

        for vp in VIEWPORTS:
            context = browser.new_context(viewport={"width": vp["width"], "height": vp["height"]})
            page = context.new_page()

            page.goto(FRONTEND_URL, wait_until="networkidle")
            page.wait_for_selector("text=Notice2Action AI", timeout=10000)

            # Assert zero horizontal overflow
            scroll_width, client_width = page.evaluate("() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]")
            assert scroll_width <= client_width + 1, (
                f"Horizontal overflow at {vp['name']} ({vp['width']}x{vp['height']}): "
                f"scrollWidth={scroll_width} > clientWidth={client_width}"
            )

            # Screenshot
            img_path = SCREENSHOT_DIR / f"react_viewport_{vp['width']}x{vp['height']}.png"
            page.screenshot(path=str(img_path))
            assert img_path.is_file()

            context.close()
        browser.close()


def test_react_frontend_full_workflow_and_tabs():
    """
    Exercises complete end-to-end user journey in React frontend:
    1. Navigation tab switching
    2. Quick-load demo notice fixture
    3. Notice analysis with local Gemma 4 (or verify buffer)
    4. Grounded Facts inspection
    5. Summary and Checklist interaction
    6. Suggested Q&A inquiry and grounded answer verification
    7. Stale buffer detection
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH if Path(CHROME_PATH).is_file() else None,
        )
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()

        # Step 1: Ingestion view
        page.goto(FRONTEND_URL, wait_until="networkidle")
        page.wait_for_selector("text=Notice2Action AI", timeout=10000)

        # Step 2: Load Competition Demo
        demo_btn = page.locator("button:has-text('Competition Demo (TEST-SCH)')").first
        demo_btn.click()
        page.wait_for_timeout(1000)

        # Verify notice buffer has content
        buffer_val = page.locator("textarea").input_value()
        assert "TEST-SCH-2026-001" in buffer_val

        # Step 3: Run Analysis
        analyze_btn = page.locator("button:has-text('Analyze Notice with Local Gemma 4')")
        assert analyze_btn.is_enabled()
        analyze_btn.click()

        # Wait for analysis to complete (up to 90s for local Ollama)
        page.wait_for_selector("text=Notice Analyzed", timeout=90000)

        # Screenshot analyzed ingestion tab
        page.screenshot(path=str(SCREENSHOT_DIR / "react_workflow_01_ingestion_analyzed.png"))

        # Step 4: Switch to Tab 2 (Grounded Facts)
        page.locator("button:has-text('2. Grounded Facts')").click()
        page.wait_for_selector("text=Notice Purpose & Program Name", timeout=5000)
        page.wait_for_selector("text=Stated", timeout=5000)
        page.screenshot(path=str(SCREENSHOT_DIR / "react_workflow_02_grounded_facts.png"))

        # Step 5: Switch to Tab 3 (Summary & Actions)
        page.locator("button:has-text('3. Summary & Actions')").click()
        page.wait_for_selector("text=Sequential Action Checklist", timeout=5000)
        page.wait_for_selector("text=Download Markdown", timeout=5000)
        page.wait_for_selector("text=Add to Calendar", timeout=5000)

        # Toggle first checklist item
        step1 = page.locator("text=Step 1").first
        step1.click()
        page.wait_for_timeout(500)
        page.screenshot(path=str(SCREENSHOT_DIR / "react_workflow_03_summary_checklist.png"))

        # Step 6: Switch to Tab 4 (Follow-Up Q&A)
        page.locator("button:has-text('4. Follow-Up Q&A')").click()
        page.wait_for_selector("text=Notice-Grounded Q&A Assistant", timeout=5000)

        # Click suggested question
        sug_btn = page.locator("button:has-text('Required Documents?')").first
        sug_btn.click()

        # Wait for answer
        page.wait_for_selector("text=Supporting Quote from Notice", timeout=60000)
        page.screenshot(path=str(SCREENSHOT_DIR / "react_workflow_04_qa_grounded.png"))

        # Step 7: Test Stale Warning Detection
        page.locator("button:has-text('1. Ingestion & OCR')").click()
        page.wait_for_timeout(500)
        page.locator("textarea").fill(buffer_val + "\n\nADDITIONAL AMENDMENT: Deadline extended to 15 November 2026.")
        page.wait_for_timeout(1000)

        # Stale warning should now be visible
        page.wait_for_selector("text=Notice Buffer Modified", timeout=5000)
        page.screenshot(path=str(SCREENSHOT_DIR / "react_workflow_05_stale_warning.png"))

        context.close()
        browser.close()
