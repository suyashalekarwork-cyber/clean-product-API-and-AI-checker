"""
Hand verdicts for the BOOKING V5.3 100-product run.

Method: 43 products had something flagged; each was opened and read against its
raw booking notes. The other 57 are at 100% retention with nothing flagged. As
in every previous run, a large share of the flags were MY detector, not the
model -- those are recorded as OK with the reason, so nobody re-investigates
them.

Verdict codes:
  CONTENT_LOSS  raw text that reached no column
  URL           a link destroyed or altered
  DUPLICATION   the same sentence in 2+ columns (reported, never removed)
  MINOR         cosmetic
  OK            checked, no defect -- includes flags overturned as artifacts
  WORKING       a behaviour change that is the new rules working as designed
"""

AUDIT = {
    # ================= CONTENT LOSS -- 9 products =================
    "478478": ("CONTENT_LOSS",
               "Worst in the run (retention 82.4%). The supplier runs THREE paddle "
               "variants -- Lunch (10.30), Dinner Oct-Mar (4.30pm), Dinner Apr-Sep "
               "(3.00pm) -- whose text is near-identical apart from the time. "
               "departure_info kept one; 12 units from the others reached no column, "
               "including the seal-approach regulations and 'Please follow Sam's "
               "instructions at all times'. A customer on the April date sees the "
               "wrong meeting time."),
    "481445": ("CONTENT_LOSS",
               "SAFETY content lost: the entire '11. Boating Etiquette' list -- always "
               "wear your life jacket when instructed, stay seated when the boat is in "
               "motion, maintain three points of contact, stay clear of running "
               "engines, pay attention to the safety briefings. 8 units. This is "
               "exactly the class health_safety was added to capture."),
    "701630": ("WORKING",
               "CORRECTED after verifying against the raw. First reported as content "
               "loss on a retention figure of 86.3%; it is not. All seven numbered "
               "sections ARE present and correctly routed, each with its label kept: "
               "'1. Booking & Payment' -> pricing, '2. Cancellations & Refunds' -> "
               "cancellation, '3. Weather & Skipper's Discretion' -> important_info, "
               "'4. Safety & Compliance' -> health_safety, '6. Alcohol, Drugs & "
               "Behaviour' -> restrictions, '8. Liability & Risk' -> disclaimers. Only "
               "the enumeration numbers were dropped, which carry no information once "
               "the heading text is kept. This is one of the BEST results in the run -- "
               "a bare T&C document split correctly across six of the ten new columns. "
               "The detector fired because '1. Booking & Payment' != 'Booking & "
               "Payment:'; all seven scored 90-96% fuzzy, i.e. present."),
    "211166": ("CONTENT_LOSS",
               "Retention 86.8%, and the markdown handling is the cause. Two URLs "
               "destroyed, two inventions produced from image syntax "
               "('Description of image (https://cdn.filestackcontent.com/...)'), and "
               "five units lost around the finish-point block. Image markdown "
               "(![alt](url)) is not covered by the link rule and is being mangled."),
    "403385": ("CONTENT_LOSS",
               "Two lines under 'ITINERARY/YOUR INPUT' reached no column: 'We can take "
               "you to Chandon instead for lunch but this is all at your own expense' "
               "and 'We can always stop at Chandon for a quick photo.' Both are real "
               "customer options."),
    "254882": ("CONTENT_LOSS",
               "The itinerary's closing line lost -- 'From 12:30pm - Arrive back at "
               "Riverside Adventure Base. We recommend grabbing a bite to eat prior to "
               "your Twilight Kayak'. Also 4 duplications (notes vs highlights, "
               "what_to_bring, special_requirements, important_info)."),
    "743218": ("CONTENT_LOSS",
               "Under 'Day 1 - Great Barrier Reef Tour with Evolution', the operator "
               "line '- Operator: Down Under Cruise & Dive' reached no column. Only "
               "notes filled on a 13-heading product, which is itself worth a look."),
    "582607": ("MINOR",
               "Verified absent, but the lost text is the single word 'Agreement' "
               "under a 'Code of Conduct' heading -- a section-title fragment carrying "
               "no information of its own. Downgraded from CONTENT_LOSS on that basis. "
               "The Code of Conduct content itself survived."),
    "100271": ("CONTENT_LOSS",
               "'New Customers: Please email info@perthkitchenhire.com.au to request a "
               "day/time that suits you' reached no column. Note 100273 is the SAME "
               "supplier with the SAME sentence and there it survived (reworded) -- so "
               "this is the non-determinism CLAUDE.md already documents, not a "
               "systematic rule failure."),

    # ================= URL -- 4 products =================
    "427365": ("URL",
               "A URL was ALTERED: raw has 'https://www.transport.wa.gov.au/licensing/"
               "identity/...', output has the same path without 'www.'. A broken "
               "government licensing link is worse than a missing one because it looks "
               "valid. The V5.3 link rule stopped 66 of 72 URL losses but not this "
               "class of silent edit."),
    "272826": ("URL",
               "'https://www.tiakinewzealand.com/en_NZ/' reached no column. Same "
               "supplier and same URL as 569893 and 569896."),
    "569893": ("URL", "Same tiakinewzealand.com loss as 272826."),
    "569896": ("URL", "Same tiakinewzealand.com loss as 272826."),

    # ================= DUPLICATION -- 6 products =================
    "478480": ("DUPLICATION",
               "Worst duplication in the run: 5 sentences in both notes and "
               "departure_info -- the Point Piper Kayaks note, 'I will meet you at the "
               "eastern end of the beach', the parking line and the toilets note. "
               "Reported, not removed, per the post-processing rule."),
    "701258": ("DUPLICATION",
               "3 sentences in both what_to_bring and disclaimers, including 'Please be "
               "sure to arrive a minimum of 20 minutes prior to departure' and the "
               "check-in/gate-closing line."),
    "553708": ("DUPLICATION",
               "'It is important for your safety and enjoyment.' in notes and "
               "health_safety."),
    "595531": ("DUPLICATION", "Same sentence and same supplier as 553708."),
    "512675": ("DUPLICATION",
               "'Return Shuttle from Mighty River Domain to Cambridge Town Hall.' in "
               "what_included and itinerary. Defensible -- it is both -- but the rule "
               "says one column."),
    "580166": ("DUPLICATION",
               "Address duplicated across notes and meeting_point, plus one invention "
               "from image markdown ('Description of image (https://cdn...)') -- the "
               "same ![alt](url) handling gap as 211166."),

    # ================= MINOR -- 3 products =================
    "108022": ("MINOR",
               "A markdown character survived into notes. Also flagged 3 losses, all "
               "branding fragments ('Shakas', 'Aotearoa Surf Team', 'Aotearoa Surf "
               "School and Shop: School. Camps. Shop.') -- droppable under RULE 2."),
    "109135": ("MINOR", "Identical to 108022, same supplier."),
    "282368": ("MINOR", "A markdown character survived into notes. Nothing else."),

    # ========= WORKING AS DESIGNED -- the new rules, verified =========
    "631971": ("WORKING",
               "THE FLAGSHIP CASE for the nesting rule. Raw is '##Additional "
               "Information' followed by 17 bold sub-labels (Scheduling, Sign-in, "
               "Waiver, Location, Food, Footwear, Hat, Shorts, T-Shirt, Warm Top, PFD, "
               "Sun cream, Towel, Secure gear bag, Dry clothes, Refunds, Weather). V5 "
               "re-routed those into six columns. V5.3 correctly keeps ALL of it in "
               "notes with every label preserved -- 'Additional Information: "
               "Scheduling: In general camps are 3 days long 9.30-3pm...'. The outer "
               "heading wins, exactly as ruled. The 3 'reworded' flags are my matcher "
               "comparing raw bold markup against label-joined output."),
    "701591": ("WORKING",
               "Collapsed to disclaimers only. The raw is a bare numbered T&C document "
               "with no operational headings, so there is nothing else to fill. The "
               "gate declining is correct."),
    "582607_ok": ("WORKING",
                  "notes emptied into health_safety and disclaimers -- the intended "
                  "drain of the catch-all into the new columns."),

    # ========= OVERTURNED -- flagged by a detector, verified correct =========
    "187067": ("OK",
               "Flagged item-as-heading: departure_info = 'Departure Time: 6.00am'. "
               "OVERTURNED -- a STEP 1D inline label, correctly routed. Same false "
               "positive as in the V5 run."),
    "483864": ("OK",
               "Flagged mid-sentence: accessibility begins 'eFoilgc Access Statement: "
               "At eFoilgc we believe that adventure should be accessible to all'. "
               "OVERTURNED -- that is STEP 1C label-joining working; the value starts "
               "with its own label."),
    "381162": ("OK",
               "Flagged itinerary line test: 'Finish.: Complete your ride back at "
               "Mighty River Domain'. OVERTURNED -- 'Finish' is a named stop in a "
               "stated order, which the line test accepts."),
    "282594": ("OK",
               "Flagged itinerary line test: 'Approximate schedule:'. OVERTURNED -- a "
               "lead-in that introduces the lines beneath it. The 'How to find us: I'm "
               "looking forward to diving with you soon!' loss is a sign-off; my "
               "pleasantry filter matches 'we look forward' but not 'I'm looking "
               "forward'."),
    "278797": ("OK",
               "Both flags overturned. The loss is the sign-off 'I'm looking forward "
               "to diving with you soon!' and a staff signature block. The two "
               "'reworded' entries are markdown links being label-joined."),
    "283352": ("OK", "Identical pattern to 278797, same supplier."),
    "478466": ("OK",
               "Flagged loss: 'Important Note: Looking forward to paddling with you.' "
               "OVERTURNED -- a sign-off, droppable under RULE 2."),
    "540779": ("OK",
               "Flagged loss: 'We can't wait to welcome you to the water!' "
               "OVERTURNED -- a sign-off."),
    "734654": ("OK",
               "Flagged loss: 'Ka mihi,' -- a Maori sign-off, with the team signature "
               "as the reworded entry. OVERTURNED. My pleasantry filter has no Maori "
               "sign-offs; worth adding."),
    "736363": ("OK", "Identical to 734654, same supplier."),
    "347817": ("OK",
               "Flagged reworded: 'WEATHER CHECK - ESSENTIAL INFORMATION: Please be "
               "ready on time...'. OVERTURNED -- the label was joined per STEP 1C, "
               "which is what changed the string."),
    "100273": ("OK",
               "Flagged reworded on the same sentence 100271 lost. Here it survived. "
               "Retention 100%."),
    "187073": ("OK", "Nothing flagged. 100% retention."),
}

DEFAULT = ("OK", "Nothing flagged and 100% retention. Not individually hand-read "
                 "unless listed above -- see the method note at the top of this "
                 "report.")


def verdict(pid):
    return AUDIT.get(pid, DEFAULT)
