import os
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, PageBreak

def get_preliminary_story(styles):
    story = []
    logo_path = 'reports_generated/aditya_logo.png'
    
    # -------------------------------------------------------------
    # PAGE 1: TITLE / COVER PAGE
    # -------------------------------------------------------------
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=337, height=44))
    story.append(Spacer(1, 10))
    story.append(Paragraph("School of Computing", styles['CoverInstitution']))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Department of Computer Science and Engineering", styles['CoverDept']))
    story.append(Spacer(1, 4))
    story.append(Paragraph("NATURAL LANGUAGE PROCESSING", styles['CoverCourse']))
    story.append(Spacer(1, 26))
    story.append(Paragraph("A Cornerstone Project Report on", styles['CoverSubtitle']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("RESUME CLASSIFICATION SYSTEM", styles['CoverTitle']))
    story.append(Spacer(1, 28))
    
    story.append(Paragraph("Submitted by", styles['CoverSubmittedBy']))
    story.append(Spacer(1, 10))
    
    # Students Table: 12pt Bold Navy Blue (#1f4e79), two columns
    students_cover = [
        [Paragraph("<b>N VENKATESH</b>", styles['StudentName']), Paragraph("<b>(24B11CS318)</b>", styles['StudentRoll'])],
        [Paragraph("<b>K L MAHITH</b>", styles['StudentName']), Paragraph("<b>(24B11CS219)</b>", styles['StudentRoll'])],
        [Paragraph("<b>MD RAHAMTHULLA</b>", styles['StudentName']), Paragraph("<b>(24B11CS283)</b>", styles['StudentRoll'])],
        [Paragraph("<b>CH VIGNESH</b>", styles['StudentName']), Paragraph("<b>(24B11CS078)</b>", styles['StudentRoll'])],
    ]
    t_stud = Table(students_cover, colWidths=[180, 130], hAlign='CENTER')
    t_stud.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_stud)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Under the guidance of", styles['CoverGuidanceHeading']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Dr. T. Sudha Rani", styles['CoverGuideName']))
    story.append(Spacer(1, 2))
    story.append(Paragraph("Assistant Professor, Department of CSE", styles['CoverGuideDesig']))
    story.append(Spacer(1, 18))
    
    story.append(Paragraph(
        "in partial fulfilment of the requirements for the award of the B.Tech. degree in Computer Science ",
        styles['CoverFulfillment']
    ))
    story.append(Paragraph("and Engineering", styles['CoverFulfillment']))
    story.append(Spacer(1, 18))
    story.append(Paragraph("ADITYA UNIVERSITY", styles['CoverUniversity']))
    story.append(Spacer(1, 2))
    story.append(Paragraph("Surampalem", styles['CoverPlace']))
    story.append(Spacer(1, 2))
    story.append(Paragraph("Academic Year 2026–2027", styles['CoverYear']))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 2: CERTIFICATE (Page ii)
    # -------------------------------------------------------------
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=337, height=44))
    story.append(Spacer(1, 10))
    story.append(Paragraph("School of Computing", styles['CoverInstitution']))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Department of Computer Science and Engineering", styles['CoverDept']))
    story.append(Spacer(1, 4))
    story.append(Paragraph("NATURAL LANGUAGE PROCESSING", styles['CoverCourse']))
    story.append(Spacer(1, 18))
    story.append(Paragraph("CERTIFICATE", styles['CertHeading']))
    story.append(Spacer(1, 16))
    
    cert_text = (
        "This is to certify that the Cornerstone project work entitled "
        "<b><font color='#ee0000'><i>“RESUME CLASSIFICATION SYSTEM”</i></font></b> "
        "is submitted by"
    )
    story.append(Paragraph(cert_text, styles['CertBody']))
    story.append(Spacer(1, 12))
    
    cert_students = [
        [Paragraph("<b>N VENKATESH</b>", styles['StudentName']), Paragraph("<b>(24B11CS318)</b>", styles['StudentRoll'])],
        [Paragraph("<b>K L MAHITH</b>", styles['StudentName']), Paragraph("<b>(24B11CS219)</b>", styles['StudentRoll'])],
        [Paragraph("<b>MD RAHAMTHULLA</b>", styles['StudentName']), Paragraph("<b>(24B11CS283)</b>", styles['StudentRoll'])],
        [Paragraph("<b>CH VIGNESH</b>", styles['StudentName']), Paragraph("<b>(24B11CS078)</b>", styles['StudentRoll'])],
    ]
    t_cert_stud = Table(cert_students, colWidths=[180, 130], hAlign='CENTER')
    t_cert_stud.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_cert_stud)
    story.append(Spacer(1, 14))
    
    cert_tail = (
        "in partial fulfilment of the requirements for the award of the B.Tech. degree in "
        "Computer Science and Engineering during the academic year 2026-2027."
    )
    story.append(Paragraph(cert_tail, styles['CertBody']))
    story.append(Spacer(1, 75))
    
    # Signature blocks: Maroon headings, Black regular text
    sigs = [
        [Paragraph("<b>Project Guide</b>", styles['SigTitle']), 
         Paragraph("<b>Head of the Department</b>", styles['SigTitle'])],
        [Paragraph("Dr. T. Sudha Rani", styles['SigBody']), 
         Paragraph("Dr. A. Phani Sridhar", styles['SigBody'])],
        [Paragraph("Assistant Professor", styles['SigBody']), 
         Paragraph("Associate Professor and HOD", styles['SigBody'])],
        [Paragraph("Department of CSE", styles['SigBody']), 
         Paragraph("Department of CSE", styles['SigBody'])]
    ]
    t_sigs = Table(sigs, colWidths=[220, 248], hAlign='CENTER')
    t_sigs.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
    ]))
    story.append(t_sigs)
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 3: DECLARATION (Page iii)
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("DECLARATION", styles['PreliminaryHeading']))
    story.append(Spacer(1, 18))
    
    dec_text = (
        "We hereby declare that the project entitled <b>“RESUME CLASSIFICATION SYSTEM”</b> "
        "is our original work and is submitted to <b>ADITYA UNIVERSITY, Surampalem</b>, in "
        "partial fulfilment of the requirements for the award of the <b>B.Tech. degree in Computer "
        "Science and Engineering</b>. We further declare that this project work has not been submitted, "
        "either in full or in part, for the award of any degree or diploma in this or any other institution. "
        "We also confirm that this work has been carried out with academic honesty and complies "
        "with the <b>Institutional Academic Integrity and AI Usage Policy</b>."
    )
    story.append(Paragraph(dec_text, styles['CertBody']))
    story.append(Spacer(1, 26))
    
    story.append(Paragraph("<b>Place:</b> Surampalem", styles['DecMeta']))
    story.append(Paragraph("<b>Date:</b> 29-10-2026", styles['DecMeta']))
    story.append(Spacer(1, 20))
    
    # By block right-aligned / indented
    story.append(Paragraph("<b>By</b>", styles['DecBy']))
    story.append(Spacer(1, 8))
    
    dec_students = [
        [Paragraph("<b>N VENKATESH</b>", styles['StudentName']), Paragraph("<b>(24B11CS318)</b>", styles['StudentRoll'])],
        [Paragraph("<b>K L MAHITH</b>", styles['StudentName']), Paragraph("<b>(24B11CS219)</b>", styles['StudentRoll'])],
        [Paragraph("<b>MD RAHAMTHULLA</b>", styles['StudentName']), Paragraph("<b>(24B11CS283)</b>", styles['StudentRoll'])],
        [Paragraph("<b>CH VIGNESH</b>", styles['StudentName']), Paragraph("<b>(24B11CS078)</b>", styles['StudentRoll'])],
    ]
    t_dec_stud = Table(dec_students, colWidths=[160, 120], hAlign='RIGHT')
    t_dec_stud.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_dec_stud)
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 4: ACKNOWLEDGEMENT (Page iv)
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("ACKNOWLEDGEMENT", styles['PreliminaryHeading']))
    story.append(Spacer(1, 16))
    
    ack_1 = (
        "It is with immense pleasure that we express our sincere gratitude to our Cornerstone Project Guide, "
        "<b>Dr. T. Sudha Rani, Assistant Professor</b>, who has guided us throughout the project. Her valuable "
        "support, encouragement and guidance have greatly contributed to the successful completion of this "
        "work."
    )
    story.append(Paragraph(ack_1, styles['AckBody']))
    story.append(Spacer(1, 12))
    
    ack_2 = (
        "We would like to thank our Deputy Heads of the Department, <b>Dr. Hari J, Professor, Dr. Siva "
        "Satya Prasad P, Assistant Professor and Dr. Chandra Sekhar K, Associate Professor</b>, "
        "Department of CSE, for their support and valuable suggestions."
    )
    story.append(Paragraph(ack_2, styles['AckBody']))
    story.append(Spacer(1, 12))
    
    ack_3 = (
        "Our deepest thanks to our Head of the Department, <b>Dr. A. Phani Sridhar, Associate Professor "
        "and HOD</b>, for his inspiration and for providing all the necessary facilities and resources required "
        "for this project."
    )
    story.append(Paragraph(ack_3, styles['AckBody']))
    story.append(Spacer(1, 12))
    
    ack_4 = (
        "We also extend our sincere thanks to <b>Dr. M.V. Rajesh, Associate Dean, School of Computing</b>, "
        "for his encouragement and support during our project."
    )
    story.append(Paragraph(ack_4, styles['AckBody']))
    story.append(Spacer(1, 12))
    
    ack_5 = (
        "We would like to express our sincere gratitude to <b>Dr. G. Suresh, Registrar; Dr. A. Ramesh, Pro "
        "Vice-Chancellor (Engineering & Sciences); Dr. S. Rama Sree, Pro Vice-Chancellor "
        "(Academics); Dr. M.B. Srinivas, Vice-Chancellor;</b> and <b>Dr. M. Sreenivasa Reddy, Deputy Pro "
        "Chancellor and Management, Aditya University</b>, for providing excellent infrastructure and "
        "state-of-the-art laboratories."
    )
    story.append(Paragraph(ack_5, styles['AckBody']))
    story.append(Spacer(1, 12))
    
    ack_6 = (
        "Finally, we would like to thank the <b>faculty members, lab technicians, non-teaching staff, and "
        "our friends</b> who have directly or indirectly supported us in completing this Cornerstone project "
        "successfully."
    )
    story.append(Paragraph(ack_6, styles['AckBody']))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 5: ABSTRACT (Page v)
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("ABSTRACT", styles['PreliminaryHeading']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("RESUME CLASSIFICATION SYSTEM", styles['AbstractTitle']))
    story.append(Spacer(1, 12))
    
    abs_1 = (
        "The Resume Classification System is a Natural Language Processing (NLP) and Machine Learning application "
        "that parses candidate resumes across multi-format submissions (TXT, DOCX, digital PDF, and scanned PDF) "
        "and categorises them into target professional technical domains. The system accepts resume files as input, "
        "extracts document text using digital extractors and an embedded RapidOCR engine, pre-processes and cleans "
        "the text using NLTK while protecting programming tokens (such as C++, .NET, and CI/CD), and extracts "
        "sublinear TF-IDF word unigrams and bigrams. Multi-model classification benchmarked across five algorithms "
        "selected a Calibrated Linear Support Vector Classifier as champion, achieving 94.51% test accuracy."
    )
    story.append(Paragraph(abs_1, styles['AckBody']))
    story.append(Spacer(1, 10))
    
    abs_2 = (
        "The system is trained and evaluated on an audited dataset of 1,817 real-world resumes spanning 9 job "
        "categories: Business Analyst, Cloud Engineer, Data Analyst, Data Scientist, DevOps Engineer, Machine "
        "Learning Engineer, Software Developer, UI/UX Designer, and Web Developer. Beyond categorization, the "
        "platform computes an explainable 6-component ATS resume quality score totaling 100 points, matches "
        "candidates against target job descriptions using vector cosine similarity, maintains isolated user profiles "
        "in an SQLite database, and presents all analytics on an interactive Streamlit dashboard with downloadable "
        "ReportLab PDF audit reports."
    )
    story.append(Paragraph(abs_2, styles['AckBody']))
    story.append(Spacer(1, 14))
    
    # Requirements in two clean side-by-side columns matching sample report
    req_cols = [
        [
            Paragraph("<b>Software Requirements:</b><br/>"
                      "• Operating System: Windows<br/>"
                      "• Programming Language: Python<br/>"
                      "• IDE: Visual Studio Code<br/>"
                      "• Libraries: Scikit-learn, NLTK, RapidOCR,<br/>"
                      "&nbsp;&nbsp;PyMuPDF, ReportLab, Streamlit", styles['TableContent']),
            Paragraph("<b>Hardware Requirements:</b><br/>"
                      "• Processor: Intel i5<br/>"
                      "• RAM: Minimum 8 GB<br/>"
                      "• Hard Disk: 20 GB free space", styles['TableContent'])
        ]
    ]
    t_req = Table(req_cols, colWidths=[240, 228])
    t_req.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_req)
    story.append(Spacer(1, 16))
    
    story.append(Paragraph("<b>Project Team</b>", styles['TableContentBold']))
    story.append(Spacer(1, 4))
    story.append(Paragraph("N VENKATESH &nbsp;(24B11CS318)", styles['TableContent']))
    story.append(Paragraph("K L MAHITH &nbsp;(24B11CS219)", styles['TableContent']))
    story.append(Paragraph("MD RAHAMTHULLA &nbsp;(24B11CS283)", styles['TableContent']))
    story.append(Paragraph("CH VIGNESH &nbsp;(24B11CS078)", styles['TableContent']))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 6: TABLE OF CONTENTS - PART 1 (Page vi)
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("TABLE OF CONTENTS", styles['PreliminaryHeading']))
    story.append(Spacer(1, 8))
    
    toc_data_1 = [
        [Paragraph("<b>S.No.</b>", styles['TableHeadCentred']), Paragraph("<b>Contents</b>", styles['TableHeadLeft']), Paragraph("<b>Pages</b>", styles['TableHeadCentred'])],
        [Paragraph("1", styles['TableContentCentred']), Paragraph("Title Page", styles['TableContent']), Paragraph("i", styles['TableContentCentred'])],
        [Paragraph("2", styles['TableContentCentred']), Paragraph("Certificate", styles['TableContent']), Paragraph("ii", styles['TableContentCentred'])],
        [Paragraph("3", styles['TableContentCentred']), Paragraph("Declaration", styles['TableContent']), Paragraph("iii", styles['TableContentCentred'])],
        [Paragraph("4", styles['TableContentCentred']), Paragraph("Acknowledgement", styles['TableContent']), Paragraph("iv", styles['TableContentCentred'])],
        [Paragraph("5", styles['TableContentCentred']), Paragraph("Abstract", styles['TableContent']), Paragraph("v", styles['TableContentCentred'])],
        [Paragraph("6", styles['TableContentCentred']), Paragraph("Table of Contents", styles['TableContent']), Paragraph("vi", styles['TableContentCentred'])],
        [Paragraph("7", styles['TableContentCentred']), Paragraph("List of Figures", styles['TableContent']), Paragraph("viii", styles['TableContentCentred'])],
        [Paragraph("8", styles['TableContentCentred']), Paragraph("List of Tables", styles['TableContent']), Paragraph("ix", styles['TableContentCentred'])],
        [Paragraph("<b>Chapter 1</b>", styles['TableContentBoldCentred']), Paragraph("<b>Introduction</b>", styles['TableContentBold']), Paragraph("<b>1</b>", styles['TableContentBoldCentred'])],
        [Paragraph("1.1", styles['TableContentCentred']), Paragraph("Introduction to the Project", styles['TableContent']), Paragraph("1", styles['TableContentCentred'])],
        [Paragraph("1.2", styles['TableContentCentred']), Paragraph("Problem Statement", styles['TableContent']), Paragraph("1", styles['TableContentCentred'])],
        [Paragraph("1.3", styles['TableContentCentred']), Paragraph("Objectives of the Project", styles['TableContent']), Paragraph("2", styles['TableContentCentred'])],
        [Paragraph("1.4", styles['TableContentCentred']), Paragraph("Scope of the Project", styles['TableContent']), Paragraph("2", styles['TableContentCentred'])],
        [Paragraph("<b>Chapter 2</b>", styles['TableContentBoldCentred']), Paragraph("<b>System Analysis and Design, Requirement Analysis</b>", styles['TableContentBold']), Paragraph("<b>3</b>", styles['TableContentBoldCentred'])],
        [Paragraph("2.1", styles['TableContentCentred']), Paragraph("Proposed System", styles['TableContent']), Paragraph("3", styles['TableContentCentred'])],
        [Paragraph("2.2", styles['TableContentCentred']), Paragraph("System Architecture / System Work Flow", styles['TableContent']), Paragraph("3", styles['TableContentCentred'])],
        [Paragraph("2.3", styles['TableContentCentred']), Paragraph("Module Description", styles['TableContent']), Paragraph("4", styles['TableContentCentred'])],
        [Paragraph("2.4", styles['TableContentCentred']), Paragraph("Hardware Requirements and Software Requirements", styles['TableContent']), Paragraph("5", styles['TableContentCentred'])],
        [Paragraph("2.5", styles['TableContentCentred']), Paragraph("Tools and Technologies", styles['TableContent']), Paragraph("6", styles['TableContentCentred'])],
        [Paragraph("<b>Chapter 3</b>", styles['TableContentBoldCentred']), Paragraph("<b>Dataset and Data Preprocessing</b>", styles['TableContentBold']), Paragraph("<b>7</b>", styles['TableContentBoldCentred'])],
        [Paragraph("3.1", styles['TableContentCentred']), Paragraph("Dataset Description and Data Format", styles['TableContent']), Paragraph("7", styles['TableContentCentred'])],
        [Paragraph("3.2", styles['TableContentCentred']), Paragraph("Data Collection and Distribution", styles['TableContent']), Paragraph("8", styles['TableContentCentred'])],
        [Paragraph("3.3", styles['TableContentCentred']), Paragraph("Data Preprocessing (Text Cleaning, Unicode, Tech Tokens, Stopwords, Lemmatization)", styles['TableContent']), Paragraph("9", styles['TableContentCentred'])],
        [Paragraph("<b>Chapter 4</b>", styles['TableContentBoldCentred']), Paragraph("<b>Feature Extraction and Engineering</b>", styles['TableContentBold']), Paragraph("<b>11</b>", styles['TableContentBoldCentred'])],
        [Paragraph("4.1", styles['TableContentCentred']), Paragraph("Need for Feature Extraction", styles['TableContent']), Paragraph("11", styles['TableContentCentred'])],
        [Paragraph("4.2", styles['TableContentCentred']), Paragraph("TF-IDF Vectorization and Mathematical Formulation", styles['TableContent']), Paragraph("11", styles['TableContentCentred'])],
        [Paragraph("4.3", styles['TableContentCentred']), Paragraph("Feature Representation Comparison Matrix", styles['TableContent']), Paragraph("12", styles['TableContentCentred'])],
        [Paragraph("4.4", styles['TableContentCentred']), Paragraph("Taxonomy-Driven Skill Extraction", styles['TableContent']), Paragraph("13", styles['TableContentCentred'])],
    ]
    t_toc1 = Table(toc_data_1, colWidths=[55, 360, 53], hAlign='CENTER')
    t_toc1.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#7f7f7f')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#7f7f7f')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#d9e2f3')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_toc1)
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 7: TABLE OF CONTENTS - PART 2 (Page vii)
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("TABLE OF CONTENTS (Continued)", styles['PreliminaryHeading']))
    story.append(Spacer(1, 8))
    
    toc_data_2 = [
        [Paragraph("<b>S.No.</b>", styles['TableHeadCentred']), Paragraph("<b>Contents</b>", styles['TableHeadLeft']), Paragraph("<b>Pages</b>", styles['TableHeadCentred'])],
        [Paragraph("<b>Chapter 5</b>", styles['TableContentBoldCentred']), Paragraph("<b>Classification and ATS Scoring</b>", styles['TableContentBold']), Paragraph("<b>14</b>", styles['TableContentBoldCentred'])],
        [Paragraph("5.1", styles['TableContentCentred']), Paragraph("Classification Approach & Multi-Model Benchmarking", styles['TableContent']), Paragraph("14", styles['TableContentCentred'])],
        [Paragraph("5.2", styles['TableContentCentred']), Paragraph("Data Partitioning and Stratification", styles['TableContent']), Paragraph("14", styles['TableContentCentred'])],
        [Paragraph("5.3", styles['TableContentCentred']), Paragraph("Calibrated Probability Formulation & Champion Model", styles['TableContent']), Paragraph("15", styles['TableContentCentred'])],
        [Paragraph("5.4", styles['TableContentCentred']), Paragraph("Multi-Class Performance Evaluation", styles['TableContent']), Paragraph("15", styles['TableContentCentred'])],
        [Paragraph("5.5", styles['TableContentCentred']), Paragraph("Explainable ATS Scoring Formulation (6 Components)", styles['TableContent']), Paragraph("16", styles['TableContentCentred'])],
        [Paragraph("5.6", styles['TableContentCentred']), Paragraph("Job Description Cosine Match Formulation", styles['TableContent']), Paragraph("16", styles['TableContentCentred'])],
        [Paragraph("<b>Chapter 6</b>", styles['TableContentBoldCentred']), Paragraph("<b>Implementation</b>", styles['TableContentBold']), Paragraph("<b>17</b>", styles['TableContentBoldCentred'])],
        [Paragraph("6.1", styles['TableContentCentred']), Paragraph("Core Python Libraries and Component Setup", styles['TableContent']), Paragraph("17", styles['TableContentCentred'])],
        [Paragraph("6.2", styles['TableContentCentred']), Paragraph("Document Ingestion and RapidOCR Fallback", styles['TableContent']), Paragraph("18", styles['TableContentCentred'])],
        [Paragraph("6.3", styles['TableContentCentred']), Paragraph("Preprocessing & Token Sanitization Pipeline", styles['TableContent']), Paragraph("19", styles['TableContentCentred'])],
        [Paragraph("6.4", styles['TableContentCentred']), Paragraph("Model Training, Calibration & Artifact Serialization", styles['TableContent']), Paragraph("20", styles['TableContentCentred'])],
        [Paragraph("6.5", styles['TableContentCentred']), Paragraph("ATS Rubric Scoring & Job Match Implementation", styles['TableContent']), Paragraph("21", styles['TableContentCentred'])],
        [Paragraph("6.6", styles['TableContentCentred']), Paragraph("Key Architectural Implementation Snippets", styles['TableContent']), Paragraph("22", styles['TableContentCentred'])],
        [Paragraph("<b>Chapter 7</b>", styles['TableContentBoldCentred']), Paragraph("<b>Result Visualization and Dashboard</b>", styles['TableContentBold']), Paragraph("<b>23</b>", styles['TableContentBoldCentred'])],
        [Paragraph("7.1", styles['TableContentCentred']), Paragraph("Dashboard Architecture & Visual Identity", styles['TableContent']), Paragraph("23", styles['TableContentCentred'])],
        [Paragraph("7.2", styles['TableContentCentred']), Paragraph("Resume Category Distribution Analytics", styles['TableContent']), Paragraph("24", styles['TableContentCentred'])],
        [Paragraph("7.3", styles['TableContentCentred']), Paragraph("Confusion Matrix Analysis & Error Diagnostics", styles['TableContent']), Paragraph("25", styles['TableContentCentred'])],
        [Paragraph("7.4", styles['TableContentCentred']), Paragraph("Multi-Model Evaluation Benchmark Charts", styles['TableContent']), Paragraph("26", styles['TableContentCentred'])],
        [Paragraph("7.5", styles['TableContentCentred']), Paragraph("ATS Scoring Radar & Skill Gap Analysis", styles['TableContent']), Paragraph("27", styles['TableContentCentred'])],
        [Paragraph("7.6", styles['TableContentCentred']), Paragraph("Automated Test Suite Verification & Screenshots", styles['TableContent']), Paragraph("28", styles['TableContentCentred'])],
        [Paragraph("7.7", styles['TableContentCentred']), Paragraph("Results Discussion and Comparative Findings", styles['TableContent']), Paragraph("29", styles['TableContentCentred'])],
        [Paragraph("<b>Chapter 8</b>", styles['TableContentBoldCentred']), Paragraph("<b>Conclusion and Future Enhancements</b>", styles['TableContentBold']), Paragraph("<b>31</b>", styles['TableContentBoldCentred'])],
        [Paragraph("8.1", styles['TableContentCentred']), Paragraph("Conclusion", styles['TableContent']), Paragraph("31", styles['TableContentCentred'])],
        [Paragraph("8.2", styles['TableContentCentred']), Paragraph("Limitations", styles['TableContent']), Paragraph("31", styles['TableContentCentred'])],
        [Paragraph("8.3", styles['TableContentCentred']), Paragraph("Future Enhancements", styles['TableContent']), Paragraph("32", styles['TableContentCentred'])],
        [Paragraph("<b>9</b>", styles['TableContentBoldCentred']), Paragraph("<b>References</b>", styles['TableContentBold']), Paragraph("<b>33</b>", styles['TableContentBoldCentred'])],
        [Paragraph("<b>10</b>", styles['TableContentBoldCentred']), Paragraph("<b>Appendix – Source Code</b>", styles['TableContentBold']), Paragraph("<b>34</b>", styles['TableContentBoldCentred'])],
    ]
    t_toc2 = Table(toc_data_2, colWidths=[55, 360, 53], hAlign='CENTER')
    t_toc2.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#7f7f7f')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#7f7f7f')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#d9e2f3')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_toc2)
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 8: LIST OF FIGURES (Page viii)
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("LIST OF FIGURES", styles['PreliminaryHeading']))
    story.append(Spacer(1, 10))
    
    lof_data = [
        [Paragraph("<b>Figure No.</b>", styles['TableHeadCentred']), Paragraph("<b>Caption</b>", styles['TableHeadLeft']), Paragraph("<b>Page</b>", styles['TableHeadCentred'])],
        [Paragraph("2.1", styles['TableContentCentred']), Paragraph("System Architecture and Workflow of the Resume Classification System", styles['TableContent']), Paragraph("4", styles['TableContentCentred'])],
        [Paragraph("3.1", styles['TableContentCentred']), Paragraph("Dataset Composition Across 9 Professional Job Categories", styles['TableContent']), Paragraph("8", styles['TableContentCentred'])],
        [Paragraph("3.2", styles['TableContentCentred']), Paragraph("Multi-Stage NLP Text Preprocessing and Normalization Pipeline", styles['TableContent']), Paragraph("10", styles['TableContentCentred'])],
        [Paragraph("4.1", styles['TableContentCentred']), Paragraph("Feature Extraction Representation vs Macro F1 and Matrix Sparsity", styles['TableContent']), Paragraph("13", styles['TableContentCentred'])],
        [Paragraph("5.1", styles['TableContentCentred']), Paragraph("Multi-Model Evaluation Benchmark on Held-Out Test Resumes", styles['TableContent']), Paragraph("15", styles['TableContentCentred'])],
        [Paragraph("5.2", styles['TableContentCentred']), Paragraph("Confusion Matrix Heatmap for Champion Calibrated LinearSVC", styles['TableContent']), Paragraph("16", styles['TableContentCentred'])],
        [Paragraph("7.1", styles['TableContentCentred']), Paragraph("Explainable ATS Score Multi-Dimensional Radar Breakdown", styles['TableContent']), Paragraph("24", styles['TableContentCentred'])],
        [Paragraph("7.2", styles['TableContentCentred']), Paragraph("Streamlit Resume Intelligence Platform User Interface and Analysis View", styles['TableContent']), Paragraph("26", styles['TableContentCentred'])],
        [Paragraph("7.3", styles['TableContentCentred']), Paragraph("Job Description Match Analysis and Identified Skill Gap Visualizer", styles['TableContent']), Paragraph("27", styles['TableContentCentred'])],
        [Paragraph("7.4", styles['TableContentCentred']), Paragraph("Automated Test Suite Execution Output (23 Unit Tests Passed)", styles['TableContent']), Paragraph("28", styles['TableContentCentred'])],
    ]
    t_lof = Table(lof_data, colWidths=[65, 350, 53], hAlign='CENTER')
    t_lof.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#7f7f7f')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#7f7f7f')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#d9e2f3')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_lof)
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 9: LIST OF TABLES (Page ix)
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("LIST OF TABLES", styles['PreliminaryHeading']))
    story.append(Spacer(1, 10))
    
    lot_data = [
        [Paragraph("<b>Table No.</b>", styles['TableHeadCentred']), Paragraph("<b>Caption</b>", styles['TableHeadLeft']), Paragraph("<b>Page</b>", styles['TableHeadCentred'])],
        [Paragraph("2.1", styles['TableContentCentred']), Paragraph("Modules of the Proposed System", styles['TableContent']), Paragraph("4", styles['TableContentCentred'])],
        [Paragraph("2.2", styles['TableContentCentred']), Paragraph("Hardware Requirements", styles['TableContent']), Paragraph("5", styles['TableContentCentred'])],
        [Paragraph("2.3", styles['TableContentCentred']), Paragraph("Software Requirements", styles['TableContent']), Paragraph("6", styles['TableContentCentred'])],
        [Paragraph("2.4", styles['TableContentCentred']), Paragraph("Tools and Technologies Used", styles['TableContent']), Paragraph("6", styles['TableContentCentred'])],
        [Paragraph("3.1", styles['TableContentCentred']), Paragraph("Attributes of the Resume Classification Dataset", styles['TableContent']), Paragraph("7", styles['TableContentCentred'])],
        [Paragraph("3.2", styles['TableContentCentred']), Paragraph("Summary Statistics of the Dataset (N=1,817)", styles['TableContent']), Paragraph("8", styles['TableContentCentred'])],
        [Paragraph("3.3", styles['TableContentCentred']), Paragraph("Examples of Text Preprocessing (Before and After)", styles['TableContent']), Paragraph("10", styles['TableContentCentred'])],
        [Paragraph("4.1", styles['TableContentCentred']), Paragraph("Feature Representation Comparison Matrix", styles['TableContent']), Paragraph("12", styles['TableContentCentred'])],
        [Paragraph("4.2", styles['TableContentCentred']), Paragraph("Skill Taxonomy Categorization and Detection Scope", styles['TableContent']), Paragraph("13", styles['TableContentCentred'])],
        [Paragraph("5.1", styles['TableContentCentred']), Paragraph("Multi-Model Benchmark Results on Held-Out Test Set (N=364)", styles['TableContent']), Paragraph("14", styles['TableContentCentred'])],
        [Paragraph("5.2", styles['TableContentCentred']), Paragraph("Per-Class Evaluation Metrics of Champion Calibrated LinearSVC", styles['TableContent']), Paragraph("15", styles['TableContentCentred'])],
        [Paragraph("5.3", styles['TableContentCentred']), Paragraph("Explainable ATS Rubric Weightage and Scoring Rules", styles['TableContent']), Paragraph("16", styles['TableContentCentred'])],
        [Paragraph("6.1", styles['TableContentCentred']), Paragraph("Core Python Libraries and Component Responsibilities", styles['TableContent']), Paragraph("17", styles['TableContentCentred'])],
        [Paragraph("6.2", styles['TableContentCentred']), Paragraph("Key Functions and Pipeline Methods", styles['TableContent']), Paragraph("20", styles['TableContentCentred'])],
        [Paragraph("7.1", styles['TableContentCentred']), Paragraph("Classification Accuracy and F1 Breakdown Across Models", styles['TableContent']), Paragraph("25", styles['TableContentCentred'])],
        [Paragraph("7.2", styles['TableContentCentred']), Paragraph("Real-World Test Resumes and Model Predictions", styles['TableContent']), Paragraph("28", styles['TableContentCentred'])],
    ]
    t_lot = Table(lot_data, colWidths=[65, 350, 53], hAlign='CENTER')
    t_lot.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#7f7f7f')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#7f7f7f')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#d9e2f3')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_lot)
    story.append(PageBreak())

    return story
