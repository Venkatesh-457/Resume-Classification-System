import pymupdf

sample = pymupdf.open(r'C:\Users\nimma\.gemini\antigravity\brain\2e4208b9-0c41-48ad-ad24-a5f2ab505bb7\.user_uploaded\media_1793281440595_019d5ab9.pdf')

for p in range(3):
    print(f"\n==========================================")
    print(f"SAMPLE PDF PAGE {p+1}")
    print(f"==========================================")
    page = sample[p]
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        if "lines" in b:
            for line in b["lines"]:
                line_text = ""
                span_info = []
                for s in line["spans"]:
                    t = s["text"]
                    c = hex(s["color"])
                    sz = round(s["size"], 1)
                    fn = s["font"]
                    flags = s["flags"]
                    span_info.append(f"[{t!r} sz={sz} col={c} fn={fn}]")
                    line_text += t
                bbox = [round(x, 1) for x in line["bbox"]]
                print(f"bbox={bbox} -> {' '.join(span_info)}")
        elif "image" in b:
            print(f"IMAGE BLOCK: bbox={[round(x, 1) for x in b['bbox']]}")
