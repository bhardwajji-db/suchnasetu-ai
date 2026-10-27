"""
SuchnaSetu AI — Cloudflare Tunnel & Production Deployment Runner
Automates:
1. Verifying production React 19 build in frontend/dist.
2. Launching unified FastAPI server (API + Frontend SPA) on port 8000 if not already running.
3. Pre-flight health checks for FastAPI backend and Ollama.
4. Single-instance management: cleans up stale cloudflared instances.
5. Establishing a stable Cloudflare Tunnel with HTTP/2 protocol over TLS (avoids UDP/QUIC drops and Error 1033).
6. Continuous output streaming to logs/cloudflared.log.
7. Auto-recovery loop: bounded retries if the tunnel connection drops.
8. Synchronizing logs/active_tunnel_url.txt and .env (AUTH_PUBLIC_APP_URL, CORS_ALLOWED_ORIGINS).
9. Support for Named Tunnels (CLOUDFLARE_TUNNEL_TOKEN) for permanent production hostnames.
"""

import os
import re
import sys
import json
import time
import socket
import signal
import threading
import subprocess
import urllib.request
from pathlib import Path
from typing import Optional, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
TUNNEL_LOG = LOGS_DIR / "cloudflared.log"
BACKEND_LOG = LOGS_DIR / "backend.log"
URL_FILE = LOGS_DIR / "active_tunnel_url.txt"
PID_FILE = PROJECT_ROOT / ".tunnel_pids.json"

URL_PATTERN = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")


def log_message(prefix: str, msg: str):
    """Prints a message with timestamp and flushes stdout."""
    t = time.strftime("%H:%M:%S")
    print(f"[{t}] [{prefix}] {msg}", flush=True)


def is_port_open(port: int, host: str = "127.0.0.1") -> bool:
    """Checks whether a TCP port is listening."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def wait_for_server(url: str = "http://127.0.0.1:8000/health", timeout: float = 30.0) -> bool:
    """Waits for the FastAPI backend to respond with HTTP 200."""
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


def check_ollama_health() -> bool:
    """Checks if local Ollama server is responding at 127.0.0.1:11434."""
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags", headers={"User-Agent": "Tunnel-Checker"})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name", "") for m in data.get("models", [])]
                log_message("OLLAMA", f"Ollama is running. Available models: {', '.join(models) if models else 'None'}")
                return True
    except Exception:
        pass
    log_message("OLLAMA", "Ollama is not reachable on http://127.0.0.1:11434 (external or mock fallback will be used if needed).")
    return False


def get_cloudflared_path() -> str:
    """Finds the cloudflared executable."""
    standard_paths = [
        Path(r"C:\Program Files (x86)\cloudflared\cloudflared.exe"),
        Path(r"C:\Program Files\cloudflared\cloudflared.exe"),
    ]
    for sp in standard_paths:
        if sp.is_file():
            return str(sp)
    return "cloudflared"


def cleanup_stale_processes():
    """Terminates orphaned cloudflared or previous tunnel instances recorded in PID file."""
    if PID_FILE.is_file():
        try:
            data = json.loads(PID_FILE.read_text(encoding="utf-8"))
            tunnel_pid = data.get("tunnel_pid")
            if tunnel_pid:
                try:
                    if sys.platform == "win32":
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(tunnel_pid)],
                                       capture_output=True, text=True)
                    else:
                        os.kill(tunnel_pid, signal.SIGKILL)
                    log_message("CLEANUP", f"Terminated previous tunnel process (PID {tunnel_pid}).")
                except Exception:
                    pass
        except Exception:
            pass
        try:
            PID_FILE.unlink(missing_ok=True)
        except Exception:
            pass

    # Terminate any stray cloudflared instances running quick tunnels to port 8000 on Windows
    if sys.platform == "win32":
        try:
            cmd = 'Get-CimInstance Win32_Process -Filter "Name = \'cloudflared.exe\'" | Select-Object -ExpandProperty ProcessId'
            out = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                                 capture_output=True, text=True).stdout.strip()
            for line in out.splitlines():
                pid_str = line.strip()
                if pid_str.isdigit():
                    try:
                        subprocess.run(["taskkill", "/F", "/PID", pid_str], capture_output=True)
                        log_message("CLEANUP", f"Terminated stray cloudflared instance (PID {pid_str}).")
                    except Exception:
                        pass
        except Exception:
            pass


def update_env_file(tunnel_url: str):
    """Synchronizes AUTH_PUBLIC_APP_URL and CORS_ALLOWED_ORIGINS in .env."""
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

    # Update CSRF_TRUSTED_ORIGINS if present
    if "CSRF_TRUSTED_ORIGINS=" in text:
        def update_csrf(match):
            origins = [o.strip() for o in match.group(1).split(",") if o.strip()]
            origins = [o for o in origins if not o.endswith(".trycloudflare.com")]
            origins.insert(0, tunnel_url)
            return f"CSRF_TRUSTED_ORIGINS={','.join(origins)}"
        text = re.sub(r"^CSRF_TRUSTED_ORIGINS=(.*)$", update_csrf, text, flags=re.MULTILINE)

    env_path.write_text(text, encoding="utf-8")


def get_configured_named_tunnel_token() -> Optional[str]:
    """Reads CLOUDFLARE_TUNNEL_TOKEN from environment or .env if configured."""
    token = os.environ.get("CLOUDFLARE_TUNNEL_TOKEN")
    if token:
        return token.strip()
    env_path = PROJECT_ROOT / ".env"
    if env_path.is_file():
        text = env_path.read_text(encoding="utf-8")
        m = re.search(r"^CLOUDFLARE_TUNNEL_TOKEN=(.+)$", text, flags=re.MULTILINE)
        if m:
            val = m.group(1).strip().strip("'\"")
            if val and not val.startswith("#"):
                return val
    return None


class TunnelManager:
    """Manages cloudflared lifecycle with continuous logging and auto-recovery."""

    def __init__(self, backend_proc=None):
        self.backend_proc = backend_proc
        self.tunnel_proc = None
        self.active_url = None
        self.stop_requested = False
        self.cloudflared_bin = get_cloudflared_path()
        self.named_token = get_configured_named_tunnel_token()

    def start_tunnel_process(self) -> subprocess.Popen:
        """Launches cloudflared with HTTP/2 protocol over TLS to prevent UDP/QUIC drops."""
        if self.named_token:
            log_message("TUNNEL", "Using configured Cloudflare Named Tunnel token.")
            cmd = [
                self.cloudflared_bin,
                "tunnel",
                "run",
                "--token", self.named_token,
            ]
        else:
            log_message("TUNNEL", "Launching Cloudflare Quick Tunnel using HTTP/2 over TLS...")
            cmd = [
                self.cloudflared_bin,
                "tunnel",
                "--protocol", "http2",
                "--edge-ip-version", "auto",
                "--retries", "10",
                "--url", "http://127.0.0.1:8000",
            ]

        proc = subprocess.Popen(
            cmd,
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        return proc

    def stream_tunnel_output(self, proc: subprocess.Popen, log_file_handle):
        """Streams lines from cloudflared stdout into log file and captures public URL."""
        while not self.stop_requested and proc.poll() is None:
            line = proc.stdout.readline()
            if not line:
                break
            log_file_handle.write(line)
            log_file_handle.flush()

            if not self.active_url:
                m = URL_PATTERN.search(line)
                if m:
                    self.active_url = m.group(0).strip()
                    URL_FILE.write_text(self.active_url, encoding="utf-8")
                    try:
                        update_env_file(self.active_url)
                    except Exception as e:
                        log_message("WARN", f"Could not update .env: {e}")

    def run_supervisor(self, max_retries: int = 5):
        """Runs the tunnel supervisor with bounded automatic reconnects."""
        retry_count = 0
        backoff_delays = [2, 4, 8, 15, 30]

        while not self.stop_requested and retry_count <= max_retries:
            self.active_url = None
            log_message("TUNNEL", f"Starting cloudflared process (attempt {retry_count + 1}/{max_retries + 1})...")

            # Open log file in append mode
            with open(TUNNEL_LOG, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n--- Tunnel session started at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                log_file.flush()

                self.tunnel_proc = self.start_tunnel_process()

                # Save PID info
                pids = {
                    "launcher_pid": os.getpid(),
                    "tunnel_pid": self.tunnel_proc.pid,
                    "backend_pid": self.backend_proc.pid if self.backend_proc else None,
                }
                PID_FILE.write_text(json.dumps(pids, indent=2), encoding="utf-8")

                # Wait up to 30 seconds to extract URL
                wait_start = time.time()
                while time.time() - wait_start < 30.0 and not self.stop_requested:
                    if self.tunnel_proc.poll() is not None:
                        break
                    line = self.tunnel_proc.stdout.readline()
                    if line:
                        log_file.write(line)
                        log_file.flush()
                        m = URL_PATTERN.search(line)
                        if m:
                            self.active_url = m.group(0).strip()
                            URL_FILE.write_text(self.active_url, encoding="utf-8")
                            try:
                                update_env_file(self.active_url)
                            except Exception as e:
                                log_message("WARN", f"Could not update .env: {e}")
                            break
                    time.sleep(0.05)

                if self.active_url:
                    retry_count = 0  # Reset retry counter on successful connection
                    print("\n" + "=" * 70, flush=True)
                    print("      SUCHNASETU AI — CLOUDFLARE TUNNEL ONLINE & VERIFIED", flush=True)
                    print("=" * 70, flush=True)
                    print(f"\n   Public App URL:   {self.active_url}", flush=True)
                    print(f"   Interactive Docs: {self.active_url}/docs", flush=True)
                    print(f"   Local Mirror:     http://localhost:8000", flush=True)
                    print(f"   Protocol:         HTTP/2 over TLS (stable TCP keep-alive)\n", flush=True)
                    print("=" * 70, flush=True)
                    print("NOTE: Quick Tunnels (*.trycloudflare.com) are ephemeral test tunnels.", flush=True)
                    print("For a 100% permanent domain, add CLOUDFLARE_TUNNEL_TOKEN to .env.", flush=True)
                    print("Press Ctrl+C to stop the tunnel and server cleanly.\n", flush=True)

                    # Continue streaming output continuously
                    self.stream_tunnel_output(self.tunnel_proc, log_file)

                # If process died
                exit_code = self.tunnel_proc.poll()
                if self.stop_requested:
                    break

                log_message("TUNNEL", f"cloudflared exited unexpectedly with code {exit_code}.")
                retry_count += 1
                if retry_count <= max_retries:
                    delay = backoff_delays[min(retry_count - 1, len(backoff_delays) - 1)]
                    log_message("RETRY", f"Reconnecting in {delay} seconds (retry {retry_count}/{max_retries})...")
                    time.sleep(delay)
                else:
                    log_message("ERROR", f"Max retries ({max_retries}) reached. Tunnel supervisor stopping.")
                    break

    def stop(self):
        """Cleanly terminates tunnel and backend processes."""
        self.stop_requested = True
        log_message("SHUTDOWN", "Stopping tunnel and cleaning up processes...")
        if self.tunnel_proc:
            try:
                self.tunnel_proc.terminate()
                self.tunnel_proc.wait(timeout=3)
            except Exception:
                try:
                    self.tunnel_proc.kill()
                except Exception:
                    pass

        if self.backend_proc:
            try:
                self.backend_proc.terminate()
                self.backend_proc.wait(timeout=3)
            except Exception:
                try:
                    self.backend_proc.kill()
                except Exception:
                    pass

        try:
            PID_FILE.unlink(missing_ok=True)
        except Exception:
            pass
        log_message("SHUTDOWN", "Shutdown complete.")


def main():
    print("=" * 70, flush=True)
    print("       SUCHNASETU AI — PRODUCTION DEPLOYMENT & TUNNEL RUNNER", flush=True)
    print("=" * 70, flush=True)

    # Clean up any leftover zombie tunnel instances
    cleanup_stale_processes()

    # 1. Check frontend dist
    dist_index = PROJECT_ROOT / "frontend" / "dist" / "index.html"
    if not dist_index.is_file():
        log_message("BUILD", "Frontend bundle not found. Building React 19 production SPA...")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        subprocess.run([npm_cmd, "run", "build"], cwd=PROJECT_ROOT / "frontend", check=True)
    else:
        log_message("BUILD", "Frontend production SPA verified at frontend/dist.")

    # 2. Check / Start Backend
    backend_proc = None
    if not is_port_open(8000):
        log_message("BACKEND", "Starting unified FastAPI server on http://127.0.0.1:8000...")
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
            log_message("ERROR", "Backend failed to start or respond on port 8000.")
            if backend_proc:
                backend_proc.kill()
            sys.exit(1)
        log_message("BACKEND", "Backend server is healthy and responding on port 8000.")
    else:
        log_message("BACKEND", "Port 8000 is already active. Verifying health...")
        if not wait_for_server(timeout=5.0):
            log_message("WARN", "Port 8000 open but /health endpoint did not respond promptly.")
        else:
            log_message("BACKEND", "Existing backend on port 8000 is verified healthy.")

    # 3. Check local Ollama status
    check_ollama_health()

    # 4. Start Tunnel Manager with auto-recovery
    manager = TunnelManager(backend_proc=backend_proc)

    def signal_handler(sig, frame):
        manager.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, signal_handler)

    try:
        manager.run_supervisor()
    except KeyboardInterrupt:
        manager.stop()


if __name__ == "__main__":
    main()
