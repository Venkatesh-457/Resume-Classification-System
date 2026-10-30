"""
Job Match Studio View
Allows users to evaluate candidate resume alignment against a target job description.
Provides match score, matched vs missing skills, keyword overlap, and tailoring advice.
"""

import streamlit as st
from core.scoring.job_matcher import calculate_job_match
from data_access.analysis_repository import AnalysisRepository
from core.features.tfidf_builder import load_vectorizer


def render_job_match(active_profile: dict) -> None:
    """Render the Job Match Studio page."""
    profile_id = active_profile["id"]

    st.markdown("## 🎯 Job Match Studio")
    st.markdown(
        "Analyze how well a candidate's resume aligns with a specific job description. "
        "The matching engine evaluates **technical skill coverage (40%)**, "
        "**semantic TF-IDF similarity (35%)**, and **domain keyword overlap (25%)**."
    )

    # 1. Select Resume Source
    st.markdown("### Step 1: Select or Provide Candidate Resume")
    resume_source = st.radio(
        "Resume Source",
        ["Use Current Analyzed Resume", "Select from Saved Profile History", "Paste Resume Text"],
        horizontal=True,
    )

    resume_text = ""
    resume_title = ""

    if resume_source == "Use Current Analyzed Resume":
        resume_text = st.session_state.get("latest_raw_text", "")
        if not resume_text:
            st.info("No resume is currently loaded in memory. Upload one in 'Resume Analyzer' or select another option above.")
        else:
            resume_title = st.session_state.get("latest_analysis", {}).get("filename", "Current Resume")
            st.success(f"Using loaded resume: **{resume_title}** ({len(resume_text.split())} words)")

    elif resume_source == "Select from Saved Profile History":
        history = AnalysisRepository.get_analyses_by_profile(profile_id)
        if not history:
            st.info("No saved analyses found in this profile. Please upload a resume first.")
        else:
            options = {f"{h['id']} - {h['filename']} ({h['predicted_category']})": h for h in history}
            selected_label = st.selectbox("Choose Saved Resume", list(options.keys()))
            selected_record = options[selected_label]
            resume_text = selected_record.get("raw_text_snippet", "")
            resume_title = selected_record["filename"]
            st.caption(f"Loaded: {resume_title}")

    else:
        resume_text = st.text_area("Paste Candidate Resume Text", height=200, placeholder="Paste plain text resume content here...")
        resume_title = "Pasted Resume Text"

    # 2. Job Description Input
    st.markdown("### Step 2: Paste Target Job Description")
    job_desc = st.text_area(
        "Job Description Text",
        height=220,
        placeholder="Paste full job posting, role responsibilities, and required qualification requirements here...",
    )

    if st.button("🚀 Analyze Alignment & Match Score", type="primary"):
        if not resume_text.strip():
            st.error("Please supply resume text before matching.")
            return
        if not job_desc.strip():
            st.error("Please supply a job description to compare against.")
            return

        with st.spinner("Calculating semantic similarity, skill coverage, and keyword alignment..."):
            try:
                vec = load_vectorizer()
            except Exception:
                vec = None

            match_res = calculate_job_match(resume_text, job_desc, vectorizer=vec)

        # Match Score Display
        st.markdown("<br>", unsafe_allow_html=True)
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

        with col_m1:
            score_col = "#10B981" if match_res.match_score >= 75 else "#38BDF8" if match_res.match_score >= 50 else "#F59E0B"
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">Job Match Score</div>
                    <div class="metric-val" style="color: {score_col};">{match_res.match_score:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

        with col_m2:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">Required Skill Coverage</div>
                    <div class="metric-val">{match_res.skill_coverage_percentage:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

        with col_m3:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">Semantic Cosine Sim</div>
                    <div class="metric-val">{match_res.semantic_similarity_percentage:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

        with col_m4:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">Vocabulary Overlap</div>
                    <div class="metric-val">{match_res.keyword_overlap_percentage:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown(f"<p style='text-align: center; color: #94A3B8; margin-top: 10px;'>Alignment Verdict: <b>{match_res.grade}</b></p>", unsafe_allow_html=True)

        # Matched vs Missing Skills Cards
        col_matched, col_missing = st.columns(2)

        with col_matched:
            st.markdown('<div class="intel-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="intel-card-header">✅ Matched Technical Skills ({len(match_res.matched_skills)})</div>', unsafe_allow_html=True)
            if match_res.matched_skills:
                pills = " ".join([f"<span class='skill-pill'>{s}</span>" for s in match_res.matched_skills])
                st.markdown(pills, unsafe_allow_html=True)
            else:
                st.write("No direct taxonomy skill overlaps identified.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_missing:
            st.markdown('<div class="intel-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="intel-card-header">⚠️ Missing Target Skills ({len(match_res.missing_skills)})</div>', unsafe_allow_html=True)
            if match_res.missing_skills:
                pills = " ".join([f"<span class='skill-pill-alt'>{s}</span>" for s in match_res.missing_skills])
                st.markdown(pills, unsafe_allow_html=True)
            else:
                st.write("Excellent! Candidate satisfies all detected skill requirements.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Tailored Improvement Advice
        st.markdown('<div class="intel-card">', unsafe_allow_html=True)
        st.markdown('<div class="intel-card-header">💡 Role-Specific Optimization Advice</div>', unsafe_allow_html=True)
        for rec in match_res.tailored_recommendations:
            st.markdown(f"• {rec}")
        st.markdown('</div>', unsafe_allow_html=True)
