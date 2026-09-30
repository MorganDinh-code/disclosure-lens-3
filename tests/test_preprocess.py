from disclosure_lens.preprocess import parse_document, split_sentences


def test_abbreviations_do_not_split():
    s = split_sentences("Acme Corp. reported sales of $1.2 bn in the U.S. market. Growth was strong.")
    assert len(s) == 2


def test_units_at_sentence_end_do_split():
    s = split_sentences("Sales reached $1.2 bn. The market reacted well.")
    assert s == ["Sales reached $1.2 bn.", "The market reacted well."]


def test_corp_in_headline_is_one_sentence():
    assert len(split_sentences("Acme Corp. Reports Third Quarter Results")) == 1


def test_hard_wrapped_lines_are_joined():
    assert split_sentences("Revenue rose\nto $2 billion. Costs fell.") == ["Revenue rose to $2 billion.", "Costs fell."]


def test_positions_are_normalized():
    recs = parse_document("One. Two.\n\nThree. Four.")
    assert [round(r["pos_doc"], 2) for r in recs] == [0.25, 0.5, 0.75, 1.0]
