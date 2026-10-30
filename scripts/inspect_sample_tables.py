import pymupdf

sample = pymupdf.open(r'C:\Users\nimma\.gemini\antigravity\brain\2e4208b9-0c41-48ad-ad24-a5f2ab505bb7\.user_uploaded\media_1793281440595_019d5ab9.pdf')

# Let's inspect page 14 (Table 2.1 in sample) and page 16 (Table 3.1)
for p in [13, 14, 15]: # pages 14, 15, 16
    print(f"\n==========================================")
    print(f"SAMPLE PDF PAGE {p+1}")
    print(f"==========================================")
    page = sample[p]
    # Check drawings (table lines/rectangles)
    drawings = page.get_drawings()
    print(f"Total drawings (lines/rects): {len(drawings)}")
    for d in drawings[:10]:
        print(f"  type={d.get('type')}, rect={d.get('rect')}, stroke={d.get('color')}, fill={d.get('fill')}, width={d.get('width')}")
    # Print text blocks
    for b in page.get_text('blocks'):
        txt = b[4].strip().replace('\n', ' | ')
        if 'Table' in txt or 'S.No' in txt or 'Module' in txt:
            print(f"  bbox=({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}) -> {txt[:90]}")
