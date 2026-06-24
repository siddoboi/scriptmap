from dataclasses import dataclass

# Minimum horizontal separation between two character cues
# to be considered dual dialogue columns (in points)
DUAL_DIALOGUE_MIN_X_GAP = 100.0

# Tolerance for grouping words on the same line (in points)
LINE_TOP_TOLERANCE = 5.0


@dataclass
class WordToken:
    """Minimal representation of a pdfplumber word."""
    text: str
    x0: float
    top: float


def group_by_line(words: list[dict]) -> dict[float, list[dict]]:
    """
    Group pdfplumber word dicts by their vertical position (top).
    Words within LINE_TOP_TOLERANCE of each other are on the same line.
    Returns dict keyed by representative top value.
    """
    lines: dict[float, list[dict]] = {}

    for word in words:
        top = word['top']
        matched = False
        for key in lines:
            if abs(key - top) <= LINE_TOP_TOLERANCE:
                lines[key].append(word)
                matched = True
                break
        if not matched:
            lines[top] = [word]

    return lines


def detect_dual_dialogue_sections(words: list[dict]) -> list[tuple[float, float]]:
    """
    Detect vertical ranges on a page that contain dual dialogue.

    A dual dialogue section is identified when two character cues appear
    on the same line (same top value) with x0 positions separated by
    at least DUAL_DIALOGUE_MIN_X_GAP points.

    Returns list of (top_start, top_end) tuples for each dual dialogue section.
    """
    lines = group_by_line(words)
    dual_sections = []

    sorted_tops = sorted(lines.keys())

    for top in sorted_tops:
        line_words = lines[top]

        # Find words that look like character cues on this line
        char_candidates = [
            w for w in line_words
            if w['text'].isupper()
            and len(w['text']) > 1
            and len(w['text']) <= 35
        ]

        if len(char_candidates) < 2:
            continue

        # Check if any two candidates are separated by enough horizontal space
        x_positions = sorted(set(round(w['x0']) for w in char_candidates))

        for i in range(len(x_positions)):
            for j in range(i + 1, len(x_positions)):
                if x_positions[j] - x_positions[i] >= DUAL_DIALOGUE_MIN_X_GAP:
                    # Found a dual dialogue header line
                    # The section runs from this top to the next character cue
                    # or scene heading (approximate: next 150 points)
                    dual_sections.append((top, top + 150.0))
                    break

    return dual_sections


def split_dual_dialogue_columns(
    words: list[dict],
    section_top: float,
    section_bottom: float,
    split_x: float,
) -> tuple[list[dict], list[dict]]:
    """
    Split words in a dual dialogue section into left and right columns.

    Args:
        words: all words on the page
        section_top: top of the dual dialogue section
        section_bottom: bottom of the dual dialogue section
        split_x: x-coordinate midpoint between the two columns

    Returns:
        (left_column_words, right_column_words)
    """
    section_words = [
        w for w in words
        if section_top <= w['top'] <= section_bottom
    ]

    left  = [w for w in section_words if w['x0'] < split_x]
    right = [w for w in section_words if w['x0'] >= split_x]

    return left, right