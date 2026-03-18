import asyncio
import json
import uuid

from aiokafka import AIOKafkaConsumer

from src.core.config import settings
from src.domain.report.entities import ReportJob


class ReportJobConsumer:
    """
    Kafka consumer that picks up report jobs and processes them in a thread pool.

    Run this in a separate process (or as a background asyncio task) so that
    heavy file processing never interferes with the HTTP server event loop.

    Usage::

        consumer = ReportJobConsumer()
        await consumer.start()
        try:
            await consumer.consume()     # blocks until cancelled
        finally:
            await consumer.stop()
    """

    def __init__(self) -> None:
        self._consumer: AIOKafkaConsumer | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            settings.KAFKA_TOPIC_REPORTS,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_GROUP_ID,
            enable_auto_commit=True,
        )
        await self._consumer.start()

    async def stop(self) -> None:
        if self._consumer:
            await self._consumer.stop()

    async def consume(self) -> None:
        if not self._consumer:
            raise RuntimeError("Consumer not started. Call start() first.")

        from src.application.report.use_cases import SyncProcessFileUseCase
        from src.infrastructure.excel.report_builder import ExcelReportBuilder
        from src.infrastructure.nlp.morphology import get_normal_form

        processor = SyncProcessFileUseCase(
            report_builder=ExcelReportBuilder(),
            normalizer=get_normal_form,
        )

        loop = asyncio.get_event_loop()
        async for msg in self._consumer:
            data = json.loads(msg.value.decode("utf-8"))
            job = ReportJob(
                job_id=uuid.UUID(data["job_id"]),
                file_path=data["file_path"],
                result_path=data.get("result_path", ""),
            )
            # Run CPU-bound work off the event loop
            await loop.run_in_executor(None, processor.process, job)
