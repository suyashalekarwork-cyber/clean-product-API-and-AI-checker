# Rezdy Heading Census

Does heading-gated extraction (V5.3/V5.4, built for Fareharbor) transfer to Rezdy? A field only fills when the supplier wrote a heading naming it, so the whole approach depends on Rezdy suppliers writing headings.

**Rezdy's raw text is HTML, not markdown.** `<h2>Where to meet</h2>`, `<p>`, `<strong>` -- where Fareharbor writes `##Departure`. Running `booking_common.heading_of()` on the raw string finds almost nothing, which would read as "Rezdy has no headings" and be wrong. This census converts HTML to the markers the detector expects first:

| Rezdy HTML | converted to | treated as |
|---|---|---|
| `<h1>`-`<h6>` | `## text` | heading |
| `<li>` | `- text` | bullet, never a heading |
| a block that is ENTIRELY `<strong>`/`<b>`, <=60 chars | `**text**` | heading |
| `<strong>` mid-sentence | plain text | emphasis, NOT a heading |
| `<p>` `<div>` `<br>` `<ul>` `<table>` | newline | block boundary |

Products read: **9,363**  ·  unreadable/error stubs skipped: 10

## Headline answer

**6,439 of 9,363 products (68.8%) have at least one heading in at least one text field.**

**4,628 (49.4%) have at least one heading that NAMES A COLUMN WE SHIP.** This is the number that decides the port, not the one above. Fareharbor proved most supplier headings are topic headings (`MEALS`, `TAXI`, `Tiaki Promise`) that will never match a column, and writing patterns for those is classification by meaning -- the thing heading-gating replaced.

### Which columns Rezdy suppliers actually name

| Column | Products | % of catalogue | Distinct suppliers |
|---|---|---|---|
| `what_included` | 2,480 | 26.5% | 503 |
| `itinerary` | 1,256 | 13.4% | 257 |
| `highlights` | 1,056 | 11.3% | 224 |
| `cancellation` | 987 | 10.5% | 251 |
| `what_to_bring` | 962 | 10.3% | 236 |
| `important_info` | 838 | 9.0% | 223 |
| `meeting_point` | 632 | 6.7% | 175 |
| `what_excluded` | 497 | 5.3% | 105 |
| `restrictions` | 444 | 4.7% | 131 |
| `duration` | 242 | 2.6% | 69 |
| `check_in` | 99 | 1.1% | 31 |
| `accessibility` | 64 | 0.7% | 21 |

### What this count is NOT

An upper bound on coverage, not a promise of extraction quality. It says the supplier wrote a heading naming the field; it does not say the text beneath it is complete or correct. It also cannot see content that has no heading at all -- for those products heading-gating leaves the text in `detail_description`, which is the CORRECT behaviour, not a miss.

## Per field

| Field | Products with text | HTML | >=1 heading | % of those with text | Total headings | Distinct wordings |
|---|---|---|---|---|---|---|
| `description` | 9,363 | 9,087 | 5,722 | 61.1% | 24,018 | 8,544 |
| `additionalInformation` | 4,041 | 3,694 | 1,697 | 42.0% | 5,288 | 1,391 |
| `terms` | 3,377 | 23 | 1,330 | 39.4% | 5,530 | 1,309 |

## Headings per product (all fields combined)

| Headings | Products | % |
|---|---|---|
| 0 | 2,924 | 31.2% |
| 1 | 1,476 | 15.8% |
| 2 | 955 | 10.2% |
| 3-4 | 1,326 | 14.2% |
| 5-8 | 1,441 | 15.4% |
| 9+ | 1,241 | 13.3% |

## Top headings by DISTINCT SUPPLIERS

Ranked by how many different suppliers use the wording, not raw frequency -- one supplier with 400 products writing "What to bring" is one vote, not 400. Same rule as `reports/booking_column_definitions.md`.

### `description`

| Heading | Suppliers | Occurrences |
|---|---|---|
| inclusions | 152 | 686 |
| what to bring | 131 | 532 |
| what s included | 114 | 363 |
| highlights | 112 | 674 |
| itinerary | 76 | 599 |
| tour highlights | 72 | 158 |
| includes | 57 | 254 |
| important information | 55 | 231 |
| what to expect | 53 | 93 |
| please note | 52 | 148 |
| cancellation policy | 41 | 135 |
| tour details | 41 | 87 |
| exclusions | 31 | 202 |
| tour inclusions | 31 | 103 |
| duration | 29 | 86 |
| day 2 | 28 | 113 |
| day 1 | 27 | 125 |
| location | 27 | 67 |
| additional information | 27 | 66 |
| not included | 25 | 128 |
| terms   conditions | 23 | 96 |
| included | 23 | 59 |
| description | 19 | 83 |
| optional extras | 19 | 72 |
| tour includes | 19 | 69 |
| day 3 | 19 | 68 |
| important notes | 17 | 53 |
| note | 17 | 46 |
| weather | 16 | 192 |
| details | 16 | 24 |

### `additionalInformation`

| Heading | Suppliers | Occurrences |
|---|---|---|
| what to bring | 73 | 235 |
| important information | 17 | 68 |
| meeting point | 16 | 31 |
| cancellation policy | 15 | 56 |
| parking | 13 | 28 |
| weather | 11 | 53 |
| directions | 8 | 14 |
| inclusions | 8 | 13 |
| additional information | 7 | 43 |
| what to wear | 7 | 34 |
| where to meet | 7 | 23 |
| what to expect | 7 | 21 |
| cancellations | 7 | 15 |
| please note | 7 | 15 |
| location | 7 | 12 |
| contact us | 6 | 35 |
| meeting location | 6 | 29 |
| arrival time | 6 | 23 |
| important | 6 | 17 |
| what s included | 6 | 11 |
| on the day | 6 | 7 |
| kind regards | 5 | 16 |
| itinerary | 5 | 14 |
| getting there | 5 | 8 |
| please bring | 5 | 5 |
| terms and conditions | 4 | 20 |
| tour inclusions | 4 | 13 |
| important notes | 4 | 9 |
| transport | 4 | 8 |
| how to get there | 4 | 6 |

### `terms`

| Heading | Suppliers | Occurrences |
|---|---|---|
| cancellation policy | 66 | 243 |
| terms and conditions | 29 | 86 |
| terms   conditions | 13 | 61 |
| what to bring | 9 | 21 |
| cancellations | 8 | 59 |
| travel insurance | 7 | 14 |
| weather | 6 | 27 |
| privacy policy | 6 | 24 |
| refund policy | 6 | 18 |
| minimum numbers | 6 | 16 |
| cancellation | 6 | 12 |
| weather policy | 6 | 10 |
| bookings | 5 | 38 |
| contact us | 5 | 37 |
| child policy | 5 | 12 |
| medical conditions | 5 | 12 |
| note | 4 | 46 |
| liability | 4 | 24 |
| cleaning fees | 4 | 15 |
| booking conditions | 4 | 13 |
| payment | 4 | 12 |
| important information | 4 | 6 |
| personal belongings | 4 | 6 |
| rescheduling | 3 | 43 |
| understanding the risks | 3 | 34 |
| cancellation and refund policy | 3 | 28 |
| age restrictions | 3 | 23 |
| weight restrictions | 3 | 21 |
| booking fees | 3 | 15 |
| conditions of entry | 3 | 14 |
