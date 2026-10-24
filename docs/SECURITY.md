# SuchnaSetu AI — Security & Privacy Architecture

This document outlines the security controls, data protection principles, and adversarial defenses implemented in SochnaSetu AI.

---

## 1. Local-First Privacy Guarantees

- **Zero Cloud Transmission:** All document text, user profiles, questions, and extracted facts remain strictly on the user's host machine.
- **Local Model Execution:** Ollama runs locally on `http://127.0.0.1:11434`. No cloud telemetry or third-party AI APIs are invoked during standard operation.
- **Local Database:** Notice data, checklists, and reminders persist in `data/suchnasetu.db`, which is git-ignored and never committed.

---

## 2. Adversarial Robustness & Prompt Injection Defense

Official government circulars often contain legal warnings, disclaimers, or adversarial text. SochnaSetu AI implements multi-layered defenses:

- **Untrusted Input Treatment:** Uploaded notice text is treated strictly as **DATA**, never as instructions.
- **Prompt Injection Filter (`src/notice2action/security.py`):**
  - Scans for jailbreak patterns (`[SYSTEM_OVERRIDE_ALERT]`, "DAN mode", "ignore all instructions").
  - Strips injection attempts before prompting the model.
  - Neutralizes fake warrants and fake grant scams.
- **Verification Test:** `tests/test_synthetic_demo_suite.py::test_demo_05_adversarial_prompt_injection` verifies prompt injection neutralization.

---

## 3. Ingestion & Storage Security

- **Path Traversal Prevention:** Uploaded filenames are sanitized via `Path(filename).name`, preventing writing outside `data/documents/`.
- **XML Entity Injection (XXE):** `.docx` files are parsed via `xml.etree.ElementTree` without entity resolution, neutralizing XML bombs.
- **SQL Injection Prevention:** All SQLite queries use parameterized placeholders (`?`).
