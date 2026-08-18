"""
Review file for the products with no proper heading.

These are the ones where the heading gate should send EVERYTHING to about --
they are the test of whether the gate holds when the supplier gave it nothing to
work with. Roughly half the catalogue looks like this, so it matters more than
the flagged-defect list.

Three groups, easiest to check first:

  1. FILLED A COLUMN ANYWAY   the interesting ones. Either the gate leaked, or
                              the model saw a heading this script's regex cannot.
                              Spot-checking says it is usually the latter --
                              e.g. "Your Day in the Hunter Valley begins at:"
                              (8 words; the regex caps at 7), "Cost: $79 per
                              adult" (inline label), "Accessebility" (supplier
                              typo the model still matched by meaning).
  2. HEADINGS, NONE MAPPED    supplier wrote headings that name no column.
  3. NO HEADINGS AT ALL       pure prose. Everything belongs in about.

Group membership is decided by THIS SCRIPT's heading detector, which is
deliberately strict. "No heading" here means "no heading my regex could see",
not "no heading exists".

Writes reports/v5_3_no_heading_review.txt
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = ROOT / "data_pipeline" / "batch_api_test"
sys.path.insert(0, str(TEST_DIR))

from build_model_comparison_batches import strip_html, find_raw_file  # noqa: E402
from score_v5_3 import is_heading_shaped, next_content  # noqa: E402

OUT = ROOT / "reports" / "v5_3_no_heading_review.txt"
NICE = lambda k: k.replace("redo_desc_", "").replace("redo_", "")  # noqa: E731


def load(fn):
    out = {}
    for line in (TEST_DIR / fn).open(encoding="utf-8"):
        d = json.loads(line)
        out[d["custom_id"].split("|")[0]] = json.loads(
            d["response"]["body"]["choices"][0]["message"]["content"]
        )
    return out


def main():
    outs = load("v5_3_hard500_output.jsonl")
    scores = json.loads((TEST_DIR / "v5_3_hard500_scores.json").read_text(encoding="utf-8"))

    rows = []
    for pid, fields in outs.items():
        item = json.loads(Path(find_raw_file(pid)).read_text(encoding="utf-8"))["item"]
        sd = item.get("structured_description") or {}
        raw = strip_html(sd.get("description") or item.get("description") or "")
        lines = raw.split("\n")
        heads = [l.strip() for i, l in enumerate(lines)
                 if is_heading_shaped(l, next_content(lines, i))]
        cols = scores.get(pid, {}).get("headings_naming_a_column") or []
        if cols:
            continue                                    # has a mapped heading; not our concern
        non_about = [k for k, v in fields.items()
                     if (v or "").strip() and k not in ("redo_flags", "redo_desc_about")]
        rows.append({
            "pid": pid, "name": item.get("name") or "", "raw": raw,
            "fields": fields, "heads": heads, "non_about": non_about,
            "group": 1 if non_about else (2 if heads else 3),
        })
    rows.sort(key=lambda r: (r["group"], r["pid"]))

    g = {1: [], 2: [], 3: []}
    for r in rows:
        g[r["group"]].append(r)

    L = []
    A = L.append
    A("=" * 100)
    A("V5.3 -- PRODUCTS WITH NO PROPER HEADING")
    A("=" * 100)
    A("")
    A("These are the products where the supplier gave the extraction gate nothing to work")
    A("with. The rule says: no heading naming a column -> everything stays in about. About")
    A("half the run looks like this, so whether the gate holds here matters more than the")
    A("defect list does.")
    A("")
    A("CAVEAT: group membership is decided by this script's heading regex, which is")
    A("deliberately strict (<=7 words, Title Case or ALL CAPS or ends with ':'). 'No")
    A("heading' below means 'none my regex could see', NOT 'none exists'. Spot-checking")
    A("group 1 found the model was usually right and the regex was blind -- it caught")
    A("'Your Day in the Hunter Valley begins at:' (8 words), the inline 'Cost: $79 per")
    A("adult', and 'Accessebility' misspelled by the supplier. Finding those is exactly")
    A("why extraction uses a language model rather than a string matcher.")
    A("")
    A(f"  GROUP 1  filled a column anyway, worth checking : {len(g[1])}")
    A(f"  GROUP 2  had headings, none named a column      : {len(g[2])}")
    A(f"  GROUP 3  no headings at all -- pure prose       : {len(g[3])}")
    A(f"  TOTAL                                          : {len(rows)} of {len(outs)} products")
    A("")
    A("IDs at a glance:")
    for n, label in ((1, "GROUP 1"), (2, "GROUP 2"), (3, "GROUP 3")):
        ids = [r["pid"] for r in g[n]]
        A(f"  {label} ({len(ids)}):")
        for i in range(0, len(ids), 12):
            A("      " + "  ".join(ids[i:i + 12]))
    A("")

    TITLE = {
        1: "GROUP 1 -- NO MAPPED HEADING, BUT A COLUMN WAS FILLED ANYWAY  (check these first)",
        2: "GROUP 2 -- HEADINGS PRESENT, NONE NAMES A COLUMN  (all content should be in about)",
        3: "GROUP 3 -- NO HEADINGS AT ALL  (pure prose; all content should be in about)",
    }
    for n in (1, 2, 3):
        A("")
        A("=" * 100)
        A(TITLE[n])
        A("=" * 100)
        for r in g[n]:
            A("")
            A("-" * 100)
            A(f"{r['pid']}  |  {r['name']}")
            A("-" * 100)
            if r["heads"]:
                A(f"  headings my regex saw: {r['heads'][:8]}")
            else:
                A("  headings my regex saw: none")
            if r["non_about"]:
                A(f"  >>> FILLED BESIDES ABOUT: {[NICE(k) for k in r['non_about']]}")
                A("      Check the raw below for a heading the regex missed before calling this a leak.")
            A("")
            A("  --- RAW ---")
            for line in r["raw"].split("\n"):
                A("  | " + line.rstrip())
            A("  --- EXTRACTED ---")
            for k, v in r["fields"].items():
                if not (v or "").strip() or k == "redo_flags":
                    continue
                A(f"  [{NICE(k).upper()}]")
                for line in str(v).split("\n"):
                    A("      " + line.rstrip())
            if (r["fields"].get("redo_flags") or "").strip():
                A(f"  [MODEL FLAGS] {r['fields']['redo_flags']}")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"  group 1 (filled anyway) : {len(g[1])}")
    print(f"  group 2 (unmapped heads): {len(g[2])}")
    print(f"  group 3 (no headings)   : {len(g[3])}")
    print(f"  total {len(rows)} of {len(outs)}   {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
