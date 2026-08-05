"""
Screen the 9 candidate models' raw output and merge with the 4 already-measured
models into one 13-model table on identical products.

NO PASTE FIX -- raw extraction quality only.

The 4 existing baselines are read verbatim from model_comparison_screen_results
.json rather than recomputed, so their published numbers cannot drift. The merge
is asserted afterwards in verify_best_models.py.

Also writes per-model state files so the judge can be run later without a
rebuild. The "_post_fix_state" suffix is a naming convention required by
build_judge_batches.py, NOT a claim that a fix ran -- no fix is applied here.

Usage:
    python screen_best_models.py
"""
import sys
import json
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loss_detector import detect_lost_content_wordlevel, word_count
from screen_model_comparison import (
    DESC_FIELDS, BOOKING_FIELDS, ALL_FIELDS, PRODUCT_IDS, get_raw_texts,
)
from build_best_model_batches import CANDIDATES, EXISTING_BASELINES

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
OUT_SCREEN = TEST_DIR / "bestmodel_screen_results.json"
EXISTING_PATH = TEST_DIR / "model_comparison_screen_results.json"


def parse_output(path):
    """{pid: {'desc': dict|None, 'booking': dict|None, 'finish': {...},
              'bad_json': [sides]}}"""
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


def screen_model(model):
    safe = model.replace(".", "_")
    products = parse_output(TEST_DIR / f"bestmodel_output_{safe}.jsonl")
    per_product, state = {}, {}

    for pid in PRODUCT_IDS:
        entry = products.get(pid, {"desc": None, "booking": None,
                                   "finish": {}, "bad_json": []})
        field_values = {}
        for f in DESC_FIELDS:
            field_values[f] = (entry.get("desc") or {}).get(f, "")
        for f in BOOKING_FIELDS:
            field_values[f] = (entry.get("booking") or {}).get(f, "")

        raw_desc, raw_booking = get_raw_texts(pid)
        det = detect_lost_content_wordlevel(raw_desc, raw_booking, field_values)
        bad_finish = {s: r for s, r in entry["finish"].items() if r not in (None, "stop")}

        per_product[pid] = {
            "field_values": field_values, "raw_desc": raw_desc, "raw_booking": raw_booking,
            "input_words": word_count(raw_desc + " " + raw_booking),
            "word_coverage_pct": det["word_coverage_pct"],
            "units_missing": det["units_missing"],
            "units_partial": det["units_partial"],
            "units_present": det["units_present"],
            "desc_present": entry.get("desc") is not None,
            "booking_present": entry.get("booking") is not None,
            "truncated": bool(bad_finish),
            "bad_json": entry["bad_json"],
        }
        state[pid] = {"field_values": field_values,
                      "raw_desc": raw_desc, "raw_booking": raw_booking}

    (TEST_DIR / f"bestmodel_{safe}_post_fix_state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return per_product


def main():
    all_results = {}

    for model in CANDIDATES:
        all_results[model] = screen_model(model)

    # merge the 4 baselines verbatim -- do not recompute
    existing = json.loads(EXISTING_PATH.read_text(encoding="utf-8"))
    for model in EXISTING_BASELINES:
        if model in existing:
            all_results[model] = existing[model]
        else:
            print(f"  WARNING: baseline {model} missing from {EXISTING_PATH.name}")

    OUT_SCREEN.write_text(json.dumps(all_results, ensure_ascii=False, indent=2),
                          encoding="utf-8")

    rows = []
    for model, per in all_results.items():
        vals = list(per.values())
        n_missing_resp = sum(1 for v in vals
                             if not v.get("desc_present") or not v.get("booking_present"))
        rows.append({
            "model": model,
            "source": "NEW" if model in CANDIDATES else "existing",
            "avg_coverage_pct": round(sum(v["word_coverage_pct"] for v in vals) / len(vals), 2),
            "total_missing": sum(v["units_missing"] for v in vals),
            "total_partial": sum(v["units_partial"] for v in vals),
            "avg_fields_filled": round(sum(
                sum(1 for x in v["field_values"].values() if str(x).strip())
                for v in vals) / len(vals), 1),
            "products_missing_a_response": n_missing_resp,
            "truncated": sum(1 for v in vals if v.get("truncated")),
            "bad_json": sum(len(v.get("bad_json", [])) for v in vals),
        })
    df = pd.DataFrame(rows).sort_values("avg_coverage_pct", ascending=False)

    print("=" * 92)
    print(f"13-MODEL TABLE -- {len(PRODUCT_IDS)} identical products, raw output, no paste fix")
    print("=" * 92)
    print(df.to_string(index=False))
    print(f"\nWrote {OUT_SCREEN.name}")
    print("Wrote per-model bestmodel_{model}_post_fix_state.json "
          "(raw output; judge-script naming convention, NO fix applied)")
    return df


if __name__ == "__main__":
    main()
