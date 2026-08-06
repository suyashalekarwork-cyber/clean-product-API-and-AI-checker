"""
Build 3 Batch API input JSONLs -- terra / nano / luna -- over the 30 hardest
products, using the NEW V4.7 prompt.

Differences from build_best_model_batches.py, and why:

  PRODUCTS  30 from hard30_products.json, not the 10 in PRODUCT_IDS. These are
            all flag_for_human_review == True and share no products with the
            earlier run, so nothing is comparable to those cached baselines --
            which is why EXISTING_BASELINES is empty here.

  PROMPT    V4.7, not V4.4. V4.7 = V4.4 verbatim + NO DUPLICATION + NO
            INVENTION. V4.6 is deliberately NOT used: it is a measured
            regression (coverage 87.23% -> 85.95%) because its narrowing rules
            made the model drop unclassifiable content.

  BASELINE  gpt-4o-mini is NOT re-run. All 30 products already carry its output
            in v500_post_fix_state.json (that run was gpt-4o-mini on V4.4), so
            the baseline is merged at screen time for free.

Raw text comes from v500_post_fix_state.json rather than re-reading and
re-stripping the source JSON, so every model sees byte-identical input to what
gpt-4o-mini saw. Re-deriving it risks a subtly different strip_html result and
would make the baseline column incomparable.

Usage:
    python build_hard30_batches.py
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_model_comparison_batches import (
    PROMPT_PATH, TEST_DIR, extract_prompt,
    build_desc_user_message, build_booking_user_message, make_request,
)

sys.stdout.reconfigure(encoding="utf-8")

COMPAT_PATH = TEST_DIR / "model_compatibility_final.json"
PRODUCTS_PATH = TEST_DIR / "hard30_products.json"
STATE_PATH = TEST_DIR / "v500_post_fix_state.json"

DESC_VERSION = "SYSTEM_PROMPT_FH_DESC_V4_7"
BOOKING_VERSION = "SYSTEM_PROMPT_FH_BOOKING_V4_7"

MAX_TOKENS = 8000
TEMPERATURE = 0.1

CANDIDATES = ["gpt-5.6-terra", "gpt-5.4-nano", "gpt-5.6-luna"]

# gpt-4o-mini's output for these 30 already exists (V4.4, 500-product run) and
# is merged at screen time. Re-running it would only duplicate work.
REUSED_BASELINE = "gpt-4o-mini"


def load_param_sets():
    """Read each model's parameter set from the verified compatibility matrix.

    Fails loudly rather than guessing -- a wrong parameter set fails the whole
    batch, and guessing is exactly how that happens.
    """
    compat = json.loads(COMPAT_PATH.read_text(encoding="utf-8"))
    cfgs = {}
    for model in CANDIDATES:
        entry = compat.get(model)
        if entry is None:
            raise SystemExit(f"{model} absent from {COMPAT_PATH.name}")
        if entry.get("batch_supported") is not True:
            raise SystemExit(f"{model} is not Batch-compatible per "
                             f"{COMPAT_PATH.name}")
        param_set = entry["param_set"]
        if param_set == "max_tokens":
            cfgs[model] = {"param_set": "max_tokens",
                           "max_tokens": MAX_TOKENS, "temperature": TEMPERATURE}
        else:
            cfgs[model] = {"param_set": "max_completion_tokens",
                           "max_completion_tokens": MAX_TOKENS}
    return cfgs


def main():
    raw_prompts = PROMPT_PATH.read_text(encoding="utf-8")
    desc_prompt = extract_prompt(raw_prompts, DESC_VERSION)
    booking_prompt = extract_prompt(raw_prompts, BOOKING_VERSION)
    print(f"{DESC_VERSION}: {len(desc_prompt):,} chars")
    print(f"{BOOKING_VERSION}: {len(booking_prompt):,} chars")

    # the two new rules must actually be in the prompt being sent
    for rule in ("NO DUPLICATION RULE:", "NO INVENTION RULE:"):
        for name, body in (("desc", desc_prompt), ("booking", booking_prompt)):
            if rule not in body:
                raise SystemExit(f"{rule!r} missing from the {name} prompt -- "
                                 f"V4.7 was not extracted correctly")
    print("  both V4.7 rules present in both prompts")

    product_ids = json.loads(PRODUCTS_PATH.read_text(encoding="utf-8"))["product_ids"]
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))

    missing = [p for p in product_ids if p not in state]
    if missing:
        raise SystemExit(f"no raw text in {STATE_PATH.name} for: {missing}")

    cfgs = load_param_sets()
    print(f"\nParameter sets (from {COMPAT_PATH.name}):")
    for model, cfg in cfgs.items():
        print(f"   {model:<16} {cfg['param_set']}")

    print(f"\nProducts: {len(product_ids)} (hardest 30, all flagged for review)")
    print(f"Baseline reused, not re-run: {REUSED_BASELINE} (V4.4, from "
          f"{STATE_PATH.name})")

    total = 0
    skipped_sides = 0
    for model, cfg in cfgs.items():
        lines = []
        for pid in product_ids:
            desc = state[pid].get("raw_desc") or ""
            booking = state[pid].get("raw_booking") or ""
            # an empty side wastes a call and invites invented content
            if desc.strip():
                lines.append(json.dumps(make_request(
                    f"{pid}|{model}|desc", model, cfg, desc_prompt,
                    build_desc_user_message(desc)), ensure_ascii=False))
            else:
                skipped_sides += 1
            if booking.strip():
                lines.append(json.dumps(make_request(
                    f"{pid}|{model}|booking", model, cfg, booking_prompt,
                    build_booking_user_message(booking)), ensure_ascii=False))
            else:
                skipped_sides += 1
        safe = model.replace(".", "_")
        out = TEST_DIR / f"hard30_batch_{safe}.jsonl"
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        total += len(lines)
        print(f"   wrote {out.name}: {len(lines)} requests")

    print(f"\nTotal: {total} requests across {len(cfgs)} models")
    if skipped_sides:
        print(f"Skipped {skipped_sides} empty side(s) across all models "
              f"({skipped_sides // len(cfgs)} per model)")


if __name__ == "__main__":
    main()
