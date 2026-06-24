import os
import pdfplumber
from collections import defaultdict

from app.models.script_data import (
    DialogueLine, LineType, SceneBlock, ScriptData
)
from app.parser.block_classifier import classify_line, strip_character_suffixes
from app.parser.normalizer import (
    repair_encoding, normalize_whitespace,
    is_header_footer, normalize_character_name,
    detect_repeating_headers, strip_repeating_headers,
)
from app.parser.dual_dialogue import (
    detect_dual_dialogue_sections,
    split_dual_dialogue_columns,
)
from app.utils.text_layer import detect_text_layer

# Vertical tolerance for grouping words into lines (points)
LINE_TOP_TOLERANCE = 5.0


def _group_words_into_lines(words: list[dict]) -> list[dict]:
    """
    Group pdfplumber word dicts into logical lines by top position.
    Returns list of line dicts: {text, x0, top, words}
    """
    if not words:
        return []

    lines: dict[float, dict] = {}

    for word in words:
        top = word['top']
        matched_key = None

        for key in lines:
            if abs(key - top) <= LINE_TOP_TOLERANCE:
                matched_key = key
                break

        if matched_key is None:
            lines[top] = {
                'text': word['text'],
                'x0': word['x0'],
                'top': top,
                'words': [word],
            }
        else:
            lines[matched_key]['words'].append(word)
            lines[matched_key]['text'] += ' ' + word['text']

    # Sort by top position and re-sort words within each line by x0
    result = []
    for key in sorted(lines.keys()):
        line = lines[key]
        line['words'].sort(key=lambda w: w['x0'])
        line['text'] = ' '.join(w['text'] for w in line['words'])
        result.append(line)

    return result


def _infer_title(path: str) -> str:
    """Infer screenplay title from filename."""
    basename = os.path.basename(path)
    name, _ = os.path.splitext(basename)
    return name.replace('_', ' ').replace('-', ' ').title()


def parse(path: str) -> ScriptData:
    """
    Parse a text-based PDF screenplay into a ScriptData object.

    Pipeline:
    1. Detect text layer (raises ScannedPDFError if image-only)
    2. Extract words per page with coordinates
    3. Detect repeating headers/footers across pages
    4. Group words into lines
    5. Classify each line
    6. Build SceneBlocks and DialogueLines
    7. Detect and handle dual dialogue sections
    8. Return ScriptData
    """
    detect_text_layer(path)

    warnings: list[str] = []
    scenes: list[SceneBlock] = []
    scene_id = 0
    current_scene: SceneBlock | None = None
    last_character: str | None = None

    with pdfplumber.open(path) as pdf:
        total_pages = len(pdf.pages)
        title = _infer_title(path)

        # Pass 1 - collect raw text per page for header/footer detection
        pages_text = []
        for page in pdf.pages:
            text = page.extract_text() or ''
            text = repair_encoding(text)
            pages_text.append(text)

        repeating_headers = detect_repeating_headers(pages_text)

        # Pass 2 - parse word by word
        for page_num, page in enumerate(pdf.pages, start=1):
            words = page.extract_words()
            if not words:
                continue

            # Detect dual dialogue sections on this page
            dual_sections = detect_dual_dialogue_sections(words)

            # Build lines from words
            lines = _group_words_into_lines(words)

            for line in lines:
                raw_text = line['text']
                x0 = line['x0']
                top = line['top']

                # Repair encoding
                raw_text = repair_encoding(raw_text)
                raw_text = normalize_whitespace(raw_text).strip()

                # Skip header/footer lines
                if is_header_footer(raw_text):
                    continue
                if raw_text in repeating_headers:
                    continue

                # Classify the line
                line_type = classify_line(raw_text, x0)

                if line_type == LineType.EMPTY:
                    last_character = None
                    continue

                elif line_type == LineType.SCENE_HEADING:
                    # Save previous scene
                    if current_scene is not None:
                        if current_scene.page_end == 0:
                            current_scene.page_end = page_num
                        scenes.append(current_scene)

                    scene_id += 1
                    current_scene = SceneBlock(
                        scene_id=scene_id,
                        heading=raw_text,
                        act=0,  # assigned later by act_detector
                        page_start=page_num,
                        page_end=0,
                        characters_present=[],
                    )
                    last_character = None

                elif line_type == LineType.TRANSITION:
                    last_character = None

                elif line_type == LineType.CHARACTER:
                    canonical = normalize_character_name(
                        strip_character_suffixes(raw_text)
                    )
                    last_character = canonical

                    # Check if this line is part of a dual dialogue section
                    for ds_top, ds_bottom in dual_sections:
                        if ds_top <= top <= ds_bottom:
                            warnings.append(
                                f"Possible dual dialogue detected on page "
                                f"{page_num} near line '{raw_text}'"
                            )
                            break

                elif line_type == LineType.PARENTHETICAL:
                    pass  # parentheticals are context, not scored

                elif line_type == LineType.DIALOGUE:
                    if last_character and current_scene is not None:
                        dialogue_line = DialogueLine(
                            character=last_character,
                            text=raw_text,
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
                current_scene.page_end = total_pages
            scenes.append(current_scene)

    # Build character line count map
    characters: dict[str, int] = defaultdict(int)
    for scene in scenes:
        for line in scene.dialogue:
            characters[line.character] += 1

    return ScriptData(
        title=title,
        total_pages=total_pages,
        scenes=scenes,
        characters=dict(characters),
        act_breaks=[],   # populated by act_detector
        source_format='pdf',
        parse_warnings=warnings,
    )