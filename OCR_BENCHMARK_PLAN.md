# SochnaSetu AI — Universal Multilingual OCR Benchmark & Empirical Evaluation Plan

**Document Version:** 1.0.0  
**Design Date:** November 24, 2026  
**Author:** Principal QA Automation, OCR Evaluation & Benchmark Specialist  
**Repository Path:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**Target Scope:** Reproducible 23-Language Benchmark Protocol (22 Scheduled Languages + English)  
**Status:** PROPOSED EVALUATION SPECIFICATION (AUDIT & DESIGN ONLY)

---

## 1. Executive Summary & Benchmark Mandate

To transition SochnaSetu AI from bilingual (English/Hindi) to universal 22-language Indic support, engineering decisions must be grounded in **rigorous, reproducible empirical measurements**. Advertised accuracy claims from model creators cannot be trusted without direct validation against real-world Indian administrative circulars, gazettes, and university notifications.

This document outlines the master benchmark methodology, dataset curation strategy, perturbation pipeline, quantitative metrics, and execution protocol designed to evaluate candidate OCR engines against verifiable ground-truth transcripts.

---

## 2. Benchmark Dataset Architecture

The benchmark corpus will comprise **230 standardized test documents** spanning all 22 Eighth Schedule languages and English (10 documents per language):

```
                                  [Master Benchmark Corpus]
                                    (230 Total Documents)
                                              │
                     ┌────────────────────────┴────────────────────────┐
                     ▼                                                 ▼
          [Set A: Clean Printed Notices]                   [Set B: Degraded Scans]
             (5 Documents per Language)                   (5 Documents per Language)
             - High-resolution (300 DPI)                  - Low-resolution (150 DPI)
             - Standard government circulars              - Skewed (±7.0° tilt)
             - Exact ground-truth Unicode text            - Rotated (90°, 180°, 270°)
             - Tabular schedules & dates                  - Mobile camera shadow gradients
```

### 2.1 Domain Sampling Distribution per Language
1. **Academic Notice:** Semester examination schedule or university fee payment circular.
2. **Statutory Corrigendum:** Official gazette corrigendum amending earlier notice numbers or dates.
3. **Public Welfare / Scholarship Circular:** Social welfare grant with eligibility cutoffs and caste/income criteria.
4. **Recruitment Notification:** Public service commission notice with vacancy tables and age relaxations.
5. **Municipal / Civic Advisory:** Water supply, voter list revision, or public utility advisory.

---

## 3. Quantitative Evaluation Metrics

All benchmark runs must record five standardized mathematical metrics:

### 3.1 Character Error Rate (CER)
Computed via exact Levenshtein edit distance at the Unicode character level:
$$\text{CER} = \frac{S + D + I}{N} \times 100\%$$
Where:
- $S$ = Character Substitutions (e.g. `1` misread as `।`, or `े` misread as `ी`)
- $D$ = Character Deletions (e.g. missing vowel matras, dropped nukta)
- $I$ = Character Insertions (e.g. noise artifacts read as commas or apostrophes)
- $N$ = Total characters in ground-truth transcript

### 3.2 Word Error Rate (WER)
Computed at whitespace-delimited word tokens:
$$\text{WER} = \frac{S_w + D_w + I_w}{N_w} \times 100\%$$

### 3.3 Critical Entity Exact Match Rate (CEMR)
Measures whether key operational data required by civic users is transcribed with 100% precision:
- **Notice Dates & Deadlines:** Strict regular expression match (`DD/MM/YYYY`, `DD-MM-YYYY`).
- **Monetary Amounts & Fees:** Exact numeric currency string (e.g. `₹1,200`, `Rs. 500`).
- **Notice Reference Numbers:** Exact alpha-numeric identifier (e.g. `No. 12/4/2026-Exam`).
- **Contact Helplines & Emails:** Exact telephone and email strings.

### 3.4 Tabular & Layout Preservation Score
Measures whether multi-column table data is segmented in correct reading order without horizontally merging adjacent column cells.

### 3.5 System Performance & Profiling Metrics
- **End-to-End Latency:** Wall-clock time (seconds per page).
- **Peak Resident Memory (RAM):** Profiled via Python `tracemalloc`.
- **Peak VRAM:** GPU memory allocation (if CUDA acceleration is enabled).

---

## 4. Adversarial Perturbation Pipeline

To simulate real-world document degradation, test images will be subjected to automated, deterministic perturbations built upon the existing `tests/adversarial_ocr/` harness:

| Perturbation Class | Applied Transformation | Real-World Simulation |
| :--- | :--- | :--- |
| **Skew Distortion** | Affine rotation by $+7.0^\circ$ and $-7.0^\circ$ | Flatbed scanner misalignment |
| **Orientation Inversion**| Rotated $90^\circ$ CW, $180^\circ$ upside-down, $270^\circ$ CCW | Mobile upload with missing EXIF metadata |
| **Luminance Gradient** | Linear diagonal shadow mask ($1.0 \to 0.25$ factor) | Mobile photo taken under uneven fluorescent lighting |
| **Gaussian Blur** | Blur radius $\sigma = 1.2$ | Out-of-focus phone camera lens |
| **JPEG Compression** | Re-compressed at quality $Q = 35$ | Highly compressed WhatsApp circular forwards |
| **Resolution Downscale**| Downsampled to 120 DPI and upscaled | Photocopy-of-a-photocopy circular |

---

## 5. Execution Protocol & Tooling Integration

The evaluation will be implemented as a standardized Python CLI harness:

```powershell
# Proposed benchmark command (Audited specification)
python -m tests.benchmarks.universal_ocr_runner \
    --languages all \
    --engines tesseract,indicocr,paddleocr \
    --output reports/UNIVERSAL_OCR_BENCHMARK_RESULTS.json \
    --workers 4
```

### 5.1 Protocol Flow
1. **Harness Initialization:** Pre-flight check verifying engine binaries, weights, and test fixtures.
2. **Worker Pool Spawning:** Executes across 4 CPU worker processes, processing documents in parallel.
3. **Dual Metric Logging:** Computes both unnormalized and Unicode NFC normalized CER/WER.
4. **Side-by-Side Delta Recording:** Generates an automated Markdown report comparing candidate engines on identical document inputs.

---

## 6. Strict Anti-Regression Guardrails

Before any new multilingual engine or model is approved for integration into SochnaSetu AI's production pipeline, it must pass three mandatory regression gates:

1. **Gate 1 (Gazette Administrative Benchmark):**
   - Corrigendum S.O. 1364(E) CER must remain **$\le 2.75\%$**.
   - Critical entities (Date `28 अप्रैल 2017`, Notice number) must maintain **100% exact match**.
2. **Gate 2 (English Administrative Benchmark):**
   - Category A notices (`A01`–`A06`) Macro CER must remain **$\le 3.50\%$**.
3. **Gate 3 (Hindi Degraded Benchmark):**
   - Category E complex scans (`E01`–`E11`) Macro CER must remain **$\le 13.00\%$**.

*Any model that improves regional languages but causes regression on English or Hindi documents will be rejected.*
