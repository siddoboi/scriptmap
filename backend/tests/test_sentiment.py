import pytest
from app.nlp.sentiment import score_line, score_script, _rolling_average


# ── score_line ────────────────────────────────────────────────────────────────

def test_score_line_positive():
    score = score_line("I love this, it's wonderful and amazing!")
    assert score > 0.0

def test_score_line_negative():
    score = score_line("I hate this, it's terrible and awful.")
    assert score < 0.0

def test_score_line_neutral():
    score = score_line("The car is parked outside.")
    assert -0.3 < score < 0.3

def test_score_line_returns_float():
    score = score_line("Hello there.")
    assert isinstance(score, float)

def test_score_line_range():
    score = score_line("This is absolutely the best day of my entire life!")
    assert -1.0 <= score <= 1.0

def test_score_line_empty():
    score = score_line("")
    assert score == 0.0

def test_score_line_short():
    score = score_line("No.")
    assert isinstance(score, float)


# ── _rolling_average ──────────────────────────────────────────────────────────

def test_rolling_average_single_value():
    result = _rolling_average([0.5], window=5)
    assert result == [0.5]

def test_rolling_average_expanding_window():
    result = _rolling_average([1.0, 0.0], window=5)
    assert result[0] == 1.0
    assert result[1] == 0.5

def test_rolling_average_full_window():
    values = [1.0, 1.0, 1.0, 1.0, 1.0, 0.0]
    result = _rolling_average(values, window=5)
    # Last value: window covers indices 1-5 = [1,1,1,1,0] = avg 0.8
    assert abs(result[-1] - 0.8) < 0.001

def test_rolling_average_length_preserved():
    values = [0.1, 0.2, 0.3, 0.4, 0.5]
    result = _rolling_average(values, window=3)
    assert len(result) == len(values)

def test_rolling_average_smoothing():
    # Smoothed values should be less extreme than raw after the first point
    values = [1.0, -1.0, 1.0, -1.0, 1.0]
    result = _rolling_average(values, window=5)
    # Skip first value - it has no prior context to smooth against
    assert max(result[1:]) < 1.0
    assert min(result[1:]) > -1.0


# ── score_script ──────────────────────────────────────────────────────────────

def test_score_script_returns_dict():
    from app.parser.pdf_parser import parse
    result = parse("tests/fixtures/pulp_fiction.pdf")
    arcs = score_script(result)
    assert isinstance(arcs, dict)

def test_score_script_all_characters_have_arcs():
    from app.parser.pdf_parser import parse
    result = parse("tests/fixtures/pulp_fiction.pdf")
    arcs = score_script(result)
    for character in result.characters:
        assert character in arcs

def test_score_script_arc_has_required_keys():
    from app.parser.pdf_parser import parse
    result = parse("tests/fixtures/pulp_fiction.pdf")
    arcs = score_script(result)
    for point in arcs["JULES"][:3]:
        assert "page" in point
        assert "score" in point
        assert "raw" in point

def test_score_script_scores_in_range():
    from app.parser.pdf_parser import parse
    result = parse("tests/fixtures/pulp_fiction.pdf")
    arcs = score_script(result)
    for character, arc in arcs.items():
        for point in arc:
            assert -1.0 <= point["score"] <= 1.0
            assert -1.0 <= point["raw"] <= 1.0

def test_score_script_arc_sorted_by_page():
    from app.parser.pdf_parser import parse
    result = parse("tests/fixtures/pulp_fiction.pdf")
    arcs = score_script(result)
    for character, arc in arcs.items():
        pages = [p["page"] for p in arc]
        assert pages == sorted(pages)

def test_score_script_sets_sentiment_on_lines():
    from app.parser.pdf_parser import parse
    result = parse("tests/fixtures/pulp_fiction.pdf")
    score_script(result)
    for scene in result.scenes:
        for line in scene.dialogue:
            assert line.sentiment is not None