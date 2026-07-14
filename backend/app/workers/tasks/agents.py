"""Long-running agent tasks: research reports and generated documents."""
from app.workers.celery_app import celery
from app.workers.db import WorkerSession
from app.db.models import Report
from app.agents.research_agent import run_research
from app.agents.report_agent import generate_report


@celery.task
def research_task(workspace_id: str, question: str, depth: int) -> str:
    return run_research(workspace_id, question, depth)


@celery.task
def report_task(report_id: str, template: str):
    with WorkerSession() as db:
        report = db.get(Report, report_id)
        try:
            report.content_md = generate_report(report.workspace_id, report.topic, template)
            report.status = "READY"
        except Exception as e:  # noqa: BLE001
            report.status, report.error = "FAILED", str(e)[:2000]
        db.commit()
