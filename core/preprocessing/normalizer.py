"""
NLP Text Normalizer Module
Implements modular tokenization, stopword removal, lemmatization,
and cleaning tailored for resume classification and ATS evaluation.
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from core.preprocessing.text_cleaner import (
    normalize_unicode,
    preserve_tech_tokens,
    restore_tech_tokens,
)

# Initialize NLP components with fallback safety
try:
    STOP_WORDS = set(stopwords.words("english"))
except LookupError:
    STOP_WORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
        "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
        "by", "can", "did", "do", "does", "doing", "don", "down", "during", "each", "few", "for",
        "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
        "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just",
        "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once",
        "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she",
        "should", "so", "some", "such", "t", "than", "that", "the", "their", "theirs", "them",
        "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too",
        "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which",
        "while", "who", "whom", "why", "will", "with", "you", "your", "yours", "yourself"
    }

# Terms that should NOT be removed by stopwords because they carry classification meaning
DOMAIN_PRESERVED_TERMS = {
    "it", "ai", "r", "c", "go", "net", "os", "ux", "ui", "bi", "qa", "ml", "db"
}
ADJUSTED_STOP_WORDS = STOP_WORDS - DOMAIN_PRESERVED_TERMS

try:
    LEMMATIZER = WordNetLemmatizer()
except Exception:
    LEMMATIZER = None


def tokenize_text(text: str) -> list[str]:
    """Tokenize text into words with regex fallback."""
    try:
        tokens = nltk.word_tokenize(text)
    except Exception:
        tokens = re.findall(r"\b\w+\b", text)
    return tokens


def preprocess_resume_text(
    text: str,
    remove_stopwords: bool = True,
    lemmatize: bool = True,
    preserve_tech: bool = True,
) -> str:
    """
    Standard preprocessing pipeline applied identically during training and inference.
    
    Pipeline Steps:
    1. Unicode normalization (NFKD)
    2. Technical token preservation (e.g. C++ -> techtoken_cpp)
    3. Case folding to lowercase
    4. URL, email, and phone stripping for classification neutrality
    5. Tokenization
    6. Non-alphanumeric token filtering
    7. Stopword removal (with domain terms preserved)
    8. Lemmatization
    9. Restoring normalized tokens into space-separated string
    """
    if not text or not isinstance(text, str):
        return ""

    # Step 1: Unicode normalization
    cleaned = normalize_unicode(text)

    # Step 2: Preserve technical tokens
    if preserve_tech:
        cleaned = preserve_tech_tokens(cleaned)

    # Step 3: Lowercase
    cleaned = cleaned.lower()

    # Step 4: Neutralize noise patterns
    cleaned = re.sub(r"https?://\S+|www\.\S+", " ", cleaned)
    cleaned = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " ", cleaned)
    cleaned = re.sub(r"\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b", " ", cleaned)

    # Remove generic punctuation (keep underscores for technical tokens)
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)

    # Step 5: Tokenization
    tokens = tokenize_text(cleaned)

    processed_tokens = []
    for token in tokens:
        # Step 6: Filter short or purely numeric tokens
        if len(token) < 2 and token not in DOMAIN_PRESERVED_TERMS:
            continue
        if token.isdigit():
            continue

        # Step 7: Stopwords
        if remove_stopwords and token in ADJUSTED_STOP_WORDS:
            continue

        # Step 8: Lemmatization
        if lemmatize and LEMMATIZER is not None:
            # Simple noun lemmatization, fallback safely
            try:
                lemma = LEMMATIZER.lemmatize(token, pos="v")
                lemma = LEMMATIZER.lemmatize(lemma, pos="n")
                token = lemma
            except Exception:
                pass

        processed_tokens.append(token)

    return " ".join(processed_tokens)
