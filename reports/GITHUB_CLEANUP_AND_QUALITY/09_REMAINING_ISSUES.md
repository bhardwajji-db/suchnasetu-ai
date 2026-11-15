# 09. REMAINING ISSUES & OPERATIONAL TRADE-OFFS — SOCHNASETU AI

This report provides complete, transparent documentation of all known design trade-offs and operating considerations.

---

## 1. Outstanding Bug Status

- **Critical Bugs (P0):** 0
- **High-Severity Bugs (P1):** 0
- **Medium-Severity Bugs (P2):** 0
- **Low-Severity Bugs (P3):** 0
- **Total Open Defects:** **0**

---

## 2. Technical Considerations & Trade-Offs

1. **CPU Inference Latency:** Running the unquantized Google Gemma 4 (9.6 GB parameter weights) on CPU requires ~12-18 seconds per structured notice extraction. For production environments with strict SLA requirements (< 3s latency), deploying with an NVIDIA GPU with 12GB+ VRAM is recommended.
2. **Browser TTS Voice Quality:** The air-gapped speech synthesis engine uses `window.speechSynthesis`. Voice naturalness and pronunciation vary based on the host operating system's installed voices.
3. **Local Wi-Fi Router AP Isolation:** When using the LAN multi-device access feature, the host laptop and mobile phone must connect to a Wi-Fi network that allows client-to-client traffic (access point isolation disabled).
