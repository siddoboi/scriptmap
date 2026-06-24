import pytest
from app.parser.fdx_parser import parse
from app.models.script_data import ScriptData


PARASITE_FDX = "tests/fixtures/parasite.fdx"


# ── ScriptData structure ──────────────────────────────────────────────────────

def test_fdx_parse_returns_script_data():
    result = parse(PARASITE_FDX)
    assert isinstance(result, ScriptData)

def test_fdx_parse_source_format():
    result = parse(PARASITE_FDX)
    assert result.source_format == "fdx"

def test_fdx_parse_title_inferred():
    result = parse(PARASITE_FDX)
    assert result.title != ""


# ── Scenes ────────────────────────────────────────────────────────────────────

def test_fdx_parse_scenes_not_empty():
    result = parse(PARASITE_FDX)
    assert len(result.scenes) > 0

def test_fdx_parse_scene_count_reasonable():
    result = parse(PARASITE_FDX)
    # Parasite has ~140-170 detectable scenes in FDX
    assert 100 <= len(result.scenes) <= 200

def test_fdx_parse_scenes_have_headings():
    result = parse(PARASITE_FDX)
    for scene in result.scenes:
        assert scene.heading != ""

def test_fdx_parse_scene_ids_sequential():
    result = parse(PARASITE_FDX)
    ids = [s.scene_id for s in result.scenes]
    assert ids == list(range(1, len(result.scenes) + 1))


# ── Characters ────────────────────────────────────────────────────────────────

def test_fdx_parse_characters_not_empty():
    result = parse(PARASITE_FDX)
    assert len(result.characters) > 0

def test_fdx_parse_major_characters_present():
    result = parse(PARASITE_FDX)
    assert "KI-WOO" in result.characters
    assert "KI-TEK" in result.characters
    assert "KI-JUNG" in result.characters

def test_fdx_parse_no_contd_characters():
    result = parse(PARASITE_FDX)
    for name in result.characters:
        assert "CONT'D" not in name
        assert "CONTINUED" not in name

def test_fdx_parse_character_names_uppercase():
    result = parse(PARASITE_FDX)
    for name in result.characters:
        assert name == name.upper()

def test_fdx_parse_kiwoo_has_most_lines():
    result = parse(PARASITE_FDX)
    top_character = max(result.characters, key=result.characters.get)
    assert top_character == "KI-WOO"


# ── Dialogue ──────────────────────────────────────────────────────────────────

def test_fdx_parse_dialogue_exists():
    result = parse(PARASITE_FDX)
    all_lines = [line for scene in result.scenes for line in scene.dialogue]
    assert len(all_lines) > 0

def test_fdx_parse_dialogue_has_character():
    result = parse(PARASITE_FDX)
    for scene in result.scenes:
        for line in scene.dialogue:
            assert line.character != ""

def test_fdx_parse_dialogue_has_text():
    result = parse(PARASITE_FDX)
    for scene in result.scenes:
        for line in scene.dialogue:
            assert line.text.strip() != ""


# ── Invalid file ──────────────────────────────────────────────────────────────

def test_fdx_parse_invalid_file_raises():
    with pytest.raises((ValueError, Exception)):
        parse("tests/fixtures/pulp_fiction.pdf")


# ── FDX vs PDF consistency ────────────────────────────────────────────────────

def test_fdx_pdf_scene_count_similar():
    from app.parser.pdf_parser import parse as pdf_parse
    fdx_result = parse(PARASITE_FDX)
    pdf_result = pdf_parse("tests/fixtures/parasite.pdf")
    # Scene counts should be within 20% of each other
    diff = abs(len(fdx_result.scenes) - len(pdf_result.scenes))
    assert diff <= max(len(pdf_result.scenes), len(fdx_result.scenes)) * 0.2

def test_fdx_pdf_character_overlap():
    from app.parser.pdf_parser import parse as pdf_parse
    fdx_result = parse(PARASITE_FDX)
    pdf_result = pdf_parse("tests/fixtures/parasite.pdf")
    fdx_chars = set(fdx_result.characters.keys())
    pdf_chars = set(pdf_result.characters.keys())
    # At least 80% of FDX characters should appear in PDF parse
    overlap = len(fdx_chars & pdf_chars) / len(fdx_chars)
    assert overlap >= 0.8