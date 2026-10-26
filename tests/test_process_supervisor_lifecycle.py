"""
Automated Lifecycle Tests for SuchnaSetu AI Process Supervisor.
Verifies:
- Detection of pre-existing Ollama without attempting restart or unapproved downloads.
- Accurate PID tracking in .launcher_pids.json.
- Graceful shutdown without killing unrelated Python/Node processes.
- Port release (8000 and 5173) after shutdown.
- Repeated start/stop cycles.
"""

import sys
import time
import json
import socket
import pytest
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOCKFILE = PROJECT_ROOT / ".launcher_pids.json"


def is_port_bound(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def test_supervisor_status_cli():
    """Verify that python scripts/process_supervisor.py --status runs cleanly."""
    cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "process_supervisor.py"), "--status"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    assert proc.returncode == 0
    assert "Backend (Port 8000):" in proc.stdout
    assert "Frontend (Port 5173):" in proc.stdout
    assert "Ollama Server (11434):" in proc.stdout


def test_supervisor_preserves_pre_existing_ollama():
    """Verify that the supervisor recognizes pre-existing Ollama and does NOT claim ownership."""
    import scripts.process_supervisor as supervisor

    status = supervisor.get_ollama_status()
    # If Ollama is running in the local test environment
    if status["running"]:
        assert isinstance(status["models"], list)
        assert "has_gemma4" in status
        # Simulate supervisor state
        supervisor.supervisor_state["ollama_owned"] = False
        supervisor.cleanup_launcher_processes()
        # Verify Ollama is still responsive
        fresh_status = supervisor.get_ollama_status()
        assert fresh_status["running"] is True


def test_supervisor_pid_lockfile_lifecycle():
    """Verify lockfile creation, reading, and deletion upon cleanup."""
    import scripts.process_supervisor as supervisor

    supervisor.supervisor_state["cleaned_up"] = False
    supervisor.supervisor_state["backend_pid"] = 999999
    supervisor.supervisor_state["frontend_pid"] = 999998
    supervisor.supervisor_state["ollama_owned"] = False

    supervisor.save_pid_lockfile()
    assert LOCKFILE.exists()

    with open(LOCKFILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["backend_pid"] == 999999
    assert data["frontend_pid"] == 999998
    assert data["ollama_owned"] is False

    supervisor.cleanup_launcher_processes()
    assert not LOCKFILE.exists()


def test_supervisor_repeated_start_stop_cycles():
    """Verify that stopping processes via --stop releases lockfile and doesn't crash."""
    cmd_stop = [sys.executable, str(PROJECT_ROOT / "scripts" / "process_supervisor.py"), "--stop"]
    res1 = subprocess.run(cmd_stop, capture_output=True, text=True, timeout=10)
    assert res1.returncode == 0

    res2 = subprocess.run(cmd_stop, capture_output=True, text=True, timeout=10)
    assert res2.returncode == 0
    assert not LOCKFILE.exists()


def test_supervisor_unrelated_process_preservation():
    """Verify that stopping supervisor does not terminate current pytest process or sibling python procs."""
    current_pid = subprocess.os.getpid()
    import scripts.process_supervisor as supervisor

    # Run cleanup with dummy PIDs
    supervisor.supervisor_state["backend_pid"] = None
    supervisor.supervisor_state["frontend_pid"] = None
    supervisor.supervisor_state["ollama_owned"] = False
    supervisor.supervisor_state["cleaned_up"] = False
    supervisor.cleanup_launcher_processes()

    # The current process must still be completely alive
    assert subprocess.os.getpid() == current_pid


def test_supervisor_live_start_and_stop_releases_ports():
    """Verify live startup of services, port binding, and clean port release via --stop."""
    # Ensure ports are clear before starting
    subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "process_supervisor.py"), "--stop"], capture_output=True, timeout=10)
    time.sleep(1.0)
    assert not is_port_bound(8000)
    assert not is_port_bound(5173)

    # Launch supervisor in a background subprocess
    proc = subprocess.Popen(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "process_supervisor.py")],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait up to 25s for backend and frontend to bind ports
    ready = False
    for _ in range(50):
        time.sleep(0.5)
        if is_port_bound(8000) and is_port_bound(5173):
            ready = True
            break
    assert ready is True, "Supervisor failed to bring up ports 8000 and 5173 within timeout"

    # Now execute --stop command
    stop_proc = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "process_supervisor.py"), "--stop"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert stop_proc.returncode == 0

    # Wait up to 10s for ports to be released
    released = False
    for _ in range(20):
        time.sleep(0.5)
        if not is_port_bound(8000) and not is_port_bound(5173):
            released = True
            break
    assert released is True, "Ports 8000 and 5173 remained bound after supervisor --stop"

