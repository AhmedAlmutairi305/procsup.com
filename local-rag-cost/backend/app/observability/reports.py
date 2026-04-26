from .meter import Meter


def usage_summary(workspace_id, since, until):
    return Meter().get_usage(workspace_id, since, until)
