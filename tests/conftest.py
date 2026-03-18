import pytest


@pytest.fixture
def mock_normalizer():
    """Fast in-memory normalizer — avoids loading pymorphy3 in unit tests."""
    mapping = {
        "жители": "житель",
        "жителем": "житель",
        "жителями": "житель",
        "житель": "житель",
        "город": "город",
        "города": "город",
        "горожанин": "горожанин",
        "и": "и",
        "тест": "тест",
    }

    def normalizer(word: str) -> str:
        return mapping.get(word, word)

    return normalizer


@pytest.fixture
def sample_lines():
    return [
        "жители города",
        "жителем и горожанин",
        "город и жители",
    ]
