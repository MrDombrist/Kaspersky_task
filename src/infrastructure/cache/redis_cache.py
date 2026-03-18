import json
from uuid import UUID

from redis.asyncio import Redis

from src.core.config import settings
from src.domain.report.entities import JobStatus, ReportJob


class JobCache:
    """
    Redis-backed store for ReportJob state.

    Allows any worker or API instance to look up a job by its ID,
    enabling horizontal scaling without shared memory.
    """

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    @staticmethod
    def _key(job_id: UUID) -> str:
        return f"report:job:{job_id}"

    async def set_job(self, job: ReportJob) -> None:
        data = {
            "job_id": str(job.job_id),
            "status": job.status.value,
            "file_path": job.file_path,
            "result_path": job.result_path,
            "error": job.error,
            "total_lines": job.total_lines,
        }
        await self._redis.set(
            self._key(job.job_id),
            json.dumps(data),
            ex=settings.REDIS_JOB_TTL,
        )

    async def get_job(self, job_id: UUID) -> ReportJob | None:
        raw = await self._redis.get(self._key(job_id))
        if not raw:
            return None
        data = json.loads(raw)
        return ReportJob(
            job_id=UUID(data["job_id"]),
            status=JobStatus(data["status"]),
            file_path=data.get("file_path") or "",
            result_path=data.get("result_path"),
            error=data.get("error"),
            total_lines=data.get("total_lines", 0),
        )
