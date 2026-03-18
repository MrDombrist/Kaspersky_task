from dataclasses import dataclass
from uuid import UUID

from src.domain.report.entities import JobStatus


@dataclass(frozen=True)
class JobStatusDTO:
    job_id: UUID
    status: JobStatus
    error: str | None = None


@dataclass(frozen=True)
class CreateReportDTO:
    """Input data for creating a new report job."""

    filename: str
    content: bytes
