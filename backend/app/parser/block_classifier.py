import re
from app.models.script_data import LineType

# ── X-coordinate thresholds (derived from pulp_fiction.pdf inspection) ────────
# These are the measured x0 positions from pdfplumber word extraction.
# Tolerance of ±15pt applied to each threshold to handle minor PDF variations.

X_LEFT_MARGIN    = 99.2   # scene headings and action lines
X_DIALOGUE       = 170.2  # dialogue text
X_PARENTHETICAL  = 226.8  # parenthetical lines
X_CHARACTER      = 241.0  # character cues
X_TRANSITION     = 400.0  # transitions (CUT TO:, FADE OUT) - right-aligned

TOLERANCE        = 15.0   # ±pt allowed around each threshold

# ── Regex patterns ────────────────────────────────────────────────────────────
SCENE_HEADING_RE = re.compile(
    r'^(INT\.|EXT\.|INT\/EXT\.|I\/E\.)',
    re.IGNORECASE
)

TRANSITION_RE = re.compile(
    r'^(FADE\s+OUT|FADE\s+IN|FADE\s+TO|CUT\s+TO|SMASH\s+CUT|MATCH\s+CUT|'
    r'DISSOLVE\s+TO|IRIS\s+OUT|WIPE\s+TO)[\.:]*\s*$',
    re.IGNORECASE
)

PARENTHETICAL_RE = re.compile(r'^\(.*\)\s*$')

CONT_D_RE = re.compile(
    r'\s*\(CONT\'?D\)\s*$|\s*\(CONTINUED\)\s*$',
    re.IGNORECASE
)

VOICE_OVER_RE = re.compile(
    r'\s*\((V\.O\.?|O\.S\.?|O\.C\.?|OVER)\)\s*$',
    re.IGNORECASE
)

TV_ACT_RE = re.compile(
    r'^(TEASER|TAG|ACT\s+(ONE|TWO|THREE|FOUR|FIVE|\d+)|'
    r'END\s+OF\s+(TEASER|TAG|ACT)|COLD\s+OPEN|MAIN\s+TITLES?)\s*$',
    re.IGNORECASE
)


def strip_character_suffixes(name: str) -> str:
    """Remove CONT'D, V.O., O.S. suffixes from character names."""
    name = CONT_D_RE.sub('', name)
    name = VOICE_OVER_RE.sub('', name)
    return name.strip()


def is_within(x0: float, target: float, tolerance: float = TOLERANCE) -> bool:
    """Check if x0 is within tolerance of a target threshold."""
    return abs(x0 - target) <= tolerance


def classify_line(text: str, x0: float) -> LineType:
    """
    Classify a single line of screenplay text by its content and x-position.

    Priority order:
    1. Empty line
    2. Transition  (right-aligned OR matches transition regex)
    3. Scene heading  (left margin + INT./EXT. pattern)
    4. TV act break  (centered, matches act break pattern)
    5. Parenthetical  (parenthetical x-range + wrapped in parens)
    6. Character cue  (character x-range + all-caps + short)
    7. Dialogue  (dialogue x-range)
    8. Action  (fallback for left-margin lines)
    """
    stripped = text.strip()

    # 1. Empty
    if not stripped:
        return LineType.EMPTY

    # 2. Transition - right-aligned OR matches pattern at any position
    if x0 >= X_TRANSITION or TRANSITION_RE.match(stripped):
        return LineType.TRANSITION

    # 3. Scene heading - left margin + INT./EXT. pattern
    if is_within(x0, X_LEFT_MARGIN, 30) and SCENE_HEADING_RE.match(stripped):
        return LineType.SCENE_HEADING

    # 4. TV act break - centered area + matches act pattern
    if TV_ACT_RE.match(stripped):
        return LineType.TRANSITION  # treat as structural transition

    # 5. Parenthetical - correct x-range + wrapped in parens
    if is_within(x0, X_PARENTHETICAL, 20) and PARENTHETICAL_RE.match(stripped):
        return LineType.PARENTHETICAL

    # 6. Character cue - correct x-range + all-caps + short
    if is_within(x0, X_CHARACTER, 20):
        clean = strip_character_suffixes(stripped)
        if clean.isupper() and len(clean) <= 35 and len(clean) > 0:
            return LineType.CHARACTER

    # 7. Dialogue - correct x-range
    if is_within(x0, X_DIALOGUE, 20):
        return LineType.DIALOGUE

    # 8. Action - fallback (left margin, not a scene heading)
    if is_within(x0, X_LEFT_MARGIN, 30):
        return LineType.ACTION

    # 9. Absolute fallback - if nothing matches, treat as action
    return LineType.ACTION