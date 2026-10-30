import sys
import os
import shutil

print(f"Python: {sys.version}")

packages = [
    "streamlit",
    "pandas",
    "numpy",
    "sklearn",
    "nltk",
    "fitz",
    "docx",
    "pytesseract",
    "PIL",
    "reportlab",
    "plotly",
    "pytest",
    "joblib",
]

print("\n--- Checking Packages ---")
for pkg in packages:
    try:
        mod = __import__(pkg)
        ver = getattr(mod, "__version__", "installed")
        print(f"[OK] {pkg}: {ver}")
    except Exception as e:
        print(f"[FAIL] {pkg}: {e}")

print("\n--- Checking NLTK Data ---")
import nltk
for res in ["punkt", "punkt_tab", "stopwords", "wordnet"]:
    try:
        nltk.data.find(f"tokenizers/{res}" if "punkt" in res else f"corpora/{res}")
        print(f"[OK] NLTK resource: {res}")
    except LookupError:
        print(f"[MISSING] NLTK resource: {res}")

print("\n--- Checking Tesseract OCR ---")
tess_path = shutil.which("tesseract") or os.environ.get("TESSERACT_CMD")
if tess_path and os.path.exists(tess_path):
    print(f"[OK] Tesseract binary located at: {tess_path}")
else:
    print("[NOTE] Tesseract binary not found in PATH or TESSERACT_CMD (OCR will offer setup guidance).")

print("\n--- Setup Check Complete ---")
