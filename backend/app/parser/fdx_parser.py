import xml.etree.ElementTree as ET
from collections import defaultdict

from app.models.script_data import (
    DialogueLine, LineType, SceneBlock, ScriptData
)
from app.parser.block_classifier import strip_character_suffixes
from app.parser.normalizer import normalize_character_name, repair_encoding


# FDX element type to LineType mapping
FDX_TYPE_MAP = {
    'Scene Heading':  LineType.SCENE_HEADING,
    'Action':         LineType.ACTION,
    'Character':      LineType.CHARACTER,
    'Dialogue':       LineType.DIALOGUE,
    'Parenthetical':  LineType.PARENTHETICAL,
    'Transition':     LineType.TRANSITION,
    'Shot':           LineType.ACTION,
    'Cast List':      LineType.ACTION,
    'More':           LineType.EMPTY,
    'Continued':      LineType.EMPTY,
}


def _get_element_text(element) -> str:
    """Extract all text from an FDX paragraph element, including nested spans."""
    parts = []
    if element.text:
        parts.append(element.text)
    for child in element:
        if child.text:
            parts.append(child.text)
        if child.tail:
            parts.append(child.tail)
    return repair_encoding(''.join(parts).strip())


def _validate_character_line(text: str) -> bool:
    """
    Validate that a line tagged as Character in FDX is actually a character name.
    FDX element types are priors, not ground truth.
    """
    if not text:
        return False
    clean = strip_character_suffixes(text)
    # Must be all-caps after stripping suffixes
    if not clean.isupper():
        return False
    # Must be reasonably short
    if len(clean) > 35:
        return False
    return True


def parse(path: str) -> ScriptData:
    """
    Parse a Final Draft FDX screenplay file into a ScriptData object.

    FDX is XML - each paragraph has a Type attribute indicating its role.
    We use the Type as a prior but validate against content heuristics.
    """
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        raise ValueError(f"Invalid FDX file - XML parse error: {e}")

    root = tree.getroot()

    # FDX structure: FinalDraft > Content > Paragraph*
    # Try both with and without namespace
    content = root.find('Content')
    if content is None:
        # Try with namespace
        for child in root:
            if 'Content' in child.tag:
                content = child
                break

    if content is None:
        raise ValueError("FDX file has no Content element")

    warnings: list[str] = []
    scenes: list[SceneBlock] = []
    scene_id = 0
    current_scene: SceneBlock | None = None
    last_character: str | None = None
    page_num = 1

    for paragraph in content:
        # Get element type
        fdx_type = paragraph.get('Type', 'Action')
        text = _get_element_text(paragraph)

        if not text:
            last_character = None
            continue

        # Map FDX type to LineType, use as prior
        line_type = FDX_TYPE_MAP.get(fdx_type, LineType.ACTION)

        # Estimate page number from paragraph position
        # FDX doesn't always have explicit page breaks
        # We use a rough heuristic: increment page every 55 paragraphs
        if scenes:
            page_num = max(1, sum(
                len(s.dialogue) for s in scenes
            ) // 8 + 1)

        # ── Heuristic validation ──────────────────────────────────────────
        if line_type == LineType.CHARACTER:
            if not _validate_character_line(text):
                # FDX tagged as Character but doesn't look like one
                warnings.append(
                    f"FDX character element failed validation: '{text}' "
                    f"- treating as Action"
                )
                line_type = LineType.ACTION

        elif line_type == LineType.SCENE_HEADING:
            # Validate scene headings have INT. or EXT.
            if not any(text.upper().startswith(p) for p in
                       ['INT.', 'EXT.', 'INT/', 'EXT/', 'I/E']):
                # Could be a TV act break or title card
                line_type = LineType.ACTION

        # ── Process by type ───────────────────────────────────────────────
        if line_type == LineType.EMPTY:
            continue

        elif line_type == LineType.SCENE_HEADING:
            if current_scene is not None:
                if current_scene.page_end == 0:
                    current_scene.page_end = page_num
                scenes.append(current_scene)

            scene_id += 1
            current_scene = SceneBlock(
                scene_id=scene_id,
                heading=text,
                act=0,
                page_start=page_num,
                page_end=0,
                characters_present=[],
            )
            last_character = None

        elif line_type == LineType.TRANSITION:
            last_character = None

        elif line_type == LineType.CHARACTER:
            canonical = normalize_character_name(
                strip_character_suffixes(text)
            )
            last_character = canonical

        elif line_type == LineType.PARENTHETICAL:
            pass

        elif line_type == LineType.DIALOGUE:
            if last_character and current_scene is not None:
                dialogue_line = DialogueLine(
                    character=last_character,
                    text=text,
                    page=page_num,
                    line_type=LineType.DIALOGUE,
                    scene_id=current_scene.scene_id,
                )
                current_scene.dialogue.append(dialogue_line)

                if last_character not in current_scene.characters_present:
                    current_scene.characters_present.append(last_character)

        elif line_type == LineType.ACTION:
            last_character = None

    # Close final scene
    if current_scene is not None:
        if current_scene.page_end == 0:
            current_scene.page_end = page_num
        scenes.append(current_scene)

    # Build character line count map
    characters: dict[str, int] = defaultdict(int)
    for scene in scenes:
        for line in scene.dialogue:
            characters[line.character] += 1

    # Infer title from filename
    import os
    basename = os.path.basename(path)
    name, _ = os.path.splitext(basename)
    title = name.replace('_', ' ').replace('-', ' ').title()

    return ScriptData(
        title=title,
        total_pages=page_num,
        scenes=scenes,
        characters=dict(characters),
        act_breaks=[],
        source_format='fdx',
        parse_warnings=warnings,
    )