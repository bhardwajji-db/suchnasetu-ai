"""
Playwright End-to-End Analysis Workflow & Tab Visual Verification.
Performs live Gemma 4 inference through the real web UI, verifies all 4 tabs,
and captures visual evidence screenshots.
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
APP_URL = "http://localhost:8501"
SCREENSHOTS_DIR = Path("assets/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def test_full_browser_workflow():
    print("\n" + "=" * 70)
    print("🚀 LIVE BROWSER WORKFLOW: GEMMA 4 INFERENCE + ALL 4 TABS VERIFICATION")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()

        print(f"[1/5] Navigating to {APP_URL}...")
        page.goto(APP_URL, wait_until="networkidle", timeout=25000)
        page.wait_for_selector("[role=tab]", timeout=15000)

        # 1. Load Demo Notice
        print("[2/5] Loading Competition Demo Notice...")
        demo_btn = page.wait_for_selector('button:has-text("Competition Demo")')
        demo_btn.click()
        page.wait_for_timeout(2000)

        # 2. Trigger Real Gemma 4 Analysis
        print("[3/5] Clicking 'Analyze Notice with Gemma 4'...")
        t_start = time.time()
        analyze_btn = page.wait_for_selector('button:has-text("Analyze Notice with Gemma 4")')
        analyze_btn.click()

        # Wait for analysis to finish (jump button appears)
        print("  Waiting for Gemma 4 inference to complete (up to 90s)...")
        page.wait_for_selector(".st-key-btn_jump_tab2 button", timeout=90000)
        t_dur = time.time() - t_start
        print(f"  ✓ Live Gemma 4 Analysis finished in {t_dur:.2f}s!")

        # Screenshot Tab 1 with success banner
        page.screenshot(path=str(SCREENSHOTS_DIR / "workflow_tab1_analyzed.png"))
        print("  ✓ Captured workflow_tab1_analyzed.png")

        # 3. Switch to Tab 2 (Grounded Fact Breakdown) via Sidebar Nav
        print("[4/5] Navigating to Tab 2 (Extracted Facts)...")
        page.click('button:has-text("2. Extracted Facts")')
        page.wait_for_timeout(2000)

        panel = page.wait_for_selector('[role="tabpanel"]')
        card_text = panel.inner_text()
        assert "Grounded Fact Breakdown" in card_text, "Fact breakdown tab title missing"
        assert len(card_text) > 500, f"Expected rich fact cards, got length {len(card_text)}"
        page.screenshot(path=str(SCREENSHOTS_DIR / "workflow_tab2_facts.png"))
        print(f"  ✓ Tab 2 verified ({len(card_text)} chars) & captured: workflow_tab2_facts.png")

        # 4. Switch to Tab 3 (Summary & Actions) via Sidebar Nav
        print("[5/5] Navigating to Tab 3 (Summary & Actions)...")
        page.click('button:has-text("3. Summary & Actions")')
        page.wait_for_timeout(2000)

        panel = page.wait_for_selector('[role="tabpanel"]')
        tab3_text = panel.inner_text()
        assert "Summary & Action Checklist" in tab3_text, "Tab 3 title missing"
        assert len(tab3_text) > 300, f"Expected summary & checklist content, got length {len(tab3_text)}"
        page.screenshot(path=str(SCREENSHOTS_DIR / "workflow_tab3_summary.png"))
        print(f"  ✓ Tab 3 verified ({len(tab3_text)} chars) & captured: workflow_tab3_summary.png")

        # 5. Switch to Tab 4 (Follow-Up Q&A) via Sidebar Nav and ask a question
        print("[Bonus] Navigating to Tab 4 and asking grounded question...")
        page.click('button:has-text("4. Follow-Up Q&A")')
        page.wait_for_timeout(2000)

        page.click('button:has-text("Required Documents?")')
        page.wait_for_timeout(1500)

        q_inp = page.locator('.st-key-qa_input_text_box input')
        if not q_inp.input_value():
            q_inp.fill("What documents are needed to apply?")

        page.click('.st-key-btn_ask_qa button')
        print("  Waiting for Q&A answer...")
        page.wait_for_selector('text=Conversation History', timeout=60000)
        page.wait_for_timeout(1500)
        page.screenshot(path=str(SCREENSHOTS_DIR / "workflow_tab4_qa.png"))
        print("  ✓ Tab 4 verified & captured: workflow_tab4_qa.png")

        context.close()
        browser.close()

    print("\n" + "=" * 70)
    print("🎉 FULL LIVE INFERENCE BROWSER WORKFLOW VERIFIED SUCCESSFULLY!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    test_full_browser_workflow()
