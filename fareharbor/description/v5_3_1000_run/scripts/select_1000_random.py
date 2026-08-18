"""
Pick 1,000 RANDOM Fareharbor products that have never been run.

Every set so far has been chosen for difficulty -- flagged for human review
first, then lowest coverage, then longest input. That is the right way to hunt
for defects, but it means every rate we have quoted comes from the worst
products in the catalogue. This set is the opposite: a uniform random draw from
the 10,736 products the 500-run never touched.

If the heading gate is sound, this should come out CLEANER than the hardest-500,
and the gap between the two is the honest error bar for a full-catalogue run.

Seeded (42) so the selection is reproducible, matching the convention used by
rezdy_1000_pipeline.py.

Writes random1000_products.json.
"""
import json
import random
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
ROOT = TEST_DIR.parent.parent
sys.path.insert(0, str(TEST_DIR))

from build_model_comparison_batches import strip_html  # noqa: E402

N = 1000
SEED = 42
ALREADY = TEST_DIR / "hard500_products.json"
OUT = TEST_DIR / "random1000_products.json"
RAW_DIR = ROOT / "data" / "Fareharbor"


def main():
    tested = set(json.loads(ALREADY.read_text(encoding="utf-8"))["product_ids"])
    print(f"excluding the {len(tested)} already run")

    # Build the candidate pool, keeping only products that actually have text to
    # extract -- a product with an empty description tells us nothing about
    # placement, and the batch builder would skip it anyway.
    pool, empty, unreadable = [], 0, 0
    for fp in sorted(RAW_DIR.glob("*.json")):
        pid = fp.stem.split("-")[-1]
        if pid in tested:
            continue
        try:
            item = json.loads(fp.read_text(encoding="utf-8")).get("item") or {}
        except Exception:                                   # noqa: BLE001
            unreadable += 1
            continue
        sd = item.get("structured_description") or {}
        raw = strip_html(sd.get("description") or item.get("description") or "")
        if not raw.strip():
            empty += 1
            continue
        pool.append(pid)

    print(f"candidates with a description: {len(pool)}"
          f"   (skipped {empty} empty, {unreadable} unreadable)")
    if len(pool) < N:
        raise SystemExit(f"pool too small: {len(pool)} < {N}")

    random.seed(SEED)
    ids = sorted(random.sample(pool, N))

    OUT.write_text(json.dumps({
        "product_ids": ids,
        "n": len(ids),
        "selection": f"uniform random sample, seed={SEED}",
        "why": "every prior set was chosen for difficulty; this one is representative",
        "pool_size": len(pool),
        "excluded_already_run": len(tested),
        "skipped_empty_description": empty,
    }, indent=1), encoding="utf-8")

    print(f"\nselected {len(ids)} products at random (seed {SEED})")
    print(f"  overlap with the 500 already run: {len(set(ids) & tested)}  (must be 0)")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
