import asyncio
import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.automation.playwright_agent import AutomationAgent
from app.db.database import get_db
from app.models.models import ApplicationRecord, AuditLog, Document, Requirement, University
from app.schemas.schemas import (
    AutomationRequest,
    DocumentRead,
    FinalSubmissionApproval,
    MatchPreview,
    RequirementParseRequest,
    RequirementRead,
    UniversityCreate,
    UniversityRead,
)
from app.services.audit import log_action
from app.services.csv_importer import import_universities_csv
from app.services.document_matcher import match_documents
from app.services.email_drafts import draft_follow_up_email
from app.services.requirement_parser import parse_requirement_text, parsed_to_json
from app.core.config import get_settings

router = APIRouter(prefix="/api", tags=["api"])
settings = get_settings()


@router.get("/universities", response_model=list[UniversityRead])
def list_universities(status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(University)
    if status:
        query = query.filter(University.status == status)
    return query.order_by(University.deadline.is_(None), University.deadline).all()


@router.post("/universities", response_model=UniversityRead)
def create_university(payload: UniversityCreate, db: Session = Depends(get_db)):
    uni = University(**payload.model_dump())
    db.add(uni)
    db.commit()
    db.refresh(uni)
    log_action(db, "university_created", uni.name, university_id=uni.id)
    return uni


@router.post("/universities/import-csv")
def import_universities(csv_path: str = Form(...), db: Session = Depends(get_db)):
    try:
        count = import_universities_csv(db, csv_path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"imported": count}


@router.post("/requirements/parse", response_model=RequirementRead)
def parse_requirements(payload: RequirementParseRequest, db: Session = Depends(get_db)):
    uni = db.query(University).filter(University.id == payload.university_id).first()
    if not uni:
        raise HTTPException(status_code=404, detail="University not found")

    parsed = parse_requirement_text(payload.source_text)
    requirement = Requirement(
        university_id=payload.university_id,
        source_text=payload.source_text,
        structured_json=parsed_to_json(parsed),
        extracted_deadline=parsed.deadline,
        extracted_language_requirement=parsed.language_requirement,
    )
    db.add(requirement)
    if parsed.deadline:
        uni.deadline = parsed.deadline
    if parsed.application_fee is not None:
        uni.application_fee = parsed.application_fee
    if parsed.recommendation_letter_count is not None:
        uni.recommendation_letter_count = parsed.recommendation_letter_count
    db.commit()
    db.refresh(requirement)
    log_action(db, "requirement_parsed", f"university_id={uni.id}", university_id=uni.id)
    return requirement


@router.post("/documents/upload", response_model=DocumentRead)
async def upload_document(tag: str = Form(...), extra_tags: str = Form(""), file: UploadFile = File(...), db: Session = Depends(get_db)):
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / file.filename
    content = await file.read()
    destination.write_bytes(content)

    doc = Document(filename=file.filename, file_path=str(destination), tag=tag, extra_tags=extra_tags or None)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    log_action(db, "document_uploaded", f"{doc.tag} -> {doc.filename}")
    return doc


@router.get("/universities/{university_id}/match-preview", response_model=list[MatchPreview])
def preview_matches(university_id: int, db: Session = Depends(get_db)):
    req = (
        db.query(Requirement)
        .filter(Requirement.university_id == university_id)
        .order_by(Requirement.created_at.desc())
        .first()
    )
    if not req:
        return []
    docs = db.query(Document).all()
    parsed = json.loads(req.structured_json)
    return match_documents(parsed.get("required_documents", []), docs)


@router.post("/automation/start")
def start_automation(payload: AutomationRequest, db: Session = Depends(get_db)):
    agent = AutomationAgent(db)
    result = asyncio.run(agent.run(payload.university_id, payload.application_id, payload.dry_run))
    return result


@router.post("/automation/final-submit")
def final_submit(payload: FinalSubmissionApproval, db: Session = Depends(get_db)):
    agent = AutomationAgent(db)
    return agent.approve_final_submission(payload.application_id, payload.approved)


@router.get("/applications")
def list_applications(db: Session = Depends(get_db)):
    return db.query(ApplicationRecord).order_by(ApplicationRecord.updated_at.desc()).all()


@router.get("/applications/{application_id}/logs")
def list_logs(application_id: int, db: Session = Depends(get_db)):
    return (
        db.query(AuditLog)
        .filter(AuditLog.application_id == application_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )


@router.get("/applications/{application_id}/follow-up-email")
def follow_up_email(application_id: int, db: Session = Depends(get_db)):
    app = db.query(ApplicationRecord).filter(ApplicationRecord.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    uni = db.query(University).filter(University.id == app.university_id).first()
    body = draft_follow_up_email(uni.name if uni else "the university", app.pending_items)
    return {"subject": "Application Follow-up", "body": body}
