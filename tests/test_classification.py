"""
Automated Tests for Machine Learning Classification Layer
Covers model artifact loading, prediction outputs, probability calibration, and alternative classes.
"""

from core.classification.predictor import resume_classifier, ClassificationResult
from config.settings import TARGET_CATEGORIES


def test_classifier_readiness():
    assert resume_classifier.is_ready is True
    assert resume_classifier.model is not None
    assert resume_classifier.vectorizer is not None


def test_prediction_output_structure():
    sample_resume = """
    Senior Cloud Architect with 8 years of experience designing AWS, Azure, and GCP architectures.
    Deep expertise in Terraform, Kubernetes, Docker, microservices, and VPC networking.
    Led cloud migration for enterprise client reducing infrastructure cost by 35%.
    """
    res: ClassificationResult = resume_classifier.predict(sample_resume)

    assert isinstance(res, ClassificationResult)
    assert res.predicted_category in TARGET_CATEGORIES
    assert 0.0 <= res.confidence <= 1.0
    assert 0.0 <= res.confidence_percentage <= 100.0
    assert res.is_calibrated is True
    assert res.score_type == "Calibrated Probability"
    assert len(res.alternative_predictions) >= 1


def test_prediction_cloud_engineer_sample():
    cloud_resume = """
    Cloud Engineer with deep expertise in AWS, Azure, CloudFormation, Terraform, and Kubernetes.
    Automated multi-region cloud infrastructure and managed CI/CD deployment pipelines on AWS ECS.
    """
    res = resume_classifier.predict(cloud_resume)
    assert "Cloud" in res.predicted_category or "DevOps" in res.predicted_category


def test_empty_input_handling():
    res = resume_classifier.predict("")
    assert "Insufficient" in res.predicted_category or "Unclassified" in res.predicted_category
    assert res.confidence == 0.0
