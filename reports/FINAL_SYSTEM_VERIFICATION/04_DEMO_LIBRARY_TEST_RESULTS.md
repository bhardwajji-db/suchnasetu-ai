# 04 — DEMO LIBRARY TEST RESULTS & CATALOG VERIFICATION
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** PS02 (Hack Day 2026)  
**Verification Date:** 2026-10-24  

---

## 1. Demo Library Overview

A persistent, searchable library of **32 authentic synthetic demo notices** has been generated and validated in `tests/fixtures/demo_library/` accompanied by `manifest.json`.

Every notice is accessible via:
1. **Frontend Demo Library Tab (Tab 11 - BookOpen icon):** Interactive gallery with search, category filters, and language filters.
2. **Backend API Endpoint (`/api/demo-library` and `/api/demo-library/load`):** Deterministic retrieval and immediate ingestion into the active analysis session.

---

## 2. Catalog & Verification Matrix (32 Notices)

| Demo ID | Notice Title | Category | Lang | Format | Key Field Verified | Ingestion Status |
|---|---|---|---|---|---|---|
| `demo_01_scholarship` | National Merit Post-Matric Scholarship 2026 | Scholarship | `en` | `.txt` | Deadline: 15 Nov 2026 | **PASS** |
| `demo_02_hostel_circular` | University Central Hostel Maintenance | Circular | `en` | `.txt` | Vacate: 30 June 2026 | **PASS** |
| `demo_03_corrigendum` | Smart City Project Corrigendum No. 3 | Corrigendum | `en` | `.txt` | Bid Extended: 28 Nov 2026 | **PASS** |
| `demo_04_bilingual_municipal` | Property Tax Rebate Notification 2026 | Municipal | `hi` | `.txt` | Rebate: 10%, Due: 20 Nov 2026 | **PASS** |
| `demo_05_flood_relief` | DDMA Emergency Flood Relief Operations | Disaster | `en` | `.txt` | Ration relief & DDMA authority | **PASS** |
| `demo_06_scheme_hi` | प्रधानमंत्री ग्रामीण आवास योजना लाभार्थी सूची | Scheme | `hi` | `.txt` | किश्त राशि: ₹1,20,000 | **PASS** |
| `demo_07_admission_bn` | পশ্চিমবঙ্গ রাজ্য বিশ্ববিদ্যালয় স্নাতকোত্তর ভর্তি | Admission | `bn` | `.txt` | শেষ তারিখ: ২৫ নভেম্বর ২০২৬ | **PASS** |
| `demo_08_recruitment_ta` | தமிழ்நாடு அரசுப் பணியாளர் தேர்வாணையம் | Jobs | `ta` | `.txt` | விண்ணப்பிக்க கடைசி நாள் | **PASS** |
| `demo_09_tender_te` | ఆంధ్రప్రదేశ్ రహదారుల అభివృద్ధి టెండర్ | Tender | `te` | `.txt` | చివరి తేదీ: డిసెంబర్ 10 | **PASS** |
| `demo_10_municipal_mr` | बृहन्मुंबई महानगरपालिका जल आकारणी परिपत्रक | Municipal | `mr` | `.txt` | देयक मुदत: १५ डिसेंबर २०२६ | **PASS** |
| `demo_11_exam_gu` | ગુજરાત ગૌણ સેવા પસંદગી મંડળ પરીક્ષા | Exam | `gu` | `.txt` | પરીક્ષા તારીખ: 0૫ ડિસેમ્બર | **PASS** |
| `demo_12_subsidy_pa` | ਪੰਜਾਬ ਖੇਤੀਬਾੜੀ ਸਬਸਿਡੀ ਯੋਜਨਾ ਨੋਟਿਸ | Agriculture| `pa` | `.txt` | ਅੰਤਿਮ ਮਿਤੀ: ੩੦ ਨਵੰਬਰ | **PASS** |
| `demo_13_scholarship_kn`| ಕರ್ನಾಟಕ ಈ-ਪಾಸ್ ವಿದ್ಯಾರ್ಥಿವೇತನ ಪ್ರಕಟಣೆ | Scholarship| `kn` | `.txt` | ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಕೊನೆಯ ದಿನಾಂಕ | **PASS** |
| `demo_14_relief_ur` | ریلیف اور بحالی کمیٹی کا خصوصی نوٹس | Welfare | `ur` | `.txt` | آخری تاریخ: 10 دسمبر 2026 | **PASS** |
| `demo_15_docx_admission`| All India Entrance Test Instructions 2026| Entrance | `en` | `.docx`| Exam Center reporting 08:30 AM| **PASS** |
| `demo_16_png_circular` | Municipal Public Health Advisory 2026 | Health | `en` | `.png` | Sanitation checklist steps | **PASS** |
| `demo_17_jpg_corrigendum`| Road Transport Authority Fee Revision | Fee | `en` | `.jpg` | Revised late fee ₹500 | **PASS** |
| `demo_18_webp_admit_card`| Polytechnic Diploma Admit Card Release | Exam | `hi` | `.webp`| परीक्षा केंद्र प्रवेश समय | **PASS** |
| `demo_19_tiff_multipage` | District Revenue Land Settlement Record| Revenue | `en` | `.tif` | Land survey records | **PASS** |
| `demo_20_scanned_pdf` | Forest Department Guard Recruitment | Jobs | `hi` | `.pdf` | शारीरिक दक्षता परीक्षा | **PASS** |
| `demo_21_high_ambiguity` | Public Works Drainage Maintenance Notice| Tender | `en` | `.txt` | "within 15 days of rains" | **PASS** |
| `demo_22_conflicting_dates`| Technical University Mid-Semester Exams | Academic | `en` | `.txt` | Conflicting 12th vs 14th date | **PASS** |
| `demo_23_missing_fee` | Solar Rooftop Subsidy Application 2026| Renewable | `en` | `.txt` | Subsidy 40%, Fee Unstated | **PASS** |
| `demo_24_adversarial_jail`| Flood Relief Notice with Hidden DAN | Security | `en` | `.txt` | Injection neutralized | **PASS** |
| `demo_25_original_tender`| Central Library Digitization RFQ (Base) | Tender | `en` | `.txt` | EMD: ₹25,000, Due: 10 Nov | **PASS** |
| `demo_26_revised_tender` | Central Library Digitization Corrigendum | Corrigendum| `en` | `.txt` | EMD: ₹15,000, Due: 25 Nov | **PASS** |
| `demo_27_eligibility_msme`| National Handicrafts Artisan Grant | Grants | `hi` | `.txt` | कारीगर पहचान पत्र एवं कोटा | **PASS** |
| `demo_28_hearing_notice` | National Green Tribunal Public Hearing | Hearing | `en` | `.txt` | Virtual Hearing: 02 Dec 2026 | **PASS** |
| `demo_29_college_hostel` | Girls Hostel Curfew & Mess Dues Circular| Hostel | `en` | `.txt` | Mess payment by 5th Nov | **PASS** |
| `demo_30_internship` | National Informatics Centre AI Internships| Internship | `en` | `.txt` | Stipend ₹25,000 / month | **PASS** |
| `demo_31_safety_fire` | Industrial Estate Fire Safety Audit | Safety | `mr` | `.txt` | अग्निशामक यंत्रे तपासणी | **PASS** |
| `demo_32_scheme_bilingual`| Krishi Sinchayee Yojana Farmer Circular | Agriculture| `hi` | `.txt` | अनुदान ५०%, जल संरक्षण | **PASS** |

---

## 3. Automated Manifest & Ingestion Verification
- **Test:** `tests/test_demo_library.py` (5/5 passed)
- **Test:** `tests/test_demo_library_api.py` (6/6 passed)
- **Integrity Verified:** All 32 file paths exist, are non-empty, match declared metadata, and load seamlessly into the notice buffer.
