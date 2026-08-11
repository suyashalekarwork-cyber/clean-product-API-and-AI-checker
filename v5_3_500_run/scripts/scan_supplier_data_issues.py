"""
Broad scan for SUPPLIER data problems in the 500-product raw descriptions.

The first pass only looked for one thing -- a sentence over 40 characters
repeated verbatim -- and found 9 products. That test is narrow by construction:
it cannot see shorter repeats, near-duplicates, empty headings, placeholder
text, or encoding damage. This scans for all of those.

A supplier data problem is something wrong in the RAW text before extraction
touches it. It is not an extraction defect, and in most cases the right fix is
at render time or by asking the supplier -- not by changing the prompt.
"""
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

from build_model_comparison_batches import strip_html, find_raw_file  # noqa: E402
from score_v5_3 import norm, sentences, is_heading_shaped, next_content  # noqa: E402

CTRL = re.compile(r"[\000-\010\013\014\016-\037]")
MOJIBAKE = re.compile(r"â€™|â€œ|â€\x9d|Ã©|Ã¨|Ã¢|â€“|â€”|Â ")
PLACEHOLDER = re.compile(
    r"^\s*(n/?a|tbc|tba|tbd|none|null|coming soon|test|xxx+|lorem ipsum|\.+|-+)\s*$",
    re.I,
)
TEMPLATE_KEY = re.compile(
    r"^\s*(meeting_point|cancellation_summary|duration_text|product_name|"
    r"description|highlights|what_included|price|image_url)\s*:", re.I)
URL = re.compile(r"https?://\S+")
EMAIL_PHONE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\b(?:\+?61|0)[2-478](?:[ -]?\d){8}\b")


def near_dupe_pairs(sents, floor=0.85):
    """Sentence pairs that are almost the same. Catches the repeats an exact
    match misses -- a supplier pasting a line and then editing a word."""
    out = []
    ns = [(s, set(norm(s).split())) for s in sents if len(norm(s)) > 25]
    for i in range(len(ns)):
        for j in range(i + 1, len(ns)):
            a, b = ns[i][1], ns[j][1]
            if not a or not b:
                continue
            jac = len(a & b) / len(a | b)
            if jac >= floor and ns[i][0] != ns[j][0]:
                out.append((ns[i][0][:70], ns[j][0][:70], round(jac, 2)))
    return out


def main():
    rows = [json.loads(l) for l in (TEST_DIR / "v5_3_hard500_output.jsonl").open(encoding="utf-8")]
    found = defaultdict(list)

    for row in rows:
        pid = row["custom_id"].split("|")[0]
        item = json.loads(Path(find_raw_file(pid)).read_text(encoding="utf-8"))["item"]
        sd = item.get("structured_description") or {}
        raw = strip_html(sd.get("description") or item.get("description") or "")
        lines = [l for l in raw.split("\n")]
        sents = sentences(raw)

        # A. exact self-duplication, at ANY length (the first pass used >40 chars)
        ns = [norm(s) for s in sents if len(norm(s)) > 15]
        dup = [s for s, n in Counter(ns).items() if n > 1]
        if dup:
            found["A_exact_repeat"].append((pid, f"{len(dup)} repeated line(s): {dup[0][:60]!r}"))

        # B. near-duplicates -- same line lightly edited
        nd = near_dupe_pairs(sents)
        if nd and not dup:
            found["B_near_repeat"].append((pid, f"{nd[0][0]!r} ~= {nd[0][1]!r} ({nd[0][2]})"))

        # C. a heading with nothing under it
        empty = []
        for i, l in enumerate(lines):
            if is_heading_shaped(l, next_content(lines, i)) or (
                    l.strip() and len(l.split()) <= 6 and not l.strip()[-1:] in ".!?"):
                nxt = next_content(lines, i)
                if not nxt.strip() and l.strip():
                    empty.append(l.strip())
        if empty:
            found["C_empty_heading"].append((pid, f"{len(empty)}: {empty[:3]}"))

        # D. placeholder values the supplier never filled in
        ph = [l.strip() for l in lines if PLACEHOLDER.match(l or "")]
        if ph:
            found["D_placeholder"].append((pid, str(ph[:3])))

        # E. a template/field key pasted into the description
        tk = [l.strip() for l in lines if TEMPLATE_KEY.match(l or "")]
        if tk:
            found["E_template_key"].append((pid, str(tk[:3])))

        # F. encoding damage
        if CTRL.search(raw):
            found["F_control_chars"].append((pid, f"{len(CTRL.findall(raw))} control char(s)"))
        if MOJIBAKE.search(raw):
            found["F_mojibake"].append((pid, MOJIBAKE.search(raw).group(0)))
        if "�" in raw:
            found["F_replacement_char"].append((pid, f"{raw.count(chr(0xfffd))}x U+FFFD"))

        # G. booking links / contact details inside the description
        if URL.search(raw):
            found["G_url_in_description"].append((pid, URL.search(raw).group(0)[:60]))
        if EMAIL_PHONE.search(raw):
            found["G_contact_in_description"].append((pid, EMAIL_PHONE.search(raw).group(0)))

        # H. effectively no description at all
        if len(norm(raw).split()) < 12:
            found["H_almost_empty"].append((pid, repr(raw[:70])))

    print("=" * 84)
    print("SUPPLIER DATA PROBLEMS IN THE RAW -- 499 products")
    print("=" * 84)
    order = ["A_exact_repeat", "B_near_repeat", "C_empty_heading", "D_placeholder",
             "E_template_key", "F_control_chars", "F_mojibake", "F_replacement_char",
             "G_url_in_description", "G_contact_in_description", "H_almost_empty"]
    affected = set()
    for k in order:
        v = found.get(k, [])
        if not v:
            continue
        affected |= {p for p, _ in v}
        print(f"\n{k}  --  {len(v)} products ({100*len(v)/len(rows):.1f}%)")
        for pid, note in v[:6]:
            print(f"    {pid}  {note[:92]}")
        if len(v) > 6:
            print(f"    ... and {len(v)-6} more")
    print("\n" + "=" * 84)
    print(f"DISTINCT products with at least one supplier data problem: "
          f"{len(affected)} of {len(rows)}  ({100*len(affected)/len(rows):.1f}%)")
    out = TEST_DIR / "supplier_data_issues.json"
    out.write_text(json.dumps({k: v for k, v in found.items()}, indent=1), encoding="utf-8")
    print(f"wrote {out.name}")


if __name__ == "__main__":
    main()
