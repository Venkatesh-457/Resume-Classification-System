"""
Unit tests for Resume Document Validation Engine
Tests valid resumes, fresher resumes, resumes lacking phone/experience,
scanned resumes, and non-resume documents (papers, essays, invoices, legal text, empty files).
"""

import pytest
from core.ingestion.validator import (
    ResumeValidator,
    ResumeValidationDecision,
    validate_resume_document
)


@pytest.fixture
def validator():
    return ResumeValidator()


def test_standard_software_developer_resume(validator):
    text = """
    Alex Mercer
    Email: alex.mercer@example.com | Phone: (555) 234-5678 | San Francisco, CA
    LinkedIn: linkedin.com/in/alexmercer | GitHub: github.com/alexm

    PROFESSIONAL SUMMARY
    Dedicated Full-Stack Software Engineer with 5+ years of experience designing and implementing
    scalable web applications, distributed microservices, and high-throughput REST APIs.

    WORK EXPERIENCE
    Senior Software Engineer | TechNova Solutions | 2021 – Present
    • Architected and deployed microservices handling 15M+ daily requests using Python, FastAPI, and Docker.
    • Optimized PostgreSQL query execution plans, reducing p99 latency by 42%.
    • Spearheaded transition from monolithic codebase to Kubernetes-managed container workloads.

    Software Developer | DataWave Systems | 2019 – 2021
    • Developed responsive single-page web applications utilizing React.js, TypeScript, and Redux.
    • Integrated OAuth2 and JWT authentication mechanisms ensuring enterprise compliance.

    TECHNICAL SKILLS
    Languages: Python, JavaScript, TypeScript, Go, SQL, C++
    Frameworks: FastAPI, Django, React, Node.js, Express
    Cloud & DevOps: AWS, Docker, Kubernetes, Terraform, CI/CD, Git

    EDUCATION
    Bachelor of Technology in Computer Science and Engineering
    California State University | 2015 – 2019 | GPA: 3.8 / 4.0
    """
    res = validator.validate(text)
    assert res.decision == ResumeValidationDecision.VALID_RESUME
    assert res.is_valid is True
    assert res.is_uncertain is False
    assert res.confidence_score >= 60.0


def test_fresher_student_resume_no_experience(validator):
    """Verify that a college fresher with no work experience is classified as VALID_RESUME."""
    text = """
    Sneha Patel
    Email: sneha.patel@gmail.com | Mobile: +91 98765 43210
    Hyderabad, India | GitHub: github.com/snehapatel

    CAREER OBJECTIVE
    Enthusiastic Computer Science undergraduate seeking an entry-level software engineering role
    to contribute foundational skills in Python, algorithms, and data structures.

    EDUCATION
    B.Tech in Information Technology
    Aditya University, Surampalem | 2022 – 2026
    CGPA: 8.75 / 10.0

    Higher Secondary Education (12th Grade) | State Board | 2020 – 2022 | Aggregate: 92%

    TECHNICAL SKILLS
    Programming: Python, Java, C, SQL
    Web: HTML5, CSS3, JavaScript, Flask
    Tools: Git, VS Code, Linux

    ACADEMIC PROJECTS
    1. Online Book Recommendation System (2024)
       • Implemented collaborative filtering algorithm in Python using Pandas and Scikit-Learn.
       • Designed web interface using Flask and SQLite database.
    2. Smart Attendance Tracking App (2023)
       • Developed facial recognition pipeline using OpenCV and Python.

    CERTIFICATIONS
    • Python for Data Science – Coursera (2023)
    • Database Foundations – Oracle Academy (2022)
    """
    res = validator.validate(text)
    assert res.decision == ResumeValidationDecision.VALID_RESUME
    assert res.is_valid is True
    assert res.confidence_score >= 50.0


def test_resume_without_phone_number(validator):
    """Verify that a resume without a phone number is still recognized as VALID_RESUME."""
    text = """
    Marcus Vance
    Email: marcus.vance@techcorp.io
    GitHub: github.com/marcusvance | London, UK

    EXPERIENCE
    DevOps Specialist | CloudScale Ltd | 2020 – 2024
    • Designed and maintained automated Jenkins and GitHub Actions CI/CD pipelines.
    • Deployed multi-region infrastructure on AWS using Terraform and Ansible.
    • Monitored system health utilizing Prometheus and Grafana dashboards.

    SKILLS
    Cloud: AWS, Azure, GCP
    Containerization: Docker, Kubernetes, Helm
    Scripting: Bash, Python, YAML

    EDUCATION
    Master of Science in Software Engineering
    University of Bristol | 2018 – 2020
    """
    res = validator.validate(text)
    assert res.decision == ResumeValidationDecision.VALID_RESUME
    assert res.is_valid is True


def test_resume_without_professional_experience(validator):
    """Verify resume with education, projects, skills, but no professional experience."""
    text = """
    David Kim
    Email: dkim@uwaterloo.ca | Phone: 416-555-0199
    Waterloo, ON | Portfolio: dkim.dev

    EDUCATION
    Bachelor of Science in Mathematics and Computing
    University of Waterloo | 2021 – 2025 (Expected)
    Relevant Coursework: Algorithms, Operating Systems, Machine Learning, Database Design

    PROJECTS
    • Distributed Key-Value Store: Architected Raft-consensus distributed store in Go.
    • Neural Style Transfer: Built PyTorch model for real-time video transformation.
    • Mobile Expense Tracker: Designed React Native cross-platform application.

    TECHNICAL PROFICIENCIES
    Go, C++, Python, Rust, Docker, PyTorch, Git

    AWARDS & HONORS
    • Dean's Honours List (2022, 2023)
    • 2nd Place, HackWaterloo 2023
    """
    res = validator.validate(text)
    assert res.decision == ResumeValidationDecision.VALID_RESUME
    assert res.is_valid is True


def test_academic_research_paper_rejected(validator):
    """Verify that a scientific research paper is classified as NOT_A_RESUME."""
    text = """
    Attention Is All You Need: Advanced Transformer Networks for Neural Machine Translation

    ABSTRACT
    The dominant sequence transduction models are based on complex recurrent or convolutional
    neural networks. In this work, we propose the Transformer, a model architecture eschewing
    recurrence and relying entirely on an attention mechanism to draw global dependencies.
    Keywords: Deep Learning, Neural Machine Translation, Self-Attention, Natural Language Processing.

    1. INTRODUCTION
    Recurrent neural networks, particularly long short-term memory [1] and gated recurrent [2]
    architectures, have been established as state of the art in sequence modeling.

    2. RELATED WORK
    The goal of reducing sequential computation also forms the foundation of the Extended Neural
    GPU [3], ByteNet [4] and ConvS2S [5].

    3. PROPOSED METHODOLOGY AND EXPERIMENTS
    We evaluated on the WMT 2014 English-to-German translation task. The Transformer achieves
    28.4 BLEU on English-to-German translation, improving by over 2 BLEU over existing models.

    4. CONCLUDING REMARKS
    We presented the Transformer, the first sequence transduction model based entirely on attention.

    REFERENCES
    [1] S. Hochreiter and J. Schmidhuber, Long Short-Term Memory, Neural Computation, 1997.
    [2] K. Cho et al., Learning Phrase Representations using RNN Encoder-Decoder, 2014.
    [3] A. Vaswani et al., Proceedings of the 31st Conference on Neural Information Processing Systems, 2017.
    """
    res = validator.validate(text)
    assert res.decision == ResumeValidationDecision.NOT_A_RESUME
    assert res.is_valid is False
    assert "This document does not appear to be a resume" in res.message


def test_commercial_invoice_rejected(validator):
    """Verify that a billing invoice is classified as NOT_A_RESUME."""
    text = """
    INVOICE
    Acme Enterprise Cloud Solutions Inc.
    Invoice Number: INV-2026-98124
    Invoice Date: October 15, 2026
    Due Date: November 15, 2026

    BILL TO:
    Global Logistics Corp
    100 Main Street, Suite 400
    Chicago, IL 60601

    DESCRIPTION                     QTY    UNIT PRICE    TOTAL
    Cloud Server Hosting Plan         1       $450.00    $450.00
    Managed Database Service (MySQL)  1       $180.00    $180.00
    Network Bandwidth Overage         3        $40.00    $120.00

    Subtotal: $750.00
    Tax (8.25%): $61.88
    Total Due: $811.88
    Balance Due: $811.88

    Payment Terms: Net 30 days. Thank you for your business!
    """
    res = validator.validate(text)
    assert res.decision == ResumeValidationDecision.NOT_A_RESUME
    assert res.is_valid is False


def test_terms_of_service_legal_rejected(validator):
    """Verify that a legal terms agreement is classified as NOT_A_RESUME."""
    text = """
    TERMS OF SERVICE AND USER LICENSE AGREEMENT
    Last Updated: January 1, 2026

    1. ACCEPTANCE OF TERMS
    By accessing or using our platform, you hereby agree to be bound by these Terms and Conditions
    and our Privacy Policy. If you disagree with any part of these terms, you may not access the service.

    2. LIMITATION OF LIABILITY
    In no event shall the Company, its directors, employees, or partners be liable for any indirect,
    incidental, punitive, or consequential damages resulting from your use of the service.

    3. GOVERNING LAW AND JURISDICTION
    These Terms shall be governed by and construed in accordance with the laws of Delaware,
    without regard to its conflict of law provisions.

    4. INDEMNIFICATION
    You agree to defend, indemnify, and hold harmless the Company from and against any claims,
    liabilities, damages, and expenses. All rights reserved.
    """
    res = validator.validate(text)
    assert res.decision == ResumeValidationDecision.NOT_A_RESUME
    assert res.is_valid is False


def test_empty_and_trivial_text_rejected(validator):
    """Verify that empty, whitespace, or trivially short texts are rejected."""
    assert validator.validate("").decision == ResumeValidationDecision.NOT_A_RESUME
    assert validator.validate("   \n\n\t  ").decision == ResumeValidationDecision.NOT_A_RESUME
    assert validator.validate("Hello world, this is a test document.").decision == ResumeValidationDecision.NOT_A_RESUME


def test_ambiguous_short_snippet_uncertain(validator):
    """Verify that ambiguous short text without structured sections triggers UNCERTAIN or NOT_A_RESUME."""
    text = """
    Rahul Sharma. Software developer interested in Python and Java programming.
    Studied at Delhi Technological University. Contact me at rahul@example.com for collaboration.
    Looking for backend opportunities in technology.
    """
    res = validator.validate(text)
    # Lacks standard sections, timeline, bullet structure, but has an email and degree/university
    assert res.decision in (ResumeValidationDecision.UNCERTAIN_DOCUMENT, ResumeValidationDecision.NOT_A_RESUME)
    assert res.is_valid is False
