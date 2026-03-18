from functools import lru_cache

import pymorphy3

from src.core.config import settings

_morph = pymorphy3.MorphAnalyzer()


@lru_cache(maxsize=settings.LRU_CACHE_SIZE)
def get_normal_form(word: str) -> str:
    """
    Return the canonical (lemma) form of *word*.

    «житель», «жителем», «жителями» → «житель»

    Results are cached in-process (LRU). For multi-process deployments the
    cache can be replaced with a Redis-backed version via USE_REDIS_CACHE.
    """
    return str(_morph.parse(word)[0].normal_form)
