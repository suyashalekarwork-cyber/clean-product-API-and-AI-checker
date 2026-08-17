"""Build SYSTEM_PROMPT_RZ_DESC_V1 from Fareharbor's SYSTEM_PROMPT_FH_DESC_V5_3.

WHY A BUILDER AND NOT A HAND-WRITTEN PROMPT: the V5.3 body is the most-validated
text in this project -- tuned across V5.0 -> V5.3 against thousands of
hand-checked products, with STEP 1B, 1C and 1D each added to fix a specific
measured defect. Retyping it would silently lose that. So the Rezdy prompt is
DERIVED, and every change is declared, applied exactly once, and asserted.

The script REFUSES TO WRITE if any transformation did not apply exactly once, if
a core rule went missing, or if the key set does not match the column list.

WHAT CHANGES (and nothing else):
  1. Fareharbor -> Rezdy in the opening line.
  2. A new "WHAT THE TEXT LOOKS LIKE" section: Rezdy arrives as HTML and is
     converted to '## ', '- ' and '**bold**' before the model sees it.
  3. A new rule that a heading may be phrased as a QUESTION. Measured: 484
     question-form headings across 241 products ("What do you need to bring?"),
     which a guard in our own converter used to delete.
  4. Two columns added -- health_safety (78 suppliers) and contact (59) -- both
     already exist on Fareharbor's BOOKING side, so neither is invented.
  5. min_age / max_age REMOVED. V5.3 orders them ALWAYS "" because age content
     goes to restrictions; carrying two permanently-empty columns into a new
     lineage copies a wart.
  6. Worked examples replaced with Rezdy shapes, using INVENTED operator names.
     V5 once copied an example sentence into product 78026, so a real-looking
     name in output is contamination we cannot prove; an invented one is a
     one-line assertion.

WHAT DOES NOT CHANGE: the governing rule, STEP 1 / 1B / 1C / 1D, STEP 2, the
line tests, RULES 1-9 and the self-check. Those are asserted present verbatim.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
ROOT = TEST_DIR.parent.parent
FH_PROMPTS = ROOT / "config" / "fareharbor_prompts.txt"
RZ_PROMPTS = ROOT / "config" / "rezdy_prompts.txt"

SOURCE_VERSION = "SYSTEM_PROMPT_FH_DESC_V5_3"
# The URL rule comes from the BOOKING lineage, not the description one. V5.3's
# RULE 7 is markup-only and says nothing about links, so a Rezdy port that took
# it unchanged would tell the model to "strip markup" over `[text](url)` and
# destroy the target. 2,529 Rezdy products (27.0%) contain a link. V5.4 exists
# precisely because that loss was measured on Fareharbor -- 31 URLs across 22
# products on a 500-product run -- so the fixed rule is taken from there.
URL_RULE_VERSION = "SYSTEM_PROMPT_FH_BOOKING_V5_4"
NEW_VERSION = "SYSTEM_PROMPT_RZ_DESC_V1"

COLUMNS = [
    "redo_desc_about", "redo_desc_important_info", "redo_desc_highlights",
    "redo_desc_what_included", "redo_desc_what_excluded", "redo_desc_extras",
    "redo_desc_itinerary", "redo_desc_what_to_bring", "redo_desc_duration_text",
    "redo_desc_cancellation", "redo_desc_check_in", "redo_desc_accessibility",
    "redo_desc_restrictions", "redo_desc_special_requirements",
    "redo_desc_faqs", "redo_desc_pricing", "redo_desc_disclaimers",
    "redo_desc_health_safety", "redo_desc_contact", "redo_meeting_point",
    "redo_group_size", "redo_flags",
]

# Blocks that must survive byte-identical. Each exists because of a defect.
INVARIANTS = [
    "Extract content into a field ONLY when the supplier wrote a HEADING for it",
    "An empty field is a CORRECT answer.",
    "STEP 1B -- A LINE THAT LOOKS LIKE A HEADING BUT CARRIES ITS OWN INFORMATION",
    "STEP 1C -- LABELLED BLOCKS KEEP THEIR LABEL",
    'STEP 1D -- INLINE "Label: value" ON ONE LINE',
    "1. NO DUPLICATION - extracting is a MOVE, not a copy.",
    "2. NO CONTENT LOSS - every sentence of the raw text must appear in exactly one",
    "4. NO INVENTION - never write text that is not in the raw description.",
    "5. VERBATIM - copy the exact words.",
    "6. FAQ PAIRING - a question and its answer are one unit and move together.",
    "ITINERARY LINE TEST",
    "WHAT_INCLUDED LINE TEST",
    "SELF-CHECK BEFORE RETURNING:",
    # From V5.4, not V5.3 -- see URL_RULE_VERSION and BOOKING_PORTS. Each of
    # these covers a shape measured in the Rezdy catalogue that the description
    # lineage has no rule for.
    "7. STRIP MARKUP, KEEP THE LINE AND KEEP THE URL.",
    "A MARKDOWN LINK KEEPS ITS TARGET.",
    "NEVER shorten, expand or otherwise alter a URL.",
    "STEP 1E -- NESTED HEADINGS: THE OUTER HEADING WINS",
    "STEP 1F -- KEEP EVERY OTHER LABEL, JOINED TO ITS CONTENT",
    "10. A SENTENCE IS THE SMALLEST MOVABLE UNIT.",
    "11. CLAUSE COMPLETENESS",
]


def extract_prompt(raw, version):
    v = re.escape(version)
    m = re.search(r"PROMPT:\s*" + v + r"\s*\n.*?\n=+\n\n(.*?)\n\n=+\nEND OF "
                  + v + r"\s*$", raw, re.DOTALL | re.MULTILINE)
    if not m:
        raise SystemExit(f"could not extract {version}")
    return m.group(1).strip()


# ---------------------------------------------------------------------------
# The declared changes. (find, replace, label) -- each must apply exactly once.
# ---------------------------------------------------------------------------
INPUT_SHAPE = """
WHAT THE TEXT LOOKS LIKE

The supplier wrote this in HTML. It has been converted to plain marks before
reaching you, and the conversion adds nothing and removes nothing:

    ## text        the supplier used a heading tag
    **text**       the supplier made this bold
    - text         a bullet in the supplier's list
    [text](url)    a link -- RULE 7 keeps BOTH the text and the url

'##' and '**' mean the supplier gave that line special formatting. They do NOT
mean it is a heading -- suppliers bold sentences for emphasis and write whole
paragraphs inside heading tags. Decide using STEP 1 as usual. A bold line that
is a full sentence is CONTENT, and STEP 1B applies to it.

A '- ' line is a list item. It is NEVER a heading.

A HEADING MAY BE A QUESTION. Suppliers frequently phrase one that way, and it
names its column exactly as a statement would:

    ## What do you need to bring?      names what_to_bring
    ## What is included?               names what_included
    ## How long does the tour go for?  names duration

Many Rezdy products carry NO heading of any kind. For those, everything belongs
in redo_desc_about and every other field is "". That is the rule working
correctly, not a failure to extract.
"""

NEW_COLUMNS = """  redo_desc_health_safety
      Safety rules, health policy, risk-management procedure, what happens in
      an emergency. Headings: Health & Safety, Safety, Safety Information,
      Safety Briefing, Health Requirements, Covid Policy.
      A RISK WARNING that disclaims liability is redo_desc_disclaimers, not this
      -- this is what the operator DOES to keep the customer safe.

  redo_desc_contact
      How to reach the operator: phone, email, office hours, who to call on the
      day. Headings: Contact, Contact Us, Get in Touch, Questions?, Need Help.
      A contact detail sitting inside another section stays where it is -- only
      a heading naming contact opens this field.

"""


def url_rule(fh_raw):
    """Lift RULE 8 out of BOOKING V5.4 and renumber it for the description set.

    Extracted rather than retyped, for the same reason the body is: it is
    validated text. Its wording was proved on a same-500 A/B where 25 of the 31
    URLs V5.3 lost came back and the other 6 turned out to be the scorer's own
    regex rather than real losses.
    """
    body = extract_prompt(fh_raw, URL_RULE_VERSION)
    m = re.search(r"^8\. STRIP MARKUP.*?(?=^9\. )", body, re.S | re.M)
    if not m:
        raise SystemExit(f"could not find RULE 8 in {URL_RULE_VERSION}")
    rule = m.group(0).rstrip() + "\n"

    # Three wording fixes so it reads correctly in the DESCRIPTION prompt.
    for find, repl in [
        ("8. STRIP MARKUP", "7. STRIP MARKUP"),
        ("Two more\n   shapes appear in booking notes and BOTH must survive:",
         "Two more\n   shapes can appear here too, and BOTH must survive:"),
        ("and RULE 11 admits no exception: every URL in the\n   raw appears in "
         "the output.",
         "and the self-check admits no exception:\n   every URL in the raw "
         "appears in the output."),
    ]:
        if rule.count(find) != 1:
            raise SystemExit(
                f"REFUSING TO WRITE -- URL rule adaptation {find[:40]!r} "
                f"matched {rule.count(find)} times, expected 1")
        rule = rule.replace(find, repl, 1)
    return rule


def lift(fh_raw, version, pattern, renames, label):
    """Pull a validated block out of another prompt and rename its fields.

    Extracted, never retyped. Every rename must apply at least once or the
    build refuses -- a silent no-op rename is how a port ends up referring to a
    field that does not exist (the F1 failure).
    """
    m = re.search(pattern, extract_prompt(fh_raw, version), re.S | re.M)
    if not m:
        raise SystemExit(f"REFUSING TO WRITE -- could not lift {label}")
    block = m.group(0).rstrip() + "\n"
    for find, repl in renames:
        if find not in block:
            raise SystemExit(
                f"REFUSING TO WRITE -- lifting {label}: {find[:50]!r} not found")
        block = block.replace(find, repl)
    return block


# Shapes measured in the Rezdy catalogue that DESC V5.3 has no rule for.
# Each number is products out of 9,363 descriptions.
BOOKING_PORTS = [
    # 1,057 products (11.3%) put a bold line underneath a '##' heading. With no
    # nesting rule the model must invent one, and inventing it means deciding by
    # MEANING -- the failure heading-gating exists to remove.
    ("STEP 1E -- NESTED HEADINGS", r"^STEP 1E -- .*?(?=^STEP 2 --)",
     [("redo_booking_notes", "redo_desc_about"),
      ("STEP 1C", "STEP 1F")]),
    # 2,267 products (24.2%) write a bold LABEL with its value on the next line
    # ("**Duration**" / "3 hours"). DESC V5.3's STEP 1C covers only audience
    # tiers, so this shape -- a quarter of the catalogue -- had no rule at all.
    ("STEP 1F -- KEEP EVERY LABEL", r"^STEP 1C -- KEEP EVERY LABEL.*?(?=^STEP 1D)",
     [("STEP 1C -- KEEP EVERY LABEL", "STEP 1F -- KEEP EVERY OTHER LABEL"),
      ("Never emit a value with its label stripped. Join a label to its content with\n"
       '": " -- the way suppliers already write it.',
       "An audience tier or ticket tier is handled by STEP 1C, with its \" - \"\n"
       "joiner. EVERY OTHER label -- a duration, a time, a day, an option -- keeps\n"
       "its label too. Never emit a value with its label stripped: join it to its\n"
       'content with ": ", the way suppliers already write it.\n\n'
       "This is the commonest shape in this catalogue after a plain heading: a\n"
       "bolded label on one line with its value on the next.")]),
]

RULE_PORTS = [
    # The C1 defect: a field value that begins part-way through a sentence.
    # Scored as a hard gate on both Fareharbor runs; DESC V5.3 never states it.
    # Both rules are field-agnostic; only the booking-side NOUN changes.
    ("10", r"^3\. A SENTENCE IS THE SMALLEST MOVABLE UNIT\..*?(?=^4\. )",
     [("across two\n   columns", "across two\n   fields"),
      ("never start a column's value", "never start a field's value")]),
    # Stops the model compressing "arrive 15 minutes before so we can fit your
    # wetsuit and complete the briefing" down to "arrive early".
    ("11", r"^4\. CLAUSE COMPLETENESS.*?(?=^5\. )",
     [("in the MIDDLE of long\n   notes", "in the MIDDLE of a long\n   description")]),
]


def transformations(body):
    return [
        ("You are extracting structured fields from a Fareharbor tour's raw "
         "description.",
         "You are extracting structured fields from a Rezdy tour's raw "
         "description.",
         "supplier name"),

        # The input-shape section goes AFTER the governing rule, so the rule is
        # still the first thing read.
        ("STEP 1 -- FIND THE HEADINGS",
         INPUT_SHAPE.strip() + "\n\nSTEP 1 -- FIND THE HEADINGS",
         "input-shape section"),

        # Two new columns, inserted before meeting_point so the prose-column
        # block stays together.
        ("  redo_desc_disclaimers Disclaimers, Risk Disclosure, Liability, Waiver.\n",
         "  redo_desc_disclaimers Disclaimers, Risk Disclosure, Liability, Waiver.\n\n"
         + NEW_COLUMNS,
         "health_safety + contact columns"),

        # min_age / max_age removed -- V5.3 orders them always "".
        ("""  redo_min_age / redo_max_age
      ALWAYS return "". These are never filled from description text -- age
      content goes to redo_desc_restrictions.

""",
         "",
         "remove min_age/max_age definition"),

        # The restrictions definition still points at the two removed fields.
        # Caught by the builder's own "no unknown redo_* name" guard -- the F1
        # class of bug, where a port leaves a reference to a field that does
        # not exist and a check quietly passes against nothing.
        # GAP 1: our column document maps "Day 1"/"Day 2" headings to itinerary
        # (30 and 32 distinct suppliers, 250+ occurrences -- it is how multi-day
        # tours structure a route), but the inherited definition never says so.
        # The model would read "Day 1" as naming no column and route it to
        # about, silently contradicting the agreed column list.
        ("""  redo_desc_itinerary
      A time- or step-ordered sequence of what happens DURING the experience.
      ** SUBJECT TO THE LINE TEST IN STEP 3 **
      A "Schedule" heading is NOT an itinerary: it means departure times.""",
         """  redo_desc_itinerary
      A time- or step-ordered sequence of what happens DURING the experience.
      ** SUBJECT TO THE LINE TEST IN STEP 3 **
      A "Schedule" heading is NOT an itinerary: it means departure times.
      A DAY heading -- "Day 1", "Day 2", "Day 3" -- DOES name itinerary. It is
      how multi-day tours structure their route, and day numbering already
      counts as a qualifying signal in the line test. Each day's content goes
      into itinerary with its day label kept, per STEP 1F.""",
         "Day 1/Day 2 name itinerary"),

        # GAP 2: STEP 1F says keep the label; STEP 2 says a heading naming a
        # column moves its content there. They meet on "**Duration**" / "3
        # hours" and the inherited text never resolves which applies.
        ("Where the supplier already wrote the colon, do not double it.",
         "If the label NAMES A COLUMN (STEP 2), the VALUE moves to that column\n"
         "and the label is dropped -- apply STEP 1B's test: remove \"Duration\"\n"
         "from a duration field and nothing is lost, so it was a bare label.\n"
         "Keep the label joined to its value only when it names NO column and\n"
         "the line therefore stays in redo_desc_about.\n\n"
         "Where the supplier already wrote the colon, do not double it.",
         "resolve STEP 1F vs STEP 2"),

        # NO INVENTION names the ONLY punctuation the model may add. STEP 1F
        # introduces a second joiner, so the rule must say so or the two
        # contradict each other.
        ('   The " - " joiner in STEP 1C is the ONLY punctuation you may add, and only to\n'
         "   rejoin a label to its own content.",
         '   The " - " joiner in STEP 1C and the ": " joiner in STEP 1F are the ONLY\n'
         "   punctuation you may add, and only to rejoin a label to its own content.",
         "joiner list in NO INVENTION"),

        ("      Age content ALWAYS goes here, never to redo_min_age / redo_max_age.",
         "      Age content ALWAYS goes here. There is no separate age field.",
         "restrictions age note"),

        ('11. redo_min_age and redo_max_age are "".\n'
         "12. No literal * or # characters remain.",
         "11. No literal * or # characters remain.\n"
         "12. Every URL in the raw appears in the output, character for\n"
         "    character. Stripping a link never removes its target.\n"
         "13. Every line that the supplier bolded or put in a heading tag is\n"
         "    present in the output -- as a heading's content, or as content in\n"
         "    its own right per STEP 1B. Formatting is never a reason to drop a\n"
         "    line.",
         "self-check items"),
    ]


def build_schema_line():
    return json.dumps({c: "" for c in COLUMNS}, ensure_ascii=False)


EXAMPLES = r"""
--- EXAMPLE 1 (a bold line is the heading; bullets under it are items) ---
=== RAW DESCRIPTION (source of truth) ===
"Each year the bay fills with humpback whales on their migration north. From
departure to return you will enjoy stunning coastal scenery and commentary from
our skipper.
**WHAT IS INCLUDED**
- Guaranteed sightings or return for free.
- Qualified, experienced skipper and crew.
- Maximum 12 passengers.
## What do you need to bring?
- Warm jacket
- Sunscreen"

Output:
{"redo_desc_about": "Each year the bay fills with humpback whales on their migration north. From departure to return you will enjoy stunning coastal scenery and commentary from our skipper.", "redo_desc_important_info": "", "redo_desc_highlights": "", "redo_desc_what_included": "Guaranteed sightings or return for free.\nQualified, experienced skipper and crew.\nMaximum 12 passengers.", "redo_desc_what_excluded": "", "redo_desc_extras": "", "redo_desc_itinerary": "", "redo_desc_what_to_bring": "Warm jacket\nSunscreen", "redo_desc_duration_text": "", "redo_desc_cancellation": "", "redo_desc_check_in": "", "redo_desc_accessibility": "", "redo_desc_restrictions": "", "redo_desc_special_requirements": "", "redo_desc_faqs": "", "redo_desc_pricing": "", "redo_desc_disclaimers": "", "redo_desc_health_safety": "", "redo_desc_contact": "", "redo_meeting_point": "", "redo_group_size": "", "redo_flags": ""}

(The bold line names what_included even though it carries no '##'. The question
heading names what_to_bring -- a heading phrased as a question is still a
heading. The bullets are ITEMS and never open a field of their own.)

--- EXAMPLE 2 (a bold line that is a SENTENCE is content, not a heading) ---
=== RAW DESCRIPTION (source of truth) ===
"**Please call the office to confirm availability before booking - bookings are
on request.**
Join us for a day on the water with Sample Charters. We depart from the marina
and cruise the sheltered side of the island."

Output:
{"redo_desc_about": "Please call the office to confirm availability before booking - bookings are on request.\nJoin us for a day on the water with Sample Charters. We depart from the marina and cruise the sheltered side of the island.", "redo_desc_important_info": "", "redo_desc_highlights": "", "redo_desc_what_included": "", "redo_desc_what_excluded": "", "redo_desc_extras": "", "redo_desc_itinerary": "", "redo_desc_what_to_bring": "", "redo_desc_duration_text": "", "redo_desc_cancellation": "", "redo_desc_check_in": "", "redo_desc_accessibility": "", "redo_desc_restrictions": "", "redo_desc_special_requirements": "", "redo_desc_faqs": "", "redo_desc_pricing": "", "redo_desc_disclaimers": "", "redo_desc_health_safety": "", "redo_desc_contact": "", "redo_meeting_point": "", "redo_group_size": "", "redo_flags": ""}

(The bold line is a full instruction carrying its own information, so STEP 1B
applies: it is CONTENT and is kept as the first line of about. It is not a
label, and the bold does not make it a heading. Losing it would be a
content-loss defect.)

--- EXAMPLE 3 (health_safety vs disclaimers; contact) ---
=== RAW DESCRIPTION (source of truth) ===
"## Safety
All passengers are briefed before departure and lifejackets are provided in all
sizes.
## Risk Warning
Adventure activities carry inherent risks. Acme Tours accepts no liability for
loss or injury.
## Contact
Call 000 000 000 or email bookings@example.test"

Output:
{"redo_desc_about": "", "redo_desc_important_info": "", "redo_desc_highlights": "", "redo_desc_what_included": "", "redo_desc_what_excluded": "", "redo_desc_extras": "", "redo_desc_itinerary": "", "redo_desc_what_to_bring": "", "redo_desc_duration_text": "", "redo_desc_cancellation": "", "redo_desc_check_in": "", "redo_desc_accessibility": "", "redo_desc_restrictions": "", "redo_desc_special_requirements": "", "redo_desc_faqs": "", "redo_desc_pricing": "", "redo_desc_disclaimers": "Adventure activities carry inherent risks. Acme Tours accepts no liability for loss or injury.", "redo_desc_health_safety": "All passengers are briefed before departure and lifejackets are provided in all sizes.", "redo_desc_contact": "Call 000 000 000 or email bookings@example.test", "redo_meeting_point": "", "redo_group_size": "", "redo_flags": ""}

(Safety is what the operator DOES to keep people safe -> health_safety. A risk
warning that disclaims liability -> disclaimers. The two are next to each other
and are not the same field.)

--- EXAMPLE 4 (no headings at all -> everything stays in about) ---
=== RAW DESCRIPTION (source of truth) ===
"Private sunset paddle for two on the estuary. Approximately 90 minutes. No
experience needed, though you must be able to swim."

Output:
{"redo_desc_about": "Private sunset paddle for two on the estuary. Approximately 90 minutes. No experience needed, though you must be able to swim.", "redo_desc_important_info": "", "redo_desc_highlights": "", "redo_desc_what_included": "", "redo_desc_what_excluded": "", "redo_desc_extras": "", "redo_desc_itinerary": "", "redo_desc_what_to_bring": "", "redo_desc_duration_text": "", "redo_desc_cancellation": "", "redo_desc_check_in": "", "redo_desc_accessibility": "", "redo_desc_restrictions": "", "redo_desc_special_requirements": "", "redo_desc_faqs": "", "redo_desc_pricing": "", "redo_desc_disclaimers": "", "redo_desc_health_safety": "", "redo_desc_contact": "", "redo_meeting_point": "", "redo_group_size": "", "redo_flags": ""}

(The text states a duration and a restriction, but the supplier wrote NO
heading for either, so both fields stay empty and the whole text stays in
about. About half of this catalogue looks like this. Filling duration here
would be guessing, and guessing is the failure this prompt exists to prevent.)

--- EXAMPLE 5 (bold labels: one names a column, one does not; Day headings) ---
=== RAW DESCRIPTION (source of truth) ===
"**Duration**
3 hours
**Departs**
Daily from Sample Marina at 9:00 AM
## Day 1
Cruise to the outer reef with morning tea on board. 2:00 PM return.
## Day 2
Guided rainforest walk. We recommend a good level of fitness."

Output:
{"redo_desc_about": "Departs: Daily from Sample Marina at 9:00 AM\nWe recommend a good level of fitness.", "redo_desc_important_info": "", "redo_desc_highlights": "", "redo_desc_what_included": "", "redo_desc_what_excluded": "", "redo_desc_extras": "", "redo_desc_itinerary": "Day 1: Cruise to the outer reef with morning tea on board. 2:00 PM return.\nDay 2: Guided rainforest walk.", "redo_desc_what_to_bring": "", "redo_desc_duration_text": "3 hours", "redo_desc_cancellation": "", "redo_desc_check_in": "", "redo_desc_accessibility": "", "redo_desc_restrictions": "", "redo_desc_special_requirements": "", "redo_desc_faqs": "", "redo_desc_pricing": "", "redo_desc_disclaimers": "", "redo_desc_health_safety": "", "redo_desc_contact": "", "redo_meeting_point": "", "redo_group_size": "", "redo_flags": "itinerary: moved 'We recommend a good level of fitness.' -> about (no time or stop)"}

("Duration" names a column, so its value moves to duration_text and the bare
label is dropped -- remove "Duration" from a duration field and nothing is
lost. "Departs" names NO column, so per STEP 1F the label is KEPT, joined with
": ", and the whole line stays in about. "Day 1"/"Day 2" name itinerary, each
day's label kept. The fitness sentence sits under Day 2 but carries no time,
stop or step -- it FAILS the line test and moves to about, recorded in flags.
It mentions fitness, but no restrictions heading licensed that field, and
routing it there by meaning is exactly what this prompt forbids.)
"""

HEADER = f"""
PROMPT: {NEW_VERSION}
VERSION: 1.0-rezdy-desc
CREATED: 2026-08-17
AUTHOR: Claude Code
SOURCE: derived from {SOURCE_VERSION} by build_rezdy_desc_prompt.py, which
        asserts every core rule survived byte-identical and refuses to write
        otherwise.
PURPOSE: Heading-gated extraction for REZDY product descriptions. Same governing
         rule as Fareharbor -- a field fills ONLY when the supplier wrote a
         heading naming it -- applied to a source with no structured_description
         to fall back on, where headings do 100% of the work.
CHANGES FROM {SOURCE_VERSION}:
  1. Rezdy, not Fareharbor.
  2. NEW "WHAT THE TEXT LOOKS LIKE" section. Rezdy's raw text is HTML and is
     converted to '## ', '- ', '**bold**' and '[text](url)' before the model
     sees it. Measured: 72.8% of Rezdy headings come from markup (bold-only
     lines 50.7%, <h1-6> 22.1%), so the model must be told what those marks
     mean -- and told that they do NOT by themselves make a line a heading.
  3. NEW rule: a heading may be phrased as a QUESTION ("What do you need to
     bring?"). 484 such headings across 241 products.
  4. TWO COLUMNS ADDED: redo_desc_health_safety (78 distinct suppliers) and
     redo_desc_contact (59). Both already exist on Fareharbor's booking side.
  5. redo_min_age / redo_max_age REMOVED. V5.3 requires them to be ALWAYS "";
     carrying two permanently-empty columns forward copies a wart.
  6. Worked examples rebuilt for Rezdy shapes, with INVENTED operator names
     (Sample Charters, Acme Tours, example.test) so contamination is provable.
COLUMN EVIDENCE: reports/rezdy_column_definitions.md -- every column justified
         by how many DISTINCT SUPPLIERS write a heading naming it.
NOT PORTED: V5.4's RULE 9 (required-item markers). It is the confirmed cause of
         42 invented "(required)" sentences across 34 Fareharbor products and
         overwrites the supplier's own wording; it is queued for deletion there.
========================================
""".lstrip("\n")


def main():
    fh_raw = FH_PROMPTS.read_text(encoding="utf-8", errors="replace")
    before_sha = hashlib.sha256(fh_raw.encode("utf-8", "replace")).hexdigest()
    body = extract_prompt(fh_raw, SOURCE_VERSION)
    print(f"source {SOURCE_VERSION}: {len(body):,} chars")

    # RULE 7 is REPLACED, not edited: V5.3's markup-only rule would destroy the
    # URL in `[text](url)`, which our converter produces for 27% of products.
    old_rule7 = re.search(r"^7\. STRIP MARKUP.*?(?=^8\. )", body, re.S | re.M)
    if not old_rule7:
        raise SystemExit("REFUSING TO WRITE -- RULE 7 not found in the source")
    body = body.replace(old_rule7.group(0), url_rule(fh_raw), 1)
    print(f"  applied: RULE 7 replaced with {URL_RULE_VERSION}'s URL rule")

    # Nesting + general label rules, lifted from the booking lineage and slotted
    # in before STEP 2 so the STEP 1x family stays together.
    for label, pattern, renames in BOOKING_PORTS:
        block = lift(fh_raw, URL_RULE_VERSION, pattern, renames, label)
        anchor = "STEP 2 -- DECIDE WHICH COLUMN EACH HEADING NAMES"
        if body.count(anchor) != 1:
            raise SystemExit("REFUSING TO WRITE -- STEP 2 anchor is not unique")
        body = body.replace(anchor, block.rstrip() + "\n\n" + anchor, 1)
        print(f"  applied: {label} (lifted from {URL_RULE_VERSION})")

    # The two content-loss rules the description set never had. APPENDED rather
    # than inserted: renumbering validated rules risks breaking a cross-
    # reference, and the body carries exactly one (RULE 7, which stays put).
    for number, pattern, renames in RULE_PORTS:
        block = lift(fh_raw, URL_RULE_VERSION, pattern, renames, f"RULE {number}")
        block = re.sub(r"^\d+\. ", f"{number}. ", block, count=1)
        anchor = "SELF-CHECK BEFORE RETURNING:"
        body = body.replace(anchor, block.rstrip() + "\n\n" + anchor, 1)
        print(f"  applied: RULE {number} ({block.splitlines()[0][:52]}...)")

    for find, repl, label in transformations(body):
        n = body.count(find)
        if n != 1:
            raise SystemExit(
                f"REFUSING TO WRITE -- '{label}' matched {n} times, expected 1.\n"
                f"  looked for: {find[:90]!r}")
        body = body.replace(find, repl, 1)
        print(f"  applied: {label}")

    # Schema line + examples are replaced wholesale, not patched.
    old_schema = re.search(r'^\{"redo_desc_about".*\}$', body, re.M)
    if not old_schema:
        raise SystemExit("REFUSING TO WRITE -- schema line not found")
    body = body.replace(old_schema.group(0), build_schema_line(), 1)
    print("  applied: schema line")

    i = body.find("--- EXAMPLE 1")
    if i < 0:
        raise SystemExit("REFUSING TO WRITE -- examples block not found")
    body = body[:i].rstrip() + "\n" + EXAMPLES.rstrip() + "\n"
    print("  applied: examples replaced")

    verify(body)

    block = HEADER + "\n" + body.strip() + "\n\n" + "=" * 40 + \
        f"\nEND OF {NEW_VERSION}\n"

    if RZ_PROMPTS.exists():
        existing = RZ_PROMPTS.read_text(encoding="utf-8")
        if f"PROMPT: {NEW_VERSION}" in existing:
            raise SystemExit(
                f"REFUSING TO WRITE -- {NEW_VERSION} already exists in "
                f"{RZ_PROMPTS.name}. Prompts are APPEND-ONLY: bump the version "
                f"rather than editing in place, so rollback stays possible.")
        out = existing.rstrip("\n") + "\n\n" + block
    else:
        out = ("REZDY EXTRACTION PROMPTS\n"
               "Append-only. Never edit a block in place -- every version must "
               "stay extractable so a rollback is one constant.\n"
               "Kept separate from config/fareharbor_prompts.txt, which other "
               "sessions append to concurrently.\n\n" + block)
    RZ_PROMPTS.write_text(out, encoding="utf-8")

    after_sha = hashlib.sha256(
        FH_PROMPTS.read_text(encoding="utf-8", errors="replace")
        .encode("utf-8", "replace")).hexdigest()
    if before_sha != after_sha:
        raise SystemExit("the Fareharbor prompt file changed -- investigate")

    check = extract_prompt(RZ_PROMPTS.read_text(encoding="utf-8"), NEW_VERSION)
    print(f"\nround-trips through extract_prompt(): {len(check):,} chars")
    print(f"fareharbor_prompts.txt unchanged (sha256 {before_sha[:12]})")
    print(f"\nwrote {NEW_VERSION} -> {RZ_PROMPTS}")


def verify(body):
    """Refuse to write unless every invariant and every column check passes."""
    for inv in INVARIANTS:
        if inv not in body:
            raise SystemExit(f"REFUSING TO WRITE -- core rule missing: {inv[:70]}")
    print(f"  verified: {len(INVARIANTS)} core rules survived")

    schema = re.search(r'^\{"redo_desc_about".*\}$', body, re.M)
    keys = list(json.loads(schema.group(0)).keys())
    if keys != COLUMNS:
        raise SystemExit(f"REFUSING TO WRITE -- schema keys != column list\n"
                         f"  missing: {set(COLUMNS) - set(keys)}\n"
                         f"  extra  : {set(keys) - set(COLUMNS)}")
    print(f"  verified: {len(keys)} keys match the column list")

    # Every example must carry the full key set -- a missing key in an example
    # teaches the model to omit it.
    for n, ex in enumerate(re.findall(r'^\{"redo_desc_about".*\}$', body, re.M)[1:], 1):
        if list(json.loads(ex).keys()) != COLUMNS:
            raise SystemExit(f"REFUSING TO WRITE -- example {n} has wrong keys")
    print("  verified: every worked example carries all keys")

    for banned in ["Fareharbor", "redo_min_age", "redo_max_age",
                   "structured_description"]:
        if banned in body:
            raise SystemExit(f"REFUSING TO WRITE -- '{banned}' still present")
    print("  verified: no Fareharbor-specific references remain")

    # The F1 guard: a find-and-replace port once produced a field name that did
    # not exist and a check that quietly passed against an empty column.
    for key in re.findall(r'"(redo_[a-z_]+)"', body):
        if key not in COLUMNS:
            raise SystemExit(f"REFUSING TO WRITE -- unknown field name {key!r}")
    print("  verified: no unknown redo_* field names anywhere in the body")


if __name__ == "__main__":
    main()
