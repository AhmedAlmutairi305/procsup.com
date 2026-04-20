import json
import re
from dataclasses import dataclass


@dataclass
class ParsedRequirements:
    required_documents: list[str]
    deadline: str | None
    language_requirement: str | None
    application_fee: float | None
    recommendation_letter_count: int | None
    flags: dict[str, bool]


def _extract_fee(text: str) -> float | None:
    m = re.search(r"(?:fee|application fee)[^\d]{0,10}(\d+[\.]?\d*)", text, re.IGNORECASE)
    return float(m.group(1)) if m else None


def parse_requirement_text(raw_text: str) -> ParsedRequirements:
    text = raw_text.replace("\n", " ")
    doc_keywords = {
        "passport": ["passport"],
        "transcript": ["transcript", "academic record"],
        "graduation_certificate": ["graduation certificate", "diploma"],
        "cv": ["cv", "resume"],
        "study_plan": ["study plan", "personal statement"],
        "recommendation_letter": ["recommendation letter", "reference letter"],
        "language_certificate": ["hsk", "ielts", "toefl", "language certificate"],
        "photo": ["photo", "passport photo"],
        "bank_statement": ["bank statement", "financial proof"],
        "medical_form": ["medical form", "physical examination"],
    }

    required_documents = [
        k for k, aliases in doc_keywords.items() if any(a in text.lower() for a in aliases)
    ]

    deadline_match = re.search(r"(deadline|due date)[:\s]*([A-Za-z]+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2})", text, re.IGNORECASE)
    lang_match = re.search(r"(hsk\s*\d|ielts\s*\d(?:\.\d)?|toefl\s*\d+|english|chinese)", text, re.IGNORECASE)
    rec_match = re.search(r"(\d+)\s+(recommendation|reference)\s+letters?", text, re.IGNORECASE)

    flags = {
        "study_plan_required": "study plan" in text.lower() or "personal statement" in text.lower(),
        "cv_required": "cv" in text.lower() or "resume" in text.lower(),
        "passport_required": "passport" in text.lower(),
        "transcript_required": "transcript" in text.lower(),
        "medical_form_required": "medical" in text.lower(),
    }

    return ParsedRequirements(
        required_documents=required_documents,
        deadline=deadline_match.group(2) if deadline_match else None,
        language_requirement=lang_match.group(1) if lang_match else None,
        application_fee=_extract_fee(text),
        recommendation_letter_count=int(rec_match.group(1)) if rec_match else None,
        flags=flags,
    )


def parsed_to_json(parsed: ParsedRequirements) -> str:
    return json.dumps(parsed.__dict__, ensure_ascii=False, indent=2)
