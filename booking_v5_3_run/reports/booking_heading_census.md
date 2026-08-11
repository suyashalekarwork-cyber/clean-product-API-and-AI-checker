# Booking notes — heading census

Every distinct heading suppliers wrote in `item.booking_notes`, with counts.
Produced with the CORRECTED heading detector — the earlier figures (1,732 distinct, 41.9% of products) came from a detector that was blind to
`##Heading` with no space, bare ALL-CAPS, and Title Case sections. Treat
those older numbers as superseded.

## Coverage

- products with booking notes: **8,244**
- products with at least one heading: **5,916** (71.8%)
- total heading occurrences: **17,212**
- distinct heading strings: **3,729**
- mean headings per product: 2.1

| top N headings | share of all occurrences |
|---|---|
| 25 | 26.5% |
| 50 | 32.6% |
| 100 | 40.8% |
| 250 | 53.8% |
| 500 | 65.3% |
| 1000 | 78.1% |

- occurrences that already map to a column: **8,972** (52.1%)
- occurrences with no column: **8,240** (47.9%)

## The three open column decisions

Counted across every heading, so the decision is made on volume.

### `before_arrival` — 348 occurrences across 89 distinct headings

| count | heading | example product |
|---|---|---|
| 36 | `prior to arrival` | 391580 |
| 22 | `the waiver is to make sure you` | 310276 |
| 20 | `please ensure all waivers above are completed.` | 618266 |
| 18 | `please print and sign [go surf standard participant waiver.pdf](https:` | 103597 |
| 14 | `please check in 30 minutes prior to your flight departure time at our ` | 479369 |
| 13 | `please arrive 20 minutes prior to your booking to allow you enough tim` | 255058 |
| 9 | `please complete the waiver form prior to your tour using the link belo` | 571706 |
| 9 | `[to finalise your booking please sign this waiver](https://docs.google` | 316021 |
| 8 | `before you arrive` | 722773 |
| 8 | `before your adventure` | 272823 |
| 8 | `must sign online waiver` | 190239 |
| 8 | `please arrive 20 mins prior to your departure time for a safety brief ` | 345549 |
| 7 | `please check in 30 minutes prior to your flight departure time` | 478991 |
| 7 | `waivers##` | 250776 |
| 6 | `waiver` | 448439 |

### `operator_info` — 62 occurrences across 16 distinct headings

| count | heading | example product |
|---|---|---|
| 27 | `the crew` | 461982 |
| 13 | `your vessel` | 268127 |
| 4 | `the team at gravity nelson` | 137618 |
| 3 | `available for purchase on board our vessel.` | 130639 |
| 3 | `please email us with the copy of your boat licence` | 502537 |
| 2 | `operator cancellations` | 653639 |
| 1 | `go straight to the water park & show our team this email to redeem.` | 188147 |
| 1 | `go straight to the laser tag arena & show our team this email to redee` | 189380 |
| 1 | `💬 what people say about us` | 661255 |
| 1 | `you must book your boat trip by following instructions below` | 223122 |
| 1 | `how to book your boat tour` | 223122 |
| 1 | `!!your boat tour is not booked until you do this!!.` | 223122 |
| 1 | `the team at larnach castle` | 741266 |
| 1 | `please meet the crew at the explore kiosk, viaduct harbour, cbd, auckl` | 501367 |
| 1 | `our vessels are cleaned regularly` | 321828 |

### `payment` — 324 occurrences across 54 distinct headings

| count | heading | example product |
|---|---|---|
| 60 | `tax invoice` | 640891 |
| 48 | `abn: 36 611 842 947` | 210549 |
| 28 | `gst tax invoice` | 525411 |
| 28 | `gst# 88-952-413` | 525411 |
| 20 | `abn: 42 666 747 011` | 635388 |
| 12 | `inflite - gst: 109-091-502` | 189679 |
| 8 | `notice: we may ask that you present the credit card used for payment o` | 266983 |
| 8 | `gst 011 005 578` | 191580 |
| 7 | `abn: 28 006 114 996` | 176474 |
| 6 | `balance of payment` | 393731 |
| 6 | `abn 98 617 389 198` | 163044 |
| 5 | `payment` | 427368 |
| 5 | `booking confirmation/ tax invoice` | 510981 |
| 5 | `bond payment` | 271584 |
| 5 | `payment & cancellation for multi day tours` | 733525 |

## Headings by column (already mapped)

### `redo_booking_what_to_bring` — 3,285 occurrences, 169 distinct

| count | heading |
|---|---|
| 2097 | `what to bring` |
| 198 | `what to wear` |
| 139 | `bring` |
| 88 | `please bring` |
| 42 | `[please print, complete and bring this medical information form](https` |
| 38 | `what should you bring` |
| 37 | `what to bring?` |
| 36 | `what do you need to bring?` |
| 31 | `what you need to bring` |
| 27 | `dress code` |
| 26 | `what to bring##` |
| 24 | `what you should bring` |
| 19 | `things to bring` |
| 17 | `what should i bring with me?` |
| 16 | `please ensure that you bring along the following items` |
| 16 | `what to wear/bring` |
| 15 | `don't forget to bring your camera and sunscreen!` |
| 14 | `you will not be able to bring` |
| 14 | `what to wear & bring` |
| 11 | `please remember the following items` |
| … | _149 more distinct headings_ |

### `redo_booking_important_info` — 1,539 occurrences, 220 distinct

| count | heading |
|---|---|
| 166 | `important information` |
| 113 | `please note` |
| 84 | `general information` |
| 73 | `additional information` |
| 64 | `important` |
| 64 | `tour information` |
| 57 | `things to know` |
| 50 | `here are a few things to note (for all classes and events)` |
| 49 | `accessibility` |
| 42 | `important things to note` |
| 41 | `more information` |
| 36 | `key reminders` |
| 34 | `other information` |
| 28 | `important notes` |
| 22 | `note` |
| 22 | `general` |
| 20 | `important note` |
| 20 | `weather updates & travel information` |
| 19 | `weather` |
| 13 | `notes` |
| … | _200 more distinct headings_ |

### `redo_booking_location` — 1,099 occurrences, 181 distinct

| count | heading |
|---|---|
| 244 | `location` |
| 85 | `meeting point` |
| 53 | `meeting location` |
| 53 | `parking` |
| 46 | `where to meet` |
| 40 | `directions` |
| 30 | `information for parking and around king street wharf` |
| 21 | `getting there` |
| 20 | `sailing address` |
| 18 | `how to find us` |
| 17 | `location##` |
| 15 | `address` |
| 14 | `[click here for directions!](https://goo.gl/maps/uspqjmnm6xm)` |
| 11 | `central meeting location` |
| 10 | `🚗 parking` |
| 10 | `arriving to the venue` |
| 9 | `please also see the map below for directions` |
| 9 | `check in location is the fantasea cruising darling harbour office at p` |
| 9 | `we will reach out to once again confirm your tour & pickup location wi` |
| 9 | `location and parking` |
| … | _161 more distinct headings_ |

### `redo_booking_inclusions` — 930 occurrences, 96 distinct

| count | heading |
|---|---|
| 280 | `inclusions` |
| 134 | `what's included` |
| 58 | `we provide` |
| 51 | `whats included` |
| 40 | `what’s included` |
| 38 | `what we provide` |
| 37 | `what is included?` |
| 26 | `what's included?` |
| 20 | `what is provided` |
| 17 | `what is included` |
| 15 | `inclusions##` |
| 14 | `we provide helmets, locks and chains!` |
| 9 | `included` |
| 9 | `includes` |
| 9 | `included in this package` |
| 8 | `💰 what’s included` |
| 8 | `we supply` |
| 7 | `tour inclusions` |
| 6 | `boat charter includes` |
| 6 | `included in your package is the following` |
| … | _76 more distinct headings_ |

### `redo_booking_departure_info` — 494 occurrences, 144 distinct

| count | heading |
|---|---|
| 82 | `departure information` |
| 26 | `please arrive 30 minutes prior to departure!` |
| 22 | `departure times` |
| 18 | `your cruise departs from` |
| 14 | `please check in 30 minutes prior to your flight departure time at our ` |
| 11 | `departures` |
| 11 | `departure & return -` |
| 10 | `pick up time and location` |
| 10 | `please check in 20 mins before your departure time.` |
| 9 | `departure point` |
| 9 | `departure location` |
| 8 | `before departure` |
| 8 | `departure` |
| 8 | `please arrive 10-15 minutes prior to scheduled departure time.` |
| 8 | `please arrive 20 mins prior to your departure time for a safety brief ` |
| 7 | `please check in 30 minutes prior to your flight departure time` |
| 7 | `please arrive 15 mins before your departure time` |
| 6 | `please arrive at a minimum 15 minutes before your departure time.` |
| 6 | `just a little departure information for you to follow..` |
| 6 | `boarding time: 30 minutes prior to schedule cruise time!!` |
| … | _124 more distinct headings_ |

### `redo_booking_check_in` — 492 occurrences, 78 distinct

| count | heading |
|---|---|
| 99 | `check in` |
| 67 | `check-in` |
| 32 | `check in time` |
| 30 | `arrival time` |
| 21 | `check in information` |
| 20 | `check-in time: 2pm` |
| 18 | `arrival` |
| 13 | `check-in details` |
| 10 | `check-in & boarding` |
| 9 | `the driver/captain of the boat must be physically checking in at our o` |
| 9 | `late arrival may result in you missing out on part or all of the exper` |
| 8 | `✅ssi registration & myssi app` |
| 8 | `arrival time##` |
| 8 | `if joining this tour from our visitor centre, please check-in 15 minut` |
| 7 | `2) arrival time` |
| 6 | `new registrations (first-time participants)` |
| 6 | `arrival & accommodation` |
| 6 | `upon arrival we will brief you on the following` |
| 6 | `check-in arrival time` |
| 5 | `check-in & arrival` |
| … | _58 more distinct headings_ |

### `redo_booking_restrictions` — 437 occurrences, 79 distinct

| count | heading |
|---|---|
| 76 | `tour requirements` |
| 30 | `our most important (but not our only) tour rules` |
| 25 | `requirements` |
| 25 | `suitability` |
| 22 | `rules & conditions of entry` |
| 21 | `dietary requirements` |
| 20 | `special requirements` |
| 17 | `reminder of our tour rules/ company policy` |
| 16 | `rules` |
| 14 | `precis of queensland cycling rules and safety` |
| 12 | `food & beverages` |
| 11 | `reminder of our tour rules / company policy` |
| 8 | `disability access & suitability` |
| 8 | `house rules – safety first 🪓##` |
| 7 | `footwear requirement` |
| 6 | `customer requirements` |
| 5 | `reminder of our tour rules & company policy` |
| 4 | `if you have any concerns about your fitness to fly, or any other quest` |
| 4 | `waiver requirement` |
| 4 | `code of conduct for the participants` |
| … | _59 more distinct headings_ |

### `redo_booking_before_arrival` — 236 occurrences, 44 distinct

| count | heading |
|---|---|
| 36 | `prior to arrival` |
| 22 | `the waiver is to make sure you` |
| 20 | `please ensure all waivers above are completed.` |
| 18 | `please print and sign [go surf standard participant waiver.pdf](https:` |
| 9 | `please complete the waiver form prior to your tour using the link belo` |
| 9 | `[to finalise your booking please sign this waiver](https://docs.google` |
| 8 | `before you arrive` |
| 8 | `before your adventure` |
| 8 | `must sign online waiver` |
| 7 | `waivers##` |
| 6 | `waiver` |
| 6 | `important pre-arrival information` |
| 5 | `please fill out your waiver here` |
| 5 | `online waiver` |
| 5 | `copy of terms and liability waiver` |
| 5 | `please make sure you have completed the online waiver form at least 72` |
| 4 | `parents must sign online waiver` |
| 4 | `sign your waiver` |
| 4 | `medical travel and waiver forms` |
| 4 | `please sign waiver attached to this email before your first lesson` |
| … | _24 more distinct headings_ |

### `redo_booking_itinerary` — 125 occurrences, 12 distinct

| count | heading |
|---|---|
| 74 | `itinerary` |
| 15 | `itinerary##` |
| 8 | `tour itinerary` |
| 8 | `your itinerary` |
| 8 | `itenerary` |
| 5 | `fare & itinerary` |
| 2 | `please read woebegone freedive's itinerary below` |
| 1 | `your island itinerary` |
| 1 | `here is the itinerary for day 1` |
| 1 | `📅 your festival itinerary` |
| 1 | `itinerary/your input` |
| 1 | `logistics and itinerary notes` |

### `redo_booking_contact` — 120 occurrences, 32 distinct

| count | heading |
|---|---|
| 21 | `contact` |
| 12 | `we look forward to your tour. feel free to contact us with questions.` |
| 10 | `contact us for the latest weather call` |
| 10 | `contact us` |
| 9 | `please contact us as soon as you have your accommodation booked, if no` |
| 7 | `need to contact us?` |
| 6 | `contact information` |
| 4 | `contact details` |
| 4 | `please contact manly surf guide to arrange a time for pick-up or deliv` |
| 4 | `we will contact you for your course arrangements` |
| 4 | `we will contact you to confirm the exact pick time` |
| 3 | `contact us via whatsapp: +61 459 060 011` |
| 2 | `if you have any questions prior to travel, please contact us at` |
| 2 | `contacting us` |
| 2 | `customers are asked to contact us by phone the day before the lesson t` |
| 2 | `please contact us with any questions or if you have flight changes tha` |
| 2 | `contact port phillip ferries customer support team##` |
| 2 | `if you have any issues accessing your tour, please contact us` |
| 1 | `whale watch kaikoura contact information` |
| 1 | `once you arrive in taumarunui, please contact owhango adventures via` |
| … | _12 more distinct headings_ |

### `redo_booking_cancellation` — 117 occurrences, 30 distinct

| count | heading |
|---|---|
| 29 | `cancellation policy` |
| 17 | `cancellations` |
| 8 | `cancellation/ refund notes` |
| 7 | `need to reschedule?` |
| 6 | `a full refund or` |
| 6 | `weather cancellation` |
| 5 | `payment & cancellation for multi day tours` |
| 3 | `refunds` |
| 3 | `tour cancellation` |
| 3 | `please call to reschedule your cruise if you have` |
| 3 | `cancellations & bad weather` |
| 3 | `bad weather cancellations & your safety` |
| 2 | `exclusion without refund!!!! read all notes below!!!` |
| 2 | `cancellations due to weather` |
| 2 | `all passes are non-refundable and non-transferable` |
| 2 | `refund requests` |
| 2 | `no-show policy` |
| 2 | `operator cancellations` |
| 1 | `what is the refund policy?` |
| 1 | `refunds / cancellations - guest` |
| … | _10 more distinct headings_ |

### `redo_booking_faqs` — 86 occurrences, 23 distinct

| count | heading |
|---|---|
| 14 | `here is our link to faqs` |
| 9 | `faqs` |
| 8 | `🙋‍♂️ questions?` |
| 6 | `questions?` |
| 6 | `please review our [faq page](http://www.islandscenicflights.com.au/isl` |
| 5 | `faq` |
| 5 | `got questions?` |
| 5 | `link to faqs` |
| 5 | `check out our [faq page!](https://spiritwhalewatching.com.au/faq/)` |
| 4 | `please remember that if you answer “yes” to any of the questions on th` |
| 3 | `phone us with any questions` |
| 2 | `questions & assistance` |
| 2 | `if you have any additional questions, please email heidi at [h.daniels` |
| 2 | `any questions or requests email info@motorvesselwairua.co.nz` |
| 2 | `if you answer no to all medical questions` |
| 1 | `frequently asked questions` |
| 1 | `for frequently asked questions, please visit` |
| 1 | `for questions or to report an issue with your stored item` |
| 1 | `faq's` |
| 1 | `if you have any questions, or there's anything we can help with, pleas` |
| … | _3 more distinct headings_ |

### `redo_booking_what_not_to_bring` — 12 occurrences, 5 distinct

| count | heading |
|---|---|
| 7 | `what not to bring` |
| 2 | `not permitted` |
| 1 | `what not to bring?` |
| 1 | `smoking is not permitted during a ghost tour` |
| 1 | `please note: photography and video filming are not permitted inside th` |

## UNASSIGNED — the queue to work through

2,616 distinct headings, 8,240 occurrences, none of which any column currently claims.

| count | heading | example product |
|---|---|---|
| 60 | `tax invoice` | 640891 |
| 48 | `please arrive 15 minutes prior` | 496818 |
| 48 | `about` | 713267 |
| 48 | `abn: 36 611 842 947` | 210549 |
| 45 | `duration` | 491230 |
| 45 | `sydney seafood school` | 660870 |
| 42 | `what to expect` | 439970 |
| 42 | `we look forward to seeing you soon!` | 374466 |
| 41 | `please arrive 15 minutes early!` | 235849 |
| 40 | `reminder` | 665305 |
| 37 | `safety` | 592732 |
| 37 | `please always` | 215245 |
| 37 | `see you soon!` | 428890 |
| 36 | `terms and conditions` | 399947 |
| 36 | `we hope you are looking forward to riding the vehicle.` | 391580 |
| 35 | `please arrive 15 minutes prior.` | 545862 |
| 32 | `restrictions` | 266501 |
| 32 | `rain` | 223111 |
| 32 | `thank you for booking. we look forward to your visit.` | 269572 |
| 31 | `on board safety` | 170699 |
| 31 | `safe boarding and disembarking` | 438838 |
| 31 | `responsible service of alcohol` | 438838 |
| 31 | `booking subject to vagabond cruises’ terms and conditions` | 438838 |
| 31 | `instagram competition` | 438838 |
| 30 | `dear guest` | 175366 |
| 30 | `plan your trip ahead of time with nsw transport` | 438838 |
| 30 | `nearest train station to darling harbour | king street wharf` | 438838 |
| 28 | `for cycling you will need to wear` | 478642 |
| 28 | `gst tax invoice` | 525411 |
| 28 | `gst# 88-952-413` | 525411 |
| 28 | `to access the bicycle and equipment rental agreement, click the link b` | 584033 |
| 28 | `please arrive 10 minutes before your start time` | 586870 |
| 27 | `the crew` | 461982 |
| 26 | `what's provided` | 713267 |
| 26 | `terms & conditions` | 701258 |
| 25 | `we look forward to having you!` | 568774 |
| 25 | `please arrive 20 minutes earlier for safety briefing` | 272228 |
| 24 | `schedule` | 257880 |
| 24 | `participation form` | 103450 |
| 24 | `disclaimers` | 254532 |
| 23 | `on the day` | 176259 |
| 23 | `safety responsibility` | 480027 |
| 23 | `food & drinks` | 734654 |
| 23 | `how to get there` | 689483 |
| 23 | `please arrive 15 minutes early for a safety briefing` | 236268 |
| 22 | `toowoomba railway station` | 505742 |
| 22 | `fraud prevention` | 239380 |
| 22 | `what happens if it rains?` | 310276 |
| 22 | `storage` | 310276 |
| 22 | `change of booking` | 310276 |
| 21 | `thank you for booking with dave's travel group!` | 112645 |
| 20 | `check-out time: 9am` | 584922 |
| 20 | `time` | 553397 |
| 20 | `abn: 42 666 747 011` | 635388 |
| 18 | `trip information` | 110419 |
| 18 | `info about your lesson` | 328412 |
| 16 | `thank you for booking with us!` | 400008 |
| 16 | `cellphone with data` | 223111 |
| 16 | `dress for the conditions!` | 223111 |
| 16 | `sun` | 223111 |
| 16 | `wind proof jacket` | 223111 |
| 16 | `will i get wet?` | 223111 |
| 16 | `splashes` | 223111 |
| 16 | `disclaimer` | 480027 |
| 16 | `the capturedu team` | 539058 |
| 16 | `start` | 112645 |
| 16 | `also recommended` | 234931 |
| 16 | `milford sound risk disclosure` | 257745 |
| 16 | `aotearoa new zealand` | 257745 |
| 16 | `piopiotahi milford sound` | 257745 |
| 16 | `earthquakes at piopiotahi milford sound` | 257745 |
| 16 | `what to do in an earthquake` | 257745 |
| 15 | `houseboat policy additions` | 270299 |
| 15 | `have fun!` | 347371 |
| 15 | `don't forget` | 347371 |
| 15 | `our tips` | 347371 |
| 15 | `how to operate e-bikes` | 347371 |
| 15 | `please arrive at least 15 minutes prior to the start of your booking.` | 419095 |
| 14 | `canoe safaris` | 175557 |
| 14 | `end` | 126065 |
| 14 | `pathways` | 126418 |
| 14 | `shared pathways` | 126418 |
| 14 | `separate pathways` | 126418 |
| 14 | `no bicycle zone` | 126418 |
| 14 | `riding` | 126418 |
| 14 | `boarding` | 266987 |
| 14 | `here’s what you need to know:###` | 288751 |
| 14 | `final things you should know` | 288751 |
| 14 | `we hope you are looking forward to your adventure. please see below a ` | 278762 |
| 14 | `please meet at mount surf school 15 minutes beforehand - that should a` | 475345 |
| 14 | `please see reception to pick up your bikes.` | 347371 |
| 14 | `thank you for choosing watsons mountain country trail rides.` | 172430 |
| 14 | `conditions of use` | 172430 |
| 14 | `surf shop` | 328412 |
| 13 | `meeting your guide` | 346619 |
| 13 | `blue sky helicopters` | 176259 |
| 13 | `booking confirmed` | 176264 |
| 13 | `what next` | 175557 |
| 13 | `highlights` | 153631 |
| 13 | `time to be there` | 627558 |
| 13 | `your vessel` | 268127 |
| 13 | `once heletranz receives your booking they will confirm within 24 hours` | 189679 |
| 13 | `are you ready for action?!` | 196167 |
| 13 | `please arrive 20 minutes prior to your booking to allow you enough tim` | 255058 |
| 13 | `lake mac watersports` | 255058 |
| 13 | `where to go` | 183348 |
| 13 | `booking confirmation` | 74549 |
| 13 | `we have complementary fishing rods, reals and tackle. we sell bait, ic` | 419095 |
| 13 | `extra accessories` | 328412 |
| 12 | `downssteam tourist railway and museum` | 563586 |
| 12 | `cruise information` | 268658 |
| 12 | `membership programme` | 267507 |
| 12 | `inflite - gst: 109-091-502` | 189679 |
| 12 | `please arrive at your booked ride time not earlier :)` | 117405 |
| 12 | `vessel specific information` | 180984 |
| 12 | `melbourne river cruises` | 176446 |
| 12 | `information for visit` | 422888 |
| 12 | `sun protection (hat, sunglasses, sunscreen) camera` | 531283 |
| 12 | `download the app` | 328412 |
| 11 | `booking conditions` | 309930 |
| 11 | `fare conditions` | 309930 |
| 11 | `passenger behaviour` | 309930 |
| 11 | `luggage` | 309930 |
| 11 | `cold and/or windy` | 223140 |
| 11 | `need assistance?` | 272823 |
| 11 | `check us out on social media!` | 112645 |
| 11 | `mövenpick hotel auckland` | 232531 |
| 11 | `if you require an airport transfer to or from whitsunday coast airport` | 175366 |
| 11 | `on the night` | 268127 |
| 11 | `tour translation` | 324103 |
| 11 | `follow these links to download the app` | 324103 |
| 11 | `love queenstown community fund` | 508766 |
| 11 | `aero logistics hunter valley` | 74549 |
| 11 | `currumbin alley – gold coast, qld australia` | 109372 |
| 11 | `[wellington surf shop](https://wellingtonsurfshop.co.nz/)` | 328412 |
| 10 | `sea sickness` | 187067 |
| 10 | `please ensure` | 440992 |
| 10 | `workshop details` | 539058 |
| 10 | `[click the map to open in google maps!](https://goo.gl/maps/fwacuxr5uw` | 201804 |
| 10 | `on the day of your flight` | 107890 |
| 10 | `please call us the day before your flight to confirm minimum numbers a` | 109891 |
| 10 | `should you eat?` | 155617 |
| 10 | `eftpos, all major credit cards & wechat pay available` | 196167 |
| 10 | `how to get here` | 103145 |
| 10 | `your flight is pending final approval.` | 413332 |
| 10 | `we recommend packing` | 356142 |
| 10 | `essential equipment` | 172706 |
| 10 | `toiletries` | 172706 |
| 10 | `personal equipment` | 172706 |
| 10 | `wildlife coast cruises terms` | 718813 |

## Inline `Label: value` lines (STEP 1D — these license a column too)

| count | label |
|---|---|
| 180 | `please note` |
| 131 | `phone` |
| 126 | `note` |
| 119 | `email` |
| 98 | `abn` |
| 85 | `website` |
| 84 | `location` |
| 76 | `office hours` |
| 43 | `important` |
| 41 | `footwear` |
| 41 | `address` |
| 37 | `what to bring` |
| 36 | `parking` |
| 36 | `hat` |
| 36 | `waiver` |
| 33 | `scheduling` |
| 33 | `sun cream` |
| 32 | `weather` |
| 32 | `meeting point` |
| 29 | `clothing` |
| 23 | `check-in time` |
| 22 | `check-out time` |
| 21 | `dry clothes` |
| 20 | `important note` |
| 20 | `refunds and changes` |
| 18 | `google maps link` |
| 18 | `warm top` |
| 15 | `secure gear bag` |
| 14 | `towel` |
| 13 | `food/water` |
| 12 | `arrival time` |
| 12 | `inflite - gst` |
| 12 | `sign-in and out` |
| 12 | `food` |
| 11 | `shorts` |
| 11 | `t-shirt` |
| 10 | `optional` |
| 10 | `duration` |
| 10 | `things to pack for your cruise include` |
| 9 | `arrive` |
