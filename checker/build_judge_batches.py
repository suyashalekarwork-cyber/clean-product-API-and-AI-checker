"""
AI accuracy checker -- Part A: build the Batch API input JSONLs.

One request per product per model. Each request shows the judge the raw source
text plus every NON-EMPTY redo_* field for that product, and asks for a
placement verdict per field (CORRECT / WRONG_FIELD / GARBLED).

Read-only: consumes v50_post_fix_state.json, writes only judge_batch_*.jsonl.

Usage:
    python build_judge_batches.py                      # v50, 4-model panel
    python build_judge_batches.py --limit 5            # dry-run subset
    python build_judge_batches.py --run v500 \
        --models gpt-5.5-pro                           # v500, single judge
"""
import sys
import json
import re
import argparse
from pathlib import Path

from judge_fields import definitions_block

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent.parent
PROMPT_PATH = PROJECT_ROOT / "config" / "fareharbor_prompts.txt"
PROMPT_VERSION = "SYSTEM_PROMPT_FH_JUDGE_V1"
JUDGE_TAG = "judge_v1"

# Parameter sets come from the verified matrix in model_compatibility.md.
# gpt-4 family: max_tokens + temperature. gpt-5 family: max_completion_tokens
# only, no temperature (the API rejects it).
MODELS = {
    "gpt-4o-mini": {"param_set": "max_tokens", "max_tokens": 8000, "temperature": 0.1},
    "gpt-5.4": {"param_set": "max_completion_tokens", "max_completion_tokens": 8000},
    "gpt-5.5-pro": {"param_set": "max_completion_tokens", "max_completion_tokens": 8000},
    "gpt-5.6-terra": {"param_set": "max_completion_tokens", "max_completion_tokens": 8000},
}


def extract_prompt(raw, version):
    """Pull one prompt body out of fareharbor_prompts.txt by EXACT version."""
    v = re.escape(version)
    pattern = (
        r"PROMPT:\s*" + v + r"\b"
        r".*?\n=+\n\n"
        r"(.*?)"
        r"\n\n=+\nEND OF " + v + r"\s*$"
    )
    m = re.search(pattern, raw, re.DOTALL | re.MULTILINE)
    if not m:
        raise RuntimeError(f"Could not extract prompt body for {version}")
    return m.group(1).strip()


def build_system_prompt():
    raw = PROMPT_PATH.read_text(encoding="utf-8")
    body = extract_prompt(raw, PROMPT_VERSION)
    if "{FIELD_DEFINITIONS}" not in body:
        raise RuntimeError("Judge prompt is missing the {FIELD_DEFINITIONS} placeholder")
    return body.replace("{FIELD_DEFINITIONS}", definitions_block())


def nonempty_fields(field_values):
    return {k: v for k, v in field_values.items() if v and str(v).strip()}


def build_user_message(product_id, raw_desc, raw_booking, fields):
    lines = [
        f"PRODUCT ID: {product_id}",
        "",
        "=== RAW DESCRIPTION (context only) ===",
        raw_desc if raw_desc and raw_desc.strip() else "(empty)",
        "",
        "=== RAW BOOKING NOTES (context only) ===",
        raw_booking if raw_booking and raw_booking.strip() else "(empty)",
        "",
        f"=== EXTRACTED FIELDS TO JUDGE ({len(fields)} fields) ===",
    ]
    for name, val in fields.items():
        lines.append(f"[{name}]")
        lines.append(str(val))
        lines.append("")
    lines.append(
        f"Return exactly {len(fields)} verdicts, one for each field name shown above."
    )
    return "\n".join(lines)


def make_request(custom_id, model, cfg, system_prompt, user_message):
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }
    if cfg["param_set"] == "max_tokens":
        body["max_tokens"] = cfg["max_tokens"]
        body["temperature"] = cfg["temperature"]
    else:
        body["max_completion_tokens"] = cfg["max_completion_tokens"]
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": body,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None,
                    help="only build requests for the first N products")
    ap.add_argument("--run", default="v50",
                    help="which extraction run to judge: v50 | v500")
    ap.add_argument("--models", nargs="+", default=list(MODELS),
                    help="subset of judge models to build batches for")
    args = ap.parse_args()

    for m in args.models:
        if m not in MODELS:
            raise SystemExit(f"Unknown model {m}; known: {list(MODELS)}")
    models = {m: MODELS[m] for m in args.models}

    state_path = TEST_DIR / f"{args.run}_post_fix_state.json"
    if not state_path.exists():
        raise SystemExit(f"No such state file: {state_path}")

    system_prompt = build_system_prompt()
    state = json.loads(state_path.read_text(encoding="utf-8"))

    product_ids = list(state)
    if args.limit:
        product_ids = product_ids[: args.limit]

    suffix = f"_{args.run}" + (f"_limit{args.limit}" if args.limit else "")

    total_fields = 0
    skipped = []
    per_model_counts = {}

    for model, cfg in models.items():
        out_path = TEST_DIR / f"judge_batch_{model}{suffix}.jsonl"
        n = 0
        with open(out_path, "w", encoding="utf-8") as f:
            for pid in product_ids:
                rec = state[pid]
                fields = nonempty_fields(rec["field_values"])
                if not fields:
                    if model == list(models)[0]:
                        skipped.append(pid)
                    continue
                if model == list(models)[0]:
                    total_fields += len(fields)
                msg = build_user_message(
                    pid, rec.get("raw_desc", ""), rec.get("raw_booking", ""), fields
                )
                req = make_request(
                    f"{pid}|{model}|{JUDGE_TAG}", model, cfg, system_prompt, msg
                )
                f.write(json.dumps(req, ensure_ascii=False) + "\n")
                n += 1
        per_model_counts[model] = n
        print(f"{out_path.name}: {n} requests")

    print()
    print(f"Products considered : {len(product_ids)}")
    print(f"Products skipped (no non-empty fields): {len(skipped)} {skipped}")
    print(f"Field-judgements per model: {total_fields}")
    print(f"Total requests across {len(models)} models: {sum(per_model_counts.values())}")


if __name__ == "__main__":
    main()
