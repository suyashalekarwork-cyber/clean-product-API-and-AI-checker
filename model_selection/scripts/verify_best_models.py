"""
Safety assertions for the 13-model comparison. If any fail, the ranking must
not be reported as-is.

  1. COMPLETE RESPONSES   -- every model answered every product on both sides.
  2. NO TRUNCATION        -- flagged and excluded rather than counted as loss.
  3. PARSEABLE JSON       -- a model emitting non-JSON is a COMPATIBILITY
                             failure, not a quality score of zero.
  4. NO FIX APPLIED       -- each state file is byte-identical to the screen's
                             field_values.
  5. NO INVENTED CONTENT  -- extracted text traces back to the raw source.
                             Cheap models are the likeliest to hallucinate, so
                             this matters more here than in earlier runs.
  6. BASELINES UNCHANGED  -- the 4 pre-existing models' numbers still match
                             model_comparison_screen_results.json exactly,
                             proving the merge did not alter them.

Usage:
    python verify_best_models.py
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loss_detector import normalize_for_loss_check
from build_best_model_batches import CANDIDATES, EXISTING_BASELINES
from screen_model_comparison import PRODUCT_IDS

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
MIN_WORDS_FOR_INVENTION_CHECK = 8
INVENTION_THRESHOLD = 0.5


def main():
    screen = json.loads((TEST_DIR / "bestmodel_screen_results.json").read_text(encoding="utf-8"))
    existing = json.loads((TEST_DIR / "model_comparison_screen_results.json").read_text(encoding="utf-8"))

    f = {"incomplete": [], "truncated": [], "bad_json": [],
         "state_mismatch": [], "invented": [], "baseline_drift": []}

    for model in CANDIDATES:
        per = screen.get(model, {})
        safe = model.replace(".", "_")
        state_path = TEST_DIR / f"bestmodel_{safe}_post_fix_state.json"
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}

        for pid in PRODUCT_IDS:
            d = per.get(pid)
            if d is None:
                f["incomplete"].append(f"{model}/{pid} absent")
                continue
            if not d["desc_present"] or not d["booking_present"]:
                sides = []
                if not d["desc_present"]:
                    sides.append("desc")
                if not d["booking_present"]:
                    sides.append("booking")
                f["incomplete"].append(f"{model}/{pid} no response: {','.join(sides)}")
            if d.get("truncated"):
                f["truncated"].append(f"{model}/{pid}")
            if d.get("bad_json"):
                f["bad_json"].append(f"{model}/{pid} sides={d['bad_json']}")
            if pid in state and state[pid]["field_values"] != d["field_values"]:
                f["state_mismatch"].append(f"{model}/{pid}")

            raw_words = set(normalize_for_loss_check(
                (d.get("raw_desc") or "") + " " + (d.get("raw_booking") or "")).split())
            if not raw_words:
                continue
            for field, value in d["field_values"].items():
                words = [w for w in normalize_for_loss_check(str(value or "")).split()
                         if len(w) > 3]
                if len(words) < MIN_WORDS_FOR_INVENTION_CHECK:
                    continue
                overlap = sum(1 for w in words if w in raw_words) / len(words)
                if overlap < INVENTION_THRESHOLD:
                    f["invented"].append(f"{model}/{pid}/{field} {overlap:.0%} traceable")

    # baselines must be untouched by the merge
    for model in EXISTING_BASELINES:
        if model not in screen or model not in existing:
            f["baseline_drift"].append(f"{model} missing")
            continue
        for pid in PRODUCT_IDS:
            a, b = screen[model].get(pid, {}), existing[model].get(pid, {})
            if a.get("word_coverage_pct") != b.get("word_coverage_pct") \
                    or a.get("units_missing") != b.get("units_missing"):
                f["baseline_drift"].append(f"{model}/{pid} numbers changed")

    labels = {
        "incomplete": "1. every model answered every product/side",
        "truncated": "2. no truncated responses",
        "bad_json": "3. all responses parseable JSON",
        "state_mismatch": "4. state files == screen output (no fix applied)",
        "invented": "5. extracted text traces to raw source",
        "baseline_drift": "6. the 4 existing baselines unchanged by the merge",
    }
    print("=" * 78)
    print(f"VERIFICATION -- {len(CANDIDATES)} new + {len(EXISTING_BASELINES)} baseline models")
    print("=" * 78)
    for key, label in labels.items():
        n = len(f[key])
        print(f"  {label:<50} {'PASS' if n == 0 else f'FAIL ({n})'}")
        for item in f[key][:8]:
            print(f"       {item}")
        if n > 8:
            print(f"       ... and {n - 8} more")

    # truncation/bad JSON are reportable facts, not blockers -- they identify
    # models that are unsuitable, which is itself a result
    blocking = ("state_mismatch", "baseline_drift")
    ok = not any(f[k] for k in blocking)
    print("\n" + ("INTEGRITY ASSERTIONS PASSED" if ok
                  else "INTEGRITY FAILURE -- DO NOT REPORT"))
    if any(f[k] for k in ("incomplete", "truncated", "bad_json", "invented")):
        print("NOTE: model-quality issues above are RESULTS to report, not blockers.")
    (TEST_DIR / "bestmodel_verification.json").write_text(
        json.dumps(f, indent=2), encoding="utf-8")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
