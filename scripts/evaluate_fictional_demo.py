import json
from pathlib import Path
from notice2action.ingestion import ingest_uploaded_file
from notice2action.analysis import NoticeAnalyzer
from notice2action.followup import FollowUpAssistant

def run_fictional_demo_evaluation():
    p = Path("tests/fixtures/fake_notice_for_testing.docx")
    b = p.read_bytes()
    ingestion = ingest_uploaded_file("fake_notice_for_testing.docx", b)
    assert ingestion.raw_text, "Failed to extract text from DOCX"
    raw_text = ingestion.raw_text

    analyzer = NoticeAnalyzer()
    structured = analyzer.analyze_notice(raw_text)

    # 10 Questions from Section 7.4
    questions = [
        "What is the application deadline, including the time zone?",
        "What are all the eligibility conditions?",
        "What is the grant amount?",
        "List every required document.",
        "What are the opening date, result date and correction window?",
        "Create an ordered action checklist.",
        "Explain the notice in Hindi.",
        "Explain the notice in English.",
        "Does an applicant with annual household income of ₹2,80,000 who is a full-time undergraduate meet the stated income and enrollment conditions? Explain that other conditions still apply and that this is not an official approval.",
        "Does the notice establish a real government grant? The correct response must identify the notice as fictional and avoid presenting it as an authentic scheme."
    ]

    assistant = FollowUpAssistant()
    qa_results = []
    for q in questions:
        lang = "hi" if "Hindi" in q else "en"
        ans = assistant.answer_question(
            question=q,
            raw_notice_text=raw_text,
            target_lang=lang
        )
        qa_results.append({
            "question": q,
            "answer": ans.answer,
            "evidence_quote": ans.evidence_quote,
            "is_supported": ans.is_supported
        })

    output_data = {
        "raw_text": raw_text,
        "structured_notice": structured.model_dump(),
        "qa_results": qa_results
    }

    out_path = Path("reports/FINAL_SYSTEM_VERIFICATION/fictional_demo_eval.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Evaluation completed successfully and saved to reports/FINAL_SYSTEM_VERIFICATION/fictional_demo_eval.json")

if __name__ == "__main__":
    run_fictional_demo_evaluation()
