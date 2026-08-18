"""
Submit a reviewer batch to the OpenAI Batch API and poll until done.

    python run_review_batch.py --set validation73
    python run_review_batch.py --set validation73 --pass 2
    python run_review_batch.py --set random1000

Clone of run_v5_3_random1000_batch.py. EXPECTED comes from the input file's own
line count rather than a hard-coded constant, because pass 2 only covers the
products pass 1 flagged.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv  # noqa: E402
from openai import OpenAI  # noqa: E402

TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))
load_dotenv(TEST_DIR / ".env")

from build_review_batch import parse_content  # noqa: E402

POLL_INTERVAL = 20
TIMEOUT_SECONDS = 300 * 60

STEMS = {
    (1, "validation73"): "review_validation73",
    (1, "random1000"): "review_random1000",
    (2, "validation73"): "review_verify_validation73",
    (2, "random1000"): "review_verify_random1000",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", dest="which", choices=["validation73", "random1000"], required=True)
    ap.add_argument("--pass", dest="which_pass", type=int, choices=[1, 2], default=1)
    args = ap.parse_args()

    stem = STEMS[(args.which_pass, args.which)]
    in_jsonl = TEST_DIR / (stem + "_batch.jsonl")
    out_jsonl = TEST_DIR / (stem + "_output.jsonl")
    err_jsonl = TEST_DIR / (stem + "_errors.jsonl")

    if not in_jsonl.exists():
        raise SystemExit("missing input: %s -- build it first" % in_jsonl.name)

    n_in = sum(1 for _ in in_jsonl.open(encoding="utf-8"))
    if n_in == 0:
        raise SystemExit("%s is empty -- nothing to submit" % in_jsonl.name)
    size_mb = in_jsonl.stat().st_size / 1e6
    print("uploading %s (%d requests, %.1f MB) ..." % (in_jsonl.name, n_in, size_mb))

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    upload = client.files.create(file=in_jsonl.open("rb"), purpose="batch")
    batch = client.batches.create(
        input_file_id=upload.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    print("batch id: %s" % batch.id)

    start = time.time()
    while True:
        batch = client.batches.retrieve(batch.id)
        elapsed = int(time.time() - start)
        c = batch.request_counts
        print("  [%4ds] %s  completed=%s/%s failed=%s"
              % (elapsed, batch.status, c.completed, c.total, c.failed))
        if batch.status in ("completed", "failed", "expired", "cancelled"):
            break
        if elapsed > TIMEOUT_SECONDS:
            raise SystemExit("timed out after %ds (status=%s)" % (elapsed, batch.status))
        time.sleep(POLL_INTERVAL)

    if batch.output_file_id:
        out_jsonl.write_text(client.files.content(batch.output_file_id).text, encoding="utf-8")
        print("wrote %s" % out_jsonl.name)
    if batch.error_file_id:
        err_jsonl.write_text(client.files.content(batch.error_file_id).text, encoding="utf-8")
        print("wrote %s  <-- ERRORS PRESENT" % err_jsonl.name)

    if out_jsonl.exists():
        truncated = unparseable = ok = repaired = 0
        for line in out_jsonl.open(encoding="utf-8"):
            choice = json.loads(line)["response"]["body"]["choices"][0]
            if choice.get("finish_reason") != "stop":
                truncated += 1
            text = choice["message"]["content"]
            try:
                json.loads(text.strip())
                ok += 1
            except Exception:
                try:
                    parse_content(text)
                    ok += 1
                    repaired += 1
                except Exception:
                    unparseable += 1
        print("\nparsed ok: %d (of which repaired: %d)   truncated: %d   unparseable: %d"
              % (ok, repaired, truncated, unparseable))
        if n_in != ok + unparseable:
            print("WARNING: %d requests in, %d responses out" % (n_in, ok + unparseable))


if __name__ == "__main__":
    main()
