from app.parser.dual_dialogue import (
    group_by_line,
    detect_dual_dialogue_sections,
    split_dual_dialogue_columns,
    DUAL_DIALOGUE_MIN_X_GAP,
)


def make_word(text: str, x0: float, top: float) -> dict:
    """Helper to create a pdfplumber-style word dict."""
    return {'text': text, 'x0': x0, 'top': top, 'x1': x0 + len(text) * 7}


# ── group_by_line ─────────────────────────────────────────────────────────────

def test_group_by_line_same_top():
    words = [make_word("VINCENT", 170.0, 100.0), make_word("JULES", 350.0, 100.0)]
    lines = group_by_line(words)
    assert len(lines) == 1


def test_group_by_line_different_top():
    words = [make_word("VINCENT", 170.0, 100.0), make_word("JULES", 170.0, 200.0)]
    lines = group_by_line(words)
    assert len(lines) == 2


def test_group_by_line_within_tolerance():
    # Words within 5pt of each other should be on the same line
    words = [make_word("VINCENT", 170.0, 100.0), make_word("JULES", 350.0, 103.0)]
    lines = group_by_line(words)
    assert len(lines) == 1


def test_group_by_line_outside_tolerance():
    words = [make_word("VINCENT", 170.0, 100.0), make_word("JULES", 350.0, 110.0)]
    lines = group_by_line(words)
    assert len(lines) == 2


# ── detect_dual_dialogue_sections ─────────────────────────────────────────────

def test_detect_dual_dialogue_two_characters_same_line():
    """Two character cues on the same line = dual dialogue."""
    words = [
        make_word("VINCENT", 170.0, 100.0),
        make_word("JULES",   350.0, 100.0),
        make_word("You",     170.0, 115.0),
        make_word("sure?",   170.0, 115.0),
        make_word("Yeah.",   350.0, 115.0),
    ]
    sections = detect_dual_dialogue_sections(words)
    assert len(sections) == 1
    assert sections[0][0] == 100.0


def test_detect_no_dual_dialogue_single_column():
    """Normal sequential dialogue should not be detected as dual."""
    words = [
        make_word("VINCENT", 241.0, 100.0),
        make_word("What",    170.0, 115.0),
        make_word("do",      190.0, 115.0),
        make_word("JULES",   241.0, 200.0),
        make_word("Nothing.",170.0, 215.0),
    ]
    sections = detect_dual_dialogue_sections(words)
    assert len(sections) == 0


def test_detect_no_dual_dialogue_close_x():
    """Two all-caps words close together horizontally are not dual dialogue."""
    words = [
        make_word("ED",       241.0, 100.0),
        make_word("SULLIVAN", 259.0, 100.0),  # gap = 18pt, below threshold
    ]
    sections = detect_dual_dialogue_sections(words)
    assert len(sections) == 0


def test_detect_dual_dialogue_gap_exactly_at_threshold():
    """Gap exactly at DUAL_DIALOGUE_MIN_X_GAP should be detected."""
    words = [
        make_word("VINCENT", 170.0, 100.0),
        make_word("JULES",   170.0 + DUAL_DIALOGUE_MIN_X_GAP, 100.0),
    ]
    sections = detect_dual_dialogue_sections(words)
    assert len(sections) == 1


# ── split_dual_dialogue_columns ───────────────────────────────────────────────

def test_split_columns_correctly():
    words = [
        make_word("VINCENT", 170.0, 100.0),
        make_word("JULES",   350.0, 100.0),
        make_word("You",     170.0, 115.0),
        make_word("Yeah.",   350.0, 115.0),
    ]
    left, right = split_dual_dialogue_columns(
        words, section_top=100.0, section_bottom=200.0, split_x=260.0
    )
    assert len(left)  == 2  # VINCENT + You
    assert len(right) == 2  # JULES + Yeah.


def test_split_columns_left_only():
    words = [
        make_word("VINCENT", 170.0, 100.0),
        make_word("You",     170.0, 115.0),
    ]
    left, right = split_dual_dialogue_columns(
        words, section_top=100.0, section_bottom=200.0, split_x=260.0
    )
    assert len(left)  == 2
    assert len(right) == 0


def test_split_excludes_words_outside_section():
    words = [
        make_word("VINCENT", 170.0, 50.0),   # above section
        make_word("JULES",   350.0, 100.0),   # inside section
        make_word("below",   170.0, 300.0),   # below section
    ]
    left, right = split_dual_dialogue_columns(
        words, section_top=90.0, section_bottom=200.0, split_x=260.0
    )
    assert len(left)  == 0
    assert len(right) == 1