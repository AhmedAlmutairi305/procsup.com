from datetime import datetime, timedelta
from fastapi import APIRouter, Query
from ..observability.meter import Meter

router = APIRouter(prefix="/api/costs")


@router.get("/summary")
def costs_summary(workspace_id: str = Query(...)):
    meter = Meter()
    since = datetime.utcnow() - timedelta(days=30)
    until = datetime.utcnow()
    return meter.get_usage(workspace_id, since, until)
