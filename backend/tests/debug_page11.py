import pdfplumber
from app.parser.dual_dialogue import detect_dual_dialogue_sections

for page_num in [11, 43, 54, 72]:
    with pdfplumber.open("tests/fixtures/pulp_fiction.pdf") as pdf:
        page = pdf.pages[page_num - 1]
        words = page.extract_words()

        sections = detect_dual_dialogue_sections(words)
        print(f"\n=== PAGE {page_num} - sections: {sections} ===")

        candidates = [
            w for w in words
            if 180 <= w["x0"] <= 380
            and w["text"].isupper()
            and len(w["text"]) > 1
        ]
        for w in candidates:
            print(f"  x0={w['x0']:.1f}  top={w['top']:.1f}  text={w['text']}")