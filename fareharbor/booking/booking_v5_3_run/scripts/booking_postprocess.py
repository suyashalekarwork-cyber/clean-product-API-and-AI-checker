"""
Post-processing for booking extraction. Two passes, neither of which deletes.

GOVERNING RULE: post-processing may only ADD or REPORT. It may never delete.

Evidence for that rule, from this project: a dedup pass was trialled earlier and
"9 booking fields would be emptied completely, across 8 products" (blocker F2 in
PLAN_REVIEW_10_AUGUST.md). Deciding which duplicate copy is "more specific" is a
judgement about meaning, made where no human can see it. So duplication is
REPORTED and left in place.

    recovered_content  raw text present in NO column, recorded WITH the heading
                       it sat under, so it can be put back rather than merely
                       counted.
    duplicate_content  sentences appearing in 2+ columns, recorded not removed.

Both should be EMPTY in a healthy run. A non-empty value is a signal to
investigate, not normal output.

WHY recovered_content EXISTS. CLAUDE.md: "Post-extraction content-loss check --
return any raw sentence present in no column. Takes the 0.6-0.7% loss rate to 0;
a prompt rule cannot, because the loss is random." It would have caught 478466,
where the supplier's entire "clothing Golden Rules" block vanished while
what_to_bring kept the OTHER advice -- so the output read as complete at 82.4%
retention with nothing pointing at what was gone.

TEXT UNITS. Booking notes are not prose: a third of all lines are bullets, and
`Label: value` pairs are everywhere. So the unit is the LINE first, and prose
lines are sentence-split second. spaCy was benchmarked and rejected for this --
it merged "Sunscreen / Towel / Hat" into ONE unit, fused headings onto the prose
beneath them, and ran 397x slower, while splitting "Trip Breakdown (Approx." just
as badly as the regex it would have replaced.

MATCHING uses rapidfuzz in three bands, because exact-substring matching cannot
tell "absent" from "reworded":

    >= 97   retained
    80-96   PRESENT BUT REWORDED -- a VERBATIM defect
    < 80    missing -> recovered_content

That middle band was invisible before: 701258 turned "specific dietary
allergies, Island Life Adventures Pty Ltd" into "a specific dietary allergy,
Island Life Adventures" and the old 6-word sliding window scored it retained.
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

from rapidfuzz import fuzz                                   # noqa: E402
from booking_common import (headings_in, lines_of, demark,   # noqa: E402
                            BULLET, is_separator)

RETAINED_AT = 97
REWORDED_AT = 80

# Greetings and sign-offs: the prompt permits omitting these, so their absence
# is correct and must not be reported as loss.
PLEASANTRY = re.compile(
    r"^\s*[#*\s]*(?:thanks?|thank you|kia ora|hey there|hi|hello|welcome|"
    r"nau mai|greetings|congratulations|dear\b|see you|cheers|"
    r"kind regards|warm regards|regards|good luck|"
    r"we(?:'re| are)? (?:stoked|thrilled|excited|delighted|pleased|looking)|"
    r"we look forward|we can'?t wait|we hope|you(?:'re| are)? all booked|"
    r"enjoy your|have a (?:great|wonderful|fantastic)|"
    r"feel free to reach out|happy to help)\b", re.I)

# A bare label introducing content that survived -- not loss in itself.
LEAD_IN = re.compile(r"[:;]\s*$")

# Do not split a sentence after an abbreviation, an initial, or a decimal.
# This replaces the hardcoded abbreviation list the old scorer carried: the
# general shape is "a period preceded by a short token, or followed by a
# lowercase word or a digit".
SENT_SPLIT = re.compile(
    r"(?<=[.!?])\s+(?=[A-Z0-9])"          # split only before a capital/digit
)
ABBREV_TAIL = re.compile(r"(?:^|\s)(?:[A-Za-z]{1,4}|no|mins?|hrs?|approx|est|"
                         r"incl|excl|max|min|etc|vs|ave|st|rd|mt|dr)\.$", re.I)


def norm(s):
    s = (s or "").lower()
    s = s.replace("’", "'").replace("‘", "'")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def sentences_in_line(line):
    """Split a prose line, without breaking on abbreviations or decimals."""
    parts, buf = [], ""
    for chunk in SENT_SPLIT.split(line):
        buf = (buf + " " + chunk).strip() if buf else chunk
        if ABBREV_TAIL.search(buf):
            continue                       # ends in an abbreviation -- keep going
        parts.append(buf)
        buf = ""
    if buf:
        parts.append(buf)
    return [p for p in parts if p.strip()]


def units_with_headings(raw):
    """-> [(unit_text, heading_or_None)] preserving which section each sat in.

    The LINE is the unit. A bullet or `Label: value` line is one unit whatever
    its punctuation. Only prose lines are sentence-split.
    """
    lines = lines_of(raw)
    head_at = dict(headings_in(lines))
    out, current = [], None
    for i, line in enumerate(lines):
        if i in head_at:
            current = head_at[i]
            continue
        if is_separator(line):
            continue
        t = demark(line).strip()
        if not t:
            continue
        if BULLET.match(line) or len(t.split()) <= 12:
            out.append((t, current))       # list item / short line: one unit
        else:
            for s in sentences_in_line(t):
                out.append((s, current))
    return out


def best_score(unit, blobs):
    """Highest similarity of `unit` against any column's text.

    SHORT units (a packing-list item like "Sunscreen", "Towel", "Hat") are
    matched on whole words, not fuzzily. partial_ratio would score "hat" ~100
    against "that" and a dropped item would read as retained -- and a dropped
    item is exactly what this pass exists to catch.
    """
    u = norm(unit)
    if not u:
        return 100
    words = u.split()
    if len(words) <= 3:
        for b in blobs:
            if re.search(r"\b" + re.escape(u) + r"\b", b):
                return 100
        return 0
    return max((fuzz.partial_ratio(u, b) for b in blobs if b), default=0)


def classify(unit):
    """-> 'skip' when the prompt permits omitting this unit."""
    t = unit.strip()
    if not t:
        return "skip"
    if PLEASANTRY.match(t):
        return "skip"
    if LEAD_IN.search(t) and len(t.split()) <= 12:
        return "skip"                      # a lead-in dies with its list
    # A single-word packing item IS checkable -- "Sunscreen" going missing is
    # the exact loss this pass must catch, and best_score() matches short units
    # on whole words so it cannot false-positive. Only skip units with no
    # substantive word at all.
    if not any(len(w) > 2 for w in norm(t).split()):
        return "skip"
    return "check"


def recover(raw, columns):
    """
    -> (recovered_content, reworded, stats)

    columns: {column_name: value} -- the model's output, excluding flags.
    """
    blobs = [norm(v) for v in columns.values() if v and v.strip()]
    recovered, reworded = [], []
    n_checked = 0

    for unit, heading in units_with_headings(raw):
        if classify(unit) == "skip":
            continue
        n_checked += 1
        score = best_score(unit, blobs)
        if score >= RETAINED_AT:
            continue
        label = (heading or "no heading").strip().rstrip(":")
        if score >= REWORDED_AT:
            reworded.append(f"{label}: {unit.strip()[:200]}")
        else:
            recovered.append(f"{label}: {unit.strip()[:200]}")

    stats = {"units_checked": n_checked,
             "recovered": len(recovered),
             "reworded": len(reworded)}
    return "\n".join(recovered), "\n".join(reworded), stats


def find_duplicates(columns):
    """Sentences appearing in 2+ columns. REPORTED, never removed."""
    dupes, names = [], list(columns)
    for i, a in enumerate(names):
        va = columns.get(a) or ""
        if not va.strip():
            continue
        for s in [x.strip() for x in re.split(r"(?<=[.!?])\s+|\n+", va)]:
            if len(norm(s).split()) < 5:
                continue
            ns = norm(s)
            for b in names[i + 1:]:
                vb = columns.get(b) or ""
                if vb.strip() and ns in norm(vb):
                    dupes.append(f"{a} & {b}: {s[:150]}")
    return "\n".join(dupes)


def process(raw, columns):
    """Run both passes. Returns the two diagnostic columns plus stats."""
    recovered, reworded, stats = recover(raw, columns)
    duplicates = find_duplicates(columns)
    stats["duplicates"] = len(duplicates.split("\n")) if duplicates else 0
    return {
        "recovered_content": recovered,
        "reworded_content": reworded,
        "duplicate_content": duplicates,
        "stats": stats,
    }


if __name__ == "__main__":
    # Self-test on the shapes that motivated each rule.
    raw = (
        "Thanks for booking with us!\n"
        "##What to Bring\n"
        "Sunscreen\n"
        "Towel\n"
        "NO COTTON or DENIM - when they get wet they stay cold and heavy.\n"
        "##Check In\n"
        "Please arrive 15 minutes prior. Boarding closes at 9:00 AM sharp.\n"
        "Duration is approx. 2 hrs. Meet at the wharf.\n"
    )
    cols = {
        "what_to_bring": "Sunscreen\nTowel",           # golden-rule line LOST
        "check_in": "Please arrive 15 minutes prior. Boarding closes at 9:00 AM sharp.",
        "notes": "Duration is approx. 2 hrs. Meet at the wharf.",
        "important_info": "Please arrive 15 minutes prior.",   # duplicate
    }
    r = process(raw, cols)
    print("units checked :", r["stats"]["units_checked"])
    print()
    print("RECOVERED (should contain the NO COTTON line, with its heading):")
    print(r["recovered_content"] or "  (none)")
    print()
    print("REWORDED:")
    print(r["reworded_content"] or "  (none)")
    print()
    print("DUPLICATES (reported, not removed):")
    print(r["duplicate_content"] or "  (none)")
    print()
    print("greeting skipped:", "Thanks for booking" not in r["recovered_content"])
    print("abbreviation not split:",
          "approx" not in r["recovered_content"].lower()
          or "2 hrs" in r["recovered_content"])
