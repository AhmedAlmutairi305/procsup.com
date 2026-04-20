from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from playwright.async_api import Page, async_playwright
from sqlalchemy.orm import Session

from app.automation.desktop_fallback import DesktopFallbackExecutor
from app.core.config import get_settings
from app.models.models import (
    ApplicantProfile,
    ApplicationRecord,
    AutomationRun,
    AutomationStatus,
    ManualAction,
    ManualActionType,
    RunEvent,
    RunScreenshot,
    RunStatus,
    University,
)
from app.services.audit import log_action
from app.services.credentials import CredentialProvider
from app.services.document_router import build_document_plan, persist_document_decisions
from app.services.field_mapper import map_fields
from app.services.recipe_loader import load_recipe
from app.services.run_hub import manual_gates, run_hub
from app.utils.retry import with_retry

logger = logging.getLogger(__name__)
RUN_CONTROLS: dict[int, str] = {}


class AutomationAgent:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.creds = CredentialProvider()
        self.desktop = DesktopFallbackExecutor()

    async def run(
        self,
        university_id: int,
        applicant_profile_id: int,
        application_id: int | None = None,
        dry_run: bool = True,
        headed: bool = True,
    ) -> dict:
        uni = self.db.query(University).filter(University.id == university_id).first()
        applicant = self.db.query(ApplicantProfile).filter(ApplicantProfile.id == applicant_profile_id).first()
        if not uni or not applicant:
            raise ValueError("University/applicant not found")

        app = self._get_or_create_application(uni, application_id)
        run = AutomationRun(
            university_id=uni.id,
            applicant_id=applicant.id,
            application_record_id=app.id,
            portal_url=uni.portal_url,
            status=RunStatus.preparing,
            current_step="prepare",
            progress_percent=5,
            dry_run=dry_run,
            headed=headed,
            started_at=datetime.utcnow(),
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        RUN_CONTROLS[run.id] = "running"

        await self._emit(run, "status", "Run preparing", {"status": run.status.value})
        recipe = load_recipe(uni.slug)
        document_plan = build_document_plan(self.db, applicant, recipe)
        persist_document_decisions(self.db, run, document_plan)
        await self._emit(run, "document_plan", "Document routing ready", document_plan)

        app.status = AutomationStatus.running
        run.status = RunStatus.running
        run.current_step = "launch_browser"
        run.progress_percent = 15
        self.db.commit()

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=not headed)
            context = await browser.new_context()
            page = await context.new_page()
            try:
                await self._navigate(page, uni.portal_url)
                await self._checkpoint(page, run, "portal_opened", 20)

                if await self._detect_captcha(page):
                    run.status = RunStatus.waiting_manual_action
                    run.captcha_required = True
                    run.current_warning_error = "CAPTCHA detected"
                    self.db.commit()
                    await self._emit(run, "captcha", "Captcha detected. Manual solve required.", {"captcha": True})

                await self._manual_gate(run, ManualActionType.login_submit)
                await self._fill_fields(page, applicant, recipe, run)
                await self._upload_files(page, run, recipe)

                run.status = RunStatus.waiting_email_verification
                run.waiting_email_verification = True
                run.current_step = "email_verification"
                run.progress_percent = 75
                self.db.commit()
                await self._emit(run, "email_wait", "Waiting email verification approval", {})
                await self._manual_gate(run, ManualActionType.email_verification_continue)
                run.waiting_email_verification = False

                await self._manual_gate(run, ManualActionType.final_application_submit)
                run.current_step = "finalize"

                if dry_run:
                    app.status = AutomationStatus.completed_prepared
                    run.status = RunStatus.completed
                    run.last_successful_action = "Dry run completed"
                else:
                    app.status = AutomationStatus.completed_submitted
                    app.submitted = True
                    app.submitted_at = datetime.utcnow()
                    run.status = RunStatus.completed
                    run.last_successful_action = "Final submission approved"

                run.progress_percent = 100
                run.completed_at = datetime.utcnow()
                run.last_completed_step = "done"
                self.db.commit()
                await self._checkpoint(page, run, "completed", 100)
                await self._emit(run, "done", "Run completed", {"application_id": app.id})

                return {"status": run.status.value, "application_id": app.id, "run_id": run.id, "human_gate": True}
            except Exception as exc:
                run.status = RunStatus.failed
                run.current_warning_error = str(exc)
                app.status = AutomationStatus.failed
                run.completed_at = datetime.utcnow()
                self.db.commit()
                await self._emit(run, "error", str(exc), {"status": "failed"})
                log_action(self.db, "automation_failed", str(exc), "ERROR", app.id, uni.id, run_id=run.id)
                raise
            finally:
                await context.close()
                await browser.close()

    def pause_run(self, run_id: int) -> dict:
        RUN_CONTROLS[run_id] = "paused"
        run = self.db.query(AutomationRun).filter(AutomationRun.id == run_id).first()
        if run:
            run.status = RunStatus.paused
            self.db.commit()
        return {"run_id": run_id, "status": "paused"}

    def resume_run(self, run_id: int) -> dict:
        RUN_CONTROLS[run_id] = "running"
        run = self.db.query(AutomationRun).filter(AutomationRun.id == run_id).first()
        if run and run.status == RunStatus.paused:
            run.status = RunStatus.running
            self.db.commit()
        return {"run_id": run_id, "status": "running"}

    def cancel_run(self, run_id: int) -> dict:
        RUN_CONTROLS[run_id] = "cancelled"
        run = self.db.query(AutomationRun).filter(AutomationRun.id == run_id).first()
        if run:
            run.status = RunStatus.cancelled
            run.completed_at = datetime.utcnow()
            self.db.commit()
        return {"run_id": run_id, "status": "cancelled"}

    def resolve_manual_action(self, run_id: int, action_type: ManualActionType, approved: bool, note: str | None = None) -> dict:
        action = (
            self.db.query(ManualAction)
            .filter(ManualAction.run_id == run_id, ManualAction.action_type == action_type, ManualAction.approved.is_(None))
            .order_by(ManualAction.created_at.desc())
            .first()
        )
        if not action:
            action = ManualAction(run_id=run_id, action_type=action_type)
            self.db.add(action)
        action.approved = approved
        action.note = note
        action.resolved_at = datetime.utcnow()
        self.db.commit()
        manual_gates.resolve(run_id, action_type.value, approved)
        return {"run_id": run_id, "action_type": action_type.value, "approved": approved}

    def approve_final_submission(self, application_id: int, approved: bool) -> dict:
        app = self.db.query(ApplicationRecord).filter(ApplicationRecord.id == application_id).first()
        if not app:
            raise ValueError("Application not found")
        if not approved:
            log_action(self.db, "submission_rejected", "Human rejected final submit", application_id=application_id, university_id=app.university_id)
            return {"status": app.status.value, "submitted": False}

        app.submitted = True
        app.submitted_at = datetime.utcnow()
        app.pending_items = None
        app.status = AutomationStatus.completed_submitted
        self.db.commit()
        log_action(self.db, "final_submit_confirmed", "Human approved final submit", application_id=application_id, university_id=app.university_id)
        return {"status": app.status.value, "submitted": True}

    async def _manual_gate(self, run: AutomationRun, action_type: ManualActionType) -> None:
        action = ManualAction(run_id=run.id, action_type=action_type, approved=None)
        run.status = RunStatus.waiting_manual_action
        run.current_step = f"await_{action_type.value}"
        self.db.add(action)
        self.db.commit()
        await self._emit(run, "manual_gate", f"Waiting approval: {action_type.value}", {"action_type": action_type.value})

        gate = manual_gates.wait_event(run.id, action_type.value)
        while not gate.is_set():
            await self._respect_run_controls(run.id)
            await asyncio.sleep(0.5)
        if not manual_gates.get_decision(run.id, action_type.value):
            raise RuntimeError(f"Manual action rejected: {action_type.value}")

        run.status = RunStatus.running
        run.last_successful_action = f"approved:{action_type.value}"
        self.db.commit()
        await self._emit(run, "manual_approved", f"Approved: {action_type.value}", {})

    async def _fill_fields(self, page: Page, applicant: ApplicantProfile, recipe: dict, run: AutomationRun) -> None:
        mappings = map_fields(applicant, recipe)
        for m in mappings:
            await self._respect_run_controls(run.id)
            if not m.get("value"):
                continue
            selector = m.get("selector")
            if not selector:
                continue
            try:
                loc = page.locator(selector).first
                if await loc.count() > 0:
                    if m["field_type"] in {"text", "date"}:
                        await loc.fill(str(m["value"]))
                    elif m["field_type"] == "checkbox" and str(m["value"]).lower() in {"1", "true", "yes"}:
                        await loc.check()
                run.last_successful_action = f"filled:{m['canonical_field']}"
                run.current_step = f"fill_{m['canonical_field']}"
                run.progress_percent = min(run.progress_percent + 1, 70)
                self.db.commit()
                await self._emit(run, "field_filled", run.last_successful_action, m)
            except Exception as exc:
                await self._emit(run, "selector_failed", f"{selector}: {exc}", {"selector": selector})

    async def _upload_files(self, page: Page, run: AutomationRun, recipe: dict) -> None:
        selected_files = json.loads(run.selected_files_json or "{}")
        upload_mappings = recipe.get("upload_mappings", {})
        for doc_key, path in selected_files.items():
            await self._respect_run_controls(run.id)
            if not path:
                continue
            selector = upload_mappings.get(doc_key)
            if isinstance(selector, dict):
                selector = selector.get("selector")
            if not selector:
                selector = "input[type='file']"
            try:
                loc = page.locator(selector).first
                if await loc.count() > 0:
                    await loc.set_input_files(path)
                    await self._emit(run, "upload", f"Uploaded {doc_key}", {"field": doc_key, "file": path})
                else:
                    result = self.desktop.upload_via_native_dialog(path)
                    await self._emit(run, "desktop_fallback", f"Fallback for {doc_key}", result)
            except Exception:
                result = self.desktop.upload_via_native_dialog(path)
                await self._emit(run, "desktop_fallback", f"Fallback for {doc_key}", result)
        await self._checkpoint(page, run, "uploads_done", 72)

    async def _respect_run_controls(self, run_id: int) -> None:
        while RUN_CONTROLS.get(run_id) == "paused":
            await asyncio.sleep(0.5)
        if RUN_CONTROLS.get(run_id) == "cancelled":
            raise RuntimeError("Run cancelled by user")

    def _get_or_create_application(self, uni: University, application_id: int | None) -> ApplicationRecord:
        app = None
        if application_id:
            app = self.db.query(ApplicationRecord).filter(ApplicationRecord.id == application_id).first()
        if not app:
            app = ApplicationRecord(university_id=uni.id, portal_name=uni.name)
            self.db.add(app)
            self.db.commit()
            self.db.refresh(app)
        return app

    @with_retry
    async def _navigate(self, page: Page, url: str) -> None:
        await page.goto(url, timeout=self.settings.automation_timeout_ms)

    async def _detect_captcha(self, page: Page) -> bool:
        captcha_selectors = ["iframe[src*='captcha']", "text=CAPTCHA", "img[alt*='captcha']"]
        for selector in captcha_selectors:
            try:
                if await page.locator(selector).count() > 0:
                    return True
            except Exception:
                continue
        return False

    async def _checkpoint(self, page: Page, run: AutomationRun, step: str, progress: int) -> None:
        filename = f"run_{run.id}_{step}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
        shot_path = str(Path(self.settings.screenshot_dir) / filename)
        await page.screenshot(path=shot_path, full_page=True)
        self.db.add(RunScreenshot(run_id=run.id, step=step, screenshot_path=shot_path))
        run.current_step = step
        run.last_completed_step = step
        run.progress_percent = progress
        self.db.commit()
        await self._emit(run, "screenshot", step, {"screenshot_path": shot_path})

    async def _emit(self, run: AutomationRun, event_type: str, message: str, data: dict) -> None:
        self.db.add(RunEvent(run_id=run.id, event_type=event_type, message=message, event_json=json.dumps(data), level="INFO"))
        self.db.commit()
        payload = {
            "run_id": run.id,
            "event_type": event_type,
            "message": message,
            "status": run.status.value,
            "current_step": run.current_step,
            "progress_percent": run.progress_percent,
            "last_successful_action": run.last_successful_action,
            "current_warning_error": run.current_warning_error,
            **data,
        }
        await run_hub.broadcast(run.id, payload)
