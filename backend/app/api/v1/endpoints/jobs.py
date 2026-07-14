from fastapi import APIRouter, Depends
from celery.result import AsyncResult
from app.core.deps import get_current_user
from app.workers.celery_app import celery

router = APIRouter(prefix="/jobs", tags=["jobs"], dependencies=[Depends(get_current_user)])

STATUS_MAP = {"PENDING": "pending", "STARTED": "started",
              "SUCCESS": "success", "FAILURE": "failure", "RETRY": "started"}


@router.get("/{job_id}")
async def job_status(job_id: str):
    result = AsyncResult(job_id, app=celery)
    payload = {"job_id": job_id, "status": STATUS_MAP.get(result.state, result.state.lower())}
    if result.successful():
        payload["result"] = result.result
    elif result.failed():
        payload["error"] = str(result.result)
    return payload
