"""
Thorough security scanner for SochnaSetu AI repository.
Scans:
1. All tracked files and working tree files for secrets, tokens, personal data, and absolute machine paths.
2. Full git log history across all commits.
"""

import os
import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SECRET_PATTERNS = [
    (r"ghp_[a-zA-Z0-9]{36,}", "GitHub Personal Access Token"),
    (r"sk-[a-zA-Z0-9]{20,}", "OpenAI / Cloud Secret Key"),
    (r"(?:AIzaSy)[a-zA-Z0-9\-_]{33}", "Google API Key"),
    (r"(?:hf_)[a-zA-Z0-9]{34,}", "Hugging Face Token"),
    (r"-----BEGIN (?:RSA|OPENSSH|DSA|EC)?\s*PRIVATE KEY-----", "Private Key"),
    (r"(?:password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{6,}['\"]", "Hardcoded Password"),
    (r"(?:bearer\s+[a-zA-Z0-9_\-\.]{20,})", "Bearer Token"),
]

PERSONAL_PATH_PATTERNS = [
    (r"C:[\\/]Users[\\/][a-zA-Z0-9_\-]+", "Machine Absolute User Path"),
    (r"file:///[a-zA-Z]:/[^ \)\"'>]+", "file:/// Absolute URI"),
]

def scan_working_tree():
    print("=== Scanning Working Tree Files ===")
    findings = []
    
    # Get all tracked files
    tracked = subprocess.check_output(["git", "ls-files"], cwd=PROJECT_ROOT, text=True).splitlines()
    
    for rel_path in tracked:
        file_path = PROJECT_ROOT / rel_path
        if not file_path.is_file():
            continue
        
        # Skip binary files like png, pdf, traineddata
        if file_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".pdf", ".traineddata", ".docx", ".zip"]:
            continue
            
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
            
        # Check secrets
        for pattern, desc in SECRET_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for m in matches:
                # Mask match for safe display
                val = m.group(0)
                masked = val[:4] + "..." + val[-3:] if len(val) > 7 else "****"
                line_no = content[:m.start()].count("\n") + 1
                findings.append({
                    "file": rel_path,
                    "line": line_no,
                    "type": "SECRET",
                    "desc": desc,
                    "masked": masked
                })
                
        # Check personal paths
        for pattern, desc in PERSONAL_PATH_PATTERNS:
            matches = re.finditer(pattern, content)
            for m in matches:
                val = m.group(0)
                line_no = content[:m.start()].count("\n") + 1
                findings.append({
                    "file": rel_path,
                    "line": line_no,
                    "type": "PERSONAL_PATH",
                    "desc": desc,
                    "value": val
                })
                
    return findings

def scan_git_history():
    print("=== Scanning Git Commit History ===")
    history_findings = []
    
    # Get list of commits
    commits = subprocess.check_output(["git", "log", "--format=%H|%s"], cwd=PROJECT_ROOT, text=True).splitlines()
    
    # Check commit diffs for secret patterns
    for c_info in commits:
        commit_hash, subject = c_info.split("|", 1)
        diff = subprocess.check_output(["git", "show", commit_hash], cwd=PROJECT_ROOT, text=True, errors="ignore")
        
        for pattern, desc in SECRET_PATTERNS:
            matches = re.finditer(pattern, diff, re.IGNORECASE)
            for m in matches:
                val = m.group(0)
                masked = val[:4] + "..." + val[-3:] if len(val) > 7 else "****"
                history_findings.append({
                    "commit": commit_hash[:8],
                    "subject": subject,
                    "type": "HISTORICAL_SECRET",
                    "desc": desc,
                    "masked": masked
                })
                
    return history_findings

if __name__ == "__main__":
    findings = scan_working_tree()
    history = scan_git_history()
    
    print(f"\nWorking tree findings: {len(findings)}")
    secrets = [f for f in findings if f["type"] == "SECRET"]
    paths = [f for f in findings if f["type"] == "PERSONAL_PATH"]
    print(f"  - Secrets: {len(secrets)}")
    for s in secrets:
        print(f"    [!] {s['file']}:{s['line']} - {s['desc']} ({s['masked']})")
    print(f"  - Machine Absolute Paths: {len(paths)}")
    for p in paths[:10]:
        print(f"    [-] {p['file']}:{p['line']} - {p['value']}")
    if len(paths) > 10:
        print(f"    ... and {len(paths) - 10} more paths.")
        
    print(f"\nGit history findings: {len(history)}")
    for h in history:
        print(f"  [!] Commit {h['commit']} ({h['subject']}) - {h['desc']} ({h['masked']})")
