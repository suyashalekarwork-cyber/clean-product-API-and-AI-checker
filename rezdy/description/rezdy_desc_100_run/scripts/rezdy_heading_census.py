"""Rezdy heading census -- does heading-gating transfer from Fareharbor?

The V5 prompt only works when the supplier WROTE a heading naming the field.
That was measured true for Fareharbor before the prompt was written (8,244
booking products, 17,212 headings, 3,729 distinct wordings). Nobody has
measured it for Rezdy. This does that, and nothing else -- no extraction,
no prompt, no LLM call.

THE ONE THING THAT MAKES THIS DIFFERENT FROM THE FAREHARBOR CENSUS:
Rezdy's raw text is HTML (<h2>Where to meet</h2>, <p>, <strong>), while
Fareharbor's is markdown. booking_common.heading_of() reads markdown markers,
so running it on Rezdy's raw string finds almost nothing -- a false negative
that would read as "Rezdy has no headings" and kill the port for the wrong
reason. So HTML is converted to the marker syntax the detector expects
FIRST, and the conversion is reported alongside the result so the number can
be audited.

Counts are reported per FIELD (description / additionalInformation / terms),
because they are three different kinds of text and may not answer the same way.

Heading importance is ranked by HOW MANY DISTINCT SUPPLIERS use it, not by raw
frequency -- one supplier with 400 products writing "What to bring" is one
vote, not 400. This is the same rule reports/booking_column_definitions.md used.
"""
import html
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "Rezdy"
OUT = ROOT / "reports" / "rezdy_heading_census.md"

sys.path.insert(0, str(ROOT / "data_pipeline" / "batch_api_test"))
from booking_common import heading_of  # noqa: E402

FIELDS = ["description", "additionalInformation", "terms"]

# Block-level tags. Per CLAUDE.md, suppliers write these back-to-back with NO
# whitespace between them, so stripping tags naively mashes paragraphs together.
BLOCK = re.compile(
    r"</?(?:p|div|br|ul|ol|li|tr|table|h[1-6]|section|article)\b[^>]*>",
    re.I,
)
H_TAG = re.compile(r"<h([1-6])\b[^>]*>(.*?)</h\1>", re.I | re.S)
LI_TAG = re.compile(r"<li\b[^>]*>(.*?)</li>", re.I | re.S)
# A block whose ENTIRE visible content is bold -- that is the HTML equivalent of
# markdown's **Heading**. A <strong> mid-sentence is emphasis and must NOT
# become a heading marker, so this is anchored to the whole block.
BOLD_BLOCK = re.compile(
    r"^\s*<(strong|b)\b[^>]*>(.*?)</\1>\s*:?\s*$", re.I | re.S
)
# NOT <[^>]+> -- a '>' inside a quoted attribute value ends the match early and
# leaks the rest of the tag out as visible text. Measured: Word-pasted styles
# like mso-fareast-language:EN-AU" leaked 'EN-AU">' and it scored as an ALL-CAPS
# heading across 9 suppliers. Quoted runs must be consumed as units.
ANY_TAG = re.compile(r"""<(?:[^>"']|"[^"]*"|'[^']*')*>""")

# Suppliers use <h5> (and bold) for ordinary PROSE, not just section headings --
# barossaoutdoors writes four full sentences inside <h5>. Fareharbor's markdown
# never did this, so the Fareharbor census needed no such guard. A heading is
# short and does not end like a sentence; this mirrors the guard booking_common
# already applies to its own ALL-CAPS case.
MAX_HEAD_WORDS = 12


def is_headinglike(t):
    """Short, and doesn't end like a sentence. Rejects prose in <h5>/<strong>."""
    if not t or len(t.split()) > MAX_HEAD_WORDS or len(t) > 60:
        return False
    return t.rstrip()[-1] not in ".!?,;"


def _text(s):
    """Tags out, entities decoded, whitespace normalised. No newlines added."""
    s = ANY_TAG.sub(" ", s)
    s = html.unescape(s)
    return re.sub(r"[ \t ]+", " ", s).strip()


def html_to_markers(raw):
    """Rezdy HTML -> the marker syntax booking_common.heading_of() reads.

    <h1-6>   -> '## text'      (unambiguous heading, same as markdown)
    <li>     -> '- text'       (a bullet is never a heading -- must survive)
    bold-only block -> '**text**'
    other block tags -> newline
    """
    if not isinstance(raw, str) or not raw.strip():
        return []

    def _h(m):
        t = _text(m.group(2))
        # Prose inside <h5> stays prose. Marking it '##' would make whole
        # sentences read as headings -- 4 of 10 on barossaoutdoors PB5S7C.
        return ("\n## " + t + "\n") if is_headinglike(t) else ("\n" + t + "\n")

    # Word-pasted markup carries literal newlines INSIDE tag attributes
    # (`...mso-ligatures:none;\r\nmso-fareast-language:EN-AU">`). The split("\n")
    # below would cut such a tag in half, leaving a fragment with no opening '<'
    # that survives tag-stripping and scores as an ALL-CAPS heading. Flatten
    # tag-internal whitespace before anything looks at line structure.
    raw = ANY_TAG.sub(lambda m: re.sub(r"\s+", " ", m.group(0)), raw)

    # In HTML a newline in CONTENT is whitespace, not a line break -- only <br>
    # and the block tags break a line. Rezdy's Word-pasted text is hard-wrapped
    # mid-sentence, so honouring those newlines split "We look\r\nforward to
    # seeing you" and left "We look" scoring as a heading. Blank the content
    # newlines and let ONLY the block tags below introduce line structure.
    # Conditional on the field actually being HTML: `terms` is 3,354/3,377 PLAIN
    # TEXT, where the newlines are the only structure there is.
    if BLOCK.search(raw):
        raw = re.sub(r"[\r\n]+", " ", raw)

    s = H_TAG.sub(_h, raw)
    s = LI_TAG.sub(lambda m: "\n- " + _text(m.group(1)) + "\n", s)
    s = BLOCK.sub("\n", s)

    lines = []
    for chunk in s.split("\n"):
        if not chunk.strip():
            continue
        m = BOLD_BLOCK.match(chunk.strip())
        if m:
            inner = _text(m.group(2))
            # A whole PARAGRAPH in bold is emphasis, not a heading, and neither
            # is a bold marketing tagline ("Great Wines. Great Company. Book
            # Your Tasting Today." -- mcguigan PUNFFB).
            if inner:
                lines.append("**" + inner + "**" if is_headinglike(inner) else inner)
                continue
        t = _text(chunk)
        if t:
            lines.append(t)
    return lines


def headings_in(lines):
    out = []
    for i, line in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        h = heading_of(line, nxt)
        if h and h.strip():
            out.append(h.strip())
    return out


def norm(h):
    """Fold wordings that differ only by case/punctuation/whitespace."""
    return re.sub(r"[^a-z0-9 ]+", " ", h.lower()).strip()


# THE DECIDING MEASURE. "Has a heading" is not the question -- Fareharbor proved
# most supplier headings are TOPIC headings (MEALS, TAXI, Tiaki Promise) that
# never match a column, and CLAUDE.md is explicit that adding patterns for them
# is classification by meaning, the thing V5 replaced. What decides whether
# heading-gating transfers is how many products have a heading naming a field we
# actually ship. Deliberately conservative: substring match on unambiguous stems
# only, no synonym guessing.
# ORDER IS LOAD-BEARING and this is a list, not a dict, to make that visible.
# `what_excluded` MUST be tested before `what_included`: "What's Not Included"
# contains "included", and inclusion-first mapped it to what_included -- caught
# on adventuredaytrips-PRLBHU by the raw-text verification, not by review. Same
# class as the MEETING TIME/PLACE-vs-departure ordering bug in CLAUDE.md.
COLUMN_STEMS = [
    ("what_excluded", ["exclusion", "not included", "excludes", "excluded",
                       "what s not included", "doesn t include",
                       "does not include", "not inclusive"]),
    ("what_included", ["inclusion", "what s included", "what is included",
                       "includes", "included", "tour includes", "price includes"]),
    ("highlights", ["highlight"]),
    ("itinerary", ["itinerary", "what to expect", "the day", "schedule"]),
    ("what_to_bring", ["what to bring", "please bring", "bring with you",
                       "what to wear", "what you need"]),
    ("meeting_point", ["meeting point", "meeting location", "where to meet",
                       "where we meet", "getting there", "directions",
                       "departure point", "pick up", "pickup"]),
    ("cancellation", ["cancellation", "refund"]),
    ("important_info", ["important information", "important note", "please note",
                        "good to know", "need to know", "before you"]),
    ("restrictions", ["restriction", "requirement", "age limit", "fitness"]),
    ("check_in", ["check in", "arrival time", "checkin"]),
    ("duration", ["duration", "how long"]),
    ("accessibility", ["accessib", "mobility", "wheelchair"]),
]


def maps_to_column(n):
    """Return the column a normalised heading names, or None. Order matters."""
    for col, stems in COLUMN_STEMS:
        for s in stems:
            if s in n:
                return col
    return None


def main():
    files = sorted(RAW_DIR.glob("*.json"))
    print(f"Reading {len(files)} files from {RAW_DIR} ...")

    stats = {f: {
        "present": 0, "with_heading": 0, "headings": 0,
        "counts": Counter(), "suppliers": defaultdict(set),
        "per_product": Counter(), "html": 0,
    } for f in FIELDS}

    products = 0
    skipped = 0
    any_field_heading = 0
    any_field_mapped = 0
    per_product_total = Counter()
    col_products = defaultdict(set)
    col_suppliers = defaultdict(set)

    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            skipped += 1
            continue
        # Rezdy nests everything under "product" (Critical Rule 6).
        p = data.get("product", data)
        if not isinstance(p, dict) or "error" in data:
            skipped += 1
            continue
        products += 1

        # Product ID = LAST hyphen segment of the filename; supplierAlias can
        # itself contain hyphens, so never index a fixed position.
        supplier = p.get("supplierAlias") or path.stem.rsplit("-", 1)[0]

        pid = path.stem.rsplit("-", 1)[-1]
        total_here = 0
        mapped_here = False
        for f in FIELDS:
            raw = p.get(f)
            if not isinstance(raw, str) or not raw.strip():
                continue
            st = stats[f]
            st["present"] += 1
            if "<" in raw and ">" in raw:
                st["html"] += 1
            hs = headings_in(html_to_markers(raw))
            st["per_product"][len(hs)] += 1
            if hs:
                st["with_heading"] += 1
                st["headings"] += len(hs)
                total_here += len(hs)
                for h in hs:
                    n = norm(h)
                    if n:
                        st["counts"][n] += 1
                        st["suppliers"][n].add(supplier)
                        col = maps_to_column(n)
                        if col:
                            mapped_here = True
                            col_products[col].add(pid)
                            col_suppliers[col].add(supplier)
        per_product_total[total_here] += 1
        if total_here:
            any_field_heading += 1
        if mapped_here:
            any_field_mapped += 1

    write_report(products, skipped, stats, any_field_heading, per_product_total,
                 any_field_mapped, col_products, col_suppliers)


def write_report(products, skipped, stats, any_field_heading, per_product_total,
                 any_field_mapped, col_products, col_suppliers):
    L = []
    A = L.append
    A("# Rezdy Heading Census")
    A("")
    A("Does heading-gated extraction (V5.3/V5.4, built for Fareharbor) transfer "
      "to Rezdy? A field only fills when the supplier wrote a heading naming it, "
      "so the whole approach depends on Rezdy suppliers writing headings.")
    A("")
    A("**Rezdy's raw text is HTML, not markdown.** `<h2>Where to meet</h2>`, "
      "`<p>`, `<strong>` -- where Fareharbor writes `##Departure`. Running "
      "`booking_common.heading_of()` on the raw string finds almost nothing, "
      "which would read as \"Rezdy has no headings\" and be wrong. This census "
      "converts HTML to the markers the detector expects first:")
    A("")
    A("| Rezdy HTML | converted to | treated as |")
    A("|---|---|---|")
    A("| `<h1>`-`<h6>` | `## text` | heading |")
    A("| `<li>` | `- text` | bullet, never a heading |")
    A("| a block that is ENTIRELY `<strong>`/`<b>`, <=60 chars | `**text**` | heading |")
    A("| `<strong>` mid-sentence | plain text | emphasis, NOT a heading |")
    A("| `<p>` `<div>` `<br>` `<ul>` `<table>` | newline | block boundary |")
    A("")
    A(f"Products read: **{products:,}**  ·  unreadable/error stubs skipped: {skipped}")
    A("")
    A("## Headline answer")
    A("")
    pct = 100.0 * any_field_heading / products if products else 0
    A(f"**{any_field_heading:,} of {products:,} products ({pct:.1f}%) have at "
      f"least one heading in at least one text field.**")
    A("")
    mpct = 100.0 * any_field_mapped / products if products else 0
    A(f"**{any_field_mapped:,} ({mpct:.1f}%) have at least one heading that "
      f"NAMES A COLUMN WE SHIP.** This is the number that decides the port, not "
      f"the one above. Fareharbor proved most supplier headings are topic "
      f"headings (`MEALS`, `TAXI`, `Tiaki Promise`) that will never match a "
      f"column, and writing patterns for those is classification by meaning -- "
      f"the thing heading-gating replaced.")
    A("")
    A("### Which columns Rezdy suppliers actually name")
    A("")
    A("| Column | Products | % of catalogue | Distinct suppliers |")
    A("|---|---|---|---|")
    for col in sorted(col_products, key=lambda c: -len(col_products[c])):
        n = len(col_products[col])
        A(f"| `{col}` | {n:,} | {100.0 * n / products if products else 0:.1f}% "
          f"| {len(col_suppliers[col])} |")
    A("")
    A("### What this count is NOT")
    A("")
    A("An upper bound on coverage, not a promise of extraction quality. It says "
      "the supplier wrote a heading naming the field; it does not say the text "
      "beneath it is complete or correct. It also cannot see content that has "
      "no heading at all -- for those products heading-gating leaves the text "
      "in `detail_description`, which is the CORRECT behaviour, not a miss.")
    A("")
    A("## Per field")
    A("")
    A("| Field | Products with text | HTML | >=1 heading | % of those with text | Total headings | Distinct wordings |")
    A("|---|---|---|---|---|---|---|")
    for f in FIELDS:
        st = stats[f]
        p = st["present"]
        pc = 100.0 * st["with_heading"] / p if p else 0
        A(f"| `{f}` | {p:,} | {st['html']:,} | {st['with_heading']:,} | "
          f"{pc:.1f}% | {st['headings']:,} | {len(st['counts']):,} |")
    A("")
    A("## Headings per product (all fields combined)")
    A("")
    A("| Headings | Products | % |")
    A("|---|---|---|")
    buckets = [(0, 0), (1, 1), (2, 2), (3, 4), (5, 8), (9, 10 ** 6)]
    for lo, hi in buckets:
        n = sum(v for k, v in per_product_total.items() if lo <= k <= hi)
        label = str(lo) if lo == hi else (f"{lo}+" if hi > 10 ** 5 else f"{lo}-{hi}")
        A(f"| {label} | {n:,} | {100.0 * n / products if products else 0:.1f}% |")
    A("")
    A("## Top headings by DISTINCT SUPPLIERS")
    A("")
    A("Ranked by how many different suppliers use the wording, not raw "
      "frequency -- one supplier with 400 products writing \"What to bring\" is "
      "one vote, not 400. Same rule as `reports/booking_column_definitions.md`.")
    for f in FIELDS:
        st = stats[f]
        if not st["counts"]:
            A("")
            A(f"### `{f}` -- no headings found")
            continue
        A("")
        A(f"### `{f}`")
        A("")
        A("| Heading | Suppliers | Occurrences |")
        A("|---|---|---|")
        ranked = sorted(st["suppliers"].items(),
                        key=lambda kv: (-len(kv[1]), -st["counts"][kv[0]]))
        for h, sup in ranked[:30]:
            A(f"| {h} | {len(sup)} | {st['counts'][h]:,} |")
    A("")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L), encoding="utf-8")

    print(f"\n{any_field_heading:,} / {products:,} products "
          f"({pct:.1f}%) have >=1 heading")
    print(f"{any_field_mapped:,} / {products:,} products "
          f"({100.0 * any_field_mapped / products if products else 0:.1f}%) "
          f"have >=1 heading NAMING A COLUMN WE SHIP  <-- the deciding number")
    for f in FIELDS:
        st = stats[f]
        p = st["present"]
        print(f"  {f:24s} text={p:6,}  html={st['html']:6,}  "
              f">=1 heading={st['with_heading']:6,} "
              f"({100.0 * st['with_heading'] / p if p else 0:5.1f}%)  "
              f"distinct={len(st['counts']):,}")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
