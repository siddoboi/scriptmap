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
    """
    from collections import defaultdict

    char_lines: dict[str, list[dict]] = defaultdict(list)

    for scene in script_data.scenes:
        for line in scene.dialogue:
            raw_score = score_line(line.text)
            char_lines[line.character].append({
                'page': line.page,
                'raw':  raw_score,
            })

    # Store scores on DialogueLine objects
    for scene in script_data.scenes:
        for line in scene.dialogue:
            line.sentiment = score_line(line.text)

    # Build smoothed arcs per character
    arcs: dict[str, list[dict]] = {}

    for character, lines in char_lines.items():
        lines.sort(key=lambda item: item['page'])

        smoothed = _rolling_average(
            [item['raw'] for item in lines],
            window=5
        )

        arc = []
        for i, entry in enumerate(lines):
            arc.append({
                'page':  entry['page'],
                'score': round(smoothed[i], 4),
                'raw':   round(entry['raw'], 4),
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