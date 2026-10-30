"""
Automated Tests for Persistence & Profile Isolation Layer
Covers profile creation, switching, CRUD analyses, profile isolation, and deletion.
"""

import uuid
import pytest
from data_access.profile_repository import ProfileRepository
from data_access.analysis_repository import AnalysisRepository


def test_profile_creation_and_switching():
    unique_suffix = str(uuid.uuid4())[:8]
    profile_name = f"Test Profile {unique_suffix}"
    new_id = ProfileRepository.create_profile(profile_name)
    assert new_id > 0

    try:
        ProfileRepository.set_active_profile(new_id)
        active = ProfileRepository.get_active_profile()
        assert active["id"] == new_id
        assert active["name"] == profile_name
    finally:
        # Switch back to first profile and clean up test profile
        profiles = ProfileRepository.list_profiles()
        other = [p for p in profiles if p["id"] != new_id]
        if other:
            ProfileRepository.set_active_profile(other[0]["id"])
            ProfileRepository.delete_profile(new_id)


def test_analysis_persistence_and_profile_isolation():
    u = str(uuid.uuid4())[:8]
    p1_id = ProfileRepository.create_profile(f"Profile Alpha {u}")
    p2_id = ProfileRepository.create_profile(f"Profile Beta {u}")

    try:
        # Save analysis in Profile Alpha
        record_alpha = {
            "filename": "alpha_resume.pdf",
            "file_format": "PDF",
            "extraction_method": "Digital",
            "predicted_category": "Software Developer",
            "confidence": 0.95,
            "ats_score": 88.0,
            "ats_grade": "A",
            "raw_text": "Sample Alpha resume text",
        }
        a_id = AnalysisRepository.save_analysis(p1_id, record_alpha)
        assert a_id > 0

        # Verify Profile Alpha sees it
        alpha_records = AnalysisRepository.get_analyses_by_profile(p1_id)
        assert len(alpha_records) >= 1
        assert any(r["id"] == a_id for r in alpha_records)

        # CRITICAL TEST: Verify Profile Beta CANNOT see Profile Alpha's record
        beta_records = AnalysisRepository.get_analyses_by_profile(p2_id)
        assert not any(r["id"] == a_id for r in beta_records)

    finally:
        # Clean up test profiles
        AnalysisRepository.clear_profile_history(p1_id)
        ProfileRepository.delete_profile(p1_id)
        ProfileRepository.delete_profile(p2_id)
