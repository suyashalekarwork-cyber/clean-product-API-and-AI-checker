"""
Build the V5 test batch: 10 hard products x gpt-5.6-luna x SYSTEM_PROMPT_FH_DESC_V5.

Description side ONLY -- booking notes are out of scope for V5.
One request per product => 10 requests.

Reuses strip_html / find_raw_file / build_desc_user_message / make_request from
build_model_comparison_batches.py unchanged.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
ROOT = TEST_DIR.parent.parent
sys.path.insert(0, str(TEST_DIR))

from build_model_comparison_batches import (  # noqa: E402
    strip_html,
    find_raw_file,
    build_desc_user_message,
    make_request,
)

MODEL = "gpt-5.6-luna"
PROMPT_VERSION = "SYSTEM_PROMPT_FH_DESC_V5_3"
N_PRODUCTS = 500
PROMPTS_FILE = ROOT / "config" / "fareharbor_prompts.txt"
COMPAT_FILE = TEST_DIR / "model_compatibility_final.json"
HARD30 = TEST_DIR / "hard500_products.json"
OUT_JSONL = TEST_DIR / "v5_3_hard500_batch.jsonl"


def extract_prompt(raw, version):
    """Exact-version block extractor (same contract as build_v500_batch_jsonl)."""
    import re
    v = re.escape(version)
    pattern = (
        r"PROMPT:\s*" + v + r"\s*\n"
        r".*?\n=+\n\n"
        r"(.*?)"
        r"\n\n=+\nEND OF " + v + r"\s*$"
    )
    m = re.search(pattern, raw, re.DOTALL | re.MULTILINE)
    if not m:
        raise RuntimeError(f"Could not extract prompt body for {version}")
    return m.group(1).strip()


def load_model_cfg(model):
    data = json.loads(COMPAT_FILE.read_text(encoding="utf-8"))
    entry = data.get(model) if isinstance(data, dict) else None
    if entry is None and isinstance(data, dict):
        for section in data.values():
            if isinstance(section, dict) and model in section:
                entry = section[model]
                break
    if entry is None:
        raise SystemExit(f"{model} not found in model_compatibility_final.json")
    if entry.get("batch_supported") is not True:
        raise SystemExit(f"{model} is not Batch-compatible ({entry.get('error_code')})")
    # The compat file records param_set only; the caller supplies the limits.
    # Same values as build_best_model_batches.py (MAX_TOKENS=8000, TEMPERATURE=0.1).
    if entry["param_set"] == "max_tokens":
        return {"param_set": "max_tokens", "max_tokens": 8000, "temperature": 0.1}
    return {"param_set": "max_completion_tokens", "max_completion_tokens": 8000}


def main():
    system_prompt = extract_prompt(
        PROMPTS_FILE.read_text(encoding="utf-8"), PROMPT_VERSION
    )
    print(f"prompt {PROMPT_VERSION}: {len(system_prompt)} chars")
    # Guard: V5 must not carry the removed catch-all field.
    if "redo_desc_other" in system_prompt:
        raise SystemExit("V5 prompt still references redo_desc_other")

    cfg = load_model_cfg(MODEL)
    print(f"model {MODEL}: param_set={cfg['param_set']}")

    ids = json.loads(HARD30.read_text(encoding="utf-8"))["product_ids"][:N_PRODUCTS]
    print(f"products: {ids}")

    requests, skipped = [], []
    for pid in ids:
        try:
            path = find_raw_file(pid)
        except (FileNotFoundError, RuntimeError) as exc:
            skipped.append((pid, str(exc)))
            continue
        item = json.loads(Path(path).read_text(encoding="utf-8")).get("item", {})
        sd = item.get("structured_description") or {}
        raw_desc = strip_html(sd.get("description") or item.get("description") or "")
        if not raw_desc:
            skipped.append((pid, "empty description"))
            continue
        requests.append(
            make_request(
                custom_id=f"{pid}|{MODEL}|desc|v5_3",
                model=MODEL,
                model_cfg=cfg,
                system_prompt=system_prompt,
                user_message=build_desc_user_message(raw_desc),
            )
        )

    with OUT_JSONL.open("w", encoding="utf-8") as fh:
        for r in requests:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\nwrote {OUT_JSONL.name}: {len(requests)} requests")
    if skipped:
        print("SKIPPED:")
        for pid, why in skipped:
            print(f"  {pid}: {why}")


if __name__ == "__main__":
    main()
