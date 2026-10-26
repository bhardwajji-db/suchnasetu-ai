"""
Sanitizes machine-specific absolute paths across repository documentation and scripts.
Replaces personal Windows paths with clean relative paths or generic placeholders.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REPLACEMENTS = [
    # Absolute file:/// URIs
    (".", "."),
    (".", "."),
    # Absolute local paths with backslashes
    ("C:\\Users\\<developer>\\OneDrive\\Desktop\\AI-Projects\\Hacktober fest\\ps2", "."),
    (".", "."),
    ("C:\\Users\\<developer>\\OneDrive\\Desktop\\OM\\Hacktober", "<reference-dir>"),
    ("<reference-dir>", "<reference-dir>"),
    # Local Ollama binary path
    ("ollama.exe", "ollama"),
    ("ollama", "ollama"),
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
    for target, repl in REPLACEMENTS:
        content = content.replace(target, repl)
        
    if content != original:
        p.write_text(content, encoding="utf-8")
        return 1
    return 0

def main():
    modified_count = 0
    # Walk through tracked files
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip .git, node_modules, .venv, .backup
        dirs[:] = [d for d in dirs if d not in [".git", "node_modules", ".venv", ".pytest_cache", ".sessions", ".backup"]]
        for f in files:
            file_path = Path(root) / f
            if file_path.suffix.lower() in EXTENSIONS:
                if sanitize_file(file_path):
                    print(f"Sanitized: {file_path.relative_to(PROJECT_ROOT)}")
                    modified_count += 1
                    
    print(f"\nTotal files sanitized: {modified_count}")

if __name__ == "__main__":
    main()
