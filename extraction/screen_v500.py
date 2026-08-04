"""
Isolated POC: Step 3 -- screen for the 500-product round. Same logic as
screen_v50.py, pointed at v500_output.jsonl / new_500_products_selection.csv.
Unchanged pipeline logic (word-level detector from loss_detector.py, source_side
determined by raw-field substring check). Skip-and-continue: products with a
failed desc OR booking call (per v500_failures.csv) are excluded here.

Usage:
    python screen_v500.py
"""
import sys
import json
import glob
import re
from pathlib import Path
from html import unescape

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loss_detector import detect_lost_content_wordlevel, normalize_for_loss_check, word_count

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "Fareharbor"
TEST_DIR = Path(__file__).resolve().parent

OUTPUT_JSONL = TEST_DIR / "v500_output.jsonl"
SELECTION_CSV = TEST_DIR / "new_500_products_selection.csv"
FAILURES_CSV = TEST_DIR / "v500_failures.csv"

DESC_FIELDS = [
    "redo_desc_about", "redo_desc_highlights", "redo_desc_what_included",
    "redo_desc_what_excluded", "redo_desc_itinerary", "redo_desc_what_to_bring",
    "redo_desc_duration_text", "redo_desc_requirements",
    "redo_desc_cancellation", "redo_desc_check_in",
    "redo_min_age", "redo_max_age", "redo_group_size", "redo_meeting_point",
    "redo_desc_other",
]
BOOKING_FIELDS = [
    "redo_booking_what_to_bring", "redo_booking_what_not_to_bring", "redo_booking_inclusions",
    "redo_booking_location", "redo_booking_check_in", "redo_booking_departure_info",
    "redo_booking_itinerary", "redo_booking_important_info", "redo_booking_cancellation",
    "redo_booking_faqs", "redo_booking_before_arrival", "redo_booking_contact",
    "redo_booking_other",
]
ALL_FIELDS = DESC_FIELDS + BOOKING_FIELDS

BLOCK_TAG_RE = re.compile(r"</?(p|div|h[1-6]|ul|ol|li|br)\b[^>]*>", re.IGNORECASE)
ANY_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text):
    if not text:
        return ""
    text = BLOCK_TAG_RE.sub(" ", text)
    text = ANY_TAG_RE.sub("", text)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def find_raw_file(product_id):
    matches = glob.glob(str(RAW_DIR / f"Fareharbor-*-{product_id}.json"))
    if not matches:
        raise FileNotFoundError(f"No raw JSON found for product_id={product_id}")
    return matches[0]


def get_raw_texts(product_id):
    data = json.loads(Path(find_raw_file(product_id)).read_text(encoding="utf-8"))
    item = data["item"]
    desc_unstripped = item.get("description") or ""
    return strip_html(desc_unstripped), strip_html(item.get("booking_notes") or ""), desc_unstripped


def merge_fields(result_list, field_names):
    merged = {}
    for field in field_names:
        combined = []
        seen = set()
        for result in result_list:
            value = (result or {}).get(field, "")
            if not value:
                continue
            for line in value.split("\n"):
                line = line.strip()
                if not line:
                    continue
                norm = re.sub(r"\s+", " ", line.lower())
                if norm in seen:
                    continue
                seen.add(norm)
                combined.append(line)
        merged[field] = "\n".join(combined)
    return merged


def parse_output_file(output_jsonl, desc_tag="desc-v44", booking_tag="booking-v44"):
    products = {}
    failed_custom_ids = set()
    with open(output_jsonl, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            custom_id = rec.get("custom_id", "")
            parts = custom_id.split("|")
            product_id = parts[0] if parts else None
            call_tag = parts[2] if len(parts) > 2 else None
            entry = products.setdefault(product_id, {"desc_results": [], "booking_results": []})
            error = rec.get("error")
            response = rec.get("response")
            if error is not None or response is None:
                failed_custom_ids.add(custom_id)
                continue
            try:
                content_str = response["body"]["choices"][0]["message"]["content"]
                parsed = json.loads(content_str)
            except (KeyError, IndexError, json.JSONDecodeError, TypeError):
                failed_custom_ids.add(custom_id)
                continue
            if call_tag == desc_tag:
                entry["desc_results"].append(parsed)
            elif call_tag == booking_tag:
                entry["booking_results"].append(parsed)
    return products, failed_custom_ids


def get_field_values(products, pid):
    entry = products.get(pid)
    if not entry:
        return None
    merged_desc = merge_fields(entry["desc_results"], DESC_FIELDS)
    merged_booking = merge_fields(entry["booking_results"], BOOKING_FIELDS)
    return {**merged_desc, **merged_booking}


def determine_source_side(unit_text, raw_desc, raw_booking):
    norm_unit = normalize_for_loss_check(unit_text)
    norm_desc = normalize_for_loss_check(raw_desc)
    norm_booking = normalize_for_loss_check(raw_booking)

    in_desc = norm_unit in norm_desc
    in_booking = norm_unit in norm_booking

    if in_desc and not in_booking:
        return "description"
    if in_booking and not in_desc:
        return "booking_notes"
    if in_desc and in_booking:
        return "description"
    return "unknown"


def run_screen():
    selection_df = pd.read_csv(SELECTION_CSV, dtype={"product_id": str})
    all_product_ids = selection_df["product_id"].tolist()

    winning_products, failed_custom_ids = parse_output_file(OUTPUT_JSONL, "desc-v44", "booking-v44")

    failed_product_ids = set()
    for cid in failed_custom_ids:
        parts = cid.split("|")
        if parts:
            failed_product_ids.add(parts[0])

    # a product is dropped if EITHER its desc or booking call failed/is missing
    usable_product_ids = []
    dropped_rows = []
    for pid in all_product_ids:
        entry = winning_products.get(pid)
        has_desc = bool(entry and entry["desc_results"])
        has_booking = bool(entry and entry["booking_results"])
        if pid in failed_product_ids or not has_desc or not has_booking:
            reason = "desc call failed/missing" if not has_desc else ""
            reason += (" + " if reason and not has_booking else "") + ("booking call failed/missing" if not has_booking else "")
            dropped_rows.append({"product_id": pid, "reason": reason or "in failed_custom_ids"})
        else:
            usable_product_ids.append(pid)

    print(f"Usable products (both calls succeeded): {len(usable_product_ids)} / {len(all_product_ids)}")
    print(f"Dropped products: {len(dropped_rows)}")

    screen_results = {}
    for pid in usable_product_ids:
        field_values = get_field_values(winning_products, pid) or {}
        raw_desc, raw_booking, raw_desc_unstripped = get_raw_texts(pid)
        result = detect_lost_content_wordlevel(raw_desc, raw_booking, field_values)

        enriched_units = []
        for pu in result["problem_units"]:
            side = determine_source_side(pu["unit_text"], raw_desc, raw_booking)
            enriched_units.append({
                "unit_text": pu["unit_text"],
                "coverage_pct": pu["coverage_pct"],
                "status": pu["status"],
                "missing_phrase": pu["missing_phrase"],
                "missing_words": pu["missing_words"],
                "best_field_guess": pu["best_field_guess"],
                "triggers_adjudicator": pu["triggers_adjudicator"],
                "source_side": side,
            })

        screen_results[pid] = {
            "field_values": field_values,
            "raw_desc": raw_desc,
            "raw_booking": raw_booking,
            "input_words": word_count(raw_desc + " " + raw_booking),
            "problem_units": enriched_units,
            "units_missing": result["units_missing"],
            "units_partial": result["units_partial"],
            "units_present": result["units_present"],
            "word_coverage_pct": result["word_coverage_pct"],
        }

    return screen_results, selection_df, dropped_rows


def main():
    screen_results, selection_df, dropped_rows = run_screen()

    print("=" * 80)
    print(f"SCREEN RESULTS ({len(screen_results)} usable products)")
    print("=" * 80)
    total_missing = sum(sum(1 for u in r["problem_units"] if u["status"] == "MISSING") for r in screen_results.values())
    total_partial = sum(sum(1 for u in r["problem_units"] if u["status"] == "PARTIAL") for r in screen_results.values())
    print(f"Total MISSING units: {total_missing}")
    print(f"Total PARTIAL units: {total_partial}")

    if dropped_rows:
        dropped_df = pd.DataFrame(dropped_rows)
        dropped_df.to_csv(TEST_DIR / "v500_screen_dropped.csv", index=False)
        print(f"\nWrote v500_screen_dropped.csv ({len(dropped_rows)} rows)")

    return screen_results, dropped_rows


if __name__ == "__main__":
    main()
