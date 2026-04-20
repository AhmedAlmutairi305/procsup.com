from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.models import ApplicantProfile, AutomationRun, Document, RunEvent

DOC_FIELDS = [
    "passport_file", "transcript_file", "graduation_certificate_file", "cv_file", "study_plan_file", "personal_statement_file",
    "recommendation_1_file", "recommendation_2_file", "language_certificate_file", "photo_file", "medical_form_file",
    "bank_statement_file", "police_clearance_file", "portfolio_file", "other_file_1", "other_file_2",
]


def _resolve(path: str, base_dir: Path) -> str:
    p = Path(path)
    return str((base_dir / p).resolve()) if not p.is_absolute() else str(p)


def build_document_plan(db: Session, applicant: ApplicantProfile, recipe: dict, base_dir: str = ".") -> dict:
    base = Path(base_dir)
    upload_mappings = recipe.get("upload_mappings", {})
    docs = db.query(Document).all()

    selected: dict[str, str | None] = {}
    warnings: list[str] = []
    for field in DOC_FIELDS:
        value = getattr(applicant, field)
        resolved = _resolve(value, base) if value else None
        if resolved and Path(resolved).exists():
            selected[field] = resolved
            continue

        fallback_tag = upload_mappings.get(field, field.replace("_file", ""))
        matched = next((d for d in docs if d.tag == fallback_tag), None)
        if matched:
            selected[field] = matched.file_path
        else:
            selected[field] = None
            warnings.append(f"Missing file for {field}")

    return {"selected_files": selected, "warnings": warnings}


def persist_document_decisions(db: Session, run: AutomationRun, plan: dict) -> None:
    run.selected_files_json = json.dumps(plan.get("selected_files", {}), ensure_ascii=False)
    db.add(
        RunEvent(
            run_id=run.id,
            event_type="document_plan",
            level="WARNING" if plan.get("warnings") else "INFO",
            message="Document routing prepared",
            event_json=json.dumps(plan, ensure_ascii=False),
        )
    )
    db.commit()
