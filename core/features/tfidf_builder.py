"""
TF-IDF Feature Engineering Module
Builds word-level, character-level, and hybrid FeatureUnion vectorizers.
Handles vectorizer configuration, fitting, serialization, and vocabulary inspections.
"""

from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion

from config.settings import VECTORIZER_PATH


def create_word_vectorizer(
    ngram_range: tuple[int, int] = (1, 2),
    max_features: int = 5000,
    min_df: int = 2,
    sublinear_tf: bool = True,
) -> TfidfVectorizer:
    """Build word-level TF-IDF vectorizer (unigrams + bigrams)."""
    return TfidfVectorizer(
        ngram_range=ngram_range,
        max_features=max_features,
        min_df=min_df,
        sublinear_tf=sublinear_tf,
        strip_accents="unicode",
        lowercase=True,
    )


def create_char_vectorizer(
    ngram_range: tuple[int, int] = (3, 5),
    max_features: int = 3000,
    min_df: int = 3,
    sublinear_tf: bool = True,
) -> TfidfVectorizer:
    """Build character n-gram TF-IDF vectorizer for sub-word morphology."""
    return TfidfVectorizer(
        analyzer="char",
        ngram_range=ngram_range,
        max_features=max_features,
        min_df=min_df,
        sublinear_tf=sublinear_tf,
        lowercase=True,
    )


def create_hybrid_vectorizer(
    word_ngram: tuple[int, int] = (1, 2),
    char_ngram: tuple[int, int] = (3, 5),
    word_max_features: int = 5000,
    char_max_features: int = 3000,
) -> FeatureUnion:
    """
    Combine word-level and character-level TF-IDF via FeatureUnion.
    Captures both vocabulary context and subword morphology (e.g., abbreviations, typos).
    """
    word_vec = create_word_vectorizer(
        ngram_range=word_ngram,
        max_features=word_max_features,
    )
    char_vec = create_char_vectorizer(
        ngram_range=char_ngram,
        max_features=char_max_features,
    )
    return FeatureUnion([
        ("word_tfidf", word_vec),
        ("char_tfidf", char_vec),
    ])


def save_vectorizer(vectorizer, path: Path | str = VECTORIZER_PATH) -> None:
    """Save fitted vectorizer to disk."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, path)


def load_vectorizer(path: Path | str = VECTORIZER_PATH):
    """Load fitted vectorizer from disk."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"TF-IDF vectorizer artifact not found at {path}")
    return joblib.load(path)
