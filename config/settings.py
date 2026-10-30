"""
Resume Intelligence Platform - Configuration Settings
Defines global application settings, paths, thresholds, and environment overrides.
"""

from pathlib import Path
import os
import shutil

# Base directory: absolute path to project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Application Identity
APP_NAME = "Resume Intelligence"
APP_SUBTITLE = "NLP-Based Resume Classification & ATS Analytics Platform"
APP_VERSION = "2.0.0"

# Paths
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "resume_dataset.csv"
EXTERNAL_DATA_PATH = DATA_DIR / "external" / "real_resumes_mapped.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "resume_dataset_processed.csv"
SKILLS_TAXONOMY_PATH = DATA_DIR / "skills.json"

ARTIFACTS_DIR = BASE_DIR / "artifacts"
EVALUATION_DIR = BASE_DIR / "evaluation"
REPORTS_DIR = BASE_DIR / "reports_generated"
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "resume_intelligence.db"

# Model Artifact Filenames
CHAMPION_MODEL_PATH = ARTIFACTS_DIR / "champion_model.joblib"
VECTORIZER_PATH = ARTIFACTS_DIR / "tfidf_vectorizer.joblib"
LABEL_ENCODER_PATH = ARTIFACTS_DIR / "label_encoder.joblib"
MODEL_METADATA_PATH = ARTIFACTS_DIR / "model_metadata.json"

# Ingestion Settings
MAX_FILE_SIZE_MB = 10.0
MAX_FILE_SIZE_BYTES = int(MAX_FILE_SIZE_MB * 1024 * 1024)
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

# OCR Configuration
def get_tesseract_cmd() -> str | None:
    """Locate Tesseract OCR binary from env variable or standard Windows paths."""
    env_cmd = os.environ.get("TESSERACT_CMD")
    if env_cmd and Path(env_cmd).is_file():
        return env_cmd
    
    path_which = shutil.which("tesseract")
    if path_which:
        return path_which
    
    standard_paths = [
        Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
        Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Tesseract-OCR" / "tesseract.exe",
    ]
    for p in standard_paths:
        if p.is_file():
            return str(p)
    return None

TESSERACT_CMD = get_tesseract_cmd()

# Machine Learning & Reproducibility Settings
RANDOM_SEED = 42
TEST_SPLIT_RATIO = 0.20
CV_FOLDS = 5

TARGET_CATEGORIES = [
    "Business Analyst",
    "Cloud Engineer",
    "Data Analyst",
    "Data Scientist",
    "DevOps Engineer",
    "Machine Learning Engineer",
    "Software Developer",
    "UI/UX Designer",
    "Web Developer",
]

# Ensure required runtime directories exist
for directory in [ARTIFACTS_DIR, EVALUATION_DIR, REPORTS_DIR, DATABASE_DIR, DATA_DIR / "processed"]:
    directory.mkdir(parents=True, exist_ok=True)
