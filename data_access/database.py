"""
Database Architecture Module
Provides SQLite connection management, schema migrations, and parameterized query execution.
Enforces foreign keys, indexing, and strict profile separation.
"""

import logging
import sqlite3
from pathlib import Path
from config.settings import DATABASE_PATH

logger = logging.getLogger(__name__)


def get_connection(db_path: Path | str = DATABASE_PATH) -> sqlite3.Connection:
    """Return SQLite database connection with row factory and foreign keys enabled."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_db(db_path: Path | str = DATABASE_PATH) -> None:
    """Initialize database tables, indices, and default user profile."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with get_connection(path) as conn:
        cursor = conn.cursor()

        # Table 1: Profiles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                is_active INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Table 2: Analyses (strictly associated with a local profile)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_format TEXT NOT NULL,
                extraction_method TEXT NOT NULL,
                ocr_used INTEGER NOT NULL DEFAULT 0,
                page_count INTEGER NOT NULL DEFAULT 1,
                word_count INTEGER NOT NULL DEFAULT 0,
                predicted_category TEXT NOT NULL,
                confidence REAL NOT NULL,
                is_calibrated INTEGER NOT NULL DEFAULT 1,
                score_type TEXT NOT NULL DEFAULT 'Calibrated Probability',
                alternative_predictions_json TEXT,
                ats_score REAL NOT NULL,
                ats_grade TEXT NOT NULL,
                score_breakdown_json TEXT,
                skills_detected_json TEXT,
                section_coverage_json TEXT,
                warnings_json TEXT,
                recommendations_json TEXT,
                job_description_snippet TEXT,
                job_match_score REAL,
                job_match_details_json TEXT,
                raw_text_snippet TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profile_id) REFERENCES profiles (id) ON DELETE CASCADE
            );
        """)

        # Performance Indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_profile_id ON analyses (profile_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses (created_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_category ON analyses (predicted_category);")

        # Seed default profile if none exists
        cursor.execute("SELECT COUNT(*) FROM profiles;")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO profiles (name, is_active) VALUES (?, ?);",
                ("Default Profile", 1)
            )

        conn.commit()
    logger.info("Database initialized successfully at %s", path)


# Initialize schema on module import
init_db()
