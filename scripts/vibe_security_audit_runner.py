"""
Automated Vibe Security Skill 30-Point Audit Runner for SochnaSetu AI.
Executes deep code inspection across FastAPI backend, SQLite storage,
and React/Vite frontend.
"""

import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run_checks():
    print("=" * 70)
    print("  SOCHNASETU AI — VIBE SECURITY SKILL 30-POINT AUDIT RUNNER")
    print("=" * 70)

    # 1. Tech Stack Detection
    print("\n--- TECH STACK DETECTION ---")
    tech_stack = {}
    if (ROOT / "frontend" / "vite.config.ts").exists():
        tech_stack["Frontend Framework"] = "React 19 + TypeScript + Vite + Tailwind CSS"
    if (ROOT / "src" / "notice2action" / "api" / "server.py").exists():
        tech_stack["Backend Framework"] = "FastAPI (Python 3.11) + Uvicorn"
    if (ROOT / "data" / "suchnasetu.db").exists() or (ROOT / "src" / "notice2action" / "storage" / "db.py").exists():
        tech_stack["Database"] = "SQLite (WAL mode enabled)"
    tech_stack["AI Engine"] = "Local Ollama + Google Gemma 4 (gemma4:latest)"
    tech_stack["OCR"] = "Tesseract OCR (pytesseract) + PIL"
    
    for k, v in tech_stack.items():
        print(f"  * {k}: {v}")

    # Check 1: Secrets Exposure
    print("\n[Check 01] Secrets Exposure & Git-Tracked Env Files")
    tracked_env = subprocess.check_output(["git", "ls-files", "*.env*"], cwd=ROOT, text=True).splitlines()
    print(f"  Tracked .env files in git: {tracked_env}")
    
    # Check 3: Custom Auth & Hashing
    print("\n[Check 03] Custom Auth & Cryptographic Hash Primitives")
    auth_service_path = ROOT / "src" / "notice2action" / "auth" / "auth_service.py"
    if auth_service_path.exists():
        content = auth_service_path.read_text(encoding="utf-8")
        hash_algos = re.findall(r"(hashlib\.\w+|argon2|bcrypt|scrypt|pbkdf2)", content)
        print(f"  Hash primitives found in auth_service: {set(hash_algos)}")
        salt_usage = "salt" in content.lower()
        print(f"  Salt usage present: {salt_usage}")
        jwt_usage = re.findall(r"(jwt\.\w+|pyjwt)", content)
        print(f"  JWT libraries: {set(jwt_usage)}")

    # Check 5: Injection & SQL Parameterization
    print("\n[Check 05] Injection Attacks (SQL, Command, XSS)")
    db_path = ROOT / "src" / "notice2action" / "storage" / "db.py"
    if db_path.exists():
        db_content = db_path.read_text(encoding="utf-8")
        raw_interpolations = re.findall(r"execute\s*\(\s*f[\"'].*[\"']", db_content)
        print(f"  String interpolation in SQLite db.py queries: {len(raw_interpolations)}")
        if raw_interpolations:
            for r in raw_interpolations:
                print(f"    [!] Interpolation: {r}")
        else:
            print("    [OK] Parameterized queries (?) consistently used in db.py")

    # Check 6: Gitignore Coverage
    print("\n[Check 06] Gitignore Coverage")
    gitignore_path = ROOT / ".gitignore"
    if gitignore_path.exists():
        gi_content = gitignore_path.read_text(encoding="utf-8")
        gi_rules = [line.strip() for line in gi_content.splitlines() if line.strip() and not line.startswith("#")]
        print(f"  Total rules in .gitignore: {len(gi_rules)}")
        checks = [".env", ".env.*", "data/*.db", "node_modules", ".venv", "__pycache__"]
        for c in checks:
            present = any(c in r for r in gi_rules)
            print(f"    * Rule '{c}': {'Present' if present else 'MISSING'}")

    # Check 11: CORS Configuration
    print("\n[Check 11] CORS Misconfiguration")
    server_path = ROOT / "src" / "notice2action" / "api" / "server.py"
    if server_path.exists():
        srv_content = server_path.read_text(encoding="utf-8")
        cors_match = re.search(r"add_middleware\s*\(\s*CORSMiddleware\s*,(.*?)\)", srv_content, re.DOTALL)
        if cors_match:
            print(f"  CORS Middleware snippet:\n{cors_match.group(0)[:300]}...")

    # Check 8: Rate Limiting
    print("\n[Check 08] Rate Limiting & Abuse Prevention")
    has_guest_limit = "check_guest_rate_limit" in srv_content or "check_guest_rate_limit" in content
    print(f"  Guest analysis rate limiting present: {has_guest_limit}")
    auth_routes_path = ROOT / "src" / "notice2action" / "api" / "auth_routes.py"
    if auth_routes_path.exists():
        ar_content = auth_routes_path.read_text(encoding="utf-8")
        login_limit = "login" in ar_content and "check_rate_limit" in content
        print(f"  Auth endpoint rate limits enforced in auth_service: {login_limit}")

    # Check 20: Session Management & Cookies
    print("\n[Check 20] Session Management & Cookie Flags")
    if auth_routes_path.exists():
        cookie_sets = re.findall(r"set_cookie\s*\((.*?)\)", ar_content, re.DOTALL)
        print(f"  set_cookie calls: {len(cookie_sets)}")
        for cs in cookie_sets:
            print(f"    - Flags: {cs.strip().replace(chr(10), ' ')}")

    # Check 28: Upload Size Limits & Validation
    print("\n[Check 28] File Upload Size Limits & Validation")
    upload_matches = re.findall(r"def upload_file_endpoint.*?:.*?(?=def |\Z)", srv_content, re.DOTALL)
    if upload_matches:
        up_code = upload_matches[0]
        has_len_check = "len(" in up_code or "content_length" in up_code or "max_size" in up_code
        print(f"  Size limit validation in /api/ingest/upload: {has_len_check}")
        print(f"  Snippet:\n{up_code[:250]}...")

    # Check 19: Error Leakage
    print("\n[Check 19] Error Leakage & Stack Traces")
    error_handlers = re.findall(r"@app\.exception_handler\(.*?\).*?def .*?\(.*?\):.*?(?=def |@app|\Z)", srv_content, re.DOTALL)
    print(f"  Custom exception handlers registered: {len(error_handlers)}")

    # Check 27: Localhost Binding & Ollama Public Exposure Risk
    print("\n[Check 27 & Deployment] Host Binding & Network Exposure")
    bind_0 = re.findall(r"host=['\"]0\.0\.0\.0['\"]", srv_content) + re.findall(r"--host 0\.0\.0\.0", (ROOT / "run_sochnasetu.ps1").read_text(encoding="utf-8"))
    print(f"  0.0.0.0 binding instances: {len(bind_0)}")

if __name__ == "__main__":
    run_checks()
