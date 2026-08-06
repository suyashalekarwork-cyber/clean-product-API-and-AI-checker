"""
Screen the 100-product gpt-5.6-luna output.

Same measurements as screen_hard30.py, on one model instead of four. Kept as a
separate script rather than parameterising the other one, because that script
is already published in the repo and rewriting it would invalidate a file
someone else may be running.

Technical failures (HTTP errors, unparseable JSON, truncation) are counted
separately from extraction quality. A response that never arrived is not a
model scoring zero, and merging the two makes a broken run look like a bad
model.

Usage:
    python screen_luna100.py
"""
import sys
import re
import json
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loss_detector import detect_lost_content_wordlevel, word_count
from screen_model_comparison import DESC_FIELDS, BOOKING_FIELDS

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
OUTPUT = TEST_DIR / "luna100_output.jsonl"
PRODUCTS = TEST_DIR / "luna100_products.json"
STATE = TEST_DIR / "v500_post_fix_state.json"
OUT = TEST_DIR / "luna100_screen_results.json"

MODEL = "gpt-5.6-luna"
MIN_DUP_WORDS = 5
MD_RE = re.compile(r"\*\*|^\s*#{1,3}\s", re.M)


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", str(text))
    return [p.strip() for p in parts if p.strip()]


def norm(s):
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s.lower()).split())


def count_dupes(fv):
    """Sentences in 2+ fields, per side only.

    Never across sides: cancellation and accessibility genuinely appear in both
    the description and the booking notes, and counting those as duplicates
    would penalise correct output.
    """
    total = 0
    for side in (DESC_FIELDS, BOOKING_FIELDS):
        where = {}
        for f in side:
            for s in split_sentences(str(fv.get(f) or "")):
                if len(s.split()) >= MIN_DUP_WORDS:
                    where.setdefault(norm(s), set()).add(f)
        total += sum(1 for v in where.values() if len(v) > 1)
    return total


def count_untraceable(fv, raw):
    """Fields whose words do not trace back to the source -- genuine invention."""
    def keys(s):
        return {w for w in re.sub(r"[^a-z0-9 ]", " ", str(s).lower()).split()
                if len(w) > 3}
    raw_words = keys(raw)
    if not raw_words:
        return 0
    n = 0
    for v in fv.values():
        w = keys(v)
        if w and len(w & raw_words) / len(w) < 0.8:
            n += 1
    return n


def main():
    meta = json.loads(PRODUCTS.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8"))
    ids = meta["product_ids"]

    parsed, bad_json, truncated, http_error = {}, [], [], []
    n_lines = 0
    for line in open(OUTPUT, encoding="utf-8"):
        if not line.strip():
            continue
        n_lines += 1
        rec = json.loads(line)
        cid = rec.get("custom_id", "")
        pid, _, side = (cid.split("|") + ["", "", ""])[:3]
        resp = rec.get("response") or {}
        if rec.get("error") or resp.get("status_code") != 200:
            http_error.append(cid)
            continue
        choice = (resp.get("body", {}).get("choices") or [{}])[0]
        if choice.get("finish_reason") not in (None, "stop"):
            truncated.append(cid)
        content = ((choice.get("message") or {}).get("content") or "").strip()
        if content.startswith("```"):
            content = re.sub(r"^```[a-z]*\s*|\s*```$", "", content)
        try:
            parsed.setdefault(pid, {})[side] = json.loads(content)
        except json.JSONDecodeError:
            bad_json.append(cid)

    results = {}
    for pid in ids:
        got = parsed.get(pid, {})
        fv = {}
        for f in DESC_FIELDS:
            fv[f] = (got.get("desc") or {}).get(f, "")
        for f in BOOKING_FIELDS:
            fv[f] = (got.get("booking") or {}).get(f, "")
        raw_desc = state[pid].get("raw_desc") or ""
        raw_booking = state[pid].get("raw_booking") or ""
        raw_all = raw_desc + " " + raw_booking
        det = detect_lost_content_wordlevel(raw_desc, raw_booking, fv)
        emitted = sum(len(str(v or "").split()) for v in fv.values())
        rw = word_count(raw_all)
        results[pid] = {
            "field_values": fv, "raw_desc": raw_desc, "raw_booking": raw_booking,
            "input_words": rw,
            "word_coverage_pct": det["word_coverage_pct"],
            "units_missing": det["units_missing"],
            "units_partial": det["units_partial"],
            "words_emitted": emitted,
            "word_ratio": round(emitted / rw, 3) if rw else 0.0,
            "dup_sentences": count_dupes(fv),
            "untraceable_fields": count_untraceable(fv, raw_all),
            "markdown_fields": sum(1 for v in fv.values() if MD_RE.search(str(v or ""))),
            "fields_filled": sum(1 for v in fv.values() if str(v or "").strip()),
            "desc_present": got.get("desc") is not None,
            "booking_present": got.get("booking") is not None or not raw_booking.strip(),
        }

    OUT.write_text(json.dumps({MODEL: results}, ensure_ascii=False, indent=2),
                   encoding="utf-8")

    vals = list(results.values())
    n = len(vals)
    raw_tot = sum(v["input_words"] for v in vals)
    emit_tot = sum(v["words_emitted"] for v in vals)

    print("=" * 74)
    print(f"LUNA 100-PRODUCT SCREEN -- {MODEL}, V4.7")
    print("=" * 74)
    print(f"  responses          : {n_lines} of {meta['n_requests']} expected")
    print(f"  products with output: {len(parsed)} of {n}")
    print()
    print("  TECHNICAL FAILURES (not quality):")
    print(f"    HTTP errors      : {len(http_error)}")
    print(f"    unparseable JSON : {len(bad_json)}")
    print(f"    truncated        : {len(truncated)}")
    print()
    print("  EXTRACTION QUALITY:")
    print(f"    coverage         : {sum(v['word_coverage_pct'] for v in vals) / n:.2f}%")
    print(f"    word ratio       : {emit_tot / raw_tot:.3f}")
    print(f"    missing units    : {sum(v['units_missing'] for v in vals)}")
    print(f"    duplicates       : {sum(v['dup_sentences'] for v in vals)}")
    print(f"    untraceable      : {sum(v['untraceable_fields'] for v in vals)}")
    print(f"    markdown fields  : {sum(v['markdown_fields'] for v in vals)}")
    print(f"    avg fields filled: {sum(v['fields_filled'] for v in vals) / n:.1f} of 28")
    print(f"\nWrote {OUT.name}")


if __name__ == "__main__":
    main()
