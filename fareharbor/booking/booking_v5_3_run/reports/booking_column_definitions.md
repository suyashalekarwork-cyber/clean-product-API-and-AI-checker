# Booking Notes — Column Definitions (V5.3_BOOKING)

Definitions for extracting `item.booking_notes`. Companion to
`reports/fareharbor_column_definitions.md`, which covers the description side.

**Why this document exists.** Extraction is heading-gated: the AI reads a heading
and decides which column it names. **The column list drives every decision.** If a
column is vaguely defined, headings get routed to it wrongly and the
misclassification problem returns.

**Every heading count below is measured**, not assumed — from a scan of all 8,244
Fareharbor products that have booking notes (17,212 heading occurrences, 3,729
distinct wordings). Fill rates come from the 100-product V5 run.

**Two numbers are quoted per heading and they mean different things:**

- **times** — how often the wording appears
- **suppliers** — how many *different* operators use it

48 uses by one supplier is that operator's template copied across their own
products. 42 uses by 17 suppliers is a shared concept. Only the second is
evidence for a column.

---

## The rules that apply to every column

**1. A heading licenses extraction. Nothing else does.**
No heading → the column stays `""` and the text goes to **Booking Notes**.
An empty column is a CORRECT answer. A column filled by guessing is a failure.

**2. Nothing is ever deleted.** Only greetings, sign-offs and separator rules may
be omitted, and greetings are recorded in `flags` so the omission is auditable.
Everything else appears somewhere. Anything that still slips through is caught
by the post-processing pass — see `recovered_content` below.

**3. Trust the supplier's heading, even when the content disagrees with it.**
Product `327258` has *"we supply all safety gear"* under a **What to Bring**
heading. Content-wise that is an inclusion. It stays in `what_to_bring`, and the
mismatch is recorded in `flags`. Moving it would be classification by meaning —
the thing that produced 294 of 329 misclassifications before V5.

**4. The OUTER heading wins. Sub-headings do not re-route content.**
Vagabond Cruises (31 products) writes:

```
###ADDITIONAL INFORMATION
    **Information for parking and around King Street Wharf**  - Wilson Parking
    **Plan your trip ahead of time with NSW Transport**       - Transport NSW
    **Nearest train station to Darling Harbour**              - Wynyard Station
    **Booking subject to Vagabond Cruises' terms and conditions**
```

`ADDITIONAL INFORMATION` names Booking Notes, so **all four blocks go to Booking
Notes** — including the parking and train-station links, which look like
`meeting_point` content. We do not look inside a claimed section and re-route it.
This follows rule 3.

**Every label is kept, at both levels**, joined by `: ` per rule 6:

```
ADDITIONAL INFORMATION:
Information for parking and around King Street Wharf: Wilson Parking, Secure Parking
Plan your trip ahead of time with NSW Transport: Transport NSW
Nearest train station to Darling Harbour: Wynyard Station
Booking subject to Vagabond Cruises' terms and conditions: vagabond.com.au/terms-conditions
```

Nothing is routed on meaning and nothing is left unlabelled, so the blocks can be
separated later if the design calls for it.

**5. A heading must name a COLUMN, not a fact.**
Ask: could this heading appear on *any* tour? `What to Bring` could. `Nearest
train station to Darling Harbour` could not — it names a fact about one venue.
Facts are content, not headings.

| Line | Heading? | Why |
|---|---|---|
| `What to Bring` | yes | names a column, works on any product |
| `Accessibility` | yes | names a column |
| `Plan your trip ahead of time with NSW Transport` | **no** | advice with a verb; tells you to do something |
| `Nearest train station to Darling Harbour` | **no** | a fact about this venue |
| `Booking subject to Vagabond Cruises' terms and conditions` | **no** | a statement; contains its own content |

**6. Keep the label with its content.** Never emit a value with its label
stripped. Join them with `: ` — the way suppliers already write it. `Duration:
3 Hours`, not `3 Hours`. Where the supplier already wrote the colon, do not
double it. A dropped label is content loss that a retention check cannot see.

**7. A bullet or list item is NEVER a heading.** This is the booking-specific
failure mode. Under a **What to Bring** heading, these are ITEMS:

```
Sunscreen        Towel        Water bottle        Hat
```

Measured: under a naive detector the three most common "headings" in the entire
catalogue are `sunscreen` (834), `towel` (430) and `camera` (279). Booking notes
are list-dominated — 32.2% of all lines are bullets, and 25.4% of products are
majority-bullet — so this matters far more here than on the description side.

**8. Line tests apply to `itinerary` and `what_included` ONLY.** Every other
column moves as a block. Checking every line of every column would mean judging
content by meaning, which rule 3 forbids.

**Considered and rejected for `what_to_bring`** (2026-08-11). The concern was
fair — it is a list column, and a supplier may put something unrelated in it. But
both existing tests were added to fix a *measured* defect: prose polluting timed
itinerary lists, and purchasable items under an Inclusions heading. No equivalent
problem has been observed in `what_to_bring`, and at 580 suppliers and 3,400
headings it is our largest column by a wide margin — a line test there means the
model second-guessing 3,400 blocks, and every judgement is a chance to move
something wrongly. Revisit if the hand-read of the 100-product run shows
suppliers putting unrelated content under What to Bring.

---

## The columns

### `booking_notes` — the default destination

**Holds:** all text with no heading, plus content under any heading that names no
column, plus any line rejected by a line test, plus every informative
heading-shaped line.

**Fill rate: 94%.** Holds 28.9% of all words in the 100-run.

**This being large is correct.** It is the honest home for unlabelled content —
the customer still reads it. It is also what makes the strict gate safe: because
nothing is deleted, declining to classify costs nothing.

**Replaces `redo_booking_other`.** The old name was vague, so it accumulated
junk. This one says what it is and matches the Figma sub-block that already
exists under Important Information.

Measured content in the 100-run: terms and waivers (`275941`, 625 words;
`735310`/`316333`, 620 each), payment process (`98642`, 850 words), operator
background (`516920`), and content whose column had no heading. Much of that
drains into the new columns below — **re-measure after the next run before
concluding anything about its size.**

**Figma:** Important Information → Booking Notes sub-block.

---

### `recovered_content` — built by code, never by the AI

**The AI never sees this column and is never asked to fill it.** It is written by
a post-processing pass after extraction.

**How it works.** Code compares the raw booking notes against every extracted
column. Anything present in the raw and absent from all columns is written here,
**labelled with the heading it sat under**:

```
what_to_bring: sunscreen
check_in: Please collect your boarding passes 20 minutes prior to departure
```

**Why a column and not just a log.** Recording only *that* something is missing
tells you a defect exists. Recording *where it belonged* means a human — or a
later AI pass — can put it back. Until then nothing is silently gone.

**Why this cannot be a prompt rule.** Content loss is random, not systematic:
re-running identical products on an identical prompt made 4 of 6 defects vanish.
No wording can guarantee it. This is the deterministic check CLAUDE.md already
calls for: *"Post-extraction content-loss check — return any raw sentence present
in no column. Takes the 0.6–0.7% loss rate to 0; a prompt rule cannot."*

**It should be EMPTY in a healthy run.** A non-empty value is a signal to
investigate, not normal output.

**The case it would have caught:** product `478466`, where the supplier's entire
"clothing Golden Rules" block disappeared — NO COTTON or DENIM, the layering
advice, the nylon jacket guidance — while `what_to_bring` kept the *other*
advice. The output looked complete. Retention read 82.4% and nothing pointed at
what was gone.

**Not shown to customers.**

---

### `what_to_bring` — 3,400 times, 580 suppliers, 72% fill

**Holds:** what the customer must bring or wear.

| Times | Suppliers | Heading |
|---|---|---|
| 2,097 | many | what to bring |
| 198 | | what to wear |
| 139 | | bring |
| 88 | | please bring |
| 38 | | what should you bring |
| 37 | | what to bring? |
| 36 | | what do you need to bring? |
| 31 | | what you need to bring |

Also: Packing List, Dress Code, Footwear, Clothing, Gear, Equipment,
Things to Pack, Don't Forget.

**The biggest column by a wide margin** — booking notes are mostly packing lists.

**Does not belong:** what the operator PROVIDES. But if the supplier wrote it
under a What to Bring heading, it stays here per rule 3 (`327258`) — flag it.

**Figma:** Important Information sub-block.

---

### `important_info` — 1,566 times, 297 suppliers, 68% fill

**Holds:** general notices the supplier flagged as important, which name no more
specific column. Also owns weather and operating conditions.

Headings: Important Information (166), Please Note (113), General Information
(84), Additional Information (73), Tour Information (64), Important (64),
Things to Know (57), Important Things to Note (42), Reminder (40), More
Information (41), Key Reminders (36), Other Information (34).

Weather: Rain (32), weather policy, wet weather plan, tide dependence.

**Not cancellation unless the same text states a refund.**
*"We do not operate when winds exceed 25 knots"* → here.
*"Trips cancelled for weather are refunded"* → `cancellation`.

**Watch:** on the description side this column became the catch-all, absorbing
1,016 products. See the OPEN QUESTION on `operations` below.

**Figma:** Important Information.

---

### `meeting_point` — 1,228 times, 243 suppliers, 66% fill

**Holds:** where to meet, or where the activity happens.

Headings: Location (244), Meeting Point (85), Meeting Location (53), Parking
(53), Where to Meet (46), Directions (40), Boarding Location, Getting There,
How to Get There (23), Venue, Address.

**An address alone is location. A time alone is `departure_info`.**

**Renamed from `location`** so it matches the description side's
`meeting_point` — the two must share a name or the merge cannot be mechanical.

**Figma:** Meeting Point card.

---

### `check_in` — 1,139 times, 213 suppliers, 36% fill

**Holds:** what to do on arrival, and arrival timing.

Headings: Check In (99), Check-in (67), Check In Time (32), Arrival Time,
On Arrival, On the Day (23), Registration, Sign In.

**Arrival instructions written as sentences belong here too** — `please arrive
15 minutes prior` appears 48 times as that exact wording and hundreds more
across variants. It is CONTENT (rule 6), not a droppable label, and this is the
column that answers "when must I be there?".

**Does not belong:** things to do days beforehand → `before_arrival`.

**Figma:** Important Information → Know Before You Travel.

---

### `what_included` — 959 times, 201 suppliers, 38% fill

**Holds:** what the price covers at no extra cost. **SUBJECT TO THE LINE TEST.**

| Times | Heading |
|---|---|
| 280 | inclusions |
| 134 | what's included |
| 58 | we provide |
| 51 | whats included |
| 40 | what's included *(curly apostrophe)* |
| 38 | what we provide |
| 37 | what is included? |

**LINE TEST:** each line must be free of charge. Disqualifying, even under an
Inclusions heading: *available for purchase, can be purchased, at extra cost,
additional charge, available for hire, optional*. A disqualified line goes to
`booking_notes` and MUST be recorded in `flags`.

**Renamed from `inclusions`** to match the description side's `what_included`.
This rename removes the single biggest obstacle to merging the two sources — a
`desc`→`booking` find-and-replace previously produced a field name that does not
exist and a check that quietly passed against an empty column.

**Figma:** What's Included.

---

### `departure_info` — 607 times, 139 suppliers, 20% fill

**Holds:** when and from where the activity leaves.

Headings: Departure Information (82), Schedule (24), Timetable, Boarding Time,
Your Cruise Departs From, Start (16), Pickup Times.

**Distinct from `check_in`,** which is about arriving. A list of departure TIMES
is not an itinerary.

**Figma:** Departure Time.

---

### `disclaimers` — 511 times, 86 suppliers

**Holds:** terms, waivers, liability, risk disclosure.

Headings: Terms and Conditions (36), Terms & Conditions (26), Disclaimers (24),
Disclaimer (16), Fraud Prevention (22), Risk Disclosure (16), Conditions of Use.

**Stays its own column even though it displays inside Important Information.**
Combining columns for display is trivial; un-combining them requires
re-extraction. On the description side `disclaimers` fills 22.4% — more often
than `highlights` or `itinerary`, both of which have their own page sections.

**Figma:** Important Information sub-block.

---

### `health_safety` — 492 times, 72 suppliers — **NEW COLUMN**

**Holds:** safety rules, hazards, medical and emergency information.

Headings: Safety (37), On Board Safety (31), Safe Boarding and Disembarking
(31), Responsible Service of Alcohol (31), Safety Responsibility (23), Sea
Sickness, First Aid, plus the earthquake/tsunami/landslide cluster.

**Why it is justified:** 72 different suppliers — more than `restrictions` (65),
`pricing` (60), `faqs` (54) or `cancellation` (35), all of which are unquestioned
columns. And the unified schema **already has a `detail_health_safety` field
mapped to a Figma "Health & Safety" section**, fed today from
`item.health_and_safety_policy` — a different API field. Safety text written
inside booking notes currently has nowhere to go.

**Figma:** Health & Safety.

---

### `restrictions` — 409 times, 65 suppliers, 33% fill

**Holds:** limits on WHO may take part or HOW they must behave.

Headings: Tour Requirements (76), Restrictions (32), Tour Rules (30), Special
Rules, Company Policy, Prerequisites, Suitability, Fitness, plus ALL age
headings — Ages, Age Range, Age Requirement, Minimum Age.

**Age content always comes here**, never to a numeric age column.

**Does not belong:** *"arrive 15 minutes early"* → `check_in`. *"non-refundable"*
→ `cancellation`. *"wheelchair accessible"* → `accessibility`.

**Figma:** displays under Important Information.

---

### `pricing` — 371 times, 60 suppliers

**Holds:** rates, charges, deposits, tax and payment details.

Headings: Tax Invoice (60), ABN (48+), GST Tax Invoice (28), GST# (28),
Rates (8), Deposit, Payment.

**REQUIRES A REAL FIGURE.** Marketing copy about affordability is not pricing —
it stays in `booking_notes`. A Pricing section containing no price is a defect.

**Figma:** Important Information sub-block.

---

### `faqs` — 240 times, 54 suppliers, 17% fill

**Holds:** question-and-answer content.

**FAQ PAIRING RULE:** a question and its answer move together or neither moves.
An answer stored without its question is a failure. Format `Q: … A: …`.

**A heading ending in `?` is only an FAQ if no other column claims it.** *"What
is included?"* is an inclusions heading phrased as a question. *"Will I get
wet?"* is an FAQ.

**Never fired once in any pre-V5 run** across 100 products — the FAQ pairing rule
ported from V4.6 is what changed that. Now 17%.

**Figma:** to be created.

---

### `contact` — 155 times, 51 suppliers, 30% fill

**Holds:** phone, email, website, how to reach the operator.

Headings: Office Hours (74), Email, Phone, Website, Contact.

**Figma:** Contact Information card (PHONE / EMAIL / WEBSITE / ADDRESS).

---

### `itinerary` — 149 times, 40 suppliers, 16% fill

**Holds:** a time- or step-ordered sequence. **SUBJECT TO THE LINE TEST.**

Headings: Itinerary (74), Itenerary (7 — recurring supplier misspelling).

**LINE TEST:** a line qualifies only with a clock time (`9:30 AM`), a day/step
number (`Day 1`), or a named stop in order. Ordering words alone — *then,
before, first* — are not enough. Failed lines go to `booking_notes`, recorded in
`flags`.

**A list of departure times is not an itinerary** — that is `departure_info`.

**Figma:** Cruise Route / Itinerary.

---

### `cancellation` — 140 times, 35 suppliers, 22% fill

**Holds:** REFUNDS ONLY — refund rules, cancellation windows, no-show terms,
deposit forfeits, rescheduling.

Headings: Cancellation Policy (16), Refunds and Changes, Change of Booking.

**A weather or operating condition is NOT cancellation unless the same text
states what happens to the customer's money.**

**Figma:** Cancellation Policy.

---

### `before_arrival` — 108 times, 26 suppliers, 19% fill

**Holds:** things to do BEFORE the day — sign a waiver, create an account, get a
licence, pre-book parking.

Headings: Prior to Arrival (36), Before You Arrive, Before Your Adventure,
Participation Form (24), Sign Your Waiver.

**Kept as its own column** rather than folded into `check_in`: 236 heading
occurrences, roughly double `cancellation` and nearly triple `faqs`, both of
which are unquestioned columns. `316333` — *"To finalise your booking please
sign this waiver"* — is a different customer action, with a different deadline,
from *"arrive 15 minutes early"*.

**Figma:** Important Information → Know Before You Travel.

---

### The smaller columns

| Column | Times | Suppliers | Fill | Notes |
|---|---|---|---|---|
| `accessibility` | 60 | 13 | — | Accessibility (49). Figma: Accessibility |
| `special_requirements` | 59 | 18 | — | only when the supplier used that exact heading |
| `duration_text` | 55 | 14 | — | Duration (45). NOT opening hours |
| `extras` | 45 | 24 | — | optional paid add-ons and upgrades |
| `group_size` | 33 | 7 | — | Group Size, Capacity, Minimum Numbers |
| `what_excluded` | 24 | 15 | — | explicitly not covered by the price |
| `highlights` | ~13 | 5 | — | thin, but real |
| `what_not_to_bring` | 12 | 7 | 5% | prohibited items. Weakest column — kept deliberately, see Decisions |
| `flags` | — | — | — | diagnostics + dropped greetings. Never shown to customers |

---

## Decisions taken (2026-08-11)

### `operations` — NOT a column

Sized before deciding. As **headings** — the only thing the gate can act on:

| Concept | Times | Suppliers |
|---|---|---|
| **Weather** | 313 | **76** |
| minimum numbers to run | 44 | 13 |
| service rules (RSA, BYO) | 44 | 12 |
| opening hours | 22 | 9 |
| reschedule / discretion | 7 | 3 |
| operating days / season | 5 | 2 |
| **Total** | **435** | **106** |

106 suppliers looks like it clears the bar — but **it is one concept wearing a
coat.** Weather alone is 313 of the 435 occurrences and 76 of the suppliers.
Remove weather and the remainder is 122 occurrences across ~30 suppliers spread
over five unrelated ideas, none of which individually reaches `accessibility`'s
13 suppliers except minimum-numbers, which ties it.

That is not a column — it is a label for a bag of leftovers, and a column defined
as "miscellaneous operating stuff" is exactly the vague definition this document
opens by warning against.

**And weather already has a home.** V5.3 deliberately gave weather and operating
conditions to `important_info` with a working boundary: no refund stated →
`important_info`; money stated → `cancellation`. Creating `operations` would
re-litigate a settled decision and add a *second* boundary to get right.

**So:** weather → `important_info`. Minimum numbers, opening hours, BYO and
operator discretion → `important_info`, or `restrictions` where the text is a
rule about behaviour.

**Revisit trigger:** only if Important Information becomes the largest section on
the page in practice — the same trigger the description doc already sets.

*Caveat: 296 lines were routed to `cancellation` for mentioning money and were
not individually verified, and this count carries the same ~26% heading noise as
everything else. The ranking is reliable; the absolute figures are approximate.*

### `what_not_to_bring` — KEPT

12 occurrences, 7 suppliers, 5% fill — the weakest column by a clear margin, and
12 is a ceiling given the heading noise.

**Kept anyway**, on two grounds: where a supplier writes a clear *What NOT to
Bring* heading we should extract it rather than merge on a technicality, and
Rezdy is expected to use this concept more heavily. Merging it into
`restrictions` stays available later — merging columns is easy, un-merging
requires re-extraction.

### Greetings — dropped from output, recorded in `flags`

657 occurrences of `Hello Sailor!`, `See you soon!`, `Thanks for booking!`. No
travel agent will read them, and both prompts already permit omitting them.
Recording them in `flags` gives the audit trail without page clutter.

### `what_to_bring` line test — NOT added

See rule 8.

---

## Known measurement caveat

**About 26% of what the heading detector found are not real headings.** Tested
structurally — a heading is followed by content:

| Verdict | Count | Share |
|---|---|---|
| Real heading (prose or a list follows) | 12,731 | 74.0% |
| Not a heading | 2,215 | 12.9% |
| Doubtful | 2,266 | 13.2% |

The false ones are full sentences (979), greetings (657) and `Label: value`
lines (579) such as `ABN: 36152614894`. By detection rule, ALL-CAPS is worst at
55.1% real; markdown `##` is 72.7% and is the largest rule by volume.

**So treat the per-column counts as approximate and the RANKING as sound.** This
is a limitation of keyword counting, not a prediction of extraction behaviour —
the AI reads each line in context and can tell that `##Thanks for booking!` is a
greeting, which a regex cannot.
