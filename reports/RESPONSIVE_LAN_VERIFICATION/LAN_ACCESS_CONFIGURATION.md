# Multi-Device Local Area Network (LAN) Configuration Guide

**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Date:** October 24, 2026  
**Auditor:** Antigravity AI Engineering Team  
**Scope:** Local Wi-Fi / LAN Network Connectivity, Host Binding, and Firewall Security  

---

## 1. Executive Summary

To allow users to access SochnaSetu AI from mobile phones, tablets, and secondary computers connected to the same local Wi-Fi network without third-party cloud services or exposing the machine to the public internet:
1. The **FastAPI backend** is configured to bind to `0.0.0.0:8000`.
2. The **Vite frontend development server** is configured to bind to `0.0.0.0:5173`.
3. The **Vite internal reverse proxy** routes `/api` requests transparently to the backend (`http://127.0.0.1:8000`), so mobile browsers never need to make cross-origin requests directly to port 8000.
4. The backend CORS policy utilizes regex matching to safely admit local private IP ranges (`192.168.*`, `10.*`, `172.16-31.*`) without wildcards (`*`).

---

## 2. Server Startup & Host Binding Configurations

### A. Backend FastAPI (`src/notice2action/api/server.py`)
Run the backend with host `0.0.0.0` to listen on all network interfaces:
```bash
.venv\Scripts\python -m uvicorn notice2action.api.server:app --app-dir src --host 0.0.0.0 --port 8000
```

### B. Frontend Vite (`frontend/vite.config.ts`)
The `vite.config.ts` includes host binding and proxy routing:
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Listen on all network interfaces
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
```

Start the frontend:
```bash
npm --prefix frontend run dev -- --host 0.0.0.0 --port 5173
```

---

## 3. How to Connect from a Mobile Phone or Tablet

### Step 1: Connect to the Same Wi-Fi
Ensure your phone or tablet is connected to the exact same Wi-Fi network as your host laptop/PC.

### Step 2: Find Your Host Laptop's Local IP Address
Open PowerShell on your Windows laptop and run:
```powershell
ipconfig
```
Locate the **Wireless LAN adapter Wi-Fi** section and find the **IPv4 Address**:
```text
Wireless LAN adapter Wi-Fi:
   Connection-specific DNS Suffix  . :
   IPv4 Address. . . . . . . . . . . : 192.168.29.182
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . . : 192.168.29.1
```
*(In this example, the local IP is `192.168.29.182`.)*

### Step 3: Open the URL in Your Mobile Browser
Open Chrome, Safari, or Firefox on your phone and navigate to:
```text
http://192.168.29.182:5173
```
The application will load immediately with the responsive mobile layout, bottom navigation bar, and instant multilingual switching.

---

## 4. Windows Defender Firewall Configuration (Safe Private Network Rule)

If your phone cannot reach `http://<YOUR_IP>:5173` (connection timed out), Windows Defender Firewall may be blocking incoming LAN connections on port 5173. 

**Safe Rule (Allow port 5173 on Private Networks Only):**
Run PowerShell as Administrator:
```powershell
New-NetFirewallRule -DisplayName "SochnaSetu Vite Dev Server" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow -Profile Private
```

> [!IMPORTANT]
> **Safety Guarantee:** Never disable the Windows Defender Firewall globally. The command above only permits incoming connections on port 5173 specifically on trusted Private networks (home Wi-Fi). Public Wi-Fi networks remain completely blocked.
