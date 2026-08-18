"""
Build the Batch API input for SYSTEM_PROMPT_FH_BOOKING_V5 on the 100 selected
booking products.

Mirrors build_v5_3_hard100_batch.py, with three differences:
  - reads item.booking_notes, not structured_description.description
  - uses the booking user-message header, not the description one
  - custom_id carries a `booking|bv5` tag so no loader can confuse this run with
    a description run (every V5.x desc run tags `desc|v5_x`)

Writes booking_v5_100_batch.jsonl. Do NOT commit that file -- the 26 KB system
prompt is repeated on every line.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
ROOT = TEST_DIR.parent.parent
sys.path.insert(0, str(TEST_DIR))

from build_model_comparison_batches import make_request        # noqa: E402
from booking_common import load_raw                            # noqa: E402

MODEL = "gpt-5.6-luna"
PROMPT_VERSION = "SYSTEM_PROMPT_FH_BOOKING_V5_3"
TAG = "bv53"
PROMPTS_FILE = ROOT / "config" / "fareharbor_prompts.txt"
COMPAT_FILE = TEST_DIR / "model_compatibility_final.json"
SELECTION = TEST_DIR / "booking100_products.json"
OUT_JSONL = TEST_DIR / "booking_v5_3_100_batch.jsonl"

EXPECTED_KEYS = [
    "redo_booking_notes",
    "redo_booking_highlights",
    "redo_booking_what_to_bring",
    "redo_booking_what_not_to_bring",
    "redo_booking_what_included",
    "redo_booking_what_excluded",
    "redo_booking_extras",
    "redo_booking_meeting_point",
    "redo_booking_check_in",
    "redo_booking_before_arrival",
    "redo_booking_departure_info",
    "redo_booking_itinerary",
    "redo_booking_duration_text",
    "redo_booking_important_info",
    "redo_booking_health_safety",
    "redo_booking_restrictions",
    "redo_booking_special_requirements",
    "redo_booking_accessibility",
    "redo_booking_group_size",
    "redo_booking_cancellation",
    "redo_booking_disclaimers",
    "redo_booking_pricing",
    "redo_booking_faqs",
    "redo_booking_contact",
    "redo_booking_flags",
]



def extract_prompt(raw, version):
    """Exact-version extraction -- V5 must never partial-match a future V5_1."""
    v = re.escape(version)
    pattern = (r"PROMPT:\s*" + v + r"\s*\n"
               r".*?\n=+\n\n"
               r"(.*?)"
               r"\n\n=+\nEND OF " + v + r"\s*$")
    m = re.search(pattern, raw, re.DOTALL | re.MULTILINE)
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


def build_booking_user_message(raw_booking_notes):
    content = raw_booking_notes if raw_booking_notes else "No content found in raw text."
    return f"=== RAW BOOKING NOTES (source of truth) ===\n{content}"


def main():
    system_prompt = extract_prompt(
        PROMPTS_FILE.read_text(encoding="utf-8"), PROMPT_VERSION)

    # Guards: the F1 trap (a desc field name leaking into a booking prompt) and
    # the schema itself. Both would fail silently at analysis time otherwise.
    leaked = sorted(set(re.findall(r"redo_desc_\w+", system_prompt)))
    if leaked:
        raise SystemExit(f"desc field names leaked into the booking prompt: {leaked}")
    for k in EXPECTED_KEYS:
        if f'"{k}": ""' not in system_prompt:
            raise SystemExit(f"prompt schema line is missing {k}")
    print(f"prompt {PROMPT_VERSION}: {len(system_prompt)} chars, "
          f"{len(EXPECTED_KEYS)} keys, no desc leakage")

    cfg = load_model_cfg(MODEL)
    sel = json.loads(SELECTION.read_text(encoding="utf-8"))
    ids = sel["product_ids"]

    requests, skipped = [], []
    total_chars = 0
    for pid in ids:
        try:
            _, raw_bn = load_raw(pid)
        except RuntimeError as exc:
            skipped.append((pid, str(exc)))
            continue
        if not raw_bn.strip():
            skipped.append((pid, "empty booking notes"))
            continue
        total_chars += len(raw_bn)
        requests.append(make_request(
            custom_id=f"{pid}|{MODEL}|booking|{TAG}",
            model=MODEL,
            model_cfg=cfg,
            system_prompt=system_prompt,
            user_message=build_booking_user_message(raw_bn),
        ))

    with OUT_JSONL.open("w", encoding="utf-8") as fh:
        for r in requests:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"selected      : {len(ids)}")
    print(f"requests built: {len(requests)}")
    if skipped:
        print(f"skipped       : {len(skipped)}  {skipped[:5]}")
    print(f"raw booking chars sent: {total_chars}")
    print(f"wrote {OUT_JSONL.name} "
          f"({OUT_JSONL.stat().st_size / 1e6:.1f} MB -- do not commit)")


if __name__ == "__main__":
    main()
