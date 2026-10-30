"""
Analysis Repository Module
Provides CRUD operations for resume analyses, strictly isolated by profile_id.
Handles JSON serialization/deserialization, query filtering, and search.
"""

import json
import logging
from typing import Any
from data_access.database import get_connection

logger = logging.getLogger(__name__)


def _parse_row(row: Any) -> dict:
    """Helper to convert sqlite3.Row to dict and parse JSON fields."""
    d = dict(row)
    json_fields = [
        "alternative_predictions_json",
        "score_breakdown_json",
        "skills_detected_json",
        "section_coverage_json",
        "warnings_json",
        "recommendations_json",
        "job_match_details_json",
    ]
    for field in json_fields:
        raw_val = d.get(field)
        if raw_val:
            try:
                d[field.replace("_json", "")] = json.loads(raw_val)
            except Exception:
                d[field.replace("_json", "")] = None
        else:
            d[field.replace("_json", "")] = None
    return d


class AnalysisRepository:
    """Repository for persisted resume analyses."""

    @staticmethod
    def save_analysis(profile_id: int, data: dict) -> int:
        """
        Persist a completed analysis record associated with a specific profile.
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO analyses (
                    profile_id, filename, file_format, extraction_method, ocr_used,
                    page_count, word_count, predicted_category, confidence, is_calibrated,
                    score_type, alternative_predictions_json, ats_score, ats_grade,
                    score_breakdown_json, skills_detected_json, section_coverage_json,
                    warnings_json, recommendations_json, job_description_snippet,
                    job_match_score, job_match_details_json, raw_text_snippet
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                );
            """

            # Limit raw snippet to first 1200 characters for privacy and lightweight storage
            raw_snippet = data.get("raw_text", "")[:1200]
            if len(data.get("raw_text", "")) > 1200:
                raw_snippet += " ... [truncated]"

            params = (
                profile_id,
                data.get("filename", "unknown.pdf"),
                data.get("file_format", "PDF"),
                data.get("extraction_method", "Digital"),
                1 if data.get("ocr_used") else 0,
                data.get("page_count", 1),
                data.get("word_count", 0),
                data.get("predicted_category", "Unclassified"),
                data.get("confidence", 0.0),
                1 if data.get("is_calibrated", True) else 0,
                data.get("score_type", "Calibrated Probability"),
                json.dumps(data.get("alternative_predictions", [])),
                data.get("ats_score", 0.0),
                data.get("ats_grade", "Needs Improvement"),
                json.dumps(data.get("score_breakdown", {})),
                json.dumps(data.get("skills_detected", {})),
                json.dumps(data.get("section_coverage", {})),
                json.dumps(data.get("warnings", [])),
                json.dumps(data.get("recommendations", [])),
                data.get("job_description_snippet", None),
                data.get("job_match_score", None),
                json.dumps(data.get("job_match_details", {})) if data.get("job_match_details") else None,
                raw_snippet,
            )

            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_analyses_by_profile(
        profile_id: int,
        category: str | None = None,
        min_score: float | None = None,
        search_query: str | None = None,
        sort_by: str = "date_desc",
    ) -> list[dict]:
        """
        Retrieve analyses filtered by owning profile_id with search, filter, and sort options.
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            conditions = ["profile_id = ?"]
            params: list[Any] = [profile_id]

            if category and category != "All Categories":
                conditions.append("predicted_category = ?")
                params.append(category)

            if min_score is not None and min_score > 0:
                conditions.append("ats_score >= ?")
                params.append(min_score)

            if search_query and search_query.strip():
                conditions.append("(filename LIKE ? OR predicted_category LIKE ?)")
                term = f"%{search_query.strip()}%"
                params.extend([term, term])

            order_clause = {
                "date_desc": "created_at DESC",
                "date_asc": "created_at ASC",
                "score_desc": "ats_score DESC",
                "score_asc": "ats_score ASC",
            }.get(sort_by, "created_at DESC")

            query = f"""
                SELECT * FROM analyses
                WHERE {' AND '.join(conditions)}
                ORDER BY {order_clause};
            """

            cursor.execute(query, params)
            return [_parse_row(row) for row in cursor.fetchall()]

    @staticmethod
    def get_analysis_by_id(analysis_id: int, profile_id: int) -> dict | None:
        """Fetch a specific analysis while enforcing profile isolation."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM analyses WHERE id = ? AND profile_id = ? LIMIT 1;",
                (analysis_id, profile_id),
            )
            row = cursor.fetchone()
            return _parse_row(row) if row else None

    @staticmethod
    def delete_analysis(analysis_id: int, profile_id: int) -> bool:
        """Delete an analysis while strictly validating profile ownership."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM analyses WHERE id = ? AND profile_id = ?;",
                (analysis_id, profile_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def clear_profile_history(profile_id: int) -> int:
        """Clear all historical analysis records for a specific profile."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM analyses WHERE profile_id = ?;", (profile_id,))
            conn.commit()
            return cursor.rowcount
