"""
Shared booking-notes text helpers.

Single source of truth for heading detection on the BOOKING side, used by both
select_booking_100.py and score_booking_v5.py so the selector and the scorer can
never disagree about what a heading is.

Why this is booking-specific and not reused from score_v5_3.py: the description
scorer treats a short capitalised line with no terminal punctuation as a
heading. On booking notes that returns the PACKING LIST -- measured across all
8,244 products with booking notes, the top "headings" under that rule are
sunscreen (834), towel (430), camera (279), water bottle (268), swimwear (253),
hat (253), wetsuit (202). Booking notes are list-dominated: 32.2% of all lines
are bulleted and 25.4% of products are majority-bullet.

So a booking heading requires an UNAMBIGUOUS marker -- markdown, bold-only, or a
trailing colon -- and a bulleted line is never a heading.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = ROOT / "data" / "Fareharbor"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_model_comparison_batches import strip_html  # noqa: E402

# NOTE the \s* not \s+ -- Fareharbor suppliers overwhelmingly write "##Departure"
# with no space after the hashes. Requiring whitespace made every such heading
# invisible, which showed up as 245 phantom "filled with no heading" gate leaks
# on the first booking run.
MD_HEAD = re.compile(r"^\s{0,3}#{1,6}\s*\S")
BOLD_ONLY = re.compile(r"^\s*\*{2,3}([^*]{1,60})\*{2,3}\s*:?\s*$")
BULLET = re.compile(r"^\s*(?:[-*•‣●▪·]|\d{1,2}[.)])\s+")
SEPARATOR = re.compile(r"^[\s_\-=*~.]{5,}$")
INLINE_LABEL = re.compile(r"^\s*([A-Za-z][A-Za-z /&'\-]{1,38}):\s+(\S.*)$")


def demark(s):
    """Strip markdown decoration so the text underneath can be compared."""
    s = re.sub(r"^\s{0,3}#{1,6}\s*", "", s)
    s = re.sub(r"\*{1,3}", "", s)
    return s.strip()


def is_separator(line):
    return bool(SEPARATOR.match(line.strip()))


NUMBERED_SECTION = re.compile(r"^\s*\d{1,2}[.)]\s+([A-Z][^.!?]{2,50})$")


def heading_of(line, next_line=None):
    """Return the heading text, or None.

    Marker-based cases need no context. The two context-sensitive cases --
    a bare Title Case line and a numbered section -- require `next_line`,
    because that is the only thing separating a heading from a packing-list
    item: a heading is followed by PROSE, an item by another item.

    Without that test, "Sunscreen" / "Towel" / "Water bottle" all read as
    headings (measured: they are the top 3 "headings" in the catalogue under a
    naive rule). With it, "Risk Disclosure" followed by a full sentence is a
    heading and "Towel" followed by "Hat" is not.
    """
    raw = line.rstrip()
    if not raw.strip() or is_separator(raw) or BULLET.match(raw):
        return None
    if MD_HEAD.match(raw):
        return demark(raw).rstrip(":").strip()
    m = BOLD_ONLY.match(raw)
    if m:
        return m.group(1).rstrip(":").strip()
    t = demark(raw)
    # A trailing colon marks a section heading, but only when it is short and
    # carries no value of its own -- "Location:" is a heading, while
    # "Location: Berth 4, Forster Marina" is an inline label (STEP 1D).
    if t.endswith(":") and len(t.split()) <= 12:
        return t.rstrip(":").strip()
    # A short ALL-CAPS line with no terminal punctuation. Very common in booking
    # notes and carries no markdown at all -- 714332 writes SAILING ADDRESS /
    # PARKING / ARRIVAL TIME / WHAT TO BRING / FOOTWEAR REQUIREMENT, and 403385
    # writes DEPARTURE TIME AND PLACE. Missing these made whole products read as
    # "0 headings", so every correct fill was reported as a gate leak.
    # Guarded: must contain letters, be short, and not end like a sentence.
    if (t and len(t.split()) <= 8 and t == t.upper()
            and re.search(r"[A-Z]{2}", t) and t[-1] not in ".!?,;"):
        return t.strip()

    # --- context-sensitive cases: need to see what follows ---
    if next_line is None:
        return None
    nxt = demark(next_line).strip()
    # "followed by prose" = the next line is a sentence, not another short item
    follows_prose = bool(nxt) and (len(nxt.split()) >= 8 or nxt[-1:] in ".!?")
    if not follows_prose:
        return None

    m = NUMBERED_SECTION.match(raw)
    if m:                                     # "1. Booking & Payment"
        return m.group(1).strip()

    # Bare Title Case section name: "Risk Disclosure", "Arrival & Accommodation"
    if (2 <= len(t.split()) <= 6 and t[-1] not in ".!?,;:"
            and t[:1].isupper() and not t.isupper()
            and not re.search(r"\d", t)):
        return t.strip()
    return None


def inline_label_of(line):
    """Return (label, value) for a STEP 1D `Label: value` line, or None."""
    m = INLINE_LABEL.match(demark(line))
    return (m.group(1).strip(), m.group(2).strip()) if m else None


def lines_of(text):
    return [l for l in text.split("\n") if l.strip()]


def headings_in(text_or_lines):
    """-> [(line_index, heading_text)] with the next-line context supplied."""
    lines = (lines_of(text_or_lines) if isinstance(text_or_lines, str)
             else list(text_or_lines))
    out = []
    for i, l in enumerate(lines):
        h = heading_of(l, lines[i + 1] if i + 1 < len(lines) else None)
        if h:
            out.append((i, h))
    return out


def profile(bn):
    """Structural profile of one product's booking notes."""
    lines = lines_of(bn)
    heads = [h for _, h in headings_in(lines)]
    bullets = [l for l in lines if BULLET.match(l)]
    labels = [x for x in (inline_label_of(l) for l in lines) if x]
    words = len(bn.split())
    return {
        "words": words,
        "lines": len(lines),
        "headings": heads,
        "n_headings": len(heads),
        "n_bullets": len(bullets),
        "bullet_ratio": (len(bullets) / len(lines)) if lines else 0.0,
        "n_inline_labels": len(labels),
    }


def regime(p):
    """Which of the four measured regimes a product falls into."""
    if p["n_headings"] > 0:
        return "heading_rich"
    if p["n_inline_labels"] > 0:
        return "inline_label_only"
    if p["words"] > 60:
        return "long_no_heading"
    return "short_no_heading"


def raw_path(pid):
    hits = list(RAW_DIR.glob(f"Fareharbor-*-{pid}.json"))
    if len(hits) != 1:
        raise RuntimeError(f"expected 1 raw file for {pid}, found {len(hits)}")
    return hits[0]


def load_raw(pid):
    """-> (product_name, raw_booking_notes) with HTML stripped."""
    item = json.loads(raw_path(pid).read_text(encoding="utf-8")).get("item") or {}
    return (item.get("name") or "",
            strip_html(item.get("booking_notes") or ""))


STRAY_COMMA = re.compile(r',\s*"\s*\}\s*$')
FENCE = re.compile(r"^```(?:json)?\s*|\s*```$")


def _repair_orphan_strings(text):
    """Rejoin a value the model emitted as a second, key-less string.

    Observed on 98642 in the first booking run: the supplier had two FAQ pairs,
    and the model emitted them as two ADJACENT JSON strings rather than one
    newline-joined value:

        "redo_booking_faqs":"Q: CAN WE BRING DRINKS...","Q: CHILDREN/NON
        DRINKERS? A: ...","redo_booking_before_arrival":""

    All 15 keys are present, so this is not a dropped key -- the second string
    is an orphaned continuation. json.loads reads it as a KEY and dies on the
    missing ':'. Unrepaired the whole product is dropped and reads as empty,
    which is exactly how a correct extraction gets mistaken for content loss.

    This walks the object and re-attaches any key-position string that is not
    followed by ':' onto the preceding value, newline-separated. Returns None
    when the text is not repairable this way.
    """
    t = text.strip()
    if not (t.startswith("{") and t.endswith("}")):
        return None

    pairs, i, n, expecting, last_key = {}, 0, len(t), "key", None
    order = []
    while i < n:
        if t[i] != '"':
            i += 1
            continue
        j = i + 1
        while j < n:
            if t[j] == "\\":
                j += 2
                continue
            if t[j] == '"':
                break
            j += 1
        if j >= n:
            return None
        try:
            s = json.loads(t[i:j + 1])
        except json.JSONDecodeError:
            return None
        k = j + 1
        while k < n and t[k] in " \t\r\n":
            k += 1
        nxt = t[k] if k < n else ""

        if expecting == "key":
            if nxt == ":":
                last_key = s
                if s not in pairs:
                    order.append(s)
                pairs.setdefault(s, "")
                expecting = "value"
            else:
                # orphaned continuation of the previous value
                if last_key is None:
                    return None
                pairs[last_key] = (pairs[last_key] + "\n" + s).strip("\n")
        else:
            pairs[last_key] = s
            expecting = "key"
        i = j + 1

    return pairs if pairs else None


def parse_booking_json(text):
    """-> (fields_dict | None, repair_note)."""
    t = FENCE.sub("", (text or "").strip())
    try:
        return json.loads(t), ""
    except json.JSONDecodeError:
        pass
    try:
        return json.loads(STRAY_COMMA.sub("}", t)), "stray-comma"
    except json.JSONDecodeError:
        pass
    fixed = _repair_orphan_strings(t)
    if fixed is not None:
        return fixed, "orphan-string"
    return None, "UNREPAIRABLE"


def iter_products():
    """Yield (pid, name, booking_notes) for every product WITH booking notes."""
    for fp in sorted(RAW_DIR.glob("*.json")):
        pid = fp.stem.split("-")[-1]
        try:
            item = json.loads(fp.read_text(encoding="utf-8")).get("item") or {}
        except Exception:                                          # noqa: BLE001
            continue
        bn = strip_html(item.get("booking_notes") or "")
        if bn.strip():
            yield pid, (item.get("name") or ""), bn
