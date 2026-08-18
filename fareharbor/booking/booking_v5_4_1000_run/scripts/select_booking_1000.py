"""
Pick 1000 NEW booking-notes products, UNIFORM RANDOM.

Deliberately NOT stratified and NOT hardest-first, unlike select_booking_100.py
and select_booking_500.py. Those two were chosen for difficulty, so every rate
the booking side has produced so far is the PESSIMISTIC end of the catalogue,
not the typical case. The description side hit exactly this: 2.6% defects on
the hardest-500 against 1.2% on a uniform random 1,000 -- the same prompt, 2x
apart.

This run exists to be hand-verified, so it has to be representative. A random
sample is the only kind whose rate can be quoted for the catalogue as a whole.

EXCLUDES all 600 products already run (the 100 and the 500), asserted rather
than assumed -- an overlap would let a product be "verified" twice and inflate
agreement between runs.

Writes booking1000_products.json.
"""
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

from booking_common import iter_products, profile, regime  # noqa: E402

DONE_FILES = [TEST_DIR / "booking100_products.json",
              TEST_DIR / "booking500_products.json"]
OUT = TEST_DIR / "booking1000_products.json"
WANT = 1000
SEED = 42


def main():
    done = set()
    for f in DONE_FILES:
        ids = json.loads(f.read_text(encoding="utf-8"))["product_ids"]
        done |= set(ids)
        print(f"excluding {len(ids)} from {f.name}")
    print(f"total excluded: {len(done)}")

    pool, seen = [], 0
    for pid, name, bn in iter_products():
        seen += 1
        if pid in done:
            continue
        pool.append((pid, name, profile(bn)))
    print(f"scanned {seen} products with booking notes; pool = {len(pool)}")

    if len(pool) < WANT:
        raise SystemExit(f"only {len(pool)} available, wanted {WANT}")

    rng = random.Random(SEED)
    take = rng.sample(pool, WANT)
    chosen = [p for p, _, _ in take]

    assert len(set(chosen)) == len(chosen), "duplicate ids"
    overlap = set(chosen) & done
    assert not overlap, f"{len(overlap)} overlap the 600 already run"

    # report the regime mix WITHOUT having selected on it -- this is what the
    # catalogue actually looks like, and it is the thing the stratified runs
    # deliberately distorted.
    mix = Counter(regime(p) for _, _, p in take)
    print("\nregime mix of the random 1000 (observed, not imposed):")
    for r, c in mix.most_common():
        print(f"  {r:20s} {c:5d}  ({100*c/WANT:4.1f}%)")

    rows = [{
        "product_id": pid, "name": name, "regime": regime(p),
        "words": p["words"], "lines": p["lines"], "n_headings": p["n_headings"],
        "n_bullets": p["n_bullets"], "bullet_ratio": round(p["bullet_ratio"], 2),
        "n_inline_labels": p["n_inline_labels"], "headings": p["headings"][:12],
    } for pid, name, p in take]

    OUT.write_text(json.dumps({
        "product_ids": chosen,
        "n": len(chosen),
        "selection": f"UNIFORM RANDOM (seed {SEED}) from all products with "
                     "booking notes, excluding the 600 already run. NOT "
                     "stratified and NOT hardest-first -- this run is meant to "
                     "be representative so its rate can be quoted for the "
                     "catalogue.",
        "seed": SEED,
        "excluded_already_run": len(done),
        "pool_size": len(pool),
        "observed_regime_mix": dict(mix),
        "products": rows,
    }, indent=1, ensure_ascii=False), encoding="utf-8")

    words = sorted(r["words"] for r in rows)
    heads = sorted(r["n_headings"] for r in rows)
    print(f"\nselected {len(chosen)} -> {OUT.name}")
    print(f"  zero overlap with the 600: CONFIRMED")
    print(f"  median words {words[len(words)//2]}   median headings {heads[len(heads)//2]}")


if __name__ == "__main__":
    main()
