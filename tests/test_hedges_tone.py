from disclosure_lens.hedges import hedge_counts, hedge_density, modal_intensity
from disclosure_lens.tone import tone_score


def test_may_the_month_is_not_a_hedge():
    assert hedge_counts("We report on May 5.")["low"] == 0
    assert hedge_counts("We may report late.")["low"] == 1


def test_multiword_hedges():
    assert hedge_counts("This is subject to review, depending on demand.")["low"] == 2


def test_density_and_modal():
    assert hedge_density("") == 0.0
    assert modal_intensity("Nothing here.") is None
    assert modal_intensity("Sales might fall.") == 1


def test_negation_flips_positive_words():
    assert tone_score("Results were strong.") > 0
    assert tone_score("Results were not strong.") < 0
