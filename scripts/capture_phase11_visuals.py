import os
import sys
import shutil
import sqlite3
import urllib.request
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ARTIFACT_DIR = r"C:\Users\Avinash\.gemini\antigravity\brain\fbfce4c4-6320-4a72-aa55-be593fe67410"
os.makedirs("test_reports", exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

# 1. Setup a test citizen account via API and verify in SQLite
email = "rajesh.sharma@gov.in"
password = "Password123!"
name = "Rajesh Sharma"

try:
    req = urllib.request.Request(
        "http://localhost:8000/api/auth/register",
        data=json.dumps({
            "name": name,
            "email": email,
            "password": password,
            "confirm_password": password
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req)
    print("Registered citizen user.")
except Exception as e:
    print(f"User might already exist ({e}).")

# Ensure is_verified is 1 in data/suchnasetu.db
db_file = Path("data") / "suchnasetu.db"
if db_file.exists():
    with sqlite3.connect(str(db_file)) as conn:
        conn.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))
        conn.commit()
    print("User is_verified set to 1 in suchnasetu.db.")

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH if Path(CHROME_PATH).is_file() else None,
        )

        # Context 1: Desktop Viewport (1366x850)
        context = browser.new_context(viewport={"width": 1366, "height": 850})
        page = context.new_page()

        # Step 1: Open app as Guest in Slate + Deep Green (Light)
        page.goto("http://localhost:5173", wait_until="networkidle")
        page.wait_for_selector("text=PS02", timeout=8000)

        # Force light theme initially
        page.evaluate("() => { localStorage.setItem('suchnasetu_theme', 'light'); document.documentElement.setAttribute('data-theme', 'light'); document.documentElement.classList.remove('dark'); }")
        page.reload(wait_until="networkidle")
        page.wait_for_selector("text=PS02", timeout=8000)
        page.wait_for_timeout(1000)

        # Capture Guest Light Dashboard
        guest_light = "test_reports/phase11_guest_light.png"
        page.screenshot(path=guest_light, full_page=False)
        shutil.copy(guest_light, os.path.join(ARTIFACT_DIR, "phase11_guest_light.png"))
        print("Captured phase11_guest_light.png")

        # Step 2: Sign in through the header button
        sign_in_btn = page.locator('button[aria-label="Sign In or Create Citizen Account"]')
        if sign_in_btn.is_visible():
            sign_in_btn.click()
            page.wait_for_selector('input[type="email"]', timeout=5000)

            # Fill credentials
            page.locator('input[type="email"]').fill(email)
            page.locator('input[type="password"]').fill(password)
            page.locator('button[type="submit"]:has-text("Sign In")').click()
            page.wait_for_timeout(2000)

        # Verify authenticated state with Avatar Initials
        avatar_btn = page.locator('button[aria-label="Citizen Account Menu"]')
        if avatar_btn.is_visible():
            print("Authenticated successfully! Avatar button is visible.")

            # Capture Authenticated Light Dashboard with Welcome Illustration & Avatar
            auth_light = "test_reports/phase11_authenticated_light.png"
            page.screenshot(path=auth_light, full_page=False)
            shutil.copy(auth_light, os.path.join(ARTIFACT_DIR, "phase11_authenticated_light.png"))
            print("Captured phase11_authenticated_light.png")

            # Step 3: Open Profile Avatar dropdown and capture
            avatar_btn.click()
            page.wait_for_timeout(600)
            dropdown_shot = "test_reports/phase11_profile_dropdown.png"
            page.screenshot(path=dropdown_shot, full_page=False)
            shutil.copy(dropdown_shot, os.path.join(ARTIFACT_DIR, "phase11_profile_dropdown.png"))
            print("Captured phase11_profile_dropdown.png")

            # Close dropdown by clicking header area
            page.mouse.click(100, 20)
            page.wait_for_timeout(300)

        # Step 4: Switch to Dark Theme (Midnight Navy + Teal)
        dark_toggle = page.locator('button[aria-label="Switch to dark theme"]')
        if dark_toggle.is_visible():
            dark_toggle.click()
            page.wait_for_timeout(1000)

            # Capture Authenticated Dark Dashboard
            auth_dark = "test_reports/phase11_authenticated_dark.png"
            page.screenshot(path=auth_dark, full_page=False)
            shutil.copy(auth_dark, os.path.join(ARTIFACT_DIR, "phase11_authenticated_dark.png"))
            print("Captured phase11_authenticated_dark.png")

        # Step 5: Mobile Viewport (390x844) Navigation Drawer
        mobile_ctx = browser.new_context(viewport={"width": 390, "height": 844})
        mobile_page = mobile_ctx.new_page()
        mobile_page.goto("http://localhost:5173", wait_until="networkidle")
        mobile_page.wait_for_selector("text=PS02", timeout=8000)

        # Open mobile drawer
        drawer_btn = mobile_page.locator('button[aria-label="Open navigation drawer"]')
        if drawer_btn.is_visible():
            drawer_btn.click()
            mobile_page.wait_for_timeout(800)
            drawer_shot = "test_reports/phase11_mobile_drawer.png"
            mobile_page.screenshot(path=drawer_shot, full_page=False)
            shutil.copy(drawer_shot, os.path.join(ARTIFACT_DIR, "phase11_mobile_drawer.png"))
            print("Captured phase11_mobile_drawer.png")

        browser.close()
        print("Completed visual verification and artifact generation.")

if __name__ == "__main__":
    run()
