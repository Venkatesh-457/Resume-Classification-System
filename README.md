# Resume Intelligence: NLP-Based Resume Classification & ATS Analytics System

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, independent natural language processing (NLP) and machine learning platform for intelligent resume document classification, explainable ATS resume quality scoring, job-description alignment analytics, and executive PDF audit reporting.

---

## 1. Executive Summary & Capabilities

Resume Intelligence transforms the unstructured, noisy natural language found in modern resumes into structured, transparent hiring intelligence. Built from the ground up to address real-world document variety and class imbalance, the system features:

1. **Multi-Format Ingestion:** Native parsing of **Digital PDF**, **DOCX**, and **TXT** documents.
2. **Optical Character Recognition (OCR):** Automatic detection of scanned or rasterized image PDFs with seamless **Tesseract OCR fallback**.
3. **Advanced NLP Engineering:**
   - Unicode NFKD normalization with ligature expansion.
   - Specialized **Technical Token Preservation** ensuring vital terms (`C++`, `C#`, `.NET`, `Node.js`, `CI/CD`) survive tokenization.
   - Domain-sensitive stopword filtering retaining keywords (`AI`, `ML`, `DB`, `UX`, `UI`).
   - WordNet lemmatization.
   - Hybrid **FeatureUnion** evaluating word-level TF-IDF (unigrams + bigrams) and character n-grams.
4. **Benchmarked Machine Learning Classification:**
   - 5 candidate models evaluated: *Multinomial Naive Bayes*, *Complement Naive Bayes*, *Logistic Regression*, *Calibrated Linear Support Vector Classifier*, and *Random Forest*.
   - Champion model: **LinearSVC with Platt Sigmoid Calibration** achieving **94.51% Accuracy** and **96.29% Macro F1-Score**.
   - True calibrated probability outputs (no raw, uncalibrated SVM margins disguised as probabilities).
5. **Explainable ATS Quality Scoring (0 to 100):**
   - 6 transparent, weighted evaluation dimensions: Readability (15 pts), Contact Info (15 pts), Section Coverage (20 pts), Skills Depth (25 pts), Quantifiable Metrics (15 pts), Action Verbs (10 pts).
6. **Job Match Studio:**
   - Optional candidate-to-job matching measuring **Technical Skill Coverage (40%)**, **Semantic Cosine Similarity (35%)**, and **Keyword Overlap (25%)**.
7. **Local Multi-Profile Architecture:**
   - Persistent SQLite storage enforcing strict **profile data isolation**. Different candidates or users manage separate analysis archives on the same machine.
8. **Executive PDF Report Generator:**
   - Built from scratch using **ReportLab** (A4 layout, corporate navy/teal palette, dynamic `Page X of Y` footers, tables, charts, checklists, and academic disclaimers).

---

## 2. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Programming Language** | Python 3.12 (Windows / Linux / macOS) |
| **Web Dashboard** | Streamlit 1.66+, Custom Enterprise CSS, Responsive Cards |
| **Data Processing & ML** | scikit-learn 1.9+, pandas 3.1+, NumPy 2.5+, joblib |
| **Natural Language Processing** | NLTK 3.10+ (tokenizers, stopwords, WordNet lemmatizer) |
| **Document Ingestion** | PyMuPDF (fitz) 2.0+, python-docx 1.2+, Pillow (PIL) 13.0+ |
| **OCR Fallback Engine** | pytesseract 0.3.13 + Tesseract OCR binary |
| **Database & Persistence** | SQLite3 (WAL mode, foreign keys, parameterized queries) |
| **Data Visualization** | Plotly 7.1+ (interactive donut charts, timelines, heatmaps) |
| **Executive Reporting** | ReportLab 5.1+ (custom canvas, dynamic pagination) |
| **Automated Testing** | pytest 9.1+ |

---

## 3. Project Directory Architecture

```
Resume Classification Sysytem Project/
│
├── app.py                          # Application entry point (Streamlit)
├── README.md                       # Comprehensive project documentation
├── CODEBASE_GUIDE.md               # Technical architecture & code reference
├── MODEL_EVALUATION_RESULTS.txt    # Official empirical training benchmark report
├── requirements.txt                # Production package dependencies
├── pytest.ini                      # Pytest runner configuration
├── .gitignore                      # Git exclusion rules
├── .env.example                    # Environment variable template
│
├── config/
│   └── settings.py                 # Paths, thresholds, OCR config, constants
│
├── ui/                             # Presentation Layer (Streamlit Pages)
│   ├── styles.py                   # Enterprise visual theme & custom CSS
│   ├── dashboard.py                # Page 1: Overview Dashboard (KPIs, Plotly charts)
│   ├── analyzer.py                 # Page 2: Resume Analyzer (Upload, OCR, ATS Score)
│   ├── job_match.py                # Page 3: Job Match Studio (JD alignment)
│   ├── history.py                  # Page 4: History & Side-by-Side Comparison
│   ├── model_lab.py                # Page 5: Model Laboratory (Benchmarking metrics)
│   ├── reports.py                  # Page 6: PDF Reports Repository
│   └── docs.py                     # Page 7: Technical Documentation View
│
├── core/                           # Business & Computational Core
│   ├── ingestion/
│   │   ├── parser.py               # Multi-format parser (TXT, DOCX, PDF)
│   │   └── ocr.py                  # Tesseract OCR wrapper & diagnostics
│   ├── preprocessing/
│   │   ├── text_cleaner.py         # Tech-token preservation, regex entities
│   │   └── normalizer.py           # Tokenization, stopwords, lemmatization
│   ├── features/
│   │   ├── tfidf_builder.py        # Word/Char/Hybrid TF-IDF vectorizers
│   │   └── skill_extractor.py      # Taxonomy-driven skill extractor (14 cats)
│   ├── classification/
│   │   ├── predictor.py            # Calibrated inference engine
│   │   └── explainability.py       # Attribution feature importance
│   ├── scoring/
│   │   ├── ats_scorer.py           # 6-dimension explainable ATS score (0-100)
│   │   └── job_matcher.py          # Candidate-to-job description matcher
│   ├── analytics/
│   │   └── metrics_aggregator.py   # Historical analytics & comparison matrices
│   └── reporting/
│       └── pdf_generator.py        # Executive ReportLab PDF generator
│
├── data_access/                    # Persistence Layer
│   ├── database.py                 # SQLite connection & schema initialization
│   ├── profile_repository.py       # Local profile management
│   └── analysis_repository.py      # Profile-isolated analysis records
│
├── training/                       # ML Experimentation & Training Pipeline
│   ├── dataset_audit.py            # Dataset distribution & integrity audit
│   ├── compare_features.py         # 5-fold CV feature engineering comparison
│   ├── train_models.py             # Model training, calibration & benchmark
│   └── evaluate_models.py          # CLI metrics inspector
│
├── data/                           # Data Assets (Preserved)
│   ├── raw/resume_dataset.csv      # Base dataset (1,260 samples, 9 classes)
│   ├── external/                   # Real-world mapped resumes (557 samples)
│   ├── processed/                  # Cleaned & preprocessed training dataset
│   └── skills.json                 # Taxonomy: 14 categories, 120 aliases
│
├── artifacts/                      # Production Model Artifacts
│   ├── champion_model.joblib       # Calibrated LinearSVC pipeline
│   ├── tfidf_vectorizer.joblib     # Fitted TF-IDF vectorizer (5,000 terms)
│   └── model_metadata.json         # Training metrics, classes, hyperparameters
│
├── evaluation/                     # Evaluation Outputs
│   ├── model_comparison.csv        # Metrics table (Acc, F1, Latency)
│   ├── model_comparison.json       # Structured benchmark outputs
│   ├── per_class_metrics.csv       # Precision, Recall, F1 for 9 categories
│   ├── confusion_matrix.json       # Confusion matrices for all models
│   └── feature_comparison.csv      # Word vs Char vs Hybrid CV results
│
├── tests/                          # Automated Pytest Suite (23 Tests)
│   ├── test_ingestion.py           # File parsing, empty docs, OCR detection
│   ├── test_nlp_features.py        # Tech tokens, normalization, taxonomy
│   ├── test_classification.py      # Inference, calibration, class shapes
│   ├── test_scoring.py             # ATS score bounds, job description match
│   ├── test_database.py            # Persistence, profile isolation, CRUD
│   └── test_pdf_report.py          # ReportLab PDF creation & byte validation
│
└── scripts/
    └── setup_check.py              # System environment & dependency check
```

---

## 4. Installation & Local Setup (Windows)

### Prerequisites
- Windows 10 or 11 (64-bit)
- Python 3.12 (installed from [python.org](https://www.python.org/downloads/))

### Step 1: Open PowerShell in Project Root
```powershell
cd "c:\Users\nimma\OneDrive\Desktop\Resume Classification Sysytem Project"
```

### Step 2: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Verify Environment Health
Run the built-in diagnostic script:
```powershell
python scripts/setup_check.py
```

### Step 4: Optional OCR Setup (For Scanned PDFs)
The application automatically processes digital PDFs, DOCX, and TXT files out of the box. To enable OCR for scanned image documents:
1. Download the Tesseract Windows installer from [UB-Mannheim GitHub](https://github.com/UB-Mannheim/tesseract/wiki).
2. Install to default path (`C:\Program Files\Tesseract-OCR\tesseract.exe`).
3. If installed to a custom folder, set `TESSERACT_CMD` in `.env`:
   ```ini
   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

---

## 5. Model Training & Evaluation Workflow

To retrain the classification models, evaluate feature alternatives, and regenerate evaluation benchmarks:

```powershell
python training/train_models.py
```

This automated pipeline:
1. Audits raw (`data/raw/resume_dataset.csv`) and external mapped resumes (`data/external/real_resumes_mapped.csv`).
2. Splits data into **80% Stratified Train (1,453 samples)** and **20% Held-Out Test (364 samples)** using seed `42`.
3. Fits the TF-IDF feature pipeline exclusively on the training partition (zero data leakage).
4. Trains and benchmarks 5 algorithms with holdout metrics and latency measurements.
5. Performs 5-fold Stratified Cross-Validation on feature representation variants (Word, Char, Hybrid).
6. Exports the champion model to `artifacts/champion_model.joblib`.
7. Updates `MODEL_EVALUATION_RESULTS.txt` and `evaluation/` metrics.

To inspect the stored evaluation results in terminal:
```powershell
python training/evaluate_models.py
```

---

## 6. Launching the Application

Start the Streamlit dashboard:

```powershell
streamlit run app.py
```

The application will launch in your default web browser at `http://localhost:8501`.

---

## 7. Running Automated Tests

Run the complete test suite with verbose reporting:

```powershell
python -m pytest -v
```

All **23 unit and integration tests** cover:
- Document extraction across TXT, DOCX, Digital PDF, empty files, and corrupted binaries.
- OCR diagnostics and fallback triggers.
- Unicode normalization and technical token preservation (`C++`, `C#`, `.NET`).
- Categorized skill taxonomy extraction and alias canonicalization.
- Machine learning inference, output shape, and probability calibration.
- ATS scoring bounds (0–100), component weights, and job matching.
- SQLite profile isolation (ensuring Profile Alpha cannot see Profile Beta's data).
- Custom ReportLab PDF creation and byte validity.

---

## 8. Empirical Model Evaluation Summary

Results evaluated on the held-out test partition ($n = 364$ resumes):

| Classification Algorithm | Accuracy | Macro Prec | Macro Rec | Macro F1 | Weighted F1 | Train Time | Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Linear Support Vector Classifier (Calibrated)** *(Champion)* | **94.51%** | **96.32%** | **96.33%** | **96.29%** | **94.51%** | 0.503s | 0.017 ms |
| Random Forest Classifier | 94.51% | 96.92% | 95.82% | 96.23% | 94.55% | 0.344s | 0.114 ms |
| Logistic Regression | 93.68% | 96.06% | 95.56% | 95.74% | 93.73% | 0.270s | 0.000 ms |
| Multinomial Naive Bayes | 89.29% | 94.84% | 91.75% | 92.65% | 89.46% | 0.007s | 0.001 ms |
| Complement Naive Bayes | 87.64% | 94.49% | 90.30% | 91.38% | 87.78% | 0.007s | 0.000 ms |

### Champion Model Selection Rationale
- **Macro F1 Leadership (96.29%):** Outperforms all candidates across balanced class weights, preventing bias toward majority classes like *Business Analyst*.
- **Platt Sigmoid Calibration:** LinearSVC decision margins are wrapped in `CalibratedClassifierCV`, outputting verified mathematical probabilities.
- **Microsecond Latency:** Inference latency is **0.017 ms per document**, delivering instant results in production.

---

## 9. Explainable ATS Resume Quality Score

The ATS Quality Score is deterministic, fully explainable, and scaled from 0 to 100:

1. **Structure & Readability (Max 15 pts):** Optimal length (350–950 words) and clean paragraph flow.
2. **Contact Information (Max 15 pts):** Email (+5), phone (+4), LinkedIn/GitHub/Portfolio (+4), header structure (+2).
3. **Section Coverage (Max 20 pts):** Experience (+5), Education (+4), Skills (+4), Projects (+3), Summary (+2), Certifications (+2).
4. **Skills Depth & Taxonomy (Max 25 pts):** Breadth and volume of detected canonical skills across 14 technical domains.
5. **Quantifiable Metrics (Max 15 pts):** Measurable business impact: percentages (%), currency amounts ($), throughput metrics, user counts.
6. **Action Verbs & Phrasing (Max 10 pts):** High-impact power verbs (engineered, spearheaded, orchestrated, optimized).
7. **Penalties Deductions:** Formatting anomalies, extreme character noise, or unreadable blocks.

---

## 10. Privacy & Disclaimers

- **Privacy:** Document processing occurs strictly on the local machine. No resume contents or candidate data are transmitted to external servers.
- **Academic Purpose:** This system was engineered for educational analytics and resume optimization. Automated classification predictions and ATS scores do not constitute formal hiring recommendations or commercial ATS certifications.
