"""
PDF Reports Hub View
Allows users to browse, generate, and download professional PDF reports
associated with their historical analyses.
"""

import streamlit as st
from data_access.analysis_repository import AnalysisRepository
from core.reporting.pdf_generator import pdf_report_generator


def render_reports(active_profile: dict) -> None:
    """Render the PDF Reports Hub page."""
    profile_id = active_profile["id"]
    profile_name = active_profile["name"]

    st.markdown("## 📑 PDF Audit Reports Repository")
    st.markdown(f"Generate and download official PDF audit reports for analyses saved under: **{profile_name}**")

    records = AnalysisRepository.get_analyses_by_profile(profile_id, sort_by="date_desc")

    if not records:
        st.info("No recorded analyses found for this profile. Analyze a resume to generate downloadable PDF reports.")
        return

    st.markdown(f"Available Reports: **{len(records)}**")

    for rec in records:
        with st.container():
            col1, col2, col3, col4 = st.columns([2.5, 1.8, 1.2, 1.5])
            with col1:
                st.markdown(f"**{rec['filename']}**")
                st.caption(f"ID: #{rec['id']} • {str(rec['created_at'])[:16]}")
            with col2:
                st.markdown(f"Category: **{rec['predicted_category']}**")
                st.caption(f"Confidence: {rec['confidence']*100:.1f}%")
            with col3:
                badge_class = "badge-success" if rec['ats_score'] >= 75 else "badge-warning"
                st.markdown(f"<span class='{badge_class}'>{rec['ats_score']:.0f} pts</span>", unsafe_allow_html=True)
                st.caption(rec['ats_grade'])
            with col4:
                pdf_bytes = pdf_report_generator.generate_report(rec)
                clean_name = rec['filename'].replace(' ', '_').split('.')[0]
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name=f"Report_{rec['id']}_{clean_name}.pdf",
                    mime="application/pdf",
                    key=f"rep_hub_{rec['id']}",
                )
            st.divider()
