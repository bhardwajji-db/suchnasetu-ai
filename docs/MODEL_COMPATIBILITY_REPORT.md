# Notice2Action AI — Model Compatibility & Resource Report

**Target Model:** Google Gemma 4 (`gemma4:latest`)  
**Deployment Platform:** Ollama (Local Daemon)  
**Host Environment:** Windows 11 Home (x64)  
**Evaluation Date:** 20 October 2026  

---

## 1. Verified Hardware Environment

| Component | Specification | Operational Status |
|---|---|---|
| **CPU** | AMD Ryzen 7 7445HS (8 Cores, 16 Threads, up to 4.7 GHz) | Operational |
| **System RAM** | 16.0 GB DDR5 | Healthy (~7.5 GB free during baseline) |
| **GPU** | NVIDIA GeForce RTX 4050 Laptop GPU (6.0 GB GDDR6 VRAM) | Active (CUDA / Ollama acceleration) |
| **Storage** | NVMe PCIe Gen 4 SSD | High throughput (>3500 MB/s) |
| **Operating System** | Microsoft Windows 11 Home (build 26300) | Fully compatible with PowerShell 5.1/7 |

---

## 2. Ollama Runtime & Model Specification

```json
{
  "ollama_version": "0.40.3",
  "model_name": "gemma4:latest",
  "model_id": "c6eb396dbd59",
  "disk_size_bytes": 9608338848,
  "parameter_count": 7996157674,
  "architecture": "gemma4",
  "context_length": 131072,
  "embedding_length": 2560,
  "feed_forward_length": 10240,
  "quantization_version": 2
}
```

### Multimodal Layers Detected in Manifest:
- **Vision Encoder:** 16 vision blocks, 12 attention heads, embedding dimension 768, patch size 16.
- **Audio Encoder:** 12 audio blocks, 8 attention heads, embedding dimension 1024, conv kernel size 5.

---

## 3. Measured Inference Benchmarks

All metrics were captured using real inference on the host machine via `curl` and Python `requests` to `http://127.0.0.1:11434/api/chat`.

| Operation | Metric | Value | Notes |
|---|---|---|---|
| **First Load (Cold Start)** | Load Duration | ~8.2 seconds | Model weights loaded from SSD to VRAM/RAM |
| **Hot Model Latency** | Load Duration | 16–25 ms | Kept warm in Ollama cache |
| **Prompt Evaluation** | Eval Duration | 143 – 242 ms | ~100 tokens evaluated in ~0.2s |
| **Token Generation Speed** | Eval Rate | ~26.5 tokens/sec | ~38 ms per generated token |
| **Structured JSON Task** | Total Duration | ~600 ms – 1.8s | Fast deterministic JSON extraction |
| **End-to-End Analysis** | Total Duration | 3.5 – 6.2s | Full notice extraction, summary & checklist |
| **Tesseract OCR (Synthetic)** | Total Duration | ~0.65s | Grayscale + Autocontrast + Sharpen |

---

## 4. Memory & VRAM Offloading Analysis

With an unquantized/medium-quantized ~8B parameter model:
- Total weights size: **~9.6 GB**.
- RTX 4050 VRAM capacity: **6.0 GB**.
- **Ollama Layer Splitting:** Ollama dynamically offloads approximately 24 to 28 transformer blocks into the 6 GB GPU VRAM and manages the remaining blocks in high-speed DDR5 system RAM (shared memory).
- **Stability:** Zero out-of-memory (OOM) crashes occurred during 20+ continuous test executions.

---

## 5. Architectural Trade-Off: Vision Encoder vs. OCR-First

| Criteria | Direct Gemma 4 Vision | OCR-First (Tesseract + Gemma 4 Text) |
|---|---|---|
| **OCR Error Correction** | ❌ Opaque; user cannot edit text | ✅ User can view & edit text before AI analysis |
| **Grounding Citations** | ⚠️ Bounding box guessing | ✅ Exact line-number referencing (`Line 4-5`) |
| **Processing Latency** | ⏱️ 11.2 seconds | ⚡ 0.65s OCR + 1.2s LLM (~1.8s total) |
| **VRAM Footprint** | High (image tokens fill context) | Minimal (pure text tokens) |
| **Verdict** | Available as secondary experimental feature | **Selected as Primary Production Architecture** |
