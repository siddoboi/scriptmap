import pdfplumber

with pdfplumber.open("tests/fixtures/parasite.pdf") as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    
    for page_num, page in enumerate(pdf.pages[:10]):
        words = page.extract_words()
        
        # Group words by top position (within 5pt)
        from collections import defaultdict
        rows = defaultdict(list)
        for w in words:
            row_key = round(w['top'] / 5) * 5
            rows[row_key].append(w)
        
        # Find rows with character-position words at very different x0 values
        for row_key, row_words in rows.items():
            char_words = [w for w in row_words if w['text'].isupper() and len(w['text']) > 1]
            if len(char_words) >= 2:
                x_positions = [w['x0'] for w in char_words]
                if max(x_positions) - min(x_positions) > 100:
                    print(f"\nPage {page_num+1} - possible dual dialogue at top~{row_key}:")
                    for w in char_words:
                        print(f"  x0={w['x0']:.1f}  top={w['top']:.1f}  text={w['text']}")