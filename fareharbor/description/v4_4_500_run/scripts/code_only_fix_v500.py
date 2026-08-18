"""
Isolated POC: Step 5 -- pure CODE-ONLY fix for the 50-product round.
Identical logic to code_only_fix.py (30-product round): no AI calls, no
keyword routing. Every MISSING unit's full sentence is pasted verbatim
into its home bucket (description -> redo_desc_about, booking_notes ->
redo_booking_other). PARTIAL units recorded, not touched.

Usage:
    python code_only_fix_v500.py
"""
import sys
import json
import copy
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loss_detector import normalize_for_loss_check

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
SNAPSHOT_PATH = TEST_DIR / "v500_pre_fix_state.json"

HOME_BUCKET = {
    "description": "redo_desc_about",
    "booking_notes": "redo_booking_other",
}


def main():
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    working_copy = copy.deepcopy(snapshot)

    paste_records = []
    partial_records = []

    for pid, entry in snapshot.items():
        fields_dict = working_copy[pid]["field_values"]

        for pu in entry["problem_units"]:
            if pu["status"] == "MISSING":
                sentence = pu["unit_text"].strip()
                source_side = pu["source_side"]
                home_bucket = HOME_BUCKET.get(source_side, "redo_desc_about")

                current_value = fields_dict.get(home_bucket, "") or ""
                norm_sentence = normalize_for_loss_check(sentence)
                already_present_lines = [normalize_for_loss_check(l) for l in current_value.split("\n") if l.strip()]
                already_present = norm_sentence in already_present_lines

                if already_present:
                    paste_records.append({
                        "product_id": pid, "sentence": sentence, "source_side": source_side,
                        "home_bucket": home_bucket, "was_already_present": True, "action": "skipped_duplicate",
                    })
                    continue

                new_value = (current_value + "\n" + sentence).strip() if current_value else sentence
                fields_dict[home_bucket] = new_value

                paste_records.append({
                    "product_id": pid, "sentence": sentence, "source_side": source_side,
                    "home_bucket": home_bucket, "was_already_present": False, "action": "pasted",
                })
                print(f"  [{pid}] PASTED -> {home_bucket} ({source_side}): {sentence[:70]}...")

            elif pu["status"] == "PARTIAL":
                partial_records.append({
                    "product_id": pid, "unit_text": pu["unit_text"], "coverage_pct": pu["coverage_pct"],
                    "missing_phrase": pu["missing_phrase"], "source_side": pu["source_side"],
                    "action": "recorded_only",
                })

    n_pasted = sum(1 for r in paste_records if r["action"] == "pasted")
    n_skipped_dup = sum(1 for r in paste_records if r["action"] == "skipped_duplicate")

    print(f"\nTotal MISSING units processed: {len(paste_records)}")
    print(f"Pasted: {n_pasted}")
    print(f"Skipped as duplicate: {n_skipped_dup}")
    print(f"PARTIAL units recorded (not touched): {len(partial_records)}")

    paste_df = pd.DataFrame(paste_records)
    partial_df = pd.DataFrame(partial_records)

    paste_df.to_csv(TEST_DIR / "code_only_fix_v500_paste_records.csv", index=False)
    partial_df.to_csv(TEST_DIR / "code_only_fix_v500_partial_records.csv", index=False)

    post_fix_state = {}
    for pid in snapshot:
        post_fix_state[pid] = {
            "field_values": working_copy[pid]["field_values"],
            "raw_desc": snapshot[pid]["raw_desc"],
            "raw_booking": snapshot[pid]["raw_booking"],
        }
    with open(TEST_DIR / "v500_post_fix_state.json", "w", encoding="utf-8") as f:
        json.dump(post_fix_state, f, ensure_ascii=False, indent=2)

    print(f"\nWrote code_only_fix_v500_paste_records.csv ({len(paste_df)} rows)")
    print(f"Wrote code_only_fix_v500_partial_records.csv ({len(partial_df)} rows)")
    print(f"Wrote v500_post_fix_state.json")

    return paste_df, partial_df, post_fix_state


if __name__ == "__main__":
    main()

