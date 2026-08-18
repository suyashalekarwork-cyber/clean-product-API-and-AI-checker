"""
Build the FULL-CATALOGUE description batch: every Fareharbor product that has a
description, split into chunks the Batch API will accept.

11,069 products with a description (167 have none and are skipped). At ~29 KB
per line -- the 28.5 KB system prompt repeats on every request -- the whole run
is ~330 MB, over the 200 MB batch input limit. So it is written as CHUNKS of
3,500 products (~100 MB each), submitted as separate batches.

Prompt caching makes the repetition cheap rather than wasteful: on the 1,000-run
6,694 of 6,815 prompt tokens came back cached.

Writes v5_3_full_batch_01.jsonl ... and v5_3_full_products.json.
Do NOT commit the batch files.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
ROOT = TEST_DIR.parent.parent
sys.path.insert(0, str(TEST_DIR))

from build_model_comparison_batches import (strip_html, make_request,   # noqa: E402
                                            build_desc_user_message)

MODEL = "gpt-5.6-luna"
PROMPT_VERSION = "SYSTEM_PROMPT_FH_DESC_V5_3"
TAG = "v53full"
CHUNK = 3500
RAW_DIR = ROOT / "data" / "Fareharbor"
PROMPTS_FILE = ROOT / "config" / "fareharbor_prompts.txt"
COMPAT_FILE = TEST_DIR / "model_compatibility_final.json"
SELECTION = TEST_DIR / "v5_3_full_products.json"


def extract_prompt(raw, version):
    v = re.escape(version)
    m = re.search(r"PROMPT:\s*" + v + r"\s*\n.*?\n=+\n\n(.*?)\n\n=+\nEND OF "
                  + v + r"\s*$", raw, re.DOTALL | re.MULTILINE)
    if not m:
        raise SystemExit(f"could not extract {version}")
    return m.group(1).strip()


def load_model_cfg(model):
    entry = json.loads(COMPAT_FILE.read_text(encoding="utf-8"))[model]
    if not entry.get("batch_supported"):
        raise SystemExit(f"{model} does not support the Batch API")
    if entry["param_set"] == "max_tokens":
        return {"param_set": "max_tokens", "max_tokens": 8000, "temperature": 0.1}
    return {"param_set": "max_completion_tokens", "max_completion_tokens": 8000}


def main():
    system_prompt = extract_prompt(
        PROMPTS_FILE.read_text(encoding="utf-8"), PROMPT_VERSION)
    if "redo_booking" in system_prompt:
        raise SystemExit("booking field names leaked into the description prompt")
    print(f"prompt {PROMPT_VERSION}: {len(system_prompt)} chars")

    cfg = load_model_cfg(MODEL)

    requests, skipped = [], 0
    for fp in sorted(RAW_DIR.glob("*.json")):
        pid = fp.stem.split("-")[-1]
        try:
            item = json.loads(fp.read_text(encoding="utf-8")).get("item") or {}
        except Exception:                                          # noqa: BLE001
            skipped += 1
            continue
        sd = item.get("structured_description") or {}
        raw = strip_html(sd.get("description") or item.get("description") or "")
        if not raw.strip():
            skipped += 1
            continue
        requests.append(make_request(
            custom_id=f"{pid}|{MODEL}|desc|{TAG}",
            model=MODEL, model_cfg=cfg,
            system_prompt=system_prompt,
            user_message=build_desc_user_message(raw)))

    ids = [r["custom_id"].split("|")[0] for r in requests]
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate product ids in the batch")

    chunks = [requests[i:i + CHUNK] for i in range(0, len(requests), CHUNK)]
    written = []
    for n, chunk in enumerate(chunks, 1):
        path = TEST_DIR / f"v5_3_full_batch_{n:02d}.jsonl"
        with path.open("w", encoding="utf-8") as fh:
            for r in chunk:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        mb = path.stat().st_size / 1e6
        written.append({"file": path.name, "requests": len(chunk),
                        "size_mb": round(mb, 1)})
        flag = "  <-- OVER 200MB LIMIT" if mb > 200 else ""
        print(f"  {path.name}: {len(chunk):5d} requests, {mb:6.1f} MB{flag}")
        if mb > 200:
            raise SystemExit("chunk exceeds the batch input limit -- lower CHUNK")

    SELECTION.write_text(json.dumps({
        "product_ids": ids, "n": len(ids),
        "selection": "every Fareharbor product with a non-empty description",
        "skipped_no_description": skipped,
        "chunks": written,
    }, indent=1), encoding="utf-8")

    print(f"\nproducts : {len(ids):,}   skipped (no description): {skipped}")
    print(f"chunks   : {len(chunks)}   total "
          f"{sum(c['size_mb'] for c in written):.0f} MB")
    print(f"wrote {SELECTION.name}")


if __name__ == "__main__":
    main()
