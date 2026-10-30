"""
Resume Document Validation Module
Determines whether an uploaded document is legitimately a Resume or CV
prior to downstream classification, skill extraction, or ATS scoring.

Evaluates multi-factor weighted signals:
1. Contact Information & Candidate Identity
2. Candidate-related Section Headings (Education, Experience, Skills, Projects, etc.)
3. Academic Degrees and Educational Credentials
4. Professional Experience and Employment History
5. Employment / Graduation Timelines and Date Patterns
6. Action Verbs and Structural Characteristics
7. Negative Indicators (Academic papers, invoices, terms of service, arbitrary prose)
"""

from dataclasses import dataclass, field
from enum import Enum
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class ResumeValidationDecision(str, Enum):
    """Validation decision categories for uploaded documents."""
    VALID_RESUME = "VALID_RESUME"
    UNCERTAIN_DOCUMENT = "UNCERTAIN_DOCUMENT"
    NOT_A_RESUME = "NOT_A_RESUME"


@dataclass
class ValidationResult:
    """Detailed result container from resume content validation."""
    decision: ResumeValidationDecision
    confidence_score: float  # Normalized 0.0 to 100.0
    is_valid: bool
    is_uncertain: bool
    reasons: list[str] = field(default_factory=list)
    detected_signals: dict[str, Any] = field(default_factory=dict)
    message: str = ""


class ResumeValidator:
    """
    Evaluates whether raw extracted document text possesses the structural,
    lexical, and semantic characteristics of a legitimate Resume or CV.
    """

    # Minimum threshold for meaningful document content
    MIN_WORD_COUNT = 30
    MIN_CHAR_COUNT = 150

    # 1. Contact Info Patterns
    EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_REGEX = re.compile(
        r'(?:(?:\+|00)\d{1,3}[-.\s]*)?(?:\(?\d{2,4}\)?[-.\s]*)?\d{3,5}[-.\s]*\d{3,5}\b'
    )
    LINK_REGEX = re.compile(
        r'(?:linkedin\.com/(?:in|pub)/|github\.com/|gitlab\.com/|behance\.net/|dribbble\.com/|kaggle\.com/|portfolio|gitee\.com/)',
        re.IGNORECASE
    )

    # 2. Section Headings (checked as lines or prominent headers)
    SECTION_PATTERNS = {
        "education": re.compile(
            r'(?:^|\n)\s*(?:education|academic(?:s|\s+background|\s+qualifications|\s+credentials)?|degrees?|qualifications?|coursework|educational\s+details)\b',
            re.IGNORECASE
        ),
        "experience": re.compile(
            r'(?:^|\n)\s*(?:work\s+experience|professional\s+experience|employment(?:\s+history)?|experience|career\s+history|internships?(?:\s+experience)?|work\s+history|industry\s+experience)\b',
            re.IGNORECASE
        ),
        "skills": re.compile(
            r'(?:^|\n)\s*(?:technical\s+skills?|key\s+skills?|core\s+competencies|skills?\s*(?:&|and)\s*abilities|skills?\s*(?:&|and)\s*tools|skills?|technologies|areas\s+of\s+expertise|proficiencies|tools?\s*(?:&|and)\s*technologies)\b',
            re.IGNORECASE
        ),
        "projects": re.compile(
            r'(?:^|\n)\s*(?:projects?|academic\s+projects?|personal\s+projects?|key\s+projects?|project\s+work|capstone\s+projects?)\b',
            re.IGNORECASE
        ),
        "summary": re.compile(
            r'(?:^|\n)\s*(?:summary|professional\s+summary|career\s+objective|profile\s+summary|executive\s+summary|about\s+me|objective)\b',
            re.IGNORECASE
        ),
        "certifications": re.compile(
            r'(?:^|\n)\s*(?:certifications?|certificates?|licenses?|courses?\s*(?:&|and)\s*certifications?|trainings?)\b',
            re.IGNORECASE
        ),
        "achievements": re.compile(
            r'(?:^|\n)\s*(?:achievements?|awards?(?:\s*(?:&|and)\s*honors?)?|honors?|accomplishments?|extracurricular(?:\s+activities)?)\b',
            re.IGNORECASE
        ),
        "personal": re.compile(
            r'(?:^|\n)\s*(?:personal\s+details|personal\s+profile|languages?\s+known|languages?|declaration|hobbies)\b',
            re.IGNORECASE
        ),
    }

    # 3. Academic Degrees and Credentials
    DEGREE_PATTERNS = re.compile(
        r'\b(?:b\.?\s*tech|b\.?\s*e\.?|b\.?\s*s\.?|bachelor(?:[\'’]s)?(?:\s+of\s+[a-z]+)?|'
        r'm\.?\s*tech|m\.?\s*e\.?|m\.?\s*s\.?|master(?:[\'’]s)?(?:\s+of\s+[a-z]+)?|'
        r'ph\.?\s*d|doctorate|diploma|intermediate|matriculation|higher\s+secondary|'
        r'bca|mca|bba|mba|b\.?\s*sc|m\.?\s*sc|associate\s+degree)\b',
        re.IGNORECASE
    )
    ACADEMIC_INSTITUTION = re.compile(
        r'\b(?:university|institute(?:\s+of\s+technology)?|college|school|academy|polytechnic|campus)\b',
        re.IGNORECASE
    )
    ACADEMIC_PERF = re.compile(
        r'\b(?:cgpa|gpa|percentage|percentile|aggregate|marks|grade|valedictorian|cum\s+laude)\b',
        re.IGNORECASE
    )

    # 4. Timeline and Date Patterns
    DATE_RANGE_REGEX = re.compile(
        r'\b(?:(?:19|20)\d{2}\s*[-–—to/]+\s*(?:(?:19|20)\d{2}|present|current|ongoing|till\s+date|now))\b',
        re.IGNORECASE
    )
    MONTH_YEAR_REGEX = re.compile(
        r'\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|'
        r'aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)[a-z]*\.?\s*(?:19|20)\d{2}\b',
        re.IGNORECASE
    )
    EXPERIENCE_DURATION = re.compile(
        r'\b\d+\+?\s*(?:years?|yrs?|months?|mos?)\s*(?:of\s*)?(?:experience|exp|track\s+record)\b',
        re.IGNORECASE
    )

    # 5. Professional Titles and Action Verbs
    JOB_TITLES = re.compile(
        r'\b(?:software\s+(?:engineer|developer)|web\s+developer|frontend\s+developer|backend\s+developer|'
        r'full\s*stack\s+developer|data\s+scientist|data\s+analyst|machine\s+learning\s+engineer|'
        r'devops\s+engineer|cloud\s+engineer|business\s+analyst|ui/ux\s+designer|system\s+administrator|'
        r'qa\s+engineer|product\s+manager|project\s+manager|intern|associate|consultant|lead|architect)\b',
        re.IGNORECASE
    )
    ACTION_VERBS = re.compile(
        r'\b(?:developed|implemented|designed|created|managed|led|collaborated|spearheaded|'
        r'architected|optimized|engineered|delivered|achieved|built|conducted|assisted|'
        r'maintained|supervised|automated|facilitated|analyzed|coordinated|resolved)\b',
        re.IGNORECASE
    )

    # 6. Negative Indicators (Strong indicators that document is NOT a resume)
    ACADEMIC_PAPER_MARKERS = re.compile(
        r'\b(?:abstract\b.{0,60}\bkeywords\b|related\s+work|proceedings\s+of|ieee\s+transactions|'
        r'conference\s+on|journal\s+of|arxiv:\d+|doi:\s*10\.\d+|table\s+of\s+contents|'
        r'literature\s+review|methodology\s+and\s+experiments|concluding\s+remarks)\b',
        re.IGNORECASE
    )
    INVOICE_MARKERS = re.compile(
        r'\b(?:invoice\s+(?:number|no|#)|bill\s+to\b|ship\s+to\b|payment\s+terms|due\s+date|'
        r'subtotal|total\s+due|amount\s+due|balance\s+due|purchase\s+order\s+no|tax\s+invoice)\b',
        re.IGNORECASE
    )
    LEGAL_MARKERS = re.compile(
        r'\b(?:terms\s+and\s+conditions|terms\s+of\s+service|privacy\s+policy|hereby\s+agree|'
        r'governing\s+law|indemnification|limitation\s+of\s+liability|license\s+agreement|'
        r'all\s+rights\s+reserved|party\s+of\s+the\s+first\s+part|non-disclosure\s+agreement)\b',
        re.IGNORECASE
    )

    def validate(self, text: str, filename: str = "") -> ValidationResult:
        """
        Validate whether the provided document text is a genuine Resume / CV.

        Returns:
            ValidationResult with decision in (VALID_RESUME, UNCERTAIN_DOCUMENT, NOT_A_RESUME),
            numeric confidence score, reasons, and user-facing guidance message.
        """
        if not text or not isinstance(text, str):
            return ValidationResult(
                decision=ResumeValidationDecision.NOT_A_RESUME,
                confidence_score=0.0,
                is_valid=False,
                is_uncertain=False,
                reasons=["Document text is empty or missing."],
                message="This document does not appear to be a resume or CV. Please upload a valid resume in TXT, DOCX, or PDF format."
            )

        words = text.split()
        word_count = len(words)
        char_count = len(text)

        # Immediate rejection for empty or trivially short documents
        if word_count < self.MIN_WORD_COUNT or char_count < self.MIN_CHAR_COUNT:
            return ValidationResult(
                decision=ResumeValidationDecision.NOT_A_RESUME,
                confidence_score=5.0,
                is_valid=False,
                is_uncertain=False,
                reasons=[f"Document text is insufficient ({word_count} words, {char_count} chars; minimum {self.MIN_WORD_COUNT} required)."],
                message="This document does not appear to be a resume or CV. Please upload a valid resume in TXT, DOCX, or PDF format."
            )

        # -------------------------------------------------------------
        # 1. EVALUATE POSITIVE SIGNALS
        # -------------------------------------------------------------
        signals: dict[str, Any] = {}
        score = 0.0
        reasons: list[str] = []

        # Pillar 1: Contact Information (up to 20 pts)
        has_email = bool(self.EMAIL_REGEX.search(text))
        has_phone = bool(self.PHONE_REGEX.search(text))
        has_link = bool(self.LINK_REGEX.search(text))
        contact_pts = (8.0 if has_email else 0.0) + (7.0 if has_phone else 0.0) + (5.0 if has_link else 0.0)
        score += contact_pts
        signals["contact"] = {
            "has_email": has_email,
            "has_phone": has_phone,
            "has_link": has_link,
            "points": contact_pts,
        }
        if contact_pts >= 7.0:
            reasons.append("Detected verified candidate contact information.")

        # Pillar 2: Section Headings (up to 30 pts)
        detected_sections = []
        for sec_name, pattern in self.SECTION_PATTERNS.items():
            if pattern.search(text):
                detected_sections.append(sec_name)
        
        # Calculate section score: education (8), experience (8), skills (8), projects (6), summary (4), certs (4)
        sec_pts = 0.0
        if "education" in detected_sections:
            sec_pts += 8.0
        if "experience" in detected_sections:
            sec_pts += 8.0
        if "skills" in detected_sections:
            sec_pts += 8.0
        if "projects" in detected_sections:
            sec_pts += 6.0
        if "summary" in detected_sections:
            sec_pts += 4.0
        if "certifications" in detected_sections or "achievements" in detected_sections:
            sec_pts += 4.0
        sec_pts = min(30.0, sec_pts)
        score += sec_pts
        signals["sections"] = {
            "detected": detected_sections,
            "count": len(detected_sections),
            "points": sec_pts,
        }
        if len(detected_sections) >= 2:
            reasons.append(f"Found {len(detected_sections)} standard resume sections ({', '.join(detected_sections[:4])}).")

        # Pillar 3: Academic / Educational Credentials (up to 20 pts)
        has_degree = bool(self.DEGREE_PATTERNS.search(text))
        has_institution = bool(self.ACADEMIC_INSTITUTION.search(text))
        has_perf = bool(self.ACADEMIC_PERF.search(text))
        edu_pts = (8.0 if has_degree else 0.0) + (6.0 if has_institution else 0.0) + (6.0 if has_perf else 0.0)
        score += edu_pts
        signals["education"] = {
            "has_degree": has_degree,
            "has_institution": has_institution,
            "has_performance_metric": has_perf,
            "points": edu_pts,
        }
        if edu_pts >= 8.0:
            reasons.append("Identified academic qualifications / degrees.")

        # Pillar 4: Experience, Timelines and Action Verbs (up to 20 pts)
        date_ranges = self.DATE_RANGE_REGEX.findall(text)
        month_years = self.MONTH_YEAR_REGEX.findall(text)
        has_dates = len(date_ranges) > 0 or len(month_years) > 1 or bool(self.EXPERIENCE_DURATION.search(text))
        has_job_title = bool(self.JOB_TITLES.search(text))
        action_verb_count = len(self.ACTION_VERBS.findall(text))
        
        timeline_pts = (8.0 if has_dates else 0.0) + (6.0 if has_job_title else 0.0) + (min(6.0, action_verb_count * 1.5))
        score += timeline_pts
        signals["experience_timeline"] = {
            "has_dates": has_dates,
            "has_job_title": has_job_title,
            "action_verb_count": action_verb_count,
            "points": timeline_pts,
        }
        if timeline_pts >= 8.0:
            reasons.append("Found professional timeline dates / employment indicators.")

        # Pillar 5: Structural formatting (up to 10 pts)
        has_bullets = bool(re.search(r'[•\-\*■▪]\s+', text))
        has_structured_lines = len([l for l in text.split('\n') if len(l.strip()) > 0 and len(l.strip()) < 80]) > 5
        struct_pts = (5.0 if has_bullets else 0.0) + (5.0 if has_structured_lines else 0.0)
        score += struct_pts
        signals["structure"] = {
            "has_bullets": has_bullets,
            "has_structured_lines": has_structured_lines,
            "points": struct_pts,
        }

        # -------------------------------------------------------------
        # 2. EVALUATE NEGATIVE / NON-RESUME SIGNALS
        # -------------------------------------------------------------
        negative_penalty = 0.0
        neg_reasons = []

        # Check Academic Paper / Thesis Indicators
        academic_matches = len(self.ACADEMIC_PAPER_MARKERS.findall(text))
        has_citations = len(re.findall(r'\[\d{1,3}\]', text)) >= 3
        if academic_matches >= 2 or (academic_matches >= 1 and has_citations):
            penalty = 30.0 if academic_matches >= 2 else 20.0
            negative_penalty += penalty
            neg_reasons.append(f"Document contains academic research paper markers ({academic_matches} matched).")

        # Check Invoices / Receipts
        invoice_matches = len(self.INVOICE_MARKERS.findall(text))
        if invoice_matches >= 2:
            negative_penalty += 35.0
            neg_reasons.append(f"Document contains billing / commercial invoice markers ({invoice_matches} matched).")

        # Check Legal / Policy Contracts
        legal_matches = len(self.LEGAL_MARKERS.findall(text))
        if legal_matches >= 2:
            negative_penalty += 35.0
            neg_reasons.append(f"Document contains legal agreement / terms of service clauses ({legal_matches} matched).")

        # Check excessive continuous essay length without contact/sections
        if word_count > 4000 and len(detected_sections) <= 1 and not has_email and not has_phone:
            negative_penalty += 20.0
            neg_reasons.append("Document is unusually long for a resume with negligible structural sections.")

        signals["negative_penalty"] = negative_penalty
        signals["negative_reasons"] = neg_reasons

        # Net Confidence Score
        # If strong negative indicators are present, cap confidence to reflect non-resume verdict
        if negative_penalty >= 30.0:
            net_score = max(0.0, min(15.0, score - negative_penalty))
        elif negative_penalty >= 20.0:
            net_score = max(0.0, min(25.0, score - negative_penalty))
        else:
            net_score = max(0.0, min(100.0, score - negative_penalty))

        # -------------------------------------------------------------
        # 3. CORE RESUME PILLARS VERIFICATION
        # -------------------------------------------------------------
        # Count primary resume pillars satisfied:
        # P1: Contact info (Email or Phone or Profile link)
        # P2: Educational credentials (Degree, Academic institution, or Education section)
        # P3: Experience / Career trajectory (Experience section, Job titles, or Timeline date ranges)
        # P4: Technical / Professional skills or Projects (Skills section or Projects section)
        p1_contact = contact_pts >= 7.0
        p2_education = (edu_pts >= 8.0) or ("education" in detected_sections)
        p3_experience = (timeline_pts >= 8.0) or ("experience" in detected_sections)
        p4_skills_projects = ("skills" in detected_sections) or ("projects" in detected_sections) or (has_job_title and has_degree)

        pillars_satisfied = sum([p1_contact, p2_education, p3_experience, p4_skills_projects])
        signals["pillars_satisfied_count"] = pillars_satisfied

        # -------------------------------------------------------------
        # 4. DECISION LOGIC
        # -------------------------------------------------------------
        # A valid resume must have:
        # - Net score >= 40.0
        # - At least 2 of the 4 core pillars
        # - No overwhelming non-resume penalty (< 25.0)
        # - At least 1 recognizable section or contact info
        if net_score >= 40.0 and pillars_satisfied >= 2 and negative_penalty < 25.0:
            decision = ResumeValidationDecision.VALID_RESUME
            is_valid = True
            is_uncertain = False
            msg = "Document validated as a legitimate candidate resume / CV."
            reasons.append("Satisfies structural and content requirements of a candidate resume.")
        elif net_score >= 25.0 and (pillars_satisfied >= 1 or len(detected_sections) >= 1) and negative_penalty < 30.0:
            decision = ResumeValidationDecision.UNCERTAIN_DOCUMENT
            is_valid = False
            is_uncertain = True
            msg = (
                "The uploaded document could not be confidently verified as a resume or CV. "
                "Please upload a clearer or more complete resume in TXT, DOCX, or PDF format."
            )
            reasons.append("Document exhibits some resume elements but lacks essential structural sections or candidate details.")
        else:
            decision = ResumeValidationDecision.NOT_A_RESUME
            is_valid = False
            is_uncertain = False
            msg = "This document does not appear to be a resume or CV. Please upload a valid resume in TXT, DOCX, or PDF format."
            reasons.extend(neg_reasons)
            if not reasons:
                reasons.append("Content does not match resume structure, qualifications, or candidate history.")

        return ValidationResult(
            decision=decision,
            confidence_score=round(net_score, 1),
            is_valid=is_valid,
            is_uncertain=is_uncertain,
            reasons=reasons,
            detected_signals=signals,
            message=msg
        )


# Shared validator singleton instance
resume_validator = ResumeValidator()


def validate_resume_document(text: str, filename: str = "") -> ValidationResult:
    """Convenience functional interface for resume validation."""
    return resume_validator.validate(text, filename=filename)
