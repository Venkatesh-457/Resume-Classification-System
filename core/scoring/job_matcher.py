"""
Job Description Matcher Module
Analyzes alignment between a candidate resume and a specific job description.
Computes technical skill overlap, semantic cosine similarity, keyword coverage, and tailored advice.
"""

from dataclasses import dataclass, field
import re
from sklearn.metrics.pairwise import cosine_similarity
from core.features.skill_extractor import skill_extractor
from core.preprocessing.normalizer import preprocess_resume_text
from core.features.tfidf_builder import create_word_vectorizer


@dataclass
class JobMatchResult:
    """Comprehensive job matching analytical breakdown."""
    match_score: float
    grade: str
    skill_coverage_percentage: float
    semantic_similarity_percentage: float
    keyword_overlap_percentage: float
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    job_required_skills: list[str] = field(default_factory=list)
    resume_skills: list[str] = field(default_factory=list)
    tailored_recommendations: list[str] = field(default_factory=list)


def calculate_job_match(
    resume_text: str,
    job_description: str,
    vectorizer=None,
) -> JobMatchResult:
    """
    Compare resume against target job description.
    
    Formula:
    - Skill Coverage: 40%
    - Semantic / TF-IDF Cosine Similarity: 35%
    - Keyword / Jaccard Overlap: 25%
    """
    if not resume_text.strip() or not job_description.strip():
        return JobMatchResult(
            match_score=0.0,
            grade="Incomplete",
            skill_coverage_percentage=0.0,
            semantic_similarity_percentage=0.0,
            keyword_overlap_percentage=0.0,
            tailored_recommendations=["Both resume text and job description are required for matching analysis."],
        )

    # 1. Skill Extraction on both documents
    resume_skills_res = skill_extractor.extract_skills(resume_text)
    jd_skills_res = skill_extractor.extract_skills(job_description)

    resume_skills_set = set(resume_skills_res.all_detected_skills)
    jd_skills_set = set(jd_skills_res.all_detected_skills)

    matched_skills = sorted(list(resume_skills_set.intersection(jd_skills_set)))
    missing_skills = sorted(list(jd_skills_set - resume_skills_set))

    if jd_skills_set:
        skill_coverage = (len(matched_skills) / len(jd_skills_set)) * 100.0
    else:
        # If JD has no detectable skills from taxonomy, base skill score on general keywords
        skill_coverage = 70.0

    # 2. Semantic TF-IDF Similarity
    clean_resume = preprocess_resume_text(resume_text)
    clean_jd = preprocess_resume_text(job_description)

    if vectorizer is None:
        local_vec = create_word_vectorizer(ngram_range=(1, 2), max_features=3000)
        try:
            tfidf_matrix = local_vec.fit_transform([clean_resume, clean_jd])
            sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
            semantic_sim = max(0.0, min(100.0, sim * 100.0))
        except Exception:
            semantic_sim = 50.0
    else:
        try:
            r_vec = vectorizer.transform([clean_resume])
            j_vec = vectorizer.transform([clean_jd])
            sim = float(cosine_similarity(r_vec, j_vec)[0][0])
            semantic_sim = max(0.0, min(100.0, sim * 100.0))
        except Exception:
            semantic_sim = 50.0

    # 3. Keyword / Vocabulary Overlap
    resume_tokens = set(clean_resume.split())
    jd_tokens = set(clean_jd.split())

    if jd_tokens:
        overlap_tokens = resume_tokens.intersection(jd_tokens)
        keyword_overlap = (len(overlap_tokens) / len(jd_tokens)) * 100.0
    else:
        keyword_overlap = 50.0

    # Weighted Aggregate Match Score
    # 40% skills, 35% semantic, 25% keywords
    raw_match = (0.40 * skill_coverage) + (0.35 * semantic_sim) + (0.25 * keyword_overlap)
    match_score = max(0.0, min(100.0, round(raw_match, 1)))

    if match_score >= 85:
        grade = "High Match (Target Candidate)"
    elif match_score >= 70:
        grade = "Moderate Match (Competitive)"
    elif match_score >= 50:
        grade = "Partial Match (Gaps Detected)"
    else:
        grade = "Low Match (Substantial Pivot Required)"

    # Actionable tailored recommendations
    recommendations = []
    if missing_skills:
        top_missing = missing_skills[:6]
        recommendations.append(
            f"Add relevant experience or project coursework covering key job requirements: {', '.join(top_missing)}."
        )

    if semantic_sim < 40.0:
        recommendations.append(
            "The language in your resume diverges from the terminology in the job description. Adapt section phrasing to mirror job requirements."
        )

    if keyword_overlap < 30.0:
        recommendations.append(
            "Low keyword alignment. Ensure common industry nouns, role titles, and technology stack terms are explicitly mentioned."
        )

    if not recommendations:
        recommendations.append("Strong overall profile alignment with the provided job description.")

    return JobMatchResult(
        match_score=match_score,
        grade=grade,
        skill_coverage_percentage=round(skill_coverage, 1),
        semantic_similarity_percentage=round(semantic_sim, 1),
        keyword_overlap_percentage=round(keyword_overlap, 1),
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        job_required_skills=sorted(list(jd_skills_set)),
        resume_skills=sorted(list(resume_skills_set)),
        tailored_recommendations=recommendations,
    )
