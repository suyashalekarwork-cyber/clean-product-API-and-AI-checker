"""
Pass 2 of the V5.3 reviewer -- adversarial verification, flagged products only.

Reads pass 1's output, keeps only the products that came back with at least one
finding, and asks a fresh call to knock each finding down. Cheap, because most
products have no findings at all.

    python build_review_verify_batch.py --set validation73
    python build_review_verify_batch.py --set random1000

Prior art for why this pass exists (qa_bot_v2/GENERALISATION_FINDING.md, 50
blind products): judge alone -> false-alarm rate 0.423; judge + adversarial
verifier -> 0.038, with precision 0.514 -> 0.638.

custom_id = {product_id}|{model}|verify|rev1
"""
import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

import review_contract as rc  # noqa: E402
from build_model_comparison_batches import make_request  # noqa: E402
from build_v5_3_random1000_batch import load_model_cfg  # noqa: E402
from build_review_batch import (  # noqa: E402
    MODEL, REV, build_user_message, load_extractions, parse_content, raw_description, select,
)

FINDING_FIELDS = ["check", "owner", "severity", "confidence", "column",
                  "target_column", "placement", "evidence", "explanation"]


def load_pass1(stem):
    """{product_id: review dict} from a pass-1 output JSONL."""
    path = TEST_DIR / (stem + "_output.jsonl")
    if not path.exists():
        raise SystemExit("missing pass-1 output: %s -- run pass 1 first" % path.name)
    out, bad = {}, []
    for line in path.open(encoding="utf-8"):
        row = json.loads(line)
        pid = row["custom_id"].split("|")[0]
        try:
            out[pid] = parse_content(row["response"]["body"]["choices"][0]["message"]["content"])
        except Exception as exc:
            bad.append((pid, str(exc)))
    if bad:
        print("  WARNING unparseable pass-1 rows: %d %s" % (len(bad), bad[:5]))
    return out


def render_findings(findings):
    lines = ["=== FINDINGS RAISED AGAINST THIS EXTRACTION ==="]
    for i, f in enumerate(findings, 1):
        lines.append("")
        lines.append("FINDING %d" % i)
        for k in FINDING_FIELDS:
            v = (f.get(k) or "").strip() if isinstance(f.get(k), str) else f.get(k)
            if v:
                lines.append("  %-14s %s" % (k + ":", v))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", dest="which", choices=["validation73", "random1000"], required=True)
    args = ap.parse_args()

    stem = "review_" + args.which
    out_path = TEST_DIR / ("review_verify_" + args.which + "_batch.jsonl")

    system_prompt = rc.verify_prompt()
    print("prompt %s + live contract: %d chars" % (rc.VERIFY_VERSION, len(system_prompt)))
    cfg = load_model_cfg(MODEL)

    reviews = load_pass1(stem)
    print("pass-1 responses: %d" % len(reviews))

    flagged = {p: r for p, r in reviews.items() if r.get("findings")}
    n_findings = sum(len(r["findings"]) for r in flagged.values())
    print("flagged products: %d  (%.1f%%)   findings: %d"
          % (len(flagged), 100.0 * len(flagged) / max(1, len(reviews)), n_findings))
    if not flagged:
        out_path.write_text("", encoding="utf-8")
        print("nothing to verify -- wrote empty %s" % out_path.name)
        return

    source = dict(select(args.which))
    caches = {}
    requests, skipped = [], []
    for pid in sorted(flagged):
        fn = source.get(pid)
        if fn is None:
            skipped.append((pid, "not in the selected set"))
            continue
        if fn not in caches:
            caches[fn] = load_extractions(fn)
        cols = caches[fn].get(pid)
        if cols is None:
            skipped.append((pid, "no extraction in " + fn))
            continue
        try:
            raw = raw_description(pid)
        except (FileNotFoundError, RuntimeError) as exc:
            skipped.append((pid, str(exc)))
            continue
        user = (build_user_message(pid, raw, cols) + "\n\n"
                + render_findings(flagged[pid]["findings"]))
        requests.append(make_request(
            custom_id="%s|%s|verify|%s" % (pid, MODEL, REV),
            model=MODEL,
            model_cfg=cfg,
            system_prompt=system_prompt,
            user_message=user,
        ))

    with out_path.open("w", encoding="utf-8") as fh:
        for r in requests:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("\nwrote %s: %d requests, %.1f MB"
          % (out_path.name, len(requests), out_path.stat().st_size / 1e6))
    if skipped:
        print("SKIPPED %d: %s" % (len(skipped), skipped[:10]))


if __name__ == "__main__":
    main()
