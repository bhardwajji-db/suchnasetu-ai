import os
from pathlib import Path
import markdown
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MD_PATH = PROJECT_ROOT / "reports" / "SochnaSetu_AI_Project_Health_Audit.md"
PDF_PATH = PROJECT_ROOT / "reports" / "SochnaSetu_AI_Project_Health_Audit.pdf"
HTML_TEMP_PATH = PROJECT_ROOT / "reports" / "SochnaSetu_AI_Project_Health_Audit.html"

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]
chrome_path = next((c for c in CHROME_CANDIDATES if Path(c).is_file()), None)

def generate_pdf():
    print(f"Reading markdown from: {MD_PATH}")
    md_text = MD_PATH.read_text(encoding="utf-8")

    # Convert markdown to HTML with table and code extensions
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"]
    )

    styled_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SochnaSetu AI — Health Audit Report</title>
<style>
  @page {{
    size: A4;
    margin: 18mm 15mm 18mm 15mm;
    @bottom-right {{
      content: counter(page);
    }}
  }}
  *, *::before, *::after {{
    box-sizing: border-box;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #12233D;
    background-color: #FFFFFF;
    line-height: 1.55;
    font-size: 10pt;
    margin: 0;
    padding: 0;
  }}
  .report-header {{
    border-bottom: 3px solid #08785D;
    padding-bottom: 12px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }}
  .report-title-area h1 {{
    font-size: 18pt;
    font-weight: 800;
    color: #08785D;
    margin: 0 0 6px 0;
    letter-spacing: -0.02em;
  }}
  .badge {{
    display: inline-block;
    padding: 3px 8px;
    font-size: 8pt;
    font-weight: 700;
    border-radius: 4px;
    text-transform: uppercase;
    background-color: #E6F4F0;
    color: #08785D;
    border: 1px solid #A7E0D3;
  }}
  h1 {{
    font-size: 16pt;
    color: #0D1E35;
    border-bottom: 1.5px solid #E1E7EE;
    padding-bottom: 6px;
    margin-top: 24px;
    margin-bottom: 12px;
  }}
  h2 {{
    font-size: 13pt;
    color: #08785D;
    margin-top: 20px;
    margin-bottom: 10px;
    border-bottom: 1px solid #E6ECEF;
    padding-bottom: 4px;
  }}
  h3 {{
    font-size: 11pt;
    color: #12233D;
    margin-top: 14px;
    margin-bottom: 6px;
  }}
  p {{
    margin: 0 0 10px 0;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0 18px 0;
    font-size: 9pt;
  }}
  th, td {{
    padding: 7px 10px;
    text-align: left;
    border: 1px solid #D5DFE8;
    vertical-align: top;
  }}
  th {{
    background-color: #F1F6F5;
    color: #08785D;
    font-weight: 700;
  }}
  tr:nth-child(even) {{
    background-color: #FBFDFD;
  }}
  code {{
    font-family: Consolas, "Courier New", monospace;
    font-size: 8.5pt;
    background-color: #F1F5F9;
    padding: 1px 4px;
    border-radius: 3px;
    color: #0F172A;
    border: 1px solid #E2E8F0;
  }}
  pre {{
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 10px 14px;
    overflow-x: auto;
    font-size: 8.5pt;
    line-height: 1.4;
    margin: 12px 0;
  }}
  pre code {{
    background-color: transparent;
    padding: 0;
    border: none;
  }}
  ul, ol {{
    margin: 6px 0 12px 20px;
    padding: 0;
  }}
  li {{
    margin-bottom: 4px;
  }}
  hr {{
    border: 0;
    height: 1px;
    background: #E1E7EE;
    margin: 20px 0;
  }}
  strong {{
    color: #0D1E35;
  }}
</style>
</head>
<body>
  {html_body}
</body>
</html>
"""
    HTML_TEMP_PATH.write_text(styled_html, encoding="utf-8")
    print(f"Temporary styled HTML saved to: {HTML_TEMP_PATH}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=chrome_path,
        )
        page = browser.new_page()
        page.goto(f"file:///{HTML_TEMP_PATH.as_posix()}", wait_until="networkidle")

        page.pdf(
            path=str(PDF_PATH),
            format="A4",
            print_background=True,
            margin={
                "top": "15mm",
                "bottom": "15mm",
                "left": "15mm",
                "right": "15mm",
            },
        )
        browser.close()

    assert PDF_PATH.is_file(), f"PDF failed to generate at {PDF_PATH}"
    size_kb = PDF_PATH.stat().st_size / 1024
    print(f"SUCCESS: Generated PDF at {PDF_PATH} ({size_kb:.2f} KB)")

if __name__ == "__main__":
    generate_pdf()
