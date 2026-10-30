"""
Analysis History & Comparison View
Provides searchable, filterable historical record management,
side-by-side comparative analytics, PDF report generation for past analyses, and deletion.
"""

import streamlit as st
import pandas as pd
from data_access.analysis_repository import AnalysisRepository
from core.analytics.metrics_aggregator import MetricsAggregator
from core.reporting.pdf_generator import pdf_report_generator
from config.settings import TARGET_CATEGORIES


def render_history(active_profile: dict) -> None:
    """Render the historical analyses and comparison laboratory."""
    profile_id = active_profile["id"]
    profile_name = active_profile["name"]

    st.markdown("## 📜 Analysis History & Comparison Studio")
    st.markdown(f"Manage previous evaluations and compare resumes for profile: **{profile_name}**")

    # Filters and Search Bar
    col_search, col_cat, col_score, col_sort = st.columns([2, 1.5, 1, 1.2])

    with col_search:
        search_query = st.text_input("🔍 Search by Filename", placeholder="Type keyword...")

    with col_cat:
        cat_filter = st.selectbox("Category Filter", ["All Categories"] + TARGET_CATEGORIES)

    with col_score:
        min_score = st.slider("Min ATS Score", 0, 100, 0, step=5)

    with col_sort:
        sort_by = st.selectbox(
            "Sort Order",
            ["date_desc", "date_asc", "score_desc", "score_asc"],
            format_func=lambda x: {
                "date_desc": "Newest First",
                "date_asc": "Oldest First",
                "score_desc": "Highest Score",
                "score_asc": "Lowest Score",
            }.get(x, x),
        )

    # Fetch records strictly for active profile
    records = AnalysisRepository.get_analyses_by_profile(
        profile_id=profile_id,
        category=cat_filter,
        min_score=float(min_score),
        search_query=search_query,
        sort_by=sort_by,
    )

    st.markdown(f"Found **{len(records)}** recorded analysis / analyses.")

    if not records:
        st.info("No matching records found for the selected filter criteria.")
        return

    # Tabs: History Table vs Side-by-Side Comparison
    tab_list, tab_compare = st.tabs(["📋 Analysis Archive", "⚖️ Side-by-Side Comparison"])

    with tab_list:
        # Render historical cards
        for rec in records:
            with st.expander(f"📄 {rec['filename']} — {rec['predicted_category']} (Score: {rec['ats_score']:.0f}/100) — {str(rec['created_at'])[:16]}"):
                c1, c2, c3 = st.columns([1.5, 1.5, 1])

                with c1:
                    st.write(f"**Predicted Category:** {rec['predicted_category']}")
                    st.write(f"**Confidence:** {rec['confidence']*100:.1f}% ({rec['score_type']})")
                    st.write(f"**Format:** {rec['file_format']} ({rec['extraction_method']})")
                    st.write(f"**Words:** {rec['word_count']} | **Pages:** {rec['page_count']}")

                with c2:
                    st.write(f"**ATS Score:** {rec['ats_score']:.0f} / 100 ({rec['ats_grade']})")
                    skills = (rec.get("skills_detected") or {}).get("all_detected_skills") or []
                    st.write(f"**Skills Detected ({len(skills)}):** {', '.join(skills[:8])}{'...' if len(skills) > 8 else ''}")
                    if rec.get("warnings"):
                        st.caption(f"⚠️ Warnings: {'; '.join(rec['warnings'])}")

                with c3:
                    # PDF Download Action
                    pdf_bytes = pdf_report_generator.generate_report(rec)
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_bytes,
                        file_name=f"Report_{rec['id']}_{rec['filename'].split('.')[0]}.pdf",
                        mime="application/pdf",
                        key=f"dl_{rec['id']}",
                    )

                    # Delete Action
                    if st.button("🗑️ Delete", key=f"del_{rec['id']}"):
                        AnalysisRepository.delete_analysis(rec["id"], profile_id)
                        st.toast("Record deleted successfully.")
                        st.rerun()

        # Clear All History Action with Confirmation
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("⚠️ Danger Zone: Clear History"):
            st.warning("This will permanently remove all analysis records for the current profile.")
            if st.button("🚨 Clear All Profile Records", type="secondary"):
                AnalysisRepository.clear_profile_history(profile_id)
                st.success("All profile history has been cleared.")
                st.rerun()

    with tab_compare:
        st.markdown("### Side-by-Side Resume Comparative Studio")
        st.markdown("Select two resumes from your history to evaluate score differentials, section coverage, and skills overlap.")

        if len(records) < 2:
            st.info("You need at least 2 saved resumes in this profile to use comparative analytics.")
        else:
            rec_options = {f"{r['id']}: {r['filename']} ({r['ats_score']:.0f} pts)": r["id"] for r in records}
            c_sel1, c_sel2 = st.columns(2)
            with c_sel1:
                id1_label = st.selectbox("Select Baseline Resume (A)", list(rec_options.keys()), index=0)
                id1 = rec_options[id1_label]
            with c_sel2:
                id2_label = st.selectbox("Select Comparison Resume (B)", list(rec_options.keys()), index=min(1, len(records)-1))
                id2 = rec_options[id2_label]

            if id1 == id2:
                st.warning("Please choose two distinct resumes to compute meaningful comparison analytics.")
            else:
                comp_data = MetricsAggregator.compare_analyses(id1, id2, profile_id)
                if comp_data:
                    r1 = comp_data["resume_1"]
                    r2 = comp_data["resume_2"]
                    delta = comp_data["score_delta"]

                    delta_color = "#10B981" if delta > 0 else "#EF4444" if delta < 0 else "#94A3B8"
                    delta_symbol = f"+{delta:.1f}" if delta > 0 else f"{delta:.1f}"

                    st.markdown(f"""
                        <div class="intel-card" style="text-align: center;">
                            <div style="font-size: 0.9rem; color: #94A3B8;">ATS Score Differential (B vs A)</div>
                            <div style="font-size: 2.2rem; font-weight: 800; color: {delta_color};">{delta_symbol} Points</div>
                        </div>
                    """, unsafe_allow_html=True)

                    # Summary Comparison Table
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"#### 📄 Resume A: {r1['filename']}")
                        st.write(f"• **Category:** {r1['predicted_category']}")
                        st.write(f"• **Score:** {r1['ats_score']:.0f} / 100 ({r1['ats_grade']})")
                        st.write(f"• **Word Count:** {r1['word_count']} words")
                        st.write(f"• **Unique Skills:** {', '.join(comp_data['unique_to_resume_1'][:6]) or 'None'}")

                    with col_b:
                        st.markdown(f"#### 📄 Resume B: {r2['filename']}")
                        st.write(f"• **Category:** {r2['predicted_category']}")
                        st.write(f"• **Score:** {r2['ats_score']:.0f} / 100 ({r2['ats_grade']})")
                        st.write(f"• **Word Count:** {r2['word_count']} words")
                        st.write(f"• **Unique Skills:** {', '.join(comp_data['unique_to_resume_2'][:6]) or 'None'}")

                    # Common Skills Overlap
                    st.markdown(f"**Shared Skills ({len(comp_data['common_skills'])}):** {', '.join(comp_data['common_skills']) or 'No overlap'}")
