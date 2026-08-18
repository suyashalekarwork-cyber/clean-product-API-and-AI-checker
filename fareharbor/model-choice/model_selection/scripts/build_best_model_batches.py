"""
Build 9 Batch API input JSONLs -- one per candidate model -- over the SAME 10
products already used by build_model_comparison_batches.py.

Reusing that product set is the point: gpt-4o-mini, gpt-5.5-pro, gpt-5.6-terra
and gpt-5.4 already have measured results on these exact products, so those four
become free baselines and the 9 new models slot into the same table with no
apples-to-oranges problem.

Everything except the model is held identical to the original run -- same V4.4
prompts, same "=== RAW DESCRIPTION ===" wrapper, same empty-side placeholder,
same custom_id shape. Any deviation would make the new numbers incomparable to
the four baselines, which would defeat the purpose.

Per-model parameter sets are read from model_compatibility_final.json rather
than hardcoded: gpt-4 family needs max_tokens+temperature, gpt-5 family and
o-series need max_completion_tokens only, and sending the wrong one fails the
entire batch.

Usage:
    python build_best_model_batches.py
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_model_comparison_batches import (
    PRODUCT_IDS, PROMPT_PATH, TEST_DIR,
    extract_prompt, find_raw_file, strip_html,
    build_desc_user_message, build_booking_user_message, make_request,
)

sys.stdout.reconfigure(encoding="utf-8")

COMPAT_PATH = TEST_DIR / "model_compatibility_final.json"
MAX_TOKENS = 8000
TEMPERATURE = 0.1

# 9 candidates spanning $15 -> $374 for all 23,034 products, bracketing the
# decision space between gpt-4o-mini ($28, 89.38%) and gpt-5.6-terra
# ($487, 99.13%). Ordered cheapest first.
CANDIDATES = [
    "gpt-5-nano",      # $15
    "gpt-4.1-nano",    # $19
    "gpt-5.6-luna",    # $49
    "gpt-5.4-nano",    # $50
    "gpt-5-mini",      # $75
    "gpt-4.1-mini",    # $75
    "gpt-5.4-mini",    # $183
    "o4-mini",         # $207
    "gpt-5",           # $374
]

# already measured on these same 10 products -- not re-run
EXISTING_BASELINES = ["gpt-4o-mini", "gpt-5.5-pro", "gpt-5.6-terra", "gpt-5.4"]


def load_param_sets():
    """Read each candidate's confirmed parameter set from the compatibility
    matrix. Fails loudly rather than guessing -- a wrong parameter set fails
    the whole batch, and guessing is exactly how that happens."""
    compat = json.loads(COMPAT_PATH.read_text(encoding="utf-8"))
    cfgs = {}
    for model in CANDIDATES:
        entry = compat.get(model)
        if entry is None:
            raise SystemExit(f"{model} not in {COMPAT_PATH.name} -- untested, refusing to guess")
        if entry.get("batch_supported") is not True:
            raise SystemExit(f"{model} is not Batch-compatible ({entry.get('error_code')})")
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
    desc_prompt = extract_prompt(raw_prompts, "SYSTEM_PROMPT_FH_DESC_V4_4")
    booking_prompt = extract_prompt(raw_prompts, "SYSTEM_PROMPT_FH_BOOKING_V4_4")
    print(f"V4.4 desc prompt: {len(desc_prompt):,} chars | "
          f"booking prompt: {len(booking_prompt):,} chars")

    cfgs = load_param_sets()
    print(f"\nParameter sets (from {COMPAT_PATH.name}):")
    for model, cfg in cfgs.items():
        print(f"   {model:<16} {cfg['param_set']}")

    raw_texts = {}
    for pid in PRODUCT_IDS:
        item = json.loads(Path(find_raw_file(pid)).read_text(encoding="utf-8"))["item"]
        raw_texts[pid] = {"desc": strip_html(item.get("description") or ""),
                          "booking": strip_html(item.get("booking_notes") or "")}

    print(f"\nProducts: {len(PRODUCT_IDS)} (same set as the 4 existing baselines)")

    total = 0
    for model, cfg in cfgs.items():
        lines = []
        for pid in PRODUCT_IDS:
            lines.append(json.dumps(make_request(
                f"{pid}|{model}|desc", model, cfg, desc_prompt,
                build_desc_user_message(raw_texts[pid]["desc"])), ensure_ascii=False))
            lines.append(json.dumps(make_request(
                f"{pid}|{model}|booking", model, cfg, booking_prompt,
                build_booking_user_message(raw_texts[pid]["booking"])), ensure_ascii=False))
        safe = model.replace(".", "_")
        out = TEST_DIR / f"bestmodel_batch_{safe}.jsonl"
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        total += len(lines)
        print(f"   wrote {out.name}: {len(lines)} requests")

    print(f"\nTotal: {total} requests across {len(cfgs)} models")
    print(f"Free baselines merged at screen time (not re-run): {EXISTING_BASELINES}")


if __name__ == "__main__":
    main()
