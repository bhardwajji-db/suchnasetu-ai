"""
Weekly Action Planner Service for SuchnaSetu AI.
Extracts assignment titles and submission dates from official notices,
manages user-isolated saved notices, evaluates weekly task schedules (today + 7 days),
flags ambiguous/tentative deadlines, and answers "What do I need to complete this week?".
"""

from __future__ import annotations

import re
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple

from notice2action.storage.db import get_db


class WeeklyActionPlannerService:
    """Provides weekly action planning, deadline extraction, and task prioritization."""

    def __init__(self):
        self.db = get_db()

    @staticmethod
    def parse_deadline_and_ambiguity(raw_deadline: Optional[str]) -> Tuple[Optional[date], bool, str]:
        """
        Parses a date string and determines if it is ambiguous, tentative, or exact.
        Returns: (parsed_date, is_ambiguous, reason)
        """
        if not raw_deadline or not raw_deadline.strip():
            return None, True, "No deadline specified in notice."

        text = raw_deadline.strip()
        lower = text.lower()

        # Check for ambiguity markers
        ambiguity_terms = [
            "tentative", "likely", "subject to change", "approx", "around",
            "within", "expected", "tbd", "to be announced", "unclear", "not stated"
        ]
        is_ambiguous = any(term in lower for term in ambiguity_terms)
        reason = "Date is tentative or subject to confirmation." if is_ambiguous else "Confirmed exact deadline."

        # Search for date pattern
        date_pattern = r"(\d{1,2}[-/]\d{1,2}[-/]\d{4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|[A-Za-z]+\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4})"
        match = re.search(date_pattern, text)
        if not match:
            return None, True, "No standard calendar date found in text."

        date_str = match.group(1).replace(",", "").strip()
        parsed_date: Optional[date] = None

        date_formats = [
            "%B %d %Y", "%d %B %Y", "%d %b %Y", "%b %d %Y",
            "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt).date()
                break
            except Exception:
                continue

        if not parsed_date:
            return None, True, f"Unrecognized date format: '{date_str}'"

        return parsed_date, is_ambiguous, reason

    @classmethod
    def extract_tasks_from_notice_text(
        cls, notice_title: str, notice_text: str, default_deadline: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extracts assignment/submission tasks, their specific titles, and deadlines from notice text.
        """
        tasks: List[Dict[str, Any]] = []

        # Look for assignment lines, submission lines, or deadline clauses
        lines = [line.strip() for line in notice_text.splitlines() if line.strip()]

        task_patterns = [
            r"(?:assignment|project|report|synopsis|thesis|fee|registration|submission|verification|application)\s*(?:no\.?|#)?\s*([0-9A-Za-z\s-]+)?(?::|—|-|\bis\b|\bdue\b)",
            r"(?:last date for|deadline for|submission of)\s+([^\n,;]+)",
        ]

        found_titles = set()

        for line in lines:
            for pat in task_patterns:
                m = re.search(pat, line, re.IGNORECASE)
                if m:
                    raw_name = m.group(0).strip()
                    # Clean up name
                    clean_name = re.sub(r"^(last date for|deadline for|submission of)\s+", "", raw_name, flags=re.IGNORECASE).strip()
                    if clean_name and len(clean_name) > 3 and clean_name.lower() not in found_titles:
                        found_titles.add(clean_name.lower())
                        parsed_d, is_amb, amb_reason = cls.parse_deadline_and_ambiguity(line)
                        if not parsed_d and default_deadline:
                            parsed_d, is_amb, amb_reason = cls.parse_deadline_and_ambiguity(default_deadline)

                        tasks.append({
                            "task_title": clean_name[:100],
                            "raw_line": line[:200],
                            "parsed_date": parsed_d.isoformat() if parsed_d else None,
                            "raw_deadline": default_deadline or line,
                            "is_ambiguous_date": is_amb,
                            "ambiguity_reason": amb_reason,
                        })

        # If no granular sub-tasks found, treat the notice itself as a primary task
        if not tasks:
            parsed_d, is_amb, amb_reason = cls.parse_deadline_and_ambiguity(default_deadline or notice_text)
            tasks.append({
                "task_title": notice_title or "Notice Action & Submission",
                "raw_line": (notice_text[:200] if notice_text else notice_title),
                "parsed_date": parsed_d.isoformat() if parsed_d else None,
                "raw_deadline": default_deadline or "Not Stated",
                "is_ambiguous_date": is_amb,
                "ambiguity_reason": amb_reason,
            })

        return tasks

    def get_weekly_plan(
        self, user_id: str, reference_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculates the 7-day action plan for the user's saved notices.
        Orders tasks chronologically (earliest first) and flags ambiguous items.
        """
        today = reference_date or date.today()
        week_end = today + timedelta(days=7)

        saved = self.db.list_saved_notices_for_user(user_id)

        all_tasks: List[Dict[str, Any]] = []
        seen_document_ids = set()

        for item in saved:
            doc_id = item["document_id"]
            if doc_id in seen_document_ids:
                continue
            seen_document_ids.add(doc_id)

            extracted = self.extract_tasks_from_notice_text(
                notice_title=item["title"],
                notice_text=item.get("raw_text") or item["title"],
                default_deadline=item.get("deadline") or item.get("submission_date")
            )

            for t in extracted:
                t["document_id"] = doc_id
                t["notice_title"] = item["title"]
                t["authority"] = item.get("authority", "")
                all_tasks.append(t)

        due_this_week: List[Dict[str, Any]] = []
        upcoming_later: List[Dict[str, Any]] = []
        past_due: List[Dict[str, Any]] = []
        ambiguous_tasks: List[Dict[str, Any]] = []

        for task in all_tasks:
            d_str = task.get("parsed_date")
            if not d_str:
                ambiguous_tasks.append(task)
                continue

            try:
                task_d = date.fromisoformat(d_str)
                diff = (task_d - today).days

                task["days_remaining"] = diff
                if diff < 0:
                    task["status"] = "EXPIRED"
                    past_due.append(task)
                elif 0 <= diff <= 7:
                    task["status"] = "DUE_THIS_WEEK"
                    if diff == 0:
                        task["urgency"] = "DUE_TODAY"
                    elif diff <= 2:
                        task["urgency"] = "CRITICAL"
                    else:
                        task["urgency"] = "UPCOMING"
                    due_this_week.append(task)
                else:
                    task["status"] = "UPCOMING_LATER"
                    upcoming_later.append(task)

                if task.get("is_ambiguous_date"):
                    ambiguous_tasks.append(task)

            except Exception:
                ambiguous_tasks.append(task)

        # Sort chronologically (earliest date first)
        due_this_week.sort(key=lambda x: (x.get("parsed_date") or "9999-99-99", x.get("task_title", "")))
        upcoming_later.sort(key=lambda x: (x.get("parsed_date") or "9999-99-99", x.get("task_title", "")))
        past_due.sort(key=lambda x: (x.get("parsed_date") or "0000-00-00", x.get("task_title", ""),), reverse=True)

        # Natural language synthesis for "What do I need to complete this week?"
        summary_text = self._generate_weekly_summary(today, week_end, due_this_week, ambiguous_tasks)

        return {
            "user_id": user_id,
            "reference_date": today.isoformat(),
            "week_window": {
                "start_date": today.isoformat(),
                "end_date": week_end.isoformat(),
            },
            "due_this_week": due_this_week,
            "due_this_week_count": len(due_this_week),
            "upcoming_later": upcoming_later,
            "past_due": past_due,
            "ambiguous_tasks": ambiguous_tasks,
            "total_saved_notices": len(saved),
            "summary": summary_text,
        }

    def _generate_weekly_summary(
        self, today: date, week_end: date, due_this_week: List[Dict[str, Any]], ambiguous_tasks: List[Dict[str, Any]]
    ) -> str:
        """Produces a grounded, polite natural language answer for weekly task questions."""
        start_fmt = today.strftime("%B %d, %Y")
        end_fmt = week_end.strftime("%B %d, %Y")

        if not due_this_week and not ambiguous_tasks:
            return (
                f"You have no tasks or submissions due this week ({start_fmt} to {end_fmt}) "
                "across your saved notices. All obligations are either completed or scheduled for later dates."
            )

        lines = [f"Here is what you need to complete this week ({start_fmt} to {end_fmt}):"]
        for idx, task in enumerate(due_this_week, 1):
            d_str = task.get("parsed_date")
            days = task.get("days_remaining", 0)
            day_label = "today" if days == 0 else (f"in {days} day" if days == 1 else f"in {days} days")
            lines.append(f"{idx}. **{task['task_title']}** — Due {d_str} ({day_label}). Source notice: \"{task['notice_title']}\".")

        if ambiguous_tasks:
            lines.append(
                f"\nNotice: {len(ambiguous_tasks)} task(s) have tentative or unconfirmed dates. "
                "Please verify with official authorities before planning submission."
            )

        return "\n".join(lines)


# Singleton instance
weekly_planner = WeeklyActionPlannerService()
