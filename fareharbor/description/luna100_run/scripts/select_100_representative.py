"""
Select 100 products representative of the real catalogue size distribution.

Deliberately NOT a hard-product sample. hard30 and luna50 both selected
flagged-for-review products, which answers "how does luna cope when the input
is difficult" -- it does not show what a normal spread looks like, and those
runs understate typical performance by construction.

This draws a proportional stratified sample across the four size bands from the
products not already used, so band shares match the remaining pool rather than
being hand-picked. random_state=42 makes it reproducible.

Zero overlap with hard30_products.json or luna50_products.json is asserted, not
assumed -- reusing a product would silently turn new evidence into a repeat.

Usage:
    python select_100_representative.py
"""
import sys
import json
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
V500 = TEST_DIR / "v500_products.xlsx"
STATE = TEST_DIR / "v500_post_fix_state.json"
OUT = TEST_DIR / "luna100_products.json"

# Product sets already used, which must not be reused. Each is searched in a few
# likely locations so this runs from a clone as well as from the working
# directory; a set that cannot be found is reported loudly rather than silently
# skipped, because a missing exclusion turns "new evidence" into a repeat.
PRIOR_RUNS = {
    "hard30": ["hard30_products.json",
               "../../hard30_run/hard30_products.json",
               "hard30_run/hard30_products.json"],
    "luna50": ["luna50_products.json",
               "../../luna50_run/luna50_products.json",
               "luna50_run/luna50_products.json"],
}


def load_prior_ids():
    """Union of product IDs used by earlier runs."""
    used, missing = set(), []
    for name, candidates in PRIOR_RUNS.items():
        for rel in candidates:
            p = (TEST_DIR / rel).resolve()
            if p.exists():
                used |= set(json.loads(p.read_text(encoding="utf-8"))["product_ids"])
                print(f"  excluding {name}: {p.name}")
                break
        else:
            missing.append(name)
    if missing:
        print(f"  WARNING: could not find {', '.join(missing)} -- products from "
              f"those runs may be reselected, making this a partial repeat")
    return used

N = 100
SEED = 42


def main():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    used = load_prior_ids()

    df = pd.read_excel(V500, sheet_name="Summary")
    df["product_id"] = df["product_id"].astype(str)
    avail = df[df.product_id.isin(state) & ~df.product_id.isin(used)]
    print(f"Pool: {len(avail)} products not already used "
          f"({len(used)} excluded from earlier runs)")

    # proportional across bands, largest-remainder so the total lands on N
    total = len(avail)
    exact = {b: N * len(g) / total for b, g in avail.groupby("band")}
    counts = {b: int(v) for b, v in exact.items()}
    for b, _ in sorted(exact.items(), key=lambda kv: -(kv[1] - int(kv[1]))):
        if sum(counts.values()) >= N:
            break
        counts[b] += 1

    picks = []
    for band, g in avail.groupby("band"):
        n = min(counts.get(band, 0), len(g))
        if n:
            picks.append(g.sample(n=n, random_state=SEED))
    picked = pd.concat(picks).sort_values("input_words")

    ids = list(picked.product_id)
    assert len(ids) == N, f"expected {N}, got {len(ids)}"
    assert not (set(ids) & used), "OVERLAP with an earlier run -- selection is wrong"
    empty = [p for p in ids
             if not (state[p].get("raw_desc") or "").strip()
             and not (state[p].get("raw_booking") or "").strip()]
    assert not empty, f"products with no raw text on either side: {empty}"

    n_desc = sum(1 for p in ids if (state[p].get("raw_desc") or "").strip())
    n_booking = sum(1 for p in ids if (state[p].get("raw_booking") or "").strip())

    meta = {
        "n_products": len(ids),
        "n_requests": n_desc + n_booking,
        "selection": "proportional stratified sample across size bands, "
                     f"seed={SEED}, from products not used in hard30 or luna50",
        "bands": {str(b): int(n) for b, n in
                  picked.band.value_counts().sort_index().items()},
        "input_words_range": [int(picked.input_words.min()),
                              int(picked.input_words.max())],
        "input_words_median": int(picked.input_words.median()),
        "excluded_prior_runs": sorted(used),
        "product_ids": ids,
    }
    OUT.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print("=" * 74)
    print(f"SELECTED {len(ids)} REPRESENTATIVE PRODUCTS")
    print("=" * 74)
    for b, n in meta["bands"].items():
        print(f"  {b:<12} {n:>3} products  ({100 * n / len(ids):.0f}%)")
    print(f"\n  words   : {meta['input_words_range'][0]}-"
          f"{meta['input_words_range'][1]} (median {meta['input_words_median']})")
    print(f"  requests: {meta['n_requests']}  "
          f"({n_desc} desc + {n_booking} booking; "
          f"{2 * len(ids) - meta['n_requests']} empty sides skipped)")
    print(f"  overlap with earlier runs: 0 (asserted)")
    print(f"\nWrote {OUT.name}")


if __name__ == "__main__":
    main()
