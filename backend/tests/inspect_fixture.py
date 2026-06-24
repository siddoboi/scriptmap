import pdfplumber
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "tests/fixtures/pulp_fiction.pdf"

with pdfplumber.open("tests/fixtures/pulp_fiction.pdf") as pdf:
    for page_num, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text and ("CUT TO" in text or "FADE" in text or "SMASH" in text):
            print(f"\n=== PAGE {page_num + 1} ===")
            for word in page.extract_words():
                if any(t in word['text'] for t in ["CUT", "FADE", "SMASH", "TO:"]):
                    print(f"  x0={word['x0']:.1f}  top={word['top']:.1f}  text={word['text']}")
                    
with pdfplumber.open(path) as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")

    for page_num in [3, 4, 5]:
        page = pdf.pages[page_num]
        print(f"=== PAGE {page_num + 1} - WORDS WITH COORDINATES (first 40) ===")
        for word in page.extract_words()[:40]:
            print(f"  x0={word['x0']:.1f}  top={word['top']:.1f}  text={word['text']}")
        print(f"\n=== PAGE {page_num + 1} - RAW TEXT ===")
        print(page.extract_text())
        print("\n" + "="*60 + "\n")