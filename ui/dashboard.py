"""
Overview Dashboard View
Displays profile metrics, interactive Plotly charts, category distributions,
score trends, frequently detected skills, and model health status.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from core.analytics.metrics_aggregator import MetricsAggregator
from data_access.profile_repository import ProfileRepository
from core.classification.predictor import resume_classifier


def render_dashboard(active_profile: dict) -> None:
    """Render the main executive analytical dashboard for the active profile."""
    profile_id = active_profile["id"]
    profile_name = active_profile["name"]

    st.markdown(f"## 📊 Executive Dashboard")
    st.markdown(f"Welcome back! Viewing analytics for active profile: **{profile_name}**")

    metrics = MetricsAggregator.get_profile_dashboard_metrics(profile_id)
    total_analyses = metrics["total_analyses"]

    # Top KPI Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Total Resumes Analyzed</div>
                <div class="metric-val">{total_analyses}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        avg_score = metrics["avg_ats_score"]
        score_color = "#10B981" if avg_score >= 75 else "#38BDF8" if avg_score >= 60 else "#F59E0B"
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Average ATS Score</div>
                <div class="metric-val" style="color: {score_color}">{avg_score:.1f}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Highest Score</div>
                <div class="metric-val">{metrics['highest_ats_score']:.1f}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        model_status = "Active & Calibrated" if resume_classifier.is_ready else "Not Loaded"
        status_color = "#10B981" if resume_classifier.is_ready else "#EF4444"
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">NLP Model Engine</div>
                <div class="metric-val" style="font-size: 1.1rem; color: {status_color}; margin-top: 12px;">{model_status}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if total_analyses == 0:
        # Polished Empty State for New Profiles
        st.markdown("""
            <div class="intel-card" style="text-align: center; padding: 45px 20px;">
                <h3 style="color: #38BDF8; margin-bottom: 8px;">No Resumes Analyzed Yet in This Profile</h3>
                <p style="color: #94A3B8; max-width: 580px; margin: 0 auto 20px auto;">
                    This profile currently has no recorded resume analyses. Upload your first PDF, DOCX, or TXT
                    document in the <b>Resume Analyzer</b> tab to evaluate category predictions, ATS scores, and technical skills.
                </p>
            </div>
        """, unsafe_allow_html=True)
        return

    # Charts Row 1: Category Distribution & Score Trajectory
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown('<div class="intel-card">', unsafe_allow_html=True)
        st.markdown('<div class="intel-card-header">📂 Predicted Category Breakdown</div>', unsafe_allow_html=True)
        cat_counts = metrics["category_counts"]
        if cat_counts:
            fig_pie = px.pie(
                names=list(cat_counts.keys()),
                values=list(cat_counts.values()),
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Dark24,
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=300,
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No category data available.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_chart2:
        st.markdown('<div class="intel-card">', unsafe_allow_html=True)
        st.markdown('<div class="intel-card-header">📈 ATS Quality Score Trajectory</div>', unsafe_allow_html=True)
        trends = metrics["score_trend"]
        if len(trends) > 1:
            df_trend = [
                {"Index": i + 1, "Score": t["score"], "Filename": t["filename"], "Date": t["date"]}
                for i, t in enumerate(trends)
            ]
            fig_line = px.line(
                df_trend,
                x="Index",
                y="Score",
                markers=True,
                hover_data=["Filename", "Date"],
                color_discrete_sequence=["#0EA5E9"],
            )
            fig_line.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC"),
                yaxis=dict(range=[0, 100], gridcolor="#334155"),
                xaxis=dict(gridcolor="#334155", title="Analysis Sequence"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=300,
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.markdown("""
                <div style="height: 300px; display: flex; align-items: center; justify-content: center; color: #94A3B8;">
                    Analyze at least 2 resumes to visualize your quality score progression over time.
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Charts Row 2: Frequently Detected Skills & Recent Activity
    col_chart3, col_chart4 = st.columns([1, 1])

    with col_chart3:
        st.markdown('<div class="intel-card">', unsafe_allow_html=True)
        st.markdown('<div class="intel-card-header">🛠️ Most Detected Technical Skills</div>', unsafe_allow_html=True)
        top_skills = metrics["top_skills"]
        if top_skills:
            skill_names = [s[0] for s in top_skills]
            skill_freqs = [s[1] for s in top_skills]
            fig_bar = px.bar(
                x=skill_freqs,
                y=skill_names,
                orientation="h",
                color=skill_freqs,
                color_continuous_scale="Teal",
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC"),
                xaxis=dict(title="Occurrences", gridcolor="#334155"),
                yaxis=dict(autorange="reversed", gridcolor="#334155"),
                coloraxis_showscale=False,
                margin=dict(t=10, b=10, l=10, r=10),
                height=320,
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No skill data detected yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_chart4:
        st.markdown('<div class="intel-card">', unsafe_allow_html=True)
        st.markdown('<div class="intel-card-header">⏱️ Recent Analyses</div>', unsafe_allow_html=True)
        recents = metrics["recent_analyses"]
        if recents:
            for r in recents:
                score_badge_class = "badge-success" if r["ats_score"] >= 75 else "badge-warning"
                st.markdown(f"""
                    <div style="background: #131D31; border: 1px solid #2A3950; border-radius: 6px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 600; color: #F8FAFC;">{r['filename']}</div>
                            <div style="font-size: 0.78rem; color: #94A3B8;">
                                {r['predicted_category']} • {str(r['created_at'])[:16]}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <span class="{score_badge_class}">{r['ats_score']:.0f} / 100</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
