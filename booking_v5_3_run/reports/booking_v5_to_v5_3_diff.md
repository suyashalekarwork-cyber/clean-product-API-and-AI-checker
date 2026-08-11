# Booking V5 → V5.3 — what changed

Same 100 products, same raw input. Every difference below is
caused by the prompt change and nothing else.

## Column fill: before and after

| Column | V5 | V5.3 | Δ | V5 words | V5.3 words |
|---|---|---|---|---|---|
| notes  *(was other)* | 94 | 90 | -4 | 20,536 | 17,682 |
| what_to_bring | 72 | 61 | -11 | 5,264 | 3,993 |
| meeting_point  *(was location)* | 66 | 53 | -13 | 4,503 | 3,406 |
| important_info | 68 | 36 | -32 | 16,018 | 4,985 |
| what_included  *(was inclusions)* | 38 | 32 | -6 | 1,052 | 789 |
| disclaimers **NEW** | 0 | 26 | +26 | 0 | 11,780 |
| check_in | 36 | 23 | -13 | 1,363 | 1,813 |
| before_arrival | 19 | 23 | +4 | 1,280 | 5,104 |
| health_safety **NEW** | 0 | 19 | +19 | 0 | 7,048 |
| restrictions | 33 | 18 | -15 | 6,639 | 3,562 |
| pricing **NEW** | 0 | 15 | +15 | 0 | 859 |
| itinerary | 16 | 13 | -3 | 1,334 | 1,011 |
| departure_info | 20 | 11 | -9 | 1,276 | 833 |
| duration_text **NEW** | 0 | 11 | +11 | 0 | 279 |
| contact | 30 | 10 | -20 | 1,013 | 570 |
| faqs | 17 | 10 | -7 | 2,185 | 674 |
| cancellation | 22 | 9 | -13 | 2,134 | 1,318 |
| highlights **NEW** | 0 | 6 | +6 | 0 | 386 |
| special_requirements **NEW** | 0 | 5 | +5 | 0 | 217 |
| what_not_to_bring | 5 | 3 | -2 | 279 | 178 |
| accessibility **NEW** | 0 | 3 | +3 | 0 | 148 |
| extras **NEW** | 0 | 2 | +2 | 0 | 75 |
| what_excluded **NEW** | 0 | 2 | +2 | 0 | 126 |
| group_size **NEW** | 0 | 1 | +1 | 0 | 10 |
| location | 66 | 0 | -66 | 4,503 | 0 |
| other | 94 | 0 | -94 | 20,536 | 0 |
| inclusions | 38 | 0 | -38 | 1,052 | 0 |

## Where content moved

Rows where a sentence did NOT stay in its expected column. Movement out
of `other`/`notes` into a new column is the intended effect. Movement out
of a column that already worked is what to scrutinise.

| From (V5) | To (V5.3) | Sentences |
|---|---|---|
| important_info | health_safety | 403 |
| important_info | disclaimers | 373 |
| other | disclaimers | 139 |
| restrictions | disclaimers | 103 |
| location | before_arrival | 92 |
| restrictions | notes | 91 |
| restrictions | health_safety | 79 |
| other | important_info | 78 |
| important_info | notes | 69 |
| other | before_arrival | 64 |
| important_info | before_arrival | 62 |
| other | LOST ⚠️ | 54 |
| faqs | notes | 51 |
| what_to_bring | before_arrival | 50 |
| other | pricing | 49 |
| cancellation | disclaimers | 41 |
| other | restrictions | 38 |
| what_to_bring | notes | 37 |
| location | important_info | 34 |
| other | check_in | 34 |
| inclusions | notes | 31 |
| restrictions | LOST ⚠️ | 30 |
| faqs | LOST ⚠️ | 26 |
| other | duration_text | 25 |
| other | highlights | 24 |
| contact | before_arrival | 24 |
| location | notes | 18 |
| check_in | meeting_point | 17 |
| departure_info | meeting_point | 15 |
| what_to_bring | important_info | 14 |
| departure_info | before_arrival | 14 |
| itinerary | notes | 13 |
| departure_info | important_info | 13 |
| other | what_included | 12 |
| important_info | LOST ⚠️ | 12 |
| restrictions | important_info | 12 |
| what_to_bring | disclaimers | 11 |
| restrictions | special_requirements | 10 |
| check_in | notes | 10 |
| contact | notes | 10 |
| cancellation | important_info | 9 |
| contact | important_info | 9 |
| important_info | accessibility | 9 |
| other | health_safety | 9 |
| location | disclaimers | 8 |
| location | LOST ⚠️ | 8 |
| other | meeting_point | 7 |
| itinerary | LOST ⚠️ | 7 |
| other | contact | 7 |
| inclusions | before_arrival | 6 |
| before_arrival | notes | 6 |
| other | what_excluded | 6 |
| important_info | restrictions | 6 |
| before_arrival | disclaimers | 5 |
| itinerary | departure_info | 5 |
| what_not_to_bring | important_info | 5 |
| inclusions | disclaimers | 4 |
| inclusions | important_info | 4 |
| what_to_bring | LOST ⚠️ | 4 |
| contact | health_safety | 4 |
| departure_info | disclaimers | 4 |
| departure_info | notes | 4 |
| other | special_requirements | 4 |
| contact | LOST ⚠️ | 3 |
| contact | disclaimers | 3 |
| restrictions | before_arrival | 3 |
| before_arrival | what_to_bring | 3 |
| what_not_to_bring | notes | 3 |
| before_arrival | LOST ⚠️ | 2 |
| other | extras | 2 |
| what_not_to_bring | what_to_bring | 2 |
| important_info | what_to_bring | 2 |
| inclusions | special_requirements | 2 |
| contact | faqs | 2 |
| contact | meeting_point | 2 |
| check_in | LOST ⚠️ | 2 |
| check_in | disclaimers | 2 |
| location | check_in | 2 |
| departure_info | itinerary | 2 |
| itinerary | check_in | 1 |
| restrictions | extras | 1 |
| check_in | before_arrival | 1 |
| other | group_size | 1 |
| faqs | important_info | 1 |
| other | departure_info | 1 |
| other | itinerary | 1 |
| cancellation | restrictions | 1 |
| cancellation | notes | 1 |
| other | cancellation | 1 |
| check_in | itinerary | 1 |
| departure_info | LOST ⚠️ | 1 |

**Sentences present in V5 but in no V5.3 column: 149**

## Per product

### 100271 — Kitchen One (Bratt Pan) - Hourly Rental

- `inclusions` → `notes` — All equipment within kitchen i.e
- `inclusions` → `notes` — Toilets (within the strata.
- `inclusions` → `notes` — Toilets in The Cooking Professor are NOT to be used by Perth Kitchen Hire clients unless T
- `inclusions` → `notes` — Use of fridge for storage during hire period only
- `inclusions` → `notes` — (for all cold/dry storage hire log on to https://www.perthkitchenhire.com.au)
- `inclusions` → `disclaimers` — Perth Kitchen Hire provides usage of utilities – water, power, gas and toilets as part of 
- `inclusions` → `disclaimers` — Should it be deemed that unnecessary or excessive usage of these utilities occurs, then Pe
- `location` → `disclaimers` — Perth Kitchen Hire is situated in a business strata title and parking is restricted to a f
- `location` → `disclaimers` — Parking bay usage differs during business and non-business hours.
- `location` → `disclaimers` — Access to the building is via the large sliding door and you can park temporarily outside 
- _…and 39 more_

### 100273 — Kitchen Two - Hourly Rental

- `what_to_bring` → `disclaimers` — A list of equipment included in the Kitchen for hire includes and is limited to:
- `what_to_bring` → `disclaimers` — All main equipment within kitchen i.e.
- `what_to_bring` → `disclaimers` — ovens, oven trays, cooktops, benches and sinks.
- `what_to_bring` → `disclaimers` — This does not include items stored on shelves that are rented by other hire clients.
- `what_to_bring` → `disclaimers` — Use of fridge shelving allocated for food preps, only during hire period, unless hired and
- `what_to_bring` → `disclaimers` — All kitchen utensils and equipment such as pots, pans, utensils and electrical goods are t
- `what_to_bring` → `disclaimers` — No equipment is to be left at the kitchens unless storage arrangements have been made.
- `what_to_bring` → `disclaimers` — Should damage occur that renders any item unusable it is expected that it will be replaced
- `what_to_bring` → `disclaimers` — It is expected that hirers will provide all necessary foodstuffs for their requirements.
- `what_to_bring` → `disclaimers` — Perth Kitchen Hire will not provide any foodstuffs.
- _…and 49 more_

### 103729 — U/12's Micro-Groms High Performance Camp

- `faqs` → `LOST` — Q: WHAT IS HIGH PERFORMANCE ALL ABOUT?
- `faqs` → `LOST` — A: Our high performance coaching camps are about reaching your true surfing ability with t
- `faqs` → `LOST` — Q: WHAT STRATEGIES DO YOU USE?
- `faqs` → `LOST` — A: Video Analysis: We use video analysis to improve your surfing technique and skill level
- `faqs` → `notes` — Our high performance coaches film your surfing session from the beach, then sit with you t
- `faqs` → `notes` — You then get to go back out in the water to put the advice in to practice.
- `faqs` → `notes` — You will be amazed at how the slightest tweak can make you look and feel like a whole new 
- `faqs` → `notes` — Surf Skate boards: No wave is ever the same and conditions are forever changing.
- `faqs` → `notes` — Practice makes improvements and getting the feel of how your body should be balanced and p
- `faqs` → `notes` — Our Surf Skate boards are purpose built to create the same feeling of surfing and let you 
- _…and 7 more_

### 103730 — 16's & Under Groms High Performance Camp

- `faqs` → `LOST` — Q: WHAT IS HIGH PERFORMANCE ALL ABOUT?
- `faqs` → `LOST` — A: Our high performance coaching camps are about reaching your true surfing ability with t
- `faqs` → `LOST` — Q: WHAT STRATEGIES DO YOU USE?
- `faqs` → `LOST` — A: Video Analysis: We use video analysis to improve your surfing technique and skill level
- `faqs` → `notes` — Our high performance coaches film your surfing session from the beach, then sit with you t
- `faqs` → `notes` — You then get to go back out in the water to put the advice in to practice.
- `faqs` → `notes` — You will be amazed at how the slightest tweak can make you look and feel like a whole new 
- `faqs` → `notes` — Surf Skate boards: No wave is ever the same and conditions are forever changing.
- `faqs` → `notes` — Practice makes improvements and getting the feel of how your body should be balanced and p
- `faqs` → `notes` — Our Surf Skate boards are purpose built to create the same feeling of surfing and let you 
- _…and 7 more_

### 103734 — Grom Squad Term Training

- `what_to_bring` → `LOST` — Swimming Squad - Drinking water
- `what_to_bring` → `LOST` — Strength and Mobility Training - Drinking water
- `other` → `pricing` — Full Program: $70 per week
- `other` → `pricing` — Surfing Training Only: $60 per week
- `other` → `pricing` — Swimming Squad Only: $15 per week
- `other` → `pricing` — Strength/Mobility Only: $15 per week
- `other` → `duration_text` — Programs change from term to term.
- `other` → `duration_text` — They normally run for 4 to 8 weeks per term.
- `other` → `duration_text` — Please see our term timetable below to see all dates, start time & duration of programs.
- `other` → `what_included` — We will provide you with the following when you arrive for your camp

### 103791 — Sunshine Masters Camping Trip

- `departure_info` → `meeting_point` — Meet at 2 Villers St Cowaramup at 4pm on Thursday sharp for our camp to head off to Perth 
- `departure_info` → `meeting_point` — Perth crew meet at 9 Cunningham Tec Daghlish at 8:30pm on Thursday.
- `faqs` → `LOST` — Q: WHAT IS SUNSHINE SURF MASTERS COMP ROAD TRIP ALL ABOUT?
- `faqs` → `LOST` — A: It’s about having fun camping with friends while competing and getting coaching tips al
- `faqs` → `notes` — It teaches the groms to work as a team to set up their camping area, cook and clean.
- `faqs` → `notes` — They also have to budget their money for their meals over the 4 days.
- `faqs` → `notes` — All while being supervised by our qualified, professional and friendly coaches.
- `faqs` → `notes` — The camp involves surfing the day before the comp to become familiar with the wave and the
- `faqs` → `notes` — We will also film most of the heats so the groms can look over their footage.
- `other` → `what_included` — We will provide you with the following when you arrive for your tour:
- _…and 4 more_

### 104248 — Yallingup Boardriders Coaching

- `faqs` → `LOST` — Q: WHAT IS HIGH PERFORMANCE ALL ABOUT?
- `faqs` → `LOST` — A: Our Performance Surf Coaching camps are about reaching your true surfing ability with t
- `faqs` → `LOST` — Q: WHAT STRATEGIES DO YOU USE?
- `faqs` → `LOST` — A: Video Analysis: We use video analysis to improve your surfing technique and skill level
- `faqs` → `notes` — Our high performance coaches film your surfing session from the beach, then sit with you t
- `faqs` → `notes` — You then get to go back out in the water to put the advice in to practice.
- `faqs` → `notes` — You will be amazed at how the slightest tweak can make you look and feel like a whole new 
- `faqs` → `notes` — Competition Practice: We hold mock competitions & drills and run through successful heat s
- `other` → `duration_text` — Day 1 - 15th December 2023
- `other` → `duration_text` — Day 2 - 22nd December 2023
- _…and 16 more_

### 108022 — Private Surf Lesson @ Te Arai

- `other` → `LOST` — 2 Hour Surf Lesson - Ages 6+
- `other` → `LOST` — Private Surf Lesson - Ages 4+
- `other` → `LOST` — Surf Tours - 2 night weekend tour of Mangawhai and Te Arai, including pickup drop off Auck
- `other` → `LOST` — Ultimate Kids Surf Camp (5 nights) April, October, January - Ages 8+
- `other` → `LOST` — Youth Surf Camp (4 nights) April, October, December, January - Ages 13+
- `other` → `LOST` — After School Surfing (also avalable Sat mornings) - 6 week Learn to Surf Program - Ages 6+
- `other` → `LOST` — School Holiday Programs - 2 Day program - 4 lessons - April, October & December - Ages 6+
- `other` → `LOST` — Surf Day Programs for Shools Any Auckland or Northland location - ages 5+
- `other` → `LOST` — Overnight School Camps (3-5 day camps) Full service camps in Mangawhai - Accomodation, cat
- `other` → `LOST` — Corporates and Teams Custom lessons, programs or overnight experiences for all ages and fi

### 124223 — U/13's Girls Get Start Intermediate 3 Half Day Camp

- `faqs` → `LOST` — Q: WHAT IS HIGH PERFORMANCE ALL ABOUT?
- `faqs` → `LOST` — A: Our Get Start Intermediate Coaching Camps are about reaching your true surfing ability 
- `faqs` → `LOST` — Q: WHAT STRATEGIES DO YOU USE?
- `faqs` → `LOST` — A: Water Coaching: We have coach that swim in the water helps groms learn where catch wave
- `faqs` → `notes` — Video Analysis: We use video analysis to improve your surfing technique and skill level.
- `faqs` → `notes` — Our high performance coaches film your surfing session from the beach, then sit with you t
- `faqs` → `notes` — You then get to go back out in the water to put the advice in to practice.
- `faqs` → `notes` — You will be amazed at how the slightest tweak can make you look and feel like a whole new 
- `faqs` → `notes` — Surf Skate: No wave is ever the same and conditions are forever changing.
- `faqs` → `notes` — Practice makes improvements and getting the feel of how your body should be balanced and p
- _…and 4 more_

### 179366 — Camp Epic Timber Trail Package

- `other` → `pricing` — Please ensure payment is made 1 week prior to your booking.
- `other` → `pricing` — Either by card (credit card fee applies) or by bank deposit 03-1322-0775006-00 using your 
- `other` → `pricing` — Alternatively you can pay cash/card on arrival if preferred.

### 179370 — Camp Epic - Accommodation Only

- `important_info` → `notes` — Important info for your stay.
- `important_info` → `notes` — Please pass this on to other members of your group.
- `other` → `pricing` — Please ensure payment is made 1 week prior to your booking.
- `other` → `pricing` — Either by card (credit card fee applies) or by bank deposit 03-1322-0775006-00 using your 
- `other` → `pricing` — Alternatively you can pay cash/card on arrival if preferred.

### 187067 — Half Day Reef Deep Sea Fishing

- `location` → `important_info` — Your skipper is extremely experienced and is able to provide you the benefits of local kno
- `location` → `important_info` — Where we fish also depends on weather conditions and your skipper will take you to the app
- `location` → `important_info` — Distance out to sea will also be dependent on weather, current and a variety of sea condit
- `location` → `important_info` — Whilst every effort is made to catch fish we can not guarantee fish.
- `location` → `important_info` — It is extremely rare that you would not catch a fish and you are able to keep what you cat
- `location` → `important_info` — Your fish are cleaned, bagged and iced for you to take home.
- `location` → `important_info` — We recommend that you have an esky in the car so that you can transport your fish home.
- `other` → `important_info` — Description of image https://cdn.filestackcontent.com/sJXa6f8NTPOmo5AMvkxT

### 187073 — Full Day Fishing Trip

- `location` → `notes` — Your skipper is extremely experienced and is able to provide you the benefits of local kno
- `location` → `notes` — Where we fish also depends on weather conditions and your skipper will take you to the app
- `location` → `notes` — Distance out to sea will also be dependent on weather, current and a variety of sea condit
- `location` → `notes` — Whilst every effort is made to catch fish we can not guarantee fish.
- `location` → `notes` — It is extremely rare that you would not catch a fish and you are able to keep what you cat
- `location` → `notes` — Your fish are cleaned, bagged and iced for you to take home.
- `location` → `notes` — We recommend that you have an esky in the car so that you can transport your fish home.

### 188491 — Junior Surf Titles Coaching Squads & Camps

- `faqs` → `LOST` — Q: WHAT IS JUNIOR SURF TITLES COACHING SQUADS & CAMPS ALL ABOUT?
- `faqs` → `LOST` — A: Our high performance coaching camps are about reaching your true surfing ability with t
- `faqs` → `LOST` — Q: WHAT STRATEGIES DO YOU USE?
- `faqs` → `LOST` — A: Video Analysis: We use video analysis to improve your surfing technique and skill level
- `faqs` → `notes` — Our high performance coaches film your surfing session from the beach, then sit with you t
- `faqs` → `notes` — You then get to go back out in the water to put the advice in to practice.
- `faqs` → `notes` — You will be amazed at how the slightest tweak can make you look and feel like a whole new 
- `faqs` → `notes` — Competition Practice: We hold mock competitions and run through successful heat strategies
- `faqs` → `notes` — Surf Skate boards: No wave is ever the same and conditions are forever changing.
- `faqs` → `notes` — Practice makes improvements and getting the feel of how your body should be balanced and p
- _…and 17 more_

### 211166 — Ride to Riches Trail – Arrowtown to Queenstown (Self-Guided)

- `location` → `LOST` — Meet & Greet Point – Queenstown CBD - Your meeting point is bus stop The Station Building 
- `location` → `LOST` — Finish Point - You’ll finish the ride at Queenstown Gardens – 16 Park Street, around:
- `location` → `LOST` — 4:30 PM for 10:00 AM sessions
- `location` → `LOST` — 5:00 PM for 12:00 PM sessions
- `location` → `LOST` — If you’ve arranged a door-to-door drop-off, we’ll take care of the rest.
- `location` → `LOST` — Please lock the bikes and message us when you’ve finished.
- `itinerary` → `check_in` — Route: Arrow River Trail → Twin Rivers Trail → Queenstown Gardens
- `important_info` → `notes` — ⚠️ 2026 Frankton Trail Update
- `important_info` → `notes` — Between mid-January and mid-November 2026, a short section of the Frankton Track is closed
- `important_info` → `notes` — A 3km sealed lakeside cycle path alongside Frankton Road will be used
- _…and 4 more_

### 254882 — Twilight Triventure

- `what_to_bring` → `notes` — Camera for photos while upstream in daylight.
- `inclusions` → `notes` — Safety Briefing and paddling instruction.
- `inclusions` → `notes` — Splash pants and jackets.
- `inclusions` → `notes` — PFD (personal Flotation Device).
- `inclusions` → `notes` — Changing area and secure storage available.
- `inclusions` → `notes` — Dry bag to store personal items in while kayaking.
- `inclusions` → `notes` — Warm woollen socks (during Winter)
- `inclusions` → `notes` — Plenty of parking onsite.
- `check_in` → `meeting_point` — Meet at Riverside Adventures Waikato Base, 362 Horahora Rd, Piarere.
- `check_in` → `meeting_point` — [View RAW Parking & Check in directions (3).pdf](https://cdn.filestackcontent.com/dWVH0MKr
- _…and 49 more_

### 254884 — Half Day Karāpiro

- `important_info` → `disclaimers` — This is a guided experience and operates in all weather conditions; Riverside Adventures i
- `important_info` → `disclaimers` — Ride times are estimates and may vary depending on fitness levels and time spent at stops.
- `important_info` → `disclaimers` — Minimum numbers may apply for shuttle departures.
- `important_info` → `disclaimers` — It is the customer’s responsibility to check Rhubarb Café opening hours if planning to vis
- `restrictions` → `special_requirements` — Participants must be confident riding a bike independently.
- `restrictions` → `special_requirements` — All participants must follow safety instructions and wear provided safety equipment where 
- `restrictions` → `special_requirements` — All safety briefings and instructions provided by Riverside Adventures staff must be follo
- `restrictions` → `special_requirements` — If wanting to upgrade from Standard Mountain bike to eBike, do get in touch.
- `restrictions` → `disclaimers` — Children must be a minimum of 8yrs (MTB) 10yrs old & 140cm (eBike) and be supervised by an
- `restrictions` → `disclaimers` — Participants are responsible for their own safety and should carry water, weather-appropri
- _…and 3 more_

### 257745 — Milford Sound Cruise | Aboard The Sovereign or Monarch

- `what_to_bring` → `notes` — Cabinet café food and snacks will be available for purchase onboard.
- `what_to_bring` → `notes` — Please be aware we do not accept cash onboard, please come prepared with a card payment op
- `what_to_bring` → `notes` — This is a cashless experience so please come prepared.
- `important_info` → `health_safety` — Visitors to Milford Sound should be aware of various natural hazards when going to Milford
- `important_info` → `health_safety` — Aotearoa New Zealand - Powerful natural forces have shaped Aotearoa New Zealand over milli
- `important_info` → `health_safety` — Earthquakes and volcanoes lifted these beautiful islands out of the Pacific Ocean.
- `important_info` → `health_safety` — They have created the dramatic landscapes we enjoy today.
- `important_info` → `health_safety` — Natural hazards are part of life here.
- `important_info` → `health_safety` — Around 20,000 earthquakes are recorded each year.
- `important_info` → `health_safety` — Most are small and go unnoticed, but larger events can cause damage.
- _…and 64 more_

### 265555 — Milford Sound Cruise and Coach – Queenstown Departure

- `what_to_bring` → `notes` — Drinks and snacks are available for purchase.
- `what_to_bring` → `notes` — This is a cashless experience so please come prepared.
- `check_in` → `notes` — If joining this tour from our Visitor Centre, please check-in 15 minutes before your depar
- `important_info` → `disclaimers` — Aotearoa New Zealand - Powerful natural forces have shaped Aotearoa New Zealand over milli
- `important_info` → `disclaimers` — Earthquakes and volcanoes lifted these beautiful islands out of the Pacific Ocean.
- `important_info` → `disclaimers` — They have created the dramatic landscapes we enjoy today.
- `important_info` → `disclaimers` — Natural hazards are part of life here.
- `important_info` → `disclaimers` — Around 20,000 earthquakes are recorded each year.
- `important_info` → `disclaimers` — Most are small and go unnoticed, but larger events can cause damage.
- `important_info` → `disclaimers` — Understanding the hazards and how to stay safe is an important part of planning your visit
- _…and 60 more_

### 265556 — Milford Sound Cruise and Coach – Te Anau Departure

- `what_to_bring` → `notes` — Drinks and snacks are available for purchase (please note we are cashless onboard)
- `check_in` → `notes` — Please check in at the Realnz Te Anau Visitor Centre front counter 20 minutes before your 
- `important_info` → `LOST` — Milford Sound Risk Disclosure
- `important_info` → `disclaimers` — Visitors to Milford Sound should be aware of various natural hazards when going to Milford
- `important_info` → `disclaimers` — Aotearoa New Zealand - Powerful natural forces have shaped Aotearoa New Zealand over milli
- `important_info` → `disclaimers` — Earthquakes and volcanoes lifted these beautiful islands out of the Pacific Ocean.
- `important_info` → `disclaimers` — They have created the dramatic landscapes we enjoy today.
- `important_info` → `disclaimers` — Natural hazards are part of life here.
- `important_info` → `disclaimers` — Around 20,000 earthquakes are recorded each year.
- `important_info` → `disclaimers` — Most are small and go unnoticed, but larger events can cause damage.
- _…and 61 more_

### 272823 — Gibbston Valley Canyoning Half Day Adventure

- `what_to_bring` → `before_arrival` — Swimwear to wear under your wetsuit
- `what_to_bring` → `before_arrival` — A towel for after the adventure
- `what_to_bring` → `before_arrival` — A personal water bottle
- `what_to_bring` → `before_arrival` — Any personal medications you may require
- `what_to_bring` → `before_arrival` — For your peace of mind, we recommend leaving unnecessary valuables at home.
- `what_to_bring` → `before_arrival` — Your dry clothes and personal belongings can be stored in our lock box while you are in th
- `what_to_bring` → `before_arrival` — While we have never experienced any security issues, we still recommend bringing only what
- `inclusions` → `before_arrival` — Lunch is included on the 08.30am tour
- `inclusions` → `before_arrival` — Participants will receive a lunch voucher to enjoy at one of our selected Queenstown partn
- `inclusions` → `before_arrival` — Erik's Fish and Chips https://www.eriks.nz/
- _…and 26 more_

### 272824 — Gibbston Valley Canyoning 3hr Self Drive Adventure

- `location` → `before_arrival` — Public Toilets Address: Coalpit Road, Gibbston Valley 9371
- `location` → `before_arrival` — Google Maps Pin https://maps.app.goo.gl/ByEnPXx8ShQ4iwucA
- `location` → `before_arrival` — Public Parking Address: Coalpit Road, Gibbston Valley 9371
- `location` → `before_arrival` — Google Maps Pin https://maps.app.goo.gl/Cfnk3QVCJaBpRcTD9
- `location` → `before_arrival` — From the parking area, it's just a short 2-minute walk to our check-in location.
- `location` → `before_arrival` — Please make your way to the Canyoning New Zealand branded changing shelter, located at the
- `location` → `before_arrival` — Your guides will meet you at the shelter for check-in and help you get ready for your adve
- `location` → `before_arrival` — If you arrive early, please wait at the shelter and we’ll be with you shortly.
- `location` → `before_arrival` — Address: 8 Coalpit Road, Gibbston Valley 9371
- `location` → `before_arrival` — Google Maps Pin https://maps.app.goo.gl/hs1a2zTBDGGu82np7
- _…and 9 more_

### 272826 — Mt Aspiring Canyoning Full Day Adventure

- `what_to_bring` → `before_arrival` — Swimwear to wear under your wetsuit
- `what_to_bring` → `before_arrival` — A towel for after the adventure
- `what_to_bring` → `before_arrival` — A personal water bottle
- `what_to_bring` → `before_arrival` — Any personal medications you may require
- `what_to_bring` → `before_arrival` — For your peace of mind, we recommend leaving unnecessary valuables at home.
- `what_to_bring` → `before_arrival` — Your dry clothes and personal belongings can be stored in our locked vehicle while you are
- `what_to_bring` → `before_arrival` — While we have never experienced any security issues, we still recommend bringing only what
- `location` → `before_arrival` — Please check your booking carefully and arrive at the meeting location selected for your t
- `location` → `before_arrival` — Queenstown Pick-Up – 08:20am meeting time
- `location` → `before_arrival` — Please wait outside the Eichardt’s Hotel.
- _…and 36 more_

### 275941 — Little Farmer Tours

- `other` → `disclaimers` — By continuing with your booking on line for a "Little Farmer Tour" at Tarnasey Farm locate
- `other` → `disclaimers` — expenses, causes of action, lawsuits, damages and liabilities, of every kind and nature, w
- `other` → `disclaimers` — I understand that the activities that I/children will participate in and that I/children w
- `other` → `disclaimers` — I/children will be in direct contact with animals that include but are not limited to:
- `other` → `disclaimers` — goats, pigs, sheep, horses, chickens, cows, alpacas etc., among other animals that may not
- `other` → `disclaimers` — I understand that, as with most animals, they may react in an unpredictable way to sounds,
- `other` → `disclaimers` — On behalf of myself, said children, my heirs, assigns and next of kin, I/children waive al
- `other` → `disclaimers` — By this waiver, I/children, assume any risk, and take full responsibility and waive any cl
- `other` → `disclaimers` — It is a condition of entry that visitors observe all verbal and visual warnings, do not ve
- `other` → `disclaimers` — This WAIVER AND RELEASE contains the entire agreement between parties, and supersedes any 
- _…and 7 more_

### 278797 — Try Scuba

- `important_info` → `before_arrival` — Recreational scuba diving and freediving require good physical and mental health.
- `important_info` → `before_arrival` — Some medical conditions can increase the risks associated with diving.
- `important_info` → `before_arrival` — The Fit to Dive Screening questions help determine whether you need to complete an additio
- `important_info` → `before_arrival` — For your safety — and the safety of those diving with you — please answer all questions ho
- `important_info` → `before_arrival` — If you are feeling unwell at any time, it’s important to avoid diving.

### 282368 — Surf Beach Boardriders Coaching

- `faqs` → `LOST` — Q: WHAT IS HIGH PERFORMANCE ALL ABOUT?
- `faqs` → `LOST` — A: Our high performance coaching camps are about reaching your true surfing ability with t
- `faqs` → `LOST` — Q: WHAT STRATEGIES DO YOU USE?
- `faqs` → `LOST` — A: Video Analysis: We use video analysis to improve your surfing technique and skill level
- `faqs` → `notes` — Our high performance coaches film your surfing session from the beach, then sit with you t
- `faqs` → `notes` — You then get to go back out in the water to put the advice in to practice.
- `faqs` → `notes` — You will be amazed at how the slightest tweak can make you look and feel like a whole new 
- `faqs` → `notes` — Surf Skate boards: No wave is ever the same and conditions are forever changing.
- `faqs` → `notes` — Practice makes improvements and getting the feel of how your body should be balanced and p
- `faqs` → `notes` — Our Surf Skate boards are purpose built to create the same feeling of surfing and let you 
- _…and 7 more_

### 282594 — Open Water Diver course

- `important_info` → `before_arrival` — Recreational scuba diving and freediving require good physical and mental health.
- `important_info` → `before_arrival` — Some medical conditions can increase the risks associated with diving.
- `important_info` → `before_arrival` — The Diver Medical Participant Questionnaire helps determine whether you should be assessed
- `important_info` → `before_arrival` — For your safety — and the safety of those diving with you — please answer all questions ho
- `important_info` → `before_arrival` — If you are feeling unwell at any time, it’s important to avoid diving.
- `before_arrival` → `LOST` — To begin your training, you’ll need to create an SSI account (at https://my.divessi.com) a
- `before_arrival` → `LOST` — Create your profile at https://my.divessi.com and affiliate with Dive Eden.

### 283352 — Freediving Level 1

- `itinerary` → `LOST` — Day 1 - 1:00–2:00pm – Lunch
- `itinerary` → `LOST` — Day 2 - 12:00pm – Lunch
- `itinerary` → `LOST` — Day 2 - Ocean dive 1
- `itinerary` → `LOST` — Day 2 - Ocean dive 2
- `itinerary` → `LOST` — Day 2 - 4:00pm – Finish
- `important_info` → `before_arrival` — Recreational scuba diving and freediving require good physical and mental health.
- `important_info` → `before_arrival` — Some medical conditions can increase the risks associated with diving.
- `important_info` → `before_arrival` — The Diver Medical Participant Questionnaire helps determine whether you should be assessed
- `important_info` → `before_arrival` — For your safety — and the safety of those diving with you — please answer all questions ho
- `important_info` → `before_arrival` — If you are feeling unwell at any time, it’s important to avoid diving.

### 309930 — 1 Day Thredbo Snow Tour

- `departure_info` → `important_info` — Please arrive at your designated departure point at least 15 minutes prior to departure ti
- `departure_info` → `important_info` — The coach cannot wait for late passengers.
- `departure_info` → `important_info` — The coach doors will remain closed after drop-off
- `departure_info` → `important_info` — Coach departs from Resort at approx.
- `departure_info` → `important_info` — Please follow the driver's/tour guide's instructions.
- `departure_info` → `disclaimers` — Travel times may vary due to weather, road, or traffic conditions.
- `departure_info` → `disclaimers` — Changes may be made at any time in the interest of passenger safety and operational requir
- `important_info` → `LOST` — Please note that the coach doors will remain closed after drop-off.
- `important_info` → `disclaimers` — Brighton Tours takes no responsibility for snow conditions, weather conditions, or resort 
- `important_info` → `disclaimers` — Minimum passenger numbers are required for tours to operate.
- _…and 36 more_

### 314330 — Using a Light Meter Workshop

- `what_to_bring` → `important_info` — On the day bring your digital SLR camera body and close to standard lens with charged batt
- `location` → `important_info` — The experience takes place bayside in Melbourne at a professional studio.
- `restrictions` → `important_info` — This workshop runs with a minimum of 2 and a maximum of 4
- `other` → `highlights` — What you will learn is how correct exposure is defined and how to look, expose and shoot f
- `other` → `highlights` — And how correct exposure forms the foundation of a good photograph.
- `other` → `highlights` — Develop an understanding of how different light meters work in incident, reflected and fla
- `other` → `highlights` — How to define and look for blacks, whites, tonal ranges, detail in highlight and shadow.
- `other` → `highlights` — Includes grey, B&W & colour scales & passport checker.
- `other` → `duration_text` — This course runs for 2 hours from 6pm – 8pm

### 314333 — Shoot, Develop and Scan B&W 35mm Film Workshop

- `other` → `LOST` — Shoot, Develop & Scan B&W 35mm film
- `other` → `highlights` — You will be given a roll of 35mm B&W film to go into your camera, followed by a shooting t
- `other` → `highlights` — A lecture on film processing and then in a 1 on 1 learning environment you will learn how 
- `other` → `duration_text` — This course runs for 4 hours from 12pm – 4pm
- `other` → `group_size` — This workshop operates 1 on 1.

### 316333 — Southern Lagoon - Guided Snorkelling Tour

- `before_arrival` → `notes` — To finalise your booking please sign this waiver https://docs.google.com/forms/d/e/1FAIpQL
- `other` → `check_in` — All tours with Reef N Beyond Eco Tours are undertaken entirely at your own risk.
- `other` → `check_in` — With the exclusion of gross negligence proven in a court of law, you agree that Reef N Bey
- `other` → `check_in` — Please arrive 15 mins prior to the departure time.
- `other` → `check_in` — No seating configuration is guaranteed, although Reef N Beyond staff will do the best they
- `other` → `check_in` — Reef N Beyond operates in a marine environment, and passengers can get wet or be exposed t
- `other` → `check_in` — A safety briefing will be given once onboard and prior to departure therefore please liste
- `other` → `check_in` — Reef N Beyond staff hold the right to refuse to carry any passenger that we feel may be at
- `other` → `check_in` — Passengers with any medical condition, injury or potential health risk should advise Reef 
- `other` → `check_in` — No smoking is permitted onboard Reef N Beyond at any time.
- _…and 8 more_

### 347817 — Dawn Drifters Balloon Flight

- `important_info` → `LOST` — Please be ready on time, late arrivals may miss the balloon.
- `important_info` → `health_safety` — Your temperature may be taken upon arrival.
- `important_info` → `health_safety` — Should your temperature be 38.0 or higher you will not be able to undertake your flight bu
- `important_info` → `health_safety` — We ask that all passengers adhere to social distancing guidelines while not in the balloon
- `important_info` → `health_safety` — You may be asked to wear a mask on the morning, including while indoors for the flight che
- `important_info` → `health_safety` — Hand sanitiser will be made available to you to use throughout the morning, but please be 
- `important_info` → `health_safety` — Should you feel unwell in the days before your flight please call 02 6248 8200 and speak w
- `important_info` → `health_safety` — Be aware YOU WILL BE CLOSE TO OTHER PASSENGERS during your outdoor adventure.
- `other` → `extras` — If you haven't already ordered it a full buffet breakfast is available after the flight at
- `other` → `extras` — Please contact us at the office prior to your flight if you wish to arrange breakfast or c

### 347825 — Dawn Drifters - Canberra Balloon Spectacular

- `cancellation` → `important_info` — If you cancel within 72 hours of departure or do not show up on the morning you will not b

### 370917 — Canyoning New Zealand Equipment Rentals

- `location` → `notes` — Your equipment will be waiting outside this address with your name on it.
- `location` → `notes` — Address: 47 Peregrine Falcon Road, Mount Creighton, Queenstown 9371
- `location` → `notes` — Google Maps Pin - https://maps.app.goo.gl/Cg4FsDzRBHmBgRwZ8
- `other` → `important_info` — New Zealand is a truly special place, and everyone who lives here or visits has a responsi
- `other` → `important_info` — The Tiaki Promise is a commitment to care for Aotearoa, now and for future generations.
- `other` → `important_info` — By embracing the Tiaki Promise, you are choosing to act as a guardian — respecting the lan

### 381162 — Te Awa: Karāpiro to Ngaruawahia

- `restrictions` → `important_info` — Minimum four people required for regular bookings; call to book if you have fewer than fou
- `restrictions` → `important_info` — All riders must wear a helmet (compulsory).
- `restrictions` → `important_info` — Participants must arrive on time for departure.
- `restrictions` → `important_info` — Children must be accompanied and supervised by an adult.
- `restrictions` → `important_info` — Please advise in advance if you have a non-standard bike (e.g.
- `restrictions` → `important_info` — Shuttle operates at specified times only—late arrivals may miss departure.
- `restrictions` → `important_info` — Non-standard bikes (e.g.
- `restrictions` → `important_info` — trailers, large e-bikes) must be advised in advance.
- `restrictions` → `important_info` — Children must be accompanied by an adult.
- `faqs` → `important_info` — [View faqs](https://cdn.filestackcontent.com/HP62aRBR7iFlfBKtVY9Z)
- _…and 12 more_

### 383995 — Te Awa: Cambridge to Ngaruawahia

- `itinerary` → `notes` — Complete your ride back at Cambridge Town Hall, where your vehicle will be waiting.
- `itinerary` → `notes` — We estimate 1 hour for every 10km biked, less if on eBike.
- `important_info` → `disclaimers` — A minimum fare (covering 1–4 people) applies to ensure the shuttle operates and is not sha
- `important_info` → `disclaimers` — The shuttle runs in most weather conditions; weather and trail conditions are outside of o
- `important_info` → `disclaimers` — Ride times and distances are estimates and may vary.
- `important_info` → `disclaimers` — Shuttle pick-up and drop-off times along the Te Awa are estimates and may vary, as we may 
- `contact` → `disclaimers` — [View terms-and-conditions](https://cdn.filestackcontent.com/illvevbySYe1dovcZdJZ)

### 397199 — 1 Day Perisher Snow Tour

- `departure_info` → `important_info` — Please arrive at your designated departure point at least 15 minutes prior to departure ti
- `departure_info` → `important_info` — The coach cannot wait for late passengers.
- `departure_info` → `important_info` — The coach doors will remain closed after drop-off
- `departure_info` → `important_info` — Coach departs from Resort at approx.
- `departure_info` → `important_info` — Please follow the driver's/tour guide's instructions
- `departure_info` → `important_info` — Late passengers may miss the coach departure, and no refunds or compensation will be provi
- `important_info` → `disclaimers` — All fares are subject to change without prior notice.
- `important_info` → `disclaimers` — Travel times may vary due to weather, road, or traffic conditions.
- `important_info` → `disclaimers` — Changes may be made at any time in the interest of passenger safety and operational requir
- `important_info` → `disclaimers` — Brighton Tours takes no responsibility for snow conditions, weather conditions, or resort 
- _…and 32 more_

### 403385 — Daily Public Group Tour Yarra Valley

- `what_not_to_bring` → `what_to_bring` — We do not allow customers to bring their own alcohol at the tart of the tour.
- `what_not_to_bring` → `what_to_bring` — Of course you can purchase when you are out there, but you can't bring your own.
- `itinerary` → `LOST` — We can take you to Chandon instead for lunch but this is all at your own expense but you n
- `itinerary` → `LOST` — We can always stop at Chandon for a quick photo.
- `itinerary` → `notes` — Note: That option is dependent on the tour running OK on time.
- `itinerary` → `notes` — This split is at the drivers discretion.
- `contact` → `LOST` — You can reach me on +61423237833 BY Text OR Whatsapp if you need anything or if you're run
- `other` → `LOST` — Thanks for booking with us.
- `other` → `LOST` — Excited to meet you!
- `other` → `restrictions` — In short: We WILL leave without if you are late.
- _…and 21 more_

### 427365 — Recreational Skipper’s Ticket

- `other` → `before_arrival` — In preparation for your upcoming [Recreational Skipper ticket course](https://www.transpor
- `other` → `before_arrival` — If you have booked someone else in, please make sure they read this confirmation email and
- `other` → `restrictions` — Please select your appropriate group.
- `other` → `restrictions` — Over 18 with drivers licence - You simply bring your WA drivers licence with you on the da
- `other` → `restrictions` — Under 18 with drivers licence or learners permit - You will need your licence or learners 
- `other` → `restrictions` — Under 18 NO LICENCE or Learners Permit - You need this [Parent consent form](https://www.t
- `other` → `restrictions` — A completed [Eyesight test](https://www.transport.wa.gov.au/mediaFiles/marine/MAC_F_RST_Ey
- `other` → `restrictions` — DO NOT DO MEDICAL UNLESS YOU HAVE A CONDITION THAT WOULD AFFECT YOUR ABILITY TO DRIVE A BO
- `other` → `restrictions` — (The easiest ID is a AUST passport less than 2 years old) If you don’t have a passport oth
- `other` → `restrictions` — IT IS A REQUIREMENT THAT YOU WILL COMPLETE THE PRE-COURSE STUDY!
- _…and 17 more_

### 469609 — Milford Sound Premium Cruise

- `check_in` → `notes` — Check in closes 15 minutes prior to departure
- `important_info` → `health_safety` — Visitors to Milford Sound should be aware of various natural hazards when going to Milford
- `important_info` → `health_safety` — Aotearoa New Zealand - Powerful natural forces have shaped Aotearoa New Zealand over milli
- `important_info` → `health_safety` — Earthquakes and volcanoes lifted these beautiful islands out of the Pacific Ocean.
- `important_info` → `health_safety` — They have created the dramatic landscapes we enjoy today.
- `important_info` → `health_safety` — Natural hazards are part of life here.
- `important_info` → `health_safety` — Around 20,000 earthquakes are recorded each year.
- `important_info` → `health_safety` — Most are small and go unnoticed, but larger events can cause damage.
- `important_info` → `health_safety` — Understanding the hazards and how to stay safe is an important part of planning your visit
- `important_info` → `health_safety` — Piopiotahi Milford Sound - Dramatic and ever-changing, Piopiotahi Milford Sound is one of 
- _…and 62 more_

### 478466 — Sydney Harbour Bridge Breakfast Paddle

- `itinerary` → `departure_info` — Meet at the beach in Quibaree Park, Lavender Bay before 7.00am.
- `itinerary` → `departure_info` — We start at 7.00 so please arrive 10 minutes early so you can complete the paperwork and h
- `itinerary` → `departure_info` — We will pack the Kayaks, have a safety and paddle technique briefing and the plan is to be
- `itinerary` → `departure_info` — We will paddle under the Harbour Bridge, past the Opera House, Admiralty House and Kirribi
- `itinerary` → `departure_info` — After breakfast we will retrace our route back to Lavender bay.
- `important_info` → `what_to_bring` — Paddling is a water sport so expect to get splashed.
- `important_info` → `what_to_bring` — Your feet will get wet so water friendly footwear is strongly recommended.
- `important_info` → `notes` — There can be a lot of boat traffic so we can sometimes spend a few minutes waiting for Fer
- `important_info` → `notes` — This is an easy paddle of about an hour each way depending on conditions.
- `contact` → `notes` — Call or text Sam 04 5188 7675.
- _…and 2 more_

### 478478 — Seal Experience Paddle

- `contact` → `notes` — Any questions call or text Sam on 04 5188 7675.
- `other` → `LOST` — Thank you for joining Sydney Kayak on a Seal encounter lunch paddle adventure.
- `other` → `LOST` — We will paddle around the back of Barrenjoey Head and spend some time looking at the Seals
- `other` → `LOST` — Please note Seals are wild animals in their natural habitat and there are regulations rega
- `other` → `LOST` — Please follow Sam’s instructions at all times.
- `other` → `LOST` — When we have had enough of the Seals we will paddle across Pittwater and have lunch on a s
- `other` → `LOST` — Which beach will depend on the weather conditions on the day.
- `other` → `LOST` — After lunch/dinner, and a swim if that is your thing, we will head back to Station Beach, 
- `other` → `duration_text` — This is an easy paddle of about 2.5 hours of paddling, depending on conditions and the pad

### 480028 — 2-Day Whanganui River Canoe Journey | FREE Night Stay Includ

- `important_info` → `disclaimers` — Customers are responsible for loss or damage to hired equipment
- `important_info` → `disclaimers` — Owhango Adventures is not responsible for loss or damage to personal belongings, valuables
- `important_info` → `disclaimers` — All equipment is regularly inspected and maintained for safety and reliability
- `important_info` → `health_safety` — A full safety briefing is provided before departure
- `important_info` → `health_safety` — There is little to no cellphone reception across much of the journey
- `restrictions` → `notes` — This is a self-guided freedom hire journey
- `restrictions` → `notes` — Customers are responsible for managing their own safety while on the river
- `restrictions` → `notes` — If river conditions deteriorate during the journey, your first option should always be to 
- `restrictions` → `notes` — If required due to weather or river conditions, customers may return a day later at no add
- `restrictions` → `health_safety` — All paddlers must wear the provided life jacket / PFD at all times while on the river
- _…and 7 more_

### 480032 — 2 Day Culturally Guided Whanganui River Journey – Ohinepane 

- `inclusions` → `special_requirements` — Fully catered meals, snacks, and drinks are included throughout the journey
- `inclusions` → `special_requirements` — Dietary requirements can usually be accommodated
- `departure_info` → `notes` — The journey concludes at Whakahoro on the second morning
- `departure_info` → `notes` — Pickup is approximately 9:30am at Whakahoro
- `departure_info` → `notes` — Return shuttle transport to Owhango is included
- `departure_info` → `notes` — Estimated arrival back to Owhango is approximately 10:30am – 11:00am
- `important_info` → `disclaimers` — Owhango Adventures is not responsible for loss or damage to personal belongings, valuables
- `important_info` → `disclaimers` — Customers are encouraged to use additional waterproof protection for cameras and electroni
- `important_info` → `disclaimers` — Outdoor adventure activities involve inherent risks including changing weather, river curr
- `restrictions` → `health_safety` — All participants must wear the provided lifejacket / PFD at all times while on the river
- _…and 7 more_

### 480877 — Scuba Experience at Wave Break Island - Perfect for Beginner

- `important_info` → `notes` — Please read the SAFETY INFORMATION below.
- `important_info` → `notes` — 👇 It is important for your safety and enjoyment.
- `important_info` → `notes` — Short notice plan updates may be sent
- `important_info` → `notes` — Wave Break Island is tide-dependent, therefore departure times vary depending on tide time
- `important_info` → `notes` — Although we can predict the tide flow, in-water activity involves other conditions that ar
- `important_info` → `notes` — If trips are cancelled due to weather, please understand this is for safety reasons (yours
- `important_info` → `notes` — We know cancellations can be frustrating but please understand that the weather and sea co
- `important_info` → `notes` — Please be kind and polite to our staff who are only working towards a safe operation.
- `important_info` → `notes` — We have a zero-tolerance policy for rudeness or aggression towards our customers and team.
- `restrictions` → `notes` — no touching, collecting, damaging, feeding or moving marine life.
- _…and 1 more_

### 480930 — Snorkelling | Wave Break Island

- `check_in` → `meeting_point` — Check-in times are the times shown on the booking (eg: for a 6:30 snorkel you need to be a
- `check_in` → `meeting_point` — Please don't show up earlier for trips as we are unable to accommodate guests until the de
- `important_info` → `notes` — Wave Break Island is located within the Gold Coast Broad-water (inshore) and is therefore 
- `important_info` → `notes` — It provides an ideal environment for beginners or for someone who enjoys calm and easygoin
- `important_info` → `notes` — Wave Break Island is tide-dependent, therefore departure times vary depending on tide time
- `important_info` → `notes` — Although we can predict the tide flow, in-water activity involves other conditions that ar
- `important_info` → `notes` — If trips are cancelled due to weather, please understand this is for safety reasons (yours
- `important_info` → `notes` — We know cancellations can be frustrating but please understand that the weather and sea co
- `important_info` → `notes` — Please be kind and polite to our staff who are only working towards a safe operation.
- `important_info` → `notes` — We have a zero-tolerance policy for rudeness or aggression towards our customers and team.
- _…and 33 more_

### 480932 — Snorkel with Turtles at Cook Island Aquatic Reserve

- `check_in` → `meeting_point` — Please arrive at the time shown on your booking
- `check_in` → `meeting_point` — (e.g., for a 6:30 trip, check in by 6:30).
- `check_in` → `meeting_point` — We can’t accommodate early arrivals, but there will be plenty of time to get ready once ch
- `important_info` → `health_safety` — Due to the location of Cook Island, seasickness can be an issue.
- `important_info` → `health_safety` — We recommend taking a seasickness remedy (e.g., Travacalm, Travalcalm HO, or Kwells) 30 mi
- `important_info` → `health_safety` — Bring extra remedies with you — Natural remedies (like ginger) are not as effective.
- `important_info` → `notes` — Gold Coast Dive Centre isn’t responsible for personal items.
- `important_info` → `notes` — Any gear or items brought on the trip are at your own risk.
- `important_info` → `notes` — We are not liable for loss, theft, or damage.
- `important_info` → `notes` — Please check your belongings before leaving.
- _…and 37 more_

### 481445 — Dive with Sea Turtles — Cook Island Half-Day Dive Experience

- `check_in` → `meeting_point` — Please arrive at the time shown on your booking
- `check_in` → `meeting_point` — (e.g., for a 6:30 trip, check in by 6:30).
- `check_in` → `meeting_point` — We can’t accommodate early arrivals, but there will be plenty of time to get ready once ch
- `important_info` → `restrictions` — Cook Island is an open-ocean site.
- `important_info` → `restrictions` — Conditions can vary and may include currents, swells, and winds.
- `important_info` → `health_safety` — Due to the location of Cook Island, seasickness can be an issue.
- `important_info` → `health_safety` — We recommend taking a seasickness remedy (e.g., Travacalm, Travalcalm HO, or Kwells) 30 mi
- `important_info` → `health_safety` — Bring extra remedies with you — Natural remedies (like ginger) are not as effective.
- `important_info` → `disclaimers` — Gold Coast Dive Centre isn’t responsible for personal items.
- `important_info` → `disclaimers` — Any gear or items brought on the trip are at your own risk.
- _…and 54 more_

### 481450 — Milford Sound Cruise | Aboard The Haven

- `check_in` → `notes` — Check in closes 15 minutes prior to departure.
- `check_in` → `notes` — Gate closes 5 minutes prior to departure time
- `important_info` → `health_safety` — Aotearoa New Zealand - Powerful natural forces have shaped Aotearoa New Zealand over milli
- `important_info` → `health_safety` — Earthquakes and volcanoes lifted these beautiful islands out of the Pacific Ocean.
- `important_info` → `health_safety` — They have created the dramatic landscapes we enjoy today.
- `important_info` → `health_safety` — Natural hazards are part of life here.
- `important_info` → `health_safety` — Around 20,000 earthquakes are recorded each year.
- `important_info` → `health_safety` — Most are small and go unnoticed, but larger events can cause damage.
- `important_info` → `health_safety` — Understanding the hazards and how to stay safe is an important part of planning your visit
- `important_info` → `health_safety` — Piopiotahi Milford Sound - Dramatic and ever-changing, Piopiotahi Milford Sound is one of 
- _…and 59 more_

### 481451 — Milford Sound Cruise | Aboard The Mariner

- `check_in` → `notes` — Check-in closes 15 minutes prior to departure.
- `check_in` → `notes` — Gate closes 5 minutes prior to departure.
- `important_info` → `health_safety` — Visitors to Milford Sound should be aware of various natural hazards when going to Milford
- `important_info` → `health_safety` — Aotearoa New Zealand - Powerful natural forces have shaped Aotearoa New Zealand over milli
- `important_info` → `health_safety` — Earthquakes and volcanoes lifted these beautiful islands out of the Pacific Ocean.
- `important_info` → `health_safety` — They have created the dramatic landscapes we enjoy today.
- `important_info` → `health_safety` — Natural hazards are part of life here.
- `important_info` → `health_safety` — Around 20,000 earthquakes are recorded each year.
- `important_info` → `health_safety` — Most are small and go unnoticed, but larger events can cause damage.
- `important_info` → `health_safety` — Understanding the hazards and how to stay safe is an important part of planning your visit
- _…and 60 more_

### 483864 — Accessible Adventures

- `important_info` → `accessibility` — At eFoilgc we believe that adventure should be accessible to all.
- `important_info` → `accessibility` — We aim to break down barriers and empower individuals with disabilities to experience the 
- `important_info` → `accessibility` — We are committed to creating an inclusive environment where everyone can thrive.
- `important_info` → `accessibility` — In this statement, we aim to accurately describe our offering so you can decide if it suit

### 493022 — Broadwater Sunset Cruise

- `what_to_bring` → `important_info` — Pack a warm jumper and a windproof/waterproof jacket as conditions at sea can be windier a
- `what_to_bring` → `important_info` — Life is bright, you gotta have shades!
- `what_to_bring` → `important_info` — You may bring a camera, mobile phone, etc.
- `what_to_bring` → `important_info` — However, since you may be splashed with ocean spray, please bring these items at your own 
- `location` → `important_info` — Aqua Adventure Centre, 95 Marine Parade, Southport 4215
- `location` → `important_info` — Once you arrive at the Aqua Adventures Centre, please meet the Spirit Team outside of the 
- `location` → `important_info` — Our meeting location is on the grass, on the left-hand-side of the Broadwater Cafe.
- `location` → `important_info` — Aqua Adventure Centre, 95 Marine Parade, Southport 4215.
- `location` → `important_info` — https://maps.app.goo.gl/iV6RH53DJCDtHuUT9
- `location` → `important_info` — Driving from North/Brisbane - Take the Pacific Motorway (M1) southbound and exit at Smith 
- _…and 17 more_

### 507729 — Te Araroa Trail – Freedom Hire Canoe Journey | Whakahoro to 

- `departure_info` → `before_arrival` — Option 1 – Continue Walking to Whakahoro
- `departure_info` → `before_arrival` — Continue hiking from National Park / Waimarino to Whakahoro over the following days.
- `departure_info` → `before_arrival` — We will meet you at Whakahoro with:
- `departure_info` → `before_arrival` — At Whakahoro we will:
- `departure_info` → `before_arrival` — Conduct a full safety briefing
- `departure_info` → `before_arrival` — Assist with packing dry barrels
- `departure_info` → `before_arrival` — Explain river logistics and safety procedures
- `departure_info` → `before_arrival` — Provide river maps and tide information
- `departure_info` → `before_arrival` — You will then begin your self-guided Whanganui River Journey.
- `departure_info` → `before_arrival` — Option 2 – Shuttle Back to Owhango
- _…and 17 more_

### 509806 — Glass Bottom boat Night Tour

- `location` → `notes` — Meet at Shute Harbour Marine Terminal (15 minute drive from Airlie Beach)
- `location` → `notes` — If you selected meet us at Shute Harbour please meet at marine terminal building 15 minute
- `restrictions` → `notes` — All guests need to be Physically fit enough to get on the boat unaided no strollers or wal

### 512675 — Half Day Te Awa River Ride

- `restrictions` → `special_requirements` — Participants must be confident riding a bike independently.
- `restrictions` → `special_requirements` — All participants must follow safety instructions and wear provided safety equipment where 
- `restrictions` → `special_requirements` — All safety briefings and instructions provided by Riverside Adventures staff must be follo
- `restrictions` → `special_requirements` — If wanting to upgrade from Standard Mountain bike to eBike, do get in touch.
- `other` → `itinerary` — Bike induction for RAW mountain bike or e-bike hires.
- `other` → `highlights` — Scenic riverside riding along the Waikato River.
- `other` → `highlights` — The Cambridge Art Precinct with unique sculptures and public art.
- `other` → `highlights` — Riding through the charming Cambridge township cafés and river paths.
- `other` → `highlights` — Boardwalk and lakeside trail sections.
- `other` → `highlights` — Finishing at beautiful Lake Karapiro and Mighty River Domain.
- _…and 7 more_

### 516920 — Scattering of Ashes at Sea

- `check_in` → `notes` — Please arrive 10 minutes before your scheduled departure time.
- `other` → `disclaimers` — Epic Marine Charters - Busselton Cruises promotes itself as a safe, fun, friendly and fami
- `other` → `disclaimers` — It also is conscious of the environment and areas in which it operates.
- `other` → `disclaimers` — We will never intentionally put the vessel, crew, passenger, public or environmental safet
- `other` → `disclaimers` — As such passengers acknowledge that at the sole discretion of Epic Marine Charters - Busse
- `other` → `disclaimers` — Epic Marine Charters - Busselton Cruises reserves the right to alter prices, schedules or 
- `other` → `disclaimers` — Our Vessel “Equador” is bound to comply with strict regulations and enforce maximum 30 pas
- `other` → `disclaimers` — All passengers/ guests release Elswood Pty Ltd (trading as Epic Marine Charters - Busselto
- `other` → `disclaimers` — Activities include but are not limited to, access to jetties, wharves, or access areas, em
- `other` → `disclaimers` — It is the sole responsibility of passengers to ensure their own safety, behaviour and cond
- _…and 16 more_

### 540779 — Dive Cook Island at Night – Dusk & Night Double Dive

- `check_in` → `meeting_point` — Please arrive at the time shown on your booking (e.g., for a 3:00 trip, check in by 3:00).
- `check_in` → `meeting_point` — We can’t accommodate early arrivals, but there will be plenty of time to get ready once ch
- `restrictions` → `notes` — Certified divers must bring proof of certification (physical or digital), showing: Your fu
- `restrictions` → `notes` — Open Water), the certifying agency (e.g.
- `restrictions` → `notes` — SSI, PADI) Logbooks are not accepted.
- `restrictions` → `notes` — If you’re SSI certified and can’t find your card, contact us at least 24 hours in advance,
- `restrictions` → `notes` — We can only verify SSI certifications.
- `restrictions` → `notes` — No proof = no diving = no refund.
- `restrictions` → `notes` — You’ll carry your own gear from the trailer to the boat (approx.
- `restrictions` → `notes` — After the trip, return and rinse the gear you used — your help is appreciated!
- _…and 33 more_

### 553708 — Night Dive | Scottish Prince 1887

- `important_info` → `notes` — Please read the SAFETY INFORMATION below.
- `important_info` → `notes` — 👇 It is important for your safety and enjoyment.
- `important_info` → `notes` — Short-notice plan updates may be sent
- `important_info` → `notes` — Cook Island is one of the most weather-dependent sites on Australia's east coast, we patie
- `important_info` → `notes` — If trips are cancelled due to weather, please understand this is for safety reasons (yours
- `important_info` → `notes` — We know cancellations can be frustrating but please understand that the weather and sea co
- `important_info` → `notes` — Please be kind and polite to our staff who are only working towards a safe operation.
- `important_info` → `notes` — We have a zero-tolerance policy for rudeness or aggression towards our customers and team.
- `important_info` → `health_safety` — Cook Island's position is just south of the often treacherous Tweed River Bar.
- `important_info` → `health_safety` — We strongly recommend taking a seasickness remedy 30 minutes before boarding (as well as t
- _…and 25 more_

### 567501 — Pony Party

- `important_info` → `notes` — Please Note Waiver Form issued via email will only be for 1st participant
- `important_info` → `notes` — Additional Waiver Forms for guests available via link https://mono.wherewolf.co.nz/b2tqdk

_…and 32 more products with movement._