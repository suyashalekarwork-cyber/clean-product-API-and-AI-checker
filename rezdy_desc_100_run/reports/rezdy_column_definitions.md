# Rezdy Column Definitions

*Phase 1 of `reports/REZDY_STEP2_PLAN.md`. The source document the Rezdy extraction prompts get written FROM. No prompt is written until this is agreed.*

Built by `scripts/build_rezdy_column_definitions.py` from all **9,363** readable products in `data/Rezdy/`.

Every column below is justified by **how many DIFFERENT SUPPLIERS write a heading naming it** -- never by raw frequency. One supplier with 400 products writing "What to bring" is one vote, not 400. Rezdy has suppliers repeating 13 KB of identical text across every product they list, so frequency would hand them the schema.

Headings are counted from `rezdy_common.html_to_markdown()` -- the converter that restores structure and makes **no heading judgements**. The earlier census used a guarded converter that demoted 32.7% of heading tags, so **its numbers are a floor and these are higher**.

## Three converter bugs this phase found and fixed

Building this document required running the converter over the whole catalogue, which surfaced three faults the earlier sampling missed. All three CORRUPT text rather than lose it, so a word-count check is blind to them by construction:

| # | Fault | Example | Effect |
|---|---|---|---|
| 1 | a heading-tag guard that demoted anything ending `.!?` | `<h4>What do you need to bring?</h4>` | 484 real headings across 241 products deleted before the model saw them |
| 2 | `<b>&nbsp;</b>` (bold around a space) collapsed to nothing | `a course/experience.` + `This can be done` | words FUSED into `course/experience.This` |
| 3 | `.strip()` ate the space inside a bold label | `<b>HOW LONG: </b>2 HOURS` (PJBKTR) | became `HOW LONG:2 HOURS`, which no longer matches the prompt's `Label: value` rule |

After the fixes, the lossless gate reads **0 real losses in 2,668 field-texts** (separator rules like `-----` excepted, which the prompt is explicitly allowed to drop).

## Verification

**248 of 250 sampled mapped headings (99.2%) confirmed present in the raw supplier text.** A heading our detector invented would map to a column just as happily as a real one, so the map is only as good as this check. It is also how the `not included` ordering bug was found -- by reading raw text, not by reading the code.

Not found verbatim (worth reading before trusting their column):

| Product | Field | Heading |
|---|---|---|
| `PHNX5Q` | `terms` | 3.4. The following tours have minimum age restrictions |
| `PJGTDZ` | `terms` | 5.4. Cancellation fees for scheduled tours are as follows |

## Proposed columns

**5,398 of 9,363 products (57.7%)** have at least one heading naming one of these columns.

Ranked by distinct suppliers. **Ship / Argue / Reject** is the decision this document exists to settle.

| Column | Suppliers | Products | % of catalogue | Verdict |
|---|---|---|---|---|
| `what_included` | **574** | 2,815 | 30.1% | **SHIP** |
| `important_info` | **408** | 1,731 | 18.5% | **SHIP** |
| `meeting_point` | **276** | 981 | 10.5% | **SHIP** |
| `what_to_bring` | **272** | 1,175 | 12.5% | **SHIP** |
| `cancellation` | **271** | 1,037 | 11.1% | **SHIP** |
| `highlights` | **239** | 1,091 | 11.7% | **SHIP** |
| `itinerary` | **193** | 1,085 | 11.6% | **SHIP** |
| `restrictions` | **189** | 724 | 7.7% | **SHIP** |
| `disclaimers` | **178** | 736 | 7.9% | **SHIP** |
| `pricing` | **136** | 389 | 4.2% | **SHIP** |
| `what_excluded` | **122** | 547 | 5.8% | **SHIP** |
| `check_in` | **115** | 335 | 3.6% | **SHIP** |
| `extras` | **88** | 355 | 3.8% | **SHIP** |
| `duration_text` | **82** | 252 | 2.7% | **SHIP** |
| `health_safety` | **78** | 233 | 2.5% | **SHIP** |
| `contact` | **59** | 244 | 2.6% | **SHIP** |
| `group_size` | **47** | 120 | 1.3% | **SHIP** |
| `accessibility` | **23** | 65 | 0.7% | ARGUE |
| `faqs` | **21** | 71 | 0.8% | ARGUE |
| `special_requirements` | **3** | 4 | 0.0% | REJECT? |

Thresholds are a starting point, not a rule: **SHIP** ≥40 suppliers, **ARGUE** 15-39, **REJECT?** <15. Fareharbor has the same decision outstanding on three columns measured at 0.2-0.6% of its catalogue, and it is still unsettled -- so a low count here is a question, not an automatic no.

## Which field feeds which column

This is the merge problem in table form. A column fed by BOTH `description` and `additionalInformation` will need a precedence rule -- and that rule is inherited from Fareharbor, not invented here.

| Column | description | additionalInformation | terms | contested? |
|---|---|---|---|---|
| `what_included` | 2,748 | 119 | 35 | **YES** |
| `important_info` | 1,208 | 494 | 190 | **YES** |
| `meeting_point` | 581 | 404 | 65 | **YES** |
| `what_to_bring` | 780 | 426 | 53 | **YES** |
| `cancellation` | 301 | 154 | 674 | **YES** |
| `highlights` | 1,091 | 3 | 0 |  |
| `itinerary` | 1,051 | 21 | 26 |  |
| `restrictions` | 505 | 130 | 218 | **YES** |
| `disclaimers` | 283 | 93 | 443 | **YES** |
| `pricing` | 289 | 31 | 92 |  |
| `what_excluded` | 519 | 20 | 14 |  |
| `check_in` | 118 | 160 | 70 | **YES** |
| `extras` | 298 | 62 | 2 | **YES** |
| `duration_text` | 208 | 45 | 3 |  |
| `health_safety` | 89 | 46 | 105 |  |
| `contact` | 83 | 110 | 51 | **YES** |
| `group_size` | 83 | 14 | 52 |  |
| `accessibility` | 44 | 11 | 11 |  |
| `faqs` | 55 | 16 | 0 |  |
| `special_requirements` | 2 | 2 | 0 |  |

## Evidence per column

The actual supplier wordings, so a reviewer can judge whether the stem list is honest. `sup` = distinct suppliers using that wording.

### `what_included`  ·  574 suppliers  ·  2,815 products

| Heading wording | sup | uses |
|---|---|---|
| inclusions | 156 | 707 |
| what s included | 139 | 502 |
| includes | 58 | 250 |
| tour inclusions | 33 | 115 |
| included | 27 | 73 |
| tour includes | 19 | 72 |
| price includes | 13 | 99 |
| whats included | 11 | 31 |
| what is included | 11 | 27 |
| your experience includes | 11 | 22 |
| package includes | 10 | 27 |
| we provide | 9 | 21 |

### `important_info`  ·  408 suppliers  ·  1,731 products

| Heading wording | sup | uses |
|---|---|---|
| important information | 70 | 308 |
| please note | 60 | 163 |
| additional information | 34 | 110 |
| weather | 30 | 283 |
| important notes | 22 | 64 |
| notes | 19 | 91 |
| note | 19 | 89 |
| important | 18 | 29 |
| good to know | 13 | 40 |
| important note | 10 | 23 |
| important info | 9 | 32 |
| weather policy | 9 | 15 |

### `meeting_point`  ·  276 suppliers  ·  981 products

| Heading wording | sup | uses |
|---|---|---|
| location | 33 | 79 |
| meeting point | 28 | 57 |
| where to meet | 13 | 33 |
| pick up | 9 | 33 |
| departure point | 8 | 25 |
| meeting location | 7 | 29 |
| departure location | 7 | 26 |
| pick up location | 6 | 34 |
| locations | 6 | 10 |
| pick up drop off | 5 | 16 |
| meeting place | 4 | 11 |
| location and contact details | 4 | 6 |

### `what_to_bring`  ·  272 suppliers  ·  1,175 products

| Heading wording | sup | uses |
|---|---|---|
| what to bring | 200 | 868 |
| what to wear | 18 | 54 |
| dress code | 12 | 84 |
| please bring | 10 | 30 |
| what you need to bring | 7 | 13 |
| what to bring wear | 6 | 33 |
| what you need to know | 6 | 22 |
| what should i bring | 5 | 22 |
| what to wear bring | 4 | 18 |
| what to wear bring with you | 4 | 6 |
| what to bring with you | 2 | 7 |
| what to bring not to bring | 2 | 2 |

### `cancellation`  ·  271 suppliers  ·  1,037 products

| Heading wording | sup | uses |
|---|---|---|
| cancellation policy | 108 | 434 |
| cancellations | 22 | 97 |
| refund policy | 12 | 27 |
| cancellation | 11 | 29 |
| no shows | 5 | 15 |
| cancellations refunds | 5 | 8 |
| refunds | 4 | 46 |
| cancellation and refund policy | 4 | 30 |
| rescheduling | 3 | 43 |
| cancellations by guests | 3 | 11 |
| guest cancellations | 3 | 8 |
| non refundable tickets | 3 | 4 |

### `highlights`  ·  239 suppliers  ·  1,091 products

| Heading wording | sup | uses |
|---|---|---|
| highlights | 116 | 696 |
| tour highlights | 74 | 162 |
| highlights include | 9 | 34 |
| experience highlights | 6 | 12 |
| day 1 highlights | 5 | 21 |
| day 2 highlights | 5 | 21 |
| cruise highlights | 4 | 24 |
| event highlights | 4 | 4 |
| tour highlights include | 3 | 3 |
| day 3 highlights | 2 | 14 |
| highlights of your journey | 2 | 9 |
| itinerary highlights | 2 | 5 |

### `itinerary`  ·  193 suppliers  ·  1,085 products

| Heading wording | sup | uses |
|---|---|---|
| itinerary | 80 | 622 |
| day 2 | 32 | 120 |
| day 1 | 30 | 129 |
| day 3 | 21 | 71 |
| day 4 | 13 | 49 |
| tour itinerary | 11 | 39 |
| day 5 | 9 | 33 |
| suggested itinerary | 5 | 13 |
| your itinerary | 5 | 8 |
| full itinerary | 3 | 11 |
| itinerary features | 3 | 5 |
| itinerary overview | 3 | 4 |

### `restrictions`  ·  189 suppliers  ·  724 products

| Heading wording | sup | uses |
|---|---|---|
| child policy | 12 | 138 |
| restrictions | 10 | 26 |
| medical conditions | 9 | 19 |
| prerequisites | 8 | 19 |
| who can participate | 8 | 11 |
| supervision requirements | 8 | 10 |
| requirements | 7 | 61 |
| dietary requirements | 7 | 49 |
| age requirements | 6 | 20 |
| age restrictions | 5 | 54 |
| fitness requirements | 5 | 12 |
| participant requirements | 5 | 11 |

### `disclaimers`  ·  178 suppliers  ·  736 products

| Heading wording | sup | uses |
|---|---|---|
| terms and conditions | 40 | 174 |
| terms conditions | 35 | 165 |
| liability | 5 | 59 |
| understanding the risks | 4 | 39 |
| general terms and conditions | 4 | 11 |
| disclaimer | 4 | 8 |
| booking terms conditions | 4 | 6 |
| risk disclosure | 3 | 10 |
| waiver | 3 | 8 |
| booking terms and conditions | 3 | 7 |
| participant waiver required | 2 | 6 |
| risks | 2 | 5 |

### `pricing`  ·  136 suppliers  ·  389 products

| Heading wording | sup | uses |
|---|---|---|
| pricing | 17 | 48 |
| price | 12 | 21 |
| prices | 8 | 15 |
| rates | 7 | 17 |
| cleaning fees | 4 | 17 |
| booking fees | 3 | 15 |
| entry fees | 3 | 12 |
| package prices are not available 20th dec 31st jan | 2 | 13 |
| deposit | 2 | 7 |
| payment deposit | 2 | 6 |
| additional fees | 2 | 5 |
| prices increase yearly | 2 | 5 |

### `what_excluded`  ·  122 suppliers  ·  547 products

| Heading wording | sup | uses |
|---|---|---|
| exclusions | 34 | 210 |
| not included | 29 | 126 |
| what s not included | 16 | 42 |
| excludes | 9 | 43 |
| what s excluded | 3 | 16 |
| excluded | 3 | 12 |
| tour exclusions | 3 | 7 |
| price does not include | 2 | 7 |
| exclusion | 2 | 6 |
| inclusions and exclusions | 2 | 3 |
| inclusions exclusions pickup cost payment information | 1 | 8 |
| inclusions exclusions | 1 | 8 |

### `check_in`  ·  115 suppliers  ·  335 products

| Heading wording | sup | uses |
|---|---|---|
| getting there | 10 | 22 |
| directions | 9 | 16 |
| on the day | 8 | 34 |
| arrival time | 7 | 39 |
| how to get there | 6 | 14 |
| check in | 4 | 11 |
| what to expect on the day of your jump | 4 | 6 |
| check in details | 2 | 6 |
| bad weather on the day | 1 | 22 |
| directions and parking | 1 | 14 |
| ferry check in | 1 | 9 |
| on the day of your ride | 1 | 8 |

### `extras`  ·  88 suppliers  ·  355 products

| Heading wording | sup | uses |
|---|---|---|
| optional extras | 20 | 77 |
| extras | 9 | 67 |
| optional add on | 7 | 11 |
| optional add ons | 6 | 15 |
| optional extra | 4 | 5 |
| additional extras | 3 | 4 |
| single room upgrade | 2 | 34 |
| upgraded extras | 2 | 14 |
| optional upgrades | 2 | 5 |
| add ons | 2 | 3 |
| add on option | 2 | 2 |
| optional extras available see next page | 1 | 22 |

### `duration_text`  ·  82 suppliers  ·  252 products

| Heading wording | sup | uses |
|---|---|---|
| duration | 30 | 86 |
| tour duration | 6 | 71 |
| how long 2 hours | 5 | 11 |
| how long 3 hours | 3 | 3 |
| how long is the tour | 2 | 8 |
| distance and duration | 1 | 5 |
| duration 9 hours | 1 | 4 |
| course duration | 1 | 3 |
| time and duration | 1 | 3 |
| how long 4 hours | 1 | 3 |
| how long minimum 2 hour rental | 1 | 3 |
| duration 1 hour | 1 | 2 |

### `health_safety`  ·  78 suppliers  ·  233 products

| Heading wording | sup | uses |
|---|---|---|
| health safety | 5 | 13 |
| safety | 4 | 17 |
| safety first | 3 | 10 |
| health and safety | 3 | 4 |
| we care about your safety | 2 | 14 |
| safety message | 2 | 2 |
| safety briefing | 1 | 22 |
| southbound escapes accepts no responsibility for food and food safety as this is the sole responsibility of the licensed caterer who prepares and delivers to our picnic setting | 1 | 12 |
| 1 alcohol safety behaviour | 1 | 10 |
| safety supervision | 1 | 9 |
| covid health hygiene policy | 1 | 9 |
| safety and behaviour | 1 | 8 |

### `contact`  ·  59 suppliers  ·  244 products

| Heading wording | sup | uses |
|---|---|---|
| contact us | 13 | 82 |
| contact details | 4 | 28 |
| contact | 3 | 5 |
| this is not an instant booking once you place your order you will receive an email with your order id and contact details for the golf club you will need to call or email them to confirm your booking | 1 | 13 |
| our contact details are as follows | 1 | 12 |
| need to contact us | 1 | 11 |
| business hours contact us | 1 | 9 |
| contact information | 1 | 6 |
| need to contact us urgently | 1 | 5 |
| contact libbie geason 61 419 548 096 | 1 | 5 |
| team bonding and corporate days also available we put together multi adventure day or days including activities such as biking hiking camping kayaking and much more please contact us to discuss your dream team experience | 1 | 4 |
| how to contact us | 1 | 4 |

### `group_size`  ·  47 suppliers  ·  120 products

| Heading wording | sup | uses |
|---|---|---|
| minimum numbers | 14 | 35 |
| group size | 7 | 16 |
| minimum number of groups | 1 | 46 |
| minimum number | 1 | 6 |
| minimum number of guests | 1 | 5 |
| carriage capacity | 1 | 3 |
| no minimum numbers | 1 | 3 |
| minimum number of participants | 1 | 3 |
| shared charters require minimum numbers to operate | 1 | 2 |
| travel voucher water bottle capacity 1 5 litres strong non slip walking shoes hat wide brimmed is best flynet sunglasses sunscreen camera casual and comfortable clothing cool light clothing is best in summer and warm clothing for winter swim wear amp towel during summer | 1 | 2 |
| support our temporary venue capacity limits | 1 | 2 |
| vessel capacity strict | 1 | 2 |

### `accessibility`  ·  23 suppliers  ·  65 products

| Heading wording | sup | uses |
|---|---|---|
| accessibility | 7 | 26 |
| accessibility information | 2 | 4 |
| nb there is no wheelchair access for this cruise | 1 | 4 |
| not wheelchair accessible | 1 | 4 |
| wheelchair and pram accessibility | 1 | 4 |
| electric wheelchair | 1 | 4 |
| wheelchairs and special assistance | 1 | 2 |
| accessibility walk details | 1 | 2 |
| this is an internal cabin with no windows suitable for a solo traveller or somebody with limited mobility for stairs | 1 | 2 |
| cabin 24 main deck king single bunk internal king single bunk with 2 king single beds ladder for top bunk featuring a private ensuite is fully air conditioned and cupboard this is an internal cabin with no windows suitable for a solo traveller or somebody with limited mobility for stairs | 1 | 2 |
| not suitable if you have limited mobility or injuries | 1 | 1 |
| nb please let us know if wheelchair access is required | 1 | 1 |

### `faqs`  ·  21 suppliers  ·  71 products

| Heading wording | sup | uses |
|---|---|---|
| frequently asked questions | 9 | 21 |
| faq s | 3 | 8 |
| faqs | 2 | 7 |
| faq | 2 | 5 |
| some faq s | 2 | 4 |
| frequently asked questions faqs | 2 | 3 |
| please take a moment to review the information below and make yourself familiar with our faqs | 1 | 9 |
| got questions visit our faqs page we re here to help | 1 | 4 |
| faqs and terms and conditions | 1 | 3 |
| common questions | 1 | 2 |
| small group experience max 15 guests fully guided by local experts travel in a luxury mercedes benz vehicle water and snacks provided hotel drop off in te anau at cheeky kiwi travel we believe that travel should inspire surprise and connect you with the heart of a place that s why our tours are thoughtfully designed with passionate guides secret stops and a commitment to personal unforgettable experiences got questions visit our faqs page we re here to help | 1 | 1 |
| visit our faqs page we re here to help | 1 | 1 |

### `special_requirements`  ·  3 suppliers  ·  4 products

| Heading wording | sup | uses |
|---|---|---|
| dietary needs | 1 | 2 |
| all dietary | 1 | 1 |
| dietary considerations | 1 | 1 |

## Corrections to the census stem list

The census answered a yes/no question with a stem list written in an afternoon. It contradicts the shipped Fareharbor V5.3 prompt in three places. **The prompt wins** -- it was validated on thousands of hand-checked products. Each correction moved counts, so it is recorded rather than silently applied.

| Census had | Corrected to | Why |
|---|---|---|
| `what to expect` -> itinerary | -> about | V5.3 lists 'What to Expect' under NARRATIVE HEADINGS, which name no column and route to the default field. |
| `schedule` -> itinerary | -> not mapped | V5.3: "A 'Schedule' heading is NOT an itinerary: it means departure times." It is listed under VENUE HOURS, which are explicitly not duration either. |
| `getting there` / `directions` -> meeting_point | -> check_in | V5.3 gives check_in the headings 'Getting There', 'On the Day' and 'Before You Arrive'. meeting_point is the PLACE, check_in is the instructions for arriving. |

Consequence: the census's `itinerary` figure (13.4%) was inflated by `what to expect` and `schedule`, neither of which is an itinerary under V5.3. The number in this document is the corrected one.

## Headings we deliberately do NOT map

These are the most-used headings that match no column. **This is not a TODO list.** They name topics, not fields. Writing patterns for them is classification by meaning -- the exact thing heading-gating replaced -- and on Fareharbor it does not converge: fixing four wordings removed only 14 of 290 flags. Their content correctly stays in the default field.

| Heading | Suppliers | Uses |
|---|---|---|
| what to expect | 58 | 115 |
| tour details | 42 | 92 |
| description | 19 | 83 |
| accommodation | 16 | 55 |
| features | 15 | 65 |
| overview | 15 | 40 |
| or | 15 | 37 |
| parking | 14 | 29 |
| details | 14 | 23 |
| lunch | 13 | 31 |
| about | 12 | 70 |
| travel insurance | 12 | 43 |
| perfect for | 12 | 19 |
| tour description | 11 | 37 |
| availability | 11 | 22 |
| meals | 10 | 82 |
| bookings | 10 | 48 |
| booking information | 10 | 33 |
| transport | 10 | 30 |
| tour information | 10 | 21 |
| the experience | 10 | 16 |
| know before you go | 9 | 28 |
| optional | 9 | 25 |
| departure times | 9 | 23 |
| payment | 9 | 21 |
| why choose this tour | 9 | 19 |
| schedule | 9 | 16 |
| other information | 9 | 15 |
| morning | 9 | 12 |
| conditions | 8 | 18 |
| tour overview | 8 | 17 |
| departure | 8 | 12 |
| afternoon | 8 | 10 |
| how it works | 7 | 34 |
| privacy policy | 7 | 31 |
| what you will learn | 7 | 22 |
| what | 7 | 19 |
| booking conditions | 7 | 18 |
| day 6 | 7 | 18 |
| cruise times | 7 | 16 |

(9,612 distinct unmapped wordings in total. The long tail is the point: no list can be completed.)

## Open decisions for review

1. **Which `ARGUE` columns ship?** Each is real but thin. Fareharbor has the identical question open on `group_size` (0.2%), `what_not_to_bring` (0.3%) and `accessibility` (0.6%) -- settling both together would be cheaper than settling them twice.
2. **Do `Day 1` / `Day 2` headings name `itinerary`?** They are how multi-day tours structure a route, and V5.3's itinerary LINE TEST already accepts day numbering as a valid structural signal. Mapped as itinerary here; flagged because it is a judgement, not an obvious match.
3. **Does `terms and conditions` name `disclaimers`?** Mapped here. But in the `terms` FIELD it is just the field's own name repeated, which is a different thing from a T&C heading appearing inside a description.
4. **`Additional Information` means different things in the two Fareharbor prompts, and Rezdy needs one answer.** DESC V5.3 lists 'Additional Info / Additional Information' under `important_info`. BOOKING V5.4 says the opposite in STEP 1E: "'Additional Information' names redo_booking_notes, so everything beneath it goes there." It is the 3rd-commonest `important_info` wording here (34 suppliers), so the choice is worth money. Mapped to `important_info` in this document, following the DESCRIPTION prompt, because Rezdy's biggest field is a description. Flagged because it contradicts the booking prompt.
5. **The contested columns above** need a precedence rule before any merge. Inherited from Fareharbor -- see `reports/FAREHARBOR_UNIFIED_STRUCTURE_CONTEXT.md`, still open.
