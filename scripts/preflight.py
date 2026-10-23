"""
Preflight Diagnostics CLI for SuchnaSetu AI.
"""

import sys
from pathlib import Path

# Ensure src is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from notice2action.config import run_preflight_diagnostics

def main():
    report = run_preflight_diagnostics()
    print("\nDiagnostic Results:")
    for item in report.items:
        status_label = "OK" if item.status == "ok" else ("WARN" if item.status == "warning" else "FAIL")
        print(f"  [{status_label}] {item.name}: {item.details}")
        if item.remedy:
            print(f"         Remedy: {item.remedy}")
    print(f"\nOverall System Status: {report.overall_status.upper()}\n")

if __name__ == "__main__":
    main()

