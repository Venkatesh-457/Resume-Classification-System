"""
Resume Analyzer View
Handles document upload, text extraction, OCR fallback, classification,
ATS scoring, skill detection, section coverage audit, and immediate PDF download.
"""

import streamlit as st
from core.ingestion.parser import document_parser, DocumentParsingError
from core.ingestion.validator import resume_validator, ResumeValidationDecision
from core.classification.predictor import resume_classifier
from core.features.skill_extractor import skill_extractor
from core.scoring.ats_scorer import calculate_ats_score
from core.reporting.pdf_generator import pdf_report_generator
from data_access.analysis_repository import AnalysisRepository


def render_analyzer(active_profile: dict) -> None:
    """Render the interactive resume analyzer page."""
    profile_id = active_profile["id"]
    profile_name = active_profile["name"]

    st.markdown("## 📄 Resume Analyzer & ATS Audit Engine")
    st.markdown(
        "Upload a candidate resume in **PDF, DOCX, or TXT** format. "
        "The system parses text (with OCR fallback for scans), predicts the job category, "
        "calculates an explainable ATS quality score, extracts technical skills, and produces an executive PDF report."
    )

    uploaded_file = st.file_uploader(
        "Select Resume Document",
        type=["pdf", "docx", "txt"],
        help="Upload digital PDF, scanned PDF, Word document (.docx), or plain text (.txt). Max size: 10 MB.",
    )

    if not uploaded_file:
        st.info("👆 Please upload a resume file above to begin the analysis.")
        return

    # Trigger analysis on file upload
    with st.spinner("Ingesting document and running NLP analysis pipeline..."):
        file_bytes = uploaded_file.read()
        filename = uploaded_file.name

        try:
            # 1. Document Extraction
            extraction_res = document_parser.parse_file(file_bytes, filename)
        except DocumentParsingError as e:
            st.error(f"❌ Extraction Error: {e}")
            return
        except Exception as e:
            st.error(f"❌ Unexpected processing error: {e}")
            return

        raw_text = extraction_res.raw_text

        # 2. Resume Document Content Validation (Stage 2)
        val_res = resume_validator.validate(raw_text, filename=filename)

        if val_res.decision == ResumeValidationDecision.NOT_A_RESUME:
            st.error(f"❌ {val_res.message}")
            if val_res.reasons:
                with st.expander("🔍 Diagnostic Details"):
                    st.markdown("**Why was this document rejected?**")
                    for reason in val_res.reasons:
                        st.markdown(f"- {reason}")
                    st.caption(f"Document Confidence Score: {val_res.confidence_score:.1f}/100.0 (Threshold: 40.0)")
            return

        elif val_res.decision == ResumeValidationDecision.UNCERTAIN_DOCUMENT:
            st.warning(f"⚠️ {val_res.message}")
            if val_res.reasons:
                with st.expander("🔍 Diagnostic Details"):
                    st.markdown("**Observations:**")
                    for reason in val_res.reasons:
                        st.markdown(f"- {reason}")
                    st.caption(f"Document Confidence Score: {val_res.confidence_score:.1f}/100.0 (Uncertain Range: 25.0 - 39.9)")
            return

        # 3. Skill Extraction (Stage 3)
        skill_res = skill_extractor.extract_skills(raw_text)

        # 4. Model Classification
        if resume_classifier.is_ready:
            clf_res = resume_classifier.predict(raw_text)
        else:
            st.error("⚠️ Classification model is not loaded. Please ensure trained model artifacts are present.")
            return

        # 5. ATS Resume Quality Scoring
        ats_res = calculate_ats_score(raw_text, skill_result=skill_res)

        # 5. Persist Analysis to SQLite (Associated with active profile)
        analysis_record = {
            "filename": filename,
            "file_format": extraction_res.file_format,
            "extraction_method": extraction_res.extraction_method,
            "ocr_used": extraction_res.ocr_used,
            "page_count": extraction_res.page_count,
            "word_count": extraction_res.word_count,
            "predicted_category": clf_res.predicted_category,
            "confidence": clf_res.confidence,
            "is_calibrated": clf_res.is_calibrated,
            "score_type": clf_res.score_type,
            "alternative_predictions": [
                {"category": alt.category, "confidence": alt.confidence, "percentage": alt.percentage}
                for alt in clf_res.alternative_predictions
            ],
            "ats_score": ats_res.total_score,
            "ats_grade": ats_res.grade,
            "score_breakdown": ats_res.breakdown.to_dict(),
            "skills_detected": {
                "total_count": skill_res.total_skills_count,
                "all_detected_skills": skill_res.all_detected_skills,
                "skills_by_category": skill_res.skills_by_category,
            },
            "section_coverage": ats_res.detected_sections,
            "warnings": extraction_res.warnings + clf_res.warnings,
            "recommendations": ats_res.recommendations,
            "raw_text": raw_text,
        }

        # Store in session state to enable instant download
        st.session_state["latest_analysis"] = analysis_record
        st.session_state["latest_raw_text"] = raw_text

        # Save to database if not already saved in this session run
        last_saved = st.session_state.get("last_saved_file")
        if last_saved != filename:
            saved_id = AnalysisRepository.save_analysis(profile_id, analysis_record)
            st.session_state["last_saved_file"] = filename
            st.session_state["latest_analysis"]["id"] = saved_id

    # Display Results
    st.success(f"✅ Document successfully parsed and evaluated for profile: **{profile_name}**")

    # Document Ingestion Metadata Pill Row
    st.markdown(f"""
        <div style="background: #131D31; border: 1px solid #2A3950; border-radius: 8px; padding: 12px 18px; margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 20px; font-size: 0.85rem;">
            <div><span style="color: #94A3B8;">Format:</span> <b>{extraction_res.file_format}</b></div>
            <div><span style="color: #94A3B8;">Method:</span> <b>{extraction_res.extraction_method}</b></div>
            <div><span style="color: #94A3B8;">Length:</span> <b>{extraction_res.word_count} words ({extraction_res.page_count} page(s))</b></div>
            <div><span style="color: #94A3B8;">OCR Used:</span> <b>{'Yes' if extraction_res.ocr_used else 'No'}</b></div>
            <div><span style="color: #94A3B8;">Status:</span> <span class="badge-success">Verified</span></div>
        </div>
    """, unsafe_allow_html=True)

    # Warnings Display (if any)
    all_warnings = extraction_res.warnings + clf_res.warnings
    if all_warnings:
        for w in all_warnings:
            st.warning(f"⚠️ {w}")

    # Two Main Hero Cards: Classification & ATS Score
    col_pred, col_score = st.columns([1, 1])

    with col_pred:
        st.markdown('<div class="intel-card">', unsafe_allow_html=True)
        st.markdown('<div class="intel-card-header">🎯 Predicted Job Category</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="category-highlight">{clf_res.predicted_category}</div>', unsafe_allow_html=True)
        st.markdown(
            f"<div style='color: #94A3B8; font-size: 0.85rem; margin: 6px 0 14px 0;'>"
            f"Confidence: <b style='color: #38BDF8;'>{clf_res.confidence_percentage:.1f}%</b> ({clf_res.score_type})<br>"
            f"Model: {clf_res.model_name}</div>",
            unsafe_allow_html=True
        )

        # Alternative Rankings
        if clf_res.alternative_predictions:
            st.markdown("<b style='font-size: 0.85rem; color: #F8FAFC;'>Alternative Candidate Classes:</b>", unsafe_allow_html=True)
            for alt in clf_res.alternative_predictions:
                st.write(f"• **{alt.category}**: {alt.percentage:.1f}%")
                st.progress(float(alt.confidence))

        # Top Contributing Vocabulary Terms
        if clf_res.top_contributing_terms:
            st.markdown("<br><b style='font-size: 0.85rem; color: #F8FAFC;'>Key Attribution Keywords:</b><br>", unsafe_allow_html=True)
            terms_html = " ".join([
                f"<span class='skill-pill'>{term}</span>"
                for term, _ in clf_res.top_contributing_terms[:6]
            ])
            st.markdown(terms_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_score:
        st.markdown('<div class="intel-card">', unsafe_allow_html=True)
        st.markdown('<div class="intel-card-header">⭐ ATS Resume Quality Score</div>', unsafe_allow_html=True)

        score_val = ats_res.total_score
        grade_color = "#10B981" if score_val >= 80 else "#38BDF8" if score_val >= 70 else "#F59E0B"
        st.markdown(f"""
            <div style="display: flex; align-items: baseline; gap: 14px; margin-bottom: 10px;">
                <div style="font-size: 3rem; font-weight: 800; color: {grade_color};">{score_val:.0f}</div>
                <div>
                    <span style="font-size: 1rem; color: #94A3B8;">/ 100</span><br>
                    <span class="badge-success" style="background: #1E3A8A; color: #93C5FD; font-size: 0.85rem;">{ats_res.grade}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<b style='font-size: 0.85rem; color: #F8FAFC;'>Score Component Breakdown:</b>", unsafe_allow_html=True)
        b = ats_res.breakdown
        components = [
            ("Structure & Readability", b.structure_readability, 15.0),
            ("Contact Information", b.contact_information, 15.0),
            ("Section Coverage", b.section_coverage, 20.0),
            ("Skills Depth & Taxonomy", b.skills_depth, 25.0),
            ("Quantifiable Metrics", b.quantifiable_metrics, 15.0),
            ("Action Verbs & Phrasing", b.action_verbs, 10.0),
        ]
        for name, pts, max_pts in components:
            pct = min(1.0, pts / max_pts)
            st.write(f"• **{name}**: {pts:.1f} / {max_pts:.0f} pts")
            st.progress(pct)

        st.markdown('</div>', unsafe_allow_html=True)

    # Detected Skills Categorized Card
    st.markdown('<div class="intel-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="intel-card-header">🛠️ Detected Technical Skills ({skill_res.total_skills_count} total detected)</div>', unsafe_allow_html=True)

    if skill_res.skills_by_category:
        for cat_name, skills_list in skill_res.skills_by_category.items():
            st.markdown(f"<b style='color: #94A3B8; font-size: 0.85rem;'>{cat_name}:</b>", unsafe_allow_html=True)
            pills = " ".join([f"<span class='skill-pill'>{s}</span>" for s in skills_list])
            st.markdown(pills + "<br>", unsafe_allow_html=True)
    else:
        st.write("No specialized technical skills were identified from the structured taxonomy.")

    st.markdown(f"<div style='color: #64748B; font-size: 0.75rem; margin-top: 10px;'>{skill_res.disclaimer}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Section Coverage & Actionable Recommendations Row
    col_sec, col_recs = st.columns([1, 1])

    with col_sec:
        st.markdown('<div class="intel-card">', unsafe_allow_html=True)
        st.markdown('<div class="intel-card-header">📋 Section Coverage Audit</div>', unsafe_allow_html=True)
        for sec_name, present in ats_res.detected_sections.items():
            icon = "✅" if present else "❌"
            status = "Present" if present else "<font color='#F87171'>Missing</font>"
            st.markdown(f"{icon} **{sec_name.title()}**: {status}", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_recs:
        st.markdown('<div class="intel-card">', unsafe_allow_html=True)
        st.markdown('<div class="intel-card-header">💡 Actionable Improvement Recommendations</div>', unsafe_allow_html=True)
        if ats_res.recommendations:
            for rec in ats_res.recommendations:
                st.markdown(f"• {rec}")
        else:
            st.markdown("✨ Exceptional resume structure and coverage! No major structural gaps identified.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Extracted Text Preview Expander
    with st.expander("🔍 View Extracted Document Text"):
        st.text_area("Normalized Extracted Text", value=raw_text, height=250, disabled=True)

    # Instant PDF Report Download Action
    st.markdown("<br>", unsafe_allow_html=True)
    pdf_bytes = pdf_report_generator.generate_report(st.session_state["latest_analysis"])

    report_filename = f"Resume_Intelligence_Report_{filename.replace(' ', '_').split('.')[0]}.pdf"
    st.download_button(
        label="📥 Download Executive PDF Audit Report",
        data=pdf_bytes,
        file_name=report_filename,
        mime="application/pdf",
        help="Generate and download a branded, publication-ready PDF evaluation report.",
    )
