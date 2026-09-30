import pytest

from disclosure_lens import lexicon_info as li
from disclosure_lens.classify import direction
from disclosure_lens.hedges import hedge_matches
from disclosure_lens.tone import tone_matches


@pytest.mark.parametrize("term", li.NEGATIVE_EVENT_TERMS)
def test_every_listed_bad_news_term_is_read_as_bad_news(term):
    assert direction(f"The company reported {term}.") == -1


def test_positive_terms_listed_are_read_as_good_news():
    for t in ["exceeded", "outperformed", "beat expectations"]:
        assert direction(f"The company {t}.") == 1


def test_hedge_matches_report_tiers_in_order():
    assert hedge_matches("We expect sales may rise.") == [("expect", "moderate"), ("may", "low")]


def test_tone_matches_include_negation():
    assert tone_matches("Results were not strong and losses grew.") == [("not strong", -1), ("losses", -1)]


def test_lookup_word():
    assert any("Low certainty" in x for x in li.lookup_word("may"))
    assert any("cost-type" in x for x in li.lookup_word("expenses"))
    assert li.lookup_word("zebra") == []
