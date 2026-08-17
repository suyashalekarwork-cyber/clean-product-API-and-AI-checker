"""Pick the 100 HARDEST Rezdy descriptions for Round 1.

Hardest = most headings, then most words. Round 1 exists to break the prompt
cheaply, so it gets the products most likely to break it. The honest rate comes
from the uniform-random 1,000 later -- CLAUDE.md is explicit that every
difficulty-selected set is the pessimistic end, measured 2x apart on Fareharbor.

ONE GUARD THAT FAREHARBOR DID NOT NEED: a per-supplier cap.

Rezdy suppliers repeat themselves at a scale Fareharbor never did -- 00seven
carries ~13 KB of near-identical text across every product it lists. Taking the
top 100 by raw difficulty would hand most of the sample to a handful of
suppliers and we would learn one supplier's quirks 100 times over. Same reasoning
as ranking headings by DISTINCT SUPPLIERS in the column census.

Writes rezdy_desc_100_products.json.
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

from rezdy_common import (conversion_losses, html_to_markdown,  # noqa: E402
                          iter_products)
from booking_common import heading_of                            # noqa: E402

OUT = TEST_DIR / "rezdy_desc_100_products.json"
N = 100
MAX_PER_SUPPLIER = 3


def headings_of(text):
    lines = [l for l in text.split("\n") if l.strip()]
    return [h for i, l in enumerate(lines)
            if (h := heading_of(l, lines[i + 1] if i + 1 < len(lines) else None))]


def main():
    rows, lossy = [], []
    for pid, supplier, p in iter_products(fields=["description"]):
        raw = p.get("description")
        conv = html_to_markdown(raw)
        if not conv.strip():
            continue
        # The lossless gate is not only a build-time refusal -- a product whose
        # conversion drops text must never be used to JUDGE the prompt, or the
        # converter's bug is scored as the model's.
        if conversion_losses(raw, conv):
            lossy.append(pid)
            continue
        hs = headings_of(conv)
        rows.append({
            "product_id": pid,
            "supplier": supplier,
            "name": (p.get("name") or "").strip(),
            "n_headings": len(hs),
            "words": len(conv.split()),
            "chars": len(conv),
            "headings": hs[:12],
        })

    rows.sort(key=lambda r: (-r["n_headings"], -r["words"]))

    picked, per_supplier = [], Counter()
    for r in rows:
        if per_supplier[r["supplier"]] >= MAX_PER_SUPPLIER:
            continue
        picked.append(r)
        per_supplier[r["supplier"]] += 1
        if len(picked) == N:
            break

    if len(picked) < N:
        raise SystemExit(f"only {len(picked)} products available, wanted {N}")

    OUT.write_text(json.dumps(picked, indent=1, ensure_ascii=False),
                   encoding="utf-8")

    print(f"candidates              : {len(rows):,}")
    print(f"skipped (lossy convert) : {len(lossy)}  {lossy[:6]}")
    print(f"selected                : {len(picked)}")
    print(f"distinct suppliers      : {len(per_supplier)}  "
          f"(cap {MAX_PER_SUPPLIER}/supplier)")
    print(f"headings  min/med/max   : {picked[-1]['n_headings']} / "
          f"{picked[len(picked)//2]['n_headings']} / {picked[0]['n_headings']}")
    print(f"words     min/max       : {min(r['words'] for r in picked):,} / "
          f"{max(r['words'] for r in picked):,}")
    print(f"\nwrote {OUT}")
    print("\nfirst 8:")
    for r in picked[:8]:
        print(f"  {r['product_id']:9s} {r['supplier'][:22]:24s} "
              f"{r['n_headings']:3d} headings {r['words']:5,} words  "
              f"{r['name'][:38]}")


if __name__ == "__main__":
    main()
