"""
Generates high-resolution academic diagrams and official placeholders
for SochnaSetu AI B.Tech Mini Project Report.
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "SochnaSetu_AI_Final_Report"
DIAGRAMS_DIR = os.path.join(OUTPUT_DIR, "diagrams")
SCREENSHOTS_DIR = os.path.join(OUTPUT_DIR, "screenshots")
os.makedirs(DIAGRAMS_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. College Logo Placeholder
# -------------------------------------------------------------
def generate_logo_placeholder():
    w, h = 600, 160
    img = Image.new("RGBA", (w, h), (248, 250, 252, 255))
    draw = ImageDraw.Draw(img)
    # Border
    draw.rectangle([6, 6, w - 7, h - 7], outline=(30, 58, 138), width=3)
    draw.rectangle([12, 12, w - 13, h - 13], outline=(148, 163, 184), width=1)
    
    # Text
    draw.text((w // 2, 50), "[INSERT OFFICIAL COLLEGE LOGO]", fill=(30, 58, 138), anchor="mm")
    draw.text((w // 2, 85), "IIMT Engineering College, Meerut", fill=(71, 85, 105), anchor="mm")
    draw.text((w // 2, 115), "Affiliated to Dr. A.P.J. Abdul Kalam Technical University, UP", fill=(100, 116, 139), anchor="mm")
    
    dest = os.path.join(SCREENSHOTS_DIR, "college_logo_placeholder.png")
    img.save(dest, "PNG")
    print(f"Generated logo placeholder at: {dest}")

# -------------------------------------------------------------
# 2. Fig 4.1: System Architecture Diagram
# -------------------------------------------------------------
def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis('off')

    # Background subtle styling
    fig.patch.set_facecolor('#ffffff')

    # Outer Tiers
    tiers = [
        ("Presentation Layer (Client Browser / SPA)", 0.5, 0.5, 3.2, 6.5, '#eff6ff', '#1e40af'),
        ("Application & Processing Layer (FastAPI Service)", 4.2, 0.5, 4.4, 6.5, '#f0fdf4', '#166534'),
        ("Persistence Layer (Local Host Storage)", 9.1, 0.5, 2.4, 6.5, '#fefce8', '#854d0e')
    ]
    for title, x, y, w, h, bg, border in tiers:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                                      facecolor=bg, edgecolor=border, linewidth=1.5, linestyle='--')
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 0.35, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color=border)

    # Subcomponents - Presentation Tier
    pres_boxes = [
        ("React 19 / Vite SPA\n(TypeScript 6.0.3, Tailwind CSS)", 0.7, 5.0, 2.8, 0.9, '#dbeafe', '#1d4ed8'),
        ("Interactive Review Canvas\n(Bounding Boxes & Keyword Search)", 0.7, 3.8, 2.8, 0.9, '#dbeafe', '#1d4ed8'),
        ("Action Checklist & iCal Export\n(Task Tracking & .ics Alarms)", 0.7, 2.6, 2.8, 0.9, '#dbeafe', '#1d4ed8'),
        ("Voice Guidance & Themes\n(HTML5 Web Audio & Contrast Themes)", 0.7, 1.4, 2.8, 0.9, '#dbeafe', '#1d4ed8'),
    ]
    for text, x, y, w, h, bg, border in pres_boxes:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.1",
                                      facecolor=bg, edgecolor=border, linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=8, color='#0f172a', multialignment='center')

    # Subcomponents - Application Tier
    app_boxes = [
        ("FastAPI ASGI Server (Port 8000)\nREST API Endpoints & Session Auth", 4.5, 5.4, 3.8, 0.75, '#dcfce7', '#15803d'),
        ("Document Ingestion & Validation\nMIME Verification & SHA-256 Hashing", 4.5, 4.4, 3.8, 0.75, '#dcfce7', '#15803d'),
        ("Orientation & OCR Fusion Core\nTesseract (OSD + hin+eng) & RapidOCR", 4.5, 3.4, 3.8, 0.75, '#dcfce7', '#15803d'),
        ("NoticeAnalyzer AI Core\nLocal Gemma 4 / Ollama + Regex Fallback", 4.5, 2.4, 3.8, 0.75, '#dcfce7', '#15803d'),
        ("Evidence Grounding Engine\nSubstring Anchoring & NOT_STATED Calibration", 4.5, 1.4, 3.8, 0.75, '#dcfce7', '#15803d'),
    ]
    for text, x, y, w, h, bg, border in app_boxes:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.1",
                                      facecolor=bg, edgecolor=border, linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=8, color='#0f172a', multialignment='center')

    # Subcomponents - Persistence Tier
    data_boxes = [
        ("SQLite 3 Database\n(WAL Mode ACID Storage)\nsuchnasetu.db (18 Tables)", 9.3, 4.2, 2.0, 1.8, '#fef08a', '#a16207'),
        ("Upload Filesystem\n(Raw PDFs & PNGs)\ndata/uploads/ Directory", 9.3, 1.6, 2.0, 1.8, '#fef08a', '#a16207'),
    ]
    for text, x, y, w, h, bg, border in data_boxes:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.1",
                                      facecolor=bg, edgecolor=border, linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=8, color='#0f172a', multialignment='center')

    # Arrows Connecting Tiers
    arrow_props = dict(arrowstyle="<->", color="#0284c7", lw=1.5, mutation_scale=14)
    # UI <-> Server
    ax.annotate("", xy=(4.5, 5.75), xytext=(3.5, 5.45), arrowprops=arrow_props)
    ax.text(4.0, 5.85, "REST / JSON", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#0369a1')
    
    # Server <-> DB
    ax.annotate("", xy=(9.3, 5.1), xytext=(8.3, 5.75), arrowprops=arrow_props)
    ax.text(8.8, 5.65, "SQL / WAL", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#0369a1')

    # Server <-> Filesystem
    ax.annotate("", xy=(9.3, 2.5), xytext=(8.3, 4.75), arrowprops=arrow_props)
    ax.text(8.8, 3.8, "Disk I/O", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#0369a1')

    plt.tight_layout()
    dest = os.path.join(DIAGRAMS_DIR, "fig_4_1_system_architecture.png")
    plt.savefig(dest, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Generated architecture diagram at: {dest}")

# -------------------------------------------------------------
# 3. Fig 4.2: UML Use Case Diagram
# -------------------------------------------------------------
def generate_use_case_diagram():
    fig, ax = plt.subplots(figsize=(11, 8), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Boundary Box
    rect = patches.FancyBboxPatch((2.6, 0.4), 6.0, 7.2, boxstyle="round,pad=0.1,rounding_size=0.15",
                                  facecolor='#f8fafc', edgecolor='#334155', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(5.6, 7.3, "SochnaSetu AI System Boundary", ha='center', va='center', fontsize=11, fontweight='bold', color='#1e293b')

    # Actors
    def draw_actor(x, y, label):
        # Head
        circle = patches.Circle((x, y + 0.35), 0.16, facecolor='#ffffff', edgecolor='#0f172a', lw=1.5)
        ax.add_patch(circle)
        # Body
        ax.plot([x, x], [y + 0.19, y - 0.15], color='#0f172a', lw=1.5)
        # Arms
        ax.plot([x - 0.25, x + 0.25], [y + 0.05, y + 0.05], color='#0f172a', lw=1.5)
        # Legs
        ax.plot([x, x - 0.2], [y - 0.15, y - 0.45], color='#0f172a', lw=1.5)
        ax.plot([x, x + 0.2], [y - 0.15, y - 0.45], color='#0f172a', lw=1.5)
        ax.text(x, y - 0.65, label, ha='center', va='top', fontsize=9, fontweight='bold', color='#0f172a')

    draw_actor(1.2, 4.5, "Student /\nCitizen User")
    draw_actor(9.8, 4.5, "College Staff /\nReviewer")

    # Use Cases (Ellipses)
    use_cases = [
        (1, "Upload Official Notice (PDF / Image)", 5.6, 6.7, True, True),
        (2, "View Original Document & Overlay", 5.6, 6.0, True, True),
        (3, "Execute Multi-Engine OCR & Deskew", 5.6, 5.3, True, True),
        (4, "Review & Correct Uncertain Spans", 5.6, 4.6, True, True),
        (5, "Inspect Grounded Six Core Fields", 5.6, 3.9, True, True),
        (6, "Evaluate Candidate Eligibility", 5.6, 3.2, True, False),
        (7, "Manage Action Checklist & Deadlines", 5.6, 2.5, True, False),
        (8, "Export Calendar Reminders (.ics)", 5.6, 1.8, True, False),
        (9, "Compare Circular with Corrigendum", 5.6, 1.1, False, True),
    ]

    for num, title, cx, cy, for_student, for_staff in use_cases:
        ellipse = patches.Ellipse((cx, cy), 4.6, 0.52, facecolor='#eff6ff', edgecolor='#2563eb', lw=1.2)
        ax.add_patch(ellipse)
        ax.text(cx, cy, f"UC-{num:02d}: {title}", ha='center', va='center', fontsize=8, color='#1e3a8a')

        # Link to actors
        if for_student:
            ax.plot([1.4, cx - 2.3], [4.5, cy], color='#64748b', lw=1.0, linestyle='-')
        if for_staff:
            ax.plot([9.6, cx + 2.3], [4.5, cy], color='#64748b', lw=1.0, linestyle='-')

    plt.tight_layout()
    dest = os.path.join(DIAGRAMS_DIR, "fig_4_2_use_case_diagram.png")
    plt.savefig(dest, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Generated use case diagram at: {dest}")

# -------------------------------------------------------------
# 4. Fig 4.3 & 4.4: DFD Level 0 & Level 1
# -------------------------------------------------------------
def generate_dfd_level_0():
    fig, ax = plt.subplots(figsize=(9, 4), dpi=300)
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 4)
    ax.axis('off')

    # External Entity User
    user_box = patches.Rectangle((0.6, 1.3), 1.8, 1.4, facecolor='#dbeafe', edgecolor='#1e40af', lw=1.5)
    ax.add_patch(user_box)
    ax.text(1.5, 2.0, "User\n(Student/Staff)", ha='center', va='center', fontsize=9, fontweight='bold', color='#1e3a8a')

    # Process 0
    proc_circle = patches.Circle((4.5, 2.0), 1.1, facecolor='#dcfce7', edgecolor='#15803d', lw=1.8)
    ax.add_patch(proc_circle)
    ax.text(4.5, 2.15, "0.0", ha='center', va='center', fontsize=10, fontweight='bold', color='#166534')
    ax.text(4.5, 1.85, "SochnaSetu AI\nSystem", ha='center', va='center', fontsize=9, fontweight='bold', color='#166534')

    # Data Store Storage
    ds_top = patches.Rectangle((7.0, 1.4), 1.6, 1.2, facecolor='#fef08a', edgecolor='#a16207', lw=1.5)
    ax.add_patch(ds_top)
    ax.text(7.8, 2.0, "D1: Local Storage\n(SQLite + Disk)", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#854d0e')

    # Data Flows
    arrow_right = dict(arrowstyle="->", color="#0284c7", lw=1.3, mutation_scale=12)
    arrow_left = dict(arrowstyle="->", color="#059669", lw=1.3, mutation_scale=12)

    # User -> Process
    ax.annotate("", xy=(3.4, 2.3), xytext=(2.4, 2.3), arrowprops=arrow_right)
    ax.text(2.9, 2.5, "Notice PDF / Image", ha='center', va='bottom', fontsize=7.5, color='#0369a1')

    # Process -> User
    ax.annotate("", xy=(2.4, 1.7), xytext=(3.4, 1.7), arrowprops=arrow_left)
    ax.text(2.9, 1.45, "Action Checklist / Grounded Facts", ha='center', va='top', fontsize=7.5, color='#047857')

    # Process <-> Storage
    ax.annotate("", xy=(7.0, 2.3), xytext=(5.6, 2.3), arrowprops=arrow_right)
    ax.text(6.3, 2.5, "Persist Record", ha='center', va='bottom', fontsize=7.5, color='#0369a1')

    ax.annotate("", xy=(5.6, 1.7), xytext=(7.0, 1.7), arrowprops=arrow_left)
    ax.text(6.3, 1.45, "Retrieve Data", ha='center', va='top', fontsize=7.5, color='#047857')

    plt.tight_layout()
    dest = os.path.join(DIAGRAMS_DIR, "fig_4_3_dfd_level_0.png")
    plt.savefig(dest, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Generated DFD Level 0 at: {dest}")

def generate_dfd_level_1():
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7)
    ax.axis('off')

    processes = [
        (1, "1.0 Validate & Store File", 1.8, 5.8),
        (2, "2.0 Detect Angle & Deskew", 4.5, 5.8),
        (3, "3.0 Fused OCR & Token Boxes", 7.5, 5.8),
        (4, "4.0 Detect Document Language", 9.5, 4.3),
        (5, "5.0 Human Review Calibration", 7.5, 2.8),
        (6, "6.0 Canonical AI Extraction", 4.5, 2.8),
        (7, "7.0 Evidence Grounding Match", 1.8, 2.8),
        (8, "8.0 Action Checklist & Alarms", 1.8, 1.0),
    ]

    for pnum, pname, px, py in processes:
        rect = patches.FancyBboxPatch((px - 1.1, py - 0.4), 2.2, 0.8, boxstyle="round,pad=0.08,rounding_size=0.1",
                                      facecolor='#eff6ff', edgecolor='#1d4ed8', lw=1.3)
        ax.add_patch(rect)
        ax.text(px, py, pname, ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1e3a8a')

    # Stores
    ds1 = patches.Rectangle((4.5 - 1.1, 4.3 - 0.35), 2.2, 0.7, facecolor='#fef08a', edgecolor='#a16207', lw=1.2)
    ax.add_patch(ds1)
    ax.text(4.5, 4.3, "D1: documents / uploads", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#854d0e')

    ds2 = patches.Rectangle((4.5 - 1.1, 1.0 - 0.35), 2.2, 0.7, facecolor='#fef08a', edgecolor='#a16207', lw=1.2)
    ax.add_patch(ds2)
    ax.text(4.5, 1.0, "D2: analyses / checklist", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#854d0e')

    # Flow arrows
    arr = dict(arrowstyle="->", color="#0284c7", lw=1.2, mutation_scale=10)
    # 1.0 -> 2.0
    ax.annotate("", xy=(3.4, 5.8), xytext=(2.9, 5.8), arrowprops=arr)
    # 2.0 -> 3.0
    ax.annotate("", xy=(6.4, 5.8), xytext=(5.6, 5.8), arrowprops=arr)
    # 3.0 -> 4.0
    ax.annotate("", xy=(9.5, 4.7), xytext=(8.4, 5.5), arrowprops=arr)
    # 4.0 -> 5.0
    ax.annotate("", xy=(8.4, 3.1), xytext=(9.1, 4.0), arrowprops=arr)
    # 5.0 -> 6.0
    ax.annotate("", xy=(5.6, 2.8), xytext=(6.4, 2.8), arrowprops=arr)
    # 6.0 -> 7.0
    ax.annotate("", xy=(2.9, 2.8), xytext=(3.4, 2.8), arrowprops=arr)
    # 7.0 -> 8.0
    ax.annotate("", xy=(1.8, 1.4), xytext=(1.8, 2.4), arrowprops=arr)

    # 1.0 -> D1
    ax.annotate("", xy=(4.0, 4.5), xytext=(2.4, 5.4), arrowprops=arr)
    # 8.0 -> D2
    ax.annotate("", xy=(3.4, 1.0), xytext=(2.9, 1.0), arrowprops=arr)

    plt.tight_layout()
    dest = os.path.join(DIAGRAMS_DIR, "fig_4_4_dfd_level_1.png")
    plt.savefig(dest, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Generated DFD Level 1 at: {dest}")

# -------------------------------------------------------------
# 5. Fig 4.5: Entity-Relationship Diagram
# -------------------------------------------------------------
def generate_er_diagram():
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    entities = [
        ("documents", 1.0, 4.8, 2.8, 2.6, [
            ("id", "TEXT (PK)"),
            ("filename", "TEXT"),
            ("file_path", "TEXT"),
            ("file_type", "TEXT"),
            ("file_size", "INTEGER"),
            ("sha256_hash", "TEXT"),
            ("raw_text", "TEXT"),
            ("ocr_confidence", "REAL"),
            ("detected_language", "TEXT"),
        ]),
        ("analyses", 5.0, 4.8, 2.8, 2.6, [
            ("id", "TEXT (PK)"),
            ("document_id", "TEXT (FK)"),
            ("structured_notice_json", "TEXT"),
            ("six_core_fields_json", "TEXT"),
            ("summary_json", "TEXT"),
            ("reading_level", "TEXT"),
            ("target_language", "TEXT"),
            ("created_at", "REAL"),
        ]),
        ("checklist_items", 9.0, 4.8, 2.6, 2.6, [
            ("id", "TEXT (PK)"),
            ("analysis_id", "TEXT (FK)"),
            ("step_number", "INTEGER"),
            ("action_text", "TEXT"),
            ("deadline_date", "TEXT"),
            ("is_completed", "INTEGER"),
            ("priority", "TEXT"),
        ]),
        ("human_review_items", 1.0, 1.0, 2.8, 2.8, [
            ("id", "TEXT (PK)"),
            ("document_id", "TEXT (FK)"),
            ("page_number", "INTEGER"),
            ("original_text", "TEXT"),
            ("corrected_text", "TEXT"),
            ("confidence", "REAL"),
            ("box_json", "TEXT"),
            ("status", "TEXT"),
            ("reason", "TEXT"),
        ]),
        ("user_confirmations", 5.0, 1.0, 2.8, 2.8, [
            ("id", "TEXT (PK)"),
            ("analysis_id", "TEXT (FK)"),
            ("field_name", "TEXT"),
            ("original_value", "TEXT"),
            ("confirmed_value", "TEXT"),
            ("is_confirmed", "INTEGER"),
            ("confirmed_at", "REAL"),
        ]),
        ("users", 9.0, 1.0, 2.6, 2.8, [
            ("id", "TEXT (PK)"),
            ("email", "TEXT (UNIQUE)"),
            ("password_hash", "TEXT"),
            ("full_name", "TEXT"),
            ("role", "TEXT"),
            ("is_active", "INTEGER"),
            ("created_at", "REAL"),
        ]),
    ]

    for name, x, y, w, h, cols in entities:
        # Header Box
        header_rect = patches.Rectangle((x, y + h - 0.5), w, 0.5, facecolor='#1e40af', edgecolor='#1e3a8a', lw=1.2)
        ax.add_patch(header_rect)
        ax.text(x + w/2, y + h - 0.25, name.upper(), ha='center', va='center', fontsize=8.5, fontweight='bold', color='#ffffff')

        # Body Box
        body_rect = patches.Rectangle((x, y), w, h - 0.5, facecolor='#f8fafc', edgecolor='#cbd5e1', lw=1.2)
        ax.add_patch(body_rect)

        # Columns
        start_y = y + h - 0.8
        for col_name, col_type in cols:
            ax.text(x + 0.15, start_y, col_name, ha='left', va='center', fontsize=7.5, color='#0f172a', fontweight='bold' if 'PK' in col_type or 'FK' in col_type else 'normal')
            ax.text(x + w - 0.15, start_y, col_type, ha='right', va='center', fontsize=7, color='#64748b')
            start_y -= 0.23

    # Relationships Lines
    rel_props = dict(color="#2563eb", lw=1.5)
    # documents -> analyses (1 : N)
    ax.plot([3.8, 5.0], [6.1, 6.1], **rel_props)
    ax.text(4.4, 6.25, "1 : N", ha='center', va='bottom', fontsize=8, color='#1e40af', fontweight='bold')

    # analyses -> checklist_items (1 : N)
    ax.plot([7.8, 9.0], [6.1, 6.1], **rel_props)
    ax.text(8.4, 6.25, "1 : N", ha='center', va='bottom', fontsize=8, color='#1e40af', fontweight='bold')

    # documents -> human_review_items (1 : N)
    ax.plot([2.4, 2.4], [4.8, 3.8], **rel_props)
    ax.text(2.65, 4.3, "1 : N", ha='left', va='center', fontsize=8, color='#1e40af', fontweight='bold')

    # analyses -> user_confirmations (1 : N)
    ax.plot([6.4, 6.4], [4.8, 3.8], **rel_props)
    ax.text(6.65, 4.3, "1 : N", ha='left', va='center', fontsize=8, color='#1e40af', fontweight='bold')

    plt.tight_layout()
    dest = os.path.join(DIAGRAMS_DIR, "fig_4_5_er_diagram.png")
    plt.savefig(dest, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Generated ER diagram at: {dest}")

# -------------------------------------------------------------
# 6. Fig 4.6 & 4.7: Sequence & Activity Diagrams
# -------------------------------------------------------------
def generate_sequence_diagram():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7.5)
    ax.axis('off')

    lifelines = [
        ("User", 1.0),
        ("React UI", 2.8),
        ("FastAPI Server", 4.8),
        ("OCR Pipeline", 6.8),
        ("NoticeAnalyzer (AI)", 8.8),
        ("SQLite DB", 10.2)
    ]

    for name, x in lifelines:
        # Header
        box = patches.Rectangle((x - 0.7, 6.8), 1.4, 0.5, facecolor='#dbeafe', edgecolor='#1e40af', lw=1.2)
        ax.add_patch(box)
        ax.text(x, 7.05, name, ha='center', va='center', fontsize=8, fontweight='bold', color='#1e3a8a')
        # Dashed line
        ax.plot([x, x], [6.8, 0.4], color='#94a3b8', linestyle='--', lw=1.0)

    # Sequence Messages
    msgs = [
        (6.3, 1.0, 2.8, "1: Upload notice file (image/pdf)", True),
        (5.8, 2.8, 4.8, "2: POST /api/ingest/upload", True),
        (5.3, 4.8, 10.2, "3: Store metadata & save binary", True),
        (4.8, 4.8, 6.8, "4: Execute hybrid OCR & deskew", True),
        (4.3, 6.8, 4.8, "5: Return text & token boxes", False),
        (3.8, 4.8, 8.8, "6: Extract 6 Canonical Fields", True),
        (3.3, 8.8, 4.8, "7: Return structured JSON", False),
        (2.8, 4.8, 10.2, "8: Save analysis & checklist", True),
        (2.3, 4.8, 2.8, "9: Return complete result envelope", False),
        (1.8, 2.8, 1.0, "10: Render interactive checklist & facts", False),
        (1.2, 1.0, 2.8, "11: User edits uncertain ref number", True),
        (0.7, 2.8, 4.8, "12: POST /api/human-review/apply", True),
    ]

    for y, x1, x2, text, is_call in msgs:
        style = "->"
        linestyle = "-" if is_call else "--"
        color = "#1e40af" if is_call else "#059669"
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle=style, linestyle=linestyle, color=color, lw=1.2, mutation_scale=10))
        mid_x = (x1 + x2) / 2
        ax.text(mid_x, y + 0.1, text, ha='center', va='bottom', fontsize=7, color='#0f172a')

    plt.tight_layout()
    dest = os.path.join(DIAGRAMS_DIR, "fig_4_6_sequence_diagram.png")
    plt.savefig(dest, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Generated sequence diagram at: {dest}")

def generate_activity_diagram():
    fig, ax = plt.subplots(figsize=(8, 9), dpi=300)
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Initial node
    start = patches.Circle((4.0, 8.5), 0.18, facecolor='#0f172a', edgecolor='#0f172a')
    ax.add_patch(start)

    steps = [
        ("Receive Document Upload", 4.0, 7.8, 'action'),
        ("Is Born-Digital PDF?", 4.0, 6.9, 'decision'),
        ("Extract Native PDF Stream", 2.0, 6.0, 'action'),
        ("Run Orientation & Hybrid OCR", 6.0, 6.0, 'action'),
        ("Detect Document Language", 4.0, 5.0, 'action'),
        ("Uncertain Word Spans Detected?", 4.0, 4.1, 'decision'),
        ("Route to Human Review UI", 6.2, 3.2, 'action'),
        ("Extract Six Canonical Fields", 4.0, 2.3, 'action'),
        ("Verify Evidence Grounding", 4.0, 1.4, 'action'),
        ("Generate Checklist & ICS Calendar", 4.0, 0.6, 'action'),
    ]

    for text, x, y, kind in steps:
        if kind == 'action':
            box = patches.FancyBboxPatch((x - 1.4, y - 0.28), 2.8, 0.56, boxstyle="round,pad=0.08,rounding_size=0.1",
                                         facecolor='#eff6ff', edgecolor='#1e40af', lw=1.2)
            ax.add_patch(box)
            ax.text(x, y, text, ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1e3a8a')
        elif kind == 'decision':
            # Diamond
            diamond = patches.Polygon([[x, y + 0.35], [x + 1.3, y], [x, y - 0.35], [x - 1.3, y]],
                                      facecolor='#fef08a', edgecolor='#a16207', lw=1.2)
            ax.add_patch(diamond)
            ax.text(x, y, text, ha='center', va='center', fontsize=7, fontweight='bold', color='#854d0e')

    # Connectors
    arr = dict(arrowstyle="->", color="#0284c7", lw=1.2, mutation_scale=10)
    ax.annotate("", xy=(4.0, 8.08), xytext=(4.0, 8.32), arrowprops=arr)
    ax.annotate("", xy=(4.0, 7.25), xytext=(4.0, 7.52), arrowprops=arr)

    # Born Digital Branch
    ax.annotate("", xy=(2.0, 6.28), xytext=(3.0, 6.9), arrowprops=arr)
    ax.text(2.3, 6.75, "Yes", fontsize=7.5, fontweight='bold', color='#047857')

    ax.annotate("", xy=(6.0, 6.28), xytext=(5.0, 6.9), arrowprops=arr)
    ax.text(5.5, 6.75, "No (Image/Scan)", fontsize=7.5, fontweight='bold', color='#b91c1c')

    # Merge to language
    ax.annotate("", xy=(3.8, 5.28), xytext=(2.0, 5.72), arrowprops=arr)
    ax.annotate("", xy=(4.2, 5.28), xytext=(6.0, 5.72), arrowprops=arr)

    # Language -> Uncertain decision
    ax.annotate("", xy=(4.0, 4.45), xytext=(4.0, 4.72), arrowprops=arr)

    # Uncertain branch
    ax.annotate("", xy=(6.2, 3.48), xytext=(5.0, 4.1), arrowprops=arr)
    ax.text(5.7, 3.95, "Yes (Spans < 65%)", fontsize=7, fontweight='bold', color='#b91c1c')

    ax.annotate("", xy=(4.0, 2.58), xytext=(4.0, 3.75), arrowprops=arr)
    ax.text(4.15, 3.4, "No", fontsize=7.5, fontweight='bold', color='#047857')

    # Human Review back to extract
    ax.annotate("", xy=(4.8, 2.45), xytext=(6.2, 2.92), arrowprops=arr)

    # Extract -> Grounding -> Checklist
    ax.annotate("", xy=(4.0, 1.68), xytext=(4.0, 2.02), arrowprops=arr)
    ax.annotate("", xy=(4.0, 0.88), xytext=(4.0, 1.12), arrowprops=arr)

    plt.tight_layout()
    dest = os.path.join(DIAGRAMS_DIR, "fig_4_7_activity_diagram.png")
    plt.savefig(dest, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Generated activity diagram at: {dest}")

if __name__ == "__main__":
    generate_logo_placeholder()
    generate_architecture_diagram()
    generate_use_case_diagram()
    generate_dfd_level_0()
    generate_dfd_level_1()
    generate_er_diagram()
    generate_sequence_diagram()
    generate_activity_diagram()
    print("All diagrams and assets successfully created!")
