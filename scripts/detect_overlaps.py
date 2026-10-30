import pymupdf

doc = pymupdf.open('reports_generated/Resume_Classification_System_Project_Report.pdf')

for pno in range(len(doc)):
    page = doc[pno]
    rects = []
    blocks = page.get_text('dict')['blocks']
    lines_info = []
    for b in blocks:
        if 'lines' in b:
            for l in b['lines']:
                bbox = l['bbox']
                txt = ''.join([s['text'] for s in l['spans']]).strip()
                if txt:
                    lines_info.append((bbox, txt))
    
    # Check vertical overlap among lines that share horizontal span
    for i in range(len(lines_info)):
        b1, t1 = lines_info[i]
        for j in range(i + 1, len(lines_info)):
            b2, t2 = lines_info[j]
            # check if x ranges overlap
            x_overlap = max(0, min(b1[2], b2[2]) - max(b1[0], b2[0]))
            if x_overlap > 30: # significant horizontal overlap
                # check vertical overlap: if b1 and b2 intersect vertically
                y_overlap = max(0, min(b1[3], b2[3]) - max(b1[1], b2[1]))
                # If vertical overlap is more than 3 pt, they are overlapping!
                if y_overlap > 3.0:
                    print(f"OVERLAP on Page {pno+1}:")
                    print(f"  Line 1 ({b1[1]:.1f} - {b1[3]:.1f}): '{t1[:50]}'")
                    print(f"  Line 2 ({b2[1]:.1f} - {b2[3]:.1f}): '{t2[:50]}'")
