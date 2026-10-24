import zipfile
from pathlib import Path

def create_docx_file(dest_path: Path, title: str, paragraphs: list[str]) -> None:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    body_xml = f'<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>{title}</w:t></w:r></w:p>'
    for p in paragraphs:
        safe_p = p.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        body_xml += f'<w:p><w:r><w:t>{safe_p}</w:t></w:r></w:p>'

    doc_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:body>{body_xml}</w:body>'
        '</w:document>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>'
    )

    with zipfile.ZipFile(dest_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', content_types)
        zf.writestr('_rels/.rels', rels)
        zf.writestr('word/document.xml', doc_xml)

title = "DEMO DEPARTMENT OF STUDENT SUPPORT (FICTIONAL)"
paragraphs = [
    "OFFICIAL NOTIFICATION: STUDENT TECHNOLOGY ASSISTANCE GRANT",
    "Notice Reference ID: DEMO-2026-017",
    "Date of Issue: 20 October 2026",
    "",
    "1. SCHEME PURPOSE & GRANT AMOUNT:",
    "The Demo Department of Student Support hereby announces the Student Technology Assistance Grant for academic year 2026-2027. Under this fictional welfare initiative, eligible undergraduate students will receive a one-time direct technology grant of Rs. 8,000 (Rupees Eight Thousand only) for purchasing learning equipment, digital tablets, or peripheral devices.",
    "",
    "2. ELIGIBILITY CONDITIONS:",
    "- Full-time undergraduate student currently enrolled at a fictional participating college or recognized institute.",
    "- Household annual income limit: Total family annual income must be Rs. 3,00,000 per year or less.",
    "- Application limit: Exactly one application per student is permitted. Duplicate submissions will be disqualified.",
    "",
    "3. KEY TIMELINE & IMPORTANT DATES:",
    "- Online Application Portal Opens: 25 October 2026",
    "- Application Submission Deadline: 15 November 2026, 5:00 PM IST",
    "- Declaration of Provisional Results: 30 November 2026",
    "- Grievance & Correction Window: 01 December 2026 to 03 December 2026",
    "",
    "4. MANDATORY REQUIRED DOCUMENTS:",
    "- Valid Student ID card issued by the participating institution.",
    "- Self-declared household income statement certifying annual income <= Rs. 3,00,000.",
    "- Duly completed fictional demo application form.",
    "- Study statement: A short explanation of how the technology equipment supports your degree study.",
    "",
    "5. APPLICATION PROCEDURE & CONTACT HELPDESK:",
    "Applications must be submitted exclusively via the designated fictional online portal: demo.invalid/student-grant",
    "Steps required: 1. Review eligibility criteria; 2. Prepare mandatory documentation; 3. Submit application before 15 November 2026, 5:00 PM IST; 4. Download and save the reference acknowledgment number.",
    "For technical assistance, email helpdesk@example.invalid. Note: This notice is purely for demonstration and testing purposes.",
]

dest1 = Path("tests/fixtures/fake_notice_for_testing.docx")
dest2 = Path("fake_notice_for_testing.docx")
create_docx_file(dest1, title, paragraphs)
create_docx_file(dest2, title, paragraphs)
print("Created fake_notice_for_testing.docx in tests/fixtures and project root.")
