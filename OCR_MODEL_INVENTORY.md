# SochnaSetu AI — Multilingual OCR Model Inventory

## 1. Overview
This document catalogs all machine learning models, neural weights, and language packs integrated into SochnaSetu AI's privacy-first, locally deployable universal multilingual OCR system.

All models run entirely on-premise on local CPU/GPU hardware without requiring paid external APIs or transmitting private civic documents over the internet.

---

## 2. Integrated Tesseract 5 Models (`assets/tessdata/`)

All Tesseract models are official fast integer LSTM models (`tessdata_fast`) licensed under **Apache License 2.0**.

| Language | Code | File Name | Size (MB) | License | Architecture | Primary Engine |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| **English** | `en` / `eng` | `eng.traineddata` | 4.09 MB | Apache-2.0 | LSTM Neural Network | Tesseract 5 AVX2 |
| **Hindi** | `hi` / `hin` | `hin.traineddata` | 2.50 MB | Apache-2.0 | LSTM Neural Network | Tesseract 5 AVX2 |
| **Assamese** | `as` / `asm` | `asm.traineddata` | 1.95 MB | Apache-2.0 | LSTM Neural Network | Tesseract 5 AVX2 |
| **Bengali** | `bn` / `ben` | `ben.traineddata` | 0.85 MB | Apache-2.0 | LSTM Neural Network | Tesseract 5 AVX2 |
| **Gujarati** | `gu` / `guj` | `guj.traineddata` | 1.42 MB | Apache-2.0 | LSTM Neural Network | Tesseract 5 AVX2 |
| **Kannada** | `kn` / `kan` | `kan.traineddata` | 3.61 MB | Apache-2.0 | LSTM Neural Network | Tesseract 5 AVX2 |
| **Malayalam** | `ml` / `mal` | `mal.traineddata` | 5.28 MB | Apache-2.0 | LSTM Neural Network | Tesseract 5 AVX2 |
| **Marathi** | `mr` / `mar` | `mar.traineddata` | 2.10 MB | Apache-2.0 | LSTM Neural Network | Tesseract 5 AVX2 |
| **Nepali** | `ne` / `nep` | `nep.traineddata` | 0.96 MB | Apache-2.0 | LSTM Neural Network | Tesseract 5 AVX2 |
| **Odia** | `or` / `ori` | `ori.traineddata` | 1.48 MB | Apache-2.0 | LSTM Neural Network | Tesseract 5 AVX2 |
| **Punjabi** | `pa` / `pan` | `pan.traineddata` | 0.50 MB | Apache-2.0 | LSTM Neural Network | Tesseract 5 AVX2 |
| **Sanskrit** | `sa` / `san` | `san.traineddata` | 11.83 MB | Apache-2.0 | LSTM Neural Network | Tesseract 5 AVX2 |
| **Sindhi** | `sd` / `snd` | `snd.traineddata` | 1.62 MB | Apache-2.0 | LSTM Neural Network | Tesseract 5 AVX2 |
| **Tamil** | `ta` / `tam` | `tam.traineddata` | 3.20 MB | Apache-2.0 | LSTM Neural Network | Tesseract 5 AVX2 |
| **Telugu** | `te` / `tel` | `tel.traineddata` | 2.80 MB | Apache-2.0 | LSTM Neural Network | Tesseract 5 AVX2 |
| **Urdu** | `ur` / `urd` | `urd.traineddata` | 1.40 MB | Apache-2.0 | LSTM Neural Network | Tesseract 5 AVX2 |
| **Orientation & Script**| `osd` | `osd.traineddata` | 10.50 MB | Apache-2.0 | Legacy Decision Tree | Tesseract 5 AVX2 |

**Total Tesseract Storage**: ~50.6 MB  
**VRAM Footprint**: 0 MB (runs entirely on host CPU using AVX2 SIMD instructions)

---

## 3. Specialized Regional Scripts & Architectural Adapters

| Language | Script | Base Engine | Model Routing Strategy | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Bodo** (`brx`) | Devanagari | Tesseract 5 | Routed to base Devanagari model (`hin.traineddata`) with Bodo lexical token matching | Installed / Supported |
| **Dogri** (`doi`) | Devanagari | Tesseract 5 | Routed to base Devanagari model (`hin.traineddata`) with Dogri administrative vocabulary | Installed / Supported |
| **Konkani** (`kok`)| Devanagari | Tesseract 5 | Routed to Marathi/Devanagari model (`mar.traineddata` / `hin.traineddata`) | Installed / Supported |
| **Maithili** (`mai`)| Devanagari | Tesseract 5 | Routed to base Devanagari model (`hin.traineddata`) with Maithili verb morphology | Installed / Supported |
| **Kashmiri** (`ks`)| Perso-Arabic | Tesseract 5 | Routed to Perso-Arabic base model (`urd.traineddata`) with Kashmiri character preservation | Installed / Supported |
| **Manipuri** (`mni`)| Bengali / Meetei | Tesseract 5 / IndicOCR | Bengali-script notices routed to `ben.traineddata`; Meetei Mayek routed to `IndicOCREngine` | Installed / Extensible |
| **Santali** (`sat`)| Ol Chiki / Bengali | Tesseract 5 / IndicOCR | Bengali/Devanagari notices routed to `ben`/`hin`; Ol Chiki script routed to `IndicOCREngine` | Extensible Adapter |

---

## 4. Hardware Sizing & Memory Footprint

- **RAM**: 16 GB DDR5 (Typical application peak during multi-page PDF processing: 1.2 GB RAM).
- **VRAM**: 0 MB consumed by OCR engine; 100% of the 6 GB VRAM on NVIDIA RTX 4050 remains allocated for local Ollama LLM inference.
- **CPU**: AMD Ryzen 7 7445HS utilizing multithreaded OpenMP / AVX2 vector extensions for sub-second page recognition.
