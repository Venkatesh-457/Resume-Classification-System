"""
Analytics & Metrics Aggregator Module
Computes historical analytics, category distributions, score trends,
frequent skill statistics, and side-by-side comparison matrices for local user profiles.
"""

from collections import Counter
import logging
from data_access.analysis_repository import AnalysisRepository

logger = logging.getLogger(__name__)


class MetricsAggregator:
    """Aggregates analytics strictly for the designated profile."""

    @staticmethod
    def get_profile_dashboard_metrics(profile_id: int) -> dict:
        """Calculate summary statistics for overview dashboard."""
        analyses = AnalysisRepository.get_analyses_by_profile(profile_id, sort_by="date_desc")
        total = len(analyses)

        if total == 0:
            return {
                "total_analyses": 0,
                "avg_ats_score": 0.0,
                "highest_ats_score": 0.0,
                "lowest_ats_score": 0.0,
                "category_counts": {},
                "score_trend": [],
                "top_skills": [],
                "recent_analyses": [],
            }

        scores = [a["ats_score"] for a in analyses]
        avg_score = round(sum(scores) / total, 1)
        highest_score = round(max(scores), 1)
        lowest_score = round(min(scores), 1)

        # Category distribution
        categories = [a["predicted_category"] for a in analyses]
        category_counts = dict(Counter(categories).most_common())

        # Score trend over time (chronological)
        chrono_analyses = list(reversed(analyses))
        score_trend = [
            {
                "id": a["id"],
                "filename": a["filename"],
                "score": a["ats_score"],
                "date": str(a["created_at"])[:16],
                "category": a["predicted_category"],
            }
            for a in chrono_analyses
        ]

        # Top detected skills across all profile analyses
        all_skills = []
        for a in analyses:
            skills_dict = a.get("skills_detected") or {}
            all_detected = skills_dict.get("all_detected_skills") or []
            all_skills.extend(all_detected)

        top_skills = Counter(all_skills).most_common(12)

        return {
            "total_analyses": total,
            "avg_ats_score": avg_score,
            "highest_ats_score": highest_score,
            "lowest_ats_score": lowest_score,
            "category_counts": category_counts,
            "score_trend": score_trend,
            "top_skills": top_skills,
            "recent_analyses": analyses[:5],
        }

    @staticmethod
    def compare_analyses(analysis_id_1: int, analysis_id_2: int, profile_id: int) -> dict | None:
        """Generate side-by-side comparison data between two historical analyses."""
        a1 = AnalysisRepository.get_analysis_by_id(analysis_id_1, profile_id)
        a2 = AnalysisRepository.get_analysis_by_id(analysis_id_2, profile_id)

        if not a1 or not a2:
            return None

        # Skills comparison
        s1 = set((a1.get("skills_detected") or {}).get("all_detected_skills") or [])
        s2 = set((a2.get("skills_detected") or {}).get("all_detected_skills") or [])

        common_skills = sorted(list(s1.intersection(s2)))
        unique_to_1 = sorted(list(s1 - s2))
        unique_to_2 = sorted(list(s2 - s1))

        # Score delta
        score_diff = round(a2["ats_score"] - a1["ats_score"], 1)

        return {
            "resume_1": a1,
            "resume_2": a2,
            "score_delta": score_diff,
            "common_skills": common_skills,
            "unique_to_resume_1": unique_to_1,
            "unique_to_resume_2": unique_to_2,
            "score_breakdown_diff": {
                k: round((a2.get("score_breakdown") or {}).get(k, 0) - (a1.get("score_breakdown") or {}).get(k, 0), 1)
                for k in (a1.get("score_breakdown") or {}).keys()
            }
        }
