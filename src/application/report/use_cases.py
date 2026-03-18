import asyncio
import os
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

from src.core.config import settings
from src.domain.report.entities import JobStatus, ReportJob, WordStats
from src.domain.report.services import TextAnalysisService
from src.infrastructure.excel.report_builder import ExcelReportBuilder

# Shared thread pool — keeps pymorphy3 (CPU-bound) off the asyncio event loop.
# Pool is bounded so a burst of huge uploads cannot create unlimited threads.
_executor = ThreadPoolExecutor(max_workers=settings.MAX_WORKERS)


class SyncProcessFileUseCase:
    """
    Processes a single file synchronously.

    Designed to run inside a thread pool (via run_in_executor) so it never
    blocks the FastAPI event loop.  Reads the file line-by-line → no full
    file load into RAM → safe for multi-GB inputs.
    """

    def __init__(
        self,
        report_builder: ExcelReportBuilder,
        normalizer: Callable[[str], str],
    ) -> None:
        self._report_builder = report_builder
        self._analysis_service = TextAnalysisService(normalizer=normalizer)

    def process(self, job: ReportJob) -> None:
        try:
            job.status = JobStatus.PROCESSING
            stats: dict[str, WordStats] = {}
            total_lines = 0

            with open(job.file_path, encoding="utf-8") as f:
                for i, line in enumerate(f):
                    self._analysis_service.analyze_line(line.rstrip("\n"), i, stats)
                    total_lines = i + 1

            job.total_lines = total_lines
            self._report_builder.build(stats, total_lines, job.result_path)  # type: ignore[arg-type]
            job.status = JobStatus.DONE

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)

        finally:
            # Always clean up the raw input to save disk space
            if job.file_path and os.path.exists(job.file_path):
                os.remove(job.file_path)


class ProcessFileUseCase:
    """
    Async orchestrator: persists the upload then dispatches processing
    to the bounded thread pool.

    For truly huge files routed through Kafka the same SyncProcessFileUseCase
    is reused inside the consumer; this class handles the synchronous (direct)
    path where the caller waits for the result.
    """

    def __init__(self, sync_processor: SyncProcessFileUseCase) -> None:
        self._sync_processor = sync_processor

    async def execute(self, filename: str, content: bytes) -> ReportJob:
        job_id = uuid.uuid4()
        os.makedirs(settings.TEMP_DIR, exist_ok=True)

        file_path = os.path.join(settings.TEMP_DIR, f"{job_id}_input.txt")
        result_path = os.path.join(settings.TEMP_DIR, f"{job_id}_result.xlsx")

        # Write upload to disk (no full in-memory hold for large files)
        with open(file_path, "wb") as f:
            f.write(content)

        job = ReportJob(
            job_id=job_id,
            file_path=file_path,
            result_path=result_path,
        )

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(_executor, self._sync_processor.process, job)

        return job
