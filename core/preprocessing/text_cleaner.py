"""
NLP Text Cleaner Module
Performs Unicode normalization, regex-based entity masking, section header extraction,
and specialized technical token preservation (e.g., C++, C#, .NET, Node.js).
"""

import re
import unicodedata
from dataclasses import dataclass


# Technical tokens that risk corruption during punctuation stripping or standard tokenization
TECH_TOKEN_MAP = {
    r"(?<![a-zA-Z0-9])c\+\+(?![a-zA-Z0-9])": "techtoken_cpp",
    r"(?<![a-zA-Z0-9])c#(?![a-zA-Z0-9])": "techtoken_csharp",
    r"(?<![a-zA-Z0-9])\.net(?![a-zA-Z0-9])": "techtoken_dotnet",
    r"(?<![a-zA-Z0-9])node\.js(?![a-zA-Z0-9])": "techtoken_nodejs",
    r"(?<![a-zA-Z0-9])vue\.js(?![a-zA-Z0-9])": "techtoken_vuejs",
    r"(?<![a-zA-Z0-9])react\.js(?![a-zA-Z0-9])": "techtoken_reactjs",
    r"(?<![a-zA-Z0-9])next\.js(?![a-zA-Z0-9])": "techtoken_nextjs",
    r"(?<![a-zA-Z0-9])ci/cd(?![a-zA-Z0-9])": "techtoken_cicd",
    r"(?<![a-zA-Z0-9])tcp/ip(?![a-zA-Z0-9])": "techtoken_tcpip",
    r"(?<![a-zA-Z0-9])pl/sql(?![a-zA-Z0-9])": "techtoken_plsql",
    r"(?<![a-zA-Z0-9])ui/ux(?![a-zA-Z0-9])": "techtoken_uiux",
    r"(?<![a-zA-Z0-9])scikit-learn(?![a-zA-Z0-9])": "techtoken_scikitlearn",
}

TECH_TOKEN_REVERSE_MAP = {
    "techtoken_cpp": "c++",
    "techtoken_csharp": "c#",
    "techtoken_dotnet": ".net",
    "techtoken_nodejs": "node.js",
    "techtoken_vuejs": "vue.js",
    "techtoken_reactjs": "react.js",
    "techtoken_nextjs": "next.js",
    "techtoken_cicd": "ci/cd",
    "techtoken_tcpip": "tcp/ip",
    "techtoken_plsql": "pl/sql",
    "techtoken_uiux": "ui/ux",
    "techtoken_scikitlearn": "scikit-learn",
}

# Section header patterns typical in professional resumes
SECTION_PATTERNS = {
    "summary": re.compile(r"^(?:professional\s+)?(?:summary|profile|about\s*me|overview|objective)\b", re.IGNORECASE),
    "experience": re.compile(r"^(?:work\s+|professional\s+)?(?:experience|employment|work\s+history|career\s+history)\b", re.IGNORECASE),
    "education": re.compile(r"^(?:education|academic\s+background|qualifications|degrees)\b", re.IGNORECASE),
    "skills": re.compile(r"^(?:technical\s+|core\s+)?(?:skills?|competencies|technologies|expertise)\b", re.IGNORECASE),
    "projects": re.compile(r"^(?:key\s+|featured\s+|academic\s+)?(?:projects?|portfolio|personal\s+projects?|coding\s+profiles?)\b", re.IGNORECASE),
    "certifications": re.compile(r"^(?:certifications?|certificates?|licenses?|courses|accreditations|credentials)\b", re.IGNORECASE),
    "awards": re.compile(r"^(?:awards|honors|achievements|recognition)\b", re.IGNORECASE),
    "contact": re.compile(r"^(?:contact|contact\s+info|contact\s+information|personal\s+details)\b", re.IGNORECASE),
}

EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_REGEX = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b")
URL_REGEX = re.compile(r"https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_+.~#?&//=]*)")
LINKEDIN_REGEX = re.compile(r"linkedin\.com/(?:in|profile)/[a-zA-Z0-9-_]+", re.IGNORECASE)
GITHUB_REGEX = re.compile(r"github\.com/[a-zA-Z0-9-_]+", re.IGNORECASE)


@dataclass
class ContactInfo:
    """Extracted contact information details."""
    emails: list[str]
    phones: list[str]
    urls: list[str]
    linkedin: list[str]
    github: list[str]


def normalize_unicode(text: str) -> str:
    """Standardize unicode characters into ASCII compatibility NFKD form with ligature expansion."""
    if not text:
        return ""
    # Expand common ligatures
    text = text.replace("æ", "ae").replace("Æ", "AE").replace("œ", "oe").replace("Œ", "OE")
    normalized = unicodedata.normalize("NFKD", text)
    return normalized.encode("ascii", "ignore").decode("utf-8", "ignore")


def preserve_tech_tokens(text: str) -> str:
    """Replace delicate technical abbreviations with safe alphanumeric placeholders."""
    for pattern, replacement in TECH_TOKEN_MAP.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def restore_tech_tokens(text: str) -> str:
    """Restore placeholders back to recognizable canonical token strings."""
    for placeholder, original in TECH_TOKEN_REVERSE_MAP.items():
        text = text.replace(placeholder, original)
    return text


def extract_contact_info(text: str) -> ContactInfo:
    """Extract emails, phone numbers, website URLs, and developer profiles."""
    emails = list(set(EMAIL_REGEX.findall(text)))
    phones = list(set(PHONE_REGEX.findall(text)))
    # Filter out false positive short phone matches
    valid_phones = [p for p in phones if sum(c.isdigit() for c in p) >= 9]
    urls = list(set(URL_REGEX.findall(text)))
    linkedin = list(set(LINKEDIN_REGEX.findall(text)))
    github = list(set(GITHUB_REGEX.findall(text)))

    return ContactInfo(
        emails=emails,
        phones=valid_phones,
        urls=urls,
        linkedin=linkedin,
        github=github,
    )


def identify_sections(text: str) -> dict[str, bool]:
    """
    Check for the presence of standard resume sections by inspecting line beginnings.
    Returns a mapping of section_name -> bool.
    """
    detected_sections = {section: False for section in SECTION_PATTERNS}
    lines = text.split("\n")

    for line in lines:
        cleaned_line = line.strip().strip(":#*- ")
        if not cleaned_line or len(cleaned_line) > 40:
            continue
        for section, pattern in SECTION_PATTERNS.items():
            if not detected_sections[section] and pattern.search(cleaned_line):
                detected_sections[section] = True

    return detected_sections
