"""
Sanitizes machine-specific absolute paths across repository documentation and scripts.
Replaces personal Windows paths with clean relative paths or generic placeholders.
"""

import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REPLACEMENTS = [
    # Absolute file:/// URIs
    (r"./", "./"),
    (r"./", "./"),
    # Absolute local paths with backslashes
    (r"C:\\Users\\Avinash\\OneDrive\\Desktop\\AI-Projects\\Hacktober fest\\ps2", "."),
    (r".", "."),
    # Local Ollama binary path
    (r"C:\\Users\\Avinash\\AppData\\Local\\Programs\\Ollama\\ollama.exe", "ollama.exe"),
    (r"ollama.exe", "ollama.exe"),
    (r'"C:\\Users\\Avinash\\AppData\\Local\\Programs\\Ollama\\ollama.exe"', "ollama"),
]

TARGET_DIRS = [
    PROJECT_ROOT / "reports",
    PROJECT_ROOT / "docs",
    PROJECT_ROOT / "scripts",
    PROJECT_ROOT,
]

EXTENSIONS = [".md", ".html", ".py", ".json", ".bat", ".sh", ".txt"]

def sanitize_file(p: Path) -> int:
    try:
        content = p.read_text(encoding="utf-8")
    except Exception:
        return 0
        
    original = content
    for pattern, repl in REPLACEMENTS:
        content = re.sub(pattern, repl, content)
        
    if content != original:
        p.write_text(content, encoding="utf-8")
        return 1
    return 0

def main():
    modified_count = 0
    # Walk through tracked files
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip .git, node_modules, .venv
        dirs[:] = [d for d in dirs if d not in [".git", "node_modules", ".venv", ".pytest_cache", ".sessions"]]
        for f in files:
            file_path = Path(root) / f
            if file_path.suffix.lower() in EXTENSIONS:
                if sanitize_file(file_path):
                    print(f"Sanitized: {file_path.relative_to(PROJECT_ROOT)}")
                    modified_count += 1
                    
    print(f"\nTotal files sanitized: {modified_count}")

if __name__ == "__main__":
    main()
