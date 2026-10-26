"""

Unit tests for SuchnaSetu AI SQLite database persistence layer.

Verifies ACID properties, restart survival, schema migrations, and file storage.

"""



import tempfile

import time

from pathlib import Path

import pytest



from notice2action.storage.db import DatabaseManager, SCHEMA_VERSION





@pytest.fixture

def temp_db():

    with tempfile.TemporaryDirectory() as tmp_dir:

        tmp_path = Path(tmp_dir)

        db_file = tmp_path / "test.db"

        uploads_dir = tmp_path / "uploads"

        mgr = DatabaseManager(db_path=db_file, uploads_dir=uploads_dir)

        try:

            yield mgr

        finally:

            mgr.close()





def test_schema_initialization(temp_db):

    """Verifies tables and schema migration version are correctly initialized."""

    conn = temp_db.get_connection()

    cur = conn.execute("SELECT version, description FROM schema_migrations WHERE version = 1;")

    row = cur.fetchone()

    assert row is not None

    assert row["version"] == 1

    assert "Initial SuchnaSetu AI" in row["description"]



    # Verify migration v2

    cur_v2 = conn.execute("SELECT version, description FROM schema_migrations WHERE version = 2;")

    row_v2 = cur_v2.fetchone()

    assert row_v2 is not None

    assert row_v2["version"] == 2

    assert "Add authentication" in row_v2["description"]



    # Verify migration v3

    cur_v3 = conn.execute("SELECT version, description FROM schema_migrations WHERE version = 3;")

    row_v3 = cur_v3.fetchone()

    assert row_v3 is not None

    assert row_v3["version"] == 3

    assert "saved notices" in row_v3["description"]



    # Verify latest migration matches current SCHEMA_VERSION (version 5)

    cur_v4 = conn.execute("SELECT version, description FROM schema_migrations WHERE version = 4;")

    row_v4 = cur_v4.fetchone()

    assert row_v4 is not None

    assert row_v4["version"] == 4

    assert "user notifications" in row_v4["description"]

    cur_v5 = conn.execute("SELECT version, description FROM schema_migrations WHERE version = 5;")

    row_v5 = cur_v5.fetchone()

    assert row_v5 is not None

    assert row_v5["version"] == SCHEMA_VERSION

    assert "user preferences" in row_v5["description"]





def test_save_and_retrieve_document(temp_db):

    """Verifies binary file storage, hashing, and document metadata persistence."""

    sample_bytes = b"Official Circular Notice Content for Test"

    raw_text = "Official Circular Notice Content for Test"



    doc = temp_db.save_document(

        raw_text=raw_text,

        filename="circular_test.txt",

        content_bytes=sample_bytes,

        mime_type="text/plain",

        source_language="en",

        detected_language="en",

        language_confidence=0.99,

        is_mixed_language=False,

        ocr_confidence=98.5,

        ocr_engine="tesseract",

    )



    assert doc.id is not None

    assert doc.file_path is not None

    assert doc.file_size_bytes == len(sample_bytes)

    assert doc.file_hash is not None



    # Retrieve from DB

    retrieved = temp_db.get_document(doc.id)

    assert retrieved is not None

    assert retrieved.filename == "circular_test.txt"

    assert retrieved.raw_text == raw_text

    assert retrieved.source_language == "en"

    assert retrieved.ocr_confidence == 98.5

    assert retrieved.ocr_engine == "tesseract"





def test_save_and_retrieve_analysis(temp_db):

    """Verifies structured notice, core fields, summary, and checklist persistence."""

    fp = "sample_fp_12345"

    structured = {

        "issuing_authority": {"value": "Ministry of Education", "status": "stated"},

        "purpose": {"value": "Merit Scholarship", "status": "stated"},

        "deadline": {"value": "15 November 2026", "status": "stated"},

    }

    six_fields = {

        "authority": "Ministry of Education",

        "deadline": "15 November 2026",

    }

    summary = {

        "about": "Annual scholarship for merit students",

        "deadline": "15 November 2026",

        "required_action": "Apply online at portal",

    }

    checklist = {

        "items": [

            {

                "id": "step-1",

                "title": "Verify Eligibility",

                "action": "Ensure 60% in degree",

                "deadline": "10 November 2026",

                "is_mandatory": True,

            },

            {

                "id": "step-2",

                "title": "Submit Application",

                "action": "Upload certificates",

                "deadline": "15 November 2026",

                "is_mandatory": True,

            },

        ]

    }



    record = temp_db.save_analysis(

        session_id="session-test-01",

        fingerprint=fp,

        structured_notice=structured,

        six_core_fields=six_fields,

        summary=summary,

        action_checklist=checklist,

        reading_level="simple",

        source_language="en",

        output_language="hi",

        model_used="gemma4:latest",

    )



    assert record.id is not None

    assert record.fingerprint == fp

    assert record.output_language == "hi"



    # Query by fingerprint

    by_fp = temp_db.get_analysis_by_fingerprint(fp)

    assert by_fp is not None

    assert by_fp.id == record.id

    assert by_fp.summary["about"] == "Annual scholarship for merit students"

    assert len(by_fp.action_checklist["items"]) == 2



    # Query checklist items

    items = temp_db.get_checklist_items_for_fingerprint(fp)

    assert len(items) == 2

    assert items[0].id == "step-1"

    assert items[0].completed is False



    # Mark item 1 completed

    success = temp_db.set_checklist_item_completed("step-1", True)

    assert success is True



    # Re-query checklist items to verify completion state persisted

    updated_items = temp_db.get_checklist_items_for_fingerprint(fp)

    assert updated_items[0].completed is True

    assert updated_items[0].completed_at is not None

    assert updated_items[1].completed is False





def test_database_persistence_across_restart(temp_db):

    """

    Mandatory persistence test:

    Simulates a backend crash/restart by dropping the database manager

    and opening a fresh connection to the same SQLite file.

    """

    db_file = temp_db.db_path

    uploads_dir = temp_db.uploads_dir



    # 1. Write document and analysis

    doc = temp_db.save_document(

        raw_text="Persisted notice across backend reboot",

        filename="reboot_notice.txt",

        source_language="hi",

        detected_language="hi",

    )



    analysis = temp_db.save_analysis(

        session_id="reboot-sess-99",

        fingerprint="reboot_fp_99",

        structured_notice={"purpose": {"value": "Flood Relief Fund"}},

        six_core_fields={"authority": "Disaster Management Authority"},

        summary={"about": "Relief assistance for flood victims"},

        action_checklist={

            "items": [

                {"id": "reboot-step-1", "title": "Submit Claim", "action": "Visit Tahsil office"}

            ]

        },

        document_id=doc.id,

        source_language="hi",

        output_language="hi",

    )



    temp_db.set_checklist_item_completed("reboot-step-1", True)

    temp_db.set_setting("active_theme", "high_contrast")

    temp_db.close()



    # 2. Simulate Backend Restart: instantiate brand new DatabaseManager

    restarted_db = DatabaseManager(db_path=db_file, uploads_dir=uploads_dir)

    try:

        # 3. Verify all records survived

        rebooted_doc = restarted_db.get_document(doc.id)

        assert rebooted_doc is not None

        assert rebooted_doc.raw_text == "Persisted notice across backend reboot"

        assert rebooted_doc.source_language == "hi"



        rebooted_analysis = restarted_db.get_analysis(analysis.id)

        assert rebooted_analysis is not None

        assert rebooted_analysis.summary["about"] == "Relief assistance for flood victims"



        rebooted_items = restarted_db.get_checklist_items_for_fingerprint("reboot_fp_99")

        assert len(rebooted_items) == 1

        assert rebooted_items[0].completed is True



        setting_val = restarted_db.get_setting("active_theme")

        assert setting_val == "high_contrast"

    finally:

        restarted_db.close()





def test_qa_and_confirmations_persistence(temp_db):

    """Verifies user confirmations and grounded Q&A logging."""

    conf_id = temp_db.save_user_confirmation(

        field_name="deadline",

        confirmed_value="20 November 2026",

        original_value="Uncertain / Mid-November",

    )

    assert conf_id is not None



    qa_id = temp_db.save_qa_interaction(

        session_id="qa-sess-42",

        question="What is the application fee?",

        answer="No fee is required.",

        is_supported=True,

        evidence_quote="Application fee: Nil",

        target_lang="en",

    )

    assert qa_id is not None



    history = temp_db.get_qa_history("qa-sess-42")

    assert len(history) == 1

    assert history[0]["question"] == "What is the application fee?"

    assert history[0]["evidence_quote"] == "Application fee: Nil"





def test_demo_registry_persistence(temp_db):

    """Verifies demo library notices registration and search."""

    temp_db.register_demo(

        demo_id="DEMO-TEST-01",

        title="UPSC Civil Services Scholarship Notice",

        category="Scholarship",

        source_file="scholarship/upsc_notice.txt",

        format_type="txt",

        source_lang="en",

        target_lang="hi",

        manifest_data={"ground_truth": {"authority": "UPSC", "deadline": "15 Nov 2026"}},

        is_synthetic=True,

    )



    demos = temp_db.list_demos(category="Scholarship")

    assert any(d["id"] == "DEMO-TEST-01" for d in demos)

    test_demo = next(d for d in demos if d["id"] == "DEMO-TEST-01")

    assert test_demo["title"] == "UPSC Civil Services Scholarship Notice"

    assert test_demo["source_lang"] == "en"



    # Search filter

    search_res = temp_db.list_demos(search_query="Civil Services")

    assert len(search_res) >= 1

    assert any(d["id"] == "DEMO-TEST-01" for d in search_res)



    empty_res = temp_db.list_demos(search_query="NonExistentKeyword")

    assert len(empty_res) == 0

