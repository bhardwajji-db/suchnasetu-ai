# 06 — DEADLINE TRACKING & PROACTIVE NOTIFICATIONS AUDIT
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** PS02 (Hack Day 2026)  
**Verification Date:** 2026-10-24  

---

## 1. Smart Deadline Extraction Capabilities

SochnaSetu AI's deadline engine distinguishes three distinct classes of deadlines:

1. **Explicit Absolute Deadlines:** Fixed dates such as `"15 November 2026 at 05:00 PM IST"`.
   - Engine parses date, time, and timezone.
   - Computes exact countdown in hours/days.
   - Status: `VERIFIED`.
2. **Ambiguous / Relative Deadlines:** Expressions such as `"within 15 days of gazette publication"` or `"forthwith"`.
   - Engine recognizes the absence of an explicit calendar date.
   - Computes a tentative date only if publication date is stated.
   - Status: `UNCERTAIN` (`requires_confirmation = True`), prompting user verification.
3. **Overdue / Expired Deadlines:** Notices whose deadlines have already passed.
   - Highlighted in red in the UI with an `EXPIRED` status badge.
   - Explanatory note: "This deadline has elapsed; verify if a corrigendum or extension circular has been published."

---

## 2. Proactive Alert Schedules & Reminder Hierarchy

Reminders are automatically computed and persisted into the `reminders` table in SQLite:
- **T-7 Days:** Initial preparation notice (Gather required certificates and affidavits).
- **T-3 Days:** Final document verification and fee payment reminder.
- **T-1 Day:** Urgent submission warning (24 hours remaining).
- **T-0 Day (Deadline Day):** Morning submission alert before portal closes.

---

## 3. Notification Channels Verification

| Notification Channel | Architecture / Transport | Configuration Status | Delivery Verification |
|---|---|---|---|
| **In-App Notification Banner** | React Toast & Notification Center | Enabled by default | **PASS** (Visible on Dashboard and Stale Warning Banner) |
| **Browser Push Notification** | HTML5 Notification API (`Notification.requestPermission`) | Browser Supported | **PASS** (Graceful fallback when permissions denied) |
| **Telegram Bot Dispatcher** | Async HTTP (`https://api.telegram.org/bot<TOKEN>/sendMessage`) | Configurable via `TELEGRAM_BOT_TOKEN` | **PASS** (Mock transport verified, credential check in place) |
| **Email (SMTP / SendGrid)** | Python `smtplib` / async background task | Configurable via `SMTP_HOST` | **PASS** (Isolated test transport verified, no unsolicited sends) |

### Restart & Idempotency Guarantee
- Reminders are stored in SQLite (`data/suchnasetu.db`).
- On backend boot, the scheduler loads all pending reminders with `status = 'PENDING'`.
- Completed or cancelled reminders are marked `status = 'SENT'` or `status = 'CANCELLED'`, preventing duplicate delivery.
