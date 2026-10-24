# LAN API Connectivity & Routing Results

**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Date:** October 24, 2026  
**Auditor:** Antigravity AI Engineering Team  
**Scope:** HTTP API Endpoint Validation, Reverse Proxy Verification, and CORS Validation  

---

## 1. Network Endpoint Validation Matrix

All endpoints were tested across both loopback (`127.0.0.1`) and the active Wi-Fi LAN interface (`192.168.29.182`):

| Endpoint Tested | Access Route | HTTP Method | Expected Status | Received Status | Response Body Snapshot | Result |
|-----------------|--------------|-------------|-----------------|-----------------|------------------------|--------|
| `http://127.0.0.1:8000/api/health` | Direct Backend (Loopback) | GET | 200 OK | **200 OK** | `{"status": "healthy"}` | **PASS** |
| `http://0.0.0.0:8000/api/health` | Direct Backend (All Interfaces) | GET | 200 OK | **200 OK** | `{"status": "healthy"}` | **PASS** |
| `http://192.168.29.182:5173/` | Vite Frontend (LAN Interface) | GET | 200 OK | **200 OK** | `<!DOCTYPE html><html...` | **PASS** |
| `http://192.168.29.182:5173/api/health` | Vite Reverse Proxy (LAN Interface) | GET | 200 OK | **200 OK** | `{"status": "healthy"}` | **PASS** |
| `http://192.168.29.182:5173/api/notices/sample` | Vite Reverse Proxy (Sample Notice) | GET | 200 OK | **200 OK** | `[{"id": "sample-1", "title": ...}]` | **PASS** |

---

## 2. Vite Reverse Proxy Architecture

Because modern mobile browsers enforce strict cross-origin policies, accessing the backend directly on a different port (`:8000`) from the frontend (`:5173`) over an unencrypted local IP can cause CORS or mixed-content warnings. 

The Vite reverse proxy solves this cleanly:
```
Mobile Browser (192.168.29.X)
         │
         ▼  HTTP GET http://192.168.29.182:5173/api/*
Vite Dev Server (0.0.0.0:5173)
         │
         ▼  Internal Loopback Proxy (changeOrigin: true)
FastAPI Backend (127.0.0.1:8000)
```
- **Zero CORS Pre-flight Penalty**: The browser treats all API requests as same-origin (`/api/*`).
- **No Hardcoded IPs**: Works dynamically regardless of network IP changes.

---

## 3. Backend CORS Security Policy Inspection

Inspection of `src/notice2action/api/server.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
- Restricts origin domains to local private network subnets (RFC 1918) and loopback addresses.
- Rejects wildcards (`"*"`) while supporting dynamic LAN IP assignment.
