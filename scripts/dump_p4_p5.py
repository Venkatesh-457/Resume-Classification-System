import pymupdf

sample = pymupdf.open(r'C:\Users\nimma\.gemini\antigravity\brain\2e4208b9-0c41-48ad-ad24-a5f2ab505bb7\.user_uploaded\media_1793281440595_019d5ab9.pdf')

for p in [3, 4]:
    print(f"\n=== SAMPLE PAGE {p+1} ===")
    for b in sample[p].get_text("dict")["blocks"]:
        if "lines" in b:
            for l in b["lines"]:
                info = [f"[{s['text']!r} {round(s['size'],1)}pt {hex(s['color'])} {s['font']}]" for s in l["spans"]]
                print(f"{l['bbox'][1]:.1f}: {' '.join(info)}")
