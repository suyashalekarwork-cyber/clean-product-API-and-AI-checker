"""A/B the same 100 products: SYSTEM_PROMPT_RZ_DESC_V1 vs V1_2.

THE POINT OF AN A/B IS NOT "DID IT GET BETTER". It is "is every difference
explainable by a change we made". V1.2 declares three fixes:

  FIX 1  a Day/Step heading licenses its whole block  -> itinerary should GROW,
         about should SHRINK, and orphaned fragments in about should fall
  FIX 2  a lead-in line moves with its list           -> itinerary values ending
         in ':' should disappear
  FIX 3  Terms & Conditions names disclaimers         -> disclaimers, dead at 0,
         should fill on the 6 products that carry that heading

Anything ELSE that moved is a regression until explained. That is the whole
reason the same 100 products are re-run rather than a fresh sample: with the
products held fixed and only the prompt changed, an unexplained difference has
nowhere to hide.

The Fareharbor V5.4 A/B worked exactly this way and it earned its keep -- 25 of
the 31 "lost" URLs came back and the other 6 turned out to be the scorer's own
regex, which would have been invisible against a different sample.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "data_pipeline" / "batch_api_test"
sys.path.insert(0, str(T))
sys.path.insert(0, str(ROOT / "scripts"))

from booking_common import parse_booking_json                  # noqa: E402
from rezdy_common import RAW_DIR, html_to_markdown             # noqa: E402
from build_rezdy_desc_prompt import COLUMNS                    # noqa: E402

OUT = ROOT / "reports" / "rezdy_v1_vs_v1_2_ab.txt"
A_FILE = T / "rezdy_desc_100_output.jsonl"            # V1
B_FILE = T / "rezdy_desc_100_output_rzd12.jsonl"      # V1.2
PRODUCTS = T / "rezdy_desc_100_products.json"

CONTENT = [c for c in COLUMNS if c != "redo_flags"]
WORD = re.compile(r"[A-Za-z0-9']+")

# Which fix a given field movement is attributable to.
FIX1 = {"redo_desc_itinerary", "redo_desc_about"}
FIX3 = {"redo_desc_disclaimers"}


def load(path):
    out = {}
    for line in path.open(encoding="utf-8"):
        r = json.loads(line)
        f, _ = parse_booking_json(
            r["response"]["body"]["choices"][0]["message"]["content"])
        out[r["custom_id"].split("|")[0]] = f or {}
    return out


def words(t):
    return set(w.lower() for w in WORD.findall(t or ""))


def retention(conv, f):
    r = words(conv)
    o = words(" ".join(str(v) for k, v in f.items() if k != "redo_flags"))
    return 100.0 * len(r & o) / len(r) if r else 100.0


def fragments(text):
    """Short context-free lines -- the orphaned-fragment symptom of FIX 1."""
    return [l for l in (text or "").split("\n")
            if 0 < len(l.split()) <= 6 and l.strip()
            and l.strip()[-1] not in ".!?:"]


def main():
    if not B_FILE.exists():
        raise SystemExit(f"missing {B_FILE.name} -- the V1.2 run has not landed")
    A, B = load(A_FILE), load(B_FILE)
    meta = {p["product_id"]: p
            for p in json.loads(PRODUCTS.read_text(encoding="utf-8"))}
    common = sorted(set(A) & set(B))

    L, add = [], None
    L.append("=" * 78)
    L.append("REZDY A/B -- SYSTEM_PROMPT_RZ_DESC_V1  vs  V1_2")
    L.append("=" * 78)
    L.append("")
    L.append(f"Same {len(common)} products, same supplier text, only the prompt")
    L.append("changed. Every difference must trace to one of the three declared")
    L.append("fixes; anything else is a regression until explained.")
    L.append("")
    L.append("WHAT THIS A/B CANNOT PROVE")
    L.append("-" * 78)
    L.append("There is NO CONTROL RUN. The model is not deterministic: re-running")
    L.append("identical products on an IDENTICAL prompt has previously made 4 of 6")
    L.append("defects vanish. So a small difference here cannot be attributed to")
    L.append("our change rather than to run-to-run variance.")
    L.append("")
    L.append("That is fine for the LARGE movements below -- thousands of words")
    L.append("moving in the predicted direction is not noise. It is NOT fine for")
    L.append("the handful of small unexplained diffs, which is why they are listed")
    L.append("individually rather than counted. Reading them is the only way to")
    L.append("tell a regression from a coin flip.")
    L.append("")

    # ---- headline movements
    stats = Counter()
    itin_a = itin_b = about_a = about_b = 0
    ret_a = ret_b = 0.0
    frag_a = frag_b = 0
    dangling_a = dangling_b = 0
    per_field = {c: [0, 0] for c in CONTENT}
    changed_products, unexplained = [], []

    for pid in common:
        a, b = A[pid], B[pid]
        raw = json.loads(list(RAW_DIR.glob(f"Rezdy-*-{pid}.json"))[0]
                         .read_text(encoding="utf-8"))["product"].get(
                             "description") or ""
        conv = html_to_markdown(raw)
        ret_a += retention(conv, a)
        ret_b += retention(conv, b)
        frag_a += len(fragments(a.get("redo_desc_about")))
        frag_b += len(fragments(b.get("redo_desc_about")))
        if (a.get("redo_desc_itinerary") or "").rstrip().endswith(":"):
            dangling_a += 1
        if (b.get("redo_desc_itinerary") or "").rstrip().endswith(":"):
            dangling_b += 1
        itin_a += len((a.get("redo_desc_itinerary") or "").split())
        itin_b += len((b.get("redo_desc_itinerary") or "").split())
        about_a += len((a.get("redo_desc_about") or "").split())
        about_b += len((b.get("redo_desc_about") or "").split())

        moved = []
        for c in CONTENT:
            va, vb = (a.get(c) or "").strip(), (b.get(c) or "").strip()
            per_field[c][0] += bool(va)
            per_field[c][1] += bool(vb)
            if va == vb:
                continue
            moved.append((c, len(va.split()), len(vb.split())))
        if moved:
            changed_products.append((pid, moved))
            # attributable? itinerary/about movement = FIX 1, disclaimers = FIX 3
            names = {c for c, _, _ in moved}
            if not (names & FIX1 or names & FIX3):
                unexplained.append((pid, moved))
            stats["changed"] += 1
        else:
            stats["identical"] += 1

    n = len(common)
    L.append("HEADLINE")
    L.append("-" * 78)
    L.append(f"  products identical            {stats['identical']:4d} / {n}")
    L.append(f"  products changed              {stats['changed']:4d} / {n}")
    L.append("")
    L.append(f"  mean retention   V1 {ret_a/n:5.1f}%  ->  V1.2 {ret_b/n:5.1f}%")
    L.append("")
    L.append("FIX 1 -- day blocks stay whole")
    L.append(f"  orphaned fragments in About   {frag_a:4d}  ->  {frag_b:4d}"
             f"   ({frag_b-frag_a:+d})")
    L.append(f"  itinerary filled              {per_field['redo_desc_itinerary'][0]:4d}"
             f"  ->  {per_field['redo_desc_itinerary'][1]:4d}")
    L.append(f"  WORDS in itinerary          {itin_a:6,}  ->{itin_b:7,}"
             f"   ({itin_b-itin_a:+,})")
    L.append(f"  WORDS in about              {about_a:6,}  ->{about_b:7,}"
             f"   ({about_b-about_a:+,})")
    L.append("  ^ the count of FILLED products barely moves because the same")
    L.append("    products have an itinerary either way. What moved is the")
    L.append("    CONTENT: whole day blocks left About and went back where the")
    L.append("    supplier put them.")
    L.append("")
    L.append("FIX 2 -- a lead-in moves with its list")
    L.append(f"  itinerary ending in a colon   {dangling_a:4d}  ->  {dangling_b:4d}"
             f"   ({dangling_b-dangling_a:+d})")
    L.append("")
    L.append("FIX 3 -- Terms & Conditions names disclaimers")
    L.append(f"  disclaimers filled            {per_field['redo_desc_disclaimers'][0]:4d}"
             f"  ->  {per_field['redo_desc_disclaimers'][1]:4d}")
    L.append("")

    L.append("EVERY FIELD, BEFORE AND AFTER")
    L.append("-" * 78)
    L.append(f"  {'field':34s} {'V1':>5s} {'V1.2':>6s} {'diff':>6s}")
    for c in CONTENT:
        x, y = per_field[c]
        mark = ""
        if c not in FIX1 | FIX3 and abs(y - x) >= 5:
            mark = "   <-- NOT a declared fix, check this"
        L.append(f"  {c:34s} {x:5d} {y:6d} {y-x:+6d}{mark}")
    L.append("")

    L.append("PRODUCTS WHERE NOTHING TRACES TO A DECLARED FIX")
    L.append("-" * 78)
    if not unexplained:
        L.append("  (none -- every changed product moved itinerary, about or")
        L.append("   disclaimers, which are exactly what the three fixes touch)")
    else:
        L.append(f"  {len(unexplained)} product(s). READ THESE -- a change with no")
        L.append("  declared cause is a regression until proven otherwise.")
        for pid, moved in unexplained[:25]:
            L.append(f"    {pid}: " + ", ".join(
                f"{c.replace('redo_desc_','')} {x}w->{y}w" for c, x, y in moved))
    L.append("")

    L.append("=" * 78)
    L.append("PER PRODUCT -- what moved")
    L.append("=" * 78)
    for pid, moved in changed_products:
        m = meta.get(pid, {})
        L.append("")
        L.append(f"{pid}  {m.get('supplier','?')}  ({m.get('n_headings',0)} headings)")
        for c, x, y in moved:
            L.append(f"    {c.replace('redo_desc_',''):24s} {x:5d} -> {y:5d} words")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(L), encoding="utf-8")

    print(f"identical {stats['identical']}/{n}   changed {stats['changed']}/{n}")
    print(f"retention {ret_a/n:.1f}% -> {ret_b/n:.1f}%")
    print(f"fragments {frag_a} -> {frag_b}")
    print(f"dangling  {dangling_a} -> {dangling_b}")
    print(f"disclaimers {per_field['redo_desc_disclaimers'][0]} -> "
          f"{per_field['redo_desc_disclaimers'][1]}")
    print(f"unexplained products: {len(unexplained)}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
