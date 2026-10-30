"""
Dataset Audit Script
Analyzes dataset composition, class distributions, duplicates, missing values, and data integrity.
"""

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
from config.settings import RAW_DATA_PATH, EXTERNAL_DATA_PATH, PROCESSED_DATA_PATH


def run_dataset_audit() -> dict:
    """Execute comprehensive audit on raw, external, and processed datasets."""
    audit_results = {}

    print("=" * 65)
    print("RESUME INTELLIGENCE PLATFORM — DATASET AUDIT")
    print("=" * 65)

    if RAW_DATA_PATH.exists():
        df_raw = pd.read_csv(RAW_DATA_PATH)
        raw_dups = df_raw.duplicated(subset=["resume_text"]).sum() if "resume_text" in df_raw.columns else 0
        raw_nulls = df_raw.isnull().sum().to_dict()
        cat_dist = df_raw["category"].value_counts().to_dict() if "category" in df_raw.columns else {}

        audit_results["raw"] = {
            "path": str(RAW_DATA_PATH),
            "rows": len(df_raw),
            "columns": list(df_raw.columns),
            "categories_count": len(cat_dist),
            "category_distribution": cat_dist,
            "duplicate_resumes": int(raw_dups),
            "missing_values": raw_nulls,
        }
        print(f"[RAW DATASET] Total Rows: {len(df_raw)}, Categories: {len(cat_dist)}, Duplicates: {raw_dups}")
        for c, n in cat_dist.items():
            print(f"  • {c:<28}: {n} samples")
    else:
        print(f"[RAW DATASET] Missing file at {RAW_DATA_PATH}")

    if EXTERNAL_DATA_PATH.exists():
        df_ext = pd.read_csv(EXTERNAL_DATA_PATH)
        ext_dups = df_ext.duplicated(subset=["resume_text"]).sum() if "resume_text" in df_ext.columns else 0
        ext_cat_dist = df_ext["category"].value_counts().to_dict() if "category" in df_ext.columns else {}

        audit_results["external"] = {
            "path": str(EXTERNAL_DATA_PATH),
            "rows": len(df_ext),
            "columns": list(df_ext.columns),
            "category_distribution": ext_cat_dist,
            "duplicate_resumes": int(ext_dups),
        }
        print(f"\n[EXTERNAL DATASET] Total Rows: {len(df_ext)}, Categories: {len(ext_cat_dist)}, Duplicates: {ext_dups}")
        for c, n in ext_cat_dist.items():
            print(f"  • {c:<28}: {n} samples")

    if PROCESSED_DATA_PATH.exists():
        df_proc = pd.read_csv(PROCESSED_DATA_PATH)
        proc_cat_dist = df_proc["category"].value_counts().to_dict() if "category" in df_proc.columns else {}
        audit_results["processed"] = {
            "path": str(PROCESSED_DATA_PATH),
            "rows": len(df_proc),
            "columns": list(df_proc.columns),
            "category_distribution": proc_cat_dist,
        }
        print(f"\n[PROCESSED DATASET] Total Rows: {len(df_proc)}, Categories: {len(proc_cat_dist)}")
        for c, n in proc_cat_dist.items():
            print(f"  • {c:<28}: {n} samples")

    print("=" * 65)
    return audit_results


if __name__ == "__main__":
    run_dataset_audit()
