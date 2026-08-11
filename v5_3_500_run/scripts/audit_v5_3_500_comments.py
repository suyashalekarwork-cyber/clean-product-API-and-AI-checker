"""
Hand-verified verdicts for the V5.3 500-product run.

Method, stated plainly: 500 products cannot be read line by line. Every defect
class found in the 100-product HAND audit was turned into a detector
(detect_v5_3_issues.py), those detectors were checked back against the 100 where
the answers are known, then run over all 499. Every product they flagged was
then opened and read against its raw description -- the verdicts below are that
reading, not the detector's output. Several detector hits were overturned as
false positives and are recorded as such.

So: the 28 flagged products are hand-verified. The 471 unflagged are
"none of the known defect classes fired", which is weaker than "read and
confirmed correct". A defect class that never appeared in the first 100 would
not be caught here.

Verdict codes match audit_v5_3_comments.py (the 100-product audit).
"""

AUDIT = {
    # ================= REAL CONTENT LOSS -- 3 products =================
    "371805": ("CONTENT_LOSS",
               "Lost 'Powered by a 250HP Yamaha 4.2 L engine, with a maximum cruising speed of 49 "
               "knots.' The sentence before it survived, so the boat spec reads as truncated. "
               "REPRODUCED IN BOTH RUNS -- the only content loss that is repeatable rather than "
               "random, which makes it the one a prompt rule could actually fix."),
    "535701": ("CONTENT_LOSS",
               "Lost two lines of the meal detail: 'Currently the light meal menu is a BBQ with "
               "choice of a delicious ground beef hamburger or two tasty beef sausages or a gourmet "
               "vegetarian patty...' and 'Please order your protein at the time of booking.' The "
               "second is an instruction the customer has to act on at booking time."),
    "293135": ("CONTENT_LOSS",
               "Lost the opening tagline '#Hire the Gold Coast One!' -- verified absent from every "
               "column. Same class as the Woolamai tagline that V5.3 was written to fix, so the "
               "STEP 1B rule did not hold here."),

    # ================= DUPLICATION -- 2 products =================
    "509794": ("SUPPLIER",
               "RECLASSIFIED (user ruling 2026-08-11). '3.5 hrs cruising the beautiful Sydney "
               "Harbour waterways' is in both duration_text and what_included -- but VERIFIED it "
               "appears TWICE in the supplier's own raw description, once under Duration and once "
               "under 'Included in your package'. We reproduced their data faithfully. Not an "
               "extraction defect. De-duplicate at render time if the repeat looks odd on the page."),
    "203555": ("SUPPLIER",
               "RECLASSIFIED (user ruling 2026-08-11). 'Giant stand up paddle board hire for up to "
               "8 people' is in both highlights and what_included -- VERIFIED it appears TWICE in "
               "the raw, under 'HIGHLIGHTS:' and again under \"WHAT'S INCLUDED?\". The supplier "
               "wrote it twice; we cannot invent a reason to drop one. Not an extraction defect."),

    # ================= MISCLASSIFICATION -- 5 products =================
    "156525": ("SUPPLIER",
               "USER-RAISED. what_to_bring holds three lines that are not things to bring: 'Note: "
               "Please advice us of health or mobility issues', 'Subject to weather conditions', "
               "'Not Available Christmas Day, public holidays or January 1st to 3rd'. The supplier "
               "filed them under 'What to bring' and heading-gating obeyed the label. This is the "
               "case for extending the line test to what_to_bring as the third point-wise column."),
    "327258": ("SUPPLIER",
               "The sharpest version of the 156525 problem: the WHOLE what_to_bring section says "
               "'Salt Spray Surf School provides all surfboards needed for these days, wetsuits are "
               "provided if need be.' -- i.e. what you do NOT need to bring. A customer reading a "
               "What to Bring box that lists things they don't need is actively misled."),
    "500245": ("SUPPLIER",
               "what_to_bring ends with 'In the event of being overweight on the day and outside of "
               "the vessel's advertised weight limit, the vessel will not be allowed to depart, the "
               "hire will be cancelled and all monies forfeited.' That is a cancellation term, not "
               "a packing item. Same class as 156525."),
    "466438": ("MISCLASS",
               "restrictions holds 'Level: Hard' -- a difficulty rating, not a limit on who may "
               "participate. Belongs in about. No rule currently covers difficulty ratings."),
    "491113": ("MISCLASS",
               "restrictions holds the single word 'Moderate', from a 'Difficulty' heading. A "
               "Restrictions section reading only 'Moderate' tells the customer nothing. Same class "
               "as 466438."),

    # ================= LABEL LOSS -- 3 products =================
    "713497": ("LABEL_LOSS",
               "The heading '💲 HIRE COSTS - 2 Seater Canoes' was dropped. VERIFIED the content "
               "under it survived -- '1 hour $30.00', 'fibreglass or plastic' and the rest are all "
               "in pricing. Nothing lost; the section just has no title of its own."),
    "324361": ("LABEL_LOSS",
               "'Exclusions: n/a' lost its label. The value is trivial ('n/a'), so this is "
               "cosmetic."),
    "697755": ("LABEL_LOSS",
               "Two inline labels stripped -- 'cancellation_summary: Free cancelation' and "
               "'meeting_point: Standley Chasm camping area'. Both values survived in their proper "
               "columns, so nothing is lost."),

    # ================= MINOR -- 2 products =================
    "198064": ("MINOR",
               "what_included briefly held 'An experience you'll never forget!' -- marketing, not a "
               "deliverable. The model self-flagged it and moved it to about, so this is the line "
               "test working; recorded only for completeness."),
    "501920": ("MINOR",
               "extras includes 'Designed to make your day on the water safe and easy' -- marketing "
               "swept in with the genuine 'Optional services' items."),

    # ================= SUPPLIER-SIDE -- not model defects =================
    "249729": ("SUPPLIER", "The skipper paragraph appears twice in the supplier's OWN raw text and "
                           "is preserved faithfully. De-duplicate at render time."),
    "330482": ("SUPPLIER", "Supplier repeats 'All new Kalbarri Bar-B-Cruiser - Party Pontoon Hire.' "
                           "and several lines in its own raw text; preserved faithfully."),
    "279178": ("SUPPLIER", "Supplier's raw description repeats itself; preserved faithfully."),
    "444088": ("SUPPLIER", "Supplier's raw description repeats itself; preserved faithfully."),
    "397465": ("SUPPLIER", "Supplier's raw description repeats itself; preserved faithfully."),
    "319096": ("SUPPLIER", "Supplier's raw description repeats itself; preserved faithfully."),
    "171361": ("SUPPLIER", "Supplier's raw description repeats itself; preserved faithfully."),
    "680927": ("SUPPLIER", "All columns empty -- the supplier wrote headings with no content under "
                           "any of them. Nothing to extract; correct behaviour, ignore in scoring."),

    # ================= found during the no-heading review =================
    "251713": ("MISCLASS",
               "DEBATABLE. cancellation holds 'The tour must depart at your booked time. No shows "
               "will result in a forfeit of tour costs.' The supplier's heading above it is "
               "'Note:', which maps to important_info -- so the model routed on CONTENT, not on "
               "the heading. The answer is arguably better (it genuinely is a no-show forfeit "
               "term), but content overriding a heading is the one thing the V5 gate exists to "
               "prevent. Worth watching rather than fixing."),
    "266189": ("SUPPLIER",
               "The supplier's ENTIRE raw description is the string 'meeting_point: Te Anau' -- a "
               "field name pasted into the description box. The model read it as an inline "
               "Label: value and filed it under meeting_point. Faithful; nothing else it could "
               "sensibly do. Supplier data accident, not an extraction defect."),

    # ========== found by the SECOND, independent audit; verified and accepted ==========
    "634003": ("MISCLASS",
               "HIGH. The raw has two labelled lists -- 'Departure times' (Cairns Airport 2:30 PM, "
               "Cairns Base Hospital 2:45 PM, Cairns Central 2:55 PM) and 'Arrival times' (Mission "
               "beach 5:30 PM). BOTH labels were dropped and the two lists merged into one about "
               "block, so Mission Beach 5:30 PM now reads as a fourth pickup point. The first "
               "audit missed this: its detector only flags text ABSENT from the output, and here "
               "every value survived -- only the labels went."),
    "639882": ("MISCLASS",
               "MEDIUM. Sub-labels 'Scenic Landscapes:', 'Wildlife Encounters:' and 'Dress Code:' "
               "were all dropped -- verified absent. highlights now reads as unattributed "
               "paragraphs. Same defect class as the SSAA tier labels V5.3 was written to fix."),
    "587626": ("OK",
               "REVIEWED AND SET ASIDE (2026-08-11). The model returned the key "
               "'redo_desc_group_size' instead of 'redo_group_size' -- the only schema deviation "
               "in 499 products. Recorded here because it happened, but NOT counted as a defect: "
               "the value is empty, so no data is affected. If a loader ever keys strictly on the "
               "schema it should validate names and fail loudly rather than rely on this staying "
               "harmless."),

    # ===== supplier problems found by the broad raw-text scan (scan_supplier_data_issues.py) =====
    "564767": ("SUPPLIER", "NO DESCRIPTION. The entire raw is 'Artisan Maker Shed Membership' -- "
                           "the product name and nothing else. No prompt version can fix this; the "
                           "page will render with a one-line About."),
    "531290": ("SUPPLIER", "NO DESCRIPTION. The entire raw is '30 or 60 min Jet Ski Tour'."),
    "598043": ("SUPPLIER", "NO DESCRIPTION. The entire raw is '2 to 8 hours!'."),
    "417608": ("SUPPLIER", "Near-duplicate in the raw -- a line pasted and then lightly edited, so "
                           "exact matching missed it. Preserved faithfully."),
    "442752": ("SUPPLIER", "A control character is embedded in the raw text (this is the one that "
                           "broke the Excel build). Extraction was unaffected."),
    "328897": ("SUPPLIER", "'n/a' left in the raw as a placeholder the supplier never filled."),

    # ================= detector hits OVERTURNED on reading =================
    "210832": ("OK", "Detector flagged 'About The Christmas in July Dinner Train' as lost. "
                     "OVERTURNED: it is an About heading naming the product -- a label, and the "
                     "journey description beneath it survived."),
    "702571": ("OK", "Detector flagged 'What can you expect?' as lost. OVERTURNED: a question used "
                     "as a section heading, and the block it introduces survived."),
    "278798": ("OK", "Detector flagged 'What do I need to bring?' as lost. OVERTURNED: question "
                     "heading; the bring-list beneath it is intact in what_to_bring."),
    "425749": ("OK", "Detector flagged 'Thank you and safe cycling!' as lost. OVERTURNED: a "
                     "sign-off. The prompt explicitly permits omitting greetings and sign-offs."),
    "402465": ("OK", "Detector flagged the markdown waitlist CTA link as lost. OVERTURNED: a "
                     "booking link, not product description content."),
}

DEFAULT = ("OK", "None of the known defect classes fired: no duplication, no unaccounted-for text, "
                 "pricing/cancellation definitions respected, no difficulty rating in restrictions, "
                 "no non-item lines in what_to_bring. Not individually hand-read -- see the method "
                 "note at the top of this report.")


def verdict(pid):
    return AUDIT.get(pid, DEFAULT)
