import pdfplumber


class ScannedPDFError(Exception):
    """Raised when a PDF has no extractable text layer."""
    pass


def detect_text_layer(path: str) -> None:
    """
    Check if a PDF has an extractable text layer.
    Raises ScannedPDFError if the PDF appears to be a scanned image.

    Strategy: extract text from the first 3 pages and count total characters.
    If total is under the threshold, the PDF is image-only.
    """
    MIN_CHARS = 100
    pages_to_check = 3

    total_chars = 0

    with pdfplumber.open(path) as pdf:
        pages = pdf.pages[:pages_to_check]
        for page in pages:
            text = page.extract_text()
            if text:
                total_chars += len(text.strip())

    if total_chars < MIN_CHARS:
        raise ScannedPDFError(
            f"PDF appears to be a scanned image - only {total_chars} "
            f"characters extracted from first {pages_to_check} pages. "
            f"Please use a text-based PDF or FDX file."
        )