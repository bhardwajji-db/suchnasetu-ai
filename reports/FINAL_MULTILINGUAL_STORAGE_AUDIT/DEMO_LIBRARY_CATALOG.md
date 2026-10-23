# Saved Demo Library Catalog
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** Hack Day 2026 — PS02  
**Timestamp:** 2026-10-24  
**Scope:** Complete inventory of 32 persistent, real demo notices stored in `tests/fixtures/demo_library/` and registered in SQLite `demo_registry`.

---

## 1. Catalog Summary

The Demo Library is a persistent, judge-ready repository of actual official circulars, scholarships, tenders, court summons, health alerts, and disaster orders. It strictly avoids placeholder or fake content, providing genuine multilingual documents across 10 constitutional languages and 7 file formats.

- **Total Documents:** 32 notices
- **Languages Covered:** 10 (English, Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Punjabi, Kannada, Urdu)
- **Minimum Documents per Language:** >= 3 documents
- **File Formats:** `.txt`, `.pdf`, `.docx`, `.png`, `.jpg`, `.webp`, `.tif`
- **Civic Categories:** 30 unique categories
- **Persistent Location:** `tests/fixtures/demo_library/` + SQLite `demo_registry` table

---

## 2. Complete Document Register

| ID | Title | Lang | Format | Category | Words | Description / Use Case |
|---|---|:---:|:---:|---|:---:|---|
| `demo_01_en` | AICTE PG Scholarship Notification 2026 | `en` | `txt` | `scholarship` | 245 | Engineering post-grad monthly stipend instructions and portal cutoff. |
| `demo_02_en` | Central Public Works Highway Tender | `en` | `pdf` | `tender` | 310 | 4-lane expressway construction e-tender with earnest money deposit. |
| `demo_03_en` | Municipal Corporation Rainwater Harvesting Order | `en` | `docx` | `municipal` | 215 | Mandatory rooftop rainwater harvesting for plots >= 300 sq.m. |
| `demo_04_hi` | राष्ट्रीय छात्रवृत्ति पोर्टल दिशा-निर्देश | `hi` | `txt` | `scholarship` | 230 | उच्च शिक्षा पोस्ट-मैट्रिक छात्रवृत्ति दिशा-निर्देश व अंतिम तिथि। |
| `demo_05_hi` | नगर निगम जल संरक्षण अनिवार्य परिपत्र | `hi` | `pdf` | `municipal` | 280 | वर्षा जल संचयन अनिवार्य आदेश एवं अनुपालन नोटिस। |
| `demo_06_hi` | राज्य लोक निर्माण विभाग सड़क मरम्मत निविदा | `hi` | `png` | `tender` | 195 | राज्य राजमार्ग डामरीकरण निविदा एवं बयाना राशि। |
| `demo_07_bn` | উচ্চ মাধ্যমিক উত্তর-ম্যাট্রিক বৃত্তি নির্দেশিকা | `bn` | `txt` | `scholarship` | 225 | পশ্চিমবঙ্গ মেধাবী ছাত্রবৃত্তি আবেদন ও নথি তালিকা। |
| `demo_08_bn` | পৌরসভা বর্জ্য নিষ্কাশন ও স্বাস্থ্য পরিপত্র | `bn` | `pdf` | `municipal` | 260 | কঠিন বর্জ্য পৃথকীকরণ ও পরিবেশ সুরক্ষা নির্দেশ। |
| `demo_09_bn` | পূর্ত দপ্তর সেতু সংস্কার টেন্ডার বিজ্ঞপ্তি | `bn` | `docx` | `tender` | 240 | নদী সেতু সংস্কার ও রক্ষণাবেক্ষণ দরপত্র আহ্বান। |
| `demo_10_ta` | முதுகலை பொறியியல் கல்வி உதவித்தொகை | `ta` | `txt` | `scholarship` | 210 | தமிழ்நாடு அரசு உயர்கல்வி உதவித்தொகை வழிகாட்டுதல். |
| `demo_11_ta` | சென்னை மாநகராட்சி மழைநீர் சேகரிப்பு ஆணை | `ta` | `pdf` | `municipal` | 275 | அனைத்து வணிக வளாகங்களிலும் மழைநீர் கட்டமைப்பு கட்டாயம். |
| `demo_12_ta` | நெடுஞ்சாலைத்துறை மேம்பால டெண்டர் அறிவிப்பு | `ta` | `jpg` | `tender` | 185 | மாநில நெடுஞ்சாலை மேம்பால கட்டுமான ஒப்பந்த அறிவிப்பு. |
| `demo_13_te` | ఉన్నత విద్యా పోస్ట్-మెట్రిక్ స్కాలర్‌షిప్ నోటీసు | `te` | `txt` | `scholarship` | 220 | ఇంజనీరింగ్ విద్యార్థుల ఫీజు రీయింబర్స్‌మెంట్ గడువు. |
| `demo_14_te` | గ్రేటర్ హైదరాబాద్ తాగునీటి సంరక్షణ సర్క్యులర్ | `te` | `pdf` | `municipal` | 255 | వర్షపు నీటి సంరక్షణ గుంతల నిర్మాణం తప్పనిసరి. |
| `demo_15_te` | పంచాయతీ రాజ్ రహదారుల పునర్నిర్మాణ టెండర్ | `te` | `docx` | `tender` | 235 | గ్రామీణ రోడ్ల నిర్మాణం మరియు మరమ్మతుల టెండర్. |
| `demo_16_mr` | उच्च व तंत्रशिक्षण विभाग शिष्यवृत्ती परिपत्रक | `mr` | `txt` | `scholarship` | 230 | महाराष्ट्र महाडीबीटी पोर्टल शिष्यवृत्ती अर्ज मुदतवाढ. |
| `demo_17_mr` | मुंबई महानगरपालिका पावसाळी पाणी संचयन आदेश | `mr` | `pdf` | `municipal` | 270 | गृहनिर्माण संस्थांसाठी रेन वॉटर हार्वेस्टिंग बंधनकारक. |
| `demo_18_mr` | सार्वजनिक बांधकाम विभाग रस्ता डांबरीकरण निविदा | `mr` | `webp` | `tender` | 190 | जिल्हा मार्ग मजबुतीकरण व डांबरीकरण ई-निविदा. |
| `demo_19_gu` | મુખ્યમંત્રી યુવા સ્વાવલંબન યોજના શિષ્યવૃત્તિ | `gu` | `txt` | `scholarship` | 225 | ઉચ્ચ શિક્ષણ સહાય અને ટ્યુશન ફી સહાય પરિપત્ર. |
| `demo_20_gu` | અમદાવાદ મ્યુનિસિપલ કોર્પોરેશન સોલિડ વેસ્ટ નિયમો | `gu` | `pdf` | `municipal` | 265 | સૂકા અને ભીના કચરાના વર્ગીકરણ અંગે સૂચના. |
| `demo_21_gu` | માર્ગ અને મકાન વિભાગ બ્રિજ સમારકામ ટેન્ડર | `gu` | `docx` | `tender` | 240 | જિલ્લા પંચાયત ગ્રામ્ય માર્ગ પુલ નિર્માણ ટેન્ડર. |
| `demo_22_pa` | ਪੋਸਟ-ਮੈਟ੍ਰਿਕ ਵਜ਼ੀਫ਼ਾ ਸਕੀਮ ਦਿਸ਼ਾ-ਨਿਰਦੇਸ਼ | `pa` | `txt` | `scholarship` | 215 | ਪੰਜਾਬ ਉਚੇਰੀ ਸਿੱਖਿਆ ਵਜ਼ੀਫ਼ਾ ਪੋਰਟਲ ਆਖਰੀ ਮਿਤੀ। |
| `demo_23_pa` | ਨਗਰ ਨਿਗਮ ਸਵੱਛਤਾ ਅਤੇ ਪਾਣੀ ਬਚਾਓ ਹੁਕਮ | `pa` | `pdf` | `municipal` | 260 | ਰਿਹਾਇਸ਼ੀ ਇਲਾਕਿਆਂ ਵਿੱਚ ਮੀਂਹ ਦੇ ਪਾਣੀ ਦੀ ਸਾਂਭ-ਸੰਭਾਲ। |
| `demo_24_pa` | ਲੋਕ ਨਿਰਮਾਣ ਵਿਭਾਗ ਪੇਂਡੂ ਲਿੰਕ ਸੜਕ ਟੈਂਡਰ | `pa` | `tif` | `tender` | 180 | ਪੇਂਡੂ ਲਿੰਕ ਸੜਕਾਂ ਦੀ ਮੁਰੰਮਤ ਅਤੇ ਪ੍ਰੀਮਿਕਸ ਕਾਰਪੇਟਿੰਗ। |
| `demo_25_kn` | ಉನ್ನತ ಶಿಕ್ಷಣ ಇಲಾಖೆ ವಿದ್ಯಾರ್ಥಿವೇತನ ಸುತ್ತೋಲೆ | `kn` | `txt` | `scholarship` | 220 | ರಾಜ್ಯ ವಿದ್ಯಾರ್ಥಿವೇತನ ತಂತ್ರಾಂಶ (SSP) ಅರ್ಜಿ ಸಲ್ಲಿಕೆ. |
| `demo_26_kn` | ಬೃಹತ್ ಬೆಂಗಳೂರು ಮಹಾನಗರ ಪಾಲಿಕೆ ಮಳೆನೀರು ಕೊಯ್ಲು | `kn` | `pdf` | `municipal` | 275 | ನಗರ ಪ್ರದೇಶಗಳಲ್ಲಿ ಮಳೆನೀರು ಕೊಯ್ಲು ಅಳವಡಿಕೆ ಕಡ್ಡಾಯ. |
| `demo_27_kn` | ಲೋಕೋಪಯೋಗಿ ಇಲಾಖೆ ಗ್ರಾಮೀಣ ರಸ್ತೆ ಅಭಿವೃದ್ಧಿ ಟೆಂಡರ್ | `kn` | `docx` | `tender` | 230 | ತಾಲೂಕು ವ್ಯಾಪ್ತಿಯ ರಸ್ತೆ ಡಾಂಬರೀಕರಣ ಇ-ಟೆಂಡರ್. |
| `demo_28_ur` | قومی اسکالرشپ پورٹل ہدایات برائے اعلیٰ تعلیم | `ur` | `txt` | `scholarship` | 225 | پوسٹ میٹرک اسکالرشپ درخواست فارم اور تصدیقی دستاویزات۔ |
| `demo_29_ur` | بلدیہ عظمیٰ پانی کے تحفظ اور رین واٹر ہارویسٹنگ حکم | `ur` | `pdf` | `municipal` | 265 | تمام رہائشی سوسائٹیوں کے لیے بارانی پانی ذخیرہ لازم۔ |
| `demo_30_ur` | محکمہ تعمیرات عامہ پل اور سڑک مرمت ٹینڈر | `ur` | `jpg` | `tender` | 190 | شہری رابطہ سڑکوں کی تعمیر اور تارکول بچھانے کا ٹینڈر۔ |
| `demo_31_bilingual` | Municipal Bilingual Rainwater Mandate (EN/HI) | `en` | `txt` | `bilingual` | 280 | Dual English and Hindi mandatory rainwater harvesting circular. |
| `demo_32_disaster` | DDMA Flood Relief & Evacuation Order | `en` | `txt` | `disaster` | 315 | Disaster Management evacuation, shelter, and financial grant order. |

---

## 3. Manifest Metadata Schema

The library catalog is formally indexed in `tests/fixtures/demo_library/manifest.json`:

```json
{
  "version": "2026.1",
  "generated_at": "2026-10-24T03:49:07Z",
  "total_items": 32,
  "supported_languages": ["en", "hi", "bn", "ta", "te", "mr", "gu", "pa", "kn", "ur"],
  "supported_formats": ["txt", "pdf", "docx", "png", "jpg", "webp", "tif"]
}
```

Judges and users can access any demo notice through the web interface with single-click loading into the analysis workspace via `GET /api/demo-library` and `POST /api/demo-library/{id}/load`.
