"""
Quality Assurance and Visual Page Verification for Generated PDF Report.
"""
import os
from pypdf import PdfReader
import pypdfium2 as pdfium

OUTPUT_DIR = "SochnaSetu_AI_Final_Report"
PDF_PATH = os.path.join(OUTPUT_DIR, "SochnaSetu_AI_Final_Mini_Project_Report.pdf")
CHECKLIST_PATH = os.path.join(OUTPUT_DIR, "SochnaSetu_AI_Report_Compliance_Checklist.pdf")

def inspect_report():
    print(f"=== AUDITING {PDF_PATH} ===")
    reader = PdfReader(PDF_PATH)
    total_pages = len(reader.pages)
    print(f"Total Pages: {total_pages}")
    
    empty_pages = []
    page_samples = {}
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        char_count = len(text.strip())
        if char_count < 20: # May be an image-only page or empty
            empty_pages.append(idx + 1)
        # Store snippet of first line
        first_line = text.strip().split("\n")[0] if text.strip() else "[NO TEXT / PURE IMAGE]"
        page_samples[idx + 1] = (char_count, first_line[:60])

    print("\n--- PAGE BY PAGE INVENTORY ---")
    for p_num in range(1, total_pages + 1):
        cnt, fl = page_samples[p_num]
        print(f"Page {p_num:02d}: {cnt:4d} chars | {fl}")

    print(f"\nPages with < 20 text chars: {empty_pages}")
    
    # Render key sample pages to verify visual layout
    pdf = pdfium.PdfDocument(PDF_PATH)
    sample_pages_to_render = [1, 2, 3, 10, 16, 20, 25, 30, total_pages]
    os.makedirs(os.path.join(OUTPUT_DIR, "rendered_inspection"), exist_ok=True)
    for p in sample_pages_to_render:
        if p <= total_pages:
            page = pdf[p - 1]
            image = page.render(scale=2.0).to_pil()
            dest = os.path.join(OUTPUT_DIR, "rendered_inspection", f"page_{p:02d}.png")
            image.save(dest)
            print(f"Saved visual render of Page {p:02d} to: {dest}")

if __name__ == "__main__":
    inspect_report()
