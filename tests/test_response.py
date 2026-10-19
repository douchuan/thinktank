from hundred_schools.models.response import AdviserOpinion, count_cjk_characters, length_warning


def test_count_cjk_characters_ignores_ascii_and_punctuation() -> None:
    assert count_cjk_characters("儒家 Advice！123道家") == 4


def test_length_warning_for_advice_in_target_range() -> None:
    opinion = AdviserOpinion(school="儒家", advice="仁义礼智信" * 12)
    assert length_warning(opinion) is None


def test_length_warning_for_short_advice() -> None:
    opinion = AdviserOpinion(school="法家", advice="先立规则，再明权责。")
    warning = length_warning(opinion)
    assert warning is not None
    assert "法家" in warning
