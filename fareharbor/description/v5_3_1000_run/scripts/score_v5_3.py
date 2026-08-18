"""
Score a V5.3 heading-gated run.

Copy of score_v5_2.py with the changes V5.3's rules require. Without these the
scorer would report V5.3's fixes as regressions.

Changes from score_v5_2.py:
  * WEATHER MOVED. "weather polic" was a `cancellation` keyword; V5.3 routes
    weather/operating conditions to important_info, so the keywords move too.
    Left in place, the scorer would flag every correct Fix-4 placement.
  * TIER HEADINGS. `Non Member`, `Pensioners`, `SSAA Members` etc. name no
    column -> ABOUT_ONLY.
  * INFORMATIVE HEADING LINES COUNT AS CONTENT. score_v5_2 excluded every
    heading-shaped line from the retention count, on the grounds that a label
    is not content. That is what let products 483868 and 180278 silently lose
    "UPDATE JULY 1st 2025 - New Legislation around Swords" and the Woolamai
    tagline at 100% reported retention. A heading-shaped line that names no
    column AND carries its own information (a digit, an update marker, the
    opening tagline, or sentence length) is CONTENT and must be retained.
    Tier labels likewise -- V5.3 requires them kept, joined to their line.
  * THREE NEW DIRECT CHECKS, so the five rules are measured rather than
    inferred from retention:
      dropped_informative_headings  -- Fix 1 and 2
      pricing_without_figure        -- Fix 3 ("a Pricing section with no price")
      cancellation_without_refund   -- Fix 4

Usage:
    python score_v5_3.py v5_3_hard100_output.jsonl
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

from build_model_comparison_batches import strip_html, find_raw_file  # noqa: E402

RETENTION_GATE = 99.0          # percent, bare labels excluded
DUPLICATION_GATE = 0           # sentences appearing in 2+ fields

COLUMN_KEYS = {
    "redo_desc_highlights": ["highlight"],
    "redo_desc_what_included": [
        "includ", "inclusion", "provided", "we provide", "what you get",
    ],
    "redo_desc_what_excluded": [
        "not included", "exclusion", "exclude", "own expense",
    ],
    "redo_desc_extras": ["extras", "add-on", "add on", "upgrade", "optional"],
    "redo_desc_itinerary": ["itinerar", "day by day", "the route"],
    "redo_desc_what_to_bring": [
        "what to bring", "what to wear", "dress code", "packing", "bring",
        "gear", "equipment",
    ],
    "redo_desc_duration_text": ["duration", "how long", "tour length"],
    # V5.3: weather/operating conditions are NOT cancellation unless the same
    # text says what happens to the customer's money.
    "redo_desc_cancellation": ["cancel", "refund"],
    "redo_desc_check_in": [
        "check in", "check-in", "arrival", "know before", "boarding",
        "before you arrive", "on the day", "getting there",
    ],
    "redo_desc_accessibility": ["accessib", "mobility"],
    "redo_desc_restrictions": [
        "requirement", "restriction", "rule", "prerequisit", "suitab",
        "who can", "ability level", "age",
    ],
    "redo_desc_special_requirements": ["special requirement"],
    "redo_desc_faqs": ["faq", "q&a", "question"],
    "redo_desc_pricing": ["rate", "pricing", "price", "cost", "fee", "deposit"],
    "redo_desc_disclaimers": ["disclaim", "risk disclosure", "liabilit", "waiver"],
    "redo_meeting_point": [
        "meeting point", "starting point", "start point", "departure point",
        "departure location", "boarding location", "where to meet",
        "pickup location", "pick up location", "location",
    ],
    "redo_group_size": ["group size", "capacity"],
    "redo_desc_important_info": [
        "important", "please note", "more info", "additional info",
        "other information", "notes", "note", "details", "things to know",
        "good to know", "general information", "information", "info",
        # V5.3: weather / operating conditions live here now.
        "weather", "temperature", "tide", "operating condition",
    ],
}
# Headings that name NO column -- content stays in about.
ABOUT_ONLY = [
    "schedule", "opening hours", "hours of operation", "session times",
    "departure times", "when", "hours",
    "what to expect", "how it works", "tour summary", "key information",
    "tour overview", "program overview", "return trip", "about", "description",
    "overview", "about us", "why join us",
]
# V5.3: audience tiers name WHO the customer is, not a topic.
TIER = re.compile(
    r"^(non[- ]?\w*\s*)?(member|members|membership|pensioner|pensioners|senior"
    r"|seniors|student|students|adult|adults|child|children|concession"
    r"|family|junior|group|groups)\b|(\bmember|\bpensioner|\bjunior\b|\bconcession\b)",
    re.I,
)
PARENT = "redo_desc_about"


def norm(s):
    s = (s or "").lower().strip()
    s = s.replace("’", "'").replace("‘", "'")
    s = re.sub(r"[?!:.\-–—]+$", "", s).strip()
    s = re.sub(r"['`]", "", s)
    s = re.sub(r"[^a-z0-9&+ ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def next_content(lines, i):
    for j in range(i + 1, min(i + 4, len(lines))):
        if (lines[j] or "").strip():
            return lines[j]
    return ""


MD_PREFIX = re.compile(r"^\s*(#{1,6}|\*{1,3}|_{1,3})\s*")
MD_TRAIL = re.compile(r"\s*(\*{1,3}|_{1,3})\s*$")


def demark(line):
    t = MD_PREFIX.sub("", line or "")
    return MD_TRAIL.sub("", t).strip()


def is_heading_shaped(line, nxt):
    t = demark(line)
    if not t or len(t) > 60:
        return False
    if t.endswith(".") or t.endswith(","):
        return False
    if re.match(r"^[-•‣●]", t) or re.match(r"^\s*[-•‣●]", line or ""):
        return False
    w = t.rstrip(":").strip()
    if not w or not w[0].isalpha() or not (1 <= len(w.split()) <= 7):
        return False
    if MD_PREFIX.match(line or "") and w:
        return True
    if not (nxt or "").strip():
        return False
    if t.endswith(":"):
        return True
    letters = [c for c in w if c.isalpha()]
    if letters and all(c.isupper() for c in letters):
        return True
    words = [x for x in w.split() if x[:1].isalpha()]
    return bool(words) and sum(1 for x in words if x[0].isupper()) >= max(1, len(words) - 1)


def heading_column(line):
    n = norm(demark(line))
    if not n:
        return None
    if n in ABOUT_ONLY:
        return None
    if TIER.search(n):
        return None
    best, best_len = None, 0
    for col, keys in COLUMN_KEYS.items():
        for k in keys:
            if re.search(r"\b" + re.escape(k) + r"\w{0,3}\b", n) and len(k) > best_len:
                best, best_len = col, len(k)
    return best


NOTICE = re.compile(r"\bupdate\b|\bplease note\b|\bnew\b|\bnotice\b|\bchange[sd]?\b", re.I)


def is_lead_in(line):
    """A line that only introduces the list beneath it, and dies with it.

    User ruling 2026-08-11 on product 103636: "We will provide you with the
    following when you arrive for your lesson:" is a LEAD-IN, not content --
    once the list sits in what_included the sentence adds nothing, so dropping
    it is correct.

    The test that separates it cleanly: a line ending in ':' or ';' introduces
    what follows; a line ending in '.' makes a statement of its own. Checked
    against all 12 reported losses in the 100-product run -- every one of the 9
    false positives ends in ':'/';' or is a bare label, and every one of the 4
    real losses ends in a full stop.

    Without this, the scorer over-reported content loss 3x (12 flagged, 4 real),
    which buries the genuine losses in noise.
    """
    t = demark(line).strip()
    return t.endswith(":") or t.endswith(";")


def is_informative_heading(line, is_first):
    """Does this heading-shaped line carry information of its own?

    V5.3 STEP 1B: remove the line -- is anything gone? A bare label
    ("Duration") loses nothing. A dated notice or the opening tagline does.

    Kept deliberately conservative: a false positive here makes retention read
    LOW (we demand a line the model reasonably dropped), which surfaces as a
    visible failure rather than hiding one.
    """
    t = demark(line).rstrip(":").strip()
    if not t:
        return False
    n = norm(t)
    if heading_column(line):        # a bare label naming a column
        return False
    if n in ABOUT_ONLY:
        return False
    if TIER.search(n):              # tier label -- V5.3 requires it kept
        return True
    if is_lead_in(line):            # introduces a list; dies with it
        return False
    if re.search(r"\d", t):         # dates, years, prices
        return True
    if NOTICE.search(t):
        return True
    if is_first:                    # opening tagline
        return True
    return len(t.split()) >= 6      # sentence-length line


def heading_lines(raw):
    """Bare labels only -- these are excluded from the retention count.

    Informative lines and tier labels are NOT excluded: V5.3 requires them in
    the output, so their absence must count as loss.
    """
    out, lines = set(), raw.split("\n")
    first_idx = next((i for i, l in enumerate(lines) if (l or "").strip()), -1)
    for i, l in enumerate(lines):
        if not is_heading_shaped(l, next_content(lines, i)):
            continue
        if is_informative_heading(l, i == first_idx):
            continue
        out.add(norm(l))
        out.add(norm(demark(l)))
    return out


def informative_headings(raw):
    """Heading-shaped lines that MUST survive into the output."""
    out, lines = [], raw.split("\n")
    first_idx = next((i for i, l in enumerate(lines) if (l or "").strip()), -1)
    for i, l in enumerate(lines):
        if is_heading_shaped(l, next_content(lines, i)) and is_informative_heading(l, i == first_idx):
            out.append(demark(l).rstrip(":").strip())
    return out


def headings_in(raw):
    found, lines = {}, raw.split("\n")
    for i, l in enumerate(lines):
        if not is_heading_shaped(l, next_content(lines, i)):
            continue
        col = heading_column(l)
        if col:
            found.setdefault(col, l.strip())
    return found


WINDOW = 6


def retained(sentence, blob):
    w = norm(sentence).split()
    if not w:
        return True
    if len(w) <= WINDOW:
        words = [x for x in w if len(x) > 2]
        if not words:
            return norm(sentence) in blob
        bw = set(blob.split())
        return sum(1 for x in words if x in bw) / len(words) >= 0.8
    return any(
        " ".join(w[i:i + WINDOW]) in blob for i in range(len(w) - WINDOW + 1)
    )


def sentences(text):
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if len(norm(p)) > 12]


INLINE_LABEL = re.compile(r"^\s*([A-Za-z][^:]{0,40}):\s*(\S.*)$")


def classify_absence(sentence, blob):
    """A source sentence is not in the output. Is that a real loss?

    Three outcomes, and only the third costs the customer anything:

      lead_in     the line only introduces the list beneath it and dies with
                  it -- "We will provide you with the following:" (103636).
                  User-ruled correct to drop.
      label_only  an inline "Label: value" line whose VALUE survived; only the
                  label was stripped. "Price: $149 per person" (738684) ->
                  pricing holds "$149 per person". Cosmetic, not lost.
      real        nothing of it reached any column.

    Splitting these apart is what takes the 100-product run from 12 reported
    losses to 4 real ones. Lumping them together buries the real losses.
    """
    t = (sentence or "").strip()
    if is_lead_in(t):
        return "lead_in"
    m = INLINE_LABEL.match(t)
    if m and retained(m.group(2), blob):
        return "label_only"
    if is_bare_label(t):
        return "bare_label"
    return "real"


def is_bare_label(line):
    """A short label line that is_heading_shaped() misses on casing alone.

    `Tour Requirements` (724383), `What to bring` (156525) and `What you'll do`
    (676702) are all plainly labels, but is_heading_shaped() rejects them --
    the first has no line after it, the other two are not Title Case. They then
    counted as lost content.

    The separator is terminal punctuation, the same principle as is_lead_in():
    a label states nothing and so ends bare; a sentence ends in . ! or ?. That
    keeps real short content safe -- the tagline "Two Rivers, Twice the
    Excitement!" ends in '!' and stays content.
    """
    t = demark(line).strip()
    if not t:
        return False
    w = len(t.split())

    # A question used as a section heading. Found at 500-product scale:
    # "What can you expect?" (702571), "What do I need to bring?" (278798) --
    # both introduce a block that survived. Terminal '?' alone would have made
    # them look like sentences.
    if t.endswith("?") and w <= 8:
        return True
    # "About The Christmas in July Dinner Train" (210832) -- an About heading
    # naming the product. Longer than a plain label but still a label.
    if re.match(r"^(about|welcome to)\b", t, re.I) and w <= 9:
        return True
    # Sign-offs. The prompt already permits omitting these; "Thank you and safe
    # cycling!" (425749) is not product content.
    if re.match(r"^(thank you|thanks|regards|see you|cheers|enjoy)\b", t, re.I) and w <= 8:
        return True
    # A markdown link/CTA line, e.g. the waitlist link on 402465.
    if re.match(r"^\[?.{0,60}\]\(https?://", t) or t.startswith("]("):
        return True

    if t[-1] in ".!?":
        return False
    if re.search(r"\d", t):            # a figure means it carries information
        return False
    # Up to 9 words. Section titles run long -- "HMAS Sydney II Memorial & Saint
    # Francis Xavier Cathedral" (259142), "What You Can Also Expect On This Tour"
    # (487731), "Summit Road to Akoroa and Lyttelton Harbour" (229499) are all
    # plainly labels, and a 6-word cap reported every one as lost content.
    return w <= 9


ITIN_SIGNAL = re.compile(
    r"\d{1,2}[:.]\d{2}\s*(am|pm)?|\b\d{1,2}\s*(am|pm)\b|\bday\s*\d|\bstop\s*\d",
    re.I,
)
NOT_INCLUDED_LANG = re.compile(
    r"available for purchase|can be purchased|at extra cost|additional charge"
    r"|available on request|at your own expense",
    re.I,
)
# Fix 3: a pricing value must carry a real figure.
FIGURE = re.compile(r"\d")
# Fix 4: cancellation must say what happens to the money.
REFUND_LANG = re.compile(
    r"refund|cancel|forfeit|reschedul|credit|deposit|charge|fee|no[- ]show|transfer",
    re.I,
)


def main():
    fn = sys.argv[1] if len(sys.argv) > 1 else "v5_3_hard100_output.jsonl"
    rows = [json.loads(l) for l in (TEST_DIR / fn).open(encoding="utf-8")]

    results, T = {}, defaultdict(int)
    for row in rows:
        pid = row["custom_id"].split("|")[0]
        fields = json.loads(row["response"]["body"]["choices"][0]["message"]["content"])
        flags = fields.pop("redo_flags", "")

        item = json.loads(Path(find_raw_file(pid)).read_text(encoding="utf-8"))["item"]
        sd = item.get("structured_description") or {}
        raw = strip_html(sd.get("description") or item.get("description") or "")

        present = headings_in(raw)
        heads = heading_lines(raw)
        filled = {k: v for k, v in fields.items() if (v or "").strip()}

        line_test_move = "what_included:" in (flags or "")
        filled_no_heading = [
            k for k in filled
            if k != PARENT and k not in present
            and not (line_test_move and k == "redo_desc_what_excluded")
        ]
        blank_with_heading = [k for k in present if not (fields.get(k) or "").strip()]

        seen = defaultdict(list)
        for k, v in filled.items():
            for s in sentences(v):
                seen[norm(s)].append(k)
        dupes = {s: ks for s, ks in seen.items() if len(set(ks)) > 1}

        blob = norm(" ".join(filled.values()))
        src = [s for s in sentences(raw) if norm(s) not in heads]
        absent = [s for s in src if not retained(s, blob)]
        by_kind = defaultdict(list)
        for s in absent:
            by_kind[classify_absence(s, blob)].append(s)
        missing = by_kind["real"]          # retention is scored on these only

        # Fix 1 / Fix 2 -- measured directly, not inferred from retention.
        dropped_info = [
            h for h in informative_headings(raw) if not retained(h, blob)
        ]

        raw_n = norm(raw)
        untraceable = [
            s for v in filled.values() for s in sentences(v) if norm(s) not in raw_n
        ]

        itin_bad = [
            s for s in sentences(fields.get("redo_desc_itinerary", ""))
            if not ITIN_SIGNAL.search(s)
        ]
        incl_bad = [
            s for s in sentences(fields.get("redo_desc_what_included", ""))
            if NOT_INCLUDED_LANG.search(s)
        ]
        pricing = (fields.get("redo_desc_pricing") or "").strip()
        pricing_no_figure = bool(pricing) and not FIGURE.search(pricing)
        cancel = (fields.get("redo_desc_cancellation") or "").strip()
        cancel_no_refund = bool(cancel) and not REFUND_LANG.search(cancel)

        w_in, w_out = len(raw.split()), sum(len(v.split()) for v in filled.values())
        junk = [k for k, v in filled.items() if re.search(r"\*\*|#{1,3}\s", v)]

        results[pid] = {
            "headings_naming_a_column": sorted(present),
            "fields_filled": len(filled),
            "fields_blank": len(fields) - len(filled),
            "filled_but_no_heading": filled_no_heading,
            "blank_but_heading_present": blank_with_heading,
            "duplicated_sentences": len(dupes),
            "retention_pct": round(100 * (len(src) - len(missing)) / max(1, len(src)), 1),
            "missing_sentences": [s[:110] for s in missing],
            "dropped_lead_ins": [s[:110] for s in by_kind["lead_in"]],
            "dropped_label_only": [s[:110] for s in by_kind["label_only"]],
            "dropped_bare_labels": [s[:110] for s in by_kind["bare_label"]],
            "dropped_informative_headings": dropped_info,
            "pricing_without_figure": pricing_no_figure,
            "cancellation_without_refund": cancel_no_refund,
            "untraceable_sentences": len(untraceable),
            "itinerary_lines_without_signal": [s[:90] for s in itin_bad],
            "included_lines_that_are_purchasable": [s[:90] for s in incl_bad],
            "fidelity": round(w_out / max(1, w_in), 2),
            "markdown_junk_fields": junk,
            "model_flags": flags,
        }
        T["fnh"] += len(filled_no_heading)
        T["bwh"] += len(blank_with_heading)
        T["dupes"] += len(dupes)
        T["src"] += len(src)
        T["missing"] += len(missing)
        T["lead_in"] += len(by_kind["lead_in"])
        T["label_only"] += len(by_kind["label_only"])
        T["bare_label"] += len(by_kind["bare_label"])
        T["dropped_info"] += len(dropped_info)
        T["price_nofig"] += int(pricing_no_figure)
        T["cancel_norefund"] += int(cancel_no_refund)
        T["untraceable"] += len(untraceable)
        T["itin_bad"] += len(itin_bad)
        T["incl_bad"] += len(incl_bad)
        T["w_in"] += w_in
        T["w_out"] += w_out
        T["junk"] += len(junk)

    out = TEST_DIR / (Path(fn).stem.replace("_output", "") + "_scores.json")
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")

    retention = round(100 * (T["src"] - T["missing"]) / max(1, T["src"]), 1)

    print("=" * 78)
    print(f"{fn}  --  {len(rows)} products")
    print("=" * 78)
    print(f"{'product':>9} {'fill':>5} {'noHead':>7} {'missHead':>9} "
          f"{'dupes':>6} {'reten%':>7} {'dropHd':>7} {'fidel':>6}")
    for pid, r in results.items():
        print(f"{pid:>9} {r['fields_filled']:>5} "
              f"{len(r['filled_but_no_heading']):>7} "
              f"{len(r['blank_but_heading_present']):>9} "
              f"{r['duplicated_sentences']:>6} {r['retention_pct']:>7} "
              f"{len(r['dropped_informative_headings']):>7} {r['fidelity']:>6}")
    print("-" * 78)
    print(f"\nfilled WITHOUT a heading      : {T['fnh']}")
    print(f"heading present, field blank  : {T['bwh']}")
    print(f"duplicated sentences          : {T['dupes']}       [gate: 0]")
    print(f"content retention             : {retention}%   [gate: >={RETENTION_GATE}%]")
    print(f"  of which lead-ins (correct) : {T['lead_in']}       [not loss -- user ruling]")
    print(f"  of which label-only         : {T['label_only']}       [value survived elsewhere]")
    print(f"  of which bare labels        : {T['bare_label']}       [labels, not content]")
    print(f"dropped informative headings  : {T['dropped_info']}       [V5.3 fix 1+2]")
    print(f"pricing with no figure        : {T['price_nofig']}       [V5.3 fix 3]")
    print(f"cancellation with no refund   : {T['cancel_norefund']}       [V5.3 fix 4]")
    print(f"untraceable (invented)        : {T['untraceable']}")
    print(f"itinerary lines w/o signal    : {T['itin_bad']}       [line test]")
    print(f"included lines purchasable    : {T['incl_bad']}       [line test]")
    print(f"fidelity                      : {round(T['w_out']/max(1,T['w_in']),2)}x")
    print(f"markdown junk fields          : {T['junk']}")
    print(f"\nwrote {out.name}")

    failures = []
    if T["dupes"] > DUPLICATION_GATE:
        failures.append(f"duplication {T['dupes']} > {DUPLICATION_GATE}")
    if retention < RETENTION_GATE:
        failures.append(f"retention {retention}% < {RETENTION_GATE}%")
    if failures:
        print("\nGATE FAILED: " + "; ".join(failures))
        sys.exit(1)
    print("\nGATES PASSED")


if __name__ == "__main__":
    main()
