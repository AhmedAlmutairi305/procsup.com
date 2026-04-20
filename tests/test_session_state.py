from app.models.models import RunStatus


def test_run_status_values():
    assert RunStatus.queued.value == "queued"
    assert RunStatus.waiting_manual_action.value == "waiting_manual_action"
    assert RunStatus.cancelled.value == "cancelled"
