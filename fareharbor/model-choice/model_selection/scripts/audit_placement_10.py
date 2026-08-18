"""
Placement audit: 10 products x 4 models, checking WHERE content landed rather
than whether it survived.

Why this exists: coverage counts words that survived anywhere. Product 451390
proved it is blind to the failure that matters -- "a COMPLIMENTARY shuttle bus"
filed under redo_desc_what_excluded ("what is NOT included") scores 100%
coverage while telling the customer the exact opposite of the truth.

This script finds those cases. It is deliberately NOT a scorer: it emits
evidence (product, field, the offending text, the raw context) for reading.
Every automated check in this project that produced a number has been wrong at
least once; the fix each time was reading the raw text. So the output is
designed to be read, and every rule below has a stated failure mode.

Detectors, each keyed to a defect seen in real output:

  D1 FREE_IN_EXCLUDED    text says complimentary/free/included but sits in a
                         what_excluded field. This is the 451390 defect.
  D2 SPLIT_BLOCK         one contiguous raw block split across 2+ fields --
                         the "half in about, half in meeting_point" problem.
  D3 FAQ_SCATTER         Q&A content spread across fields instead of held
                         together.
  D4 LABEL_VIOLATION     raw text carries an embedded "label:" whose V4.4
                         mapping says field X, but the content went to Y.
  D5 LABEL_LEAK          the literal "label:" prefix left inside the value.
  D6 MD_JUNK             markdown (**, ##) left in the value.
  D7 PLACEHOLDER         model wrote "No content found..." instead of "".

Usage:
    python audit_placement_10.py
"""
import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from screen_model_comparison import PRODUCT_IDS

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
SCREEN = TEST_DIR / "bestmodel_screen_results.json"
OUT_JSON = TEST_DIR / "placement_audit_10.json"

MODELS = ["gpt-5.4-nano", "gpt-5.5-pro", "gpt-5-mini", "gpt-5.6-terra", "gpt-4o-mini"]

# V4.4 LABEL MAPPING, copied from config/fareharbor_prompts.txt. Authoritative
# per the prompt: "This mapping is authoritative and overrides your own
# judgment." Used by D4 to detect a model disobeying it.
LABEL_MAP = {
    "description": "redo_desc_about",
    "highlights": "redo_desc_highlights",
    "what_is_included": "redo_desc_what_included",
    "what_is_not_included": "redo_desc_what_excluded",
    "extras": "redo_desc_what_excluded",
    "itinerary": "redo_desc_itinerary",
    "what_to_bring": "redo_desc_what_to_bring",
    "duration": "redo_desc_duration_text",
    "min_age": "redo_min_age",
    "max_age": "redo_max_age",
    "group_size": "redo_group_size",
    "meeting_point": "redo_meeting_point",
    "cancellation_summary": "redo_desc_cancellation",
    "check_in_details": "redo_desc_check_in",
    "restrictions": "redo_desc_requirements",
    "special_requirements": "redo_desc_requirements",
    "accessibility": "redo_desc_requirements",
    "disclaimers": "redo_desc_other",
    "faqs": "redo_desc_other",
    "pricing": "redo_desc_other",
}

EXCLUDED_FIELDS = {"redo_desc_what_excluded", "redo_booking_what_not_to_bring"}
FREE_RE = re.compile(
    r"\b(complimentary|free of charge|no extra cost|at no cost|included in "
    r"(?:the )?(?:price|ticket|fare)|provided free|free\b)", re.IGNORECASE)
# "free" alone is ambiguous ("free time", "gluten free", "feel free"), so the
# surrounding phrase must survive this filter before the hit is reported
FREE_FALSE_POS_RE = re.compile(
    r"\b(free time|gluten[- ]free|duty[- ]free|feel free|free from|hands[- ]free|"
    r"smoke[- ]free|toll[- ]free|carefree|sugar[- ]free)\b", re.IGNORECASE)

QUESTION_RE = re.compile(r"\?\s*(?:\*{0,2}\s*)?$", re.M)
PLACEHOLDER_RE = re.compile(
    r"^\s*(no content|none found|not (?:found|available|specified|provided|"
    r"applicable)|n/?a)\b", re.IGNORECASE)
MD_RE = re.compile(r"\*\*|^\s*#{1,3}\s", re.M)
LABEL_PREFIX_RE = re.compile(
    r"^\s*(" + "|".join(re.escape(k) for k in LABEL_MAP) + r")\s*:", re.IGNORECASE)


def norm_words(text):
    return [w for w in re.sub(r"[^a-z0-9 ]", " ", str(text).lower()).split() if len(w) > 3]


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", str(text)) if s.strip()]


def raw_blocks(raw):
    """Contiguous paragraphs of raw text that a reader would expect to stay
    together.

    Splitting on blank lines alone is NOT enough. Inspected against real
    output, most D2 hits were paragraphs that STRADDLE two embedded labels --
    e.g. the tail of what_is_included plus the head of extras:. Those belong in
    two different fields, so a model separating them is correct, and flagging
    it accused every model of a defect it did not commit.

    So each blank-line paragraph is cut again at any embedded 'label:' line,
    and only the segment before/after that boundary counts as one block.
    """
    out = []
    for para in re.split(r"\n\s*\n", str(raw)):
        # cut at embedded labels -- a label starts a new logical section
        segs = re.split(
            r"^[ \t]*(?:" + "|".join(re.escape(k) for k in LABEL_MAP) + r")[ \t]*:",
            para, flags=re.IGNORECASE | re.M)
        for seg in segs:
            seg = seg.strip()
            if len(seg.split()) >= 12:
                out.append(seg)
    return out


def find_labels(raw):
    """[(label, value)] for embedded 'label: value' blocks in the raw text."""
    out = []
    pattern = re.compile(
        r"^[ \t]*(" + "|".join(re.escape(k) for k in LABEL_MAP) + r")[ \t]*:(.*?)"
        r"(?=^[ \t]*(?:" + "|".join(re.escape(k) for k in LABEL_MAP) + r")[ \t]*:|\Z)",
        re.IGNORECASE | re.M | re.S)
    for m in pattern.finditer(str(raw)):
        val = m.group(2).strip()
        if val:
            out.append((m.group(1).strip().lower(), val))
    return out


def overlap(a_words, b_text):
    if not a_words:
        return 0.0
    have = set(norm_words(b_text))
    return sum(1 for w in a_words if w in have) / len(a_words)


def audit(pid, model, fv, raw_desc, raw_booking):
    findings = []
    raw_all = (raw_desc or "") + "\n" + (raw_booking or "")
    filled = {f: str(v or "").strip() for f, v in fv.items() if str(v or "").strip()}

    # D1 -- free/complimentary content sitting in an "excluded" field
    for field in EXCLUDED_FIELDS:
        val = filled.get(field, "")
        if not val:
            continue
        # A rate card legitimately lists a free tier alongside paid ones
        # ("3 and under are free. 4 and over are $5"). That is pricing, not a
        # contradiction, and flagging it accused two models falsely. Only treat
        # the field as contradictory when it is NOT a price list.
        is_rate_card = len(re.findall(r"\$\s?\d", val)) >= 2
        if is_rate_card:
            continue
        for sent in sentences(val):
            if FREE_RE.search(sent) and not FREE_FALSE_POS_RE.search(sent):
                findings.append({
                    "code": "D1_FREE_IN_EXCLUDED", "severity": "HIGH", "field": field,
                    "detail": "text describes something free/included but is filed "
                              "under 'what is NOT included' -- states the opposite "
                              "of the source",
                    "evidence": sent[:300]})
                break

    # D4/D5 -- embedded label routed against the authoritative V4.4 mapping
    for label, value in find_labels(raw_desc):
        target = LABEL_MAP.get(label)
        if not target:
            continue
        vw = norm_words(value)
        if len(vw) < 6:
            continue
        best, best_ov = None, 0.0
        for field, fval in filled.items():
            ov = overlap(vw, fval)
            if ov > best_ov:
                best, best_ov = field, ov
        # only claim a violation when the content clearly landed elsewhere;
        # a low best_ov means the content is scattered, which D2 covers
        if best and best_ov >= 0.6 and best != target:
            # Disobeying the mapping is not automatically harmful. Inspected
            # against real output, several "violations" were the model doing
            # the sensible thing: cancellation text under a disclaimers: label
            # routed to redo_desc_cancellation, or FAQ refund policy routed the
            # same way. V4.4 sends both to redo_desc_other, so the rule calls it
            # a violation while the reader gets BETTER data.
            #
            # So severity splits on whether the destination contradicts the
            # content. Landing in a field that misstates the facts (free
            # content under "not included") is HIGH; landing somewhere
            # defensible but off-map is INFO -- reported, not counted against
            # the model.
            benign = (
                target == "redo_desc_other"
                and best in {"redo_desc_cancellation", "redo_desc_requirements",
                             "redo_desc_check_in", "redo_desc_what_included"}
            )
            findings.append({
                "code": "D4_LABEL_VIOLATION",
                "severity": "INFO" if benign else "HIGH",
                "field": best,
                "detail": f"raw label '{label}:' maps to {target} under V4.4, but "
                          f"this content landed in {best} ({best_ov:.0%} match)"
                          + ("  [BENIGN: off-map but arguably a better home than "
                             "the catch-all]" if benign else ""),
                "evidence": value[:300]})

    for field, val in filled.items():
        m = LABEL_PREFIX_RE.match(val)
        if m:
            findings.append({
                "code": "D5_LABEL_LEAK", "severity": "LOW", "field": field,
                "detail": f"literal label prefix '{m.group(1)}:' left in the value",
                "evidence": val[:200]})

    # D2 -- a single raw paragraph torn across two or more fields
    for block in raw_blocks(raw_all):
        bw = norm_words(block)
        # a holder must own a real share of the block, not echo a few words of
        # it -- 0.25 flagged fields containing one shared sentence
        holders = [f for f, v in filled.items() if overlap(bw, v) >= 0.40]
        if len(holders) >= 2:
            strong = [f for f in holders if overlap(bw, filled[f]) >= 0.85]
            if strong:
                continue          # one field holds it whole; the rest is echo
            findings.append({
                "code": "D2_SPLIT_BLOCK", "severity": "MEDIUM",
                "field": " + ".join(sorted(holders)),
                "detail": f"one contiguous raw paragraph split across "
                          f"{len(holders)} fields, none holding it whole",
                "evidence": block[:300]})

    # D3 -- Q&A content scattered rather than kept together
    if QUESTION_RE.search(raw_all):
        holders = sorted(f for f, v in filled.items() if QUESTION_RE.search(v))
        if len(holders) >= 2:
            findings.append({
                "code": "D3_FAQ_SCATTER", "severity": "MEDIUM",
                "field": " + ".join(holders),
                "detail": f"question-and-answer content spread across "
                          f"{len(holders)} fields instead of being held together",
                "evidence": "; ".join(h for h in holders)})

    # D7 / D6 -- placeholder prose and markdown junk
    for field, val in filled.items():
        if PLACEHOLDER_RE.match(val):
            findings.append({
                "code": "D7_PLACEHOLDER", "severity": "MEDIUM", "field": field,
                "detail": "placeholder sentence written instead of an empty string",
                "evidence": val[:160]})
        elif MD_RE.search(val):
            findings.append({
                "code": "D6_MD_JUNK", "severity": "LOW", "field": field,
                "detail": "markdown syntax left in the extracted value",
                "evidence": val[:160]})
    return findings


def main():
    screen = json.loads(SCREEN.read_text(encoding="utf-8"))
    results = {}
    for model in MODELS:
        results[model] = {}
        for pid in PRODUCT_IDS:
            d = screen[model][pid]
            results[model][pid] = {
                "coverage": d["word_coverage_pct"],
                "units_missing": d["units_missing"],
                "findings": audit(pid, model, d["field_values"],
                                  d["raw_desc"], d["raw_booking"]),
            }

    OUT_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    print("=" * 88)
    print("PLACEMENT AUDIT -- 10 products x 4 models (+ incumbent)")
    print("=" * 88)
    hdr = f"{'model':<16}{'HIGH':>6}{'MED':>6}{'LOW':>6}{'INFO':>6}{'total':>7}   {'coverage':>9}"
    print(hdr)
    for model in MODELS:
        f = [x for p in results[model].values() for x in p["findings"]]
        hi = sum(1 for x in f if x["severity"] == "HIGH")
        info = sum(1 for x in f if x["severity"] == "INFO")
        me = sum(1 for x in f if x["severity"] == "MEDIUM")
        lo = sum(1 for x in f if x["severity"] == "LOW")
        cov = sum(p["coverage"] for p in results[model].values()) / len(PRODUCT_IDS)
        print(f"{model:<16}{hi:>6}{me:>6}{lo:>6}{info:>6}{len(f):>7}   {cov:>8.2f}%")

    print("\nBy defect code:")
    codes = {}
    for model in MODELS:
        for p in results[model].values():
            for x in p["findings"]:
                codes.setdefault(x["code"], {}).setdefault(model, 0)
                codes[x["code"]][model] += 1
    print(f"  {'code':<24}" + "".join(f"{m.split('-')[-1]:>12}" for m in MODELS))
    for code in sorted(codes):
        print(f"  {code:<24}" + "".join(f"{codes[code].get(m, 0):>12}" for m in MODELS))
    print(f"\nWrote {OUT_JSON.name}")
    return results


if __name__ == "__main__":
    main()
