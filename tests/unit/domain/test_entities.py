import uuid

from src.domain.report.entities import JobStatus, ReportJob, WordStats


class TestWordStats:
    def test_total_sums_all_lines(self):
        ws = WordStats(word="житель")
        ws.add(0, 3)
        ws.add(2, 5)
        assert ws.total == 8

    def test_total_zero_when_empty(self):
        ws = WordStats(word="тест")
        assert ws.total == 0

    def test_add_accumulates_for_same_line(self):
        ws = WordStats(word="слово")
        ws.add(0, 2)
        ws.add(0, 3)
        assert ws.line_counts[0] == 5

    def test_per_line_str_fills_zeros(self):
        ws = WordStats(word="житель")
        ws.add(1, 11)
        ws.add(3, 3)
        result = ws.per_line_str(total_lines=5)
        assert result == "0,11,0,3,0"

    def test_per_line_str_single_line(self):
        ws = WordStats(word="тест")
        ws.add(0, 7)
        assert ws.per_line_str(total_lines=1) == "7"

    def test_per_line_str_no_occurrences(self):
        ws = WordStats(word="пусто")
        assert ws.per_line_str(total_lines=3) == "0,0,0"


class TestReportJob:
    def test_default_status_is_pending(self):
        job = ReportJob(job_id=uuid.uuid4())
        assert job.status == JobStatus.PENDING

    def test_can_mutate_status(self):
        job = ReportJob(job_id=uuid.uuid4())
        job.status = JobStatus.DONE
        assert job.status == JobStatus.DONE

    def test_error_defaults_to_none(self):
        job = ReportJob(job_id=uuid.uuid4())
        assert job.error is None
