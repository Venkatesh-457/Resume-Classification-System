"""
ATS Resume Quality Scoring Module
Calculates an explainable, multi-component resume quality score (0 to 100).
Evaluates structure, contact info, section coverage, skills depth, measurable metrics,
and action verbs with clear recommendations.
"""

from dataclasses import dataclass, field
import re
from core.preprocessing.text_cleaner import extract_contact_info, identify_sections
from core.features.skill_extractor import skill_extractor, SkillExtractionResult

# Strong action verbs typical of high-impact resumes
ACTION_VERBS = {
    "accelerated", "achieved", "analyzed", "architected", "automated", "built", "centralized",
    "collaborated", "configured", "constructed", "created", "decreased", "delivered", "deployed",
    "designed", "developed", "directed", "documented", "drove", "engineered", "enhanced",
    "established", "executed", "expanded", "formulated", "guided", "implemented", "improved",
    "increased", "initiated", "integrated", "launched", "lead", "led", "managed", "maximized",
    "mentored", "migrated", "minimized", "modernized", "monitored", "negotiated", "optimized",
    "orchestrated", "organized", "overhauled", "pioneered", "planned", "produced", "programmed",
    "reduced", "refactored", "resolved", "restructured", "scaled", "secured", "simplified",
    "spearheaded", "standardized", "streamlined", "strengthened", "supervised", "tested", "transformed"
}

# Regex to detect measurable achievements (numbers, percentages, currencies, metrics)
METRIC_REGEX = re.compile(
    r"\b(?:\$?\d+(?:\.\d+)?%|\$\d+(?:,\d{3})*(?:\.\d+)?|\d+\+?\s*(?:users|clients|customers|projects|requests|million|billion|k|gb|tb|ms|sec|hours))\b",
    re.IGNORECASE
)


@dataclass
class ScoreBreakdown:
    """Detailed score points for each of the 6 core components."""
    structure_readability: float  # max 15
    contact_information: float   # max 15
    section_coverage: float       # max 20
    skills_depth: float           # max 25
    quantifiable_metrics: float   # max 15
    action_verbs: float           # max 10
    penalties: float              # deductions

    def to_dict(self) -> dict[str, float]:
        return {
            "Structure & Readability (max 15)": round(self.structure_readability, 1),
            "Contact Information (max 15)": round(self.contact_information, 1),
            "Section Coverage (max 20)": round(self.section_coverage, 1),
            "Skills Depth & Taxonomy (max 25)": round(self.skills_depth, 1),
            "Quantifiable Metrics (max 15)": round(self.quantifiable_metrics, 1),
            "Action Verbs & Tone (max 10)": round(self.action_verbs, 1),
            "Penalties Deducted": round(self.penalties, 1),
        }


@dataclass
class ATSScoreResult:
    """Complete ATS Quality evaluation result."""
    total_score: float
    grade: str
    breakdown: ScoreBreakdown
    detected_sections: dict[str, bool]
    contact_details: dict[str, list[str]]
    quantifiable_metrics_count: int
    action_verbs_count: int
    detected_action_verbs: list[str]
    recommendations: list[str] = field(default_factory=list)
    disclaimer: str = (
        "Educational ATS Score: This score evaluates formatting, section completeness, "
        "quantifiable metrics, and technical skill breadth based on industry best practices. "
        "It is not an official score from any proprietary commercial ATS vendor."
    )


def calculate_ats_score(
    raw_text: str,
    skill_result: SkillExtractionResult | None = None,
) -> ATSScoreResult:
    """
    Compute explainable ATS Resume Quality Score (0 to 100).
    """
    if not raw_text or not raw_text.strip():
        empty_breakdown = ScoreBreakdown(0, 0, 0, 0, 0, 0, 0)
        return ATSScoreResult(
            total_score=0.0,
            grade="Needs Improvement",
            breakdown=empty_breakdown,
            detected_sections={},
            contact_details={},
            quantifiable_metrics_count=0,
            action_verbs_count=0,
            detected_action_verbs=[],
            recommendations=["Document contains no readable text to evaluate."],
        )

    words = raw_text.split()
    word_count = len(words)
    recommendations = []

    # 1. Structure & Readability (Max 15 pts)
    # Optimal length: 350 to 900 words (~1-2 pages)
    structure_score = 0.0
    if 350 <= word_count <= 950:
        structure_score = 15.0
    elif 200 <= word_count < 350:
        structure_score = 10.0
        recommendations.append("Resume is somewhat brief (< 350 words). Consider elaborating on key projects and responsibilities.")
    elif 950 < word_count <= 1500:
        structure_score = 11.0
        recommendations.append("Resume is lengthy (> 950 words). Try condensing bullet points into concise, high-impact statements.")
    elif word_count < 200:
        structure_score = 4.0
        recommendations.append("Resume is critically short (< 200 words). Add comprehensive work experience, education, and skills.")
    else:
        structure_score = 7.0
        recommendations.append("Resume exceeds 1,500 words. Industry ATS guidelines recommend keeping resumes to 1-2 pages.")

    # 2. Contact Information (Max 15 pts)
    # Email: 5 pts, Phone: 4 pts, LinkedIn/URL/GitHub: 4 pts, Name/Location header: 2 pts
    contact = extract_contact_info(raw_text)
    contact_score = 0.0
    if contact.emails:
        contact_score += 5.0
    else:
        recommendations.append("Missing professional email address. Ensure a clear contact email is visible at the top.")

    if contact.phones:
        contact_score += 4.0
    else:
        recommendations.append("Missing contact phone number.")

    if contact.linkedin or contact.github or contact.urls:
        contact_score += 4.0
    else:
        recommendations.append("Add a LinkedIn profile or GitHub/portfolio URL to showcase verified work.")

    # Header presence
    if len(raw_text.splitlines()[:5]) >= 2:
        contact_score += 2.0

    contact_score = min(15.0, contact_score)

    # 3. Resume Section Coverage (Max 20 pts)
    # Experience (5), Education (4), Skills (4), Projects (3), Summary (2), Certifications (2)
    sections = identify_sections(raw_text)
    section_score = 0.0
    if sections.get("experience"):
        section_score += 5.0
    else:
        recommendations.append("Missing explicit 'Experience' or 'Work History' section header.")

    if sections.get("education"):
        section_score += 4.0
    else:
        recommendations.append("Missing explicit 'Education' or 'Academic Background' section header.")

    if sections.get("skills"):
        section_score += 4.0
    else:
        recommendations.append("Missing dedicated 'Skills' or 'Technical Competencies' section.")

    if sections.get("projects"):
        section_score += 3.0
    else:
        recommendations.append("Consider adding a 'Projects' section to showcase practical applications.")

    if sections.get("summary"):
        section_score += 2.0
    else:
        recommendations.append("Adding a brief 2-3 sentence 'Professional Summary' or 'Profile' improves ATS readability.")

    if sections.get("certifications") or sections.get("awards"):
        section_score += 2.0

    section_score = min(20.0, section_score)

    # 4. Technical Skills Depth (Max 25 pts)
    if skill_result is None:
        skill_result = skill_extractor.extract_skills(raw_text)

    skills_count = skill_result.total_skills_count
    categories_count = len(skill_result.skills_by_category)

    if skills_count >= 12 and categories_count >= 3:
        skills_score = 25.0
    elif skills_count >= 8 and categories_count >= 2:
        skills_score = 21.0
    elif skills_count >= 5:
        skills_score = 16.0
        recommendations.append("Skill coverage is modest. Include more domain-specific tools, frameworks, and methodologies.")
    elif skills_count >= 2:
        skills_score = 10.0
        recommendations.append("Low technical skill density detected. Detail specific programming languages, libraries, and tools.")
    else:
        skills_score = 4.0
        recommendations.append("Critically low technical keyword detection. Ensure relevant industry keywords are explicitly listed.")

    # 5. Quantifiable Achievements & Metrics (Max 15 pts)
    metrics_matches = list(set(METRIC_REGEX.findall(raw_text)))
    metrics_count = len(metrics_matches)
    if metrics_count >= 5:
        metrics_score = 15.0
    elif metrics_count >= 3:
        metrics_score = 12.0
    elif metrics_count >= 1:
        metrics_score = 8.0
        recommendations.append("Strengthen resume bullet points by adding quantifiable outcomes (e.g. 'boosted throughput by 30%', 'managed $50K budget').")
    else:
        metrics_score = 3.0
        recommendations.append("No quantifiable metrics detected. Employers and ATS algorithms prioritize data-driven achievements.")

    # 6. Action Verbs & Professional Phrasing (Max 10 pts)
    lower_words = set(w.lower().strip(".,;:()") for w in words)
    found_verbs = sorted(list(lower_words.intersection(ACTION_VERBS)))
    verbs_count = len(found_verbs)

    if verbs_count >= 10:
        verbs_score = 10.0
    elif verbs_count >= 6:
        verbs_score = 8.0
    elif verbs_count >= 3:
        verbs_score = 5.0
        recommendations.append("Incorporate more active power verbs (e.g., 'engineered', 'spearheaded', 'orchestrated') at the start of bullets.")
    else:
        verbs_score = 2.0
        recommendations.append("Bullet points lack strong action verbs. Avoid passive phrasing like 'responsible for' or 'worked on'.")

    # Penalties (Extreme formatting or noise)
    penalties = 0.0
    special_char_ratio = len(re.findall(r"[^\w\s.,;:/\-()%$#@]", raw_text)) / max(1, len(raw_text))
    if special_char_ratio > 0.08:
        penalties += 5.0
        recommendations.append("Document contains unusual character noise, which may stem from complex formatting or OCR artifacts.")

    # Total Calculation
    raw_total = structure_score + contact_score + section_score + skills_score + metrics_score + verbs_score - penalties
    total_score = max(0.0, min(100.0, round(raw_total, 1)))

    # Grade Assignment
    if total_score >= 90:
        grade = "A+ (Outstanding)"
    elif total_score >= 80:
        grade = "A (Strong Match)"
    elif total_score >= 70:
        grade = "B (Good Foundation)"
    elif total_score >= 60:
        grade = "C (Fair - Needs Polish)"
    else:
        grade = "Needs Improvement"

    breakdown = ScoreBreakdown(
        structure_readability=structure_score,
        contact_information=contact_score,
        section_coverage=section_score,
        skills_depth=skills_score,
        quantifiable_metrics=metrics_score,
        action_verbs=verbs_score,
        penalties=penalties,
    )

    contact_dict = {
        "emails": contact.emails,
        "phones": contact.phones,
        "linkedin": contact.linkedin,
        "github": contact.github,
        "urls": contact.urls,
    }

    return ATSScoreResult(
        total_score=total_score,
        grade=grade,
        breakdown=breakdown,
        detected_sections=sections,
        contact_details=contact_dict,
        quantifiable_metrics_count=metrics_count,
        action_verbs_count=verbs_count,
        detected_action_verbs=found_verbs[:12],
        recommendations=recommendations,
    )
