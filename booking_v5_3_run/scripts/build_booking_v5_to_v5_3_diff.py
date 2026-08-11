"""
V5 -> V5.3 diff for the booking run, product by product and column by column.

Both runs used the SAME 100 products, so every difference is caused by the
prompt change and nothing else. Any change that is NOT explainable by a rename,
a new column, or one of the stated rule changes is a regression.

The question this exists to answer: do the 10 new columns pull content out of
the columns that already worked, or only out of the catch-all? Content moving
from `other` -> a new column is the intended behaviour. Content moving from
`what_to_bring` -> a new column needs looking at.

Writes reports/booking_v5_to_v5_3_diff.md.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
TEST = ROOT / "data_pipeline" / "batch_api_test"
sys.path.insert(0, str(TEST))

from booking_common import parse_booking_json, load_raw   # noqa: E402
from booking_postprocess import norm                      # noqa: E402

OUT = ROOT / "reports" / "booking_v5_to_v5_3_diff.md"

# V5 name -> V5.3 name. The three renames are the whole point of the mapping.
RENAME = {
    "redo_booking_inclusions": "redo_booking_what_included",
    "redo_booking_location": "redo_booking_meeting_point",
    "redo_booking_other": "redo_booking_notes",
}
NEW_IN_V5_3 = [
    "redo_booking_highlights", "redo_booking_what_excluded",
    "redo_booking_extras", "redo_booking_duration_text",
    "redo_booking_health_safety", "redo_booking_special_requirements",
    "redo_booking_accessibility", "redo_booking_group_size",
    "redo_booking_disclaimers", "redo_booking_pricing",
]
FLAGS = "redo_booking_flags"


def load(fn):
    out = {}
    for line in (TEST / fn).open(encoding="utf-8"):
        d = json.loads(line)
        f, _ = parse_booking_json(
            d["response"]["body"]["choices"][0]["message"]["content"])
        if f:
            out[d["custom_id"].split("|")[0]] = f
    return out


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text or "")
            if len(norm(s).split()) >= 4]


def short(name):
    return name.replace("redo_booking_", "")


def main():
    v5 = load("booking_v5_100_output.jsonl")
    v53 = load("booking_v5_3_100_output.jsonl")
    pids = sorted(set(v5) & set(v53))
    print(f"comparing {len(pids)} products present in both runs")

    moves = Counter()          # (from_v5_col, to_v53_col) -> n sentences
    per_product = []
    fill_v5, fill_v53 = Counter(), Counter()
    words_v5, words_v53 = Counter(), Counter()

    for pid in pids:
        a, b = v5[pid], v53[pid]
        # where each V5 sentence ended up in V5.3
        b_index = {k: norm(v) for k, v in b.items() if k != FLAGS and v}
        prod_moves = []
        for ka, va in a.items():
            if ka == FLAGS or not (va or "").strip():
                continue
            fill_v5[ka] += 1
            words_v5[ka] += len(va.split())
            target = RENAME.get(ka, ka)
            for s in sentences(va):
                ns = norm(s)
                found = [kb for kb, nb in b_index.items() if ns and ns in nb]
                if not found:
                    moves[(short(ka), "LOST")] += 1
                    prod_moves.append((short(ka), "LOST", s[:90]))
                elif target in found:
                    moves[(short(ka), short(target))] += 1
                else:
                    dest = found[0]
                    moves[(short(ka), short(dest))] += 1
                    prod_moves.append((short(ka), short(dest), s[:90]))
        for kb, vb in b.items():
            if kb != FLAGS and (vb or "").strip():
                fill_v53[kb] += 1
                words_v53[kb] += len(vb.split())
        if prod_moves:
            per_product.append((pid, prod_moves))

    L = []
    A = L.append
    A("# Booking V5 → V5.3 — what changed")
    A("")
    A(f"Same {len(pids)} products, same raw input. Every difference below is")
    A("caused by the prompt change and nothing else.")
    A("")
    A("## Column fill: before and after")
    A("")
    A("| Column | V5 | V5.3 | Δ | V5 words | V5.3 words |")
    A("|---|---|---|---|---|---|")
    allcols = sorted(set(list(fill_v5) + list(fill_v53)),
                     key=lambda k: -fill_v53.get(k, 0))
    for k in allcols:
        src = k
        old = fill_v5.get(k, 0)
        # a renamed column's "before" lives under its old name
        for o, nw in RENAME.items():
            if nw == k:
                old = fill_v5.get(o, 0)
                src = f"{short(k)}  *(was {short(o)})*"
                break
        else:
            src = short(k)
        new = fill_v53.get(k, 0)
        mark = " **NEW**" if k in NEW_IN_V5_3 else ""
        wo = words_v5.get(k, 0) or sum(
            words_v5.get(o, 0) for o, nw in RENAME.items() if nw == k)
        A(f"| {src}{mark} | {old} | {new} | {new - old:+d} | {wo:,} | "
          f"{words_v53.get(k, 0):,} |")
    A("")

    A("## Where content moved")
    A("")
    A("Rows where a sentence did NOT stay in its expected column. Movement out")
    A("of `other`/`notes` into a new column is the intended effect. Movement out")
    A("of a column that already worked is what to scrutinise.")
    A("")
    A("| From (V5) | To (V5.3) | Sentences |")
    A("|---|---|---|")
    for (fr, to), n in moves.most_common():
        expected = (to == short(RENAME.get("redo_booking_" + fr, "redo_booking_" + fr))
                    or fr == to)
        if expected:
            continue
        flag = " ⚠️" if to == "LOST" else ""
        A(f"| {fr} | {to}{flag} | {n} |")
    A("")

    lost = sum(n for (fr, to), n in moves.items() if to == "LOST")
    A(f"**Sentences present in V5 but in no V5.3 column: {lost}**")
    A("")

    A("## Per product")
    A("")
    for pid, pm in per_product[:60]:
        name, _ = load_raw(pid)
        A(f"### {pid} — {name[:60]}")
        A("")
        for fr, to, s in pm[:10]:
            A(f"- `{fr}` → `{to}` — {s}")
        if len(pm) > 10:
            A(f"- _…and {len(pm) - 10} more_")
        A("")
    if len(per_product) > 60:
        A(f"_…and {len(per_product) - 60} more products with movement._")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L), encoding="utf-8")

    print(f"\nproducts with content movement: {len(per_product)}")
    print(f"sentences lost between runs   : {lost}")
    print("\nnew columns, products filled:")
    for k in NEW_IN_V5_3:
        print(f"  {short(k):24s} {fill_v53.get(k, 0):4d}/{len(pids)}")
    print(f"\ncatch-all words: V5 {words_v5.get('redo_booking_other', 0):,} "
          f"-> V5.3 {words_v53.get('redo_booking_notes', 0):,}")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
