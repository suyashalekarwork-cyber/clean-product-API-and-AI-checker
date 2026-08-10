"""
Run the Fareharbor description extraction over the 100-product sample.

Self-contained: everything it needs is in luna100_run/. No imports from the
wider project.

    python run_extraction.py --build                 # build the JSONL only, no API calls, free
    python run_extraction.py                         # build + submit + wait + download
    python run_extraction.py --version V4_8_2        # run an older prompt version

The batch id is written to disk immediately after submission, so an interrupted
run resumes the same job instead of submitting -- and paying for -- a second one.

Parameters are read from data/model_compatibility_final.json, never hardcoded:
the gpt-5 family accepts max_completion_tokens ONLY and rejects max_tokens and
temperature. The wrong set fails the whole batch, not one request.

Cost: ~$0.42 per full run of 166 requests. Typical wall time 3-4 minutes.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PROMPTS = ROOT / "prompts"
OUT = ROOT / "output"

MODEL = "gpt-5.6-luna"
BOOKING_VERSION = "SYSTEM_PROMPT_FH_BOOKING_V4_7"   # unchanged since V4.7
MAX_COMPLETION_TOKENS = 8000
POLL_SECONDS = 30
TIMEOUT_SECONDS = 90 * 60

# These two strings must stay byte-identical to the originals or the run will not
# reproduce. Verified against the submitted batch files.
EMPTY = "No content found in raw text for this field."
DESC_USER = "=== RAW DESCRIPTION (source of truth) ===\n{text}"
BOOKING_USER = "=== RAW BOOKING NOTES (source of truth) ===\n{text}"


def load_prompt(version):
    p = PROMPTS / f"{version}.txt"
    if not p.exists():
        avail = ", ".join(sorted(f.stem for f in PROMPTS.glob("*.txt")))
        raise SystemExit(f"{p.name} not found.\nAvailable: {avail}")
    body = p.read_text(encoding="utf-8")
    for rule in ("NO DUPLICATION RULE:", "NO INVENTION RULE:"):
        if rule not in body:
            raise SystemExit(f"{rule!r} missing from {p.name} -- refusing to run")
    return body


def build(desc_version, batch_input):
    desc_prompt = load_prompt(desc_version)
    booking_prompt = load_prompt(BOOKING_VERSION)

    compat = json.loads((DATA / "model_compatibility_final.json")
                        .read_text(encoding="utf-8")).get(MODEL)
    if not compat or compat.get("batch_supported") is not True:
        raise SystemExit(f"{MODEL} is not Batch-compatible")
    if compat["param_set"] != "max_completion_tokens":
        raise SystemExit(f"unexpected param_set {compat['param_set']!r}")

    meta = json.loads((DATA / "luna100_products.json").read_text(encoding="utf-8"))
    state = json.loads((DATA / "luna100_screen_results.json")
                       .read_text(encoding="utf-8"))[MODEL]

    lines, skipped = [], 0
    for pid in meta["product_ids"]:
        rec = state[pid]
        for side, prompt, tmpl, text in (
            ("desc", desc_prompt, DESC_USER, rec.get("raw_desc") or ""),
            ("booking", booking_prompt, BOOKING_USER, rec.get("raw_booking") or ""),
        ):
            if not text.strip():
                skipped += 1
                continue
            lines.append(json.dumps({
                "custom_id": f"{pid}|{MODEL}|{side}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": tmpl.format(text=text or EMPTY)},
                    ],
                    "max_completion_tokens": MAX_COMPLETION_TOKENS,
                },
            }, ensure_ascii=False))

    # LF endings: git's autocrlf has previously rewritten a batch file such that
    # the stored blob no longer parsed as JSON
    batch_input.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Built {batch_input.name}: {len(lines)} requests "
          f"({batch_input.stat().st_size // 1024} KB), {skipped} empty sides skipped")
    return len(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="SYSTEM_PROMPT_FH_DESC_V4_8_3",
                    help="description prompt version (default: the newest)")
    ap.add_argument("--build", action="store_true",
                    help="build the JSONL only, no API calls")
    args = ap.parse_args()

    # accepts "V4_8_3", "v4.8.3", "4.8.3" or the full block name
    v = args.version
    if not v.startswith("SYSTEM_PROMPT"):
        short = v.lstrip("vV").replace(".", "_")
        v = f"SYSTEM_PROMPT_FH_DESC_V{short}"
    tag = v.replace("SYSTEM_PROMPT_FH_DESC_", "").lower()

    OUT.mkdir(exist_ok=True)
    batch_input = OUT / f"batch_input_{tag}.jsonl"
    batch_id_file = OUT / f"batch_id_{tag}.json"
    output = OUT / f"luna100_{tag}_output.jsonl"
    errors = OUT / f"luna100_{tag}_errors.jsonl"

    print(f"Prompt: {v}\nOutput: {output.name}\n")
    expected = build(v, batch_input)
    if args.build:
        print("\n--build: nothing submitted, no cost incurred.")
        return

    load_dotenv(ROOT.parent / ".env")
    load_dotenv(ROOT / ".env")
    key = os.environ.get("OPENAI_API_KEY")
    if not key or key == "your_key_here":
        raise SystemExit("OPENAI_API_KEY not set -- copy .env.example to .env "
                         "and put your key in it")
    client = OpenAI(api_key=key)

    if batch_id_file.exists():
        batch_id = json.loads(batch_id_file.read_text(encoding="utf-8"))["batch_id"]
        print(f"Resuming existing batch {batch_id}")
    else:
        up = client.files.create(file=open(batch_input, "rb"), purpose="batch")
        batch = client.batches.create(
            input_file_id=up.id, endpoint="/v1/chat/completions",
            completion_window="24h", metadata={"description": f"luna100 {v}"})
        batch_id = batch.id
        batch_id_file.write_text(json.dumps({"batch_id": batch_id}, indent=2),
                                 encoding="utf-8")
        print(f"Submitted. Batch ID: {batch_id}")

    started = time.time()
    while True:
        batch = client.batches.retrieve(batch_id)
        rc = batch.request_counts
        print(f"  [{int(time.time() - started):>5}s] {batch.status:<12} "
              f"{rc.completed}/{rc.total} failed={rc.failed}")
        if batch.status == "completed":
            break
        if batch.status in ("failed", "expired", "cancelled"):
            if batch.error_file_id:
                errors.write_text(client.files.content(batch.error_file_id).text,
                                  encoding="utf-8")
            raise SystemExit(f"batch ended: {batch.status}")
        if time.time() - started > TIMEOUT_SECONDS:
            raise SystemExit("timed out -- re-run to resume the same batch")
        time.sleep(POLL_SECONDS)

    text = client.files.content(batch.output_file_id).text
    output.write_text(text, encoding="utf-8", newline="\n")
    n = sum(1 for line in text.splitlines() if line.strip())
    print(f"\nDone. {n}/{expected} responses -> output/{output.name}")
    print(f"Now run:  python review_output.py --run {output.name}")


if __name__ == "__main__":
    main()
