"""
Model Evaluation CLI & Inspection Utility
Loads and prints saved evaluation metrics, per-class performance tables,
confusion matrices, and champion model diagnostics.
"""

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
import pandas as pd
from tabulate import tabulate
from config.settings import EVALUATION_DIR, MODEL_METADATA_PATH


def display_saved_evaluation() -> None:
    """Print the officially saved model evaluation results to console."""
    comp_csv = EVALUATION_DIR / "model_comparison.csv"
    per_class_csv = EVALUATION_DIR / "per_class_metrics.csv"
    meta_json = MODEL_METADATA_PATH

    print("=" * 80)
    print("RESUME INTELLIGENCE PLATFORM — MODEL EVALUATION INSPECTOR")
    print("=" * 80)

    if meta_json.exists():
        with open(meta_json, "r", encoding="utf-8") as f:
            meta = json.load(f)
        print(f"Champion Model   : {meta.get('model_name')}")
        print(f"Overall Accuracy : {meta.get('accuracy', 0)*100:.2f}%")
        print(f"Macro F1-Score   : {meta.get('macro_f1', 0)*100:.2f}%")
        print(f"Weighted F1      : {meta.get('weighted_f1', 0)*100:.2f}%")
        print(f"Inference Latency: {meta.get('latency_ms_per_sample', 0):.3f} ms / sample")
        print(f"Trained Timestamp: {meta.get('timestamp')}")
        print("-" * 80)

    if comp_csv.exists():
        df_comp = pd.read_csv(comp_csv)
        print("\n[CANDIDATE MODELS COMPARISON]")
        print(tabulate(df_comp, headers="keys", tablefmt="github", showindex=False))

    if per_class_csv.exists():
        df_pc = pd.read_csv(per_class_csv)
        print("\n[CHAMPION MODEL PER-CLASS BREAKDOWN]")
        print(tabulate(df_pc, headers="keys", tablefmt="github", showindex=False))

    print("=" * 80)


if __name__ == "__main__":
    display_saved_evaluation()
