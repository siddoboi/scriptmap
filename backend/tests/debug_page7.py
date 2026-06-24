import pdfplumber
from app.parser.dual_dialogue import detect_dual_dialogue_sections

with pdfplumber.open("tests/fixtures/pulp_fiction.pdf") as pdf:
    page = pdf.pages[6]  # page 7, 0-indexed
    words = page.extract_words()

    sections = detect_dual_dialogue_sections(words)
    print(f"Dual sections detected: {sections}")
    print()

    # Show all words in character x-range on this page
    print("All words in character x-range (130-400), all-caps:")
    candidates = [
        w for w in words
        if 130 <= w["x0"] <= 400
        and w["text"].isupper()
        and len(w["text"]) > 1
    ]
    for w in candidates:
        print(f"  x0={w['x0']:.1f}  top={w['top']:.1f}  text={w['text']}")