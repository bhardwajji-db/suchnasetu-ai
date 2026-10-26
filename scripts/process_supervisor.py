"""
SuchnaSetu AI — Reliable Windows Process Supervisor
Manages the lifecycle of backend, frontend, and local AI services.
Provides deterministic startup verification, PID tree tracking, signal trapping,
and safe shutdown without killing unrelated Node/Python processes or pre-existing Ollama services.
"""

import os
import sys
import time
import json
import socket
import signal
import ctypes
import shutil
import urllib.request
import urllib.error
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PID_LOCKFILE = PROJECT_ROOT / ".launcher_pids.json"

# Global state for signal/cleanup handling
supervisor_state: Dict[str, Any] = {
    "backend_proc": None,
    "frontend_proc": None,
    "ollama_proc": None,
    "ollama_owned": False,
    "backend_pid": None,
    "frontend_pid": None,
    "ollama_pid": None,
    "cleaned_up": False,
}


def log(msg: str):
    print(f"[SUPERVISOR] {msg}", flush=True)


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check whether a TCP port is currently open and bound."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def check_http_endpoint(url: str, timeout: float = 1.5) -> bool:
    """Check if an HTTP URL responds with HTTP 200-399."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SuchnaSetu-Supervisor"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 400
    except Exception:
        return False


def get_ollama_status() -> Dict[str, Any]:
    """Inspect local Ollama server and configured model status."""
    url = "http://127.0.0.1:11434/api/tags"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SuchnaSetu-Supervisor"})
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name", "") for m in data.get("models", [])]
                return {
                    "running": True,
                    "models": models,
                    "has_gemma4": any("gemma4" in m for m in models),
                }
    except Exception:
        pass
    return {"running": False, "models": [], "has_gemma4": False}


def is_project_process(pid: Optional[int], expected_type: str = "any") -> bool:
    """
    Verifies that a PID actually belongs to this project before attempting termination.
    Guards against stale lockfiles targeting unrelated system/user processes if PIDs recycle.
    """
    if not pid or pid <= 4:
        return False

    if sys.platform == "win32":
        try:
            cmd = [
                "powershell",
                "-NoProfile",
                "-Command",
                f"(Get-CimInstance Win32_Process -Filter 'ProcessId = {pid}').CommandLine",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=3.0)
            cmdline = res.stdout.strip().lower()
            if not cmdline:
                # Process is already dead or not found
                return False

            # Type-specific verification
            if expected_type == "ollama":
                return "ollama" in cmdline
            elif expected_type == "backend":
                return any(k in cmdline for k in ("uvicorn", "notice2action", "server:app", "ps2"))
            elif expected_type == "frontend":
                return any(k in cmdline for k in ("vite", "suchnasetu", "sochnasetu", "node", "frontend"))
            elif expected_type == "supervisor":
                return any(k in cmdline for k in ("process_supervisor", "run_sochnasetu"))
            else:
                return any(k in cmdline for k in (
                    "ps2", "suchnasetu", "sochnasetu", "notice2action", "uvicorn", "vite", "process_supervisor"
                ))
        except Exception as e:
            log(f"Warning checking process identity for PID {pid}: {e}")
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except Exception:
            return False


def kill_pid_tree(pid: Optional[int], expected_type: str = "any"):
    """Terminate a specific process tree by PID only if verified as belonging to this project."""
    if not pid:
        return
    if not is_project_process(pid, expected_type):
        log(f"PID {pid} ({expected_type}) is either already stopped or not a project process. Skipping termination.")
        return

    log(f"Stopping verified project process PID {pid} and its children...")
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception as e:
            log(f"Warning: taskkill on PID {pid} failed: {e}")
    else:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        except Exception as e:
            log(f"Warning: kill on PID {pid} failed: {e}")


def cleanup_launcher_processes():
    """Clean up only processes owned by this launcher."""
    if supervisor_state["cleaned_up"]:
        return
    supervisor_state["cleaned_up"] = True

    log("Initiating graceful shutdown of launcher-owned processes...")

    # Stop Frontend
    if supervisor_state.get("frontend_proc"):
        try:
            kill_pid_tree(supervisor_state["frontend_proc"].pid, "frontend")
        except Exception:
            pass
    elif supervisor_state.get("frontend_pid"):
        kill_pid_tree(supervisor_state["frontend_pid"], "frontend")

    # Stop Backend
    if supervisor_state.get("backend_proc"):
        try:
            kill_pid_tree(supervisor_state["backend_proc"].pid, "backend")
        except Exception:
            pass
    elif supervisor_state.get("backend_pid"):
        kill_pid_tree(supervisor_state["backend_pid"], "backend")

    # Stop Ollama ONLY if this launcher started it
    if supervisor_state.get("ollama_owned"):
        log("Stopping launcher-owned Ollama server...")
        if supervisor_state.get("ollama_proc"):
            kill_pid_tree(supervisor_state["ollama_proc"].pid, "ollama")
        elif supervisor_state.get("ollama_pid"):
            kill_pid_tree(supervisor_state["ollama_pid"], "ollama")
    else:
        log("Preserving pre-existing Ollama service (untouched).")

    # Remove lockfile
    if PID_LOCKFILE.exists():
        try:
            PID_LOCKFILE.unlink()
        except Exception:
            pass

    # Verify port release
    time.sleep(1.0)
    p8000 = is_port_in_use(8000)
    p5173 = is_port_in_use(5173)
    if not p8000 and not p5173:
        log("Ports 8000 and 5173 successfully released.")
    else:
        log(f"Port status check: 8000 in use={p8000}, 5173 in use={p5173}")
    log("Cleanup complete.")


def register_console_ctrl_handler():
    """Windows console event handler to trap terminal close or logoff."""
    if sys.platform != "win32":
        return

    HANDLER_ROUTINE = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_ulong)

    def _console_ctrl_handler(ctrl_type):
        # 0: CTRL_C_EVENT, 1: CTRL_BREAK_EVENT, 2: CTRL_CLOSE_EVENT, 5: CTRL_LOGOFF_EVENT, 6: CTRL_SHUTDOWN_EVENT
        log(f"Caught console event: {ctrl_type}. Cleaning up...")
        cleanup_launcher_processes()
        return True

    # Keep a reference to prevent garbage collection
    global _ctrl_handler_ref
    _ctrl_handler_ref = HANDLER_ROUTINE(_console_ctrl_handler)
    ctypes.windll.kernel32.SetConsoleCtrlHandler(_ctrl_handler_ref, True)


def save_pid_lockfile():
    """Persist tracked PIDs for recovery and external inspection."""
    data = {
        "supervisor_pid": os.getpid(),
        "backend_pid": supervisor_state.get("backend_pid"),
        "frontend_pid": supervisor_state.get("frontend_pid"),
        "ollama_owned": supervisor_state.get("ollama_owned", False),
        "ollama_pid": supervisor_state.get("ollama_pid"),
        "created_at": time.time(),
    }
    with open(PID_LOCKFILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def stop_saved_processes():
    """Read lockfile and terminate previously tracked processes with identity verification."""
    if not PID_LOCKFILE.exists():
        log("No active launcher lockfile found (.launcher_pids.json).")
        return

    try:
        with open(PID_LOCKFILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        log(f"Corrupt or unreadable lockfile: {e}. Removing stale lockfile.")
        try:
            PID_LOCKFILE.unlink()
        except Exception:
            pass
        return

    log("Found active lockfile. Stopping previous launcher processes...")
    current_pid = os.getpid()

    # Terminate frontend and backend child trees
    if data.get("frontend_pid"):
        kill_pid_tree(data["frontend_pid"], "frontend")
    if data.get("backend_pid"):
        kill_pid_tree(data["backend_pid"], "backend")
    if data.get("ollama_owned") and data.get("ollama_pid"):
        kill_pid_tree(data["ollama_pid"], "ollama")

    # Terminate previous supervisor process if it's still alive
    prev_sup_pid = data.get("supervisor_pid")
    if prev_sup_pid and prev_sup_pid != current_pid:
        kill_pid_tree(prev_sup_pid, "supervisor")

    if PID_LOCKFILE.exists():
        try:
            PID_LOCKFILE.unlink()
        except Exception:
            pass
    log("Previous processes stopped.")


def start_supervisor():
    """Main supervisor workflow with readiness gates and failure cleanup."""
    log("==================================================================")
    log("        SOCHNASETU AI -- PROCESS SUPERVISOR & LAUNCHER            ")
    log("==================================================================")

    # 1. Check if previous instance is running
    if PID_LOCKFILE.exists():
        log("Previous instance lockfile detected. Cleaning up stale launcher...")
        stop_saved_processes()
        time.sleep(1.0)

    # 2. Check ports 8000 and 5173
    if is_port_in_use(8000):
        log("Error: Port 8000 is already in use by another process. Please close it first.")
        sys.exit(1)
    if is_port_in_use(5173):
        log("Error: Port 5173 is already in use by another process. Please close it first.")
        sys.exit(1)

    # 3. Check Ollama
    log("[1/3] Inspecting Ollama server status...")
    ollama_info = get_ollama_status()
    if ollama_info["running"]:
        log("Ollama server is already running and responsive.")
        supervisor_state["ollama_owned"] = False
        if ollama_info["has_gemma4"]:
            log("Configured model 'gemma4:latest' verified present locally.")
        else:
            log("Note: 'gemma4:latest' not found. Available models: " + ", ".join(ollama_info["models"]))
            log("System will use rule-based fallback without attempting unapproved downloads.")
    else:
        log("Ollama is not running. Attempting to start local Ollama server...")
        ollama_bin = shutil.which("ollama")
        if not ollama_bin:
            default_path = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe"
            if default_path.exists():
                ollama_bin = str(default_path)

        if ollama_bin:
            proc = subprocess.Popen(
                [ollama_bin, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False,
            )
            supervisor_state["ollama_proc"] = proc
            supervisor_state["ollama_pid"] = proc.pid
            supervisor_state["ollama_owned"] = True
            log(f"Started Ollama server (PID {proc.pid}). Waiting for initialization...")

            # Wait for Ollama to become responsive
            ready = False
            for _ in range(15):
                time.sleep(1.0)
                if get_ollama_status()["running"]:
                    ready = True
                    break
            if ready:
                log("Ollama server initialized successfully.")
            else:
                log("Warning: Ollama did not respond within 15 seconds. Proceeding anyway.")
        else:
            log("Ollama binary not found. Application will operate in deterministic fallback mode.")
            supervisor_state["ollama_owned"] = False

    # 4. Start Backend (0.0.0.0 allows LAN/Wi-Fi phone testing while maintaining local browser access)
    log("[2/3] Launching FastAPI Backend on http://0.0.0.0:8000 (accessible on LAN & localhost)...")
    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "notice2action.api.server:app",
        "--app-dir",
        "src",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]
    try:
        backend_proc = subprocess.Popen(
            backend_cmd,
            cwd=str(PROJECT_ROOT),
        )
        supervisor_state["backend_proc"] = backend_proc
        supervisor_state["backend_pid"] = backend_proc.pid
        save_pid_lockfile()
        log(f"Backend started with PID {backend_proc.pid}. Waiting for health check...")
    except Exception as e:
        log(f"Failed to start backend: {e}")
        cleanup_launcher_processes()
        sys.exit(1)

    # Health check backend
    backend_ready = False
    for _ in range(25):
        time.sleep(0.5)
        if backend_proc.poll() is not None:
            log(f"Backend process terminated unexpectedly with code {backend_proc.returncode}.")
            cleanup_launcher_processes()
            sys.exit(1)
        if check_http_endpoint("http://127.0.0.1:8000/api/health"):
            backend_ready = True
            break

    if not backend_ready:
        log("Backend failed health check at /api/health within 12 seconds.")
        cleanup_launcher_processes()
        sys.exit(1)
    log("FastAPI backend is healthy (HTTP 200).")

    # 5. Start Frontend (0.0.0.0 allows mobile devices on same Wi-Fi to load UI)
    log("[3/3] Launching React 19 Frontend on http://0.0.0.0:5173 (LAN + localhost)...")
    frontend_dir = PROJECT_ROOT / "frontend"
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    try:
        frontend_proc = subprocess.Popen(
            [npm_cmd, "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"],
            cwd=str(frontend_dir),
        )
        supervisor_state["frontend_proc"] = frontend_proc
        supervisor_state["frontend_pid"] = frontend_proc.pid
        save_pid_lockfile()
        log(f"Frontend started with PID {frontend_proc.pid}. Waiting for Vite server...")
    except Exception as e:
        log(f"Failed to start frontend: {e}")
        cleanup_launcher_processes()
        sys.exit(1)

    # Health check frontend
    frontend_ready = False
    for _ in range(30):
        time.sleep(0.5)
        if frontend_proc.poll() is not None:
            log(f"Frontend process terminated unexpectedly with code {frontend_proc.returncode}.")
            cleanup_launcher_processes()
            sys.exit(1)
        if check_http_endpoint("http://127.0.0.1:5173/"):
            frontend_ready = True
            break

    if not frontend_ready:
        log("Frontend failed to respond within 15 seconds.")
        cleanup_launcher_processes()
        sys.exit(1)
    log("React frontend is ready (HTTP 200).")

    # 6. Save PID lockfile
    save_pid_lockfile()

    # 7. Open Browser
    log("Opening default browser at http://localhost:5173...")
    webbrowser.open("http://localhost:5173")

    # Discover local LAN IP
    lan_ip = "127.0.0.1"
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            candidate = info[4][0]
            if not candidate.startswith("127.") and not candidate.startswith("169.254."):
                lan_ip = candidate
                break
    except Exception:
        pass

    log("==================================================================")
    log("  All services active!")
    log("  * Local Web UI:    http://localhost:5173")
    log(f"  * Network / Phone: http://{lan_ip}:5173")
    log("  * Local Backend:   http://localhost:8000/docs")
    log(f"  * Network Backend: http://{lan_ip}:8000/docs")
    log("  * Ollama Local AI: http://127.0.0.1:11434 (Preserved on localhost)")
    log("  * PID Tracking:    .launcher_pids.json")
    log("  Press Ctrl+C in this window at any time to shut down cleanly.")
    log("==================================================================")

    # 8. Supervise until shutdown
    try:
        while True:
            time.sleep(1.0)
            if backend_proc.poll() is not None:
                log("Backend process exited unexpectedly. Initiating cleanup...")
                break
            if frontend_proc.poll() is not None:
                log("Frontend process exited unexpectedly. Initiating cleanup...")
                break
    except KeyboardInterrupt:
        log("\nCtrl+C detected.")
    finally:
        cleanup_launcher_processes()


def main():
    # Register POSIX & Windows handlers
    signal.signal(signal.SIGINT, lambda sig, frame: cleanup_launcher_processes())
    signal.signal(signal.SIGTERM, lambda sig, frame: cleanup_launcher_processes())
    register_console_ctrl_handler()

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--stop", "stop"]:
            stop_saved_processes()
            return
        elif arg in ["--status", "status"]:
            p8000 = is_port_in_use(8000)
            p5173 = is_port_in_use(5173)
            ollama = get_ollama_status()
            lock = PID_LOCKFILE.exists()
            print(f"Backend (Port 8000):   {'ACTIVE' if p8000 else 'INACTIVE'}")
            print(f"Frontend (Port 5173):  {'ACTIVE' if p5173 else 'INACTIVE'}")
            print(f"Ollama Server (11434): {'ACTIVE' if ollama['running'] else 'INACTIVE'}")
            print(f"Tracked Launcher Lock: {'PRESENT' if lock else 'NONE'}")
            return

    start_supervisor()


if __name__ == "__main__":
    main()
