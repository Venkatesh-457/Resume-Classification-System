"""
Resume Classifier & Inference Module
Provides inference, probability calibration inspection, multi-class ranking,
and confidence diagnostics for uploaded resumes.
"""

from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
import joblib
import numpy as np

from config.settings import (
    CHAMPION_MODEL_PATH,
    VECTORIZER_PATH,
    MODEL_METADATA_PATH,
    TARGET_CATEGORIES,
)
from core.preprocessing.normalizer import preprocess_resume_text
from core.classification.explainability import extract_top_contributing_terms

logger = logging.getLogger(__name__)


@dataclass
class AlternativePrediction:
    """Represents a candidate class ranking with confidence."""
    category: str
    confidence: float
    percentage: float


@dataclass
class ClassificationResult:
    """Full inference result returned to UI and persistence layers."""
    predicted_category: str
    confidence: float
    confidence_percentage: float
    is_calibrated: bool
    score_type: str
    alternative_predictions: list[AlternativePrediction] = field(default_factory=list)
    top_contributing_terms: list[tuple[str, float]] = field(default_factory=list)
    model_name: str = "Trained Classifier"
    warnings: list[str] = field(default_factory=list)
    disclaimer: str = (
        "Automated classification provides a statistical prediction based on training patterns. "
        "It does not replace human evaluation and should not be used as the sole basis for hiring decisions."
    )


class ResumeClassifier:
    """Production inference engine for resume classification."""

    def __init__(
        self,
        model_path: Path | str = CHAMPION_MODEL_PATH,
        vectorizer_path: Path | str = VECTORIZER_PATH,
        metadata_path: Path | str = MODEL_METADATA_PATH,
    ):
        self.model_path = Path(model_path)
        self.vectorizer_path = Path(vectorizer_path)
        self.metadata_path = Path(metadata_path)
        self.model = None
        self.vectorizer = None
        self.metadata = {}
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Load trained model, vectorizer, and evaluation metadata."""
        if self.model_path.is_file() and self.vectorizer_path.is_file():
            try:
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)
                if self.metadata_path.is_file():
                    with open(self.metadata_path, "r", encoding="utf-8") as f:
                        self.metadata = json.load(f)
                logger.info("Successfully loaded champion model and vectorizer.")
            except Exception as exc:
                logger.exception("Failed to load model artifacts: %s", exc)
                self.model = None
                self.vectorizer = None
        else:
            logger.warning("Model artifacts not found. Model training must be executed before inference.")

    @property
    def is_ready(self) -> bool:
        """Check if model and vectorizer are loaded and ready for prediction."""
        return self.model is not None and self.vectorizer is not None

    def predict(self, raw_text: str) -> ClassificationResult:
        """
        Classify resume text into one of the target job categories.
        """
        if not self.is_ready:
            raise RuntimeError(
                "Model artifacts are not loaded. Please train models using the Training Module before running classification."
            )

        preprocessed = preprocess_resume_text(raw_text)
        if not preprocessed.strip():
            return ClassificationResult(
                predicted_category="Unclassified (Insufficient Content)",
                confidence=0.0,
                confidence_percentage=0.0,
                is_calibrated=False,
                score_type="None",
                warnings=["The document contains no extractable or readable vocabulary after NLP preprocessing."],
            )

        # Vectorize text
        vec = self.vectorizer.transform([preprocessed])

        classes = list(getattr(self.model, "classes_", TARGET_CATEGORIES))
        model_name = self.metadata.get("model_name", type(self.model).__name__)

        has_proba = hasattr(self.model, "predict_proba")
        warnings = []

        if has_proba:
            probabilities = self.model.predict_proba(vec)[0]
            top_idx = int(np.argmax(probabilities))
            predicted_cat = str(classes[top_idx])
            top_confidence = float(probabilities[top_idx])
            score_type = "Calibrated Probability"
            is_calibrated = True

            # Sort all alternatives in descending order
            sorted_indices = np.argsort(probabilities)[::-1]
            alternatives = [
                AlternativePrediction(
                    category=str(classes[idx]),
                    confidence=round(float(probabilities[idx]), 4),
                    percentage=round(float(probabilities[idx]) * 100.0, 1),
                )
                for idx in sorted_indices[1:4]
            ]

            # Quality and margin diagnostics
            if top_confidence < 0.35:
                warnings.append("Low classification confidence (< 35%). The resume contains cross-domain or ambiguous terminology.")
            elif len(sorted_indices) > 1:
                runner_up_conf = float(probabilities[sorted_indices[1]])
                if (top_confidence - runner_up_conf) < 0.08:
                    warnings.append(
                        f"Close classification margin: '{predicted_cat}' ({top_confidence*100:.1f}%) "
                        f"narrowly leads '{classes[sorted_indices[1]]}' ({runner_up_conf*100:.1f}%)."
                    )

        else:
            # Fallback for models without predict_proba (e.g. raw LinearSVC)
            dec_scores = self.model.decision_function(vec)[0]
            top_idx = int(np.argmax(dec_scores))
            predicted_cat = str(classes[top_idx])
            top_confidence = float(dec_scores[top_idx])
            score_type = "Raw Decision Margin"
            is_calibrated = False

            sorted_indices = np.argsort(dec_scores)[::-1]
            alternatives = [
                AlternativePrediction(
                    category=str(classes[idx]),
                    confidence=round(float(dec_scores[idx]), 4),
                    percentage=0.0,
                )
                for idx in sorted_indices[1:4]
            ]
            warnings.append("Raw SVM decision margins are uncalibrated and cannot be interpreted as strict probabilities.")

        # Extract top contributing terms
        contributing_terms = extract_top_contributing_terms(
            self.vectorizer, self.model, preprocessed, predicted_cat, top_n=8
        )

        return ClassificationResult(
            predicted_category=predicted_cat,
            confidence=round(top_confidence, 4),
            confidence_percentage=round(top_confidence * 100.0, 1) if is_calibrated else 0.0,
            is_calibrated=is_calibrated,
            score_type=score_type,
            alternative_predictions=alternatives,
            top_contributing_terms=contributing_terms,
            model_name=model_name,
            warnings=warnings,
        )


# Shared singleton classifier
resume_classifier = ResumeClassifier()
