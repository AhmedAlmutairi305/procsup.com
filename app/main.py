from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.routes import router as api_router
from app.automation.playwright_agent import AutomationAgent
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.database import get_db
from app.db.init_db import init_db
from app.models.models import ApplicantProfile, ApplicationRecord, AuditLog, AutomationRun, ManualAction, Requirement, University
from app.services.excel_importer import import_applicants

settings = get_settings()
configure_logging()
init_db()

app = FastAPI(title=settings.app_name)
app.include_router(api_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/screenshots", StaticFiles(directory=settings.screenshot_dir), name="screenshots")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    universities = db.query(University).order_by(University.deadline.is_(None), University.deadline).all()
    applications = db.query(ApplicationRecord).order_by(ApplicationRecord.updated_at.desc()).all()
    applicants = db.query(ApplicantProfile).order_by(ApplicantProfile.created_at.desc()).all()
    runs = db.query(AutomationRun).order_by(AutomationRun.created_at.desc()).limit(20).all()
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "universities": universities,
            "applications": applications,
            "applicants": applicants,
            "runs": runs,
            "dry_run_default": settings.dry_run,
        },
    )


@app.get("/universities/{university_id}", response_class=HTMLResponse)
def university_profile(university_id: int, request: Request, db: Session = Depends(get_db)):
    uni = db.query(University).filter(University.id == university_id).first()
    if not uni:
        return HTMLResponse("Not found", status_code=404)
    requirement = db.query(Requirement).filter(Requirement.university_id == university_id).order_by(Requirement.created_at.desc()).first()
    logs = db.query(AuditLog).filter(AuditLog.university_id == university_id).order_by(AuditLog.created_at.desc()).limit(100).all()
    return templates.TemplateResponse("university.html", {"request": request, "uni": uni, "requirement": requirement, "logs": logs})


@app.get("/runs/{run_id}", response_class=HTMLResponse)
def run_live_page(run_id: int, request: Request, db: Session = Depends(get_db)):
    run = db.query(AutomationRun).filter(AutomationRun.id == run_id).first()
    if not run:
        return HTMLResponse("Not found", status_code=404)
    actions = db.query(ManualAction).filter(ManualAction.run_id == run_id).order_by(ManualAction.created_at.desc()).all()
    return templates.TemplateResponse("run_live.html", {"request": request, "run": run, "actions": actions})


@app.post("/ui/applicants/import")
def ui_import_applicants(file_path: str = Form(...), db: Session = Depends(get_db)):
    import_applicants(db, file_path)
    return RedirectResponse(url="/", status_code=303)


@app.post("/ui/automation/start")
def ui_start_automation(
    university_id: int = Form(...),
    applicant_profile_id: int = Form(...),
    dry_run: bool = Form(True),
    headed: bool = Form(True),
    db: Session = Depends(get_db),
):
    import asyncio

    agent = AutomationAgent(db)
    result = asyncio.run(agent.run(university_id=university_id, applicant_profile_id=applicant_profile_id, dry_run=dry_run, headed=headed))
    return RedirectResponse(url=f"/runs/{result['run_id']}", status_code=303)


@app.post("/ui/runs/{run_id}/pause")
def ui_pause(run_id: int, db: Session = Depends(get_db)):
    AutomationAgent(db).pause_run(run_id)
    return RedirectResponse(url=f"/runs/{run_id}", status_code=303)


@app.post("/ui/runs/{run_id}/resume")
def ui_resume(run_id: int, db: Session = Depends(get_db)):
    AutomationAgent(db).resume_run(run_id)
    return RedirectResponse(url=f"/runs/{run_id}", status_code=303)


@app.post("/ui/runs/{run_id}/cancel")
def ui_cancel(run_id: int, db: Session = Depends(get_db)):
    AutomationAgent(db).cancel_run(run_id)
    return RedirectResponse(url=f"/runs/{run_id}", status_code=303)


@app.post("/ui/runs/{run_id}/approve")
def ui_approve(run_id: int, action_type: str = Form(...), approve: bool = Form(False), note: str = Form(""), db: Session = Depends(get_db)):
    from app.models.models import ManualActionType

    AutomationAgent(db).resolve_manual_action(run_id, ManualActionType(action_type), approve, note)
    return RedirectResponse(url=f"/runs/{run_id}", status_code=303)


@app.post("/ui/automation/approve")
def ui_approve_final_submit(application_id: int = Form(...), approve: bool = Form(False), db: Session = Depends(get_db)):
    agent = AutomationAgent(db)
    agent.approve_final_submission(application_id, approve)
    return RedirectResponse(url="/", status_code=303)


@app.post("/ui/requirements/parse")
def ui_parse_requirements(university_id: int = Form(...), source_text: str = Form(...), db: Session = Depends(get_db)):
    from app.models.models import Requirement
    from app.services.requirement_parser import parse_requirement_text, parsed_to_json

    parsed = parse_requirement_text(source_text)
    row = Requirement(
        university_id=university_id,
        source_text=source_text,
        structured_json=parsed_to_json(parsed),
        extracted_deadline=parsed.deadline,
        extracted_language_requirement=parsed.language_requirement,
    )
    db.add(row)
    db.commit()
    return RedirectResponse(url=f"/universities/{university_id}", status_code=303)


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok", "data_dir": str(Path(settings.data_dir).resolve())}
