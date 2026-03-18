import json
from uuid import UUID

from aiokafka import AIOKafkaProducer

from src.core.config import settings


class ReportJobProducer:
    """
    Publishes report-processing jobs to a Kafka topic.

    When USE_KAFKA=true the API sends a lightweight message (job_id + file_path)
    instead of blocking the request thread. A separate consumer pool processes
    the actual file, keeping the API fully responsive under heavy load.
    """

    def __init__(self) -> None:
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )
        await self._producer.start()

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()

    async def send_job(self, job_id: UUID, file_path: str) -> None:
        if not self._producer:
            raise RuntimeError("Producer not started. Call start() first.")
        message = json.dumps({"job_id": str(job_id), "file_path": file_path})
        await self._producer.send_and_wait(
            settings.KAFKA_TOPIC_REPORTS,
            message.encode("utf-8"),
        )
