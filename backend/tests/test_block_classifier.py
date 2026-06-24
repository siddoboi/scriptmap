import pytest
from app.parser.block_classifier import (
    classify_line,
    strip_character_suffixes,
    X_LEFT_MARGIN,
    X_DIALOGUE,
    X_PARENTHETICAL,
    X_CHARACTER,
    X_TRANSITION,
)
from app.models.script_data import LineType


# ── strip_character_suffixes ──────────────────────────────────────────────────

def test_strip_contd():
    assert strip_character_suffixes("VINCENT (CONT'D)") == "VINCENT"

def test_strip_continued():
    assert strip_character_suffixes("JULES (CONTINUED)") == "JULES"

def test_strip_vo():
    assert strip_character_suffixes("MIA (V.O.)") == "MIA"

def test_strip_os():
    assert strip_character_suffixes("BUTCH (O.S.)") == "BUTCH"

def test_strip_no_suffix():
    assert strip_character_suffixes("VINCENT") == "VINCENT"


# ── Empty lines ───────────────────────────────────────────────────────────────

def test_empty_line():
    assert classify_line("", X_LEFT_MARGIN) == LineType.EMPTY

def test_whitespace_only():
    assert classify_line("   ", X_LEFT_MARGIN) == LineType.EMPTY


# ── Scene headings ────────────────────────────────────────────────────────────

def test_int_scene_heading():
    assert classify_line("INT. COFFEE SHOP - MORNING", X_LEFT_MARGIN) == LineType.SCENE_HEADING

def test_ext_scene_heading():
    assert classify_line("EXT. PARKING LOT - NIGHT", X_LEFT_MARGIN) == LineType.SCENE_HEADING

def test_int_ext_scene_heading():
    assert classify_line("INT./EXT. CAR - DAY", X_LEFT_MARGIN) == LineType.SCENE_HEADING

def test_scene_heading_wrong_x():
    # INT. at dialogue x-position should NOT be a scene heading
    assert classify_line("INT. COFFEE SHOP - MORNING", X_DIALOGUE) != LineType.SCENE_HEADING


# ── Transitions ───────────────────────────────────────────────────────────────

def test_cut_to_by_position():
    assert classify_line("CUT TO:", X_TRANSITION) == LineType.TRANSITION

def test_fade_out_by_position():
    assert classify_line("FADE OUT.", X_TRANSITION) == LineType.TRANSITION

def test_fade_in_by_content():
    # FADE IN: at left margin - matched by regex
    assert classify_line("FADE IN:", X_LEFT_MARGIN) == LineType.TRANSITION

def test_smash_cut():
    assert classify_line("SMASH CUT TO:", X_TRANSITION) == LineType.TRANSITION


# ── Character cues ────────────────────────────────────────────────────────────

def test_character_cue():
    assert classify_line("VINCENT", X_CHARACTER) == LineType.CHARACTER

def test_character_cue_two_words():
    assert classify_line("YOUNG MAN", X_CHARACTER) == LineType.CHARACTER

def test_character_contd_classified_as_character():
    # CONT'D is stripped before isupper() check - still CHARACTER
    assert classify_line("VINCENT (CONT'D)", X_CHARACTER) == LineType.CHARACTER

def test_character_wrong_x():
    # All-caps at action x-position should NOT be a character cue
    assert classify_line("VINCENT", X_LEFT_MARGIN) != LineType.CHARACTER

def test_long_allcaps_not_character():
    # All-caps action line too long to be a character name
    assert classify_line(
        "THE GUNS ARE DRAWN AND THE CROWD GOES SILENT",
        X_CHARACTER
    ) != LineType.CHARACTER


# ── Parentheticals ────────────────────────────────────────────────────────────

def test_parenthetical():
    assert classify_line("(beat)", X_PARENTHETICAL) == LineType.PARENTHETICAL

def test_parenthetical_with_text():
    assert classify_line("(imitates a duck)", X_PARENTHETICAL) == LineType.PARENTHETICAL

def test_parenthetical_wrong_x():
    assert classify_line("(beat)", X_LEFT_MARGIN) != LineType.PARENTHETICAL


# ── Dialogue ──────────────────────────────────────────────────────────────────

def test_dialogue_line():
    assert classify_line("What so you want to know?", X_DIALOGUE) == LineType.DIALOGUE

def test_dialogue_multiword():
    assert classify_line(
        "Well, hash is legal there, right?",
        X_DIALOGUE
    ) == LineType.DIALOGUE


# ── Action lines ──────────────────────────────────────────────────────────────

def test_action_line():
    assert classify_line(
        "A normal Denny's coffee shop in Los Angeles.",
        X_LEFT_MARGIN
    ) == LineType.ACTION

def test_action_not_scene_heading():
    assert classify_line(
        "He reaches into his pocket and pulls out a gun.",
        X_LEFT_MARGIN
    ) == LineType.ACTION


# ── TV act breaks ─────────────────────────────────────────────────────────────

def test_tv_act_one():
    assert classify_line("ACT ONE", X_CHARACTER) == LineType.TRANSITION

def test_tv_end_of_teaser():
    assert classify_line("END OF TEASER", X_CHARACTER) == LineType.TRANSITION

def test_tv_teaser():
    assert classify_line("TEASER", X_CHARACTER) == LineType.TRANSITION