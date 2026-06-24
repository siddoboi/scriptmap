import pdfplumber
from app.parser.normalizer import repair_encoding
from app.parser.block_classifier import classify_line
from app.parser.pdf_parser import _group_words_into_lines

with pdfplumber.open("tests/fixtures/parasite.pdf") as pdf:
    page = pdf.pages[2]  # page 3, 0-indexed
    words = page.extract_words()
    lines = _group_words_into_lines(words)

    print("=== PAGE 3 LINES WITH CLASSIFICATION ===")
    for line in lines[:30]:
        text = repair_encoding(line['text']).strip()
        x0 = line['x0']
        line_type = classify_line(text, x0)
        print(f"  x0={x0:6.1f}  type={line_type.value:15s}  text={text[:50]}")