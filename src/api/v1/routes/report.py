import os
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from src.application.report.use_cases import ProcessFileUseCase, SyncProcessFileUseCase
from src.domain.report.entities import JobStatus
from src.infrastructure.excel.report_builder import ExcelReportBuilder
from src.infrastructure.nlp.morphology import get_normal_form

router = APIRouter()

_XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
_MAX_UPLOAD_BYTES = 2 * 1024 * 1024 * 1024  # 2 GB soft guard


def _build_use_case() -> ProcessFileUseCase:
    """Simple factory — swap out dependencies here for DI frameworks later."""
    return ProcessFileUseCase(
        sync_processor=SyncProcessFileUseCase(
            report_builder=ExcelReportBuilder(),
            normalizer=get_normal_form,
        )
    )


def _cleanup(path: str | None) -> None:
    if path and os.path.exists(path):
        os.remove(path)


@router.post(
    "/export",
    summary="Word frequency report",
    description=(
        "Upload a UTF-8 text file. Returns an .xlsx with three columns: "
        "normalised word form, total count, per-line counts."
    ),
    response_class=FileResponse,
)
async def export_report(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File(description="UTF-8 plain-text file (.txt)")],
) -> FileResponse:
    if not (file.filename or "").endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are accepted.")

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > _MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 2 GB limit.")

    job = await _build_use_case().execute(file.filename or "upload.txt", content)

    if job.status == JobStatus.FAILED:
        raise HTTPException(status_code=500, detail=f"Processing failed: {job.error}")

    if not job.result_path:
        raise HTTPException(status_code=500, detail="Result file was not created.")

    background_tasks.add_task(_cleanup, job.result_path)

    return FileResponse(
        path=job.result_path,
        filename="report.xlsx",
        media_type=_XLSX_MIME,
    )
