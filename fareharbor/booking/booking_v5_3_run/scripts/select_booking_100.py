"""
Pick the 100 booking-notes products for the first V5 booking run.

NOT a pure "hardest" sort. Measurement across all 8,244 products with booking
notes found three genuinely different regimes, and a length-ranked list would
return only the first of them:

    heading_rich       3,457  42%   median 150 words -- the gate's home ground
    short_no_heading   2,597  32%   median  47 words -- catch-all IS correct
    long_no_heading    1,730  21%   >60 words, no heading -- the real gap
    inline_label_only    460   6%   no heading, but STEP 1D labels present

Sampling all four means the run tests the gate where it should work, where it
should decline, and where we do not yet know. `short_no_heading` is deliberately
NOT sampled as its own stratum -- with a median of 47 words over 4 lines there
is nothing to route and nothing to learn; those products are represented
incidentally.

Within each stratum, hardest first (most headings, then longest), matching the
ordering convention in select_500_hardest.py.

Writes booking100_products.json.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

from booking_common import iter_products, profile, regime  # noqa: E402

OUT = TEST_DIR / "booking100_products.json"

QUOTA = {
    "heading_rich": 55,
    "long_no_heading": 25,
    "bullet_heavy": 15,
    "inline_label_only": 5,
}


def main():
    buckets = {k: [] for k in QUOTA}
    counts = {}

    for pid, name, bn in iter_products():
        p = profile(bn)
        r = regime(p)
        counts[r] = counts.get(r, 0) + 1

        # bullet_heavy is a CROSS-CUTTING stratum, claimed first: these are the
        # products where the item-vs-heading confusion actually lives, and most
        # of them are also heading_rich (a "What to Bring" heading over a list).
        if p["bullet_ratio"] >= 0.5 and p["n_bullets"] >= 4:
            buckets["bullet_heavy"].append((pid, name, p))
        elif r in buckets:
            buckets[r].append((pid, name, p))

    print("regime census across all products with booking notes:")
    for r, c in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {r:20s} {c:5d}")
    print()

    chosen, rows = [], []
    for stratum, want in QUOTA.items():
        pool = buckets[stratum]
        # hardest first: most headings, then most words
        pool.sort(key=lambda t: (-t[2]["n_headings"], -t[2]["words"]))
        take = pool[:want]
        if len(take) < want:
            print(f"  !! {stratum}: only {len(take)} available, wanted {want}")
        for pid, name, p in take:
            chosen.append(pid)
            rows.append({
                "product_id": pid,
                "name": name,
                "stratum": stratum,
                "words": p["words"],
                "lines": p["lines"],
                "n_headings": p["n_headings"],
                "n_bullets": p["n_bullets"],
                "bullet_ratio": round(p["bullet_ratio"], 2),
                "n_inline_labels": p["n_inline_labels"],
                "headings": p["headings"][:12],
            })
        print(f"  {stratum:20s} took {len(take):3d} of {len(pool):5d} available")

    if len(set(chosen)) != len(chosen):
        raise SystemExit("duplicate product ids across strata -- strata must be disjoint")

    OUT.write_text(json.dumps({
        "product_ids": chosen,
        "n": len(chosen),
        "selection": "stratified across the four measured booking-notes regimes; "
                     "hardest-first within each stratum",
        "quota": QUOTA,
        "regime_census": counts,
        "products": rows,
    }, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"\nselected {len(chosen)} products -> {OUT.name}")
    tot_w = sum(r["words"] for r in rows)
    print(f"total words: {tot_w}   median headings: "
          f"{sorted(r['n_headings'] for r in rows)[len(rows) // 2]}")


if __name__ == "__main__":
    main()
