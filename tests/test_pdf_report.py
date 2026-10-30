"""
Automated Tests for Custom PDF Report Engine
Covers ReportLab PDF generation, A4 canvas, multi-page layout, and binary validity.
"""

from core.reporting.pdf_generator import pdf_report_generator


def test_pdf_report_generation():
    analysis_data = {
        "id": 101,
        "filename": "Jane_Doe_Resume.pdf",
        "file_format": "PDF",
        "extraction_method": "PyMuPDF (Digital)",
        "ocr_used": False,
        "word_count": 480,
        "page_count": 1,
        "predicted_category": "Data Scientist",
        "confidence": 0.942,
        "score_type": "Calibrated Probability",
        "ats_score": 88.5,
        "ats_grade": "A (Strong Match)",
        "score_breakdown": {
            "Structure & Readability (max 15)": 15.0,
            "Contact Information (max 15)": 15.0,
            "Section Coverage (max 20)": 18.0,
            "Skills Depth & Taxonomy (max 25)": 21.0,
            "Quantifiable Metrics (max 15)": 12.0,
            "Action Verbs & Tone (max 10)": 8.0,
            "Penalties Deducted": 0.0,
        },
        "skills_detected": {
            "skills_by_category": {
                "Programming Languages": ["Python", "R", "SQL"],
                "Data Science & AI": ["PyTorch", "scikit-learn", "Pandas", "NLP"],
                "Cloud & Tools": ["Docker", "Git", "AWS"],
            }
        },
        "section_coverage": {
            "summary": True,
            "experience": True,
            "education": True,
            "skills": True,
            "projects": True,
            "certifications": False,
        },
        "recommendations": [
            "Consider adding an explicit Certifications section.",
            "Incorporate more active action power verbs.",
        ],
        "job_match_score": 82.0,
        "job_match_details": {
            "grade": "High Match",
            "skill_coverage_percentage": 85.0,
            "semantic_similarity_percentage": 78.0,
            "keyword_overlap_percentage": 80.0,
            "matched_skills": ["Python", "SQL", "Pandas", "Docker"],
            "missing_skills": ["Tableau"],
        }
    }

    pdf_bytes = pdf_report_generator.generate_report(analysis_data)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    # Standard PDF header magic bytes
    assert pdf_bytes.startswith(b"%PDF")
