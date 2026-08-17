"""PHASE 1 -- build reports/rezdy_column_definitions.md from the heading census.

No prompt is written until this document exists. That is the order the Fareharbor
booking side used, and it is why that column set is defensible: the census came
first, the document was written from it, and the prompt was written from the
document. Inventing columns and then looking for evidence is how the 89.4%
misclassification problem was built in the first place.

THREE RULES THIS SCRIPT ENFORCES, each one a bug that has already been paid for:

1. RANK BY DISTINCT SUPPLIERS, NEVER BY FREQUENCY. One supplier with 400
   products writing "What to bring" is ONE vote, not 400. Rezdy has suppliers
   with 13 KB of identical boilerplate across every product they list.

2. ORDER IS LOAD-BEARING, so the map is a LIST, not a dict. `what_excluded` MUST
   be tested before `what_included` because "What's Not Included" contains the
   substring "included" -- inclusion-first hid 192 products in the census. Same
   class as the MEETING TIME/PLACE-vs-departure bug in CLAUDE.md.

3. FOLLOW FAREHARBOR V5.3 WHERE IT HAS ALREADY RULED. The census used a quick
   stem list that contradicts the shipped prompt in three places (see
   CENSUS_CORRECTIONS below). The prompt wins -- it was validated on thousands of
   hand-checked products; the census stems were written in an afternoon to answer
   a yes/no question.

Counting uses rezdy_common.html_to_markdown -- the CORRECTED converter that makes
no heading judgements -- so these numbers reflect what the model will actually be
shown, not what the guarded census converter allowed through.
"""
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "rezdy_column_definitions.md"

sys.path.insert(0, str(ROOT / "data_pipeline" / "batch_api_test"))
from rezdy_common import (FIELDS, RAW_DIR, html_to_markdown,      # noqa: E402
                          iter_products, _text)
from booking_common import heading_of                              # noqa: E402

# ---------------------------------------------------------------------------
# THE HEADING -> COLUMN MAP. Order matters; see rule 2 above.
# Stems are matched as substrings against a normalised heading (lowercase,
# punctuation folded to spaces). Deliberately conservative: unambiguous stems
# only, no synonym guessing. A heading that matches nothing is NOT a failure --
# it means the supplier named a topic, not a column, and its content correctly
# stays in the default field.
# ---------------------------------------------------------------------------
COLUMN_STEMS = [
    # -- MUST BE FIRST: contains "included" as a substring ------------------
    ("what_excluded", ["exclusion", "excludes", "excluded", "not included",
                       "not inclusive", "doesn t include", "does not include",
                       "own expense", "not covered"]),
    ("what_included", ["inclusion", "includes", "included", "what s included",
                       "what is included", "price includes", "we provide",
                       "what you get"]),
    # -- 'what to wear' before restrictions ('dress' vs 'dress code') --------
    ("what_to_bring", ["what to bring", "please bring", "bring with you",
                       "what to wear", "dress code", "packing list",
                       "what you need", "what should i bring", "equipment list"]),
    ("highlights", ["highlight"]),
    ("itinerary", ["itinerary", "day 1", "day 2", "day 3", "day 4", "day 5",
                   "the route", "tour route", "order of the day"]),
    ("cancellation", ["cancellation", "cancellations", "refund", "no show",
                      "reschedul"]),
    # -- meeting_point BEFORE check_in: "meeting time" must not be eaten by an
    #    arrival/time stem. The Fareharbor bug was the mirror of this.
    # Bare "Location" (33 suppliers) is the single commonest meeting-point
    # wording after "meeting point" itself, and the Fareharbor booking column
    # set renamed its `location` column to `meeting_point` for exactly this
    # reason. Listed after the compound forms so those still win.
    ("meeting_point", ["meeting point", "meeting location", "meeting place",
                       "where to meet", "where we meet", "departure point",
                       "boarding location", "starting point", "pick up",
                       "pickup", "pick-up", "meeting time", "location"]),
    ("check_in", ["check in", "checkin", "check-in", "arrival time",
                  "on the day", "getting there", "before you arrive",
                  "prior to arrival", "how to get there", "directions"]),
    ("restrictions", ["restriction", "requirement", "prerequisite",
                      "suitability", "ability level", "age limit", "age range",
                      "minimum age", "maximum age", "fitness", "medical",
                      "weight limit", "child policy", "who can"]),
    # Bare "Note"/"Notes" (38 suppliers combined) is listed in V5.3's
    # important_info headings and was missing here. Safe at this position:
    # `cancellation` is tested earlier, so "Cancellation notes" still wins.
    ("important_info", ["important information", "important note", "important",
                        "please note", "note", "good to know", "need to know",
                        "things to know", "general information", "weather",
                        "more info", "additional information", "additional info"]),
    ("duration_text", ["duration", "how long"]),
    # Bare "Price" (12 suppliers) was missing. Safe: "Price includes" is claimed
    # by what_included and "Price does not include" by what_excluded, both of
    # which are tested first.
    ("pricing", ["rates", "price", "pricing", "deposit", "fees", "cost of"]),
    ("extras", ["optional extra", "add on", "add-on", "upgrade", "extras"]),
    ("faqs", ["faq", "frequently asked", "common questions"]),
    ("disclaimers", ["disclaimer", "risk", "liability", "waiver", "indemnity",
                     "terms and conditions", "terms conditions"]),
    ("accessibility", ["accessib", "mobility", "wheelchair"]),
    ("group_size", ["group size", "capacity", "maximum group", "minimum number"]),
    ("special_requirements", ["special requirement", "dietary"]),
    ("health_safety", ["health", "safety"]),
    ("contact", ["contact"]),
]

# Where the census's quick stem list CONTRADICTS the shipped Fareharbor prompt.
# The prompt wins. Each of these moved counts, so they are reported explicitly
# rather than silently corrected.
CENSUS_CORRECTIONS = [
    ("`what to expect` -> itinerary", "-> about",
     "V5.3 lists 'What to Expect' under NARRATIVE HEADINGS, which name no "
     "column and route to the default field."),
    ("`schedule` -> itinerary", "-> not mapped",
     "V5.3: \"A 'Schedule' heading is NOT an itinerary: it means departure "
     "times.\" It is listed under VENUE HOURS, which are explicitly not "
     "duration either."),
    ("`getting there` / `directions` -> meeting_point", "-> check_in",
     "V5.3 gives check_in the headings 'Getting There', 'On the Day' and "
     "'Before You Arrive'. meeting_point is the PLACE, check_in is the "
     "instructions for arriving."),
]

# Headings that will never name a column, and that we deliberately refuse to
# map. Fareharbor proved chasing these is classification by meaning -- the thing
# heading-gating replaced -- and that it does not converge: fixing four wordings
# removed only 14 of 290 flags.
NEVER_MAP = ["weather", "parking", "travel insurance", "privacy policy",
             "contact us", "about us", "why choose", "our story", "gift voucher",
             "transport", "meals", "photos", "tipping"]


def norm(h):
    """Fold a heading for matching. Punctuation -> space, then COLLAPSE runs.

    The collapse is not cosmetic. "Terms & Conditions" folds to
    "terms   conditions" (three spaces, one per dropped character), so the stem
    "terms conditions" never matched and 35 suppliers' T&C headings read as
    unmapped. Found by reading the unmapped list, not the code -- the same way
    the `not included` bug was found.
    """
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", h.lower())).strip()


def maps_to_column(n):
    for col, stems in COLUMN_STEMS:
        for s in stems:
            if s in n:
                return col
    return None


def headings_in(text):
    lines = [l for l in text.split("\n") if l.strip()]
    out = []
    for i, l in enumerate(lines):
        h = heading_of(l, lines[i + 1] if i + 1 < len(lines) else None)
        if h and h.strip():
            out.append(h.strip())
    return out


def main():
    col_products = defaultdict(set)
    col_suppliers = defaultdict(set)
    col_wordings = defaultdict(Counter)
    col_wording_suppliers = defaultdict(lambda: defaultdict(set))
    per_field_col = defaultdict(lambda: defaultdict(set))
    unmapped = Counter()
    unmapped_suppliers = defaultdict(set)
    samples = []                       # (pid, field, heading) for verification
    products = 0
    mapped_products = set()

    for pid, supplier, p in iter_products():
        products += 1
        for f in FIELDS:
            raw = p.get(f)
            if not isinstance(raw, str) or not raw.strip():
                continue
            for h in headings_in(html_to_markdown(raw)):
                n = norm(h)
                if not n:
                    continue
                col = maps_to_column(n)
                if col:
                    col_products[col].add(pid)
                    col_suppliers[col].add(supplier)
                    col_wordings[col][n] += 1
                    col_wording_suppliers[col][n].add(supplier)
                    per_field_col[f][col].add(pid)
                    mapped_products.add(pid)
                    samples.append((pid, f, h))
                else:
                    unmapped[n] += 1
                    unmapped_suppliers[n].add(supplier)

    verified, failed = verify(samples)
    write(products, mapped_products, col_products, col_suppliers, col_wordings,
          col_wording_suppliers, per_field_col, unmapped, unmapped_suppliers,
          verified, failed)


def verify(samples, k=250):
    """Confirm mapped headings really appear in the raw supplier text.

    The census found the `not included` ordering bug this way -- by reading raw
    text, not by reading the code. A heading our detector invented would map to
    a column just as happily as a real one.
    """
    random.seed(42)
    picks = random.sample(samples, min(k, len(samples)))
    ok, bad = 0, []
    cache = {}
    for pid, field, h in picks:
        if pid not in cache:
            hits = list(RAW_DIR.glob(f"Rezdy-*-{pid}.json"))
            cache[pid] = _text(hits[0].read_text(encoding="utf-8")) if hits else ""
        # Compare on letters and digits only. Four of the first 250 "failures"
        # were the CHECKER, not the data: a markdown link we added ourselves
        # (`[online](https://...)` -- the URL is in an href attribute, which
        # _text strips), an escaped quote (\"Safety First!\"), an ellipsis, and
        # a colon-spacing difference. None was an invented heading. Punctuation
        # cannot distinguish a real heading from a fake one, so it is dropped.
        needle = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", h)   # link -> its text
        hay = re.sub(r"[^a-z0-9]+", "", cache[pid].lower())
        needle = re.sub(r"[^a-z0-9]+", "", needle.lower())
        if needle and needle in hay:
            ok += 1
        else:
            bad.append((pid, field, h))
    return (ok, len(picks)), bad


def write(products, mapped_products, col_products, col_suppliers, col_wordings,
          col_wording_suppliers, per_field_col, unmapped, unmapped_suppliers,
          verified, failed):
    L = []
    A = L.append
    ok, tot = verified

    A("# Rezdy Column Definitions")
    A("")
    A("*Phase 1 of `reports/REZDY_STEP2_PLAN.md`. The source document the Rezdy "
      "extraction prompts get written FROM. No prompt is written until this is "
      "agreed.*")
    A("")
    A("Built by `scripts/build_rezdy_column_definitions.py` from all "
      f"**{products:,}** readable products in `data/Rezdy/`.")
    A("")
    A("Every column below is justified by **how many DIFFERENT SUPPLIERS write a "
      "heading naming it** -- never by raw frequency. One supplier with 400 "
      "products writing \"What to bring\" is one vote, not 400. Rezdy has "
      "suppliers repeating 13 KB of identical text across every product they "
      "list, so frequency would hand them the schema.")
    A("")
    A("Headings are counted from `rezdy_common.html_to_markdown()` -- the "
      "converter that restores structure and makes **no heading judgements**. "
      "The earlier census used a guarded converter that demoted 32.7% of "
      "heading tags, so **its numbers are a floor and these are higher**.")
    A("")

    A("## Three converter bugs this phase found and fixed")
    A("")
    A("Building this document required running the converter over the whole "
      "catalogue, which surfaced three faults the earlier sampling missed. All "
      "three CORRUPT text rather than lose it, so a word-count check is blind "
      "to them by construction:")
    A("")
    A("| # | Fault | Example | Effect |")
    A("|---|---|---|---|")
    A("| 1 | a heading-tag guard that demoted anything ending `.!?` | "
      "`<h4>What do you need to bring?</h4>` | 484 real headings across 241 "
      "products deleted before the model saw them |")
    A("| 2 | `<b>&nbsp;</b>` (bold around a space) collapsed to nothing | "
      "`a course/experience.` + `This can be done` | words FUSED into "
      "`course/experience.This` |")
    A("| 3 | `.strip()` ate the space inside a bold label | "
      "`<b>HOW LONG: </b>2 HOURS` (PJBKTR) | became `HOW LONG:2 HOURS`, which "
      "no longer matches the prompt's `Label: value` rule |")
    A("")
    A("After the fixes, the lossless gate reads **0 real losses in 2,668 "
      "field-texts** (separator rules like `-----` excepted, which the prompt "
      "is explicitly allowed to drop).")
    A("")
    A("## Verification")
    A("")
    pct = 100.0 * ok / tot if tot else 0
    A(f"**{ok} of {tot} sampled mapped headings ({pct:.1f}%) confirmed present "
      f"in the raw supplier text.** A heading our detector invented would map to "
      f"a column just as happily as a real one, so the map is only as good as "
      f"this check. It is also how the `not included` ordering bug was found -- "
      f"by reading raw text, not by reading the code.")
    if failed:
        A("")
        A("Not found verbatim (worth reading before trusting their column):")
        A("")
        A("| Product | Field | Heading |")
        A("|---|---|---|")
        for pid, f, h in failed[:15]:
            A(f"| `{pid}` | `{f}` | {h[:70]} |")
    A("")

    A("## Proposed columns")
    A("")
    mp = 100.0 * len(mapped_products) / products if products else 0
    A(f"**{len(mapped_products):,} of {products:,} products ({mp:.1f}%)** have at "
      f"least one heading naming one of these columns.")
    A("")
    A("Ranked by distinct suppliers. **Ship / Argue / Reject** is the decision "
      "this document exists to settle.")
    A("")
    A("| Column | Suppliers | Products | % of catalogue | Verdict |")
    A("|---|---|---|---|---|")
    for col in sorted(col_products, key=lambda c: -len(col_suppliers[c])):
        ns, np_ = len(col_suppliers[col]), len(col_products[col])
        pc = 100.0 * np_ / products if products else 0
        verdict = ("**SHIP**" if ns >= 40 else
                   "ARGUE" if ns >= 15 else "REJECT?")
        A(f"| `{col}` | **{ns}** | {np_:,} | {pc:.1f}% | {verdict} |")
    A("")
    A("Thresholds are a starting point, not a rule: **SHIP** ≥40 suppliers, "
      "**ARGUE** 15-39, **REJECT?** <15. Fareharbor has the same decision "
      "outstanding on three columns measured at 0.2-0.6% of its catalogue, and "
      "it is still unsettled -- so a low count here is a question, not an "
      "automatic no.")
    A("")

    A("## Which field feeds which column")
    A("")
    A("This is the merge problem in table form. A column fed by BOTH "
      "`description` and `additionalInformation` will need a precedence rule -- "
      "and that rule is inherited from Fareharbor, not invented here.")
    A("")
    cols = sorted(col_products, key=lambda c: -len(col_suppliers[c]))
    A("| Column | description | additionalInformation | terms | contested? |")
    A("|---|---|---|---|---|")
    for c in cols:
        d = len(per_field_col["description"].get(c, ()))
        a = len(per_field_col["additionalInformation"].get(c, ()))
        t = len(per_field_col["terms"].get(c, ()))
        hot = "**YES**" if (d and a and min(d, a) >= 50) else ""
        A(f"| `{c}` | {d:,} | {a:,} | {t:,} | {hot} |")
    A("")

    A("## Evidence per column")
    A("")
    A("The actual supplier wordings, so a reviewer can judge whether the stem "
      "list is honest. `sup` = distinct suppliers using that wording.")
    for col in cols:
        A("")
        A(f"### `{col}`  ·  {len(col_suppliers[col])} suppliers  ·  "
          f"{len(col_products[col]):,} products")
        A("")
        A("| Heading wording | sup | uses |")
        A("|---|---|---|")
        ranked = sorted(col_wordings[col].items(),
                        key=lambda kv: (-len(col_wording_suppliers[col][kv[0]]),
                                        -kv[1]))
        for w, c in ranked[:12]:
            A(f"| {w} | {len(col_wording_suppliers[col][w])} | {c:,} |")
    A("")

    A("## Corrections to the census stem list")
    A("")
    A("The census answered a yes/no question with a stem list written in an "
      "afternoon. It contradicts the shipped Fareharbor V5.3 prompt in three "
      "places. **The prompt wins** -- it was validated on thousands of "
      "hand-checked products. Each correction moved counts, so it is recorded "
      "rather than silently applied.")
    A("")
    A("| Census had | Corrected to | Why |")
    A("|---|---|---|")
    for was, now, why in CENSUS_CORRECTIONS:
        A(f"| {was} | {now} | {why} |")
    A("")
    A("Consequence: the census's `itinerary` figure (13.4%) was inflated by "
      "`what to expect` and `schedule`, neither of which is an itinerary under "
      "V5.3. The number in this document is the corrected one.")
    A("")

    A("## Headings we deliberately do NOT map")
    A("")
    A("These are the most-used headings that match no column. **This is not a "
      "TODO list.** They name topics, not fields. Writing patterns for them is "
      "classification by meaning -- the exact thing heading-gating replaced -- "
      "and on Fareharbor it does not converge: fixing four wordings removed "
      "only 14 of 290 flags. Their content correctly stays in the default "
      "field.")
    A("")
    A("| Heading | Suppliers | Uses |")
    A("|---|---|---|")
    ranked_un = sorted(unmapped.items(),
                       key=lambda kv: (-len(unmapped_suppliers[kv[0]]), -kv[1]))
    for w, c in ranked_un[:40]:
        A(f"| {w} | {len(unmapped_suppliers[w])} | {c:,} |")
    A("")
    A(f"({len(unmapped):,} distinct unmapped wordings in total. The long tail is "
      f"the point: no list can be completed.)")
    A("")

    A("## Open decisions for review")
    A("")
    A("1. **Which `ARGUE` columns ship?** Each is real but thin. Fareharbor has "
      "the identical question open on `group_size` (0.2%), `what_not_to_bring` "
      "(0.3%) and `accessibility` (0.6%) -- settling both together would be "
      "cheaper than settling them twice.")
    A("2. **Do `Day 1` / `Day 2` headings name `itinerary`?** They are how "
      "multi-day tours structure a route, and V5.3's itinerary LINE TEST already "
      "accepts day numbering as a valid structural signal. Mapped as itinerary "
      "here; flagged because it is a judgement, not an obvious match.")
    A("3. **Does `terms and conditions` name `disclaimers`?** Mapped here. But "
      "in the `terms` FIELD it is just the field's own name repeated, which is "
      "a different thing from a T&C heading appearing inside a description.")
    A("4. **`Additional Information` means different things in the two "
      "Fareharbor prompts, and Rezdy needs one answer.** DESC V5.3 lists "
      "'Additional Info / Additional Information' under `important_info`. "
      "BOOKING V5.4 says the opposite in STEP 1E: \"'Additional Information' "
      "names redo_booking_notes, so everything beneath it goes there.\" It is "
      "the 3rd-commonest `important_info` wording here (34 suppliers), so the "
      "choice is worth money. Mapped to `important_info` in this document, "
      "following the DESCRIPTION prompt, because Rezdy's biggest field is a "
      "description. Flagged because it contradicts the booking prompt.")
    A("5. **The contested columns above** need a precedence rule before any "
      "merge. Inherited from Fareharbor -- see "
      "`reports/FAREHARBOR_UNIFIED_STRUCTURE_CONTEXT.md`, still open.")
    A("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"products                 : {products:,}")
    print(f"with >=1 mapped heading  : {len(mapped_products):,} "
          f"({100.0*len(mapped_products)/products:.1f}%)")
    print(f"verification             : {ok}/{tot} "
          f"({100.0*ok/tot if tot else 0:.1f}%) confirmed verbatim")
    print(f"columns proposed         : {len(col_products)}")
    print(f"unmapped wordings        : {len(unmapped):,}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
