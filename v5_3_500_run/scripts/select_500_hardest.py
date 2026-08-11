"""
Pick the 100 hardest products for the V5.3 run.

Same ordering as select_50_hardest.py -- flagged for human review first, then
lowest coverage, then longest input -- extended to N=100.

The result is a SUPERSET of hard100_products.json by construction: the ordering
is deterministic and hard50 was the head of the same sorted list, so the first
50 of this list are those same 50. That matters because it is what makes a
direct V5.2 -> V5.3 comparison possible on half the set; the other ~50 are new
evidence. The assertion below proves the superset property rather than assuming
it (the pool is re-filtered for readable raw files, so a silent drop is
possible).

The 10 already run on V5.0/V5.1/V5.2 stay excluded here -- they are re-run
separately as the regression anchor.

Writes hard500_products.json.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

from build_model_comparison_batches import find_raw_file  # noqa: E402

N = 500
SRC = TEST_DIR / "v500_products.xlsx"
ALREADY = TEST_DIR / "hard30_products.json"
PRIOR50 = TEST_DIR / "hard100_products.json"
OUT = TEST_DIR / "hard500_products.json"


def main():
    import pandas as pd

    df = pd.read_excel(SRC, sheet_name="Summary")
    print(f"pool: {len(df)} products")

    # The original 10 are INCLUDED this time: at N=500 we are taking the whole
    # pool, and re-running them adds repeatability evidence rather than noise.
    tested = set(json.loads(ALREADY.read_text(encoding="utf-8"))["product_ids"][:10])
    df["product_id"] = df["product_id"].astype(str)
    print(f"including the {len(tested)} originals: {len(df)}")

    keep = []
    for pid in df["product_id"]:
        try:
            find_raw_file(pid)
            keep.append(pid)
        except (FileNotFoundError, RuntimeError):
            pass
    df = df[df["product_id"].isin(keep)]
    print(f"with a readable raw file: {len(df)}")

    df = df.sort_values(
        ["flag_for_human_review", "coverage_after", "input_words"],
        ascending=[False, True, False],
    )
    picked = df.head(N)
    ids = picked["product_id"].tolist()

    prior = json.loads(PRIOR50.read_text(encoding="utf-8"))["product_ids"]
    missing = sorted(set(prior) - set(ids))
    if missing:
        raise SystemExit(
            f"NOT a superset of hard100 -- {len(missing)} dropped: {missing}\n"
            "Every hard50 product must be present or the V5.2 -> V5.3 comparison "
            "loses its baseline."
        )
    new_ids = [p for p in ids if p not in set(prior)]

    OUT.write_text(json.dumps({
        "product_ids": ids,
        "n": len(ids),
        "selection": "flagged first, then lowest coverage_after, then longest input",
        "source": "v500_products.xlsx / Summary",
        "excluded_already_tested": sorted(tested),
        "carried_over_from_hard100": sorted(prior),
        "new_this_run": new_ids,
        "n_flagged": int(picked["flag_for_human_review"].sum()),
        "coverage_after_min": float(picked["coverage_after"].min()),
        "coverage_after_max": float(picked["coverage_after"].max()),
        "input_words_median": float(picked["input_words"].median()),
    }, indent=1), encoding="utf-8")

    print(f"\nselected {len(ids)} products")
    print(f"  superset of hard100       : YES (all {len(prior)} carried over)")
    print(f"  new this run             : {len(new_ids)}")
    print(f"  flagged for human review : {int(picked['flag_for_human_review'].sum())}/{len(ids)}")
    print(f"  coverage_after range     : {picked['coverage_after'].min():.1f} - {picked['coverage_after'].max():.1f}")
    print(f"  input_words median       : {picked['input_words'].median():.0f}")
    print(f"  suppliers                : {picked['supplier_alias'].nunique()}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
