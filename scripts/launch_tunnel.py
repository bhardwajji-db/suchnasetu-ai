"""
SuchnaSetu AI — Cloudflare Tunnel & Production Deployment Runner
Automates:
1. Verifying production React 19 build in frontend/dist.
2. Launching unified FastAPI server (API + Frontend SPA) on port 8000.
3. Establishing a public Cloudflare Tunnel via cloudflared.
4. Extracting and displaying the live HTTPS public tunnel URL.
5. Updating .env AUTH_PUBLIC_APP_URL so authentication and links are synchronized.
"""

import os
import re
import sys
import time
import socket
import urllib.request
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
TUNNEL_LOG = LOGS_DIR / "cloudflared.log"
BACKEND_LOG = LOGS_DIR / "backend.log"
URL_FILE = LOGS_DIR / "active_tunnel_url.txt"
PID_FILE = PROJECT_ROOT / ".tunnel_pids.json"


def is_port_open(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def wait_for_server(url: str = "http://127.0.0.1:8000/api/samples", timeout: float = 30.0) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Tunnel-Checker"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if 200 <= resp.status < 400:
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def update_env_file(tunnel_url: str):
    env_path = PROJECT_ROOT / ".env"
    if not env_path.is_file():
        return
    text = env_path.read_text(encoding="utf-8")
    
    # Update AUTH_PUBLIC_APP_URL
    text = re.sub(
        r"^AUTH_PUBLIC_APP_URL=.*$",
        f"AUTH_PUBLIC_APP_URL={tunnel_url}",
        text,
        flags=re.MULTILINE,
    )
    
    # Update CORS_ALLOWED_ORIGINS
    if "CORS_ALLOWED_ORIGINS=" in text:
        def update_cors(match):
            origins = [o.strip() for o in match.group(1).split(",") if o.strip()]
            # Filter out old trycloudflare urls
            origins = [o for o in origins if not o.endswith(".trycloudflare.com")]
            origins.insert(0, tunnel_url)
            return f"CORS_ALLOWED_ORIGINS={','.join(origins)}"
        text = re.sub(r"^CORS_ALLOWED_ORIGINS=(.*)$", update_cors, text, flags=re.MULTILINE)

    env_path.write_text(text, encoding="utf-8")


def main():
    print("=" * 70)
    print("       SUCHNASETU AI — CLOUDFLARE TUNNEL PRODUCTION LAUNCHER")
    print("=" * 70)

    # 1. Check frontend dist
    dist_index = PROJECT_ROOT / "frontend" / "dist" / "index.html"
    if not dist_index.is_file():
        print("[1/4] Frontend bundle not found. Building React 19 production SPA...")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        subprocess.run([npm_cmd, "run", "build"], cwd=PROJECT_ROOT / "frontend", check=True)
    else:
        print("[1/4] Frontend production SPA verified at frontend/dist.")

    # 2. Check / Start Backend
    backend_proc = None
    if not is_port_open(8000):
        print("[2/4] Starting unified FastAPI server on http://127.0.0.1:8000...")
        python_exe = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
        if not python_exe.is_file():
            python_exe = Path(sys.executable)

        backend_proc = subprocess.Popen(
            [
                str(python_exe),
                "-m", "uvicorn",
                "notice2action.api.server:app",
                "--app-dir", "src",
                "--host", "127.0.0.1",
                "--port", "8000",
            ],
            cwd=str(PROJECT_ROOT),
            stdout=open(BACKEND_LOG, "a", encoding="utf-8"),
            stderr=subprocess.STDOUT,
        )

        if not wait_for_server(timeout=25.0):
            print("[ERROR] Backend failed to start or respond on port 8000.")
            if backend_proc:
                backend_proc.kill()
            sys.exit(1)
        print("      Backend server is healthy and responding on port 8000.")
    else:
        print("[2/4] Port 8000 is already active and listening.")

    # 3. Start cloudflared
    print("[3/4] Launching Cloudflare Tunnel (cloudflared)...")
    cloudflared_bin = "cloudflared"
    # Find cloudflared executable if not in standard PATH
    standard_paths = [
        Path(r"C:\Program Files (x86)\cloudflared\cloudflared.exe"),
        Path(r"C:\Program Files\cloudflared\cloudflared.exe"),
    ]
    for sp in standard_paths:
        if sp.is_file():
            cloudflared_bin = str(sp)
            break

    # Truncate old tunnel log
    with open(TUNNEL_LOG, "w", encoding="utf-8") as f:
        f.write("")

    tunnel_proc = subprocess.Popen(
        [cloudflared_bin, "tunnel", "--url", "http://127.0.0.1:8000"],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    # 4. Wait for and extract the trycloudflare URL
    print("[4/4] Establishing secure tunnel connection...")
    tunnel_url = None
    start_time = time.time()
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    # Read output line by line
    with open(TUNNEL_LOG, "a", encoding="utf-8") as log_file:
        while time.time() - start_time < 30.0:
            line = tunnel_proc.stdout.readline()
            if not line and tunnel_proc.poll() is not None:
                break
            if line:
                log_file.write(line)
                log_file.flush()
                m = url_pattern.search(line)
                if m:
                    tunnel_url = m.group(0)
                    break
            time.sleep(0.05)

    if not tunnel_url:
        print("[ERROR] Could not extract trycloudflare URL within 30 seconds.")
        print(f"Check logs at {TUNNEL_LOG}")
        tunnel_proc.kill()
        if backend_proc:
            backend_proc.kill()
        sys.exit(1)

    # Save active tunnel URL to file & update .env
    URL_FILE.write_text(tunnel_url.strip(), encoding="utf-8")
    try:
        update_env_file(tunnel_url.strip())
    except Exception as e:
        print(f"Note: Could not update .env: {e}")

    print("\n" + "=" * 70)
    print("      🎉 LIVE CLOUDFLARE TUNNEL IS ACTIVE AND READY!")
    print("=" * 70)
    print(f"\n   🌐 Public App URL:   {tunnel_url}")
    print(f"   📡 Interactive Docs: {tunnel_url}/docs")
    print(f"   🏠 Local Mirror:     http://localhost:8000\n")
    print("=" * 70)
    print("The tunnel is now forwarding requests directly to your app.")
    print("Press Ctrl+C to stop the tunnel and server.\n")

    try:
        # Keep process alive and forward output
        while True:
            line = tunnel_proc.stdout.readline()
            if not line and tunnel_proc.poll() is not None:
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nShutting down tunnel and server...")
    finally:
        tunnel_proc.kill()
        if backend_proc:
            backend_proc.kill()
        print("Shutdown complete.")


if __name__ == "__main__":
    main()
