import logging

from sqlalchemy.orm import Session

from app.models.models import AuditLog

logger = logging.getLogger(__name__)


def log_action(
    db: Session,
    action: str,
    detail: str | None = None,
    level: str = "INFO",
    application_id: int | None = None,
    university_id: int | None = None,
    screenshot_path: str | None = None,
    run_id: int | None = None,
) -> None:
    log = AuditLog(
        action=action,
        detail=detail,
        level=level,
        application_id=application_id,
        university_id=university_id,
        screenshot_path=screenshot_path,
        run_id=run_id,
    )
    db.add(log)
    db.commit()
    logger.info("%s - %s", action, detail or "")
