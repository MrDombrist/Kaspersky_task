from src.infrastructure.nlp.morphology import get_normal_form


class TestGetNormalForm:
    def test_base_form_unchanged(self):
        assert get_normal_form("житель") == "житель"

    def test_inflected_forms_normalise(self):
        assert get_normal_form("жителем") == "житель"
        assert get_normal_form("жителями") == "житель"
        assert get_normal_form("жителей") == "житель"

    def test_verb_normalises_to_infinitive(self):
        # «бежал» → «бежать»
        result = get_normal_form("бежал")
        assert result == "бежать"

    def test_returns_string(self):
        result = get_normal_form("тест")
        assert isinstance(result, str)

    def test_cache_hit_returns_same(self):
        # Two calls with the same word must return identical result (cache doesn't corrupt)
        a = get_normal_form("городе")
        b = get_normal_form("городе")
        assert a == b

    def test_lowercase_input(self):
        result = get_normal_form("города")
        assert result == "город"
