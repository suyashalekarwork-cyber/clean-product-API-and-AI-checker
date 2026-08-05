"""
Submit and poll the 9 candidate-model batches concurrently.

One job per model so a single model's failure cannot block the others -- cheap
models are the most likely to fail in ways the others do not, and a model that
errors or emits unparseable JSON is a compatibility result, not a quality
result.

Usage:
    python run_best_model_batches.py
"""
import os
import sys
import time
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_best_model_batches import CANDIDATES

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
load_dotenv(TEST_DIR / ".env")

RESULTS_JSON = TEST_DIR / "bestmodel_batch_results.json"
TIMEOUT_SECONDS = 30 * 60
POLL_INTERVAL = 30


def safe(model):
    return model.replace(".", "_")


def finalize(client, model, batch, started):
    """Download output/errors and tally tokens + truncation for one model."""
    result = {
        "model": model, "batch_id": batch.id, "status": batch.status,
        "wall_clock_seconds": round(time.time() - started, 1),
        "requests_completed": getattr(batch.request_counts, "completed", 0),
        "requests_failed": getattr(batch.request_counts, "failed", 0),
        "expected": 20, "prompt_tokens": 0, "completion_tokens": 0,
        "truncated": [], "unparseable": [],
    }
    if batch.output_file_id:
        text = client.files.content(batch.output_file_id).text
        (TEST_DIR / f"bestmodel_output_{safe(model)}.jsonl").write_text(text, encoding="utf-8")
        for line in text.strip().split("\n"):
            if not line.strip():
                continue
            rec = json.loads(line)
            body = (rec.get("response") or {}).get("body", {})
            usage = body.get("usage", {})
            result["prompt_tokens"] += usage.get("prompt_tokens", 0)
            result["completion_tokens"] += usage.get("completion_tokens", 0)
            for choice in body.get("choices", []):
                if choice.get("finish_reason") not in (None, "stop"):
                    result["truncated"].append({"custom_id": rec.get("custom_id"),
                                                "finish_reason": choice.get("finish_reason")})
                # a cheap model emitting non-JSON is a compatibility failure,
                # not a zero score -- record it distinctly
                content = (choice.get("message") or {}).get("content")
                if content is not None:
                    try:
                        json.loads(content)
                    except (json.JSONDecodeError, TypeError):
                        result["unparseable"].append(rec.get("custom_id"))
    if batch.error_file_id:
        (TEST_DIR / f"bestmodel_errors_{safe(model)}.jsonl").write_text(
            client.files.content(batch.error_file_id).text, encoding="utf-8")
    return result


def main():
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    print("=" * 78)
    print(f"SUBMITTING {len(CANDIDATES)} BATCH JOBS (one per model)")
    print("=" * 78)
    jobs = {}
    for model in CANDIDATES:
        path = TEST_DIR / f"bestmodel_batch_{safe(model)}.jsonl"
        upload = client.files.create(file=open(path, "rb"), purpose="batch")
        batch = client.batches.create(input_file_id=upload.id,
                                      endpoint="/v1/chat/completions",
                                      completion_window="24h")
        jobs[model] = {"batch_id": batch.id, "started": time.time(), "done": False}
        print(f"  [{model}] batch_id={batch.id}")

    print("\n" + "=" * 78)
    print(f"POLLING {len(jobs)} JOBS CONCURRENTLY (30-min guard each)")
    print("=" * 78)

    results = {}
    while any(not j["done"] for j in jobs.values()):
        for model, job in jobs.items():
            if job["done"]:
                continue
            elapsed = time.time() - job["started"]
            b = client.batches.retrieve(job["batch_id"])
            counts = b.request_counts
            print(f"[{elapsed:.0f}s] {model}: {b.status} "
                  f"{getattr(counts, 'completed', 0)}/{getattr(counts, 'total', 0)} "
                  f"failed={getattr(counts, 'failed', 0)}")

            if b.status in ("completed", "failed", "expired", "cancelled"):
                results[model] = finalize(client, model, b, job["started"])
                job["done"] = True
                print(f"  [{model}] finished -> bestmodel_output_{safe(model)}.jsonl")
            elif elapsed > TIMEOUT_SECONDS:
                results[model] = {"model": model, "batch_id": job["batch_id"],
                                  "status": "TIMEOUT", "wall_clock_seconds": round(elapsed, 1),
                                  "requests_completed": getattr(counts, "completed", 0),
                                  "requests_failed": getattr(counts, "failed", 0),
                                  "expected": 20, "prompt_tokens": 0, "completion_tokens": 0,
                                  "truncated": [], "unparseable": []}
                job["done"] = True
                print(f"  [{model}] TIMEOUT after {TIMEOUT_SECONDS}s -- other models continue")
        if any(not j["done"] for j in jobs.values()):
            time.sleep(POLL_INTERVAL)

    RESULTS_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("\n" + "=" * 78)
    print("FINAL")
    print("=" * 78)
    for model in CANDIDATES:
        r = results.get(model, {})
        flags = []
        if r.get("truncated"):
            flags.append(f"TRUNCATED x{len(r['truncated'])}")
        if r.get("unparseable"):
            flags.append(f"BAD JSON x{len(r['unparseable'])}")
        print(f"  {model:<16} {r.get('status'):<12} "
              f"{r.get('requests_completed')}/{r.get('expected')} "
              f"failed={r.get('requests_failed')} "
              f"{r.get('wall_clock_seconds')}s "
              f"tok={r.get('prompt_tokens', 0):,}/{r.get('completion_tokens', 0):,}"
              + ("  " + ", ".join(flags) if flags else ""))
    print(f"\nWrote {RESULTS_JSON.name}")


if __name__ == "__main__":
    main()
