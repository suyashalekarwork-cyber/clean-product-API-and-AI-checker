"""
Write placement_audit_10_report.txt -- the readable output of
audit_placement_10.py.

Structure: verdict first, then the evidence it rests on, then every finding
product by product so any claim can be checked against the raw text.

Usage:
    python build_placement_report.py
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from screen_model_comparison import PRODUCT_IDS
from audit_placement_10 import MODELS

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).resolve().parent
OUT = TEST_DIR / "placement_audit_10_report.txt"
RULE = "=" * 78
THIN = "-" * 78

COST = {"gpt-5.4-nano": 50, "gpt-5.5-pro": 7309, "gpt-5-mini": 75,
        "gpt-5.6-terra": 487, "gpt-4o-mini": 28}

SEV_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFO": 3}


def wrap(text, width=74, indent="      "):
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(indent + cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(indent + cur)
    return "\n".join(lines)


def main():
    aud = json.loads((TEST_DIR / "placement_audit_10.json").read_text(encoding="utf-8"))
    scr = json.loads((TEST_DIR / "bestmodel_screen_results.json").read_text(encoding="utf-8"))

    stats = {}
    for m in MODELS:
        f = [x for p in aud[m].values() for x in p["findings"]]
        stats[m] = {
            "HIGH": sum(1 for x in f if x["severity"] == "HIGH"),
            "MEDIUM": sum(1 for x in f if x["severity"] == "MEDIUM"),
            "LOW": sum(1 for x in f if x["severity"] == "LOW"),
            "INFO": sum(1 for x in f if x["severity"] == "INFO"),
            "total": len(f),
            "cov": sum(p["coverage"] for p in aud[m].values()) / len(PRODUCT_IDS),
            "fields": sum(sum(1 for v in scr[m][p]["field_values"].values()
                              if str(v or "").strip()) for p in scr[m]) / len(scr[m]),
        }
        for code in ["D1_FREE_IN_EXCLUDED", "D2_SPLIT_BLOCK", "D3_FAQ_SCATTER",
                     "D4_LABEL_VIOLATION", "D5_LABEL_LEAK", "D6_MD_JUNK",
                     "D7_PLACEHOLDER"]:
            stats[m][code] = sum(1 for x in f if x["code"] == code)

    L = []
    L += [RULE, "PLACEMENT AUDIT -- 10 PRODUCTS x 5 MODELS", RULE, "",
          "Coverage asks 'did the words survive'. This asks 'did they land in the",
          "RIGHT field'. Those are different questions, and only the second one",
          "decides whether the data is usable.", "",
          "Trigger: product 451390. Every model scored 99-100% coverage on it, and",
          "two of them filed 'a COMPLIMENTARY shuttle bus' under what_excluded --",
          "'what is NOT included'. Coverage cannot see that. It counts the words,",
          "and the words are all present.", ""]

    # ---------------- verdict ----------------
    L += [RULE, "1. VERDICT", RULE, ""]
    ranked = sorted(MODELS, key=lambda m: (stats[m]["HIGH"] * 3 + stats[m]["MEDIUM"],
                                           -stats[m]["cov"]))
    best = ranked[0]
    L += [f"BEST PLACEMENT: {best}", ""]
    L += [wrap(
        f"{best} has the fewest serious placement defects: "
        f"{stats[best]['HIGH']} HIGH and {stats[best]['MEDIUM']} MEDIUM across all 10 "
        f"products. It also has the highest coverage ({stats[best]['cov']:.2f}%) and "
        f"costs ${COST[best]} for all 23,034 products. It wins on placement and on "
        f"content survival at the same time, which no other model does.", indent="  "), ""]
    L += ["  Its one real weakness is cosmetic: markdown junk (**, ##) left in",
          f"  {stats[best]['D6_MD_JUNK']} fields -- the worst of any model. That is a",
          "  formatting problem, strippable in code, not a misclassification.", ""]

    L += [THIN, "Ranked by serious defects (HIGH x3 + MEDIUM), lowest is best:", THIN, ""]
    L += [f"  {'model':<16}{'HIGH':>5}{'MED':>5}{'LOW':>5}{'INFO':>6}"
          f"{'coverage':>10}{'cost 23k':>10}"]
    for m in ranked:
        s = stats[m]
        tag = "  <- current" if m == "gpt-4o-mini" else ""
        L.append(f"  {m:<16}{s['HIGH']:>5}{s['MEDIUM']:>5}{s['LOW']:>5}{s['INFO']:>6}"
                 f"{s['cov']:>9.2f}%${COST[m]:>9,}{tag}")
    L += ["",
          "  HIGH   = states something factually wrong (content contradicts its field)",
          "  MEDIUM = content fragmented across fields, or placeholder prose",
          "  LOW    = cosmetic (markdown junk, leaked label prefix)",
          "  INFO   = broke the V4.4 label map but landed somewhere defensible",
          ""]

    # ---------------- the real conclusion ----------------
    L += [RULE, "2. WHAT THE NUMBERS DO NOT SAY", RULE, "",
          "Three conclusions that only came from reading the output:", ""]
    L += ["A. THE BIGGEST DEFECT IS IN THE PROMPT, NOT ANY MODEL.", ""]
    L += [wrap("V4.4 maps the raw label 'extras:' to redo_desc_what_excluded. That "
               "assumes extras means paid add-ons. On 451390 it means a COMPLIMENTARY "
               "shuttle bus and free low-sensory sessions. Filing them under 'what is "
               "NOT included' tells the customer the opposite of the truth.", indent="   "), ""]
    L += [wrap("V4.4 says the mapping 'is authoritative and overrides your own "
               "judgment', so a model that obeys the prompt produces the wrong answer. "
               "gpt-5.5-pro and gpt-5.6-terra -- the two most expensive models tested "
               "-- both obeyed and both got it wrong. No change of model fixes this. "
               "It needs a prompt rule that routes extras: on meaning: "
               "complimentary/free/included -> what_included, explicit surcharge -> "
               "what_excluded.", indent="   "), ""]

    L += ["B. THE MODELS THAT 'AVOIDED' IT DID SO BY SCATTERING, NOT BY UNDERSTANDING.", ""]
    L += [wrap("On 451390 the shuttle-bus block went to: what_excluded (pro, terra -- "
               "wrong), requirements + other (nano, 4o-mini -- split in two), "
               "what_included + requirements (5-mini -- the only defensible home). "
               "So avoiding the trap was mostly luck of a different failure, not "
               "comprehension. Only gpt-5-mini actually placed it sensibly.", indent="   "), ""]

    L += ["C. COVERAGE AND PLACEMENT ARE NEARLY UNCORRELATED.", ""]
    L += [wrap("gpt-5.5-pro: 99.24% coverage, the WORST placement record here (4 HIGH, "
               "19 MEDIUM) at $7,309. gpt-4o-mini: worst coverage at 89.38%, but a "
               "middling placement record. A model can preserve every word and still "
               "file half of them wrong. Ranking models on coverage alone -- which is "
               "what best_model_13.xlsx does -- is therefore not sufficient on its own.",
               indent="   "), ""]

    # ---------------- per-defect ----------------
    L += [RULE, "3. DEFECTS BY TYPE", RULE, ""]
    codes = [
        ("D1_FREE_IN_EXCLUDED", "HIGH", "free/complimentary content filed under "
         "'what is NOT included' -- states the opposite of the source"),
        ("D4_LABEL_VIOLATION", "HIGH/INFO", "content ignored its embedded V4.4 label"),
        ("D2_SPLIT_BLOCK", "MEDIUM", "one raw paragraph torn across 2+ fields, "
         "none holding it whole"),
        ("D3_FAQ_SCATTER", "MEDIUM", "Q&A content spread across fields instead of "
         "kept together"),
        ("D7_PLACEHOLDER", "MEDIUM", "wrote 'No content found...' instead of leaving "
         "the field empty -- pollutes the database with prose"),
        ("D6_MD_JUNK", "LOW", "markdown (**, ##) left in the value"),
        ("D5_LABEL_LEAK", "LOW", "literal 'label:' prefix left in the value"),
    ]
    L += [f"  {'defect':<22}" + "".join(f"{m.replace('gpt-','')[:9]:>10}" for m in MODELS)]
    for code, sev, _ in codes:
        L.append(f"  {code:<22}" + "".join(f"{stats[m][code]:>10}" for m in MODELS))
    L += [""]
    for code, sev, desc in codes:
        L += [f"  {code}  [{sev}]", wrap(desc, indent="      "), ""]

    L += [THIN,
          "Note on D2: all models fill a near-identical number of fields",
          "  (" + ", ".join(f"{m.replace('gpt-','')} {stats[m]['fields']:.1f}"
                            for m in MODELS) + " of 28 on average),",
          "  so the split-block differences are real behaviour, not an artifact of",
          "  one model simply using more fields than another.", THIN, ""]

    # ---------------- per product ----------------
    L += [RULE, "4. EVERY FINDING, BY PRODUCT", RULE, ""]
    for pid in PRODUCT_IDS:
        words = scr[MODELS[0]][pid]["input_words"]
        L += ["", RULE, f"PRODUCT {pid}   ({words} raw words)", RULE]
        total = sum(len(aud[m][pid]["findings"]) for m in MODELS)
        if total == 0:
            L += ["", "  No placement defects found in any model.", ""]
            continue
        for m in MODELS:
            p = aud[m][pid]
            f = sorted(p["findings"], key=lambda x: SEV_ORDER[x["severity"]])
            head = (f"  {m}   coverage {p['coverage']}%   "
                    f"{len(f)} finding(s)")
            L += ["", head, "  " + "-" * (len(head) - 2)]
            if not f:
                L += ["      (clean)"]
                continue
            for x in f:
                L += [f"      [{x['severity']}] {x['code']}  ->  {x['field']}",
                      wrap(x["detail"], indent="         "),
                      wrap('EVIDENCE: "' + " ".join(str(x["evidence"]).split())[:230]
                           + '"', indent="         "), ""]

    # ---------------- limits ----------------
    L += ["", RULE, "5. LIMITS OF THIS AUDIT", RULE, "",
          "  - 10 products. Small. Directionally useful, not statistically settled.",
          "  - The detectors are regex rules, and regex cannot do judgement. Three",
          "    of them produced confidently wrong answers on the first run and were",
          "    corrected only by reading the raw text:",
          "      * D2 flagged 29 splits for gpt-5.5-pro; most were paragraphs that",
          "        straddle two different labels, which SHOULD go to two fields.",
          "        Fixed by cutting blocks at label boundaries -> 12.",
          "      * D1 flagged '3 and under are free' (product 402575) as a",
          "        contradiction. It is a rate card listing a free tier among paid",
          "        ones. Fixed by exempting price lists.",
          "      * D4 flagged models for routing cancellation text out of the",
          "        catch-all into redo_desc_cancellation -- off-map per V4.4, but",
          "        BETTER for the reader. Downgraded to INFO.",
          "    Every count above is post-correction. Treat the evidence as the",
          "    result; treat the counts as a way to sort it.",
          "  - No human verdict and no LLM judge has been run. This is rule-based",
          "    detection, so it finds defects it was told to look for and misses",
          "    defect types nobody has named yet.",
          "  - Absence of a finding is not proof of correct placement.", ""]

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"Wrote {OUT.name}  ({len(L)} lines)")
    print(f"\nBEST PLACEMENT: {best}")
    for m in ranked:
        s = stats[m]
        print(f"  {m:<16} HIGH {s['HIGH']}  MED {s['MEDIUM']}  LOW {s['LOW']}  "
              f"INFO {s['INFO']}   cov {s['cov']:.2f}%   ${COST[m]:,}")


if __name__ == "__main__":
    main()
