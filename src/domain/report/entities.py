from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


@dataclass
class WordStats:
    """Frequency statistics for a single normalised word form."""

    word: str
    line_counts: dict[int, int] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return sum(self.line_counts.values())

    def add(self, line_index: int, count: int) -> None:
        self.line_counts[line_index] = self.line_counts.get(line_index, 0) + count

    def per_line_str(self, total_lines: int) -> str:
        """Return comma-separated counts per line, e.g. '0,11,32,0,0,3'."""
        return ",".join(str(self.line_counts.get(i, 0)) for i in range(total_lines))


@dataclass
class ReportJob:
    """Represents a single report processing job."""

    job_id: UUID
    status: JobStatus = JobStatus.PENDING
    file_path: str = ""
    result_path: str | None = None
    error: str | None = None
    total_lines: int = 0
