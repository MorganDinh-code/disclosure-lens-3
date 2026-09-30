from disclosure_lens.classify import direction, is_material_negative


def test_falling_costs_are_good_news():
    assert direction("Operating expenses declined 5%.") == 1


def test_rising_costs_are_bad_news():
    assert direction("Costs increased 12% year over year.") == -1


def test_revenue_decline_is_bad_news():
    assert direction("Demand in one segment declined 18%.") == -1


def test_record_as_adjective_vs_verb():
    assert direction("We delivered record revenue.") == 1
    assert direction("The company may record a charge.") == 0


def test_whole_word_matching():
    assert direction("The backup plan has a glossy finish.") == 0


def test_materiality_needs_real_figure_or_severe_term():
    assert is_material_negative("Revenue declined 18% in the segment.")
    assert is_material_negative("The company faces litigation.")
    assert not is_material_negative("Q3 sales declined.")
