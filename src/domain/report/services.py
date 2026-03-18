from collections import Counter
from collections.abc import Callable

from src.domain.report.entities import WordStats


class TextAnalysisService:
    """
    Domain service: analyses text lines and accumulates word-form statistics.

    Accepts a *normalizer* callable so the domain stays independent of any
    concrete NLP library (pymorphy3, stanza, etc.).
    """

    def __init__(self, normalizer: Callable[[str], str]) -> None:
        self._normalizer = normalizer

    def analyze_line(
        self,
        line: str,
        line_index: int,
        stats: dict[str, WordStats],
    ) -> None:
        words = line.split()
        if not words:
            return

        counts = Counter(self._normalizer(w.lower()) for w in words if w.strip())
        for word, count in counts.items():
            if word not in stats:
                stats[word] = WordStats(word=word)
            stats[word].add(line_index, count)

    def build_stats_from_lines(
        self,
        lines: list[str],
    ) -> tuple[dict[str, WordStats], int]:
        stats: dict[str, WordStats] = {}
        for i, line in enumerate(lines):
            self.analyze_line(line.rstrip("\n"), i, stats)
        return stats, len(lines)
