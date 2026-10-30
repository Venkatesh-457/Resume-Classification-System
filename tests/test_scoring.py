"""
Automated Tests for ATS Scoring and Job Match Studio
Covers 0-100 score bounds, component normalization, missing data handling, and job match similarity.
"""

from core.scoring.ats_scorer import calculate_ats_score, ATSScoreResult
from core.scoring.job_matcher import calculate_job_match, JobMatchResult


def test_ats_score_bounds_and_components():
    sample_resume = """
    John Doe
    Email: john@example.com | Phone: 555-123-4567 | LinkedIn: linkedin.com/in/johndoe
    
    PROFESSIONAL SUMMARY
    Senior Software Engineer with 6 years experience architecting distributed backend services.
    
    WORK EXPERIENCE
    Lead Backend Engineer at Stripe (2020 - Present)
    • Spearheaded transition to event-driven microservices architecture handling 50,000 requests/sec.
    • Optimized database indexing in PostgreSQL reducing latency by 45%.
    • Managed a team of 8 software engineers delivering high-availability financial APIs.
    
    EDUCATION
    BS in Computer Science, University of California, Berkeley
    
    TECHNICAL SKILLS
    Python, Java, Go, PostgreSQL, Redis, Docker, Kubernetes, AWS, REST APIs, CI/CD
    
    KEY PROJECTS
    Resume Classification Platform: Developed an NLP system achieving 95% accuracy.
    """
    res: ATSScoreResult = calculate_ats_score(sample_resume)

    assert 0.0 <= res.total_score <= 100.0
    assert res.total_score >= 70.0  # Well-structured comprehensive resume
    assert "A" in res.grade or "B" in res.grade

    b = res.breakdown
    assert 0.0 <= b.structure_readability <= 15.0
    assert 0.0 <= b.contact_information <= 15.0
    assert 0.0 <= b.section_coverage <= 20.0
    assert 0.0 <= b.skills_depth <= 25.0
    assert 0.0 <= b.quantifiable_metrics <= 15.0
    assert 0.0 <= b.action_verbs <= 10.0


def test_ats_score_empty_text():
    res = calculate_ats_score("")
    assert res.total_score == 0.0
    assert res.grade == "Needs Improvement"
    assert len(res.recommendations) > 0


def test_job_match_calculation():
    resume = "Senior Python Developer with Django, FastAPI, Docker, and PostgreSQL experience."
    jd = "Seeking Python Developer skilled in Django, PostgreSQL, and AWS Cloud infrastructure."

    match_res: JobMatchResult = calculate_job_match(resume, jd)

    assert 0.0 <= match_res.match_score <= 100.0
    assert "Python" in match_res.matched_skills
    assert "PostgreSQL" in match_res.matched_skills or "Django" in match_res.matched_skills
    assert "AWS" in match_res.missing_skills or match_res.skill_coverage_percentage > 0.0
    assert len(match_res.tailored_recommendations) > 0
