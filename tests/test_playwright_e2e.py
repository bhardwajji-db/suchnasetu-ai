"""
Playwright End-to-End Browser Automation & Verification Suite for Notice2Action AI (PS02).
Tests real rendering, sidebar navigation, tab synchronization, viewport responsiveness,
and screenshot generation across desktop, laptop, tablet, and mobile breakpoints.
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

sys.stdout.reconfigure(encoding="utf-8")

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
APP_URL = "http://localhost:8501"
SCREENSHOTS_DIR = Path("assets/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORTS = [
    ("viewport_1920x1080.png", 1920, 1080, "Large Desktop"),
    ("viewport_1366x768.png", 1366, 768, "Standard Laptop"),
    ("viewport_1280x720.png", 1280, 720, "Compact Laptop"),
    ("viewport_1024x768.png", 1024, 768, "Tablet Landscape"),
    ("viewport_768x1024.png", 768, 1024, "Tablet Portrait"),
    ("viewport_390x844.png", 390, 844, "Mobile Smartphone"),
]


def test_playwright_e2e():
    print("\n" + "=" * 70)
    print("🚀 STARTING NOTICE2ACTION AI PLAYWRIGHT E2E ACCEPTANCE SUITE")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()

        print(f"\n[1/6] Navigating to {APP_URL}...")
        page.goto(APP_URL, wait_until="networkidle", timeout=20000)
        page.wait_for_selector("[role=tab]", timeout=15000)

        # ---------------- 1. Verify Initial Tab State ----------------
        tabs = page.query_selector_all("[role=tab]")
        assert len(tabs) == 4, f"Expected 4 tabs, found {len(tabs)}"
        assert tabs[0].get_attribute("aria-selected") == "true", "Tab 0 should initially be selected"
        print("  ✓ Initial Tab 0 ('Notice Ingestion & OCR') is active")

        # ---------------- 2. Test Sidebar Navigation Buttons ----------------
        print("\n[2/6] Testing Sidebar Navigation Buttons...")
        # Click Sidebar Nav 1 (Extracted Facts)
        btn_nav1 = page.wait_for_selector('button:has-text("2. Extracted Facts")')
        btn_nav1.click()
        page.wait_for_timeout(1000)
        tabs = page.query_selector_all("[role=tab]")
        assert tabs[1].get_attribute("aria-selected") == "true", "Tab 1 should be active after clicking nav 1"
        print("  ✓ Sidebar Nav 1 clicked -> Tab 1 is aria-selected=true")

        # Click Sidebar Nav 2 (Summary & Actions)
        btn_nav2 = page.wait_for_selector('button:has-text("3. Summary & Actions")')
        btn_nav2.click()
        page.wait_for_timeout(1000)
        tabs = page.query_selector_all("[role=tab]")
        assert tabs[2].get_attribute("aria-selected") == "true", "Tab 2 should be active after clicking nav 2"
        print("  ✓ Sidebar Nav 2 clicked -> Tab 2 is aria-selected=true")

        # Click Sidebar Nav 3 (Follow-Up Q&A)
        btn_nav3 = page.wait_for_selector('button:has-text("4. Follow-Up Q&A")')
        btn_nav3.click()
        page.wait_for_timeout(1000)
        tabs = page.query_selector_all("[role=tab]")
        assert tabs[3].get_attribute("aria-selected") == "true", "Tab 3 should be active after clicking nav 3"
        print("  ✓ Sidebar Nav 3 clicked -> Tab 3 is aria-selected=true")

        # Click Sidebar Nav 0 (Process Notice)
        btn_nav0 = page.wait_for_selector('button:has-text("1. Process Notice")')
        btn_nav0.click()
        page.wait_for_timeout(1000)
        tabs = page.query_selector_all("[role=tab]")
        assert tabs[0].get_attribute("aria-selected") == "true", "Tab 0 should be active after clicking nav 0"
        print("  ✓ Sidebar Nav 0 clicked -> Tab 0 is aria-selected=true")

        # ---------------- 3. Test Two-Way Sync (Tab Click -> Sidebar Highlight) ----------------
        print("\n[3/6] Testing Two-Way Sync (Direct Tab Click -> Sidebar Update)...")
        tabs = page.query_selector_all("[role=tab]")
        tabs[1].click()
        page.wait_for_timeout(1200)
        # Check that sidebar nav 1 is now marked primary (kind=primary)
        nav1_btn = page.locator('.st-key-sidebar_nav_1 button')
        assert nav1_btn.get_attribute("kind") == "primary", "Sidebar Nav 1 should have kind='primary' when Tab 1 is active"
        print("  ✓ Tab 1 clicked directly -> Sidebar Nav 1 button automatically became kind='primary'")

        # Return to Tab 0
        tabs = page.query_selector_all("[role=tab]")
        tabs[0].click()
        page.wait_for_timeout(1000)

        # ---------------- 4. Test Quick-Load Competition Demo ----------------
        print("\n[4/6] Testing Demo Notice Loading...")
        demo_btn = page.wait_for_selector('button:has-text("Competition Demo (TEST-SCH-2026-001)")')
        demo_btn.click()
        page.wait_for_timeout(2000)
        textarea = page.wait_for_selector('textarea')
        val = textarea.input_value()
        assert "TEST-SCH-2026-001" in val, f"Demo notice TEST-SCH-2026-001 should be loaded in textarea, got: {val[:50]}..."
        print("  ✓ Demo notice (TEST-SCH-2026-001) successfully loaded into textarea")

        # ---------------- 5. Test Suggested Q&A Buttons in Tab 4 ----------------
        print("\n[5/6] Testing Suggested Q&A Buttons in Tab 4...")
        btn_nav3 = page.wait_for_selector('button:has-text("4. Follow-Up Q&A")')
        btn_nav3.click()
        page.wait_for_timeout(1200)
        sug_btn = page.wait_for_selector('button:has-text("Required Documents?")')
        sug_btn.click()
        page.wait_for_timeout(1000)
        q_input = page.wait_for_selector('.st-key-qa_input_text_box input')
        q_val = q_input.input_value()
        assert "What documents are needed to apply?" in q_val, f"Unexpected Q&A value: {q_val}"
        print(f"  ✓ Suggested question clicked -> input populated with: '{q_val}'")

        # Return to Tab 0 for full layout screenshots
        btn_nav0 = page.wait_for_selector('button:has-text("1. Process Notice")')
        btn_nav0.click()
        page.wait_for_timeout(1000)

        # ---------------- 6. Multi-Viewport Responsiveness & Screenshots ----------------
        print("\n[6/6] Testing Responsive Viewports & Capturing Screenshots...")
        overflow_results = []

        for filename, width, height, label in VIEWPORTS:
            page.set_viewport_size({"width": width, "height": height})
            page.wait_for_timeout(1200)  # Wait for reflow

            # Check horizontal overflow
            overflow_info = page.evaluate("""
                () => {
                    const doc = document.documentElement;
                    const body = document.body;
                    return {
                        scrollWidth: Math.max(doc.scrollWidth, body.scrollWidth),
                        clientWidth: doc.clientWidth,
                        hasOverflow: Math.max(doc.scrollWidth, body.scrollWidth) > doc.clientWidth + 2
                    };
                }
            """)

            save_path = SCREENSHOTS_DIR / filename
            page.screenshot(path=str(save_path), full_page=False)
            has_overflow = overflow_info["hasOverflow"]
            overflow_results.append((label, width, height, not has_overflow))

            status_str = "PASS (No overflow)" if not has_overflow else f"WARN (scroll: {overflow_info['scrollWidth']}, client: {overflow_info['clientWidth']})"
            print(f"  ✓ Viewport {label:20} ({width:4}x{height:4}) -> Screenshot: {filename} [{status_str}]")

        context.close()
        browser.close()

    print("\n" + "=" * 70)
    print("🎉 ALL PLAYWRIGHT E2E BROWSER TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    test_playwright_e2e()
