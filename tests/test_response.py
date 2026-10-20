from hundred_schools.models.response import AdviserOpinion, count_words, length_warning


def test_count_words_splits_correctly() -> None:
    assert count_words("Hello world this is a test") == 6


def test_length_warning_for_advice_in_target_range() -> None:
    # 100 words - within 80-150 range
    advice = "word " * 100
    opinion = AdviserOpinion(school="Confucian", advice=advice.strip())
    assert length_warning(opinion) is None


def test_length_warning_for_short_advice() -> None:
    opinion = AdviserOpinion(
        school="Legalist", advice="Establish rules first, then clarify responsibilities."
    )
    warning = length_warning(opinion)
    assert warning is not None
    assert "Legalist" in warning
