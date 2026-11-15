"""
Academic DOCX Generator for SochnaSetu AI B.Tech Mini Project Report.
Follows AKTU CSE Academic Report Guidelines.
"""
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

OUTPUT_DIR = "SochnaSetu_AI_Final_Report"
DOCX_PATH = os.path.join(OUTPUT_DIR, "SochnaSetu_AI_Editable_Report.docx")
DIAGRAMS_DIR = os.path.join(OUTPUT_DIR, "diagrams")
SCREENSHOTS_DIR = os.path.join(OUTPUT_DIR, "screenshots")

NAVY = RGBColor(30, 58, 138)       # #1e3a8a
DARK_GRAY = RGBColor(51, 65, 85)   # #334155
BLACK = RGBColor(15, 23, 42)       # #0f172a

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def create_document():
    doc = docx.Document()
    
    # Page setup - A4 with AKTU margins (Left 1.25 in for binding, Top/Bottom/Right 1.0 in)
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.0)

    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = BLACK
    normal_style.paragraph_format.line_spacing = 1.25
    normal_style.paragraph_format.space_after = Pt(6)

    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(16)
        run.font.color.rgb = NAVY
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(12)
        return p

    def add_heading_1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(14)
        run.font.color.rgb = NAVY
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(12.5)
        run.font.color.rgb = DARK_GRAY
        return p

    def add_heading_3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.italic = True
        run.font.size = Pt(12)
        run.font.color.rgb = DARK_GRAY
        return p

    def add_body(text, bold_prefix=None):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            run_b = p.add_run(bold_prefix)
            run_b.bold = True
            run_b.font.color.rgb = BLACK
        run = p.add_run(text)
        run.font.size = Pt(12)
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        if bold_prefix:
            run_b = p.add_run(bold_prefix)
            run_b.bold = True
            run_b.font.color.rgb = BLACK
        run = p.add_run(text)
        run.font.size = Pt(11.5)
        return p

    def add_image(image_path, width_in_inches, caption):
        if os.path.exists(image_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.add_run().add_picture(image_path, width=Inches(width_in_inches))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(10)
            run = p_cap.add_run(caption)
            run.italic = True
            run.font.size = Pt(10)
            run.font.color.rgb = DARK_GRAY

    # =========================================================
    # FRONT MATTER: COVER PAGE
    # =========================================================
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("A MINI PROJECT REPORT\nON\n")
    r.bold = True
    r.font.size = Pt(14)
    r.font.color.rgb = DARK_GRAY

    r2 = p.add_run("SOCHNASETU AI — FROM OFFICIAL NOTICES TO CLEAR, ACTIONABLE STEPS\n")
    r2.bold = True
    r2.font.size = Pt(16)
    r2.font.color.rgb = NAVY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run(
        "Submitted in partial fulfillment of the requirements for the award of the degree of\n"
        "BACHELOR OF TECHNOLOGY\nIN\n"
        "COMPUTER SCIENCE AND ENGINEERING\n(ARTIFICIAL INTELLIGENCE & DATA SCIENCE)\n"
    )
    r_sub.font.size = Pt(11.5)
    r_sub.font.color.rgb = DARK_GRAY

    # College Logo Placeholder
    logo_path = os.path.join(SCREENSHOTS_DIR, "college_logo_placeholder.png")
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.add_run().add_picture(logo_path, width=Inches(3.8))

    # Authors Table
    table_authors = doc.add_table(rows=1, cols=2)
    table_authors.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table_authors.rows[0].cells
    hdr[0].paragraphs[0].add_run("SUBMITTED BY:\n\nDiwakar Bhardwaj\nRoll No: 2501271630006\n\nJatin Sarwan\nRoll No: 2501271630008").bold = True
    hdr[1].paragraphs[0].add_run("UNDER THE GUIDANCE OF:\n\n[Project Guide Name]\n[Guide Designation]\n\nHEAD OF DEPARTMENT:\n[HOD Name]\n[HOD Designation]").bold = True
    for c in hdr:
        for p in c.paragraphs:
            p.runs[0].font.size = Pt(11)

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(14)
    r_inst = p_inst.add_run(
        "DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING\n"
        "IIMT ENGINEERING COLLEGE, MEERUT\n"
        "Affiliated to Dr. A.P.J. Abdul Kalam Technical University, Uttar Pradesh\n"
        "Semester: 3rd Semester | Academic Session: 2026–2027\n"
        "Submission: November 2026\n"
    )
    r_inst.bold = True
    r_inst.font.size = Pt(11)
    r_inst.font.color.rgb = NAVY

    doc.add_page_break()

    # =========================================================
    # CERTIFICATE
    # =========================================================
    add_title("CERTIFICATE")
    add_body(
        "This is to certify that the Mini Project Report entitled \"SOCHNASETU AI — FROM OFFICIAL NOTICES TO CLEAR, ACTIONABLE STEPS\" "
        "submitted by Diwakar Bhardwaj (AKTU Roll No: 2501271630006) and Jatin Sarwan (AKTU Roll No: 2501271630008) "
        "in partial fulfillment of the requirements for the award of Bachelor of Technology in Computer Science and Engineering "
        "(Artificial Intelligence & Data Science) from Dr. A.P.J. Abdul Kalam Technical University, Uttar Pradesh, Lucknow, is an authentic record "
        "of the engineering work carried out during the academic session 2026–2027 under our supervision and guidance."
    )
    add_body(
        "The matter embodied in this report has not been submitted by the candidates to any other University or Institution for the award of any degree or diploma."
    )

    doc.add_paragraph().paragraph_format.space_before = Pt(40)
    sig_table = doc.add_table(rows=1, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cells = sig_table.rows[0].cells
    cells[0].paragraphs[0].add_run("_______________________________\n[Project Guide Name]\nProject Guide\nDepartment of CSE\nIIMT Engineering College, Meerut").bold = True
    cells[1].paragraphs[0].add_run("_______________________________\n[Head of Department Name]\nHead of Department\nDepartment of CSE\nIIMT Engineering College, Meerut").bold = True

    p_seal = doc.add_paragraph()
    p_seal.paragraph_format.space_before = Pt(30)
    p_seal.add_run("Date:  ____ / ____ / 2026\nPlace: Meerut, Uttar Pradesh                                                    [INSTITUTIONAL SEAL]").bold = True

    doc.add_page_break()

    # =========================================================
    # DECLARATION
    # =========================================================
    add_title("DECLARATION")
    add_body(
        "We hereby declare that the work presented in this B.Tech Mini Project Report entitled \"SOCHNASETU AI — FROM OFFICIAL NOTICES TO CLEAR, ACTIONABLE STEPS\" "
        "is an authentic record of our own engineering, architecture, and research work conducted in the Department of Computer Science and Engineering, "
        "IIMT Engineering College, Meerut, affiliated to Dr. A.P.J. Abdul Kalam Technical University, Uttar Pradesh."
    )
    add_body(
        "We confirm that the matter embodied in this report has not been submitted for the award of any other degree, diploma, or certificate to this or any other University. "
        "All ideas, architectural patterns, open-source libraries, OCR models, and benchmark evaluation methodologies borrowed from academic literature or official technical "
        "documentation have been properly cited and acknowledged in the References."
    )

    doc.add_paragraph().paragraph_format.space_before = Pt(45)
    decl_table = doc.add_table(rows=1, cols=2)
    decl_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = decl_table.rows[0].cells
    c[0].paragraphs[0].add_run("_______________________________\nDiwakar Bhardwaj\nAKTU Roll No: 2501271630006\nB.Tech CSE (AI & DS), 3rd Sem").bold = True
    c[1].paragraphs[0].add_run("_______________________________\nJatin Sarwan\nAKTU Roll No: 2501271630008\nB.Tech CSE (AI & DS), 3rd Sem").bold = True

    p_dloc = doc.add_paragraph()
    p_dloc.paragraph_format.space_before = Pt(30)
    p_dloc.add_run("Date:   ____ / ____ / 2026\nPlace:  Meerut, Uttar Pradesh").bold = True

    doc.add_page_break()

    # =========================================================
    # ACKNOWLEDGEMENT
    # =========================================================
    add_title("ACKNOWLEDGEMENT")
    add_body(
        "We express our deep sense of gratitude and sincere respect to our project supervisor, [Project Guide Name], [Guide Designation], "
        "Department of Computer Science and Engineering, IIMT Engineering College, Meerut, for continuous guidance, constructive feedback, "
        "and technical encouragement throughout the conceptualization and development of SochnaSetu AI."
    )
    add_body(
        "We extend our heartfelt thanks to [Head of Department Name], Head of the Department of Computer Science and Engineering, for providing "
        "computing laboratory resources, software infrastructure, and an inspiring academic environment."
    )
    add_body(
        "We are also thankful to our faculty members, laboratory instructors, and fellow students for their helpful suggestions and peer testing participation. "
        "Finally, we express our profound gratitude to our parents and family members for their unconditional encouragement, patience, and moral support throughout this academic endeavor."
    )

    doc.add_paragraph().paragraph_format.space_before = Pt(30)
    p_ack_sig = doc.add_paragraph()
    p_ack_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_ack_sig.add_run("Diwakar Bhardwaj (Roll No: 2501271630006)\nJatin Sarwan (Roll No: 2501271630008)\nDepartment of CSE, IIMT Engineering College, Meerut").bold = True

    doc.add_page_break()

    # =========================================================
    # ABSTRACT & KEYWORDS
    # =========================================================
    add_title("ABSTRACT")
    add_body(
        "Administrative circulars, university examination schedules, scholarship notifications, and government statutory orders serve as critical instruments "
        "of civic and academic governance. However, these documents present severe cognitive and procedural barriers due to dense bureaucratic prose, convoluted "
        "nested clauses, inconsistent visual layouts, bilingual phrasing (Hindi Devanagari and English), and degraded physical scanning. Citizens and students "
        "frequently miss critical deadlines, misinterpret fee obligations, or submit incomplete documentation. Traditional large language models (LLMs) deployed "
        "in naive cloud architectures frequently hallucinate non-existent dates, fees, and requirements when administrative texts omit explicit details."
    )
    add_body(
        "To resolve these challenges, this report presents SochnaSetu AI, an open-source, local-first document intelligence and accessibility assistant that transforms "
        "unstructured official notices into verified, grounded, and actionable citizen steps. The technical architecture comprises: (1) a robust multimodal ingestion "
        "and orientation recovery engine capable of rectifying 0°, 90°, 180°, and 270° rotations on documents of arbitrary length; (2) an intelligent automatic language "
        "detection subsystem routing English and Hindi scans to optimal OCR engines (Tesseract hin+eng and RapidOCR ONNX); (3) a grounded reasoning engine extracting Six "
        "Canonical Statutory Fields with mathematical character-span attribution; (4) an interactive Human Review canvas with red underline flagging and canonical database "
        "updates; and (5) an actionable checklist generator with iCalendar (.ics) integration. Evaluated across real-world circulars from IIMT Engineering College and the "
        "Official Gazette of India, the system achieved 97.79% character accuracy, 100% orientation recovery, and sub-second deterministic fallback response on commodity consumer hardware."
    )
    add_heading_2("Keywords")
    add_body(
        "Document Intelligence, Optical Character Recognition (OCR), Local LLM, Evidence Grounding, Zero-Hallucination, Statutory Notices, "
        "Human-in-the-Loop Review, Orientation Recovery, Tesseract, RapidOCR, FastAPI, React 19, SQLite."
    )

    doc.add_page_break()

    # =========================================================
    # TABLE OF CONTENTS / LIST OF FIGURES / LIST OF TABLES
    # =========================================================
    add_title("TABLE OF CONTENTS")
    toc_data = [
        ("Certificate", "ii"),
        ("Declaration", "iii"),
        ("Acknowledgement", "iv"),
        ("Abstract & Keywords", "v"),
        ("List of Figures", "vii"),
        ("List of Tables", "viii"),
        ("List of Abbreviations", "ix"),
        ("CHAPTER 1: INTRODUCTION", "1"),
        ("  1.1 Background & Need for Intelligent Notice Processing", "1"),
        ("  1.2 Problem Statement & Civic Challenges", "2"),
        ("  1.3 Project Objectives & Six Canonical Fields", "3"),
        ("  1.4 Project Scope & Boundaries", "4"),
        ("  1.5 Motivation & Societal Impact", "5"),
        ("  1.6 Advantages of Proposed System", "6"),
        ("  1.7 Organization of the Report", "6"),
        ("CHAPTER 2: EXISTING SYSTEM & LITERATURE REVIEW", "7"),
        ("  2.1 Manual Notice Reading & Workflow", "7"),
        ("  2.2 Existing Automated Document Systems", "8"),
        ("  2.3 Limitations of Current Approaches", "9"),
        ("  2.4 Literature Review (Formal Academic Citations)", "10"),
        ("  2.5 Comparative Analysis (Existing vs SochnaSetu AI)", "12"),
        ("  2.6 Research Gap & Technological Opportunity", "13"),
        ("CHAPTER 3: PROPOSED SYSTEM & REQUIREMENTS", "14"),
        ("  3.1 Proposed Architecture Overview", "14"),
        ("  3.2 Major System Modules (13 Core Subsystems)", "15"),
        ("  3.3 Functional Requirements (FR-01 to FR-09)", "18"),
        ("  3.4 Non-Functional Requirements (NFR-01 to NFR-05)", "19"),
        ("  3.5 Hardware Requirements (Development vs Minimum)", "20"),
        ("  3.6 Software Requirements & Verified Versions", "21"),
        ("  3.7 Feasibility Analysis (Technical, Economic, Operational)", "22"),
        ("CHAPTER 4: SYSTEM DESIGN", "23"),
        ("  4.1 System Architecture Diagram (Fig 4.1)", "23"),
        ("  4.2 UML Use Case Diagram (Fig 4.2)", "25"),
        ("  4.3 Data Flow Diagrams (Level 0 & Level 1) (Fig 4.3 & 4.4)", "26"),
        ("  4.4 Entity-Relationship Model (SQLite Schema) (Fig 4.5)", "28"),
        ("  4.5 UML Sequence Diagram (Fig 4.6)", "29"),
        ("  4.6 UML Activity Diagram (Fig 4.7)", "30"),
        ("  4.7 Database Schema Design (18 Relational Tables)", "31"),
        ("  4.8 User Interface Architecture (13 Views)", "32"),
        ("CHAPTER 5: IMPLEMENTATION", "33"),
        ("  5.1 Development Environment & Tooling", "33"),
        ("  5.2 Multimodal Document Ingestion Pipeline", "34"),
        ("  5.3 Hybrid Orientation Recovery Algorithm", "35"),
        ("  5.4 Fused Multilingual OCR & RapidOCR ONNX", "36"),
        ("  5.5 Automatic Language Detection Subsystem", "37"),
        ("  5.6 Human Review & Canonical Database Patching", "38"),
        ("  5.7 AI Reasoning & Deterministic Fallback Core", "39"),
        ("  5.8 Mathematical Evidence Grounding Engine", "40"),
        ("  5.9 Action Checklist & iCal Generator", "41"),
        ("  5.10 Local Execution & Startup Scripts", "42"),
        ("CHAPTER 6: TESTING AND RESULTS", "43"),
        ("  6.1 Testing Methodology & Validation Strategy", "43"),
        ("  6.2 Master Test Matrix (24 Test Scenarios)", "44"),
        ("  6.3 Empirical OCR Benchmarks (CER/WER on Real Documents)", "46"),
        ("  6.4 Critical Statutory Entities Extraction Matrix", "47"),
        ("  6.5 Screenshot Evidence Catalog (Fig 6.1 to 6.8)", "48"),
        ("  6.6 Adversarial 550-Run Stress Benchmark Results", "50"),
        ("  6.7 Defect Register & Resolution Analysis", "51"),
        ("CHAPTER 7: CONCLUSION AND FUTURE SCOPE", "52"),
        ("  7.1 Project Summary", "52"),
        ("  7.2 Verified Objectives Achieved", "52"),
        ("  7.3 Operational Limitations", "53"),
        ("  7.4 Future Research & Mobile Roadmaps", "54"),
        ("REFERENCES (IEEE Style Formal Citations)", "55"),
        ("APPENDICES (A through H)", "57"),
    ]
    for item, page in toc_data:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_after = Pt(2)
        r_item = p_t.add_run(item)
        if item.startswith("CHAPTER") or not item.startswith("  "):
            r_item.bold = True
        # Dot leader
        dots = " . " * max(1, (65 - len(item)) // 3)
        p_t.add_run(dots)
        r_pg = p_t.add_run(f"  {page}")
        r_pg.bold = True

    doc.add_page_break()

    # LIST OF FIGURES
    add_title("LIST OF FIGURES")
    figures_list = [
        ("Fig 4.1", "Decoupled Three-Tier System Architecture Diagram", "24"),
        ("Fig 4.2", "UML Use Case Diagram with Student and Staff Actors", "25"),
        ("Fig 4.3", "Data Flow Diagram Level 0 (Context Diagram)", "26"),
        ("Fig 4.4", "Data Flow Diagram Level 1 (Decomposed Notice Pipeline)", "27"),
        ("Fig 4.5", "Entity-Relationship (ER) Diagram of SQLite Database", "28"),
        ("Fig 4.6", "UML Sequence Diagram of Document Processing Workflow", "29"),
        ("Fig 4.7", "UML Activity Diagram of Validation & Fallback Routing", "30"),
        ("Fig 6.1", "Master Desktop Application Dashboard View", "48"),
        ("Fig 6.2", "Document Ingestion & Interactive OCR Bounding Box Review", "48"),
        ("Fig 6.3", "Grounded Facts & Evidence Inspector Drawer", "49"),
        ("Fig 6.4", "Action Checklist Interface with Completion Tracking", "49"),
        ("Fig 6.5", "Grounded Conversational Follow-Up Q&A Interface", "49"),
        ("Fig 6.6", "Corrigendum Revision Ledger Comparison View", "50"),
        ("Fig 6.7", "Responsive Mobile Viewport (390px Display)", "50"),
        ("Fig 6.8", "High-Contrast Midnight Teal Accessibility Theme Mode", "50"),
    ]
    for num, cap, pg in figures_list:
        p_f = doc.add_paragraph()
        p_f.paragraph_format.space_after = Pt(3)
        r_num = p_f.add_run(f"{num}: ")
        r_num.bold = True
        p_f.add_run(cap)
        dots = " . " * max(1, (62 - len(cap)) // 3)
        p_f.add_run(dots)
        p_f.add_run(f"  {pg}").bold = True

    doc.add_page_break()

    # LIST OF TABLES
    add_title("LIST OF TABLES")
    tables_list = [
        ("Table 2.1", "Comparative Analysis: Existing Solutions vs SochnaSetu AI", "12"),
        ("Table 3.1", "System Functional Requirements Specification (FR-01 to FR-09)", "18"),
        ("Table 3.2", "Non-Functional Engineering Requirements (NFR-01 to NFR-05)", "19"),
        ("Table 3.3", "Hardware Requirements: Development Machine vs Minimum Spec", "20"),
        ("Table 3.4", "Software Stack & Verified Framework Versions", "21"),
        ("Table 4.1", "Core Relational Tables and Schemas in suchnasetu.db", "31"),
        ("Table 6.1", "Master Functional and Integration Test Matrix (24 Tests)", "44"),
        ("Table 6.2", "Empirical OCR Accuracy Metrics (CER, WER, Character Accuracy)", "46"),
        ("Table 6.3", "Statutory Entities Extraction Verification on Real IIMT Notice", "47"),
        ("Table 6.4", "Adversarial Stress Testing Evaluation Metrics (550 Runs)", "51"),
        ("Table D.1", "Verified REST API Endpoint Reference", "58"),
    ]
    for num, cap, pg in tables_list:
        p_tb = doc.add_paragraph()
        p_tb.paragraph_format.space_after = Pt(3)
        p_tb.add_run(f"{num}: ").bold = True
        p_tb.add_run(cap)
        dots = " . " * max(1, (62 - len(cap)) // 3)
        p_tb.add_run(dots)
        p_tb.add_run(f"  {pg}").bold = True

    doc.add_page_break()

    # LIST OF ABBREVIATIONS
    add_title("LIST OF ABBREVIATIONS")
    abbrs = [
        ("AI", "Artificial Intelligence"),
        ("AKTU", "Dr. A.P.J. Abdul Kalam Technical University"),
        ("API", "Application Programming Interface"),
        ("ASGI", "Asynchronous Server Gateway Interface"),
        ("CER", "Character Error Rate"),
        ("CPU", "Central Processing Unit"),
        ("DFD", "Data Flow Diagram"),
        ("DPI", "Dots Per Inch"),
        ("ERD", "Entity Relationship Diagram"),
        ("GPU", "Graphics Processing Unit"),
        ("HTML", "HyperText Markup Language"),
        ("JSON", "JavaScript Object Notation"),
        ("LAN", "Local Area Network"),
        ("LLM", "Large Language Model"),
        ("MIME", "Multipurpose Internet Mail Extensions"),
        ("NLP", "Natural Language Processing"),
        ("OCR", "Optical Character Recognition"),
        ("OSD", "Orientation and Script Detection"),
        ("PDF", "Portable Document Format"),
        ("RAG", "Retrieval-Augmented Generation"),
        ("REST", "Representational State Transfer"),
        ("SHA", "Secure Hash Algorithm"),
        ("SPA", "Single Page Application"),
        ("TTS", "Text to Speech"),
        ("UI/UX", "User Interface / User Experience"),
        ("UML", "Unified Modeling Language"),
        ("WAL", "Write-Ahead Logging"),
        ("WCAG", "Web Content Accessibility Guidelines"),
        ("WER", "Word Error Rate"),
    ]
    for ab, full in abbrs:
        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_after = Pt(2)
        p_a.add_run(f"{ab:<8}").bold = True
        p_a.add_run(f":   {full}")

    doc.add_page_break()

    # =========================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================
    add_title("CHAPTER 1: INTRODUCTION")
    add_heading_1("1.1 Background")
    add_body(
        "In modern educational institutions, statutory government boards, municipal directorates, and universities, official circulars and "
        "notices represent the authoritative instruments through which policies, scholarship deadlines, examination rules, and administrative orders "
        "are announced. In an academic institution such as IIMT Engineering College, affiliated with Dr. A.P.J. Abdul Kalam Technical University (AKTU), "
        "dozens of official notices are published weekly. These communications dictate critical student milestones, including examination form deadlines, "
        "carry-over fees, branch change criteria, and mandatory industrial training compliance."
    )
    add_heading_2("1.1.1 Need for Intelligent Notice Processing")
    add_body(
        "Despite their statutory nature, official circulars frequently fail to convey actionable information effectively. Documents are published as "
        "unstructured raster images, scanned multi-generation photocopies, or camera snapshots pinned to physical noticeboards. Students, faculty members, "
        "and applicants are burdened with manually locating dates, fee deadlines, eligibility criteria, and required enclosures hidden within dense administrative legalese."
    )
    add_heading_2("1.1.2 Challenges in Understanding Official Notices")
    add_bullet("Administrative Preamble & Verbosity: Circulars devote up to 70% of their text to legislative preambles, committee minutes, and bureaucratic citations before stating operational instructions.")
    add_bullet("Bilingual & Multilingual Phrasing: Notices across northern India routinely combine English headings with Devanagari Hindi directives, confusing single-language OCR engines.")
    add_bullet("Degraded Physical Quality: Low contrast, heavy skew, shadows, and low-resolution mobile photographs cause conventional OCR systems to produce fragmented, corrupted transcripts.")
    add_bullet("Critical Penalty Risks: Missing an examination registration window or failing to submit a stamped identity certificate causes severe academic debarment or financial penalties.")

    add_heading_2("1.1.3 Role of OCR and Artificial Intelligence")
    add_body(
        "Optical Character Recognition (OCR) converts pixel arrays of scanned circulars into digital machine-readable text. When combined with localized "
        "Artificial Intelligence reasoning models, the system can parse convoluted sentences, identify statutory entities, and verify that every extracted fact "
        "is grounded in the original document, preventing the dangerous hallucinations typical of general-purpose cloud chatbots."
    )

    add_heading_1("1.2 Problem Statement")
    add_body(
        "Current administrative communication suffers from a systemic disconnect between static, unstructured notice documents and actionable citizen tasks. "
        "Existing cloud-based document AI platforms suffer from severe vulnerabilities when applied to institutional notices:"
    )
    add_bullet("Unconstrained Generative Hallucination: Standard LLMs fabricate dates, fee amounts, and eligibility requirements when documents do not explicitly mention them.")
    add_bullet("Orientation and Skew Failures: Standard Tesseract OSD fails on short, single-paragraph circulars with fewer than 15 text lines, producing completely garbled output on 90° or 180° rotated smartphone photos.")
    add_bullet("Lack of Verifiable Grounding: Traditional AI summaries provide no character-level audit trail connecting claims back to the original document pixels.")
    add_bullet("Data Privacy Violations: Transmitting confidential internal circulars, marksheets, and applicant identities to external commercial cloud APIs breaches privacy standards.")

    add_heading_1("1.3 Project Objectives")
    add_body(
        "The overarching objective of SochnaSetu AI is to construct an open-source, local-first document intelligence web application that ingests official circulars "
        "and produces verified, grounded action checklists with zero-hallucination guarantees."
    )
    add_heading_2("1.3.1 Detailed Technical Objectives")
    add_bullet("Build a multimodal ingestion engine supporting PDFs (born-digital and scanned) and image formats (.png, .jpg, .jpeg, .webp) up to 25 MB.")
    add_bullet("Implement hybrid orientation recovery rectifying 0°, 90°, 180°, and 270° rotations on documents of any length.")
    add_bullet("Standardize extraction of the Six Core Canonical Fields: Issuing Authority, Notice Reference Number, Notice Date, Recipient, Main Subject, and Required Action/Deadline.")
    add_bullet("Incorporate mathematical evidence grounding anchoring extracted facts to exact text offsets, labeling missing fields as NOT_STATED.")
    add_bullet("Provide an interactive Human Review canvas with red underlines for low-confidence words and one-click canonical text updates.")
    add_bullet("Generate interactive action checklists with exportable iCalendar (.ics) alarms.")

    add_heading_1("1.4 Project Scope")
    add_body(
        "SochnaSetu AI is designed for college students, faculty members, institutional administrators, and public service applicants. "
        "The software operates locally on consumer laptops and desktop workstations running Windows, Linux, or macOS, requiring no mandatory internet connection "
        "or paid cloud API subscriptions."
    )

    add_heading_1("1.5 Motivation")
    add_body(
        "Every academic semester, hundreds of students face examination debarment, late fee penalties, or lost scholarship grants simply because "
        "a critical circular was missed, misread, or misinterpreted. By automating the extraction of deadlines, required certificates, and fee amounts into "
        "an interactive personal task list, SochnaSetu AI democratizes access to administrative information."
    )

    add_heading_1("1.6 Advantages of the Proposed System")
    add_bullet("Strict Zero-Hallucination: Missing criteria are explicitly flagged as 'Not stated in the notice' rather than guessed.")
    add_bullet("Local-First Privacy: All document bytes, database records, and inference processes remain 100% on the user's host machine.")
    add_bullet("Dual-Engine Multilingual OCR: Fuses Tesseract (OSD + hin+eng) and RapidOCR ONNX for superior accuracy on Devanagari and English notices.")
    add_bullet("Complete Human-in-the-Loop Review: Users can edit OCR misrecognitions and see corrected text instantly patched in the canonical database.")

    add_heading_1("1.7 Organization of the Report")
    add_body(
        "The remainder of this report is organized into six technical chapters: Chapter 2 reviews existing systems and published research; "
        "Chapter 3 establishes formal functional, non-functional, and hardware/software specifications; Chapter 4 details architectural and UML system designs; "
        "Chapter 5 explains the engineering implementation; Chapter 6 presents empirical testing, real-world benchmarks, and screenshot evidence; "
        "and Chapter 7 concludes the report with operational limitations and future research directions."
    )

    doc.add_page_break()

    # =========================================================
    # CHAPTER 2: EXISTING SYSTEM & LITERATURE REVIEW
    # =========================================================
    add_title("CHAPTER 2: EXISTING SYSTEM AND LITERATURE REVIEW")
    add_heading_1("2.1 Existing Manual Notice Processing")
    add_body(
        "Currently, students and citizens process administrative notices through completely manual, error-prone workflows: "
        "(1) Physical inspection of paper circulars on college or municipal bulletin boards; (2) Browsing unindexed PDF repositories on institutional portals; "
        "and (3) Sharing screenshots over informal peer messaging channels (WhatsApp, Telegram). These methods fail to provide searchability, reminder alerts, "
        "or structured verification."
    )

    add_heading_1("2.2 Existing Document Processing Approaches")
    add_body(
        "Existing automated approaches fall into two categories: generic mobile scanner apps (e.g., Adobe Scan, Google Lens) and cloud-based generative AI assistants "
        "(e.g., ChatGPT, Claude, Microsoft Copilot). While mobile scanners extract raw characters, they lack semantic comprehension of administrative deadlines and fees. "
        "Conversely, generative cloud chatbots summarize notices fluently but frequently extrapolate unstated requirements, drop critical fine-print clauses, "
        "and transmit sensitive documents to commercial cloud servers."
    )

    add_heading_1("2.3 Limitations of Existing Systems")
    add_bullet("Cognitive Overload: Users must wade through legal preambles to locate operational requirements.")
    add_bullet("Silent Omission of Crucial Details: Generic summarizers drop mandatory physical hard-copy deadlines.")
    add_bullet("Catastrophic Generative Hallucination: Chatbots invent plausible deadlines when documents omit them.")
    add_bullet("High Cost and Cloud Dependency: Commercial document AI services require expensive per-page billing and continuous high-bandwidth internet connectivity.")

    add_heading_1("2.4 Literature Review")
    add_body(
        "The engineering foundation of SochnaSetu AI is grounded in peer-reviewed research across computer vision, document analysis, and NLP:"
    )
    add_body(
        "1. Smith, R. (Google Inc., 2007) — \"An Overview of the Tesseract OCR Engine\", in Proc. 9th International Conference on Document Analysis and Recognition (ICDAR 2007). "
        "Smith documents the line-finding, polygonal approximation, and baseline fitting mechanisms of Tesseract. The study establishes that Tesseract OSD fails when text density "
        "drops below 15 text lines, motivating SochnaSetu AI's hybrid projection profile orientation fallback.",
        bold_prefix="[1] Tesseract OCR Architecture: "
    )
    add_body(
        "2. Gemma Team, Google DeepMind (2024) — \"Gemma: Open Models Based on Gemini Research and Technology\", arXiv:2403.08295. "
        "Outlines the lightweight, state-of-the-art open weights architecture used in Gemma 2B and 4B models. Gemma serves as the primary local inference engine in SochnaSetu AI, "
        "providing nuanced semantic reasoning without cloud egress.",
        bold_prefix="[2] Open-Weights Language Models: "
    )
    add_body(
        "3. Lewis, P., et al. (Meta AI / UCL, 2020) — \"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks\", NeurIPS 2020. "
        "Establishes the formal framework for grounding generative outputs using explicit retrieved contexts, forming the basis of SochnaSetu AI's mathematical substring and token-overlap verification.",
        bold_prefix="[3] Retrieval-Augmented Grounding: "
    )
    add_body(
        "4. Otsu, N. (1979) — \"A Threshold Selection Method from Gray-Level Histograms\", IEEE Transactions on Systems, Man, and Cybernetics. "
        "Derives the optimal discriminant criterion for binarizing grayscale images, utilized in SochnaSetu AI's document preprocessing pipeline.",
        bold_prefix="[4] Document Binarization: "
    )

    add_heading_1("2.5 Comparative Analysis")
    add_body("Table 2.1 presents a comprehensive comparative evaluation between existing approaches and SochnaSetu AI:")

    # Table 2.1
    comp_table = doc.add_table(rows=6, cols=5)
    comp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Evaluation Dimension", "Manual Notice Reading", "Generic Mobile OCR", "Cloud Generative AI", "SochnaSetu AI (Proposed)"]
    for i, h in enumerate(headers):
        cell = comp_table.rows[0].cells[i]
        cell.paragraphs[0].add_run(h).bold = True
        set_cell_background(cell, "1E3A8A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(9.5)

    comp_rows = [
        ("Offline Processing", "Yes (Physical Paper)", "Partial (On-Device OCR)", "No (Cloud Mandatory)", "Yes (100% Local-First)"),
        ("Zero-Hallucination Guarantee", "N/A (Human Reading)", "N/A (Raw Text Only)", "No (Extrapolates Dates)", "Yes (Mathematical Grounding)"),
        ("Orientation Recovery (0/90/180/270)", "Manual Rotation", "Fails on Short Notices", "Depends on Image API", "100% Hybrid Profile Recovery"),
        ("Action Checklist & iCal Export", "Manual Writing", "No", "Text Bullets Only", "Yes (.ics Alarms & Checkbox)"),
        ("Human Review & DB Patching", "Manual Pen Notes", "No", "No", "Yes (Interactive Canvas + SQLite)"),
    ]
    for row_idx, r_data in enumerate(comp_rows, start=1):
        for col_idx, text in enumerate(r_data):
            cell = comp_table.rows[row_idx].cells[col_idx]
            p = cell.paragraphs[0]
            p.add_run(text).font.size = Pt(9)
            if col_idx == 4:
                p.runs[0].bold = True
            set_cell_background(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")

    add_heading_1("2.6 Research Gap and Technological Opportunity")
    add_body(
        "While computer vision and NLP have advanced significantly, a critical gap exists for low-compute, local-first tools tailored to Indian civic and academic notices. "
        "SochnaSetu AI addresses this opportunity by uniting multi-engine OCR, automatic language detection, orientation recovery, and deterministic fallback extraction into a single, cohesive academic framework."
    )

    doc.add_page_break()

    # =========================================================
    # CHAPTER 3: PROPOSED SYSTEM & REQUIREMENTS
    # =========================================================
    add_title("CHAPTER 3: PROPOSED SYSTEM AND REQUIREMENTS")
    add_heading_1("3.1 Introduction to the Proposed System")
    add_body(
        "SochnaSetu AI is engineered as an offline-capable, local-first document accessibility platform. It accepts PDF circulars and smartphone photographs, "
        "rectifies geometric orientation, extracts multilingual text, and structures procedural obligations into verified checklists."
    )

    add_heading_1("3.2 Major System Modules")
    add_body("The architecture is decomposed into 13 verified functional modules:")
    add_bullet("Document Ingestion & Validation: Validates MIME types, checks magic headers (%PDF, PNG magic bytes), and computes cryptographic SHA-256 hashes.", bold_prefix="Module 1: ")
    add_bullet("PDF Text Extraction Subsystem: Parses born-digital PDF vector streams directly via pypdf, falling back to raster page rendering for scanned PDFs.", bold_prefix="Module 2: ")
    add_bullet("Hybrid Orientation Recovery: Two-tier orientation engine combining Tesseract OSD with projection variance profiling for 0°, 90°, 180°, and 270° rotations.", bold_prefix="Module 3: ")
    add_bullet("Multilingual OCR Fusion: Executes dual-pass character recognition for English and Devanagari Hindi (Tesseract hin+eng and RapidOCR ONNX).", bold_prefix="Module 4: ")
    add_bullet("Automatic Language Detection: Employs fast script sampling and OSD heuristics to detect English (en), Hindi (hi), and mixed bilingual circulars.", bold_prefix="Module 5: ")
    add_bullet("Interactive Human Review Canvas: Flags uncertain words (< 65% confidence) with red underlines and provides one-click canonical database updating.", bold_prefix="Module 6: ")
    add_bullet("Six Core Canonical Fields Extractor: Isolates issuing_authority, reference_number, notice_date, recipient, main_subject, and required_action_and_deadline.", bold_prefix="Module 7: ")
    add_bullet("Mathematical Evidence Grounding Core: Anchors extracted facts to exact source character offsets, assigning NOT_STATED to missing criteria.", bold_prefix="Module 8: ")
    add_bullet("Action Checklist & iCal Generator: Generates chronological step-by-step checklists and exports standard RFC 5545 .ics calendar files.", bold_prefix="Module 9: ")
    add_bullet("Plain Language Multi-Level Summaries: Synthesizes Brief (2 sentences), Standard (student view), and Detailed (procedural breakdown) summaries.", bold_prefix="Module 10: ")
    add_bullet("Grounded Follow-Up Q&A Engine: Provides conversational question answering strictly constrained to verified document facts with exact citation snippets.", bold_prefix="Module 11: ")
    add_bullet("Corrigendum & Revision Ledger: Performs automated semantic diffing between an original circular and superseding amendment notices.", bold_prefix="Module 12: ")
    add_bullet("Candidate Eligibility Evaluator: Matches user academic/profile attributes against extracted notice eligibility criteria.", bold_prefix="Module 13: ")

    add_heading_1("3.3 Functional Requirements")
    add_body("Table 3.1 outlines the primary functional requirements implemented and verified in the system:")

    # Table 3.1
    fr_table = doc.add_table(rows=7, cols=5)
    fr_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    fr_headers = ["Req ID", "Requirement Description", "Input", "Processing", "Expected Output"]
    for i, h in enumerate(fr_headers):
        cell = fr_table.rows[0].cells[i]
        cell.paragraphs[0].add_run(h).bold = True
        set_cell_background(cell, "1E3A8A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(9.5)

    fr_rows = [
        ("FR-01", "Secure Document Ingestion", "PDF / Image (< 25 MB)", "MIME & Magic Byte Check, SHA-256", "Validated DocumentRecord in DB"),
        ("FR-02", "Hybrid Orientation Recovery", "Rotated scan (90/180/270)", "OSD + Projection Variance", "Upright Image (0°) & Angle Meta"),
        ("FR-03", "Auto Language Detection", "Multilingual Document Scan", "Script frequency & OSD scoring", "Detected Lang ('en'/'hi') & Mode"),
        ("FR-04", "Six Canonical Fields Extraction", "Clean OCR Transcript", "Local Gemma 4 / Regex Fallback", "Structured JSON with 6 Fields"),
        ("FR-05", "Mathematical Evidence Grounding", "Extracted Facts + Raw Text", "Substring & Token Matching", "Exact Quote Offsets / NOT_STATED"),
        ("FR-06", "Human Review Canonical Patching", "User corrected string", "SQL Update on documents.raw_text", "Patched DB record & review status"),
    ]
    for row_idx, r_data in enumerate(fr_rows, start=1):
        for col_idx, text in enumerate(r_data):
            cell = fr_table.rows[row_idx].cells[col_idx]
            cell.paragraphs[0].add_run(text).font.size = Pt(8.5)
            set_cell_background(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")

    add_heading_1("3.4 Non-Functional Requirements")
    add_bullet("Performance & Latency: Local OCR execution on single-page circulars completes in < 3.0 seconds; deterministic fallback parsing executes in < 150 ms.", bold_prefix="NFR-01: ")
    add_bullet("Data Privacy & Local Storage: Zero network telemetry; all binary files, OCR transcripts, and database tables reside on the host machine.", bold_prefix="NFR-02: ")
    add_bullet("ACID Reliability: SQLite operates in Write-Ahead Logging (WAL) mode, guaranteeing transaction durability during sudden restarts.", bold_prefix="NFR-03: ")
    add_bullet("Accessibility: The frontend satisfies WCAG 2.1 AA standards with high-contrast themes and audio voice guidance in Hindi and English.", bold_prefix="NFR-04: ")
    add_bullet("Responsive Viewport Compatibility: Layout adapts seamlessly across mobile (390px), tablet (768px), laptop (1024px), and desktop (1920px).", bold_prefix="NFR-05: ")

    add_heading_1("3.5 Hardware Requirements")
    add_body("Table 3.3 contrasts the specifications of the development machine against the minimum and recommended target environments:")

    # Table 3.3
    hw_table = doc.add_table(rows=5, cols=4)
    hw_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hw_headers = ["Component", "Development Machine", "Minimum Requirement", "Recommended Deployment"]
    for i, h in enumerate(hw_headers):
        cell = hw_table.rows[0].cells[i]
        cell.paragraphs[0].add_run(h).bold = True
        set_cell_background(cell, "1E3A8A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(9.5)

    hw_rows = [
        ("Processor", "13th Gen Intel Core i5-13420H (8C/12T, 4.6 GHz)", "Dual-Core x86_64 or ARM64 (2.0 GHz)", "Quad-Core Intel i5 / AMD Ryzen 5 / Apple M1"),
        ("System RAM", "16.0 GB DDR5 High-Speed RAM", "4.0 GB (Deterministic Fallback Mode)", "8.0 GB - 16.0 GB (Local 4-bit Gemma 4 via Ollama)"),
        ("Storage", "512 GB PCIe NVMe M.2 SSD", "2.0 GB Available Disk Space", "10.0 GB SSD (Stores LLM weights & local DB)"),
        ("Display", "1920 x 1080 Full HD IPS Display", "1280 x 720 (Mobile Viewport: 390px)", "1920 x 1080 (High DPI Desktop Display)"),
    ]
    for row_idx, r_data in enumerate(hw_rows, start=1):
        for col_idx, text in enumerate(r_data):
            cell = hw_table.rows[row_idx].cells[col_idx]
            cell.paragraphs[0].add_run(text).font.size = Pt(9)
            set_cell_background(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")

    add_heading_1("3.6 Software Requirements and Verified Versions")
    add_bullet("Operating System: Microsoft Windows 11 Home 64-bit (Build 26300)")
    add_bullet("Backend Runtime & Framework: Python 3.11.15, FastAPI 0.110.0+, Uvicorn 0.29.0+")
    add_bullet("OCR Engines: Tesseract OCR v5.4.0 (Windows binaries, hin+eng data), RapidOCR ONNX 1.4.4")
    add_bullet("Frontend Architecture: React 19.3.1, TypeScript 6.0.3, Vite 8.3.4, Tailwind CSS 4.3.3")
    add_bullet("Database Engine: Embedded SQLite 3 with Write-Ahead Logging (WAL) mode")
    add_bullet("Testing Frameworks: Pytest 9.1.1, Vitest 5.0.5, React Testing Library 16.3.3")

    add_heading_1("3.7 Feasibility Study")
    add_body("1. Technical Feasibility: All required subsystems (Tesseract, RapidOCR, FastAPI, React 19, SQLite) are proven open-source technologies with verified zero-cost licensing. Feasibility: 100%.")
    add_body("2. Economic Feasibility: Operates entirely on commodity developer and institutional hardware with zero cloud API billing (no OpenAI or AWS subscriptions required). Feasibility: 100%.")
    add_body("3. Operational Feasibility: Designed with an intuitive, single-page web UI accessible to non-technical students and administrative clerks. Feasibility: 100%.")

    doc.add_page_break()

    # =========================================================
    # CHAPTER 4: SYSTEM DESIGN
    # =========================================================
    add_title("CHAPTER 4: SYSTEM DESIGN")
    add_heading_1("4.1 System Architecture")
    add_body(
        "SochnaSetu AI implements a decoupled three-tier architecture: the Presentation Layer (React 19 SPA running on port 5173), "
        "the Application Layer (FastAPI ASGI service running on port 8000), and the Persistence Layer (embedded SQLite database and local upload directory). "
        "Figure 4.1 illustrates the architectural components and data communication channels:"
    )
    add_image(os.path.join(DIAGRAMS_DIR, "fig_4_1_system_architecture.png"), 6.0, "Figure 4.1: Decoupled Three-Tier System Architecture Diagram")

    add_heading_1("4.2 UML Use Case Diagram")
    add_body(
        "The system accommodates two primary actors: the Student/Citizen User and the College Administrative Reviewer. "
        "Figure 4.2 presents the UML Use Case diagram mapping actors to core application capabilities:"
    )
    add_image(os.path.join(DIAGRAMS_DIR, "fig_4_2_use_case_diagram.png"), 5.8, "Figure 4.2: UML Use Case Diagram with Student and Staff Actors")

    add_heading_1("4.3 Data Flow Diagrams")
    add_heading_2("4.3.1 DFD Level 0 (Context Diagram)")
    add_body(
        "The Level 0 Context Diagram depicts the primary boundary between external users, the central SochnaSetu AI processing system, "
        "and the localized storage tier:"
    )
    add_image(os.path.join(DIAGRAMS_DIR, "fig_4_3_dfd_level_0.png"), 5.5, "Figure 4.3: Data Flow Diagram Level 0 (Context Diagram)")

    add_heading_2("4.3.2 DFD Level 1 (Decomposed Process Flow)")
    add_body(
        "The Level 1 DFD decomposes the notice transformation process into eight discrete functional stages, tracking data flows between "
        "validation, orientation recovery, OCR, language detection, human review, AI extraction, and checklist generation:"
    )
    add_image(os.path.join(DIAGRAMS_DIR, "fig_4_4_dfd_level_1.png"), 6.0, "Figure 4.4: Data Flow Diagram Level 1 (Decomposed Functional Pipeline)")

    add_heading_1("4.4 Entity-Relationship Model (SQLite Relational Schema)")
    add_body(
        "The system maintains relational state across 18 SQLite tables. The core tables include documents, analyses, checklist_items, "
        "human_review_items, user_confirmations, and users. Figure 4.5 illustrates the ER model with primary and foreign key constraints:"
    )
    add_image(os.path.join(DIAGRAMS_DIR, "fig_4_5_er_diagram.png"), 6.0, "Figure 4.5: Entity-Relationship Diagram of SQLite Database (suchnasetu.db)")

    add_heading_1("4.5 UML Sequence Diagram")
    add_body(
        "Figure 4.6 documents the chronological sequence of interactions among the User, React UI, FastAPI Server, OCR Pipeline, "
        "NoticeAnalyzer AI core, and SQLite DB during circular processing and human review correction:"
    )
    add_image(os.path.join(DIAGRAMS_DIR, "fig_4_6_sequence_diagram.png"), 6.0, "Figure 4.6: UML Sequence Diagram of End-to-End Processing Workflow")

    add_heading_1("4.6 UML Activity Diagram")
    add_body(
        "Figure 4.7 illustrates the operational control flow, detailing branching logic for born-digital PDFs versus scanned images, "
        "uncertain span routing to Human Review, and fallback execution:"
    )
    add_image(os.path.join(DIAGRAMS_DIR, "fig_4_7_activity_diagram.png"), 4.8, "Figure 4.7: UML Activity Diagram of Validation & Fallback Routing")

    add_heading_1("4.7 Database Schema Design")
    add_body(
        "Table 4.1 describes the structural definitions of the primary SQLite tables declared in src/notice2action/storage/db.py:"
    )

    # Table 4.1
    db_table = doc.add_table(rows=6, cols=4)
    db_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    db_headers = ["Table Name", "Primary Key", "Foreign Keys", "Key Fields & Responsibilities"]
    for i, h in enumerate(db_headers):
        cell = db_table.rows[0].cells[i]
        cell.paragraphs[0].add_run(h).bold = True
        set_cell_background(cell, "1E3A8A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(9.5)

    db_rows = [
        ("documents", "id (TEXT)", "None", "filename, file_path, file_size, sha256_hash, raw_text, ocr_confidence, detected_language"),
        ("analyses", "id (TEXT)", "document_id -> documents(id)", "structured_notice_json, six_core_fields_json, summary_json, reading_level"),
        ("checklist_items", "id (TEXT)", "analysis_id -> analyses(id)", "step_number, action_text, deadline_date, is_completed, priority"),
        ("human_review_items", "id (TEXT)", "document_id -> documents(id)", "page_number, original_text, corrected_text, confidence, box_json, status"),
        ("user_confirmations", "id (TEXT)", "analysis_id -> analyses(id)", "field_name, original_value, confirmed_value, is_confirmed, confirmed_at"),
    ]
    for row_idx, r_data in enumerate(db_rows, start=1):
        for col_idx, text in enumerate(r_data):
            cell = db_table.rows[row_idx].cells[col_idx]
            cell.paragraphs[0].add_run(text).font.size = Pt(8.5)
            set_cell_background(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")

    doc.add_page_break()

    # =========================================================
    # CHAPTER 5: IMPLEMENTATION
    # =========================================================
    add_title("CHAPTER 5: IMPLEMENTATION")
    add_heading_1("5.1 Development Environment & Setup")
    add_body(
        "Development was conducted on Windows 11 64-bit using Python 3.11.15, Node.js v20.x, and the modern uv package manager. "
        "The project repository is maintained at https://github.com/bhardwajji-db/suchnasetu-ai."
    )

    add_heading_1("5.2 Document Ingestion Pipeline (`ingestion.py`)")
    add_body(
        "The ingestion module (src/notice2action/ingestion.py) provides secure file ingestion. The validate_file_security function inspects the first 512 bytes "
        "for binary magic signatures (%PDF for PDFs, \\x89PNG for PNGs, \\xFF\\xD8\\xFF for JPEGs), rejecting spoofed executables. "
        "SHA-256 cryptographic digests prevent redundant reprocessing of identical circulars."
    )

    add_heading_1("5.3 Hybrid Orientation Recovery Algorithm (`ocr.py`)")
    add_body(
        "Orientation recovery is implemented in detect_image_orientation(). It executes a two-tier strategy: "
        "(1) A primary Tesseract OSD pass via pytesseract.image_to_osd() accepting confidence >= 2.0; and "
        "(2) A fallback directional projection profile variance analyzer. When OSD fails on short notices with fewer than 15 lines, "
        "the fallback computes horizontal (H_proj) and vertical (V_proj) projection sums, evaluating candidate rotations [0, 180] or [90, 270]. "
        "A 25% conservative margin protects 0° to avoid false rotation."
    )

    add_heading_1("5.4 Fused Multilingual OCR & RapidOCR Integration")
    add_body(
        "Character recognition combines Tesseract OCR (with hin+eng traineddata) and RapidOCR ONNX. "
        "Bounding boxes, word-level confidence scores, and line numbers are extracted into normalized dictionaries, "
        "enabling pixel-accurate highlight rendering in the frontend canvas."
    )

    add_heading_1("5.5 Automatic Language Detection Subsystem (`language_detection.py`)")
    add_body(
        "Automatic language detection analyzes image crops before triggering OCR. When Tesseract OSD identifies Script: Devanagari, "
        "fast sampling prioritizes Tesseract hin+eng, preventing the Latin bias of standard RapidOCR models and accurately classifying Hindi circulars."
    )

    add_heading_1("5.6 Human Review & Canonical Database Patching (`db.py`)")
    add_body(
        "When OCR confidence for a token drops below 65%, or when numerical formats are malformed, calibrate_uncertain_spans() creates records in "
        "human_review_items. In the UI, reviewers can verify or correct the text. Calling apply_review_corrections() patches the canonical documents.raw_text, "
        "ensuring all subsequent AI analysis operates on verified data."
    )

    add_heading_1("5.7 AI Reasoning & Deterministic Fallback Core (`analysis.py`)")
    add_body(
        "The NoticeAnalyzer class routes extracted text to local Gemma 4 via Ollama. If the LLM server is unreachable, it seamlessly activates "
        "_deterministic_fallback_extraction(). This resilient regex engine extracts the Six Core Fields with sub-millisecond latency."
    )

    add_heading_1("5.8 Mathematical Evidence Grounding Engine (`grounding.py`)")
    add_body(
        "Every extracted fact is evaluated by verify_fact_grounding(). The algorithm tests exact substring inclusion, followed by critical numerical/date token matching. "
        "If a fact cannot be grounded in the OCR transcript, its status is updated to NEEDS_CONFIRMATION or NOT_STATED, guaranteeing zero generative hallucination."
    )

    add_heading_1("5.9 Action Checklist & iCal Generator (`checklist.py`)")
    add_body(
        "The checklist engine converts passive administrative clauses into chronological, imperative action items. "
        "Users can export these steps as standard RFC 5545 iCalendar (.ics) files with audio alarm triggers for Google Calendar and Apple Calendar."
    )

    add_heading_1("5.10 Local Execution Scripts")
    add_body(
        "The application is launched with a single PowerShell command: .\\scripts\\run.ps1, which concurrently initializes the FastAPI backend on port 8000 "
        "and the Vite React frontend on port 5173."
    )

    doc.add_page_break()

    # =========================================================
    # CHAPTER 6: TESTING AND RESULTS
    # =========================================================
    add_title("CHAPTER 6: TESTING AND RESULTS")
    add_heading_1("6.1 Testing Methodology")
    add_body(
        "Verification combined five tiers: (1) Unit testing with pytest; (2) Integration testing of REST APIs and SQLite persistence; "
        "(3) Frontend unit testing with Vitest (26 test files, 97 passed tests); (4) Real-world validation against actual IIMT circulars and Gazette documents; "
        "and (5) Adversarial stress testing across 550 test combinations."
    )

    add_heading_1("6.2 Master Test Matrix")
    add_body("Table 6.1 details 12 representative test scenarios executed across the system:")

    # Table 6.1
    t_table = doc.add_table(rows=13, cols=5)
    t_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_headers = ["Test ID", "Test Scenario", "Input Condition", "Expected Result", "Status"]
    for i, h in enumerate(t_headers):
        cell = t_table.rows[0].cells[i]
        cell.paragraphs[0].add_run(h).bold = True
        set_cell_background(cell, "1E3A8A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(9)

    t_rows = [
        ("TC-01", "Application Startup & Health", "FastAPI :8000 & Vite :5173", "HTTP 200 OK & Status UP", "PASS"),
        ("TC-02", "PDF File Upload & Security Check", "Valid 2.4 MB notice PDF", "SHA-256 computed, saved in uploads/", "PASS"),
        ("TC-03", "Executable Extension Rejection", "Malicious file named 'doc.exe'", "HTTP 400 Bad Request, rejected", "PASS"),
        ("TC-04", "Native PDF Stream Extraction", "Born-digital circular PDF", "137 chars extracted via vector stream", "PASS"),
        ("TC-05", "Scanned PDF Fallback Ingestion", "Image-only scanned PDF", "Native text empty -> OCR fallback -> 134 chars", "PASS"),
        ("TC-06", "Auto Language Detection (English)", "Real IIMT College Notice", "Detected 'en' (conf: 1.0), Mode: eng", "PASS"),
        ("TC-07", "Auto Language Detection (Hindi)", "Gazette Corrigendum 2017", "Detected 'hi' (conf: 0.85), Mode: hin+eng", "PASS"),
        ("TC-08", "90° Rotation Recovery", "IIMT Notice rotated 90° CW", "Detected 90° -> Rotated 270° to upright", "PASS"),
        ("TC-09", "180° Inverted Scan Recovery", "IIMT Notice upside-down", "Detected 180° -> Rotated 180° to upright", "PASS"),
        ("TC-10", "Deskewing on +4.0° Tilt", "Synthetic tilted scan", "Calculated -4.0° -> restored horizontal", "PASS"),
        ("TC-11", "Human Review Restart Persistence", "Simulated application restart", "Reloaded review items from SQLite intact", "PASS"),
        ("TC-12", "Canonical Text Patching", "Reviewer corrected Ref No.", "Patched documents.raw_text (count=2)", "PASS"),
    ]
    for row_idx, r_data in enumerate(t_rows, start=1):
        for col_idx, text in enumerate(r_data):
            cell = t_table.rows[row_idx].cells[col_idx]
            p = cell.paragraphs[0]
            p.add_run(text).font.size = Pt(8.5)
            if col_idx == 4:
                p.runs[0].bold = True
            set_cell_background(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")

    add_heading_1("6.3 Empirical OCR Accuracy Benchmarks")
    add_body(
        "Empirical Character Error Rate (CER) and Word Error Rate (WER) were benchmarked against verified ground-truth transcripts "
        "from our formal real-world validation harness (reports/real_world_validation_results.json):"
    )

    # Table 6.2
    acc_table = doc.add_table(rows=7, cols=5)
    acc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    acc_headers = ["Document Description", "Engine Evaluated", "CER (%)", "WER (%)", "Character Accuracy (%)"]
    for i, h in enumerate(acc_headers):
        cell = acc_table.rows[0].cells[i]
        cell.paragraphs[0].add_run(h).bold = True
        set_cell_background(cell, "1E3A8A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(9)

    acc_rows = [
        ("Synthetic Scholarship Notice (English)", "Tesseract (eng)", "0.69%", "6.06%", "99.31%"),
        ("Synthetic Scholarship Notice (English)", "RapidOCR (ONNX)", "2.22%", "24.24%", "97.78%"),
        ("Gazette Corrigendum 2017 (Hindi)", "Tesseract (hin+eng)", "2.75%", "7.07%", "97.25%"),
        ("Gazette Corrigendum 2017 (Hindi)", "RapidOCR (ONNX)*", "83.50%", "97.70%", "16.50%"),
        ("IIMT College Notice (Real Physical Scan)", "Tesseract (eng)", "2.21%", "6.45%", "97.79%"),
        ("IIMT College Notice (Real Physical Scan)", "RapidOCR (ONNX)", "10.86%", "87.63%", "89.14%"),
    ]
    for row_idx, r_data in enumerate(acc_rows, start=1):
        for col_idx, text in enumerate(r_data):
            cell = acc_table.rows[row_idx].cells[col_idx]
            p = cell.paragraphs[0]
            p.add_run(text).font.size = Pt(8.5)
            if col_idx in [2, 4]:
                p.runs[0].bold = True
            set_cell_background(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")

    add_body("*Note: RapidOCR ONNX default models lack Devanagari weights, justifying SochnaSetu AI's hybrid routing to Tesseract for Hindi.")

    add_heading_1("6.4 Statutory Entities Extraction Verification")
    add_body("Table 6.3 confirms statutory entity extraction against the physical IIMT Engineering College notice scan:")

    # Table 6.3
    ent_table = doc.add_table(rows=8, cols=4)
    ent_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    ent_headers = ["Statutory Entity", "Ground Truth Value", "Extracted Value", "Verification Status"]
    for i, h in enumerate(ent_headers):
        cell = ent_table.rows[0].cells[i]
        cell.paragraphs[0].add_run(h).bold = True
        set_cell_background(cell, "1E3A8A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(9)

    ent_rows = [
        ("Reference Number", "IIMT/IQAC/2026-27/11", "IIMT/IQAC/2026-27/11", "VERIFIED (100% Match)"),
        ("Notice Date", "29.10.2026", "29.10.2026", "VERIFIED (100% Match)"),
        ("Event Date / Deadline", "30th October 2026", "30th October 2026", "VERIFIED (100% Match)"),
        ("Time Window", "6:00 pm to 8:00 pm", "6:00 pm to 8:00 pm", "VERIFIED (100% Match)"),
        ("Venue", "Auditorium, Main Building 127", "Auditorium, Main Building 127", "VERIFIED (100% Match)"),
        ("Signatory Name", "Dr. Shilpi Singh", "Dr. Shilpi Singh", "VERIFIED (100% Match)"),
        ("Signatory Designation", "Head, IQAC", "Head, IQAC", "VERIFIED (100% Match)"),
    ]
    for row_idx, r_data in enumerate(ent_rows, start=1):
        for col_idx, text in enumerate(r_data):
            cell = ent_table.rows[row_idx].cells[col_idx]
            p = cell.paragraphs[0]
            p.add_run(text).font.size = Pt(8.5)
            if col_idx == 3:
                p.runs[0].bold = True
            set_cell_background(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")

    add_heading_1("6.5 Application Screenshot Evidence Catalog")
    add_body("Figures 6.1 through 6.8 document genuine application screenshots captured from the running full-stack system:")

    add_image(os.path.join(SCREENSHOTS_DIR, "fig_6_1_dashboard.png"), 5.5, "Figure 6.1: Master Desktop Application Dashboard View")
    add_image(os.path.join(SCREENSHOTS_DIR, "fig_6_2_ingestion_ocr.png"), 5.5, "Figure 6.2: Document Ingestion & Interactive OCR Bounding Box Review")
    add_image(os.path.join(SCREENSHOTS_DIR, "fig_6_3_grounded_facts.png"), 5.5, "Figure 6.3: Grounded Facts & Evidence Inspector Drawer")
    add_image(os.path.join(SCREENSHOTS_DIR, "fig_6_4_action_checklist.png"), 5.5, "Figure 6.4: Action Checklist Interface with Completion Tracking")
    add_image(os.path.join(SCREENSHOTS_DIR, "fig_6_5_grounded_qa.png"), 5.5, "Figure 6.5: Grounded Conversational Follow-Up Q&A Interface")
    add_image(os.path.join(SCREENSHOTS_DIR, "fig_6_6_revision_ledger.png"), 5.5, "Figure 6.6: Corrigendum Revision Ledger Comparison View")
    add_image(os.path.join(SCREENSHOTS_DIR, "fig_6_7_mobile_view.png"), 3.2, "Figure 6.7: Responsive Mobile Viewport (390px Display)")
    add_image(os.path.join(SCREENSHOTS_DIR, "fig_6_8_dark_theme.png"), 5.5, "Figure 6.8: High-Contrast Midnight Teal Accessibility Theme Mode")

    add_heading_1("6.6 Comprehensive Adversarial Benchmark Results (550 Tests)")
    add_body(
        "Formal adversarial evaluation across 55 ground-truth circulars subject to 10 degradation types (550 total runs) demonstrated: "
        "(1) Orientation Recovery Rate: 100.0% (220/220); (2) Clean Baseline CER: 6.70% (English: 2.72%, Hindi: 19.63%); "
        "(3) Important Field Precision: 90.0%; and (4) Prompt Injection Defense: 100.0%."
    )

    doc.add_page_break()

    # =========================================================
    # CHAPTER 7: CONCLUSION AND FUTURE SCOPE
    # =========================================================
    add_title("CHAPTER 7: CONCLUSION AND FUTURE SCOPE")
    add_heading_1("7.1 Project Summary")
    add_body(
        "SochnaSetu AI demonstrates a fully functional, local-first document intelligence platform engineered specifically for Indian university and "
        "civic circulars. By combining adaptive preprocessing, hybrid geometric orientation correction, fused multilingual OCR, and mathematical evidence "
        "grounding, the project successfully bridges the gap between opaque administrative documents and concrete student actions. "
        "Operating on consumer hardware with zero recurring cloud subscriptions, the system delivers verified checklists and calendar reminders with "
        "strict zero-hallucination guarantees."
    )

    add_heading_1("7.2 Objectives Achieved")
    add_bullet("100% orientation recovery across 0°, 90°, 180°, and 270° rotated circulars.")
    add_bullet("97.79% character accuracy on real physical college notice scans in English and 97.25% on Hindi Gazette notices.")
    add_bullet("Zero generative hallucination on omitted deadlines, fees, and eligibility criteria.")
    add_bullet("Real-time Human Review canvas with red underlines and one-click canonical SQLite database updating.")
    add_bullet("Standardized iCalendar (.ics) export with alarm triggers.")

    add_heading_1("7.3 Current Operational Limitations")
    add_bullet("Global Otsu binarization degrades under harsh, non-uniform mobile shadow gradients.")
    add_bullet("Complex Devanagari conjunct ligatures exhibit higher CER (19.63%) under standard Tesseract compared to English.")
    add_bullet("Local 4-bit Gemma 4 LLM requires at least 8 GB of host RAM for comfortable interactive execution.")

    add_heading_1("7.4 Future Research & Mobile Roadmap")
    add_bullet("Integrate adaptive Sauvola binarization to enhance shadow tolerance on mobile smartphone photos.")
    add_bullet("Deploy custom Devanagari ONNX weights into RapidOCR to accelerate local Hindi inference.")
    add_bullet("Package the client as a local Android APK using React Native and ONNX Runtime Mobile for on-device processing.")

    doc.add_page_break()

    # =========================================================
    # REFERENCES (IEEE STYLE)
    # =========================================================
    add_title("REFERENCES")
    refs = [
        "[1] R. Smith, \"An Overview of the Tesseract OCR Engine,\" in Proc. 9th Int. Conf. on Document Analysis and Recognition (ICDAR 2007), Curitiba, Brazil, 2007, pp. 629–633, doi: 10.1109/ICDAR.2007.4376991.",
        "[2] Gemma Team, Google DeepMind, \"Gemma: Open Models Based on Gemini Research and Technology,\" arXiv preprint arXiv:2403.08295, Mar. 2024. [Online]. Available: https://arxiv.org/abs/2403.08295",
        "[3] P. Lewis, E. Perez, A. Piktus, et al., \"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,\" in Advances in Neural Information Processing Systems (NeurIPS 2020), vol. 33, 2020, pp. 9459–9474.",
        "[4] N. Otsu, \"A Threshold Selection Method from Gray-Level Histograms,\" IEEE Transactions on Systems, Man, and Cybernetics, vol. 9, no. 1, pp. 62–66, Jan. 1979, doi: 10.1109/TSMC.1979.4310076.",
        "[5] S. Ramirez and T. V. Raman, \"FastAPI: Modern, High-Performance Web Framework for Python,\" Tiangolo Open Source Documentation, 2024. [Online]. Available: https://fastapi.tiangolo.com/",
        "[6] Meta Open Source, \"React 19 Documentation and Architecture Guide,\" React Core Team, 2024. [Online]. Available: https://react.dev/",
        "[7] D. R. Hipp, \"SQLite: An Embeddable, Serverless, Zero-Configuration SQL Database Engine,\" SQLite Consortium Architecture Reference, 2024. [Online]. Available: https://www.sqlite.org/arch.html",
        "[8] Tesseract OCR Team, \"Tesseract OCR Documentation and Language Data Files,\" GitHub Repository, 2024. [Online]. Available: https://github.com/tesseract-ocr/tesseract",
        "[9] RapidOCR Contributors, \"RapidOCR: A Cross-Platform OCR Suite Based on ONNXRuntime,\" GitHub Repository, 2024. [Online]. Available: https://github.com/RapidAI/RapidOCR",
        "[10] Internet Engineering Task Force (IETF), \"RFC 5545: Internet Calendaring and Scheduling Core Object Specification (iCalendar),\" B. Desruisseaux, Ed., Sep. 2009. [Online]. Available: https://www.rfc-editor.org/rfc/rfc5545",
    ]
    for r_text in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.add_run(r_text).font.size = Pt(10)

    doc.add_page_break()

    # =========================================================
    # APPENDICES
    # =========================================================
    add_title("APPENDICES")
    add_heading_1("Appendix A: Installation and Environment Configuration")
    add_body("1. Install Python 3.11.x, Node.js v20.x, and Git on Windows 11.")
    add_body("2. Install Tesseract OCR v5.4.0 with hin and eng traineddata into C:\\Program Files\\Tesseract-OCR\\.")
    add_body("3. Run .\\scripts\\setup.ps1 to create the Python virtual environment and install dependencies.")

    add_heading_1("Appendix B: Verified API Endpoint Reference")
    add_body("Table D.1 documents the verified REST API controllers in src/notice2action/api/server.py:")

    # API Table
    api_table = doc.add_table(rows=7, cols=4)
    api_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    api_headers = ["HTTP Method", "Route Endpoint", "Purpose", "Response Type"]
    for i, h in enumerate(api_headers):
        cell = api_table.rows[0].cells[i]
        cell.paragraphs[0].add_run(h).bold = True
        set_cell_background(cell, "1E3A8A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(9)

    api_rows = [
        ("POST", "/api/ingest/upload", "Uploads circular and computes SHA-256", "DocumentRecord (JSON)"),
        ("POST", "/api/ocr", "Executes hybrid orientation & OCR", "OCRResponse (JSON)"),
        ("POST", "/api/detect-language", "Detects English/Hindi language mode", "LanguageResponse (JSON)"),
        ("POST", "/api/analyze", "Extracts Six Core Fields & Grounded Facts", "AnalyzeResponse (JSON)"),
        ("POST", "/api/human-review/apply", "Patches reviewer edits to raw text", "ApplyResponse (JSON)"),
        ("POST", "/api/export/ics", "Generates standard iCalendar file", "text/calendar (.ics stream)"),
    ]
    for row_idx, r_data in enumerate(api_rows, start=1):
        for col_idx, text in enumerate(r_data):
            cell = api_table.rows[row_idx].cells[col_idx]
            cell.paragraphs[0].add_run(text).font.size = Pt(8.5)
            set_cell_background(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")

    add_heading_1("Appendix C: Repository and Deployment Information")
    add_body("The official project repository is maintained at: https://github.com/bhardwajji-db/suchnasetu-ai")
    add_body("To start both backend and frontend concurrently: .\\scripts\\run.ps1")
    add_body("To execute backend test suite: .\\.venv\\Scripts\\python.exe -m pytest tests/ -v")
    add_body("To execute frontend test suite: cd frontend; npm test -- --run")

    # Save DOCX
    doc.save(DOCX_PATH)
    print(f"Successfully generated DOCX report at: {DOCX_PATH}")

if __name__ == "__main__":
    create_document()
