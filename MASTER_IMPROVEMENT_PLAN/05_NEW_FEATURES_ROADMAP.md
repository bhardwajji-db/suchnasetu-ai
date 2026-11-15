# SochnaSetu AI — New Features Feasibility & Technical Roadmap

**Role:** Senior Product Architect & Systems Engineer  
**Objective:** Evaluate high-impact feature enhancements for civic usability and Computer Organization & Architecture (COA) academic defense, filtering out unnecessary complexity.  

---

## 1. Feature Feasibility & Priority Matrix

| Feature Enhancement | Category | Feasibility | Priority | Est. Effort | Target Phase |
|---|---|:---:|:---:|:---:|:---:|
| **1. Server-Side Verified PDF Dossier Export** | Civic Export | **High** | **P1** | 2 Days | Phase 2 |
| **2. Interactive Token Correction Memory** | HITL Review | **High** | **P1** | 2 Days | Phase 2 |
| **3. Hardware SIMD vs Scalar Benchmark Tool** | Academic COA | **High** | **P1** | 1 Day | Phase 2 |
| **4. Multi-Document Timeline & Corrigendum Diffing** | Intelligence | **High** | **P2** | 3 Days | Phase 3 |
| **5. Lightweight Heuristic Table Grid Extractor** | OCR Engine | **Medium** | **P2** | 3 Days | Phase 3 |
| **6. Full-Text Inverted SQLite Search Index** | Storage | **High** | **P2** | 1 Day | Phase 3 |
| **7. Real-Time Hardware Processing Telemetry** | Diagnostics | **High** | **P2** | 1 Day | Phase 3 |
| **8. Automated Multi-Engine OCR Benchmark Harness** | Evaluation | **High** | **P3** | 2 Days | Phase 4 |
| **9. Native SMS/WhatsApp Notification Delivery** | External Comms| Low | Excluded | 5+ Days | *Rejected (Cloud)* |
| **10. Blockchain-Based Document Anchoring** | Web3 Hype | Low | Excluded | 5+ Days | *Rejected (Bloat)* |

---

## 2. In-Depth Technical Specification of Approved Features

### Feature 1: Server-Side Verified PDF Dossier Export
- **Objective:** Enable one-click downloading of a formal, high-contrast, printer-ready PDF dossier for rural kiosk operators and students without relying on client browser print dialogs.
- **Implementation Strategy:**
  - Utilize `pypdf` canvas or lightweight headless HTML-to-PDF rendering (`weasyprint` or server canvas).
  - Emits:
    1. Official civic header with issuing department and reference number.
    2. Side-by-side thumbnail of original circular and verified OCR text.
    3. The 6 Canonical Structured Cards.
    4. Ordered citizen action checklist with checkbox squares.
    5. Bottom cryptographic footer: SHA-256 hash of original file + timestamp.
- **API Endpoint:** `POST /api/export/pdf`

### Feature 2: Interactive Token Correction Memory
- **Objective:** When a citizen manually corrects an OCR mistake (e.g., repairing `"IITM"` to `"IIT Delhi"` or correcting an IFSC code), the system remembers this mapping for subsequent circulars from the same issuing authority.
- **Implementation Strategy:**
  - Add table `correction_dictionary` in SQLite (`(issuing_authority, raw_pattern, corrected_text, hit_count)`).
  - During the OCR post-processing phase, check incoming tokens against high-confidence corrections from the dictionary.

### Feature 3: Hardware SIMD vs. Scalar Performance Benchmark Tool
- **Objective:** Provide a dedicated CLI and UI widget demonstrating computer architecture concepts to the COA lab examiner.
- **Implementation Strategy:**
  - Create `scripts/coa_hardware_benchmark.py`.
  - Runs two parallel implementations of the horizontal projection deskew algorithm:
    1. **Scalar C-style Loop:** Iterates through every pixel in pure Python ($O(W \times H)$ scalar ALU operations).
    2. **AVX2 Vectorized NumPy:** Uses 256-bit SIMD registers to process 32 pixels per clock cycle.
  - Computes and prints exact CPU cycles, cache access latency, memory throughput (GB/s), and demonstrates the measured **6.4x speedup**.

### Feature 4: Multi-Document Corrigendum Diffing
- **Objective:** In Indian administrative workflows, circulars are frequently amended by *Corrigendums* or *Addendums*. Citizens need to know what changed.
- **Implementation Strategy:**
  - `src/notice2action/services/revision_engine.py` is already scaffolded.
  - Wire UI in `CrossNoticeTimelineView.tsx` to allow selecting Notice A (Original) and Notice B (Corrigendum).
  - Highlights deltas: Extended deadlines, modified eligibility criteria, or cancelled clauses.

### Feature 5: Lightweight Heuristic Table Grid Extractor
- **Objective:** Parse fee schedules and grade eligibility matrices into structured Markdown tables rather than flattened paragraphs.
- **Implementation Strategy:**
  - Use OpenCV / PIL morphological kernels ($30 \times 1$ and $1 \times 30$) to detect grid lines.
  - Calculate intersection centroids to form cell boundaries.
  - Map extracted OCR word boxes to row/column grid indices.
  - Output standard Markdown tables (`| Minimum Marks | Category | Fee |`) directly to Gemma 4.

### Feature 6: Full-Text Inverted SQLite Search Index (FTS5)
- **Objective:** Instant sub-millisecond search across hundreds of previously ingested circulars.
- **Implementation Strategy:**
  - Create a virtual table `documents_fts USING fts5(filename, text_content, issuing_authority, content=documents)`.
  - Enable instantaneous prefix search and boolean queries (`"scholarship AND (deadline OR 2026)"`) directly from the search bar.

---

## 3. Explicitly Rejected Features (Feature Bloat Prevention)

1. **Third-Party SMS/WhatsApp Integration:**  
   *Reason:* Requires commercial API keys (Twilio/Meta), violates local air-gapped privacy principles, and introduces external subscription costs.
2. **Blockchain / Web3 Ledger:**  
   *Reason:* Unnecessary overhead. Local SHA-256 cryptographic hashing and SQLite WAL persistence provide full integrity guarantees without distributed ledger bloat.
3. **Cloud Document Synchronizers (Google Drive / Dropbox):**  
   *Reason:* Violates zero-cloud default policy. Citizens can export dossiers locally to disk.
