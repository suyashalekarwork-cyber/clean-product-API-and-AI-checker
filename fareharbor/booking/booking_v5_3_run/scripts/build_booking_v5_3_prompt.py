"""
Append SYSTEM_PROMPT_FH_BOOKING_V5_3 to config/fareharbor_prompts.txt.

Built from reports/booking_column_definitions.md, which derives every column
from a census of all 8,244 products with booking notes (17,212 heading
occurrences, 3,729 distinct wordings, counted by supplier spread as well as
frequency).

WHAT CHANGES FROM SYSTEM_PROMPT_FH_BOOKING_V5 (15 keys -> 25 keys):

  RENAMED, and these are load-bearing:
    inclusions -> what_included      } the description side uses these names.
    location   -> meeting_point      } Without the rename a desc->booking
                                       find-and-replace produces a field that
                                       does not exist and a check that quietly
                                       passes against an empty column (F1).

  REPLACED:
    other -> booking_notes           A named default destination, not a junk
                                     drawer. "A catch-all that accepts anything
                                     ends up being given everything."

  NEW (10), each justified by measured supplier counts:
    health_safety   492 occurrences / 72 suppliers -- more suppliers than
                    restrictions (65), pricing (60) or cancellation (35), and
                    the unified schema already has a Health & Safety section
                    fed from a different API field.
    disclaimers     511 / 86        pricing        371 / 60
    accessibility    60 / 13        special_requirements 59 / 18
    duration_text    55 / 14        extras          45 / 24
    group_size       33 /  7        what_excluded   24 / 15
    highlights      ~13 /  5

TWO DEFECT FIXES from the 100-product V5 run:

  1. PROMPT CONTAMINATION (78026). important_info held "We do not operate when
     winds exceed 25 knots." -- absent from that product's raw text, and
     verbatim from EXAMPLE 3 of the V5 prompt. The examples read as plausible
     real operational text, so the model lifted one. Fixed by making every
     example obviously synthetic (invented operator names, absurd-but-clear
     values) AND stating explicitly that example text must never be copied.

  2. LINK LOSS. "[See here](https://realnz.com/...) for full Terms and
     Conditions" became "See here for full Terms and Conditions." -- the URL
     destroyed by the strip-markup rule (257745, 582339). On 637073 a URL was
     silently ALTERED (maps.app.goo.gl/... -> goo.gl/...). Fixed by a rule that
     stripping markdown keeps the link target verbatim.

DUPLICATION IS NOT FIXED HERE. Three prompt versions failed at it on the
description side. It is reported by booking_postprocess.py, never auto-removed
-- a dedup pass trialled earlier would have emptied 9 booking fields across 8
products (F2).

Usage:
    python build_booking_v5_3_prompt.py           # dry run
    python build_booking_v5_3_prompt.py --write   # append the block
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent.parent
PROMPTS = ROOT / "config" / "fareharbor_prompts.txt"
BACKUP = ROOT / "config" / "fareharbor_prompts.txt.bak_before_booking_v5_3"

NEW_VERSION = "SYSTEM_PROMPT_FH_BOOKING_V5_3"
RULE = "=" * 40

FIELDS = [
    "redo_booking_notes",
    "redo_booking_highlights",
    "redo_booking_what_to_bring",
    "redo_booking_what_not_to_bring",
    "redo_booking_what_included",
    "redo_booking_what_excluded",
    "redo_booking_extras",
    "redo_booking_meeting_point",
    "redo_booking_check_in",
    "redo_booking_before_arrival",
    "redo_booking_departure_info",
    "redo_booking_itinerary",
    "redo_booking_duration_text",
    "redo_booking_important_info",
    "redo_booking_health_safety",
    "redo_booking_restrictions",
    "redo_booking_special_requirements",
    "redo_booking_accessibility",
    "redo_booking_group_size",
    "redo_booking_cancellation",
    "redo_booking_disclaimers",
    "redo_booking_pricing",
    "redo_booking_faqs",
    "redo_booking_contact",
    "redo_booking_flags",
]
SCHEMA_LINE = "{" + ", ".join(f'"{f}": ""' for f in FIELDS) + "}"


def _json(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def out(**vals):
    bad = set(vals) - set(FIELDS)
    if bad:
        raise SystemExit(f"example uses unknown field(s): {sorted(bad)}")
    return "{" + ", ".join(f'"{f}": {_json(vals.get(f, ""))}' for f in FIELDS) + "}"


HEADER = f"""PROMPT: {NEW_VERSION}
VERSION: 5.3-booking
CREATED: 2026-08-11
AUTHOR: Claude Code
PURPOSE: Heading-gated extraction for booking_notes, with the column list
         derived from a census of all 8,244 products that have booking notes
         (17,212 heading occurrences, 3,729 distinct wordings). Supersedes
         SYSTEM_PROMPT_FH_BOOKING_V5, whose columns were inherited from V4.7
         rather than measured.
         25 keys, up from 15. Renames inclusions->what_included and
         location->meeting_point so the booking and description sides can be
         merged mechanically. Replaces `other` with `booking_notes`, a named
         default destination. Adds 10 columns, each justified by supplier
         counts -- notably health_safety (72 suppliers), which had no home at
         all despite an existing Health & Safety page section.
         Fixes two defects found in the 100-product V5 run: text copied out of
         the prompt's own worked examples into a real product (78026), and
         URLs destroyed or altered while stripping markdown (257745, 582339,
         637073).
         Duplication is deliberately NOT addressed here -- it is reported by
         post-processing, never auto-removed.
         The description prompt is unchanged.
{RULE}"""


BODY = '''You are extracting structured fields from a Fareharbor tour's raw BOOKING NOTES
-- the operational text sent to a customer after they book.

THE ONE RULE THAT GOVERNS EVERYTHING:

Extract content into a column ONLY when the supplier wrote a HEADING for it in
the raw text. If there is no heading, the column stays "" and the text goes to
redo_booking_notes.

An empty column is a CORRECT answer. A column filled by guessing is a failure.
You are not rewarded for filling columns. You are rewarded for being right.

Many booking notes are SHORT and have no headings at all. For those, everything
belongs in redo_booking_notes and every other column is "". That is the rule
working correctly, not a failure to extract.

NOTHING IS EVER DELETED. Only greetings, sign-offs and separator rules may be
omitted, and you must record those in redo_booking_flags.

STEP 1 -- FIND THE HEADINGS

A heading is a short label line that INTRODUCES the content beneath it. It is
usually on its own line, often ends with ":", and is frequently in Title Case,
ALL CAPS, bold, or a markdown/HTML header (#, ##, <h2>).

These are all headings:
    What to Bring         ## Location          **Check In**
    Departure Information:                     IMPORTANT INFORMATION
    Prior to Arrival:     Tour Requirements    Boarding Location:

These are NOT headings:

  - A BULLET OR LIST ITEM. THIS IS THE MOST IMPORTANT EXCLUSION ON THE BOOKING
    SIDE, because booking notes are mostly lists -- a third of all lines are
    bulleted. Under a "What to Bring" heading, every one of these is an ITEM:
        sunscreen        towel           water bottle      hat
        swimwear         wetsuit         camera            sunglasses
        insect repellent rash shirt      comfortable shoes warm jacket
    They are short, capitalised, and have no full stop -- they look exactly like
    headings and they are not. A line naming a THING THE CUSTOMER CARRIES OR
    WEARS is an item. It belongs in the column its heading opened, one per line.
    It NEVER opens a new column.
    If you find yourself creating a section for "Sunscreen", stop -- you have
    mistaken a packing item for a heading.

  - A HEADING MUST NAME A COLUMN, NOT A FACT. Ask: could this heading appear on
    ANY tour? "What to Bring" could. "Nearest train station to Darling Harbour"
    could not -- it states a fact about one venue. Facts are content.
        "Plan your trip ahead of time with NSW Transport"   -> NOT a heading
        "Nearest train station to Darling Harbour"          -> NOT a heading
        "Booking subject to Acme Cruises' terms"            -> NOT a heading
    All three are content. They go to redo_booking_notes with their text intact.

  - A PHRASE INSIDE A SENTENCE. A sentence that happens to contain "bring",
    "we provide", "includes" or "meet at" is ordinary prose.
        "Please bring a towel and sunscreen."      -> NOT a heading
        "We provide all safety equipment."          -> NOT a heading
    Each carries its own meaning. With no heading above it, it stays in
    redo_booking_notes.

  - A SEPARATOR RULE. Lines of underscores, dashes or asterisks
    ("______________", "--------") are visual dividers. Drop them.

  - AN INFORMATIVE LINE THAT ONLY LOOKS LIKE A HEADING. See STEP 1B -- these
    are CONTENT and must be KEPT.

STEP 1B -- A LINE THAT LOOKS LIKE A HEADING BUT CARRIES ITS OWN INFORMATION
           IS CONTENT. KEEP IT.

You drop a heading line only because it is a bare LABEL -- the word "Location"
tells the customer nothing once the address sits in the location column. That
reasoning applies ONLY to bare labels.

A short line standing alone is CONTENT when it carries information of its own:

  - It states a fact, time, date or instruction:
        "Please arrive 15 minutes prior"
        "Check-in time: 2pm"
        "The marina gate closes at 6pm sharp."
  - It is a complete sentence, or contains a verb, a date, a time or a number
    appearing nowhere else.

TEST: remove the line. Is any information gone? YES -> CONTENT, keep it.
NO (the content beneath already says it) -> LABEL, drop it.

    "What to Bring" + "towel, hat"   -> remove it: nothing lost.       LABEL.
    "Please arrive 15 minutes prior" -> remove it: the instruction and
                                        the timing are gone.           CONTENT.

Losing one of these is a content-loss defect, exactly like dropping a sentence.

STEP 1C -- KEEP EVERY LABEL, JOINED TO ITS CONTENT

Never emit a value with its label stripped. Join a label to its content with
": " -- the way suppliers already write it.

    RAW:                            CORRECT:
    Duration                        Duration: 3 Hours
      3 Hours
    Saturday                        Saturday: Meet at the wharf at 8:00 AM.
      Meet at the wharf at 8:00 AM

Where the supplier already wrote the colon, do not double it.
A dropped label is content loss that no retention check can see: without it the
customer cannot tell which day, tier or option each line describes.

STEP 1D -- INLINE "Label: value" ON ONE LINE

A single line holding BOTH a label and its value counts as a heading:

    Check-in time: 2pm              label "Check-in time" -> check_in
    Location: Devonport Beach       label "Location"      -> meeting_point
    Footwear: closed-toe shoes      label "Footwear"      -> what_to_bring
    ABN: 12 345 678 901             names no column       -> booking_notes

When the label names a column, THE WHOLE LINE MOVES -- label included, because
the value is meaningless without it. When it names no column, the whole line
stays in redo_booking_notes.

STEP 1E -- NESTED HEADINGS: THE OUTER HEADING WINS

A supplier may write a big section and break it into labelled sub-parts. The
OUTER heading decides the column. Sub-headings do NOT re-route the content --
they stay as labels on their own text, per STEP 1C.

    RAW:
      ###ADDITIONAL INFORMATION
        **Information for parking near the wharf**  - Acme Parking
        **Nearest train station**                   - Example Station
        **Booking subject to our terms**            - example.test/terms

    CORRECT -> all of it in redo_booking_notes, every label kept:
      ADDITIONAL INFORMATION:
      Information for parking near the wharf: Acme Parking
      Nearest train station: Example Station
      Booking subject to our terms: example.test/terms

    WRONG -> promoting the parking and station blocks to meeting_point because
    their CONTENT looks like location information. That is classification by
    meaning, and it is forbidden.

"Additional Information" names redo_booking_notes, so everything beneath it goes
there -- even content that would have gone elsewhere under its own heading.

STEP 2 -- DECIDE WHICH COLUMN EACH HEADING NAMES

MATCH HEADINGS BY MEANING, NOT BY EXACT STRING. Suppliers phrase headings freely
-- there are over 3,700 distinct wordings in this catalogue. Ignore differences
in casing, punctuation, spacing, singular vs plural, and minor wording. All of
these are the SAME heading:
    "What to Bring", "What To Bring:", "WHAT TO BRING", "Please Bring",
    "What you need to bring", "**What should I bring with me?**"
    "Boarding Location:", "BOARDING LOCATION", "Boarding Details:"

THIS IS THE ONLY PLACE MEANING IS ALLOWED: deciding WHICH HEADING a line is.
Deciding where a SENTENCE belongs is never done by meaning -- that is what the
heading is for.

TRUST THE SUPPLIER'S HEADING EVEN WHEN THE CONTENT DISAGREES WITH IT. If a
supplier writes "We supply all safety gear" under a What to Bring heading, it
STAYS in what_to_bring. Record the mismatch in redo_booking_flags. Do not move
it.

If a heading does not clearly name any column below, leave its content in
redo_booking_notes. Do not force a match.

THE COLUMNS:

  redo_booking_notes
      DEFAULT DESTINATION. All text with no heading, PLUS content under any
      heading that names no column, PLUS any line rejected by the line tests in
      STEP 3, PLUS every informative heading-shaped line from STEP 1B whose
      section names no column.
      This column being large is CORRECT. It is the honest home for unlabelled
      content -- the customer still reads it.

  redo_booking_highlights
      Selling points -- why choose THIS experience.
      Never build this by selecting or rewording lines from another column.

  redo_booking_what_to_bring
      What the customer must bring or wear. Headings: What to Bring, What to
      Wear, Please Bring, What You Need to Bring, Packing List, Dress Code,
      Footwear, Clothing, Gear, Equipment, Things to Pack, Don't Forget.
      Everything under such a heading is an ITEM -- one per line.

  redo_booking_what_not_to_bring
      Items explicitly prohibited: What NOT to Bring, Do Not Bring, Prohibited
      Items, items "not permitted".

  redo_booking_what_included
      What the price covers at no extra cost. Headings: Inclusions, What's
      Included, Includes, We Provide, What We Provide, What is Provided,
      Package Inclusions.  ** SUBJECT TO THE LINE TEST IN STEP 3 **

  redo_booking_what_excluded
      Explicitly NOT covered: Not Included, Exclusions, At Your Own Expense.

  redo_booking_extras
      Optional add-ons available at extra cost, or upgrades.

  redo_booking_meeting_point
      Where to meet or where the activity happens: Meeting Point, Meeting
      Location, Location, Where to Meet, Getting There, How to Get There,
      Directions, Address, Venue, Parking, Boarding Location.
      An address ALONE is meeting_point. A time ALONE is departure_info.

  redo_booking_check_in
      What to DO on arrival, and arrival timing: Check In, Check-in, Check-in
      Time, Arrival, Arrival Time, On Arrival, On the Day, Registration,
      Sign In.
      Arrival instructions written as sentences belong here too.

  redo_booking_before_arrival
      Things to do BEFORE the day: Prior to Arrival, Before You Arrive, Before
      You Join, complete a waiver in advance, create an account, pre-book
      parking, apply for a licence. Distinct from check_in, which is on the day.

  redo_booking_departure_info
      When and from where the activity LEAVES: Departure Information, Departure
      Times, Boarding Time, Pickup Times, Schedule, Timetable.
      A list of departure TIMES is not an itinerary.

  redo_booking_itinerary
      A time- or step-ordered sequence of what happens DURING the experience.
      ** SUBJECT TO THE LINE TEST IN STEP 3 **

  redo_booking_duration_text
      How long the experience lasts. NOT opening hours, NOT operating days.

  redo_booking_important_info
      General notices the supplier flagged as important but which name no more
      specific column. Headings: Important Information, Important, Important
      Note(s), Important Things to Note, Please Note, Notes, Note, Key
      Reminders, Things to Know, Good to Know, General Information, General,
      Other Information, Additional Information, Tour Information, More Info.
      ALSO OWNS WEATHER AND OPERATING CONDITIONS -- conditions under which the
      tour may not run: Weather Policy, Wet Weather Plan, Rain, tide
      dependence, minimum-numbers requirements, seasonal closures, opening
      hours, operator discretion. These are NOT cancellation unless they state
      a refund.
      If a more specific column claims the heading, that column wins.

  redo_booking_health_safety
      Safety rules, hazards, medical and emergency information: Safety, On
      Board Safety, Safe Boarding and Disembarking, Safety Responsibility,
      Responsible Service of Alcohol, First Aid, Sea Sickness, emergency
      procedures, natural-hazard warnings.

  redo_booking_restrictions
      Anything limiting WHO may take part or HOW they must behave:
        - Tour Requirements, Requirements, Prerequisites, Suitability,
          Ability Level, Fitness
        - Tour Rules, Rules, Company Policy, Code of Conduct
        - ALL AGE headings: Ages, Age Range, Age Requirement, Minimum Age
      Age content ALWAYS goes here.

  redo_booking_special_requirements
      Only when the supplier used a "Special Requirements" heading
      specifically, or a dietary/allergy/special-needs heading.

  redo_booking_accessibility
      Wheelchair/mobility access, accessibility information.

  redo_booking_group_size
      Group size, capacity, maximum or minimum participant counts.

  redo_booking_cancellation
      REFUNDS ONLY: refund rules, cancellation windows, no-show terms,
      rescheduling and deposit-forfeit terms.
      A weather or operating condition is NOT cancellation unless the SAME text
      states what happens to the customer's money.
          "We do not operate in high winds"          -> important_info
          "Trips cancelled for weather are refunded" -> cancellation

  redo_booking_disclaimers
      Terms and conditions, disclaimers, waivers, liability, risk disclosure,
      indemnity, privacy, rental agreements.

  redo_booking_pricing
      Rates, prices, cost, fees, deposits, tax, invoice and payment details.
      REQUIRES REAL RATE INFORMATION: the content must carry a number, a
      currency amount, a tax/registration number, or a named charge.
      Marketing copy ABOUT price is NOT pricing and stays in booking_notes.

  redo_booking_faqs
      Q&A content under a FAQ / Questions heading, or a question line followed
      by its answer. A heading ending in "?" is only an FAQ if no other column
      claims it -- "What is included?" names what_included; "Will I get wet?"
      is an FAQ.

  redo_booking_contact
      Phone numbers, email addresses, website and document links, office hours,
      and instructions about how to reach the operator.

  redo_booking_flags
      Diagnostic notes. Never shown to customers. See RULE 11.

STEP 3 -- LINE TESTS (two columns only)

A heading gets content in the door. For redo_booking_itinerary and
redo_booking_what_included ONLY, each line must then independently qualify.
Lines that fail move to redo_booking_notes. Nothing is deleted.

Apply these two tests to NO other column. Every other column moves as a block.

ITINERARY LINE TEST
  A line qualifies only if it carries a structural signal:
    - a clock time            "9:30 AM", "2:00 PM"
    - day or step numbering   "Day 1", "Stop 3"
    - a named stop in order   "Circular Quay -> Manly"
  Ordering words alone ("then", "before", "first") are NOT enough.

WHAT_INCLUDED LINE TEST
  A line qualifies only if the customer receives it at no extra cost. Ask:
  would the customer pay extra for this? If yes, it is not included.
  Disqualifying language, even under an "Inclusions:" heading:
    "available for purchase", "can be purchased", "at extra cost",
    "additional charge", "available for hire", "optional"
  A disqualified line goes to redo_booking_what_excluded (if it is a
  purchasable item) or redo_booking_notes (if it is a general statement), and
  you MUST record it in redo_booking_flags.
  This is the only place a line's content overrides the supplier's heading, so
  it must always be reported.

RULES

1. NO DUPLICATION - extracting is a MOVE, not a copy.
   Each sentence appears in EXACTLY ONE column. When you extract text into a
   column, DELETE it from redo_booking_notes. Do not leave a copy behind.
   Repetition in the SOURCE does not license repetition in the OUTPUT: if the
   supplier wrote the same sentence twice, emit it once, in the most specific
   column. This applies only when the wording is IDENTICAL -- two different
   sentences describing the same thing are both kept.

2. NO CONTENT LOSS - every sentence of the raw text must appear in exactly one
   column. Declining to classify is NEVER permission to delete. When you leave
   a column empty because there was no heading, the text still goes to
   redo_booking_notes.
   Only these may be omitted: greetings ("Kia Ora!", "Hey there!"), sign-offs
   ("We look forward to seeing you", "Thank you for booking"), pure branding
   lines, and separator rules. Record each omission in redo_booking_flags.
   Everything else must be present. When in doubt, keep it.

3. A SENTENCE IS THE SMALLEST MOVABLE UNIT.
   Route a mixed section line by line, but NEVER split a sentence across two
   columns, and never start a column's value part-way through a sentence.
   If a value you are about to emit begins with a lowercase word, or with "to",
   "and", "so", "which", "that", you have split a sentence. Move the whole one.

4. CLAUSE COMPLETENESS - compound and qualifying clauses must be kept in full.
   Do not drop connective, conditional or qualifying clauses even when the main
   idea survives without them. This applies to sentences in the MIDDLE of long
   notes exactly as much as at the start or end.
   "Please arrive 15 minutes before your booked time so we can fit your wetsuit
   and complete the safety briefing" must keep the timing AND both reasons.
   Compressing it to "Please arrive early" is forbidden.

5. NO INVENTION - never write text that is not in the raw booking notes. Do not
   add connective phrases, summaries, or placeholder prose. Never emit strings
   like "No content found in raw text for this field" - use "" instead.
   NEVER COPY TEXT FROM THE EXAMPLES IN THIS PROMPT. The examples below use
   invented operators and invented values. They exist to show FORM, never
   content. If a sentence appears in your output that is not in the raw booking
   notes you were given, you have failed this rule.
   The ": " joiner in STEP 1C and the "Q: "/" A: " markers in RULE 7 are the
   ONLY punctuation you may add.

6. VERBATIM - copy the exact words. Do not reword, rephrase, condense or
   summarise. If you are about to start a sentence with a verb that is not in
   that position in the source, you are rewording - stop and copy the original.
   Keep every numeric figure, including prices, and keep singular/plural and
   company suffixes exactly as written ("Pty Ltd" stays "Pty Ltd").

7. FAQ PAIRING - a question and its answer are one unit and move together.
   If you place a sentence that reads as an ANSWER, you MUST also place the
   QUESTION preceding it in the raw text -- however formatted ("Q:", a bolded
   line, a bare sentence ending in "?", a numbered item). Both go in the SAME
   column, question first, as "Q: <question> A: <answer>".

8. STRIP MARKUP, KEEP THE LINE AND KEEP THE URL.
   Remove *, **, ***, #, ## and backticks from all output values. Extract the
   text inside the markup; never leave the markup characters.
   A MARKDOWN LINK KEEPS ITS TARGET. When you strip [text](url), you MUST keep
   BOTH the text and the url:
       "[See here](https://example.test/terms) for full Terms and Conditions"
       -> "See here (https://example.test/terms) for full Terms and Conditions"
   Emitting "See here for full Terms and Conditions" DESTROYS the link and is a
   content-loss defect: "see here" with no "here" is useless.
   NEVER shorten, expand or otherwise alter a URL. Copy it character for
   character.
   Stripping markup from a line is NEVER a reason to delete the line. An
   asterisk-wrapped standalone line is CONTENT, not decoration.

9. REQUIRED-ITEM MARKERS - if the raw marks items as required using asterisks,
   bold, "(required)", or a legend, PRESERVE that distinction. Because RULE 8
   forbids leaving * in any value, append the literal word "(required)" instead.

10. LIST FORMAT - where the source has bullets, line breaks or numbered items,
    put one item per line (newline-separated) and strip the bullet glyph.
    Do NOT split flowing prose into invented items - that is rewording.

11. FLAGS - redo_booking_flags is a short newline-separated list of diagnostic
    notes. Record: any line moved out of what_included or itinerary by a line
    test; any case where the supplier's heading and its content plainly
    disagree; any greeting or sign-off you omitted; any heading you found
    genuinely ambiguous. Leave "" if nothing to report.

SELF-CHECK BEFORE RETURNING:
1. Every sentence of the raw booking notes appears in exactly one column.
2. No packing-list item was mistaken for a heading.
3. No column value begins part-way through a sentence.
4. Every heading-shaped line carrying its own information is present.
5. Every label is joined to its content; none was dropped.
6. No sentence appears in two columns.
7. Every non-empty column was licensed by a real heading on its own line.
8. Every line in itinerary carries a time, day/step number, or ordered stop.
9. Every line in what_included is free of charge.
10. If cancellation is non-empty, it says what happens to the customer's money.
11. Every URL in the raw appears in the output, character for character.
12. Nothing was reworded; nothing was invented; NO text came from this prompt's
    examples.
13. No literal * or # characters remain.

Return ONLY this JSON, no commentary:
{SCHEMA_LINE}

--- EXAMPLE 1 (no headings -> everything stays in booking_notes) ---
=== RAW BOOKING NOTES (source of truth) ===
"Please arrive 15 minutes before your booked departure time.
Wear closed-toe shoes and bring a hat.
Parking is available on Sample Street."

Output:
{EX1}

(Not one heading here -- just three instructions. Each mentions something that
HAS a column, but a phrase inside a sentence is not a heading, so nothing is
licensed. All three stay in booking_notes. This is the most common shape in the
catalogue and the rule working correctly.)

--- EXAMPLE 2 (packing items are NOT headings; label kept) ---
=== RAW BOOKING NOTES (source of truth) ===
"##What to Bring

Sunscreen
Towel
Water bottle

##Duration
Ninety minutes

##Location
Sample Beach, 1 Testing Road"

Output:
{EX2}

(The three short capitalised lines under What to Bring look exactly like
headings -- short, Title Case, no full stop -- and they are ITEMS. Creating a
"Sunscreen" section would be the classic booking-side failure. Note the
Duration label is KEPT joined to its value per STEP 1C.)

--- EXAMPLE 3 (nesting: the OUTER heading wins) ---
=== RAW BOOKING NOTES (source of truth) ===
"###ADDITIONAL INFORMATION
**Information for parking near the wharf**
- Acme Parking
**Nearest train station**
- Example Station
**Booking subject to our terms**
- [our terms](https://example.test/terms)"

Output:
{EX3}

(ADDITIONAL INFORMATION names booking_notes, so ALL of it goes there -- even the
parking and station blocks, whose CONTENT looks like meeting_point material.
Promoting them would be classification by meaning. Every sub-label is kept, and
the markdown link keeps BOTH its text and its URL per RULE 8.)

--- EXAMPLE 4 (line tests; heading disagrees with content; new columns) ---
=== RAW BOOKING NOTES (source of truth) ===
"Itinerary
9:00 AM - Depart Sample Wharf
10:30 AM - Arrive Testing Island
Please note the kiosk is closed on Mondays.

Inclusions
Return ferry travel
Hot drinks available for purchase onboard

What to Bring
We supply all safety gear including helmets.

Safety
Life jackets must be worn at all times on deck.

Terms
Bookings are subject to our standard conditions."

Output:
{EX4}

(Under Itinerary only the two timed lines qualify; the kiosk note has no time,
step or stop, so it moves to booking_notes. Under Inclusions "available for
purchase" is disqualifying, so that line moves to what_excluded. Under What to
Bring the supplier wrote what THEY provide -- the heading still governs, so it
stays put and the disagreement is recorded in flags. Safety fills the
health_safety column; Terms fills disclaimers.)'''


EX1 = out(
    redo_booking_notes="Please arrive 15 minutes before your booked departure time.\n"
                       "Wear closed-toe shoes and bring a hat.\n"
                       "Parking is available on Sample Street.",
)

EX2 = out(
    redo_booking_what_to_bring="Sunscreen\nTowel\nWater bottle",
    redo_booking_duration_text="Duration: Ninety minutes",
    redo_booking_meeting_point="Sample Beach, 1 Testing Road",
)

EX3 = out(
    redo_booking_notes="ADDITIONAL INFORMATION:\n"
                       "Information for parking near the wharf: Acme Parking\n"
                       "Nearest train station: Example Station\n"
                       "Booking subject to our terms: our terms "
                       "(https://example.test/terms)",
)

EX4 = out(
    redo_booking_what_to_bring="We supply all safety gear including helmets.",
    redo_booking_what_included="Return ferry travel",
    redo_booking_what_excluded="Hot drinks available for purchase onboard",
    redo_booking_itinerary="9:00 AM - Depart Sample Wharf\n"
                           "10:30 AM - Arrive Testing Island",
    redo_booking_health_safety="Life jackets must be worn at all times on deck.",
    redo_booking_disclaimers="Bookings are subject to our standard conditions.",
    redo_booking_notes="Please note the kiosk is closed on Mondays.",
    redo_booking_flags="itinerary: moved kiosk-closure note -> booking_notes "
                       "(no time or stop)\n"
                       "what_included: moved 'Hot drinks available for purchase "
                       "onboard' -> what_excluded (purchasable)\n"
                       "what_to_bring: supplier wrote what THEY provide under a "
                       "What to Bring heading; heading governs, left in place",
)


def render_body():
    return (BODY.replace("{SCHEMA_LINE}", SCHEMA_LINE)
                .replace("{EX1}", EX1).replace("{EX2}", EX2)
                .replace("{EX3}", EX3).replace("{EX4}", EX4))


def probe(raw, version):
    v = re.escape(version)
    return re.search(
        r"PROMPT:\s*" + v + r"\b.*?\n=+\n\n(.*?)\n\n=+\nEND OF " + v + r"\s*$",
        raw, re.S | re.M)


def block_names(raw):
    return re.findall(r"^PROMPT:\s*(\S+)", raw, re.M)


CHECKS = [
    ("the one governing rule", "THE ONE RULE THAT GOVERNS EVERYTHING:"),
    ("empty is correct", "An empty column is a CORRECT answer."),
    ("bullet exclusion stated first", "A BULLET OR LIST ITEM. THIS IS THE MOST IMPORTANT"),
    ("real packing items named", "sunscreen        towel"),
    ("heading must name a column not a fact", "A HEADING MUST NAME A COLUMN, NOT A FACT."),
    ("STEP 1B informative headings", "STEP 1B"),
    ("STEP 1C keep every label", "STEP 1C -- KEEP EVERY LABEL"),
    ("label joiner is ': '", 'Join a label to its content with\n": "'),
    ("STEP 1D inline label", "STEP 1D"),
    ("STEP 1E outer heading wins", "STEP 1E -- NESTED HEADINGS: THE OUTER HEADING WINS"),
    ("trust the supplier heading", "TRUST THE SUPPLIER'S HEADING EVEN WHEN"),
    ("meaning fenced to headings", "THIS IS THE ONLY PLACE MEANING IS ALLOWED"),
    ("default destination named", "DEFAULT DESTINATION"),
    ("line tests scoped to two", "Apply these two tests to NO other column."),
    ("C1 sentence smallest unit", "A SENTENCE IS THE SMALLEST MOVABLE UNIT."),
    ("clause completeness", "CLAUSE COMPLETENESS"),
    ("FIX: no copying from examples", "NEVER COPY TEXT FROM THE EXAMPLES IN THIS PROMPT."),
    ("FIX: markdown link keeps url", "A MARKDOWN LINK KEEPS ITS TARGET."),
    ("FIX: never alter a url", "NEVER shorten, expand or otherwise alter a URL."),
    ("FAQ pairing", "FAQ PAIRING"),
    ("required-item markers", "REQUIRED-ITEM MARKERS"),
    ("weather -> important_info", "NOT cancellation unless they state\n      a refund"),
    ("cancellation = money", "what happens to the customer's money"),
    ("verbatim keeps Pty Ltd", '"Pty Ltd" stays "Pty Ltd"'),
    ("self-check covers urls", "Every URL in the raw appears in the output"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    body = render_body()
    block = HEADER + "\n\n" + body + "\n\n" + RULE + "\nEND OF " + NEW_VERSION

    print(f"block chars: {len(block)}   columns: {len(FIELDS)}")
    ok = True

    missing = [f for f in FIELDS if f'"{f}": ""' not in SCHEMA_LINE]
    print(f"  [{'OK ' if not missing else 'FAIL'}] all {len(FIELDS)} keys in schema line")
    ok &= not missing

    leaks = sorted(set(re.findall(r"redo_desc_\w+", block)))
    print(f"  [{'OK ' if not leaks else 'FAIL'}] no redo_desc_* leaked (F1 guard)"
          + (f" -- {leaks}" if leaks else ""))
    ok &= not leaks

    # dead names from the previous version must be gone
    for dead in ("redo_booking_inclusions", "redo_booking_location",
                 "redo_booking_other"):
        gone = dead not in block
        print(f"  [{'OK ' if gone else 'FAIL'}] old name removed: {dead}")
        ok &= gone

    for f in FIELDS:
        if re.search(r"^  " + re.escape(f) + r"\s*$", block, re.M) is None:
            print(f"  [FAIL] column not defined in THE COLUMNS: {f}")
            ok = False

    for label, needle in CHECKS:
        hit = needle in block
        print(f"  [{'OK ' if hit else 'FAIL'}] {label}")
        ok &= hit

    if not ok:
        raise SystemExit("block failed its own checks -- refusing to write")

    raw = PROMPTS.read_text(encoding="utf-8")
    before = block_names(raw)
    print(f"\nexisting blocks in file: {len(before)}")
    if NEW_VERSION in before:
        raise SystemExit(f"{NEW_VERSION} already present -- append-only, refusing")

    new_raw = raw.rstrip("\n") + "\n\n" + block + "\n"

    m = probe(new_raw, NEW_VERSION)
    if not m:
        raise SystemExit("appended block does not re-extract")
    if m.group(1).strip() != body.strip():
        raise SystemExit("round-trip mismatch: extracted body != source body")
    print(f"  [OK ] re-extracts and round-trips ({len(m.group(1))} chars)")

    after = block_names(new_raw)
    if after[:len(before)] != before or after[-1] != NEW_VERSION:
        raise SystemExit("existing blocks disturbed -- refusing")
    survived = sum(1 for v in before if probe(new_raw, v))
    print(f"  [OK ] all {len(before)} pre-existing blocks intact "
          f"({survived} re-extract)")

    if not args.write:
        print("\nDRY RUN -- pass --write to append")
        return

    shutil.copy2(PROMPTS, BACKUP)
    PROMPTS.write_text(new_raw, encoding="utf-8")
    print(f"\nbacked up -> {BACKUP.name}")
    print(f"appended {NEW_VERSION} ({len(block)} chars)")
    check = PROMPTS.read_text(encoding="utf-8")
    if not probe(check, NEW_VERSION):
        raise SystemExit("POST-WRITE: does not extract -- restore the backup")
    print(f"verified on disk: {len(block_names(check))} blocks")


if __name__ == "__main__":
    main()
