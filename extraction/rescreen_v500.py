"""
Isolated POC: Step 7 -- re-run the detector over the post-fix state for
the 50-product round, compare against pre-fix per product.

Usage:
    python rescreen_v500.py
"""
import sys
import json
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loss_detector import detect_lost_content_wordlevel

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent


def main():
    pre_fix = json.loads((TEST_DIR / "v500_pre_fix_state.json").read_text(encoding="utf-8"))
    post_fix = json.loads((TEST_DIR / "v500_post_fix_state.json").read_text(encoding="utf-8"))

    rows = []
    for pid, entry in pre_fix.items():
        missing_before = sum(1 for u in entry["problem_units"] if u["status"] == "MISSING")
        coverage_before = entry["word_coverage_pct"]

        post_field_values = post_fix[pid]["field_values"]
        raw_desc = entry["raw_desc"]
        raw_booking = entry["raw_booking"]
        after_result = detect_lost_content_wordlevel(raw_desc, raw_booking, post_field_values)
        missing_after = after_result["units_missing"]
        coverage_after = after_result["word_coverage_pct"]

        rows.append({
            "product_id": pid,
            "missing_before": missing_before, "missing_after": missing_after,
            "coverage_before": coverage_before, "coverage_after": coverage_after,
        })

    df = pd.DataFrame(rows)
    df["product_id_sort"] = df["product_id"].astype(int)
    df = df.sort_values("product_id_sort").drop(columns=["product_id_sort"]).reset_index(drop=True)

    print("=" * 80)
    print("RE-SCREEN: BEFORE vs AFTER (50 products)")
    print("=" * 80)
    print(df.to_string(index=False))

    total_before = df["missing_before"].sum()
    total_after = df["missing_after"].sum()
    avg_cov_before = round(df["coverage_before"].mean(), 2)
    avg_cov_after = round(df["coverage_after"].mean(), 2)

    print(f"\nTotal missing before: {total_before}")
    print(f"Total missing after: {total_after}")
    print(f"Average coverage before: {avg_cov_before}%")
    print(f"Average coverage after: {avg_cov_after}%")

    df.to_csv(TEST_DIR / "rescreen_v500_results.csv", index=False)
    print(f"\nWrote rescreen_v500_results.csv")

    return df


if __name__ == "__main__":
    main()

