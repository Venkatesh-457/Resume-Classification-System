"""
NLP Feature Representation Comparison Module
Compares word-level TF-IDF (unigrams vs bigrams), character-level n-grams,
and hybrid FeatureUnion pipelines on training cross-validation metrics.
"""

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import time
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import FeatureUnion

from config.settings import PROCESSED_DATA_PATH, RANDOM_SEED
from core.features.tfidf_builder import (
    create_word_vectorizer,
    create_char_vectorizer,
    create_hybrid_vectorizer,
)


def run_feature_comparison() -> pd.DataFrame:
    """
    Compare multiple NLP feature extraction representations using 5-fold Stratified CV.
    """
    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(f"Processed dataset not found at {PROCESSED_DATA_PATH}")

    df = pd.read_csv(PROCESSED_DATA_PATH)
    X = df["processed_text"].fillna("")
    y = df["category"]

    feature_configs = {
        "Word TF-IDF (Unigrams)": create_word_vectorizer(ngram_range=(1, 1), max_features=5000),
        "Word TF-IDF (Unigrams + Bigrams)": create_word_vectorizer(ngram_range=(1, 2), max_features=5000),
        "Character TF-IDF (3-5 Grams)": create_char_vectorizer(ngram_range=(3, 5), max_features=4000),
        "Hybrid FeatureUnion (Word + Char)": create_hybrid_vectorizer(
            word_ngram=(1, 2), char_ngram=(3, 5), word_max_features=5000, char_max_features=3000
        ),
    }

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    base_model = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)

    records = []
    print("=" * 70)
    print("NLP FEATURE REPRESENTATION COMPARISON (5-Fold Stratified CV)")
    print("=" * 70)

    for name, vectorizer in feature_configs.items():
        t0 = time.time()
        X_vec = vectorizer.fit_transform(X)
        fit_time = round(time.time() - t0, 3)

        vocab_size = X_vec.shape[1]
        sparsity = round(100.0 * (1.0 - (X_vec.nnz / (X_vec.shape[0] * X_vec.shape[1]))), 2)

        # 5-fold CV macro F1 and accuracy
        f1_scores = cross_val_score(base_model, X_vec, y, cv=skf, scoring="f1_macro", n_jobs=-1)
        acc_scores = cross_val_score(base_model, X_vec, y, cv=skf, scoring="accuracy", n_jobs=-1)

        mean_f1 = round(float(f1_scores.mean()), 4)
        std_f1 = round(float(f1_scores.std()), 4)
        mean_acc = round(float(acc_scores.mean()), 4)

        records.append({
            "Feature Representation": name,
            "Vocabulary Dimension": vocab_size,
            "Matrix Sparsity (%)": sparsity,
            "Fit Time (s)": fit_time,
            "CV Macro F1": mean_f1,
            "CV F1 Std": std_f1,
            "CV Accuracy": mean_acc,
        })

        print(f"• {name:<35} | Dim: {vocab_size:>5} | Macro F1: {mean_f1:.4f} (±{std_f1:.4f}) | Acc: {mean_acc:.4f}")

    print("=" * 70)
    res_df = pd.DataFrame(records)
    return res_df


if __name__ == "__main__":
    run_feature_comparison()
