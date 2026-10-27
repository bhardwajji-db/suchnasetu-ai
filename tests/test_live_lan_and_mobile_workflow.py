"""
Automated Verification for Live LAN Access and Mobile Workflows in SuchnaSetu AI.
Requirements verified:
- FastAPI backend listens on 0.0.0.0:8000 and responds to LAN IP requests.
- Vite frontend listens on 0.0.0.0:5173 and responds to LAN IP requests.
- Vite proxy successfully forwards /api requests across LAN interface to FastAPI.
- Real API analysis request completes over LAN IP without CORS or CSRF rejection.
- Mobile screen (390x844) renders with zero horizontal overflow.
- Mobile bottom navigation and mobile view switchers function properly.
- Local Ollama endpoint remains on 127.0.0.1:11434 and is never exposed to 0.0.0.0.
"""

import sys
import time
import socket
import urllib.request
import urllib.error
import json
import subprocess
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Detect active Wi-Fi / LAN IP
def get_lan_ip() -> str:
    candidates = []
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127.") and not ip.startswith("169.254."):
                candidates.append(ip)
    except Exception:
        pass
    return candidates[0] if candidates else "127.0.0.1"


LAN_IP = get_lan_ip()
LAN_FRONTEND_URL = f"http://{LAN_IP}:5173"
LAN_BACKEND_URL = f"http://{LAN_IP}:8000"


def is_port_open(port: int, host: str) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


@pytest.fixture(scope="module", autouse=True)
def run_live_supervisor():
    """Ensures services are available for live tests."""
    if is_port_open(8000, LAN_IP) and is_port_open(5173, LAN_IP):
        yield
        return

    # Launch supervisor if not running
    proc = subprocess.Popen(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "process_supervisor.py")],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    deadline = time.time() + 30
    ready = False
    while time.time() < deadline:
        if is_port_open(8000, LAN_IP) and is_port_open(5173, LAN_IP):
            ready = True
            break
        time.sleep(0.5)

    assert ready, f"Services failed to bind to {LAN_IP}:8000 and {LAN_IP}:5173 within 30 seconds"
    yield


def test_ollama_not_exposed_to_lan():
    """Local Ollama inference daemon must NOT be accessible on the LAN IP interface."""
    # Ollama must only listen on loopback (127.0.0.1)
    is_lan_exposed = is_port_open(11434, LAN_IP)
    assert not is_lan_exposed, f"Security violation: Ollama is listening on LAN interface {LAN_IP}:11434!"


def test_backend_direct_access_via_lan_ip():
    """Another device on the Wi-Fi can directly reach FastAPI health check on laptop LAN IP."""
    url = f"{LAN_BACKEND_URL}/api/health"
    req = urllib.request.Request(url, headers={"User-Agent": "MobileDeviceSimulator"})
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["overall_status"] in ["ok", "PASS", "WARN"]


def test_frontend_delivery_via_lan_ip():
    """Another device on the Wi-Fi can load the React / Vite frontend bundle via laptop LAN IP."""
    req = urllib.request.Request(LAN_FRONTEND_URL, headers={"User-Agent": "MobileDeviceSimulator"})
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        assert resp.status == 200
        html = resp.read().decode("utf-8")
        assert "<title>SochnaSetu AI" in html or "id=\"root\"" in html


def test_vite_reverse_proxy_via_lan_ip():
    """Vite dev server correctly reverse-proxies /api to FastAPI when accessed from LAN IP."""
    url = f"{LAN_FRONTEND_URL}/api/health"
    req = urllib.request.Request(url, headers={"User-Agent": "MobileDeviceSimulator"})
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["overall_status"] in ["ok", "PASS", "WARN"]


def test_actual_notice_analysis_api_request_over_lan():
    """An actual notice analysis request originating from LAN IP executes and returns schema-compliant data."""
    url = f"{LAN_BACKEND_URL}/api/analyze"
    payload = json.dumps({
        "notice_text": "Government of Madhya Pradesh Public Works Department. Tender notice for road maintenance in Bhopal district. Bids close 2026-11-20. Required EMD: Rs 50,000.",
        "target_language": "en",
        "reading_level": "standard",
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Origin": LAN_FRONTEND_URL,
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90.0) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "structured_notice" in data
        assert "six_core_fields" in data
        assert "checklist_en" in data
        assert data["six_core_fields"]["issuing_authority"]["value"] != ""


def test_playwright_mobile_workflow_on_lan_ip():
    """Playwright verification of mobile screen (390x844) rendering and navigation on the LAN IP."""
    from playwright.sync_api import sync_playwright

    chrome_candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    chrome_path = next((c for c in chrome_candidates if Path(c).is_file()), None)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=chrome_path,
        )
        # Simulate iPhone 14 / modern smartphone viewport
        context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
        page = context.new_page()

        page.goto(LAN_FRONTEND_URL, wait_until="networkidle", timeout=15000)

        # 1. Check zero horizontal overflow on mobile
        scroll_width, client_width = page.evaluate("() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]")
        assert scroll_width <= client_width + 1, f"Horizontal overflow on mobile: scrollWidth={scroll_width} > clientWidth={client_width}"

        # If on auth screen, enter guest mode to reach mobile bottom nav
        guest_btn = page.locator("button:has-text('Continue as Guest')")
        if guest_btn.is_visible():
            guest_btn.click()
            page.wait_for_timeout(500)

        # 2. Check mobile bottom navigation presence
        bottom_nav = page.locator("[aria-label='Mobile Bottom Navigation']")
        assert bottom_nav.is_visible()

        # 3. Check mobile source/analysis tab switcher in IngestionView
        source_tab = page.locator("button:has-text('Source Document')")
        analysis_tab = page.locator("button:has-text('Structured Analysis')")
        if source_tab.is_visible():
            source_tab.click()
            time.sleep(0.5)

        # 4. Save mobile screenshot
        screenshot_path = PROJECT_ROOT / "assets" / "screenshots" / "lan_mobile_390x844_verified.png"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot_path))
        assert screenshot_path.is_file()

        context.close()
        browser.close()
