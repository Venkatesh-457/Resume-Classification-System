"""
UI Styles & Theme Module
Defines enterprise visual identity: deep charcoal/navy palette,
teal/violet accents, modern cards, metrics, and pill badges.
"""

import streamlit as st


ENTERPRISE_CSS = """
<style>
/* Main Background & Typography */
.stApp {
    background-color: #0B1120;
    color: #F8FAFC;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #0F172A !important;
    border-right: 1px solid #1E293B !important;
}

/* Card Containers */
.intel-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -2px rgba(0, 0, 0, 0.2);
}

.intel-card-header {
    font-size: 1.05rem;
    font-weight: 600;
    color: #38BDF8;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1px solid #334155;
    padding-bottom: 8px;
}

/* Metric Display Cards */
.metric-box {
    background: #131D31;
    border: 1px solid #2A3950;
    border-radius: 8px;
    padding: 14px;
    text-align: center;
}

.metric-val {
    font-size: 1.8rem;
    font-weight: 700;
    color: #38BDF8;
    margin: 4px 0;
}

.metric-label {
    font-size: 0.8rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Skill Pills */
.skill-pill {
    display: inline-block;
    background: #1E293B;
    border: 1px solid #0284C7;
    color: #E0F2FE;
    font-size: 0.8rem;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 20px;
    margin: 3px;
    transition: all 0.2s ease;
}

.skill-pill-alt {
    display: inline-block;
    background: #2D1B4E;
    border: 1px solid #8B5CF6;
    color: #EDE9FE;
    font-size: 0.8rem;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 20px;
    margin: 3px;
}

/* Status Badges */
.badge-success {
    background: #064E3B;
    color: #6EE7B7;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-warning {
    background: #78350F;
    color: #FCD34D;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-danger {
    background: #7F1D1D;
    color: #FCA5A5;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* Category Highlight */
.category-highlight {
    font-size: 1.4rem;
    font-weight: 700;
    color: #38BDF8;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0F172A;
}
::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #475569;
}
</style>
"""


def apply_theme():
    """Inject custom enterprise CSS into Streamlit page."""
    st.markdown(ENTERPRISE_CSS, unsafe_allow_html=True)
