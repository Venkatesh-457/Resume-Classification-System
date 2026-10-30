"""
Resume Intelligence Platform - Main Application Entry Point
Streamlit dashboard application orchestrating ingestion, NLP, classification,
ATS scoring, historical profile analytics, and PDF reporting.
"""

import streamlit as st
from config.settings import APP_NAME, APP_SUBTITLE, APP_VERSION
from ui.styles import apply_theme
from data_access.profile_repository import ProfileRepository
from core.classification.predictor import resume_classifier
from core.ingestion.ocr import ocr_engine

from ui.dashboard import render_dashboard
from ui.analyzer import render_analyzer
from ui.job_match import render_job_match
from ui.history import render_history
from ui.reports import render_reports


def main():
    # 1. Page Configuration
    st.set_page_config(
        page_title=f"{APP_NAME} | Enterprise Resume Intelligence",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 2. Inject Enterprise CSS Theme
    apply_theme()

    # 3. Sidebar Setup
    with st.sidebar:
        st.markdown(f"### 📄 {APP_NAME}")
        st.caption(f"{APP_SUBTITLE} • v{APP_VERSION}")
        st.markdown("---")

        # Profile Selector & Switcher
        st.markdown("#### 👤 Local User Profile")
        profiles = ProfileRepository.list_profiles()
        active_profile = ProfileRepository.get_active_profile()

        profile_names = [p["name"] for p in profiles]
        active_idx = profile_names.index(active_profile["name"]) if active_profile["name"] in profile_names else 0

        selected_profile_name = st.selectbox(
            "Active Profile",
            profile_names,
            index=active_idx,
            help="Switch between independent local profiles. Each profile maintains its own isolated analysis history.",
        )

        if selected_profile_name != active_profile["name"]:
            # Find ID and switch
            for p in profiles:
                if p["name"] == selected_profile_name:
                    ProfileRepository.set_active_profile(p["id"])
                    st.rerun()

        # Create New Profile Expander
        with st.expander("➕ Create New Profile"):
            new_profile_name = st.text_input("Profile Name", placeholder="e.g. John Doe / HR Demo")
            if st.button("Add Profile", use_container_width=True):
                if new_profile_name.strip():
                    try:
                        new_id = ProfileRepository.create_profile(new_profile_name.strip())
                        ProfileRepository.set_active_profile(new_id)
                        st.success(f"Profile '{new_profile_name}' created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Please enter a valid profile name.")

        st.markdown("---")

        # Main Navigation
        st.markdown("#### 🧭 Navigation")
        nav_selection = st.radio(
            "Select Destination",
            [
                "📊 Overview Dashboard",
                "📄 Resume Analyzer",
                "🎯 Job Match Studio",
                "📜 Analysis History",
                "📑 PDF Reports",
            ],
            index=0,
            label_visibility="collapsed",
        )

        st.markdown("---")

        # System Health Status Cards
        st.markdown("#### ⚙️ System Status")
        if resume_classifier.is_ready:
            st.markdown('<span class="badge-success">● NLP Model Ready</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-danger">● Model Artifacts Missing</span>', unsafe_allow_html=True)

        if ocr_engine.is_available:
            st.markdown(f'<span class="badge-success">● OCR Engine Ready (v{ocr_engine.version})</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-warning">● OCR Fallback Inactive</span>', unsafe_allow_html=True)

        st.caption("Windows Sandbox Mode • Local Execution")

    # 4. Route to Selected Page
    active_profile = ProfileRepository.get_active_profile()

    if nav_selection == "📊 Overview Dashboard":
        render_dashboard(active_profile)
    elif nav_selection == "📄 Resume Analyzer":
        render_analyzer(active_profile)
    elif nav_selection == "🎯 Job Match Studio":
        render_job_match(active_profile)
    elif nav_selection == "📜 Analysis History":
        render_history(active_profile)
    elif nav_selection == "📑 PDF Reports":
        render_reports(active_profile)


if __name__ == "__main__":
    main()
