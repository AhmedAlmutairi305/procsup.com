import asyncio
import logging
from datetime import datetime
from pathlib import Path

from playwright.async_api import Page, async_playwright
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.models import ApplicationRecord, AutomationStatus, University
from app.services.audit import log_action
from app.services.credentials import CredentialProvider
from app.services.document_matcher import match_documents
from app.utils.retry import with_retry

logger = logging.getLogger(__name__)


class AutomationAgent:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.creds = CredentialProvider()

    async def run(self, university_id: int, application_id: int | None = None, dry_run: bool = True) -> dict:
        uni = self.db.query(University).filter(University.id == university_id).first()
        if not uni:
            raise ValueError("University not found")

        app = self._get_or_create_application(uni, application_id)
        app.status = AutomationStatus.running
        self.db.commit()
        log_action(self.db, "automation_started", f"dry_run={dry_run}", application_id=app.id, university_id=uni.id)

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=self.settings.playwright_headless)
            context = await browser.new_context()
            page = await context.new_page()
            try:
                await self._navigate(page, uni.portal_url)
                await self._capture(page, app.id, "portal_opened", uni.id)

                captcha_present = await self._detect_captcha(page)
                if captcha_present:
                    app.status = AutomationStatus.paused_for_captcha
                    self.db.commit()
                    log_action(self.db, "captcha_detected", "Manual intervention required", "WARNING", app.id, uni.id)
                    return {"status": app.status.value, "message": "CAPTCHA detected"}

                matches = self._prepare_document_matches(uni.id)
                await self._simulate_form_fill(page, uni.name)
                await self._simulate_uploads(page, matches)
                await self._capture(page, app.id, "form_prepared", uni.id)

                app.status = AutomationStatus.paused_for_review
                app.pending_items = "Awaiting explicit dashboard approval for final submission"
                self.db.commit()
                log_action(self.db, "paused_for_review", "Ready for human review", application_id=app.id, university_id=uni.id)

                if dry_run:
                    app.status = AutomationStatus.completed_prepared
                    self.db.commit()
                    log_action(self.db, "dry_run_completed", "Did not submit", application_id=app.id, university_id=uni.id)

                return {
                    "status": app.status.value,
                    "application_id": app.id,
                    "matches": matches,
                    "human_gate": True,
                }
            except Exception as exc:
                app.status = AutomationStatus.failed
                self.db.commit()
                log_action(self.db, "automation_failed", str(exc), "ERROR", app.id, uni.id)
                raise
            finally:
                await context.close()
                await browser.close()

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

    def _prepare_document_matches(self, university_id: int) -> list[dict]:
        from app.models.models import Document, Requirement
        req = self.db.query(Requirement).filter(Requirement.university_id == university_id).order_by(Requirement.created_at.desc()).first()
        docs = self.db.query(Document).all()
        if not req:
            return []
        import json

        parsed = json.loads(req.structured_json)
        required_docs = parsed.get("required_documents", [])
        return match_documents(required_docs, docs)

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

    async def _simulate_form_fill(self, page: Page, university_name: str) -> None:
        selectors = ["input[name='full_name']", "input[type='text']", "textarea"]
        for selector in selectors:
            try:
                loc = page.locator(selector).first
                if await loc.count() > 0:
                    await loc.fill("AUTO-FILL PREVIEW")
                    log_action(self.db, "selector_used", selector, university_id=None)
                    break
            except Exception as exc:
                logger.warning("selector failed %s: %s", selector, exc)
                log_action(self.db, "selector_failed", f"{selector}: {exc}", "WARNING")

        await asyncio.sleep(1)
        log_action(self.db, "form_filled", f"Prepared form for {university_name}")

    async def _simulate_uploads(self, page: Page, matches: list[dict]) -> None:
        for match in matches:
            if not match["matched_file"]:
                log_action(self.db, "upload_skipped", f"Missing file for {match['requirement_key']}", "WARNING")
                continue

            candidate_selectors = ["input[type='file']", f"input[name*='{match['requirement_key']}']"]
            uploaded = False
            for selector in candidate_selectors:
                try:
                    loc = page.locator(selector).first
                    if await loc.count() > 0:
                        await loc.set_input_files(match["matched_file"])
                        log_action(self.db, "file_uploaded_preview", f"{match['requirement_key']} => {match['matched_file']}")
                        uploaded = True
                        break
                except Exception as exc:
                    log_action(self.db, "upload_selector_failed", f"{selector}: {exc}", "WARNING")
            if not uploaded:
                log_action(self.db, "upload_not_possible", f"No selector found for {match['requirement_key']}", "WARNING")

    async def _capture(self, page: Page, app_id: int, step: str, university_id: int) -> None:
        filename = f"app_{app_id}_{step}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
        shot_path = str(Path(self.settings.screenshot_dir) / filename)
        await page.screenshot(path=shot_path, full_page=True)
        log_action(self.db, "screenshot", step, application_id=app_id, university_id=university_id, screenshot_path=shot_path)
