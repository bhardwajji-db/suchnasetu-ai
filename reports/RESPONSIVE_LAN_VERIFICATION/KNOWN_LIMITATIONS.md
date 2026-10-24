# Known Limitations & Device Environmental Guidelines

**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Date:** October 24, 2026  
**Auditor:** Antigravity AI Engineering Team  
**Scope:** Browser Engine Discrepancies, Network Topologies, and Mobile Constraints  

---

## 1. Automated Viewport Testing vs. Real Device Rendering

- **Simulated JSDOM Testing**:
  Automated tests in `frontend/src/test/ResponsiveViewportMatrix.test.tsx` simulate viewport boundaries (`window.innerWidth`, `window.innerHeight`) within a headless JSDOM environment. They mathematically verify that responsive class bindings, modal maximum dimensions, bottom navigation visibility, and drawer triggers function correctly.
- **Physical Device Rendering Engines**:
  Physical mobile devices execute WebKit (iOS Safari) or Blink (Android Chrome). These engines feature dynamic browser chrome (expanding/collapsing address bars on scroll) and virtual keyboards. SochnaSetu AI accounts for this by utilizing `100dvh` (dynamic viewport height) where applicable and `viewport-fit=cover` for notch safe areas.

---

## 2. Local Wi-Fi Router / Hotspot Considerations

- **Access Point (AP) Client Isolation**:
  Some public Wi-Fi networks (hotels, university campuses, enterprise guest networks) enable **Client Isolation**, which forbids devices on the same Wi-Fi from communicating directly with one another. If your phone cannot open `http://<IP>:5173`:
  - Verify you are on a private home network or phone mobile hotspot.
  - If using a router, ensure "AP Isolation" or "Guest Mode" is disabled.
- **Dynamic IP Changes (DHCP Lease Expiry)**:
  If the host laptop disconnects from Wi-Fi or restarts, the router may assign a different IP address (e.g. `192.168.29.183` instead of `192.168.29.182`). Always verify the active IPv4 address using `ipconfig` if connection fails after rebooting.

---

## 3. Web Speech API Permissions over HTTP (Mobile Chrome)

- **Chromium Insecure Origin Restrictions**:
  Modern versions of Google Chrome and Android Chrome restrict microphone access (Web Speech API / SpeechRecognition) to secure origins (`https://` or `localhost`).
  - Accessing the app over plain HTTP (`http://192.168.29.182:5173`) from an Android phone may result in the microphone permission prompt being disabled by the browser.
  - **Workaround for Voice Input on Android over LAN HTTP**:
    1. On your phone's Chrome browser, navigate to `chrome://flags/#unsafely-treat-insecure-origin-as-secure`.
    2. Enter `http://192.168.29.182:5173` into the text box.
    3. Toggle the dropdown to **Enabled** and restart Chrome.
  - **Text-to-Speech (Audio Playback)** is unaffected and works out of the box on all mobile browsers over HTTP.
