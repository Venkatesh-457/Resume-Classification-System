import json
from pathlib import Path
import pandas as pd

def audit():
    raw_path = Path("data/raw/resume_dataset.csv")
    ext_path = Path("data/external/real_resumes_mapped.csv")
    skills_path = Path("data/skills.json")

    print("=== DATASET AUDIT ===")
    if raw_path.exists():
        df_raw = pd.read_csv(raw_path)
        print(f"Raw dataset shape: {df_raw.shape}")
        print(f"Raw columns: {list(df_raw.columns)}")
        print(f"Raw category distribution:\n{df_raw['category'].value_counts() if 'category' in df_raw.columns else 'No category col'}\n")
        print(f"Raw missing values:\n{df_raw.isnull().sum()}\n")
        print(f"Raw duplicates (resume_text): {df_raw.duplicated(subset=['resume_text']).sum() if 'resume_text' in df_raw.columns else 0}")
    else:
        print("Raw dataset not found at data/raw/resume_dataset.csv")

    if ext_path.exists():
        df_ext = pd.read_csv(ext_path)
        print(f"\nExternal dataset shape: {df_ext.shape}")
        print(f"External columns: {list(df_ext.columns)}")
        print(f"External category distribution:\n{df_ext['category'].value_counts() if 'category' in df_ext.columns else 'No category col'}\n")
        print(f"External missing values:\n{df_ext.isnull().sum()}\n")
        print(f"External duplicates (resume_text): {df_ext.duplicated(subset=['resume_text']).sum() if 'resume_text' in df_ext.columns else 0}")

    if skills_path.exists():
        with open(skills_path, "r", encoding="utf-8") as f:
            skills_data = json.load(f)
        print(f"\nSkills categories: {list(skills_data.keys()) if isinstance(skills_data, dict) else len(skills_data)}")
        if isinstance(skills_data, dict):
            for k, v in skills_data.items():
                print(f"  - {k}: {len(v)} skills")

if __name__ == "__main__":
    audit()
