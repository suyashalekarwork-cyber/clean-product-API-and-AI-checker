"""
AI accuracy checker -- Part B: submit all four judge batches, poll, download.

Submits every model's batch FIRST so they run concurrently, then polls until
all reach a terminal status. Each output is written explicitly to
judge_output_{model}.jsonl (the API names its own output file otherwise).

Usage:
    python run_judge_batches.py
    python run_judge_batches.py --limit 5   # consumes the *_limit5.jsonl inputs
"""
import sys
import os
import time
import json
import argparse
from pathlib import Path

from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
ENV_PATH = TEST_DIR / ".env"
POLL_INTERVAL_SECONDS = 30
TERMINAL = {"completed", "failed", "expired", "cancelled"}

MODELS = ["gpt-4o-mini", "gpt-5.4", "gpt-5.5-pro", "gpt-5.6-terra"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--run", default="v50", help="v50 | v500")
    ap.add_argument("--models", nargs="+", default=MODELS)
    args = ap.parse_args()
    suffix = f"_{args.run}" + (f"_limit{args.limit}" if args.limit else "")
    models = args.models

    load_dotenv(ENV_PATH)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or api_key == "your_key_here":
        print(f"OPENAI_API_KEY is missing in {ENV_PATH}.")
        sys.exit(1)

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    print("=" * 80)
    print("STEP 1 — UPLOAD + CREATE ALL BATCHES")
    print("=" * 80)
    jobs = {}
    for model in models:
        inp = TEST_DIR / f"judge_batch_{model}{suffix}.jsonl"
        if not inp.exists():
            print(f"  MISSING input {inp.name} — run build_judge_batches.py first")
            sys.exit(1)
        with open(inp, "rb") as f:
            uploaded = client.files.create(file=f, purpose="batch")
        batch = client.batches.create(
            input_file_id=uploaded.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )
        jobs[model] = batch.id
        print(f"  {model:16s} file={uploaded.id}  batch={batch.id}")

    (TEST_DIR / f"judge_batch_ids{suffix}.json").write_text(
        json.dumps(jobs, indent=2), encoding="utf-8"
    )

    print("\n" + "=" * 80)
    print("STEP 2 — POLL")
    print("=" * 80)
    statuses = {m: "validating" for m in models}
    while any(s not in TERMINAL for s in statuses.values()):
        time.sleep(POLL_INTERVAL_SECONDS)
        parts = []
        for model, bid in jobs.items():
            if statuses[model] in TERMINAL:
                parts.append(f"{model}={statuses[model]}")
                continue
            b = client.batches.retrieve(bid)
            statuses[model] = b.status
            c = b.request_counts
            parts.append(f"{model}={b.status}({c.completed}/{c.total},f={c.failed})")
        print("  " + " | ".join(parts), flush=True)

    print("\n" + "=" * 80)
    print("STEP 3 — DOWNLOAD")
    print("=" * 80)
    failed_any = False
    for model, bid in jobs.items():
        b = client.batches.retrieve(bid)
        out = TEST_DIR / f"judge_output_{model}{suffix}.jsonl"
        if b.status == "completed" and b.output_file_id:
            client.files.content(b.output_file_id).write_to_file(out)
            print(f"  {model:16s} -> {out.name}")
            if b.error_file_id:
                err = TEST_DIR / f"judge_errors_{model}{suffix}.jsonl"
                client.files.content(b.error_file_id).write_to_file(err)
                print(f"  {model:16s} PARTIAL FAILURES -> {err.name}")
        else:
            failed_any = True
            print(f"  {model:16s} ENDED '{b.status}' — no output")
            if b.error_file_id:
                print(client.files.content(b.error_file_id).text[:2000])

    print("\nDONE" + ("  (with failures — see above)" if failed_any else ""))


if __name__ == "__main__":
    main()
