"""Per-product issue audit for the Rezdy Round 1 run -> reports/rezdy_desc_100_issues.txt.

Every product is checked, and every product appears in the report -- including
the clean ones. A report that lists only failures cannot be used to judge a run,
because "12 issues" means nothing without knowing whether it came from 12
products or 100.

THE CHECKS, and the guard each one carries. Every guard is a false-positive class
that has already been paid for on the Fareharbor side:

  CONTENT LOSS      raw text that reached no field. Uses rezdy_postprocess ->
                    rapidfuzz bands (>=97 kept, 80-96 REWORDED, <80 missing).
                    GUARD: greetings, sign-offs and bare lead-in lines ending in
                    ':' are permitted omissions. Counting them over-reports ~3x.

  REWORDED          present but not verbatim -- the 80-96 band. Invisible to
                    exact matching, and a real defect: the VERBATIM rule exists
                    so a customer reads what the supplier actually wrote.

  URL LOST          a link in the raw that is absent from the output.
                    GUARD: the URL regex swallows trailing punctuation and
                    markdown, so `bagboyz.com/**` and a trailing full stop both
                    made present URLs read as lost. Each candidate is re-checked
                    against the output with punctuation stripped BEFORE being
                    reported.

  INVENTED          words in the output that appear nowhere in the raw.
                    GUARD: the ": " and " - " joiners are permitted by the
                    prompt, and a heading's own text may legitimately be
                    repeated as a label. Single tokens are ignored; only runs of
                    >=4 unseen words are reported.

  MID-SENTENCE      a field value starting part-way through a sentence (the C1
                    defect) -- lowercase first word, or "to/and/so/which/that".

  DUPLICATED        the same sentence in 2+ fields. REPORTED, never removed:
                    deciding which copy is "more specific" is a judgement about
                    meaning made where nobody can see it.

  CONTAMINATION     the prompt's invented operator names appearing in output.
                    Verified at build time that no supplier's raw text contains
                    them, so any hit is provably the model copying our examples.

WHAT THIS REPORT IS NOT: a defect count. It is a NOMINATION LIST. Detector output
on the Fareharbor side over-reported roughly 3x before the guards above were
added, and even after them the counts are an upper bound until a human reads the
raw text. The header says so, and per-product findings are labelled CANDIDATE.
"""
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "data_pipeline" / "batch_api_test"
sys.path.insert(0, str(T))

from booking_common import parse_booking_json                     # noqa: E402
from rezdy_common import RAW_DIR, html_to_markdown                # noqa: E402
from rezdy_postprocess import process_field                       # noqa: E402
from build_rezdy_desc_prompt import COLUMNS                       # noqa: E402
from build_rezdy_desc_100_batch import SENTINELS                  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from build_rezdy_column_definitions import COLUMN_STEMS, norm      # noqa: E402

# RZ_TAG names which run this report describes. Default "rzd1" = V1.
_TAG = os.environ.get("RZ_TAG", "rzd1")
_SFX = "" if _TAG == "rzd1" else f"_{_TAG}"
OUT = ROOT / "reports" / f"rezdy_desc_100_issues{_SFX}.txt"
OUTPUT = T / f"rezdy_desc_100_output{_SFX}.jsonl"
PRODUCTS = T / "rezdy_desc_100_products.json"

CONTENT_COLS = [c for c in COLUMNS if c != "redo_flags"]
URL = re.compile(r"https?://[^\s)\]<>\"']+")
MID = re.compile(r"^\s*(?:[a-z]|to\b|and\b|so\b|which\b|that\b)")
WORD = re.compile(r"[A-Za-z0-9']+")

# Column each stem maps to, for the "filled with no heading" check.
COL_OF = {
    "redo_desc_what_included": "what_included",
    "redo_desc_what_excluded": "what_excluded",
    "redo_desc_highlights": "highlights",
    "redo_desc_itinerary": "itinerary",
    "redo_desc_what_to_bring": "what_to_bring",
    "redo_meeting_point": "meeting_point",
    "redo_desc_cancellation": "cancellation",
    "redo_desc_important_info": "important_info",
    "redo_desc_restrictions": "restrictions",
    "redo_desc_check_in": "check_in",
    "redo_desc_duration_text": "duration_text",
    "redo_desc_accessibility": "accessibility",
    "redo_desc_pricing": "pricing",
    "redo_desc_faqs": "faqs",
    "redo_desc_disclaimers": "disclaimers",
    "redo_group_size": "group_size",
    "redo_desc_health_safety": "health_safety",
    "redo_desc_contact": "contact",
    "redo_desc_extras": "extras",
}


def strip_url(u):
    return u.rstrip(").,;:*_'\"]>").rstrip("*")


def headings_of(conv):
    """Which columns the supplier LICENSED, by heading or inline label.

    Split on `heading OR inline label`, never heading alone: the Fareharbor
    scorer split on markdown headings while the column mapper already honoured
    inline labels, and reported 93 phantom leaks across 36 products.
    """
    cols, heads = set(), []
    for line in conv.split("\n"):
        t = line.strip()
        m = re.match(r"^(?:#{1,6}\s*|\*\*)?([^*#].{0,80}?)(?:\*\*)?\s*:?\s*$", t)
        cand = None
        if t.startswith(("## ", "**")) or (t.endswith(":") and len(t.split()) <= 12):
            cand = m.group(1) if m else t
        else:
            lab = re.match(r"^([A-Za-z][A-Za-z /&'\-]{1,38}):\s+\S", t)
            if lab:
                cand = lab.group(1)
        if not cand:
            continue
        heads.append(cand.strip())
        cols |= licenses(cand)
    return cols, heads


def licenses(heading):
    """EVERY column a heading could license -- not just the first stem to match.

    maps_to_column() is a ROUTER: order matters and first match wins, because a
    heading must land in exactly one column. Licensing is a different question --
    "was the model ALLOWED to fill this?" -- and first-match-wins gives the wrong
    answer for a compound heading.

    Measured false positives from using the router here:
      * PYWRUQ "Important Health and Safety Information" matched `important`
        first, so health_safety read as filled-with-no-heading. The supplier
        named it explicitly.
      * PEVHQL "Suitable for: Beginner, naturally fit" -- the restrictions stem
        list had "suitability" but not "suitable", so the heading licensed
        nothing at all.
    """
    n = norm(heading)
    out = {col for col, stems in COLUMN_STEMS if any(s in n for s in stems)}
    # Stem gaps found by verifying flags against raw text, not by reading code.
    for extra, words in [("restrictions", ["suitable", "who can", "ability"]),
                         ("health_safety", ["health", "safety"]),
                         ("extras", ["option", "upgrade", "customis"]),
                         ("contact", ["contact", "phone", "email", "enquir"])]:
        if any(w in n for w in words):
            out.add(extra)
    return out


def audit(pid, meta, fields):
    raw_path = list(RAW_DIR.glob(f"Rezdy-*-{pid}.json"))[0]
    raw = json.loads(raw_path.read_text(encoding="utf-8"))["product"].get(
        "description") or ""
    conv = html_to_markdown(raw)
    cols = {c: (fields.get(c) or "").strip() for c in CONTENT_COLS}
    issues = []

    # --- content loss + reworded (the safety net)
    rep = process_field(raw, cols, "description")
    for ln in filter(None, rep["recovered_content"].split("\n")):
        issues.append(("CONTENT LOSS", ln.replace("[description] ", "")))
    for ln in filter(None, rep["reworded_content"].split("\n")):
        issues.append(("REWORDED", ln.replace("[description] ", "")))

    # --- URLs. Re-checked with punctuation stripped before reporting.
    out_blob = " ".join(cols.values())
    out_urls = {strip_url(u) for u in URL.findall(out_blob)}
    for u in {strip_url(u) for u in URL.findall(conv)}:
        # Prefix comparison, not equality. A long Google-Maps URL is emitted
        # with a trailing segment trimmed or a character re-encoded, and exact
        # matching called it lost -- PKBUB1's map link is in the output in full.
        if any(u[:60] == o[:60] or u in o or o in u for o in out_urls):
            continue
        issues.append(("URL LOST", u[:150]))

    # --- invented: runs of >=4 output words absent from the raw
    rawset = set(w.lower() for w in WORD.findall(conv))
    for col, val in cols.items():
        if not val:
            continue
        run = []
        for w in WORD.findall(val):
            if w.lower() in rawset:
                if len(run) >= 4:
                    issues.append(("INVENTED", f"{col}: ...{' '.join(run)}..."))
                run = []
            else:
                run.append(w)
        if len(run) >= 4:
            issues.append(("INVENTED", f"{col}: ...{' '.join(run)}..."))

    # --- mid-sentence starts
    for col, val in cols.items():
        if val and MID.match(val):
            issues.append(("MID-SENTENCE", f"{col}: {val[:110]}"))

    # --- filled with no licensing heading
    licensed, heads = headings_of(conv)
    for col, val in cols.items():
        want = COL_OF.get(col)
        if val and want and want not in licensed:
            issues.append(("NO HEADING", f"{col} filled but no heading names it"))

    # --- duplication (reported, never removed)
    for ln in filter(None, rep["duplicate_content"].split("\n")):
        issues.append(("DUPLICATED", ln[:170]))

    # --- prompt contamination
    for s in SENTINELS:
        if s.lower() in out_blob.lower():
            issues.append(("CONTAMINATION", f"prompt example text {s!r} in output"))

    return conv, heads, cols, issues, rep["stats"]


def main():
    meta = {p["product_id"]: p
            for p in json.loads(PRODUCTS.read_text(encoding="utf-8"))}
    rows = []
    for line in OUTPUT.open(encoding="utf-8"):
        r = json.loads(line)
        pid = r["custom_id"].split("|")[0]
        f, note = parse_booking_json(
            r["response"]["body"]["choices"][0]["message"]["content"])
        rows.append((pid, f or {}, note))

    audited, tally = [], Counter()
    for pid, f, note in rows:
        conv, heads, cols, issues, stats = audit(pid, meta.get(pid, {}), f)
        audited.append((pid, conv, heads, cols, issues, stats, note))
        for kind, _ in issues:
            tally[kind] += 1

    audited.sort(key=lambda x: -len(x[4]))
    clean = sum(1 for a in audited if not a[4])

    L = []
    A = L.append
    A("=" * 78)
    A("REZDY ROUND 1 -- DESCRIPTION EXTRACTION, PER-PRODUCT ISSUE LIST")
    A("=" * 78)
    A("")
    A(f"Products         : {len(audited)}  (the 100 HARDEST in the catalogue --")
    A("                   16-55 headings each, up to 2,881 words. The typical")
    A("                   Rezdy product is far simpler, so every rate below is")
    A("                   the PESSIMISTIC end, not what the catalogue will do.)")
    A(f"Prompt           : SYSTEM_PROMPT_RZ_DESC_V1")
    A(f"Clean (no finding): {clean} / {len(audited)}")
    A("")
    A("READ THIS BEFORE QUOTING ANY NUMBER")
    A("-" * 78)
    A("This is a NOMINATION LIST, not a defect count. On the Fareharbor side the")
    A("equivalent detectors over-reported roughly 3x before their guards were")
    A("added, and even now a finding is only confirmed once a human has read the")
    A("supplier's raw text. Treat every line as CANDIDATE until checked.")
    A("")
    A("HAND-VERIFIED SAMPLE -- what survived reading the raw text")
    A("-" * 78)
    A("A sample of findings was checked line by line against the supplier's own")
    A("text before this report was published. Results:")
    A("")
    A("  URL LOST      5 of 5 CONFIRMED REAL. Four are one product (PS0MP2, a")
    A("                Chinese-language description with inline Wikipedia links)")
    A("                and one is PF008R (arrowtown.com). A sixth was a FALSE")
    A("                POSITIVE -- PKBUB1's Google Maps link IS in the output;")
    A("                the checker compared URLs exactly and a long URL differed")
    A("                in its tail. Fixed, and the fix is why this reads 5 not 6.")
    A("")
    A("  NO HEADING    ~2 of 6 sampled survived. EXPECT ROUGHLY A THIRD TO BE")
    A("                REAL. This check asks 'did a heading license this fill?'")
    A("                and answers using our stem list -- which cannot name every")
    A("                supplier wording. Confirmed false positives: 'Numbers on")
    A("                the Day' (licenses group_size), 'Session Length'")
    A("                (duration), 'Gift eCards Available' (extras), and a block")
    A("                of FAQ questions used as headings. All four ARE headings;")
    A("                our stems simply do not list them. CLAUDE.md already")
    A("                records that this mapper cannot be completed -- adding")
    A("                patterns for every topic wording is classification by")
    A("                meaning, the thing heading-gating replaced.")
    A("                Genuine examples that DID survive: PQC41U (content under")
    A("                'Meeting Time' went to check_in, not meeting_point) and")
    A("                P4RRV9 (highlights filled with no highlights heading).")
    A("")
    A("  Two detector bugs were found and fixed by this verification, BEFORE")
    A("  publishing: the licensing check used the router (first stem wins), so a")
    A("  compound heading like 'Important Health and Safety Information' licensed")
    A("  important_info and left health_safety reading as unlicensed; and the URL")
    A("  check compared exactly rather than by prefix.")
    A("")
    A("Findings by type")
    A("-" * 78)
    for kind, n in tally.most_common():
        A(f"  {kind:16s} {n:5d}")
    if not tally:
        A("  (none)")
    A("")
    A("What each type means")
    A("-" * 78)
    A("  CONTENT LOSS   raw text that reached no field at all. Shown with the")
    A("                 heading it sat under, so it can be put back rather than")
    A("                 merely counted.")
    A("  REWORDED       present, but not word-for-word. The model paraphrased.")
    A("  URL LOST       a link in the raw absent from the output.")
    A("  INVENTED       4+ consecutive output words that appear nowhere in raw.")
    A("  MID-SENTENCE   a field value starting part-way through a sentence.")
    A("  NO HEADING     a field filled when no heading or label names it. This")
    A("                 is the failure heading-gating exists to prevent.")
    A("  DUPLICATED     the same sentence in 2+ fields. Reported, never removed.")
    A("  CONTAMINATION  our own prompt example text appearing in real output.")
    A("")
    A("=" * 78)
    A("PER PRODUCT -- worst first")
    A("=" * 78)

    for pid, conv, heads, cols, issues, stats, note in audited:
        m = meta.get(pid, {})
        A("")
        A("-" * 78)
        A(f"{pid}   {m.get('supplier','?')}")
        A(f"  {m.get('name','')[:72]}")
        A(f"  {m.get('n_headings',0)} headings | {len(conv.split()):,} words | "
          f"{sum(1 for v in cols.values() if v)} of {len(cols)} fields filled"
          + (f" | JSON repaired: {note}" if note else ""))
        A(f"  units checked: {stats['units_checked']}")
        if not issues:
            A("  >> NO FINDINGS")
            continue
        A(f"  >> {len(issues)} finding(s) -- CANDIDATE, verify against raw text")
        by = {}
        for kind, detail in issues:
            by.setdefault(kind, []).append(detail)
        for kind in ["CONTAMINATION", "INVENTED", "NO HEADING", "URL LOST",
                     "MID-SENTENCE", "CONTENT LOSS", "REWORDED", "DUPLICATED"]:
            for detail in by.get(kind, []):
                A(f"     [{kind}] {detail[:200]}")
        A(f"  supplier headings: {', '.join(h[:28] for h in heads[:10])}"
          + (" ..." if len(heads) > 10 else ""))

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(L), encoding="utf-8")

    print(f"products     : {len(audited)}")
    print(f"clean        : {clean}")
    for kind, n in tally.most_common():
        print(f"  {kind:16s} {n}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
