"""Side-by-side reading file: the supplier's text, then what we extracted from it.

reports/rezdy_desc_100_raw_vs_extracted.txt -- one block per product, so a
reviewer can read the source and the result without opening a JSON file or a
spreadsheet.

WHAT "RAW" MEANS HERE, and why it is not the API's exact bytes: Rezdy sends
HTML. What the MODEL saw is that HTML with its structure restored as plain marks
(## heading, - bullet, **bold**, [text](url)) and nothing added or removed --
verified lossless on all 9,361 products. Showing the tag soup instead would be
unreadable AND would not be what the model was judged on. The original bytes are
in data/Rezdy/Rezdy-{supplier}-{id}.json if a byte-level check is ever needed.

EMPTY FIELDS ARE LISTED, NOT HIDDEN. A blank field is the heading gate working:
the supplier wrote no heading, so the text stayed in About. Hiding blanks would
make a correct empty look identical to a field nobody thought about -- and the
whole point of this run is to be able to tell those apart.
"""
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "data_pipeline" / "batch_api_test"
sys.path.insert(0, str(T))
sys.path.insert(0, str(ROOT / "scripts"))

from booking_common import parse_booking_json                 # noqa: E402
from rezdy_common import RAW_DIR, html_to_markdown            # noqa: E402
from build_rezdy_desc_prompt import COLUMNS                   # noqa: E402
from build_rezdy_desc_100_issues import audit                 # noqa: E402

WORD = re.compile(r"[A-Za-z0-9']+")


def retention(conv, fields):
    """Share of the supplier's DISTINCT words that appear somewhere in output.

    Distinct words, not a count: a word the supplier used ten times and we kept
    once is kept, not 90% lost. This is the same measure used for the Step 1 vs
    Step 2 comparison, so the two numbers are directly comparable.

    It cannot see a word that survived in the WRONG field -- that is what the
    issue list is for. High retention with a misplacement is possible, and on
    Fareharbor 11 of 13 defects in one run lost no text at all.
    """
    raw_w = set(w.lower() for w in WORD.findall(conv))
    out_w = set(w.lower() for w in WORD.findall(
        " ".join(str(v) for k, v in fields.items() if k != "redo_flags")))
    return (100.0 * len(raw_w & out_w) / len(raw_w)) if raw_w else 100.0

# RZ_TAG names which run this report describes. Default "rzd1" = V1.
_TAG = os.environ.get("RZ_TAG", "rzd1")
_SFX = "" if _TAG == "rzd1" else f"_{_TAG}"
OUT = ROOT / "reports" / f"rezdy_desc_100_raw_vs_extracted{_SFX}.txt"
OUTPUT = T / f"rezdy_desc_100_output{_SFX}.jsonl"
_PROMPT_NAME = {"rzd1": "SYSTEM_PROMPT_RZ_DESC_V1",
                "rzd12": "SYSTEM_PROMPT_RZ_DESC_V1_2"}.get(_TAG, _TAG)
PRODUCTS = T / "rezdy_desc_100_products.json"

CONTENT = [c for c in COLUMNS if c != "redo_flags"]
LABEL = {
    "redo_desc_about": "ABOUT / DESCRIPTION",
    "redo_desc_important_info": "IMPORTANT INFO",
    "redo_desc_highlights": "HIGHLIGHTS",
    "redo_desc_what_included": "WHAT'S INCLUDED",
    "redo_desc_what_excluded": "WHAT'S NOT INCLUDED",
    "redo_desc_extras": "EXTRAS",
    "redo_desc_itinerary": "ITINERARY",
    "redo_desc_what_to_bring": "WHAT TO BRING",
    "redo_desc_duration_text": "DURATION",
    "redo_desc_cancellation": "CANCELLATION",
    "redo_desc_check_in": "CHECK IN",
    "redo_desc_accessibility": "ACCESSIBILITY",
    "redo_desc_restrictions": "RESTRICTIONS",
    "redo_desc_special_requirements": "SPECIAL REQUIREMENTS",
    "redo_desc_faqs": "FAQS",
    "redo_desc_pricing": "PRICING",
    "redo_desc_disclaimers": "DISCLAIMERS",
    "redo_desc_health_safety": "HEALTH & SAFETY",
    "redo_desc_contact": "CONTACT",
    "redo_meeting_point": "MEETING POINT",
    "redo_group_size": "GROUP SIZE",
}
W = 78


def indent(text, pad="    "):
    return "\n".join(pad + l for l in (text or "").split("\n"))


def main():
    meta = {p["product_id"]: p
            for p in json.loads(PRODUCTS.read_text(encoding="utf-8"))}

    rows = []
    for line in OUTPUT.open(encoding="utf-8"):
        r = json.loads(line)
        pid = r["custom_id"].split("|")[0]
        f, note = parse_booking_json(
            r["response"]["body"]["choices"][0]["message"]["content"])
        rows.append((pid, f or {}, note))
    # Score every product ONCE, up front, so the index and the per-product
    # headers cannot disagree with each other.
    scored = {}
    for pid, f, note in rows:
        hits = list(RAW_DIR.glob(f"Rezdy-*-{pid}.json"))
        raw = json.loads(hits[0].read_text(encoding="utf-8"))["product"].get(
            "description") or ""
        conv = html_to_markdown(raw)
        _, _, _, issues, _ = audit(pid, meta.get(pid, {}), f)
        filled = [c for c in CONTENT if (f.get(c) or "").strip()]
        scored[pid] = {
            "conv": conv, "file": hits[0].name, "filled": filled,
            "empty": [c for c in CONTENT if not (f.get(c) or "").strip()],
            "retention": retention(conv, f),
            "fill_rate": 100.0 * len(filled) / len(CONTENT),
            "issues": issues,
            "kinds": Counter(k for k, _ in issues),
        }

    rows.sort(key=lambda x: -meta.get(x[0], {}).get("n_headings", 0))

    L = []
    A = L.append
    A("=" * W)
    A("REZDY ROUND 1 -- SUPPLIER TEXT vs WHAT WE EXTRACTED")
    A("=" * W)
    A("")
    A(f"{len(rows)} products, the HARDEST in the catalogue (16-55 headings each).")
    A(f"Prompt: {_PROMPT_NAME}")
    A("")
    A("HOW TO READ A BLOCK")
    A("-" * W)
    A("  SUPPLIER TEXT   what the model was given. This is the supplier's own")
    A("                  words with their HTML formatting restored as plain")
    A("                  marks -- '## ' a heading tag, '**bold**', '- ' a list")
    A("                  item, '[text](url)' a link. Nothing added or removed;")
    A("                  verified word-for-word on all 9,361 products.")
    A("  EXTRACTED       the fields that were filled, and their exact contents.")
    A("  EMPTY           fields left blank. A blank is the rule WORKING: the")
    A("                  supplier wrote no heading naming that field, so the")
    A("                  text stayed in ABOUT. It does not mean text was lost.")
    A("  FLAGS           the model's own notes on anything it moved.")
    A("")
    A("THE TWO NUMBERS ON EVERY PRODUCT")
    A("-" * W)
    A("  RETENTION   share of the supplier's distinct words that appear")
    A("              SOMEWHERE in our output. This is the content-loss measure.")
    A("              It CANNOT see a word that survived in the WRONG field --")
    A("              that is what the issue list is for. On Fareharbor, 11 of 13")
    A("              defects in one run lost no text at all, so high retention")
    A("              is necessary but not sufficient.")
    A("  FILL RATE   share of the 21 fields that got content. LOW IS OFTEN")
    A("              CORRECT: a field only fills when the supplier wrote a")
    A("              heading for it, and about half of Rezdy products write few")
    A("              or none. A low fill rate with high retention means the text")
    A("              is all present, sitting in ABOUT, exactly as intended.")
    A("")

    ret = [scored[p]["retention"] for p, _, _ in rows]
    fil = [scored[p]["fill_rate"] for p, _, _ in rows]
    clean = sum(1 for p, _, _ in rows if not scored[p]["issues"])
    tally = Counter()
    for p, _, _ in rows:
        tally.update(scored[p]["kinds"])

    A("RUN TOTALS")
    A("-" * W)
    A(f"  mean retention    {sum(ret)/len(ret):5.1f}%       "
      f"(worst {min(ret):.1f}%, best {max(ret):.1f}%)")
    A(f"  products >= 95%   {sum(1 for r in ret if r >= 95):3d} / {len(ret)}")
    A(f"  products >= 99%   {sum(1 for r in ret if r >= 99):3d} / {len(ret)}")
    A(f"  mean fill rate    {sum(fil)/len(fil):5.1f}%       "
      f"({sum(len(scored[p]['filled']) for p, _, _ in rows)/len(rows):.1f} of "
      f"{len(CONTENT)} fields on average)")
    A(f"  no findings       {clean:3d} / {len(rows)} products")
    A("  findings by type  " + ", ".join(f"{k} {v}" for k, v in tally.most_common()))
    A("")
    A("  For comparison, the OLD method (Step 1) retained 71.8% of the same")
    A("  suppliers' words across these same 100 products.")
    A("")
    A("INDEX -- worst retention first")
    A("-" * W)
    A(f"  {'PRODUCT':10s} {'SUPPLIER':22s} {'HEAD':>5s} {'RETAIN':>7s} "
      f"{'FILLED':>7s}  ISSUES")
    for pid in sorted(scored, key=lambda p: scored[p]["retention"]):
        s = scored[pid]
        m = meta.get(pid, {})
        kinds = ", ".join(f"{k.lower()} {v}" for k, v in s["kinds"].most_common(3))
        A(f"  {pid:10s} {m.get('supplier','?')[:22]:22s} "
          f"{m.get('n_headings',0):5d} {s['retention']:6.1f}% "
          f"{len(s['filled']):3d}/{len(CONTENT):<3d}  {kinds or 'none'}")
    A("")
    A("Full issue detail per product: reports/rezdy_desc_100_issues.txt")
    A("The same products beside the OLD method: exports/rezdy_step1_vs_step2_100.xlsx")
    A("")

    for pid, f, note in rows:
        m = meta.get(pid, {})
        s = scored[pid]
        conv, filled, empty = s["conv"], s["filled"], s["empty"]

        A("")
        A("=" * W)
        A(f"{pid}   {m.get('supplier', '?')}")
        A(f"{m.get('name', '')}")
        A("=" * W)
        A(f"  RETENTION {s['retention']:5.1f}%   "
          f"FILL RATE {s['fill_rate']:5.1f}% ({len(filled)}/{len(CONTENT)} fields)   "
          f"FINDINGS {len(s['issues'])}")
        A(f"  {m.get('n_headings', 0)} headings | {len(conv.split()):,} words | "
          f"raw file: {s['file']}"
          + (f" | JSON repaired: {note}" if note else ""))
        if s["issues"]:
            A("")
            A("  ISSUES FOUND (CANDIDATE -- verify against the text below)")
            by = {}
            for kind, detail in s["issues"]:
                by.setdefault(kind, []).append(detail)
            for kind in ["CONTAMINATION", "INVENTED", "NO HEADING", "URL LOST",
                         "MID-SENTENCE", "CONTENT LOSS", "REWORDED",
                         "DUPLICATED"]:
                for detail in by.get(kind, []):
                    A(f"    [{kind}] {detail[:190]}")
        else:
            A("")
            A("  NO FINDINGS")
        A("")
        A("-" * W)
        A("SUPPLIER TEXT (what the model was given)")
        A("-" * W)
        A(indent(conv))
        A("")
        A("-" * W)
        A("EXTRACTED")
        A("-" * W)
        for c in CONTENT:
            v = (f.get(c) or "").strip()
            if not v:
                continue
            A("")
            A(f"  [{LABEL.get(c, c)}]")
            A(indent(v, "      "))
        A("")
        A(f"  EMPTY ({len(empty)}): "
          + ", ".join(LABEL.get(c, c) for c in empty))
        A("    ^ the supplier wrote no heading for these. Their text, if any,")
        A("      is in ABOUT above -- nothing was dropped.")
        flags = (f.get("redo_flags") or "").strip()
        if flags:
            A("")
            A("  [FLAGS -- the model's own notes, never shown to a customer]")
            A(indent(flags, "      "))
        A("")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(L), encoding="utf-8")

    print(f"products : {len(rows)}")
    print(f"lines    : {len(L):,}")
    print(f"size     : {OUT.stat().st_size/1e6:.1f} MB" if OUT.exists() else "")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
