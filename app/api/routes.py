from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.automation.playwright_agent import AutomationAgent
from app.core.config import get_settings
from app.db.database import get_db
from app.models.models import ApplicantProfile, ApplicationRecord, AuditLog, AutomationRun, Document, ManualAction, Requirement, RunEvent, RunScreenshot, University
from app.schemas.schemas import (
    ApplicantProfileRead,
    AutomationRequest,
    DocumentRead,
    FinalSubmissionApproval,
    ManualActionResolveRequest,
    MatchPreview,
    RequirementParseRequest,
    RequirementRead,
    RunRead,
    UniversityCreate,
    UniversityRead,
)
from app.services.audit import log_action
from app.services.csv_importer import import_universities_csv
from app.services.document_matcher import match_documents
from app.services.document_router import build_document_plan
from app.services.email_drafts import draft_follow_up_email
from app.services.email_verification import poll_verification_email
from app.services.excel_importer import import_applicants, parse_applicant_file
from app.services.field_mapper import map_fields
from app.services.recipe_loader import list_recipes, load_recipe, recipe_dir
from app.services.requirement_parser import parse_requirement_text, parsed_to_json
from app.services.run_hub import run_hub

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
    db.commit()
    db.refresh(requirement)
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


@router.post("/applicants/import", response_model=list[ApplicantProfileRead])
def import_applicants_from_excel(file_path: str = Form(...), db: Session = Depends(get_db)):
    try:
        rows = import_applicants(db, file_path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return rows


@router.post("/applicants/parse")
def parse_applicants_only(file_path: str = Form(...)):
    return {"rows": parse_applicant_file(file_path)}


@router.get("/applicants", response_model=list[ApplicantProfileRead])
def list_applicants(db: Session = Depends(get_db)):
    return db.query(ApplicantProfile).order_by(ApplicantProfile.created_at.desc()).all()


@router.get("/applicants/{applicant_id}")
def get_applicant(applicant_id: int, db: Session = Depends(get_db)):
    applicant = db.query(ApplicantProfile).filter(ApplicantProfile.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    return {c.name: getattr(applicant, c.name) for c in applicant.__table__.columns}


@router.put("/applicants/{applicant_id}")
def update_applicant(applicant_id: int, payload: dict, db: Session = Depends(get_db)):
    applicant = db.query(ApplicantProfile).filter(ApplicantProfile.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    for key, value in payload.items():
        if hasattr(applicant, key):
            setattr(applicant, key, value)
    db.commit()
    return {"updated": True}


@router.get("/universities/{university_id}/match-preview", response_model=list[MatchPreview])
def preview_matches(university_id: int, db: Session = Depends(get_db)):
    req = db.query(Requirement).filter(Requirement.university_id == university_id).order_by(Requirement.created_at.desc()).first()
    if not req:
        return []
    docs = db.query(Document).all()
    parsed = json.loads(req.structured_json)
    return match_documents(parsed.get("required_documents", []), docs)


@router.get("/mapping/preview")
def mapping_preview(university_id: int, applicant_profile_id: int, db: Session = Depends(get_db)):
    uni = db.query(University).filter(University.id == university_id).first()
    applicant = db.query(ApplicantProfile).filter(ApplicantProfile.id == applicant_profile_id).first()
    if not uni or not applicant:
        raise HTTPException(status_code=404, detail="University/applicant not found")
    recipe = load_recipe(uni.slug)
    mapped = map_fields(applicant, recipe)
    doc_plan = build_document_plan(db, applicant, recipe)
    return {"fields": mapped, "documents": doc_plan}


@router.post("/automation/start")
def start_automation(payload: AutomationRequest, db: Session = Depends(get_db)):
    agent = AutomationAgent(db)
    result = asyncio.run(
        agent.run(
            payload.university_id,
            payload.applicant_profile_id,
            payload.application_id,
            payload.dry_run,
            payload.headed,
        )
    )
    return result


@router.post("/automation/final-submit")
def final_submit(payload: FinalSubmissionApproval, db: Session = Depends(get_db)):
    agent = AutomationAgent(db)
    return agent.approve_final_submission(payload.application_id, payload.approved)


@router.post("/runs/{run_id}/pause")
def pause_run(run_id: int, db: Session = Depends(get_db)):
    return AutomationAgent(db).pause_run(run_id)


@router.post("/runs/{run_id}/resume")
def resume_run(run_id: int, db: Session = Depends(get_db)):
    return AutomationAgent(db).resume_run(run_id)


@router.post("/runs/{run_id}/cancel")
def cancel_run(run_id: int, db: Session = Depends(get_db)):
    return AutomationAgent(db).cancel_run(run_id)


@router.get("/runs", response_model=list[RunRead])
def list_runs(db: Session = Depends(get_db)):
    return db.query(AutomationRun).order_by(AutomationRun.created_at.desc()).all()


@router.get("/runs/{run_id}", response_model=RunRead)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(AutomationRun).filter(AutomationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/runs/{run_id}/events")
def run_events(run_id: int, db: Session = Depends(get_db)):
    return db.query(RunEvent).filter(RunEvent.run_id == run_id).order_by(RunEvent.created_at.desc()).all()


@router.get("/runs/{run_id}/screenshots")
def run_screenshots(run_id: int, db: Session = Depends(get_db)):
    return db.query(RunScreenshot).filter(RunScreenshot.run_id == run_id).order_by(RunScreenshot.created_at.desc()).all()


@router.get("/runs/{run_id}/manual-actions")
def run_manual_actions(run_id: int, db: Session = Depends(get_db)):
    return db.query(ManualAction).filter(ManualAction.run_id == run_id).order_by(ManualAction.created_at.desc()).all()


@router.post("/manual-actions/resolve")
def resolve_manual_action(payload: ManualActionResolveRequest, db: Session = Depends(get_db)):
    return AutomationAgent(db).resolve_manual_action(payload.run_id, payload.action_type, payload.approved, payload.note)


@router.get("/email-verification/poll")
def email_poll(email_address: str, password_reference: str, imap_server: str = "imap.gmail.com"):
    return poll_verification_email(email_address, password_reference, imap_server)


@router.get("/applications")
def list_applications(db: Session = Depends(get_db)):
    return db.query(ApplicationRecord).order_by(ApplicationRecord.updated_at.desc()).all()


@router.get("/applications/{application_id}/logs")
def list_logs(application_id: int, db: Session = Depends(get_db)):
    return db.query(AuditLog).filter(AuditLog.application_id == application_id).order_by(AuditLog.created_at.desc()).all()


@router.get("/applications/{application_id}/follow-up-email")
def follow_up_email(application_id: int, db: Session = Depends(get_db)):
    app = db.query(ApplicationRecord).filter(ApplicationRecord.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    uni = db.query(University).filter(University.id == app.university_id).first()
    body = draft_follow_up_email(uni.name if uni else "the university", app.pending_items)
    return {"subject": "Application Follow-up", "body": body}


@router.get("/recipes")
def recipes_list():
    return {"recipes": list_recipes()}


@router.get("/recipes/{slug}")
def recipes_get(slug: str):
    recipe_path = recipe_dir() / f"{slug}.json"
    if not recipe_path.exists():
        raise HTTPException(status_code=404, detail="recipe not found")
    return json.loads(recipe_path.read_text(encoding="utf-8"))


@router.post("/recipes/{slug}")
def recipes_upsert(slug: str, payload: dict):
    recipe_path = recipe_dir() / f"{slug}.json"
    recipe_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"saved": True, "path": str(recipe_path)}


@router.websocket("/ws/runs/{run_id}")
async def run_ws(run_id: int, websocket: WebSocket):
    await run_hub.connect(run_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        run_hub.disconnect(run_id, websocket)
