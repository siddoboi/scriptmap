import pdfplumber

with pdfplumber.open("tests/fixtures/parasite.pdf") as pdf:
    print(f"Total pages: {len(pdf.pages)}")

    for page_num in [3, 4, 5]:
        page = pdf.pages[page_num - 1]
        print(f"\n=== PAGE {page_num} - first 40 words ===")
        for word in page.extract_words()[:40]:
            print(f"  x0={word['x0']:.1f}  top={word['top']:.1f}  text={word['text']}")
        print(f"\n=== PAGE {page_num} - raw text ===")
        print(page.extract_text())
        print("\n" + "="*60)