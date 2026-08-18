"""
Verdicts for the V5.3 random-1,000 run.

Method: the detectors from detect_v5_3_issues.py flagged 48 products; each was
then opened and read against its raw description. The content-loss flags in
particular needed judgement -- 16 were flagged, 9 turned out to be headings,
markdown links or sentence-splitting artifacts, and 7 are real.

Verdict codes match the earlier runs.
"""

AUDIT = {
    # ============ REAL CONTENT LOSS -- 7 products ============
    "379566": ("CONTENT_LOSS",
               "The worst in this run: FIVE sentences of the tour narrative gone -- the guide's "
               "historic journey through the sugar-cane pioneering days, the miniature mill and "
               "distillery section, the rum and fruit-liqueur tastings, the senses paragraph, and "
               "'We encourage any questions throughout the tour!'. Most of what the customer would "
               "read about this tour is missing."),
    "473738": ("CONTENT_LOSS",
               "Four lines of the operator's pitch gone, including 'On this tour, it is US "
               "[the owner/operators] who you will be with, as we don't have staff or guides' -- "
               "the product's main differentiator."),
    "312267": ("CONTENT_LOSS",
               "Two sentences of the trek description dropped: the rendezvous/fit-out step and "
               "'Once at our start point, it's time for a safety brief and to ensure our packs are "
               "snug.'"),
    "334469": ("CONTENT_LOSS",
               "Two sentences dropped, including 'Gerard has over 30 years of NT fishing "
               "experience and uses top quality fishing gear' -- the operator's credentials."),
    "677151": ("CONTENT_LOSS",
               "Dropped 'This includes but is not limited to: apps on mobile devices, Ouija "
               "boards, pendulums, video and...' -- the specific list of what is not permitted. A "
               "restriction the customer needs."),
    "293942": ("CONTENT_LOSS",
               "Dropped 'Stargazing in the heart of the Australian outback is an experience not to "
               "be missed' plus a closing sign-off. The first is real description."),
    "709956": ("CONTENT_LOSS",
               "Dropped 'Join us for a delightful day of steam and scenery.' plus a booking CTA. "
               "Minor -- the CTA is fair to drop, the first sentence is not."),

    # ============ MISCLASSIFICATION -- 6 products ============
    "466749": ("MISCLASS",
               "restrictions holds 'Difficulty: Physical-Intermediate / Technical...' -- a "
               "difficulty rating, not a limit on who may participate. Same class as 466438/491113 "
               "in the 500-run; the rule gap is confirmed at scale."),
    "491110": ("MISCLASS", "restrictions holds the single word 'Advanced' -- a difficulty rating."),
    "499675": ("MISCLASS", "restrictions holds 'Difficulty: Hard' -- a difficulty rating."),
    "328656": ("SUPPLIER",
               "what_to_bring holds 'We supply all safety gear I.e. helmets and goggles' -- what "
               "the supplier PROVIDES, filed under their own What-to-bring heading. Same class as "
               "327258 in the 500-run."),
    "343467": ("SUPPLIER",
               "what_to_bring holds 'Please note, that you will have to provide your own "
               "transport...' -- a travel instruction, not a packing item. Supplier's own heading."),
    "500250": ("SUPPLIER",
               "what_to_bring ends with the overweight/cancellation term. Identical wording to "
               "500245 and 500246 in the 500-run -- the same supplier repeating the same mistake "
               "across their whole product range."),

    # ============ LABEL LOSS -- 2 products ============
    "255272": ("LABEL_LOSS",
               "'Group Size: Min 6, Max 8 People' lost its label; the value survived."),
    "510622": ("LABEL_LOSS",
               "'Sunscreen: Provided if needed.' lost its label; the value survived."),

    # ============ SUPPLIER: raw repeats itself -- verified, all 9 ============
    "106181": ("SUPPLIER", "'07:30am meet at beach' appears twice in the supplier's own raw text."),
    "140896": ("SUPPLIER", "'Bottled water' appears twice in the raw."),
    "203414": ("SUPPLIER", "'There is no maximum length of stay' appears twice in the raw."),
    "328412": ("SUPPLIER", "The multi-lesson discount line appears twice in the raw."),
    "407901": ("SUPPLIER", "'Set up and ready for your arrival' appears twice in the raw."),
    "412512": ("SUPPLIER", "'Booking fees can be avoided by calling...' appears twice in the raw."),
    "59230":  ("SUPPLIER", "'Qualified and professional pilot' appears twice in the raw."),
    "692040": ("SUPPLIER", "'Link to accommodation' appears twice in the raw."),
    "97594":  ("SUPPLIER", "Testimonial header repeated -- two testimonials, each with its own "
                           "header. Legitimate supplier structure, preserved faithfully."),
    "97614":  ("SUPPLIER", "Testimonial header repeated, same as 97594."),

    # ============ detector hits OVERTURNED on reading -- 9 ============
    "275303": ("OK", "Flagged as lost: '##Certification required: *ADV - 30m* and Nitrox'. "
                     "OVERTURNED -- a markdown heading; the content beneath it survived."),
    "337441": ("OK", "Flagged as lost: two markdown links to feedback PDFs. OVERTURNED -- links, "
                     "not description content."),
    "366299": ("OK", "Flagged as lost: '**Return Time:** Approx.'. OVERTURNED -- a sentence-split "
                     "artifact on the abbreviation; the time itself survived."),
    "366334": ("OK", "Flagged as lost: two inline 'Label: value' lines. OVERTURNED -- the values "
                     "survived in their columns."),
    "372587": ("OK", "Flagged as lost: 'Day 1 - Theory and Confined Water Session' / 'Day 2 - Open "
                     "Water Sessions'. OVERTURNED -- itinerary headings, content beneath survived."),
    "467115": ("OK", "Flagged as lost: 'What are the advantages...'. OVERTURNED -- a question used "
                     "as a section heading."),
    "480877": ("OK", "Flagged as lost: 'Trip Breakdown (Approx.'. OVERTURNED -- sentence-split "
                     "artifact on the abbreviation."),
    "560660": ("OK", "Flagged as lost: 'My Story Creates.'. OVERTURNED -- a brand fragment, not "
                     "description content."),
    "572930": ("OK", "Flagged as lost: 'Blue Mountains Gin Company LIQW880015803'. OVERTURNED -- a "
                     "liquor licence number, carried in the raw for compliance."),
}

DEFAULT = ("OK", "None of the known defect classes fired: no duplication, no unaccounted-for text, "
                 "pricing/cancellation definitions respected, no difficulty rating in restrictions, "
                 "no non-item lines in what_to_bring. Not individually hand-read -- see the method "
                 "note at the top of this report.")


def verdict(pid):
    return AUDIT.get(pid, DEFAULT)
