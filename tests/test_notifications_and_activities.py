"""
Tests for User Notifications and Activity Audit Trail endpoints.
Validates real persistence, unread counting, dismissal, and timeline auditing.
"""

from fastapi.testclient import TestClient
from notice2action.api.server import app
from notice2action.storage.db import get_db

client = TestClient(app)


def test_user_notifications_and_activities_lifecycle():
    # 1. Fetch notifications for current user/guest
    resp = client.get("/api/user/notifications")
    assert resp.status_code == 200
    data = resp.json()
    assert "notifications" in data
    assert "unread_count" in data
    assert "total" in data

    # 2. Add an activity and a notification directly to test lifecycle
    db = get_db()
    test_user_id = "test_citizen_42"

    notif = db.create_notification(
        user_id=test_user_id,
        title="Application Deadline Approaching",
        message="Scholarship portal closes in 48 hours.",
        type="deadline",
    )
    assert notif["id"].startswith("notif_")
    assert notif["is_read"] is False

    # Mark as read
    ok = db.mark_notification_read(test_user_id, notif["id"])
    assert ok is True

    # Mark all as read
    count = db.mark_all_notifications_read(test_user_id)
    assert isinstance(count, int)

    # Dismiss notification
    dismissed = db.dismiss_notification(test_user_id, notif["id"])
    assert dismissed is True

    # List notifications (excluding dismissed)
    active = db.list_notifications_for_user(test_user_id, include_dismissed=False)
    assert all(n["id"] != notif["id"] for n in active)

    # 3. Test activity recording and retrieval
    act = db.record_activity(
        user_id=test_user_id,
        activity_type="notice_analyzed",
        title="Analyzed State Scholarship Circular",
        description="Extracted 5 verified facts and 3 action items.",
    )
    assert act["id"].startswith("act_")

    activities = db.list_activities_for_user(test_user_id)
    assert len(activities) > 0
    assert activities[0]["activity_type"] == "notice_analyzed"
    assert "State Scholarship" in activities[0]["title"]
