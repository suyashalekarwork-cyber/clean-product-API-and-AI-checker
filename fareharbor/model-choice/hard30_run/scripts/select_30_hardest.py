"""
Pick the 30 hardest products from v500_products.xlsx for the terra/nano/luna
comparison.

"Hardest" is defined from the V4.4 500-product run's own measurements, in
priority order:

  1. flag_for_human_review == True  (37 products) -- the run itself said these
     needed a human. That is the strongest available signal.
  2. lowest coverage_after          -- content the pipeline could not place.
  3. longest input_words            -- tie-break; long text is where models
     fragment and truncate.

These 30 have ZERO overlap with the 10 products in best_model_13.xlsx, so this
is a genuinely new test set rather than a re-run.

Note on interpretation: a hard-selected set scores WORSE than the catalogue
average by construction. The earlier 10-product set had the same property, and
its low judge scores were partly an artefact of it. These numbers rank models
against each other; they are not a production accuracy estimate.

Usage:
    python select_30_hardest.py
"""
import sys
import json
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
V500 = TEST_DIR / "v500_products.xlsx"
STATE = TEST_DIR / "v500_post_fix_state.json"
BEST13 = TEST_DIR / "bestmodel_screen_results.json"
OUT = TEST_DIR / "hard30_products.json"

N = 30


def main():
    df = pd.read_excel(V500, sheet_name="Summary")
    df["product_id"] = df["product_id"].astype(str)

    # the raw source must exist in the 500-run state file, or the product
    # cannot be re-extracted
    state = json.loads(STATE.read_text(encoding="utf-8"))
    have_raw = set(state)
    before = len(df)
    df = df[df.product_id.isin(have_raw)]
    if len(df) < before:
        print(f"  dropped {before - len(df)} products with no raw text in "
              f"{STATE.name}")

    # never reuse a product already measured in the 13-model run
    already = set(json.loads(BEST13.read_text(encoding="utf-8"))["gpt-5.4-nano"])
    overlap = set(df.product_id) & already
    if overlap:
        df = df[~df.product_id.isin(already)]
        print(f"  excluded {len(overlap)} products already in best_model_13")

    # hardest first: flagged, then worst coverage, then longest
    df = df.sort_values(
        ["flag_for_human_review", "coverage_after", "input_words"],
        ascending=[False, True, False],
    )
    picked = df.head(N).copy()

    n_flagged = int(picked.flag_for_human_review.sum())
    print("=" * 74)
    print(f"SELECTED {len(picked)} HARDEST PRODUCTS (of {len(df)} eligible)")
    print("=" * 74)
    print(f"  flagged for human review : {n_flagged}")
    print(f"  coverage_after           : {picked.coverage_after.min():.1f}% - "
          f"{picked.coverage_after.max():.1f}%")
    print(f"  input_words              : {picked.input_words.min()} - "
          f"{picked.input_words.max()}  (median {int(picked.input_words.median())})")
    print(f"  size bands               : "
          f"{dict(picked.band.value_counts().sort_index())}")
    print()
    print(f"{'product_id':<12}{'words':>7}{'cov_after':>11}{'flagged':>9}  supplier")
    for r in picked.itertuples():
        print(f"{r.product_id:<12}{r.input_words:>7}{r.coverage_after:>11.1f}"
              f"{str(r.flag_for_human_review):>9}  {r.supplier_alias}")

    payload = {
        "product_ids": list(picked.product_id),
        "selection": "flagged first, then lowest coverage_after, then longest",
        "n_flagged": n_flagged,
        "source": V500.name,
        "excluded_overlap_with_best_model_13": sorted(overlap),
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # the raw text must be non-empty on at least one side or the request is wasted
    empty = [p for p in picked.product_id
             if not (state[p].get("raw_desc") or "").strip()
             and not (state[p].get("raw_booking") or "").strip()]
    if empty:
        raise SystemExit(f"products with no raw text on either side: {empty}")

    print(f"\nWrote {OUT.name}  ({len(picked)} product ids, all with raw text)")
    return picked


if __name__ == "__main__":
    main()
