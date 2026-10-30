"""
Skill Extraction Module
Extracts technical skills and competencies from resume text using a structured taxonomy.
Maps aliases to canonical terms, groups by category, and provides explainable skill analytics.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from config.settings import SKILLS_TAXONOMY_PATH

logger = logging.getLogger(__name__)


@dataclass
class SkillExtractionResult:
    """Structured representation of extracted skills."""
    total_skills_count: int = 0
    unique_skills_count: int = 0
    skills_by_category: dict[str, list[str]] = field(default_factory=dict)
    all_detected_skills: list[str] = field(default_factory=list)
    top_categories: list[tuple[str, int]] = field(default_factory=list)
    disclaimer: str = (
        "Note: Extracted skills represent detected keywords and domain terminology present in the document. "
        "Detection does not verify applicant proficiency, depth of experience, or credential validation."
    )


class SkillExtractor:
    """Configurable rule-based skill extraction engine with alias mapping and categorization."""

    def __init__(self, taxonomy_path: Path | str = SKILLS_TAXONOMY_PATH):
        self.taxonomy_path = Path(taxonomy_path)
        self.categories: dict[str, list[str]] = {}
        self.aliases: dict[str, str] = {}
        self._compiled_patterns: dict[str, re.Pattern] = {}
        self._load_taxonomy()

    def _load_taxonomy(self) -> None:
        """Load skills taxonomy and aliases from JSON file."""
        if not self.taxonomy_path.exists():
            logger.warning("Skills taxonomy file not found at %s. Using default fallback.", self.taxonomy_path)
            self._load_default_taxonomy()
            return

        try:
            with open(self.taxonomy_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.categories = data.get("categories", {})
            self.aliases = data.get("aliases", {})
            self._compile_regexes()
            logger.info("Loaded skills taxonomy: %d categories, %d aliases", len(self.categories), len(self.aliases))
        except Exception as exc:
            logger.exception("Failed to parse skills taxonomy from %s: %s", self.taxonomy_path, exc)
            self._load_default_taxonomy()

    def _load_default_taxonomy(self) -> None:
        """Fallback taxonomy if JSON is missing or invalid."""
        self.categories = {
            "Programming Languages": ["python", "java", "c++", "c#", "javascript", "typescript", "ruby", "go", "php", "sql", "r", "scala", "rust"],
            "Web Frameworks": ["react", "angular", "vue", "django", "flask", "spring boot", "fastapi", "express", "next.js", "node.js"],
            "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible", "jenkins", "ci/cd", "linux"],
            "Data Science & AI": ["machine learning", "deep learning", "nlp", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "tableau", "power bi"],
            "Databases": ["postgresql", "mysql", "mongodb", "redis", "oracle", "sql server", "cassandra", "sqlite"],
        }
        self.aliases = {
            "k8s": "kubernetes",
            "postgres": "postgresql",
            "reactjs": "react",
            "vuejs": "vue",
            "nodejs": "node.js",
            "amazon web services": "aws",
            "google cloud": "gcp",
        }
        self._compile_regexes()

    def _compile_regexes(self) -> None:
        """Precompile regex patterns for skill matching."""
        self._compiled_patterns = {}
        # Collect all unique skills and aliases
        all_terms = set(self.aliases.keys())
        for skill_list in self.categories.values():
            all_terms.update(skill_list)

        for term in all_terms:
            # Handle special characters in terms like c++, c#, .net, ci/cd
            escaped_term = re.escape(term)
            # Use negative lookbehind and lookahead to ensure word boundaries
            pattern_str = rf"(?<![a-zA-Z0-9_]){escaped_term}(?![a-zA-Z0-9_])"
            self._compiled_patterns[term] = re.compile(pattern_str, re.IGNORECASE)

    def extract_skills(self, text: str) -> SkillExtractionResult:
        """
        Extract and categorize skills from the given text.
        Resolves aliases to canonical skill names and prevents duplicates.
        """
        if not text:
            return SkillExtractionResult()

        detected_canonical = set()
        text_lower = text.lower()

        # Check all patterns
        for term, pattern in self._compiled_patterns.items():
            if pattern.search(text_lower):
                # Resolve alias if present, else use term
                canonical = self.aliases.get(term.lower(), term).title()
                # Special capitalization overrides
                capitalization_map = {
                    "Sql": "SQL", "Aws": "AWS", "Gcp": "GCP", "Ai": "AI", "Ml": "ML",
                    "Nlp": "NLP", "Ci/Cd": "CI/CD", "Html": "HTML", "Css": "CSS",
                    "Ui/Ux": "UI/UX", "R": "R", "C++": "C++", "C#": "C#", ".Net": ".NET",
                    "Php": "PHP", "Db": "DB", "Api": "API", "Apis": "APIs", "Etl": "ETL",
                    "Mysql": "MySQL", "Postgresql": "PostgreSQL", "Mongodb": "MongoDB",
                    "Jquery": "jQuery", "Devops": "DevOps", "Pytorch": "PyTorch",
                    "Scikit-Learn": "scikit-learn", "Node.Js": "Node.js", "Vue.Js": "Vue.js",
                    "Next.Js": "Next.js", "Fastapi": "FastAPI",
                }
                canonical = capitalization_map.get(canonical, canonical)
                detected_canonical.add(canonical)

        # Categorize detected skills
        by_category: dict[str, list[str]] = {}
        assigned_skills = set()

        for category_name, skills_in_cat in self.categories.items():
            matched_in_cat = []
            for s in skills_in_cat:
                canon = self.aliases.get(s.lower(), s).title()
                # Re-capitalize
                capitalization_map = {
                    "Sql": "SQL", "Aws": "AWS", "Gcp": "GCP", "Ai": "AI", "Ml": "ML",
                    "Nlp": "NLP", "Ci/Cd": "CI/CD", "Html": "HTML", "Css": "CSS",
                    "Ui/Ux": "UI/UX", "R": "R", "C++": "C++", "C#": "C#", ".Net": ".NET",
                    "Php": "PHP", "Db": "DB", "Api": "API", "Apis": "APIs", "Etl": "ETL",
                    "Mysql": "MySQL", "Postgresql": "PostgreSQL", "Mongodb": "MongoDB",
                    "Jquery": "jQuery", "Devops": "DevOps", "Pytorch": "PyTorch",
                    "Scikit-Learn": "scikit-learn", "Node.Js": "Node.js", "Vue.Js": "Vue.js",
                    "Next.Js": "Next.js", "Fastapi": "FastAPI",
                }
                canon = capitalization_map.get(canon, canon)
                if canon in detected_canonical:
                    matched_in_cat.append(canon)
                    assigned_skills.add(canon)
            if matched_in_cat:
                by_category[category_name] = sorted(list(set(matched_in_cat)))

        # Uncategorized detected skills (if any)
        uncategorized = sorted(list(detected_canonical - assigned_skills))
        if uncategorized:
            by_category["General & Domain Skills"] = uncategorized

        all_detected = sorted(list(detected_canonical))
        top_cats = sorted(
            [(cat, len(skills)) for cat, skills in by_category.items()],
            key=lambda x: x[1],
            reverse=True
        )

        return SkillExtractionResult(
            total_skills_count=len(all_detected),
            unique_skills_count=len(all_detected),
            skills_by_category=by_category,
            all_detected_skills=all_detected,
            top_categories=top_cats,
        )


# Shared singleton extractor instance
skill_extractor = SkillExtractor()
