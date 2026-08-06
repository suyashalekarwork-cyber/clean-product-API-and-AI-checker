"""
Screen the 3 V4.7 model outputs on the 30 hardest products, and merge the
existing gpt-4o-mini baseline.

Reports the measurements that actually decide this, including two that
coverage-only screening cannot see:

  word_ratio        words emitted / words in source. gpt-5.4-nano scored 1.32x
                    on the earlier run -- it duplicates rather than invents.
                    Coverage is blind to this: a word counted twice still
                    counts as present, which is how nano scored 99.75% while
                    failing human review.
  dup_sentences     sentences appearing in 2+ fields ON THE SAME SIDE. Never
                    across sides -- cancellation and accessibility legitimately
                    appear in both the description and the booking notes.
  untraceable       fields whose words do not trace back to the raw text, i.e.
                    genuine invention. Measured at 0 for nano, 4 for terra,
                    1 for luna on the earlier run; must not rise under V4.7.

The gpt-4o-mini column is READ FROM v500_post_fix_state.json, not re-run. That
run used V4.4, so it differs from the candidates in BOTH model and prompt --
it is a "what we ship today" reference, not a controlled comparison. Labelled
as such wherever it appears.

Usage:
    python screen_hard30.py
"""
import sys
import re
import json
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loss_detector import detect_lost_content_wordlevel, word_count
from screen_model_comparison import DESC_FIELDS, BOOKING_FIELDS, ALL_FIELDS
from build_hard30_batches import CANDIDATES

# minimum words for a sentence to count as duplicable -- short fragments like
# "Please note:" legitimately recur, and counting them would inflate the
# duplication figure with things no reader would call a duplicate
MIN_DUP_WORDS = 5


def split_sentences(text):
    """Split into sentence-ish units, keeping line breaks as boundaries."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", str(text))
    return [p.strip() for p in parts if p.strip()]


def norm(sentence):
    """Comparison key: case- and punctuation-insensitive, whitespace-collapsed."""
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", sentence.lower()).split())

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
PRODUCTS_PATH = TEST_DIR / "hard30_products.json"
STATE_PATH = TEST_DIR / "v500_post_fix_state.json"
OUT_SCREEN = TEST_DIR / "hard30_screen_results.json"

BASELINE = "gpt-4o-mini (V4.4, existing)"
MD_RE = re.compile(r"\*\*|^\s*#{1,3}\s", re.M)


def parse_output(path):
    """{pid: {'desc': dict|None, 'booking': dict|None, 'finish': {}, 'bad_json': []}}"""
    products = {}
    if not path.exists():
        return products
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            parts = rec.get("custom_id", "").split("|")
            if len(parts) < 3:
                continue
            pid, side = parts[0], parts[2]
            entry = products.setdefault(pid, {"desc": None, "booking": None,
                                              "finish": {}, "bad_json": []})
            response = rec.get("response")
            if rec.get("error") or response is None or response.get("status_code") != 200:
                continue
            try:
                choice = response["body"]["choices"][0]
                entry["finish"][side] = choice.get("finish_reason")
                entry[side] = json.loads(choice["message"]["content"])
            except (KeyError, IndexError, TypeError):
                continue
            except json.JSONDecodeError:
                entry["bad_json"].append(side)
    return products


def count_dupes(field_values):
    """Sentences appearing in 2+ fields, counted per side and never across."""
    total = 0
    for side_fields in (DESC_FIELDS, BOOKING_FIELDS):
        where = {}
        for f in side_fields:
            v = str(field_values.get(f) or "").strip()
            for sent in split_sentences(v):
                if len(sent.split()) < MIN_DUP_WORDS:
                    continue
                where.setdefault(norm(sent), set()).add(f)
        total += sum(1 for holders in where.values() if len(holders) > 1)
    return total


def count_untraceable(field_values, raw):
    """Fields whose words do not trace back to the source -- genuine invention."""
    def keyset(s):
        return {w for w in re.sub(r"[^a-z0-9 ]", " ", str(s).lower()).split()
                if len(w) > 3}
    raw_words = keyset(raw)
    if not raw_words:
        return 0
    n = 0
    for v in field_values.values():
        w = keyset(v)
        if w and len(w & raw_words) / len(w) < 0.8:
            n += 1
    return n


def measure(pid, field_values, raw_desc, raw_booking):
    raw_all = (raw_desc or "") + " " + (raw_booking or "")
    det = detect_lost_content_wordlevel(raw_desc, raw_booking, field_values)
    emitted = sum(len(str(v or "").split()) for v in field_values.values())
    raw_words = word_count(raw_all)
    return {
        "field_values": field_values,
        "raw_desc": raw_desc, "raw_booking": raw_booking,
        "input_words": raw_words,
        "word_coverage_pct": det["word_coverage_pct"],
        "units_missing": det["units_missing"],
        "units_partial": det["units_partial"],
        "words_emitted": emitted,
        "word_ratio": round(emitted / raw_words, 3) if raw_words else 0.0,
        "dup_sentences": count_dupes(field_values),
        "untraceable_fields": count_untraceable(field_values, raw_all),
        "markdown_fields": sum(1 for v in field_values.values()
                               if MD_RE.search(str(v or ""))),
        "fields_filled": sum(1 for v in field_values.values() if str(v or "").strip()),
    }


def main():
    product_ids = json.loads(PRODUCTS_PATH.read_text(encoding="utf-8"))["product_ids"]
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    results = {}

    for model in CANDIDATES:
        safe = model.replace(".", "_")
        products = parse_output(TEST_DIR / f"hard30_output_{safe}.jsonl")
        per, st_out = {}, {}
        for pid in product_ids:
            entry = products.get(pid, {"desc": None, "booking": None,
                                       "finish": {}, "bad_json": []})
            fv = {}
            for f in DESC_FIELDS:
                fv[f] = (entry.get("desc") or {}).get(f, "")
            for f in BOOKING_FIELDS:
                fv[f] = (entry.get("booking") or {}).get(f, "")
            raw_desc = state[pid].get("raw_desc") or ""
            raw_booking = state[pid].get("raw_booking") or ""
            m = measure(pid, fv, raw_desc, raw_booking)
            bad_finish = {s: r for s, r in entry["finish"].items()
                          if r not in (None, "stop")}
            m.update({
                "desc_present": entry.get("desc") is not None,
                # a product with no booking text was never sent a booking
                # request, so "absent" is correct, not a failure
                "booking_present": entry.get("booking") is not None
                                   or not raw_booking.strip(),
                "truncated": bool(bad_finish),
                "bad_json": entry["bad_json"],
            })
            per[pid] = m
            st_out[pid] = {"field_values": fv, "raw_desc": raw_desc,
                           "raw_booking": raw_booking}
        results[model] = per
        (TEST_DIR / f"hard30_{safe}_state.json").write_text(
            json.dumps(st_out, ensure_ascii=False, indent=2), encoding="utf-8")

    # merge the incumbent from the 500-run -- no new API calls
    per = {}
    for pid in product_ids:
        rec = state[pid]
        m = measure(pid, rec["field_values"], rec.get("raw_desc") or "",
                    rec.get("raw_booking") or "")
        m.update({"desc_present": True, "booking_present": True,
                  "truncated": False, "bad_json": []})
        per[pid] = m
    results[BASELINE] = per

    OUT_SCREEN.write_text(json.dumps(results, ensure_ascii=False, indent=2),
                          encoding="utf-8")

    rows = []
    for model, per in results.items():
        v = list(per.values())
        n = len(v)
        raw_tot = sum(x["input_words"] for x in v)
        emit_tot = sum(x["words_emitted"] for x in v)
        rows.append({
            "model": model,
            "coverage_pct": round(sum(x["word_coverage_pct"] for x in v) / n, 2),
            "MISSING": sum(x["units_missing"] for x in v),
            "word_ratio": round(emit_tot / raw_tot, 3) if raw_tot else 0,
            "dup_sentences": sum(x["dup_sentences"] for x in v),
            "untraceable": sum(x["untraceable_fields"] for x in v),
            "markdown_fields": sum(x["markdown_fields"] for x in v),
            "avg_fields": round(sum(x["fields_filled"] for x in v) / n, 1),
            "truncated": sum(1 for x in v if x["truncated"]),
            "bad_json": sum(len(x["bad_json"]) for x in v),
        })
    df = pd.DataFrame(rows)

    print("=" * 100)
    print(f"HARD30 SCREEN -- {len(product_ids)} products, V4.7 prompt "
          f"(+ gpt-4o-mini V4.4 baseline)")
    print("=" * 100)
    print(df.to_string(index=False))
    print("\nword_ratio 1.00 = emitted exactly as many words as the source. "
          "Above 1.00 means duplication.")
    print("dup_sentences counted per side; cross-side repeats are legitimate "
          "and not counted.")
    print(f"\nWrote {OUT_SCREEN.name} + per-model hard30_*_state.json")
    return df


if __name__ == "__main__":
    main()
