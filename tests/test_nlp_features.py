"""
Automated Tests for NLP Preprocessing & Feature Engineering Layer
Covers Unicode normalization, technical token preservation, lemmatization, and skill taxonomy extraction.
"""

from core.preprocessing.text_cleaner import (
    normalize_unicode,
    preserve_tech_tokens,
    restore_tech_tokens,
    extract_contact_info,
    identify_sections,
)
from core.preprocessing.normalizer import preprocess_resume_text
from core.features.skill_extractor import skill_extractor


def test_unicode_normalization():
    dirty_text = "Curriculum Vitæ with résumé and café accents."
    clean = normalize_unicode(dirty_text)
    assert "Vitae" in clean or "Vita" in clean
    assert "resume" in clean


def test_tech_token_preservation():
    sample = "Expert in C++, C#, .NET, Node.js, and CI/CD automation."
    preserved = preserve_tech_tokens(sample)
    assert "techtoken_cpp" in preserved
    assert "techtoken_csharp" in preserved
    assert "techtoken_dotnet" in preserved
    assert "techtoken_nodejs" in preserved
    assert "techtoken_cicd" in preserved

    restored = restore_tech_tokens(preserved)
    assert "c++" in restored
    assert "c#" in restored
    assert ".net" in restored


def test_contact_info_extraction():
    text = """
    John Doe
    Email: john.doe@techcorp.com
    Phone: (555) 234-5678
    Portfolio: https://johndoe.dev
    LinkedIn: linkedin.com/in/johndoe
    GitHub: github.com/johndoe
    """
    info = extract_contact_info(text)
    assert "john.doe@techcorp.com" in info.emails
    assert len(info.phones) >= 1
    assert any("johndoe" in l for l in info.linkedin)
    assert any("johndoe" in g for g in info.github)


def test_section_identification():
    text = """
    John Doe
    SUMMARY
    Experienced professional.
    
    WORK EXPERIENCE
    Software Engineer at Google.
    
    EDUCATION
    BS in Computer Science.
    
    TECHNICAL SKILLS
    Python, SQL, AWS.
    
    KEY PROJECTS
    Resume Classification System.
    """
    sections = identify_sections(text)
    assert sections["summary"] is True
    assert sections["experience"] is True
    assert sections["education"] is True
    assert sections["skills"] is True
    assert sections["projects"] is True


def test_preprocess_resume_text_pipeline():
    raw = "Architected high-scale REST APIs using Python, C++, and PostgreSQL for 100,000+ users!"
    processed = preprocess_resume_text(raw)
    assert "python" in processed
    assert "postgresql" in processed
    # Punctuation stripped, numbers stripped, lowercase
    assert "!" not in processed


def test_skill_extractor_taxonomy():
    text = "Fullstack developer with React, Node.js, PostgreSQL, Docker, and AWS experience."
    res = skill_extractor.extract_skills(text)

    assert res.total_skills_count >= 5
    assert "React" in res.all_detected_skills
    assert "Node.js" in res.all_detected_skills
    assert "PostgreSQL" in res.all_detected_skills
    assert "Docker" in res.all_detected_skills
    assert "AWS" in res.all_detected_skills

    # Alias mapping verification (e.g. k8s -> Kubernetes, postgres -> PostgreSQL)
    alias_text = "Deployed services on k8s and postgres database."
    alias_res = skill_extractor.extract_skills(alias_text)
    assert "Kubernetes" in alias_res.all_detected_skills
    assert "PostgreSQL" in alias_res.all_detected_skills
