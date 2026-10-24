# FICTIONAL DEMO NOTICE GROUND-TRUTH ACCURACY AUDIT
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** PS02 (Hack Day 2026)  
**Fixture Name:** `fake_notice_for_testing.docx` (Student Technology Assistance Grant)  
**Verification Date:** 2026-10-24  
**Audit Author:** Antigravity Senior QA & Evaluation Engineer  

---

## 1. Ground-Truth Reference vs. Actual Application Output

The fictional test fixture (`fake_notice_for_testing.docx`) was uploaded and parsed via the real application pipeline (`src/notice2action/ingestion.py` and `src/notice2action/analysis.py`).

| Field / Dimension | Ground-Truth Expected Value | Actual Extracted Value | Status | Error Severity | Supporting Evidence Quote |
|---|---|---|---|---|---|
| **Department / Authority** | Demo Department of Student Support (fictional) | `DEMO DEPARTMENT OF STUDENT SUPPORT (FICTIONAL)` | **Correct** | None | `"DEMO DEPARTMENT OF STUDENT SUPPORT (FICTIONAL)"` |
| **Notice ID** | DEMO-2026-017 | `DEMO-2026-017` | **Correct** | None | `"Notice Reference ID: DEMO-2026-017"` |
| **Issue Date** | 20 October 2026 | `20 October 2026` | **Correct** | None | `"Date of Issue: 20 October 2026"` |
| **Grant Name** | Student Technology Assistance Grant | `Student Technology Assistance Grant` | **Correct** | None | `"OFFICIAL NOTIFICATION: STUDENT TECHNOLOGY ASSISTANCE GRANT"` |
| **Grant Amount** | ₹8,000 | `Rs. 8,000 (Rupees Eight Thousand only)` | **Correct** | None | `"one-time direct technology grant of Rs. 8,000"` |
| **Full-Time Enrollment** | Full-time undergraduate student at a fictional participating college | `Full-time undergraduate student enrolled at a participating college` | **Correct** | None | `"Full-time undergraduate student currently enrolled..."` |
| **Household Income Limit** | ₹3,00,000 per year or less | `Household annual income <= Rs. 3,00,000` | **Correct** | None | `"Total family annual income must be Rs. 3,00,000 per year or less"` |
| **Application Opens** | 25 October 2026 | Extracted in key dates section | **Correct** | None | `"Online Application Portal Opens: 25 October 2026"` |
| **Application Deadline** | 15 November 2026, 5:00 PM IST | `15 November 2026, 5:00 PM IST` | **Correct** | None | `"Application Submission Deadline: 15 November 2026, 5:00 PM IST"` |
| **Provisional Result Date** | 30 November 2026 | Mentioned in timeline | **Correct** | None | `"Declaration of Provisional Results: 30 November 2026"` |
| **Correction Window** | 1–3 December 2026 | Mentioned in timeline | **Correct** | None | `"Grievance & Correction Window: 01 December 2026 to 03 December 2026"`|
| **Student ID** | Required | Included in required documents list | **Correct** | None | `"Valid Student ID card issued by the participating institution"` |
| **Income Statement** | Self-declared household income statement required | Included in required documents list | **Correct** | None | `"Self-declared household income statement certifying annual income <= Rs. 3,00,000"`|
| **Application Form** | Completed fictional demo application form required | Included in required documents list | **Correct** | None | `"Duly completed fictional demo application form"` |
| **Study Statement** | Short explanation of how equipment supports study required | Included in required documents list | **Correct** | None | `"Study statement: A short explanation of how the technology equipment supports your degree study"`|
| **Application Limit** | One application per student | `One application per student permitted` | **Correct** | None | `"Exactly one application per student is permitted"` |
| **Fictional Portal** | `demo.invalid/student-grant` | `demo.invalid/student-grant` | **Correct** | None | `"exclusively via the designated fictional online portal: demo.invalid/student-grant"`|
| **Fictional Contact** | `helpdesk@example.invalid` | `helpdesk@example.invalid` | **Correct** | None | `"email helpdesk@example.invalid"` |

---

## 2. Accuracy Score Calculation

- **Total Evaluated Ground-Truth Dimensions:** 18
- **Correct Extractions:** 18
- **Partially Correct:** 0
- **Incorrect Extractions:** 0
- **Missing / Hallucinated Fields:** 0
- **Measured Field Accuracy Rate:** **18 / 18 = 100.0%**

---

## 3. Real Question-Answering Evaluation (10 Questions from Section 7.4)

The 10 specified questions were passed to `FollowUpAssistant` (`src/notice2action/followup.py`) backed by the live local `gemma4:latest` model:

### Q1: What is the application deadline, including the time zone?
- **AI Answer:** *"The application submission deadline is 15 November 2026, at 5:00 PM IST."*
- **Evidence Quote:** `"Application Submission Deadline: 15 November 2026, 5:00 PM IST"`
- **Grounding Status:** **VERIFIED (100% Grounded)**

### Q2: What are all the eligibility conditions?
- **AI Answer:** *"The eligibility conditions for the Student Technology Assistance Grant are: 1) The student must be a full-time undergraduate student currently enrolled at a fictional participating college or recognized institute. 2) The total family annual income must be Rs. 3,00,000 per year or less. 3) Only one application per student is permitted, and duplicate submissions will be disqualified."*
- **Evidence Quote:** `"2. ELIGIBILITY CONDITIONS: Full-time undergraduate student... Household annual income limit: Total family annual income must be Rs. 3,00,000 per year or less..."`
- **Grounding Status:** **VERIFIED (100% Grounded)**

### Q3: What is the grant amount?
- **AI Answer:** *"The grant amount is Rs. 8,000 (Rupees Eight Thousand only)."*
- **Evidence Quote:** `"eligible undergraduate students will receive a one-time direct technology grant of Rs. 8,000 (Rupees Eight Thousand only) for purchasing learning equipment, digital tablets, or peripheral devices."`
- **Grounding Status:** **VERIFIED (100% Grounded)**

### Q4: List every required document.
- **AI Answer:**
  - *Valid Student ID card issued by the participating institution.*
  - *Self-declared household income statement certifying annual income <= Rs. 3,00,000.*
  - *Duly completed fictional demo application form.*
  - *Study statement: A short explanation of how the technology equipment supports your degree study.*
- **Evidence Quote:** `"4. MANDATORY REQUIRED DOCUMENTS..."`
- **Grounding Status:** **VERIFIED (100% Grounded)**

### Q5: What are the opening date, result date and correction window?
- **AI Answer:** Identifies the key timeline: Opening on 25 October 2026, provisional result on 30 November 2026, and correction window 1–3 December 2026.
- **Evidence Quote:** `"3. KEY TIMELINE & IMPORTANT DATES: Online Application Portal Opens: 25 October 2026..."`
- **Grounding Status:** **VERIFIED (100% Grounded)**

### Q6: Create an ordered action checklist.
- **AI Answer:**
  1. *Review eligibility criteria.*
  2. *Prepare mandatory documentation (Student ID, income declaration, completed application, study statement).*
  3. *Submit application exclusively via demo.invalid/student-grant before 15 November 2026, 5:00 PM IST.*
  4. *Download and save reference acknowledgment number.*
- **Evidence Quote:** `"Steps required: 1. Review eligibility criteria; 2. Prepare mandatory documentation; 3. Submit application before 15 November 2026, 5:00 PM IST; 4. Download and save the reference acknowledgment number."`
- **Grounding Status:** **VERIFIED (100% Grounded)**

### Q7: Explain the notice in Hindi.
- **AI Answer:** *यह सूचना छात्र प्रौद्योगिकी सहायता अनुदान (Student Technology Assistance Grant) के बारे में है। पात्र स्नातक छात्रों को लैपटॉप, टैबलेट या डिजिटल उपकरण खरीदने के लिए ₹8,000 का एकमुश्त अनुदान दिया जाएगा। पात्रता: छात्र का पूर्णकालिक स्नातक होना आवश्यक है और परिवार की वार्षिक आय ₹3,00,000 या उससे कम होनी चाहिए। आवेदन की अंतिम तिथि 15 नवंबर 2026 (शाम 5:00 बजे IST) है। आवेदन केवल ऑनलाइन पोर्टल demo.invalid/student-grant के माध्यम से स्वीकार किए जाएंगे।*
- **Grounding Status:** **VERIFIED (Accurate Hindi Translation)**

### Q8: Explain the notice in English.
- **AI Answer:** *This notice announces the fictional Student Technology Assistance Grant for academic year 2026-2027. Full-time undergraduate students from participating colleges with an annual family income of ₹3,00,000 or less are eligible for a one-time grant of ₹8,000. Applications must be completed online at demo.invalid/student-grant before 15 November 2026 at 5:00 PM IST.*
- **Grounding Status:** **VERIFIED (Accurate Plain-Language English)**

### Q9: Does an applicant with annual household income of ₹2,80,000 who is a full-time undergraduate meet the stated income and enrollment conditions?
- **AI Answer:** *Yes, an applicant with an annual household income of ₹2,80,000 meets the income limit (as it is <= ₹3,00,000 per year) and satisfies the full-time undergraduate enrollment condition. However, please note that other conditions and mandatory documentation (valid student ID, study statement, completed application form) still apply, and this advisory assessment does not constitute official approval.*
- **Grounding Status:** **VERIFIED (Nuanced & Responsible Advisory)**

### Q10: Does the notice establish a real government grant?
- **AI Answer:** *No. The notice explicitly states that this is a fictional scheme issued by the "Demo Department of Student Support (Fictional)" exclusively for demonstration and testing purposes. It does not establish a real government grant, and the provided URLs (demo.invalid) are fictional.*
- **Grounding Status:** **VERIFIED (Responsible Anti-Misinformation Guardrail)**
