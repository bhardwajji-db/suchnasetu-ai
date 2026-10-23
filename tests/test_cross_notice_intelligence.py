"""
Tests for Cross-Notice Intelligence & Workspace Service.
Verifies multi-document registry, chronological timeline generation,
relationship mapping, and contradiction/conflict detection.
"""

import pytest
from fastapi.testclient import TestClient
from notice2action.api.server import app
from notice2action.services.workspace_service import WorkspaceService
from notice2action.schemas import RelationshipConfidence, RelationshipType

client = TestClient(app)

NOTICE_ORIGINAL = """UNION PUBLIC SERVICE COMMISSION
Advertisement No. 04/2026
Dated: 01/08/2026

Applications are invited for Central Scholarship Scheme 2026.
Last date for online submission: October 15, 2026.
Application fee: Rs. 500.
"""

NOTICE_CORRIGENDUM = """UNION PUBLIC SERVICE COMMISSION
Corrigendum to Advertisement No. 04/2026
Dated: 15/09/2026

This corrigendum modifies and supersedes specific clauses of Advertisement No. 04/2026.
The last date for submission is extended to November 05, 2026.
The application fee is reduced to Rs. 250.
"""

NOTICE_CONFLICTING = """STATE WELFARE BOARD
Notification No. SWB/2026/88
Dated: 20/09/2026

Central Scholarship Scheme 2026
All candidates must submit physical forms.
Last date for submission: October 10, 2026.
"""


def test_workspace_service_add_and_build_report():
    ws = WorkspaceService("test_ws")
    doc1 = ws.add_notice(NOTICE_ORIGINAL, title="Original Notice")
    doc2 = ws.add_notice(NOTICE_CORRIGENDUM, title="Corrigendum")

    assert len(ws.get_notices()) == 2
    report = ws.build_report()

    assert len(report.timeline) == 2
    assert len(report.relationships) == 1

    rel = report.relationships[0]
    assert rel.relationship_type == RelationshipType.AMENDMENT
    assert rel.confidence_level == RelationshipConfidence.VERIFIED
    assert "Advertisement No" in rel.evidence_quote or "Corrigendum" in rel.evidence_quote


def test_workspace_service_conflict_detection():
    ws = WorkspaceService("test_conflict_ws")
    ws.add_notice(NOTICE_ORIGINAL, title="UPSC Original")
    ws.add_notice(NOTICE_CONFLICTING, title="State Board Contradiction")

    report = ws.build_report()
    assert len(report.conflicts) >= 1

    cnf = report.conflicts[0]
    assert cnf.field_name == "Application Deadline"
    assert cnf.conflict_severity == "CRITICAL"
    assert cnf.status == "UNRESOLVED"
    assert "October 15, 2026" in cnf.value_a or "October 15, 2026" in cnf.value_b
    assert "October 10, 2026" in cnf.value_a or "October 10, 2026" in cnf.value_b


def test_api_workspace_endpoints():
    client.post("/api/workspace/clear")

    add_resp1 = client.post(
        "/api/workspace/notices",
        json={"text": NOTICE_ORIGINAL, "title": "UPSC Circular 2026"},
    )
    assert add_resp1.status_code == 200
    doc1_id = add_resp1.json()["id"]

    add_resp2 = client.post(
        "/api/workspace/notices",
        json={"text": NOTICE_CORRIGENDUM, "title": "UPSC Corrigendum 2026"},
    )
    assert add_resp2.status_code == 200

    list_resp = client.get("/api/workspace/notices")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 2

    timeline_resp = client.get(f"/api/workspace/timeline?active_id={doc1_id}")
    assert timeline_resp.status_code == 200
    data = timeline_resp.json()
    assert len(data["timeline"]) == 2
    assert len(data["relationships"]) >= 1
