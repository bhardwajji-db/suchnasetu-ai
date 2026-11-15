# 14. REMAINING ISSUES & SYSTEM LIMITATIONS — SOCHNASETU AI

This report provides complete transparency regarding current technical trade-offs and future optimization opportunities.

---

## 1. Current Technical Trade-Offs

1. **Local LLM Inference Latency on CPU:**
   - On a machine without dedicated GPU acceleration, running Gemma 4 (9.6 GB parameter weights) takes approximately 12–18 seconds for complex structured extraction.
   - *Mitigation:* A visual progress modal informs users of the processing stages, and deterministic regex fallbacks are provided for quick extractions.
2. **Browser-Dependent Text-to-Speech:**
   - The air-gapped text-to-speech engine relies on `window.speechSynthesis`. Voice quality, accent, and pitch vary depending on the operating system's installed speech synthesis voices.
3. **Physical Mobile Device Testing Constraints:**
   - While responsive multi-viewport emulation and network LAN binding are 100% verified, physical mobile device testing depends on the local network router allowing client-to-client traffic (AP isolation must be disabled).

---

## 2. Recommended Future Enhancements

- **Quantized GGUF Model Options:** Provide smaller 4-bit quantized Gemma 2/4 variants (e.g. 2B or 4B) for ultra-low-spec hardware.
- **Service Worker PWA Offline Caching:** Implement progressive web app service workers for complete offline client asset caching.
