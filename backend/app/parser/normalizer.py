import re


# ── Ligature and encoding repair ──────────────────────────────────────────────
# PDFs from Final Draft and other screenwriting software commonly produce
# these ligature failures when text is extracted.

LIGATURE_MAP = {
    '\ufb01': 'fi',   # ﬁ
    '\ufb02': 'fl',   # ﬂ
    '\ufb00': 'ff',   # ﬀ
    '\ufb03': 'ffi',  # ﬃ
    '\ufb04': 'ffl',  # ﬄ
    '\u2013': '-',    # en dash
    '\u2014': '-',    # em dash
    '\u2018': "'",    # left single quote
    '\u2019': "'",    # right single quote
    '\u201c': '"',    # left double quote
    '\u201d': '"',    # right double quote
    '\u2026': '...',  # ellipsis
    '\u00a0': ' ',    # non-breaking space
}

# ── Header/footer patterns ────────────────────────────────────────────────────
# Lines that appear repeatedly at the same y-position across pages.
# These are page numbers, watermarks, and continuation markers.

FOOTER_PATTERNS = [
    re.compile(r'^\d+\.\s*$'),                    # page numbers: "42."
    re.compile(r'^\d+\s*$'),                       # bare page numbers: "42"
    re.compile(r'^\s*CONTINUED:\s*$', re.I),       # "CONTINUED:"
    re.compile(r'^\s*\(CONTINUED\)\s*$', re.I),    # "(CONTINUED)"
    re.compile(r'^\s*\(MORE\)\s*$', re.I),         # "(MORE)"
    re.compile(r'^\s*OVER:\s*$', re.I),            # "OVER:"
]


def repair_encoding(text: str) -> str:
    """Replace common ligature failures and smart quotes with ASCII equivalents."""
    for char, replacement in LIGATURE_MAP.items():
        text = text.replace(char, replacement)
    return text


def normalize_whitespace(text: str) -> str:
    """Collapse multiple spaces to single space. Preserve newlines."""
    lines = text.split('\n')
    lines = [re.sub(r' {2,}', ' ', line) for line in lines]
    return '\n'.join(lines)


def is_header_footer(line: str) -> bool:
    """Return True if a line matches known header/footer patterns."""
    stripped = line.strip()
    for pattern in FOOTER_PATTERNS:
        if pattern.match(stripped):
            return True
    return False


def normalize_text(text: str) -> str:
    """
    Full normalization pipeline for raw PDF extracted text.
    1. Repair ligatures and encoding
    2. Normalize whitespace
    3. Strip header/footer lines
    """
    text = repair_encoding(text)
    text = normalize_whitespace(text)

    lines = text.split('\n')
    cleaned = [line for line in lines if not is_header_footer(line)]

    return '\n'.join(cleaned)


def normalize_character_name(name: str) -> str:
    """
    Normalize a character name to its canonical form.
    - Uppercase
    - Strip leading/trailing whitespace
    - Collapse internal whitespace
    """
    name = name.strip().upper()
    name = re.sub(r'\s+', ' ', name)
    return name

def detect_repeating_headers(pages_text: list[str], threshold: float = 0.8) -> set[str]:
    """
    Detect text that appears on more than `threshold` fraction of pages.
    These are likely headers, footers, watermarks, or page numbers.

    Only considers lines that are unlikely to be character names or dialogue:
    - Under 8 characters (page numbers, short markers)
    - Or match known footer patterns explicitly

    Args:
        pages_text: list of raw text strings, one per page
        threshold: fraction of pages a line must appear on

    Returns:
        set of strings to strip from all pages
    """
    from collections import Counter

    total_pages = len(pages_text)
    if total_pages == 0:
        return set()

    min_appearances = max(2, int(total_pages * threshold))

    line_page_count: Counter = Counter()

    for page_text in pages_text:
        page_lines = set(
            line.strip()
            for line in page_text.split('\n')
            if line.strip() and len(line.strip()) < 8  # only very short strings
        )
        for line in page_lines:
            line_page_count[line] += 1

    repeating = {
        line for line, count in line_page_count.items()
        if count >= min_appearances
    }

    return repeating

def strip_repeating_headers(page_text: str, headers: set[str]) -> str:
    """Remove detected header/footer lines from a page's text."""
    lines = page_text.split('\n')
    cleaned = [
        line for line in lines
        if line.strip() not in headers
    ]
    return '\n'.join(cleaned)