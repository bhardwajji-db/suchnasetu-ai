# Contributing to SuchnaSetu AI 🤝

Thank you for your interest in contributing to **SuchnaSetu AI** (Notice-to-Action Accessibility Assistant — PS02)!

This guide outlines our development workflow, coding standards, testing requirements, and submission processes.

---

## 🏛️ Code of Conduct & Core Principles

1. **Accessibility First:** Every UI component must be keyboard-navigable and include semantic markup with `aria-*` attributes (WCAG 2.1 AA compliance).
2. **Offline-First & Zero-Cost Privacy:** The core pipeline must remain 100% operational offline using local Ollama (`gemma4:latest`) and local Tesseract OCR. Never introduce mandatory paid cloud API dependencies.
3. **Strict Grounding:** Extracted facts and generated checklists must be strictly grounded in the source notice. If a deadline, fee, or requirement is unstated, it must remain explicitly labeled as `not_stated` rather than fabricated.

---

## 💻 Local Development Setup

### 1. Prerequisites
- **Python:** 3.11+
- **Node.js:** v20+ / v24+
- **Tesseract OCR:** v5.4.0+ with `eng`, `hin`, and `osd` language data.
- **Ollama:** Running locally with model `gemma4:latest` loaded (`ollama run gemma4`).

### 2. Initial Setup
```powershell
# Clone the repository
git clone https://github.com/bhardwajji-db/suchnasetu-ai.git
cd suchnasetu-ai

# Run automated setup
.\scripts\setup.ps1

# Run preflight diagnostics check
& .venv\Scripts\python scripts\preflight.py
```

### 3. Launching the Development Stack
```powershell
.\scripts\run.ps1
```
- FastAPI Backend: `http://127.0.0.1:8000` (API docs: `http://127.0.0.1:8000/docs`)
- React Frontend: `http://127.0.0.1:5173`

---

## 🧪 Testing Requirements

All contributions must pass both backend and frontend test suites before submission:

```powershell
# Run the entire test suite:
.\scripts\test.ps1

# Or run suites individually:
# Backend non-live tests:
& .venv\Scripts\python -m pytest -m "not live"

# Frontend Vitest suite & build check:
cd frontend
npm test -- --run
npm run build
```

---

## 🌿 Git Branching & Commit Conventions

- Use feature branches off `main`:
  - `feat/feature-name`
  - `fix/bug-fix-name`
  - `docs/documentation-update`
- Follow Conventional Commits:
  - `feat: add Tamil OCR support via tesseract language pack`
  - `fix: resolve viewport overflow on narrow mobile screens`
  - `docs: update setup guide for Linux users`

---

## 📄 License

By contributing to SuchnaSetu AI, you agree that your contributions will be licensed under the project's [LICENSE](LICENSE) (Apache License 2.0).
