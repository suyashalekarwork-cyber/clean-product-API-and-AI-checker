"""
Single source of truth for the 28 redo_* field names and their definitions,
shared by build_judge_batches.py (prompt construction) and
score_judge_verdicts.py (verdict validation).

Definitions are lifted from the extraction prompts that PRODUCED these fields
(SYSTEM_PROMPT_FH_DESC_V2 / SYSTEM_PROMPT_FH_BOOKING_V2 in
config/fareharbor_prompts.txt) so the judge is held to the same rules the
extractor was given. Do not reword these without re-checking that file.
"""

# Ordered exactly as they appear in v50_post_fix_state.json field_values.
FIELD_DEFINITIONS = {
    # --- from desc_about (marketing/sales copy) ---
    "redo_desc_about": (
        "General descriptive/marketing prose about what the experience IS. "
        "Catch-all for the overview paragraph."
    ),
    "redo_desc_highlights": (
        "Specific, concrete selling points that would make a customer choose THIS "
        "experience -- unique features, standout moments, named attractions, awards. "
        "NOT generic marketing filler ('unforgettable experience'), which belongs in "
        "redo_desc_other or redo_desc_about."
    ),
    "redo_desc_what_included": (
        "Items, services or amenities provided at no extra cost (also 'Journey "
        "Inclusions', 'Package Inclusions', 'Tour Includes')."
    ),
    "redo_desc_what_excluded": (
        "Items, services or costs explicitly NOT included in the base price -- 'at "
        "your own expense', 'not included', 'extra charge'. Optional paid add-ons "
        "belong here."
    ),
    "redo_desc_itinerary": (
        "A time-based or step-by-step sequence of events DURING the experience. Must "
        "have time signals ('9am', 'Day 1', 'then', 'next') OR named stops in a clear "
        "order. A list of OPTIONS (Option A/B/C) is NOT an itinerary. A general "
        "marketing paragraph is NOT an itinerary."
    ),
    "redo_desc_what_to_bring": (
        "Things the customer must bring or wear."
    ),
    "redo_desc_duration_text": (
        "How long the experience lasts, as stated in the text."
    ),
    "redo_desc_requirements": (
        "Restrictions on WHO can participate or what they MUST do/have -- age limits, "
        "height/weight minimums, health warnings, fitness level. If it merely describes "
        "or recommends, it is redo_desc_other, not requirements."
    ),
    "redo_desc_cancellation": (
        "Refund rules, cancellation windows, weather/no-show policy."
    ),
    "redo_desc_check_in": (
        "What to DO on arrival -- present ticket, sign waiver, go to reception, meet "
        "the guide. About ACTIONS on arrival."
    ),
    "redo_min_age": (
        "Minimum age only, as a short value (e.g. '6 years'). Not a full sentence of "
        "requirements text -- that is redo_desc_requirements."
    ),
    "redo_max_age": (
        "Maximum age only, as a short value."
    ),
    "redo_group_size": (
        "Group size / participant count limits (min or max people)."
    ),
    "redo_meeting_point": (
        "The named place where customers meet before the activity starts."
    ),
    "redo_desc_other": (
        "Legitimate catch-all for description content fitting no field above: pricing "
        "tables, opening hours, booking instructions, supplier background, reviews, "
        "general info. Content here is CORRECT only if it genuinely fits no named "
        "field -- if a named field exists for it, that is WRONG_FIELD."
    ),
    # --- from booking_notes (post-booking operational text) ---
    "redo_booking_what_to_bring": (
        "Items to bring or wear, from the operational booking notes."
    ),
    "redo_booking_what_not_to_bring": (
        "Items explicitly prohibited or told not to bring."
    ),
    "redo_booking_inclusions": (
        "Items or services provided at no extra cost ('We Provide', 'What is Included')."
    ),
    "redo_booking_location": (
        "The permanent physical address or venue -- street address, suburb, map link, "
        "landmark, parking, directions. An address ALONE is location; a time alone is "
        "redo_booking_departure_info."
    ),
    "redo_booking_check_in": (
        "ACTIONS on arrival -- present your ticket, sign a waiver, go to reception, "
        "complete registration, meet your guide at a spot. Distinct from timing, which "
        "is redo_booking_departure_info."
    ),
    "redo_booking_departure_info": (
        "TIMING and departure location -- when to be there, what time the tour leaves, "
        "pickup window, which wharf/terminal it departs from."
    ),
    "redo_booking_itinerary": (
        "A time-based or step-by-step sequence of events DURING the experience. Must "
        "have time signals or ordered named stops. A list of OPTIONS is NOT an itinerary."
    ),
    "redo_booking_important_info": (
        "Health warnings, age limits, fitness requirements, safety rules, waivers."
    ),
    "redo_booking_cancellation": (
        "Refund rules, cancellation windows, weather policy."
    ),
    "redo_booking_faqs": (
        "Question-and-answer pairs. A question must be paired with ITS OWN answer -- "
        "a question paired with an unrelated answer is GARBLED."
    ),
    "redo_booking_before_arrival": (
        "Things to do BEFORE the day -- complete a form in advance, pre-book parking, "
        "download an app, check the forecast the night before."
    ),
    "redo_booking_contact": (
        "Phone numbers, email addresses, or contact instructions for reaching the "
        "operator."
    ),
    "redo_booking_other": (
        "Legitimate catch-all for booking-notes content fitting no field above. "
        "Content here is CORRECT only if it genuinely fits no named field -- if a "
        "named field exists for it, that is WRONG_FIELD. Pure filler (greetings, "
        "sign-offs, branding) should not have been extracted at all; if present here, "
        "that is WRONG_FIELD with should_be=NONE."
    ),
}

FIELD_NAMES = list(FIELD_DEFINITIONS)

# Valid values the judge may return.
VALID_VERDICTS = {"CORRECT", "WRONG_FIELD", "GARBLED"}
VALID_SHOULD_BE = set(FIELD_NAMES) | {"NONE", ""}


def definitions_block():
    """Render the field definitions as a prompt-ready block."""
    return "\n".join(f"- {name}: {desc}" for name, desc in FIELD_DEFINITIONS.items())
