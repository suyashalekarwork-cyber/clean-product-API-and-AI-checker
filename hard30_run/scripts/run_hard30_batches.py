"""
Submit the 3 hard30 V4.7 batches, poll concurrently, download outputs.

One job per model so a single failure cannot block the others. Records
per-model completed/failed/wall-clock/tokens, and tracks truncation and
unparseable JSON separately from quality -- a model emitting non-JSON is a
compatibility failure, not a score of zero.

Timeout is 90 minutes, not the 30 used for the 10-product run: gpt-5-mini took
576s on 20 requests there, and these jobs carry 52 each on longer products.

Batch IDs are written to disk immediately after submission, so an interrupted
run can be resumed by re-reading them rather than re-submitting and paying
twice.

Usage:
    python run_hard30_batches.py
"""
import os
import sys
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
IDS_PATH = TEST_DIR / "hard30_batch_ids.json"
RESULTS_PATH = TEST_DIR / "hard30_batch_results.json"

MODELS = ["gpt-5.6-terra", "gpt-5.4-nano", "gpt-5.6-luna"]
TIMEOUT_SECONDS = 90 * 60
POLL_SECONDS = 30


def download(client, model, batch_id, result):
    """Fetch output, tally tokens, flag truncation and bad JSON."""
    batch = client.batches.retrieve(batch_id)
    result["status"] = batch.status
    rc = batch.request_counts
    result["completed"] = rc.completed
    result["failed"] = rc.failed
    result["total"] = rc.total

    if not batch.output_file_id:
        return result

    text = client.files.content(batch.output_file_id).text
    safe = model.replace(".", "_")
    out = TEST_DIR / f"hard30_output_{safe}.jsonl"
    out.write_text(text, encoding="utf-8")

    for line in text.splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        resp = rec.get("response") or {}
        if resp.get("status_code") != 200:
            continue
        body = resp.get("body") or {}
        usage = body.get("usage") or {}
        result["prompt_tokens"] += usage.get("prompt_tokens", 0)
        result["completion_tokens"] += usage.get("completion_tokens", 0)
        choice = (body.get("choices") or [{}])[0]
        if choice.get("finish_reason") not in (None, "stop"):
            result["truncated"].append(rec.get("custom_id"))
        content = (choice.get("message") or {}).get("content")
        if content is not None:
            try:
                json.loads(content)
            except (json.JSONDecodeError, TypeError):
                result["unparseable"].append(rec.get("custom_id"))
    result["output_file"] = out.name
    return result


def run_one(client, model, batch_id, started):
    safe = model.replace(".", "_")
    result = {"model": model, "batch_id": batch_id, "status": "", "completed": 0,
              "failed": 0, "total": 0, "prompt_tokens": 0, "completion_tokens": 0,
              "truncated": [], "unparseable": [], "output_file": ""}
    while True:
        elapsed = time.time() - started
        batch = client.batches.retrieve(batch_id)
        rc = batch.request_counts
        print(f"[{elapsed:.0f}s] {model}: {batch.status} "
              f"{rc.completed}/{rc.total} failed={rc.failed}")
        if batch.status in ("completed", "failed", "expired", "cancelled"):
            result = download(client, model, batch_id, result)
            result["wall_clock_seconds"] = round(elapsed, 1)
            print(f"  [{model}] finished -> {result.get('output_file') or 'NO OUTPUT'}")
            return result
        if elapsed > TIMEOUT_SECONDS:
            result["status"] = "timeout"
            result["wall_clock_seconds"] = round(elapsed, 1)
            print(f"  [{model}] TIMEOUT after {elapsed:.0f}s -- batch {batch_id} "
                  f"is still running; re-run this script to resume")
            return result
        time.sleep(POLL_SECONDS)


def main():
    load_dotenv(TEST_DIR / ".env")
    key = os.environ.get("OPENAI_API_KEY")
    if not key or key == "your_key_here":
        raise SystemExit("OPENAI_API_KEY not set")
    client = OpenAI(api_key=key)

    # resume rather than re-submit: batches already paid for should not be
    # duplicated just because polling was interrupted
    ids = {}
    if IDS_PATH.exists():
        ids = json.loads(IDS_PATH.read_text(encoding="utf-8"))
        print(f"Resuming from {IDS_PATH.name}: {list(ids)}")

    print("=" * 78)
    print(f"SUBMITTING {len([m for m in MODELS if m not in ids])} BATCH JOB(S)")
    print("=" * 78)
    for model in MODELS:
        if model in ids:
            print(f"  [{model}] already submitted: {ids[model]}")
            continue
        safe = model.replace(".", "_")
        path = TEST_DIR / f"hard30_batch_{safe}.jsonl"
        if not path.exists():
            raise SystemExit(f"missing {path.name} -- run build_hard30_batches.py")
        upload = client.files.create(file=open(path, "rb"), purpose="batch")
        batch = client.batches.create(
            input_file_id=upload.id, endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={"description": f"hard30 V4.7 {model}"})
        ids[model] = batch.id
        IDS_PATH.write_text(json.dumps(ids, indent=2), encoding="utf-8")
        print(f"  [{model}] batch_id={batch.id}")

    print("\n" + "=" * 78)
    print(f"POLLING {len(MODELS)} JOBS CONCURRENTLY ({TIMEOUT_SECONDS // 60}-min guard)")
    print("=" * 78)
    started = time.time()
    with ThreadPoolExecutor(max_workers=len(MODELS)) as pool:
        futures = [pool.submit(run_one, client, m, ids[m], started) for m in MODELS]
        results = [f.result() for f in futures]

    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("\n" + "=" * 78)
    print("FINAL")
    print("=" * 78)
    for r in results:
        flags = ""
        if r["truncated"]:
            flags += f"  TRUNCATED x{len(r['truncated'])}"
        if r["unparseable"]:
            flags += f"  BAD JSON x{len(r['unparseable'])}"
        print(f"  {r['model']:<16} {r['status']:<12} {r['completed']}/{r['total']} "
              f"failed={r['failed']} {r.get('wall_clock_seconds', 0)}s "
              f"tok={r['prompt_tokens']:,}/{r['completion_tokens']:,}{flags}")
    print(f"\nWrote {RESULTS_PATH.name}")


if __name__ == "__main__":
    main()
