import re
from app.models.script_data import SceneBlock, ScriptData

# Explicit act break markers (TV format)
EXPLICIT_ACT_RE = re.compile(
    r'^(ACT\s+(ONE|TWO|THREE|FOUR|FIVE|\d+)|'
    r'END\s+OF\s+(ACT|TEASER|TAG)|'
    r'TEASER|TAG|COLD\s+OPEN)\s*$',
    re.IGNORECASE
)

FADE_OUT_RE = re.compile(
    r'^FADE\s+OUT[\.\:]?\s*$',
    re.IGNORECASE
)


def detect_act_breaks(script_data: ScriptData) -> list[int]:
    """
    Detect page numbers where act breaks occur.

    Strategy 1 (explicit): Search scene headings and transitions for
    explicit act markers (ACT ONE, END OF ACT TWO, etc.)

    Strategy 2 (page heuristic fallback): Use page percentages.
    Act 1 ends at ~25% of total pages.
    Act 2 ends at ~80% of total pages.

    Returns list of two page numbers: [end_of_act1, end_of_act2]
    """
    total_pages = script_data.total_pages
    scenes = script_data.scenes

    if not scenes:
        return _page_heuristic(total_pages)

    # Strategy 1 - scan for explicit markers in scene headings
    explicit_breaks = _detect_explicit_breaks(scenes)
    if len(explicit_breaks) >= 2:
        return explicit_breaks[:2]

    # Strategy 2 - FADE OUT markers as act breaks
    fade_breaks = _detect_fade_breaks(scenes, total_pages)
    if len(fade_breaks) >= 2:
        return fade_breaks[:2]

    # Strategy 3 - page heuristic fallback
    return _page_heuristic(total_pages)


def _detect_explicit_breaks(scenes: list[SceneBlock]) -> list[int]:
    """Find explicit ACT ONE / END OF ACT markers in scene headings."""
    breaks = []
    for scene in scenes:
        if EXPLICIT_ACT_RE.match(scene.heading.strip()):
            breaks.append(scene.page_start)
    return breaks


def _detect_fade_breaks(
    scenes: list[SceneBlock],
    total_pages: int
) -> list[int]:
    """
    Use FADE OUT occurrences as act break indicators.
    Only consider FADE OUTs in the first 85% of the screenplay
    (the last FADE OUT is the ending, not an act break).
    """
    fade_pages = []
    cutoff_page = int(total_pages * 0.85)

    for scene in scenes:
        if (FADE_OUT_RE.match(scene.heading.strip())
                and scene.page_start <= cutoff_page):
            fade_pages.append(scene.page_start)

    return fade_pages


def _page_heuristic(total_pages: int) -> list[int]:
    """
    Fallback: estimate act breaks by page percentage.
    Standard three-act structure:
      Act 1: first 25% of pages
      Act 2: pages 25-80%
      Act 3: final 20%
    """
    end_act1 = int(total_pages * 0.25)
    end_act2 = int(total_pages * 0.80)
    return [end_act1, end_act2]


def assign_acts(script_data: ScriptData) -> ScriptData:
    """
    Assign act numbers to all SceneBlocks in a ScriptData object.
    Modifies script_data in place and returns it.
    """
    act_breaks = detect_act_breaks(script_data)
    script_data.act_breaks = act_breaks

    end_act1, end_act2 = act_breaks[0], act_breaks[1]

    for scene in script_data.scenes:
        if scene.page_start <= end_act1:
            scene.act = 1
        elif scene.page_start <= end_act2:
            scene.act = 2
        else:
            scene.act = 3

        # Propagate act to dialogue lines
        for line in scene.dialogue:
            pass  # act is on the scene, not the line - access via scene_id

    return script_data