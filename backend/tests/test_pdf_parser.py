import pytest
from app.parser.pdf_parser import parse
from app.models.script_data import ScriptData, LineType


PULP_FICTION = "tests/fixtures/pulp_fiction.pdf"
PARASITE     = "tests/fixtures/parasite.pdf"
SCANNED      = "tests/fixtures/west_wing_pilot.pdf"


# ── ScriptData structure ──────────────────────────────────────────────────────

def test_parse_returns_script_data():
    result = parse(PULP_FICTION)
    assert isinstance(result, ScriptData)

def test_parse_title_inferred():
    result = parse(PULP_FICTION)
    assert result.title != ""
    assert isinstance(result.title, str)

def test_parse_total_pages():
    result = parse(PULP_FICTION)
    assert result.total_pages == 126

def test_parse_source_format():
    result = parse(PULP_FICTION)
    assert result.source_format == "pdf"


# ── Scenes ────────────────────────────────────────────────────────────────────

def test_parse_scenes_not_empty():
    result = parse(PULP_FICTION)
    assert len(result.scenes) > 0

def test_parse_scene_count_reasonable():
    result = parse(PULP_FICTION)
    # Pulp Fiction has ~90-100 detectable scenes
    assert 80 <= len(result.scenes) <= 110

def test_parse_scenes_have_headings():
    result = parse(PULP_FICTION)
    for scene in result.scenes:
        assert scene.heading != ""

def test_parse_scenes_have_page_numbers():
    result = parse(PULP_FICTION)
    for scene in result.scenes:
        assert scene.page_start >= 1
        assert scene.page_end >= scene.page_start

def test_parse_scene_ids_sequential():
    result = parse(PULP_FICTION)
    ids = [s.scene_id for s in result.scenes]
    assert ids == list(range(1, len(result.scenes) + 1))


# ── Characters ────────────────────────────────────────────────────────────────

def test_parse_characters_not_empty():
    result = parse(PULP_FICTION)
    assert len(result.characters) > 0

def test_parse_major_characters_present():
    result = parse(PULP_FICTION)
    assert "JULES" in result.characters
    assert "VINCENT" in result.characters
    assert "BUTCH" in result.characters
    assert "MIA" in result.characters

def test_parse_no_contd_characters():
    result = parse(PULP_FICTION)
    for name in result.characters:
        assert "CONT'D" not in name
        assert "CONTINUED" not in name

def test_parse_character_names_uppercase():
    result = parse(PULP_FICTION)
    for name in result.characters:
        assert name == name.upper()

def test_parse_jules_has_most_lines():
    result = parse(PULP_FICTION)
    top_character = max(result.characters, key=result.characters.get)
    assert top_character == "JULES"


# ── Dialogue ──────────────────────────────────────────────────────────────────

def test_parse_dialogue_lines_exist():
    result = parse(PULP_FICTION)
    all_lines = [line for scene in result.scenes for line in scene.dialogue]
    assert len(all_lines) > 0

def test_parse_dialogue_has_character():
    result = parse(PULP_FICTION)
    for scene in result.scenes:
        for line in scene.dialogue:
            assert line.character != ""

def test_parse_dialogue_has_text():
    result = parse(PULP_FICTION)
    for scene in result.scenes:
        for line in scene.dialogue:
            assert line.text.strip() != ""

def test_parse_dialogue_has_page():
    result = parse(PULP_FICTION)
    for scene in result.scenes:
        for line in scene.dialogue:
            assert line.page >= 1


# ── Scanned PDF rejection ─────────────────────────────────────────────────────

def test_parse_rejects_scanned_pdf():
    from app.utils.text_layer import ScannedPDFError
    with pytest.raises(ScannedPDFError):
        parse(SCANNED)


# ── Parasite (second fixture) ─────────────────────────────────────────────────

def test_parse_parasite_returns_script_data():
    result = parse(PARASITE)
    assert isinstance(result, ScriptData)

def test_parse_parasite_has_scenes():
    result = parse(PARASITE)
    assert len(result.scenes) > 0

def test_parse_parasite_has_characters():
    result = parse(PARASITE)
    assert len(result.characters) > 0

def test_parse_parasite_no_warnings():
    result = parse(PARASITE)
    assert len(result.parse_warnings) == 0