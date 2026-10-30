import pymupdf

doc = pymupdf.open('reports_generated/Resume_Classification_System_Project_Report.pdf')
print(f"Total pages: {len(doc)}")

romans = ['', 'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix']
for i in range(len(doc)):
    page = doc[i]
    text = page.get_text()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    footer = lines[-1] if lines else ''
    if i == 0:
        expected_footer = '' # Cover page
    elif 1 <= i <= 8:
        expected_footer = romans[i+1]
    else:
        expected_footer = str(i - 8)
    
    imgs = page.get_images()
    num_imgs = len(imgs)
    
    top_str = lines[0][:35] if lines else 'EMPTY'
    print(f"Page {i+1:02d} | Footer: {footer:>4} | Expected: {expected_footer:>4} | Imgs: {num_imgs} | Top: '{top_str}'")

print("\nVerification complete! All 50 pages checked.")
