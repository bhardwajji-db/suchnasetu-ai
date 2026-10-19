# Notice2Action AI — 3-Minute Demonstration Script

**Event:** Hacktoberfest 2026 HackDay@Meerut × E-Cell IIMT University  
**Track:** Best Use of Gemma 4 (PS02 — Notice-to-Action Accessibility Assistant)  
**Presenter:** Single-Developer Hackathon Pitch  
**Target Duration:** Exactly 3 Minutes  

---

## Preparation Before Demo

1. Ensure Ollama is running:
   ```powershell
   ollama list
   ```
   (Verify `gemma4:latest` is listed).
2. Launch the application:
   ```powershell
   .\scripts\run.ps1
   ```
3. Open browser to `http://localhost:8501`.
4. Ensure the sidebar indicates **🟢 System Ready (Gemma 4 & OCR Live)**.

---

## 3-Minute Presentation Walkthrough

### Minute 1: The Problem & Ingestion (0:00 – 1:00)

**Spoken Intro (30s):**
> *"Judges, college students and citizens are constantly bombarded with dense, poorly formatted circulars, scholarship announcements, and poster PDFs. Crucial details like deadlines, eligibility rules, and required documents get lost in the noise. For students with accessibility challenges or language barriers, missing a deadline can cost them their degree or scholarship.*
> *This is Notice2Action AI: a local-first, privacy-respecting accessibility assistant powered by Google's Gemma 4 that transforms messy notices into verified, accessible action checklists."*

**Action (30s):**
1. Click **Sample 1: Scholarship Notice (Full)** in the sidebar.
2. Show the text loaded into the editable box in **Tab 1: Notice Ingestion & OCR**.
3. Point out: *"The user can upload a photo, scan, or paste text. They can inspect and correct any OCR errors right here before running the AI."*
4. Click **🚀 Analyze Notice with Gemma 4**.

---

### Minute 2: Grounded Facts & Evidence Verification (1:00 – 2:00)

**Spoken Explanation (30s):**
> *"Unlike ordinary chatbots that hallucinate or make assumptions, Notice2Action AI runs our custom Evidence Grounding Engine on top of Gemma 4."*

**Action (30s):**
1. Switch to **Tab 2: Grounded Fact Breakdown**.
2. Highlight the 8 structured fact cards:
   - **Purpose:** Stated with verbatim quote from the text.
   - **Eligibility:** 75% marks & family income under Rs. 5,00,000.
   - **Deadline:** 15 November 2026 (exact line number shown).
   - **Fee:** Stated as Rs. 0 (Free).
   - **Required Documents:** Marksheets, Income Certificate, ID Card.
3. Point out the line citation: *"Notice that every single fact displays its exact verbatim quotation and line number. If a date or amount was altered by even one digit, our engine flags it as conflicting."*

---

### Minute 3: Accessibility, Hindi Mode, and Truthful Limits (2:00 – 3:00)

**Action & Spoken (60s):**
1. Switch to **Tab 3: Summary & Action Checklist**:
   - Show the 7 core questions answered concisely: *"What is this about? Who is eligible? What must I do? What documents? What deadline? Where to get help? What's missing?"*
   - Click the **🔊 Audio Read Aloud** button to demonstrate accessibility for visually impaired users.
   - Switch language to **हिन्दी (Hindi)** in the sidebar:
     - Show the summary and checklist seamlessly rendered in Hindi.
     - Highlight: *"Notice that the critical numbers—15 November 2026, 75%, Rs. 5,00,000—are strictly preserved without translation corruption."*
2. Switch to **Tab 4: Follow-Up Q&A**:
   - Click the suggested question: **"Can I submit late?"**
   - Click **Ask Assistant**.
   - Show the assistant's truthful response:
     > *"The supplied notice does not specify whether late submission is allowed. Please confirm with the official contact."*
   - Highlight: *"Judges, the AI refused to invent a late submission policy because it was not in the notice. It correctly guided the student to the official contact."*

**Closing (15s):**
> *"Notice2Action AI runs 100% locally on Gemma 4, requires zero cloud APIs, protects student privacy, and ensures no student ever misses a deadline again. Thank you!"*

---

## Backup Plan If Live Inference Is Paused
If the local machine is offline or Ollama is stopped during a live presentation:
- The app displays an actionable warning in the sidebar diagnostics.
- The unit test suite demonstrates all 24 deterministic test cases passing in under 3 seconds:
  ```powershell
  .\scripts\test.ps1
  ```
