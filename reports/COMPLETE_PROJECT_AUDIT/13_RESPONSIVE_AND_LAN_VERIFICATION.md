# 13. RESPONSIVE DESIGN & LAN ACCESS VERIFICATION

---

## 1. Multi-Viewport Layout Verification Matrix

Tested via Playwright and Vitest across 7 canonical device viewports:

| Device Category | Viewport Dimensions | Orientation | Layout Behavior | Text Wrap & Overflow | Verdict |
| :--- | :---: | :---: | :--- | :--- | :---: |
| **Small Phone (iPhone SE)** | 320 × 568 | Portrait | Single-column, stacked cards | Clean wrap, 0px overflow | **PASS** |
| **Typical Android Phone** | 360 × 800 | Portrait | Single-column, bottom nav | Clean wrap, 0px overflow | **PASS** |
| **Modern Phone (iPhone 14)** | 390 × 844 | Portrait | Single-column, bottom nav | Clean wrap, 0px overflow | **PASS** |
| **Tablet Portrait (iPad)** | 768 × 1024 | Portrait | 2-column responsive grid | Clean wrap, 0px overflow | **PASS** |
| **Tablet Landscape** | 1024 × 768 | Landscape | 2-column grid, sidebar visible| Clean wrap, 0px overflow | **PASS** |
| **Standard Laptop** | 1366 × 768 | Landscape | Full desktop layout | Clean wrap, 0px overflow | **PASS** |
| **Large Desktop Display** | 1920 × 1080 | Landscape | Full desktop layout | Clean wrap, 0px overflow | **PASS** |

---

## 2. Multi-Device Local Area Network (LAN) Access

- **Host Binding:** `0.0.0.0:8000` (FastAPI backend and compiled frontend SPA).
- **Wi-Fi Detection:** [start_production.bat](./start_production.bat) auto-detects local IPv4 addresses (e.g. `192.168.1.X`) via PowerShell and displays ready-to-use access links.
- **Physical Device Compatibility:** Phones and tablets connected to the same Wi-Fi network access the full application seamlessly at `http://<YOUR_LAN_IP>:8000`.
