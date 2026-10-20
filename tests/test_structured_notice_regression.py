"""
Regression Tests for StructuredNotice Schema and Normalization (PS02).
Verifies robust handling of model variations in missing_information and uncertain_details:
- plain string lists
- dict objects from LLM completions ({'fact': ..., 'evidence_quote': ...})
- null/missing fact values
- null/missing evidence_quote values
- empty and malformed model responses
- valid StructuredNotice outputs
- incorrectly typed fields
"""

import pytest
from notice2action.schemas import (
    CertaintyStatus,
    ExtractedFact,
    StructuredNotice,
    NOT_STATED_LABEL,
    normalize_string_list,
    normalize_string_list_entry,
)
from notice2action.analysis import NoticeAnalyzer, parse_fact_dict


def make_dummy_fact(name: str = "test", value: str = "Test value") -> ExtractedFact:
    return ExtractedFact(
        field_name=name,
        value=value,
        status=CertaintyStatus.STATED,
        evidence_quote="Test value",
    )


def make_dummy_notice(**kwargs) -> StructuredNotice:
    fields = [
        "purpose", "eligibility", "deadline", "fee_or_cost",
        "required_documents", "contact_details", "required_actions", "important_conditions"
    ]
    data = {f: make_dummy_fact(f) for f in fields}
    data.update(kwargs)
    return StructuredNotice(**data)


# 1. missing_information as a list of strings
def test_missing_information_as_list_of_strings():
    raw_list = [
        "Application fee not specified",
        "  Selection criteria missing  ",
        "",  # Should be dropped
        "   ",  # Should be dropped
        "Hostel accommodation policy absent",
    ]
    sn = make_dummy_notice(missing_information=raw_list)
    assert sn.missing_information == [
        "Application fee not specified",
        "Selection criteria missing",
        "Hostel accommodation policy absent",
    ]


# 2. Model output containing dictionaries
def test_model_output_containing_dictionaries():
    raw_dicts = [
        {"fact": "Scholarship amount not mentioned", "evidence_quote": None},
        {"description": "Application link missing", "evidence_quote": None},
        {"value": "Bank account IFSC details not provided"},
    ]
    sn = make_dummy_notice(missing_information=raw_dicts)
    assert "Scholarship amount not mentioned" in sn.missing_information
    assert "Application link missing" in sn.missing_information
    assert "Bank account IFSC details not provided" in sn.missing_information
    assert len(sn.missing_information) == 3


# 3. Missing or null fact values
def test_missing_or_null_fact_values():
    raw_items = [
        {"fact": None, "value": "Backup contact person missing", "evidence_quote": None},
        {"fact": None, "description": "Submission portal URL absent"},
        {"fact": None, "value": None, "evidence_quote": None},  # Should be safely dropped
        {"fact": "", "evidence_quote": None},  # Should be safely dropped
        {"fact": "None", "evidence_quote": None},  # Literal 'None' should be dropped
        {"fact": "null", "evidence_quote": None},  # Literal 'null' should be dropped
    ]
    sn = make_dummy_notice(missing_information=raw_items)
    assert sn.missing_information == [
        "Backup contact person missing",
        "Submission portal URL absent",
    ]
    for item in sn.missing_information:
        assert item.lower() not in ("none", "null", "")


# 4. Missing or null evidence_quote values
def test_missing_or_null_evidence_quote_values():
    raw_items = [
        {"fact": "Income certificate criteria", "evidence_quote": None},
        {"fact": "Quota reservation breakdown"},  # No evidence_quote key
        {"fact": "Late penalty fee", "evidence_quote": ""},
    ]
    sn = make_dummy_notice(missing_information=raw_items)
    assert sn.missing_information == [
        "Income certificate criteria",
        "Quota reservation breakdown",
        "Late penalty fee",
    ]
    # Ensure no string 'None' was generated
    assert all("None" not in it for it in sn.missing_information)


# 5. Empty and malformed model responses
def test_empty_and_malformed_model_responses():
    # None input
    sn_none = make_dummy_notice(missing_information=None)
    assert sn_none.missing_information == []

    # Empty list
    sn_empty = make_dummy_notice(missing_information=[])
    assert sn_empty.missing_information == []

    # Single string passed instead of list
    sn_single_str = make_dummy_notice(missing_information="Single missing item")
    assert sn_single_str.missing_information == ["Single missing item"]

    # Single dict passed instead of list
    sn_single_dict = make_dummy_notice(missing_information={"fact": "Dict missing item"})
    assert sn_single_dict.missing_information == ["Dict missing item"]

    # Arbitrary malformed objects
    sn_malformed = make_dummy_notice(missing_information=[None, 12345, True, [], {}])
    assert "12345" in sn_malformed.missing_information
    assert None not in sn_malformed.missing_information


# 6. Valid StructuredNotice output
def test_valid_structured_notice_output():
    sn = make_dummy_notice(
        missing_information=["Missing requirement 1", "Missing requirement 2"],
        uncertain_or_conflicting_details=["Deadline date appears tentative"],
    )
    assert len(sn.missing_information) == 2
    assert len(sn.uncertain_or_conflicting_details) == 1
    assert sn.purpose.value == "Test value"
    assert sn.deadline.value == "Test value"


# 7. Incorrectly typed fields
def test_incorrectly_typed_fields():
    # Dict with context explanation
    raw_items = [
        {"fact": "Interview date", "explanation": "Marked tentative in notice"},
        {"item": "Affidavit format", "notes": "Not specified"},
    ]
    sn = make_dummy_notice(missing_information=raw_items)
    assert "Interview date (Marked tentative in notice)" in sn.missing_information
    assert any("Affidavit format" in x for x in sn.missing_information)


# 8. NoticeAnalyzer integration with dict model output
def test_notice_analyzer_recovers_from_dict_missing_info():
    class MockOllamaClient:
        def generate_structured_json(self, system_prompt, user_prompt):
            return {
                "purpose": {"value": "Merit Scholarship", "status": "stated", "evidence_quote": "Merit Scholarship"},
                "eligibility": {"value": "80% marks", "status": "stated", "evidence_quote": "80% marks"},
                "deadline": {"value": "30 October 2026", "status": "stated", "evidence_quote": "30 October 2026"},
                "fee_or_cost": {"value": NOT_STATED_LABEL, "status": "not_stated", "evidence_quote": None},
                "required_documents": {"value": "Marksheet, ID", "status": "stated", "evidence_quote": "Marksheet, ID"},
                "contact_details": {"value": "help@univ.edu", "status": "stated", "evidence_quote": "help@univ.edu"},
                "required_actions": {"value": "Submit form", "status": "stated", "evidence_quote": "Submit form"},
                "important_conditions": {"value": "No late entries", "status": "stated", "evidence_quote": "No late entries"},
                # This was the exact bug reported:
                "missing_information": [
                    {"fact": "Scholarship amount not mentioned", "evidence_quote": None},
                    {"fact": "Hostel fee details", "evidence_quote": None},
                ],
                "uncertain_or_conflicting_details": [],
            }

    analyzer = NoticeAnalyzer(client=MockOllamaClient())
    text = "Merit Scholarship for students with 80% marks. Deadline 30 October 2026. Submit form with Marksheet, ID to help@univ.edu. No late entries."
    sn = analyzer.analyze_notice(text)
    assert isinstance(sn, StructuredNotice)
    assert "Scholarship amount not mentioned" in sn.missing_information
    assert "Hostel fee details" in sn.missing_information
    assert all(isinstance(x, str) for x in sn.missing_information)
