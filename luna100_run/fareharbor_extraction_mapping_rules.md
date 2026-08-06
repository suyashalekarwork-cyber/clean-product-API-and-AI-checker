# Fareharbor Description Extraction — Mapping Rules

How we turn a Fareharbor product description into the fields shown on the
product page. Last updated 2026-08-06.

## The problem this solves

Product descriptions are one block of text. To display them as sections —
"What's Included", "Cancellation Policy" — something must decide which sentence
belongs where. We use AI for that, and when the supplier gave no heading, the AI
was guessing.

We measured the guessing. Of 329 extraction failures, **294 (89.4%) were real
text filed in the wrong section**, not text lost. The AI rarely drops content —
it misfiles it. A wrong section is worse than an empty one, because the travel
agent portal presents it as fact.

## The rule

**Extract a section only when the supplier gave it a heading.**

No heading → the field stays empty and the text remains in "About the
Experience". An empty field is a correct answer.

| Description text | Heading? | Result |
|---|---|---|
| `Rates` / Adult $35 | yes | → Pricing |
| Adult $35 | no | stays in About |
| `Duration` / 2 Hours | yes | → Duration |
| The tour runs about 2 hours | no | stays in About |

Nothing is ever deleted. Text without a heading is still shown to the customer —
it sits in the About section rather than its own block.

## Scope

This covers the **description** field only. Fareharbor also sends 25 separate
named fields (`duration`, `meeting_point`, …) and a booking-notes field. Both are
separate work: we do not yet know how reliably suppliers fill the named fields,
and judging two unknowns at once would tell us nothing about either.

## Heading → section mapping

### Sections on the product page

| Heading written in the description | Goes to |
|---|---|
| *(no heading)*, About | About the Experience |
| Highlights, Tour Highlights | Tour Highlights |
| Includes, Inclusions, What's Included, Tour Includes, Journey Inclusions | What's Included |
| Itinerary, Tour Itinerary, Day by Day, The Route | Cruise Route / Itinerary |
| Cancellation Policy, Cancellations, Refund Policy, Weather Policy | Cancellation Policy |
| Accessibility, Accessibility Information, Mobility Access | Accessibility |
| Meeting Point, Boarding Location, Location | Meeting Point |
| Duration, Tour Length, How Long | Duration |

### Captured, page placement still to be decided

Real supplier content with no section in the current design. We capture it now so
the web team can place it later without re-processing 11,236 products.

| Heading written in the description | Goes to | How often filled |
|---|---|---|
| Check-in, Arrival, Know Before You Travel, Boarding | Check-in | 27.7% |
| What to Bring, What to Wear, Dress Code, Packing List | What to Bring | 28.8% |
| Not Included, Exclusions, At Your Own Expense | What's Not Included | 20.6% |
| Disclaimer, Disclaimers | Disclaimers | 22.4% |
| Requirements, Restrictions, Who Can Participate | Requirements | 18.9% |
| Special Requirements | Special Requirements | 16.6% |
| FAQ, FAQs, Q&A | FAQs | 13.7% |
| Rates, Pricing, Prices | Pricing | 10.1% |
| Extras, Optional Add-Ons | Optional Extras | 9.9% |
| Ages, Age Range | Min Age / Max Age | 23.9% / 9.5% |

Worth noting: **What to Bring (28.8%) and Disclaimers (22.4%) appear more often
than Highlights (25.6%) or Itinerary (19.6%)**, both of which already have their
own section. On frequency alone they have an equal claim to one.

## Decisions worth explaining

**Anything not on the list stays in About.** Catch-all headings — "Important
Information", "Please Note", "More Info", "What to Expect", "Tour Summary" —
have no dedicated section and their content varies too much to route safely.

**"Schedule" is not an itinerary.** Suppliers use it for departure times
("11:00am, 2:30pm Daily"), which is *when the tour runs*, not *what happens
during it*. It stays in About.

**Extracting moves text, it does not copy it.** When a paragraph is pulled into
"What's Included", it is removed from About — otherwise the same paragraph
renders twice on one page. We verify this automatically; it must be zero.

**Questions and answers stay together.** If an FAQ answer is extracted, its
question goes with it. Otherwise the page shows an answer with no question above
it.

**We do not extract facts without a heading, even obvious ones.** A description
saying "1.5 hours" with no Duration heading is left alone. We tested relaxing
this: of 10 such cases, 8 were false positives — "be ready 10 minutes before
departure", "Lunch Break (45 minutes)". Filling the Duration field from those
would tell a customer the tour lasts 10 minutes. The strict rule already captures
91% of durations correctly.

## What to expect

**Fewer fields will be filled than before, and that is the intended outcome.**
Many currently-filled fields contain the wrong text. We are trading confident
wrong answers for honest blanks.

An empty Itinerary is correct when the supplier never supplied one. Not every
tour has an itinerary, and inventing one is worse than showing nothing.

**About the Experience fills for 98.4% of products. Every other section is a
minority fill** — Itinerary 19.6%, Cancellation 17.2%, Accessibility 12.8%. The
page must look right with most sections absent.

## How we check it

We stop counting *how many* fields were filled and measure whether they are
*right*:

- Text extracted with no heading to justify it — should be near zero
- A heading present but the field left empty — should be near zero
- The same sentence in two fields — must be zero
- Nothing lost, nothing reworded from the supplier's original text

First run: 30 of the hardest products, reviewed by hand before anything scales.
