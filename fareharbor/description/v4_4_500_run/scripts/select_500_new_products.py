"""
Isolated POC: select 500 brand-new Fareharbor products (never used in any
prior round: 30-set, 50-set, or the original 62-ID exclusion list),
stratified by input_words band, all <= 650 words.

Usage:
    python select_500_new_products.py
"""
import sys
import json
import glob
import re
from pathlib import Path
from html import unescape

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "Fareharbor"
TEST_DIR = Path(__file__).resolve().parent

EARLIER_EXPLICIT_IDS = {
    "619007", "741753", "636674", "472222", "668879", "64164", "608854", "380139", "175603",
    "713979", "686074", "393743", "485873", "170699", "344037", "156951", "276176", "130667",
    "588582", "727695", "185473", "182336", "332514", "529954", "682796", "191337", "480030",
    "427366", "484405", "699063", "100110", "100271",
}

BLOCK_TAG_RE = re.compile(r"</?(p|div|h[1-6]|ul|ol|li|br)\b[^>]*>", re.IGNORECASE)
ANY_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text):
    if not text:
        return ""
    text = BLOCK_TAG_RE.sub(" ", text)
    text = ANY_TAG_RE.sub("", text)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def word_count(text):
    return len([w for w in text.split() if w])


def parse_filename_id(filename):
    stem = Path(filename).stem
    parts = stem.split("-")
    return parts[-1], "-".join(parts[1:-1])


def build_exclude_ids():
    exclude = set(EARLIER_EXPLICIT_IDS)

    d30 = pd.read_excel(TEST_DIR / "v45test_30products_v2.xlsx", sheet_name="Summary", dtype={"product_id": str})
    exclude |= set(d30["product_id"].tolist())

    d50 = pd.read_csv(TEST_DIR / "new_50_products_selection.csv", dtype={"product_id": str})
    exclude |= set(d50["product_id"].tolist())

    print(f"Exclusion list built: {len(EARLIER_EXPLICIT_IDS)} explicit + "
          f"{d30['product_id'].nunique()} from 30-set + {d50['product_id'].nunique()} from 50-set "
          f"= {len(exclude)} unique excluded IDs")
    return exclude


def scan_all_products(exclude_ids):
    files = glob.glob(str(RAW_DIR / "Fareharbor-*.json"))
    rows = []
    for fpath in files:
        pid, alias = parse_filename_id(fpath)
        if pid in exclude_ids:
            continue
        try:
            data = json.loads(Path(fpath).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        item = data.get("item")
        if not item:
            continue
        desc = strip_html(item.get("description") or "")
        booking = strip_html(item.get("booking_notes") or "")
        if not desc and not booking:
            continue
        input_words = word_count(desc + " " + booking)
        if input_words > 650:
            continue
        rows.append({"product_id": pid, "supplier_alias": alias, "input_words": input_words})
    return pd.DataFrame(rows)


def main():
    exclude_ids = build_exclude_ids()

    print("\nScanning data/Fareharbor/ for candidate products (excluding all prior-round IDs, <=650 words)...")
    df = scan_all_products(exclude_ids)
    print(f"Total candidate products scanned: {len(df)}")

    bands = [
        ("0-200", 0, 200, 200),
        ("201-350", 201, 350, 150),
        ("351-500", 351, 500, 90),
        ("501-650", 501, 650, 60),
    ]

    selected_parts = []
    already_picked_ids = set()
    shortfalls = []

    for band_label, lo, hi, n_requested in bands:
        pool = df[(df["input_words"] >= lo) & (df["input_words"] <= hi) & (~df["product_id"].isin(already_picked_ids))].copy()
        n_available = len(pool)
        n_take = min(n_requested, n_available)
        print(f"\nBand {band_label}: pool size = {n_available}, requested {n_requested}, taking {n_take}")
        if n_take < n_requested:
            shortfalls.append((band_label, n_requested, n_take))
            print(f"  SHORTFALL: {n_requested - n_take} short in this band")

        picked = pool.sample(n=n_take, random_state=42).copy()
        picked["band"] = band_label
        selected_parts.append(picked)
        already_picked_ids |= set(picked["product_id"].tolist())

    total_requested = sum(b[3] for b in bands)
    total_selected = sum(len(p) for p in selected_parts)
    shortfall_total = total_requested - total_selected
    if shortfall_total > 0:
        print(f"\nTotal shortfall across bands: {shortfall_total}. Topping up from the next band down...")
        # top up from whichever band(s) still have surplus, preferring the next lower band first
        band_order = [b[0] for b in bands]
        for i in range(len(bands) - 1, 0, -1):
            if shortfall_total <= 0:
                break
            lower_label, lower_lo, lower_hi, _ = bands[i - 1]
            pool = df[(df["input_words"] >= lower_lo) & (df["input_words"] <= lower_hi) & (~df["product_id"].isin(already_picked_ids))].copy()
            n_top_up = min(shortfall_total, len(pool))
            if n_top_up <= 0:
                continue
            topped = pool.sample(n=n_top_up, random_state=43).copy()
            topped["band"] = lower_label + " (top-up)"
            selected_parts.append(topped)
            already_picked_ids |= set(topped["product_id"].tolist())
            shortfall_total -= n_top_up
            print(f"  Topped up {n_top_up} from band {lower_label}")

    selected = pd.concat(selected_parts, ignore_index=True)
    selected["product_id_sort"] = selected["product_id"].astype(int)
    selected = selected.sort_values("product_id_sort").drop(columns=["product_id_sort"]).reset_index(drop=True)

    print("\n" + "=" * 80)
    print(f"{len(selected)} SELECTED PRODUCTS")
    print("=" * 80)
    print(selected["band"].value_counts().to_string())

    out_csv = TEST_DIR / "new_500_products_selection.csv"
    selected.to_csv(out_csv, index=False)
    print(f"\nWrote {out_csv} ({len(selected)} rows)")

    if shortfalls:
        print("\nShortfalls encountered (before top-up):")
        for band_label, requested, took in shortfalls:
            print(f"  {band_label}: requested {requested}, pool only had {took}")
    else:
        print("\nNo shortfalls -- every band had enough unused products.")

    return selected


if __name__ == "__main__":
    main()
