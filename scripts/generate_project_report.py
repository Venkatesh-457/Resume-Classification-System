import os
import sys
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, Preformatted
)
from reportlab.pdfgen import canvas
import pymupdf

# Set local Matplotlib config directory
os.environ['MPLCONFIGDIR'] = os.path.abspath('reports_generated/.mpl_cache')

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total pages and draw
    academic Roman numerals for preliminaries and Arabic numerals for body.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        p = self._pageNumber
        if p == 1:
            return  # Cover page has no number
        
        self.saveState()
        self.setFont('Times-Roman', 12)
        
        # Preliminaries: Roman numerals (ii through ix)
        if 2 <= p <= 9:
            romans = ['', 'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix']
            txt = romans[p] if p < len(romans) else str(p)
        else:
            # Body: Arabic numerals starting at 1 on Doc Page 10
            txt = str(p - 9)
            
        self.drawCentredString(letter[0] / 2.0, 36, txt)
        self.restoreState()


def get_report_styles():
    styles = getSampleStyleSheet()
    
    # -------------------------------------------------------------
    # COVER PAGE STYLES (Page 1)
    # -------------------------------------------------------------
    styles.add(ParagraphStyle(
        'CoverInstitution',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#538135'),
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'CoverDept',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#006400'),
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'CoverCourse',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#006400'),
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#000000'),
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=20,
        leading=25,
        textColor=colors.HexColor('#1f4e79'),
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'CoverSubmittedBy',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#923634'),
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'StudentName',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1f4e79'),
        alignment=0
    ))
    styles.add(ParagraphStyle(
        'StudentRoll',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1f4e79'),
        alignment=2
    ))
    styles.add(ParagraphStyle(
        'CoverGuidanceHeading',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#923634'),
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'CoverGuideName',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#000000'),
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'CoverGuideDesig',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#000000'),
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'CoverFulfillment',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#000000'),
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'CoverUniversity',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1f4e79'),
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'CoverPlace',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#000000'),
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'CoverYear',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#000000'),
        alignment=1
    ))

    # -------------------------------------------------------------
    # CERTIFICATE & DECLARATION STYLES (Pages 2 & 3)
    # -------------------------------------------------------------
    styles.add(ParagraphStyle(
        'CertHeading',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#ee0000'),
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'CertBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#000000'),
        alignment=4
    ))
    styles.add(ParagraphStyle(
        'SigTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#923634')
    ))
    styles.add(ParagraphStyle(
        'SigBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#000000')
    ))
    styles.add(ParagraphStyle(
        'DecMeta',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#000000'),
        alignment=0
    ))
    styles.add(ParagraphStyle(
        'DecBy',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#000000'),
        alignment=2,
        rightIndent=130
    ))

    # -------------------------------------------------------------
    # ACKNOWLEDGEMENT & ABSTRACT STYLES (Pages 4 & 5)
    # -------------------------------------------------------------
    styles.add(ParagraphStyle(
        'AckBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#000000'),
        alignment=4
    ))
    styles.add(ParagraphStyle(
        'AbstractTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#000000'),
        alignment=1
    ))

    # -------------------------------------------------------------
    # CHAPTER & BODY STYLES (Pages 10 to 50)
    # -------------------------------------------------------------
    styles.add(ParagraphStyle(
        'PreliminaryHeading',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.black,
        alignment=1,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        'ChapterHeading',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.black,
        alignment=1,
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=15.5,
        textColor=colors.black,
        spaceBefore=6,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        'SubSectionHeading',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=11,
        leading=14.5,
        textColor=colors.black,
        spaceBefore=5,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10.5,
        leading=14,
        textColor=colors.black,
        alignment=4,  # Justified
        spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        'ReportBullet',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10.5,
        leading=14,
        textColor=colors.black,
        leftIndent=14,
        firstLineIndent=-9,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        'TableHeadCentred',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=9,
        leading=11.5,
        textColor=colors.black,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'TableHeadLeft',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=9,
        leading=11.5,
        textColor=colors.black,
        alignment=0
    ))
    styles.add(ParagraphStyle(
        'TableContentCentred',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11,
        textColor=colors.black,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'TableContentBoldCentred',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.black,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'TableContent',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11,
        textColor=colors.black,
        alignment=0
    ))
    styles.add(ParagraphStyle(
        'TableContentBold',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.black,
        alignment=0
    ))
    styles.add(ParagraphStyle(
        'CaptionStyle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=colors.black,
        alignment=1,
        spaceBefore=3,
        spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7,
        leading=8.8,
        textColor=colors.HexColor('#1e293b')
    ))
    return styles


def assemble_and_build_report():
    output_pdf = 'reports_generated/Resume_Classification_System_Project_Report.pdf'
    os.makedirs('reports_generated', exist_ok=True)
    
    # Standard Letter margins: left 72, right 72, top 72, bottom 72 (1.0 in, printable width = 468 pt)
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        leftMargin=72,
        rightMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = get_report_styles()
    
    from report_sections_prelim import get_preliminary_story
    from report_sections_chapters import (
        get_chapter1_story,
        get_chapter2_story,
        get_chapter3_story,
        get_chapter4_story,
        get_chapter5_story,
        get_chapter6_story,
        get_chapter7_story,
        get_chapter8_story,
        get_references_story,
        get_appendix_story
    )
    
    full_story = []
    
    print("Assembling Preliminary Pages...")
    full_story.extend(get_preliminary_story(styles))
    
    print("Assembling Chapter 1 (Introduction)...")
    full_story.extend(get_chapter1_story(styles))
    
    print("Assembling Chapter 2 (System Analysis & Requirements)...")
    full_story.extend(get_chapter2_story(styles))
    
    print("Assembling Chapter 3 (Dataset & Preprocessing)...")
    full_story.extend(get_chapter3_story(styles))
    
    print("Assembling Chapter 4 (Feature Extraction)...")
    full_story.extend(get_chapter4_story(styles))
    
    print("Assembling Chapter 5 (Classification & ATS Scoring)...")
    full_story.extend(get_chapter5_story(styles))
    
    print("Assembling Chapter 6 (Implementation)...")
    full_story.extend(get_chapter6_story(styles))
    
    print("Assembling Chapter 7 (Result Visualization & Dashboard)...")
    full_story.extend(get_chapter7_story(styles))
    
    print("Assembling Chapter 8 (Conclusion & Future Work)...")
    full_story.extend(get_chapter8_story(styles))
    
    print("Assembling References...")
    full_story.extend(get_references_story(styles))
    
    print("Assembling Appendix (Source Code)...")
    full_story.extend(get_appendix_story(styles))
    
    print(f"Building document to {output_pdf}...")
    doc.build(full_story, canvasmaker=NumberedCanvas)
    print("Build complete! Verifying page structure...")
    
    # Verification with PyMuPDF
    pdf = pymupdf.open(output_pdf)
    total_pages = len(pdf)
    print(f"\n==========================================")
    print(f"TOTAL REPORT PAGES GENERATED: {total_pages}")
    print(f"==========================================")
    
    for i in range(total_pages):
        text = pdf[i].get_text().strip()
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        first_line = lines[0] if lines else 'BLANK'
        footer_line = lines[-1] if lines else 'NONE'
        print(f"Page {i+1:02d}: Top='{first_line[:40]}' | Footer='{footer_line}'")

if __name__ == '__main__':
    assemble_and_build_report()
