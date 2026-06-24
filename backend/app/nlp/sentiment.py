from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize analyzer once at module level - avoid re-instantiating per call
_analyzer = SentimentIntensityAnalyzer()


def score_line(text: str) -> float:
    """
    Score a single dialogue line using VADER.
    Returns compound score in range -1.0 to +1.0.
    """
    scores = _analyzer.polarity_scores(text)
    return scores['compound']


def score_script(script_data) -> dict[str, list[dict]]:
    """
    Score all dialogue lines in a ScriptData object and build sentiment arcs.

    For each character, produces a list of SentimentPoint dicts:
        {page: int, score: float, raw: float}

    Where:
        raw   = VADER compound score for that single line
        score = rolling average over a window of recent lines (smoothed arc)

    Args:
        script_data: ScriptData object (already parsed)

    Returns:
        dict mapping character name -> list of sentiment points
    """
    from collections import defaultdict

    # Collect all dialogue lines per character, sorted by page
    char_lines: dict[str, list[dict]] = defaultdict(list)

    for scene in script_data.scenes:
        for line in scene.dialogue:
            raw_score = score_line(line.text)
            char_lines[line.character].append({
                'page': line.page,
                'raw':  raw_score,
            })

    # Store scores on the DialogueLine objects too
    line_index = 0
    for scene in script_data.scenes:
        for line in scene.dialogue:
            line.sentiment = score_line(line.text)

    # Build smoothed arcs per character
    arcs: dict[str, list[dict]] = {}

    for character, lines in char_lines.items():
        # Sort by page
        lines.sort(key=lambda l: l['page'])

        # Rolling average with window=5
        smoothed = _rolling_average(
            [l['raw'] for l in lines],
            window=5
        )

        arc = []
        for i, line in enumerate(lines):
            arc.append({
                'page':  line['page'],
                'score': round(smoothed[i], 4),
                'raw':   round(line['raw'], 4),
            })

        arcs[character] = arc

    return arcs


def _rolling_average(values: list[float], window: int = 5) -> list[float]:
    """
    Compute rolling average over a list of floats.
    For positions with fewer than `window` preceding values,
    uses all available values (expanding window).
    """
    result = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        chunk = values[start:i + 1]
        result.append(sum(chunk) / len(chunk))
    return result