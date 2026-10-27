from pathlib import Path
import re

file_path = Path("tests/test_master_e2e_acceptance.py")
content = file_path.read_text(encoding="utf-8")

# 1. Update duplicate status code
old_dup = """    # 2. Duplicate registration rejection
    dup = client1.post("/api/auth/register", json={
        "name": "Citizen One Imposter",
        "email": email_user1,
        "password": password,
        "confirm_password": password
    })
    assert dup.status_code == 200
    assert "already" in dup.json()["message"].lower() or dup.json().get("already_verified")"""

new_dup = """    # 2. Duplicate registration rejection
    dup = client1.post("/api/auth/register", json={
        "name": "Citizen One Imposter",
        "email": email_user1,
        "password": password,
        "confirm_password": password
    })
    assert dup.status_code == 400
    assert "already" in dup.json().get("detail", "").lower()"""

content = content.replace(old_dup.replace("\r\n", "\n"), new_dup.replace("\r\n", "\n"))
content = content.replace(old_dup, new_dup)

# 2. Add _goto_app helper
helper = '''
def _goto_app(page):
    page.goto(FRONTEND_URL, wait_until="networkidle")
    guest_btn = page.locator("button[aria-label='Continue to application as guest'], button:has-text('Continue as Guest')").first
    if guest_btn.is_visible():
        guest_btn.click()
        page.wait_for_timeout(400)
    page.wait_for_selector("text=PS02", timeout=8000)
'''
if "_goto_app" not in content:
    content = content.replace("def test_master_browser_workflows_and_viewports():", helper + "\ndef test_master_browser_workflows_and_viewports():")

content = content.replace(
    'page.goto(FRONTEND_URL, wait_until="networkidle")\n            page.wait_for_selector("text=PS02", timeout=8000)',
    '_goto_app(page)'
)
content = content.replace(
    'page.goto(FRONTEND_URL, wait_until="networkidle")\n        page.wait_for_selector("text=PS02", timeout=8000)',
    '_goto_app(page)'
)

file_path.write_text(content, encoding="utf-8")
print("UPDATED MASTER TEST")
