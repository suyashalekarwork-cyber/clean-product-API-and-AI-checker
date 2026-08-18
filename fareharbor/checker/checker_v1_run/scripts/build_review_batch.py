"""
Pass 1 of the V5.3 reviewer -- build the Batch API input.

One request per product: the raw supplier description plus all 22 extracted
columns (empty ones included -- EMPTY_BUT_HEADING is only reachable because the
reviewer can see them).

    python build_review_batch.py --set validation73
    python build_review_batch.py --set random1000

custom_id = {product_id}|{model}|review|rev1

Reuses strip_html / find_raw_file / make_request from
build_model_comparison_batches.py and load_model_cfg from
build_v5_3_random1000_batch.py, unchanged.

DO NOT COMMIT the output JSONL: the system prompt is ~13 KB and repeats once
per line, so 1,000 products is ~18 MB of which ~97% is the same string.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
ROOT = TEST_DIR.parent.parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

import review_contract as rc  # noqa: E402
import review_key as rk  # noqa: E402
from build_model_comparison_batches import strip_html, find_raw_file, make_request  # noqa: E402
from build_v5_3_random1000_batch import load_model_cfg  # noqa: E402

MODEL = "gpt-5.6-luna"
REV = "rev1"

SETS = {
    "validation73": TEST_DIR / "review_validation73_batch.jsonl",
    "random1000": TEST_DIR / "review_random1000_batch.jsonl",
}

# Display order for the columns block: about first, then the rest of the
# contract order, with the three non-desc columns last.
COLUMN_ORDER = [
    "redo_desc_about",
    "redo_desc_important_info",
    "redo_desc_highlights",
    "redo_desc_what_included",
    "redo_desc_what_excluded",
    "redo_desc_extras",
    "redo_desc_itinerary",
    "redo_desc_what_to_bring",
    "redo_desc_duration_text",
    "redo_desc_cancellation",
    "redo_desc_check_in",
    "redo_desc_accessibility",
    "redo_desc_restrictions",
    "redo_desc_special_requirements",
    "redo_desc_faqs",
    "redo_desc_pricing",
    "redo_desc_disclaimers",
    "redo_meeting_point",
    "redo_group_size",
    "redo_min_age",
    "redo_max_age",
]

# gpt-5.6-luna intermittently closes its JSON with a stray comma-quote before
# the brace. Copied from check_against_raw.py:110 -- WITHOUT its
# cid.endswith("|desc") filter, which matches none of these 4-segment ids.
STRAY_COMMA = re.compile(r',\s*"\s*\}\s*$')
FENCE = re.compile(r"^```(?:json)?\s*|\s*```$")


def parse_content(text):
    """Parse a model response body, repairing the known stray-comma defect."""
    t = FENCE.sub("", text.strip())
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        return json.loads(STRAY_COMMA.sub("}", t))


def load_extractions(filename):
    """{product_id: normalised 22-key extraction} from a V5.3 output JSONL."""
    out, bad = {}, []
    for line in (TEST_DIR / filename).open(encoding="utf-8"):
        row = json.loads(line)
        pid = row["custom_id"].split("|")[0]
        try:
            rec = parse_content(row["response"]["body"]["choices"][0]["message"]["content"])
        except Exception as exc:
            bad.append((pid, str(exc)))
            continue
        out[pid] = rc.normalise_keys(rec)
    if bad:
        print("  WARNING unparseable extraction rows: %d %s" % (len(bad), bad[:5]))
    return out


def raw_description(pid):
    item = json.loads(Path(find_raw_file(pid)).read_text(encoding="utf-8")).get("item", {})
    sd = item.get("structured_description") or {}
    return strip_html(sd.get("description") or item.get("description") or "")


def build_user_message(pid, raw_desc, cols):
    """Raw on top, then every column including the empty ones."""
    lines = [
        "PRODUCT ID: %s" % pid,
        "",
        "=== RAW DESCRIPTION (source of truth, exactly as the supplier wrote it) ===",
        raw_desc,
        "",
        "=== EXTRACTED COLUMNS (all 22, empty ones shown as EMPTY) ===",
    ]
    for key in COLUMN_ORDER:
        val = (cols.get(key) or "").strip()
        lines.append("")
        lines.append("[%s]" % key)
        lines.append(val if val else "EMPTY")
    flags = (cols.get("redo_flags") or "").strip()
    lines.append("")
    lines.append("[redo_flags]  (the extractor's own notes, not a content column)")
    lines.append(flags if flags else "EMPTY")
    return "\n".join(lines)


def select(which):
    """[(product_id, output_filename)] for the chosen set."""
    if which == "validation73":
        return sorted(((p, v["output_file"]) for p, v in rk.KEY.items()),
                      key=lambda t: (t[1], t[0]))
    ids = json.loads((TEST_DIR / "random1000_products.json").read_text(encoding="utf-8"))
    return [(str(p), "v5_3_random1000_output.jsonl") for p in ids["product_ids"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", dest="which", choices=sorted(SETS), required=True)
    args = ap.parse_args()

    system_prompt = rc.review_prompt()
    print("prompt %s + live contract: %d chars" % (rc.REVIEW_VERSION, len(system_prompt)))

    cfg = load_model_cfg(MODEL)
    print("model %s: param_set=%s" % (MODEL, cfg["param_set"]))

    targets = select(args.which)
    print("products: %d" % len(targets))

    caches = {}
    for _, fn in targets:
        if fn not in caches:
            caches[fn] = load_extractions(fn)
            print("  loaded %s: %d extractions" % (fn, len(caches[fn])))

    requests, skipped = [], []
    for pid, fn in targets:
        cols = caches[fn].get(pid)
        if cols is None:
            skipped.append((pid, "no extraction in " + fn))
            continue
        try:
            raw = raw_description(pid)
        except (FileNotFoundError, RuntimeError) as exc:
            skipped.append((pid, str(exc)))
            continue
        if not raw:
            skipped.append((pid, "empty raw description"))
            continue
        requests.append(make_request(
            custom_id="%s|%s|review|%s" % (pid, MODEL, REV),
            model=MODEL,
            model_cfg=cfg,
            system_prompt=system_prompt,
            user_message=build_user_message(pid, raw, cols),
        ))

    out = SETS[args.which]
    with out.open("w", encoding="utf-8") as fh:
        for r in requests:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    size_mb = out.stat().st_size / 1e6
    print("\nwrote %s: %d requests, %.1f MB" % (out.name, len(requests), size_mb))
    if skipped:
        print("SKIPPED %d:" % len(skipped))
        for pid, why in skipped[:20]:
            print("  %s: %s" % (pid, why))


if __name__ == "__main__":
    main()
