"""
Classification Explainability Module
Extracts top contributing features and terms that influenced the model's prediction.
Provides transparent explanations for resume classification decisions.
"""

import numpy as np


def extract_top_contributing_terms(
    vectorizer,
    classifier,
    preprocessed_text: str,
    predicted_category: str,
    top_n: int = 8,
) -> list[tuple[str, float]]:
    """
    Extract the strongest vocabulary terms that contributed to the predicted category.
    Works with LinearSVC, CalibratedClassifierCV, LogisticRegression, Naive Bayes.
    """
    if not preprocessed_text or classifier is None or vectorizer is None:
        return []

    try:
        # Transform document to TF-IDF vector
        vec = vectorizer.transform([preprocessed_text])
        feature_names = np.array(vectorizer.get_feature_names_out())
        non_zero_indices = vec.indices
        if len(non_zero_indices) == 0:
            return []

        weights = vec.data

        # Determine class index
        classes = list(getattr(classifier, "classes_", []))
        if predicted_category not in classes:
            # Fallback to pure TF-IDF magnitude
            sorted_order = np.argsort(weights)[::-1][:top_n]
            return [(feature_names[non_zero_indices[i]], float(weights[i])) for i in sorted_order]

        class_idx = classes.index(predicted_category)

        # Inspect underlying estimator coefficients if linear
        base_estimator = classifier
        if hasattr(classifier, "calibrated_classifiers_"):
            # CalibratedClassifierCV wraps base estimators
            base_estimator = classifier.calibrated_classifiers_[0].estimator

        if hasattr(base_estimator, "coef_"):
            coef = base_estimator.coef_
            if coef.ndim == 2 and class_idx < coef.shape[0]:
                class_coefs = coef[class_idx]
                doc_coefs = class_coefs[non_zero_indices]
                # Combined score: term TF-IDF weight * model weight
                importance = weights * doc_coefs
                top_indices = np.argsort(importance)[::-1][:top_n]
                results = []
                for idx in top_indices:
                    term = feature_names[non_zero_indices[idx]]
                    score = float(importance[idx])
                    results.append((term, round(score, 4)))
                return results

        # Fallback to top TF-IDF terms in the document
        sorted_order = np.argsort(weights)[::-1][:top_n]
        return [(feature_names[non_zero_indices[i]], round(float(weights[i]), 4)) for i in sorted_order]

    except Exception:
        return []
