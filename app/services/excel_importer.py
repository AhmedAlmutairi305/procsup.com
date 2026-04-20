from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.models.models import ApplicantProfile

CANONICAL_COLUMNS = [
    "applicant_id", "full_name", "first_name", "middle_name", "last_name", "chinese_name", "gender",
    "date_of_birth", "nationality", "passport_number", "passport_expiry", "marital_status", "religion",
    "email", "email_password_reference", "phone", "country", "city", "address_line_1", "address_line_2",
    "postal_code", "emergency_contact_name", "emergency_contact_phone", "emergency_contact_relationship",
    "high_school_name", "previous_university", "graduation_date", "gpa", "intended_degree_level",
    "intended_major", "intended_language", "scholarship_type", "supervisor_preference", "study_plan_text",
    "personal_statement_text", "cv_text", "notes",
    "passport_file", "transcript_file", "graduation_certificate_file", "cv_file", "study_plan_file",
    "personal_statement_file", "recommendation_1_file", "recommendation_2_file", "language_certificate_file",
    "photo_file", "medical_form_file", "bank_statement_file", "police_clearance_file", "portfolio_file",
    "other_file_1", "other_file_2",
]


def _to_text(v: Any) -> str | None:
    if v is None:
        return None
    txt = str(v).strip()
    return txt if txt and txt.lower() != "nan" else None


def parse_applicant_file(file_path: str) -> list[dict[str, str | None]]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(file_path)

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path, engine="openpyxl")

    lower_map = {str(c).strip().lower(): c for c in df.columns}
    records: list[dict[str, str | None]] = []
    for _, row in df.iterrows():
        item = {}
        for canonical in CANONICAL_COLUMNS:
            source = lower_map.get(canonical)
            item[canonical] = _to_text(row[source]) if source is not None else None
        if item.get("full_name") or item.get("first_name") or item.get("applicant_id"):
            records.append(item)
    return records


def import_applicants(db: Session, file_path: str) -> list[ApplicantProfile]:
    parsed = parse_applicant_file(file_path)
    created: list[ApplicantProfile] = []
    for row in parsed:
        model = ApplicantProfile(**row, source_filename=Path(file_path).name)
        db.add(model)
        created.append(model)
    db.commit()
    for model in created:
        db.refresh(model)
    return created
