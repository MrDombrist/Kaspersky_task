from src.domain.report.entities import WordStats
from src.domain.report.services import TextAnalysisService


class TestTextAnalysisService:
    def test_single_line_counts_words(self, mock_normalizer):
        svc = TextAnalysisService(normalizer=mock_normalizer)
        stats: dict[str, WordStats] = {}
        svc.analyze_line("жители город", line_index=0, stats=stats)

        assert "житель" in stats
        assert "город" in stats
        assert stats["житель"].line_counts[0] == 1
        assert stats["город"].line_counts[0] == 1

    def test_same_lemma_counted_once(self, mock_normalizer):
        svc = TextAnalysisService(normalizer=mock_normalizer)
        stats: dict[str, WordStats] = {}
        svc.analyze_line("жители жителем жителями", line_index=0, stats=stats)

        assert stats["житель"].line_counts[0] == 3

    def test_multiline_updates_correct_index(self, mock_normalizer):
        svc = TextAnalysisService(normalizer=mock_normalizer)
        stats: dict[str, WordStats] = {}
        svc.analyze_line("жители города", 0, stats)
        svc.analyze_line("жителем и горожанин", 1, stats)
        svc.analyze_line("город и жители", 2, stats)

        # "житель" appears in lines 0, 1, 2
        assert stats["житель"].line_counts == {0: 1, 1: 1, 2: 1}
        # "город" appears in lines 0 and 2
        assert stats["город"].line_counts == {0: 1, 2: 1}

    def test_empty_line_skipped(self, mock_normalizer):
        svc = TextAnalysisService(normalizer=mock_normalizer)
        stats: dict[str, WordStats] = {}
        svc.analyze_line("", line_index=0, stats=stats)
        assert stats == {}

    def test_whitespace_only_line_skipped(self, mock_normalizer):
        svc = TextAnalysisService(normalizer=mock_normalizer)
        stats: dict[str, WordStats] = {}
        svc.analyze_line("   \t  ", line_index=0, stats=stats)
        assert stats == {}

    def test_build_stats_from_lines(self, mock_normalizer, sample_lines):
        svc = TextAnalysisService(normalizer=mock_normalizer)
        stats, n = svc.build_stats_from_lines(sample_lines)

        assert n == 3
        assert stats["житель"].total == 3
        assert stats["город"].total == 2

    def test_accumulates_across_multiple_calls_same_line(self, mock_normalizer):
        svc = TextAnalysisService(normalizer=mock_normalizer)
        stats: dict[str, WordStats] = {}
        # Call analyze_line twice for the same index — should accumulate
        svc.analyze_line("тест тест", 0, stats)
        svc.analyze_line("тест", 0, stats)
        assert stats["тест"].line_counts[0] == 3

    def test_word_count_greater_than_one_per_line(self, mock_normalizer):
        svc = TextAnalysisService(normalizer=mock_normalizer)
        stats: dict[str, WordStats] = {}
        svc.analyze_line("тест тест тест", 0, stats)
        assert stats["тест"].line_counts[0] == 3
