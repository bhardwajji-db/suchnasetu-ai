import re
from pathlib import Path

file_path = Path("tests/test_playwright_interactive_inventory.py")
content = file_path.read_text(encoding="utf-8")

old_pattern = r"        # 4\. Verify Language Switching.*?page\.screenshot\(path=str\(SCREENSHOT_DIR"
new_text = """        # 4. Verify Single Unified Language Selector (EN -> HI -> EN)
        lang_select = page.locator("select[aria-label='Select Website Language']")
        assert lang_select.is_visible()
        lang_select.select_option("hi")
        page.wait_for_timeout(400)
        lang_select.select_option("en")
        page.wait_for_timeout(400)

        page.screenshot(path=str(SCREENSHOT_DIR"""

updated = re.sub(old_pattern, new_text, content, flags=re.DOTALL)
if updated != content:
    file_path.write_text(updated, encoding="utf-8")
    print("SUCCESS")
else:
    print("PATTERN NOT MATCHED")
