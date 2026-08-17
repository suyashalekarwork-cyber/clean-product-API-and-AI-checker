"""Shared Rezdy text helpers -- the single source of truth for what the model sees.

THE ONE THING THAT MAKES REZDY DIFFERENT FROM FAREHARBOR:
Rezdy's raw text is HTML (`<h2>Where to meet</h2>`, `<p>`, `<strong>`) where
Fareharbor's is markdown (`##Departure`). Fareharbor's strip_html() deletes tags,
which is safe there -- Fareharbor's line breaks are real newline characters. On
Rezdy the line breaks ARE the tags, so deleting them collapses the whole text to
one line and every heading disappears. Measured on airbornesolutions-PU6Z60: a
`Includes:` heading plus three items became one unbroken paragraph.

Measured across all 9,373 products: 72.8% of Rezdy headings come from markup
(bold-only lines 50.7%, <h1-6> 22.1%). Only 27.2% are plain-text conventions
that survive any treatment. So the conversion carries most of the load.

THE DESIGN RULE: THIS CONVERTER RESTORES STRUCTURE AND DECIDES NOTHING.

The census version (scripts/rezdy_heading_census.py) additionally ran
is_headinglike() over every <h1-6> and bold block and demoted the ones it judged
to be prose. That was right THERE -- the census had no model, so a regex was the
only reader. It is wrong HERE. Extraction has a model, and the V5.3 prompt
already contains that judgement (STEP 1: what is a heading; STEP 1B: a
heading-shaped line carrying its own information is CONTENT, keep it).

Measured cost of moving the judgement into the converter: the guard demotes
32.7% of all heading tags and 17.7% of bold blocks, and among them 484
question-form headings across 241 products -- `<h4>What do you need to
bring?</h4>` -- purely because they end in '?'. Fareharbor's own prompt lists
"What should I bring with me?" as a valid heading wording, so those are real.

Consequence for the census numbers: this converter shows the model MORE
candidate headings than the census counted, so 68.8% / 49.4% are a FLOOR, not a
ceiling.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = ROOT / "data" / "Rezdy"          # 9,373 files -- NOT data/Full Data Dump/Rezdy (3,045)

sys.path.insert(0, str(Path(__file__).resolve().parent))

FIELDS = ["description", "additionalInformation", "terms"]

BLOCK = re.compile(
    r"</?(?:p|div|br|ul|ol|li|tr|table|h[1-6]|section|article)\b[^>]*>", re.I)
H_TAG = re.compile(r"<h([1-6])\b[^>]*>(.*?)</h\1>", re.I | re.S)
LI_TAG = re.compile(r"<li\b[^>]*>(.*?)</li>", re.I | re.S)
BOLD = re.compile(r"<(strong|b)\b[^>]*>(.*?)</\1>", re.I | re.S)
A_TAG = re.compile(r"""<a\b[^>]*?href\s*=\s*(["'])(.*?)\1[^>]*>(.*?)</a>""",
                   re.I | re.S)
# NOT <[^>]+> -- a '>' inside a quoted attribute value ends that match early and
# leaks the rest of the tag out as visible text. Measured: Word-pasted styles
# like mso-fareast-language:EN-AU" leaked `EN-AU">` and it scored as an ALL-CAPS
# heading across 9 suppliers. Quoted runs must be consumed as units.
ANY_TAG = re.compile(r"""<(?:[^>"']|"[^"]*"|'[^']*')*>""")

WORD = re.compile(r"[A-Za-z0-9$@./:%'-]+")
# A separator rule ("-----", "_____"). The prompt is explicitly allowed to drop
# these, so they are the ONE thing the lossless check tolerates losing.
RULE_ONLY = re.compile(r"^[-_=~.*\s]+$")


def _detag(s):
    """Tags out, whitespace normalised. Entities left ALONE -- see _text."""
    return re.sub(r"[ \t ]+", " ", ANY_TAG.sub(" ", s)).strip()


def _text(s):
    """Tags out, entities decoded, whitespace normalised. Adds no newlines.

    Entity decoding must happen EXACTLY ONCE, and it happens in the final
    assembly loop of html_to_markdown. Decoding a tag's inner content AND the
    assembled line decodes twice: a supplier writing `&amp;amp;` (intending to
    display "&amp;") would get "&". So the inner-content helpers use _detag and
    only the final assembly calls this.
    """
    s = ANY_TAG.sub(" ", s)
    return re.sub(r"[ \t ]+", " ", html.unescape(s)).strip()


def _bold(m):
    """<b>…</b> -> **…**, WITHOUT eating the whitespace around the content.

    Two separate failures, both of which corrupt text rather than lose it, so a
    word-count check cannot see either:

    1. `<b>&nbsp;</b>` -- suppliers bold the space BETWEEN two sentences. Emit ""
       and the words fuse: "a course/experience." + "This can be done" becomes
       "course/experience.This". It must become a SPACE.
    2. `<b>HOW LONG: </b>2 HOURS` (PJBKTR) -- the space that separates the label
       from its value lives INSIDE the bold tag. Strip it and the line becomes
       "HOW LONG:2 HOURS", which no longer matches the prompt's inline
       `Label: value` rule (STEP 1D requires `:` followed by whitespace).
       So leading/trailing space is preserved OUTSIDE the markers.
    """
    inner = _detag(m.group(2))
    if not inner or html.unescape(inner).strip() == "":
        return " "
    src = html.unescape(ANY_TAG.sub(" ", m.group(2))).replace(" ", " ")
    lead = " " if src[:1].isspace() else ""
    trail = " " if src[-1:].isspace() else ""
    return f"{lead}**{inner}**{trail}"


def html_to_markdown(raw):
    """Rezdy HTML -> the markdown shapes the V5.3/V5.4 prompts were written for.

    <h1-6>          -> '## text'    ALWAYS. Never judged -- the model decides.
    <li>            -> '- text'     a bullet is never a heading.
    <strong>/<b>    -> '**text**'   block OR inline. The model decides which.
    <a href=x>t</a> -> '[t](x)'     RULE 8 then keeps the URL character-for-char.
    block tags      -> newline      line structure, nothing more.
    """
    if not isinstance(raw, str) or not raw.strip():
        return ""

    # Word paste carries literal newlines INSIDE tag attributes
    # (`...mso-ligatures:none;\r\nmso-fareast-language:EN-AU">`). The line split
    # below would cut such a tag in half, leaving a fragment with no opening '<'
    # that survives tag-stripping and scores as an ALL-CAPS heading.
    raw = ANY_TAG.sub(lambda m: re.sub(r"\s+", " ", m.group(0)), raw)

    # In HTML a newline in CONTENT is whitespace -- only <br> and block tags
    # break a line. Rezdy's Word-pasted text is hard-wrapped mid-sentence, so
    # honouring those newlines split "We look\r\nforward to seeing you" and left
    # "We look" scoring as a heading. Conditional on the field actually BEING
    # HTML: `terms` is 3,354/3,377 plain text, where the newlines are the only
    # structure there is.
    if BLOCK.search(raw):
        raw = re.sub(r"[\r\n]+", " ", raw)

    raw = A_TAG.sub(lambda m: f"[{_detag(m.group(3))}]({m.group(2).strip()})", raw)
    # A bold tag wrapping only whitespace (`<b>&nbsp;</b>`) is extremely common
    # -- suppliers bold the space between two sentences. Replacing it with ""
    # FUSES the words either side ("a course/experience." + "This can be done"
    # -> "course/experience.This"), which reads as two lost words to a checker
    # and as a corrupted sentence to a human. It must become a SPACE.
    raw = BOLD.sub(_bold, raw)
    raw = H_TAG.sub(lambda m: "\n## " + _detag(m.group(2)) + "\n", raw)
    raw = LI_TAG.sub(lambda m: "\n- " + _detag(m.group(1)) + "\n", raw)
    raw = BLOCK.sub("\n", raw)

    out = []
    for chunk in raw.split("\n"):
        t = _text(chunk)
        if not t:
            continue
        # '## **Heading**' -> '## Heading' -- one marker is enough.
        t = re.sub(r"^(##\s*)\*\*(.*?)\*\*$", r"\1\2", t)
        t = re.sub(r"^(-\s*)\*\*(.*?)\*\*$", r"\1\2", t)
        # An empty <h4></h4> or <li></li> leaves a bare marker behind. It is not
        # a heading, and left in, it reads as one owning the NEXT line.
        if re.fullmatch(r"[#\-*\s]+", t):
            continue
        out.append(t)
    return "\n".join(out)


def conversion_losses(raw, converted=None):
    """Words present in the raw text but absent after conversion.

    The converter sits in front of everything: anything it drops is gone before
    a person or a gate can see it. Separator rules are the one tolerated loss --
    the prompt is explicitly allowed to omit them.
    """
    if converted is None:
        converted = html_to_markdown(raw)
    before, after = WORD.findall(_text(raw)), set(WORD.findall(converted))
    return [w for w in before if w not in after and not RULE_ONLY.match(w)]


def assert_lossless(raw, pid="?", field="?"):
    """Refuse to proceed if conversion dropped real text. Used as a build gate."""
    lost = conversion_losses(raw)
    if lost:
        raise AssertionError(
            f"{pid}/{field}: conversion dropped {len(lost)} word(s): "
            f"{lost[:12]}. The model would never see this text -- fix the "
            f"converter, do not lower the gate.")


def product_id_of(path):
    """Product ID = LAST hyphen segment. supplierAlias can contain hyphens."""
    return Path(path).stem.rsplit("-", 1)[-1]


def supplier_of(path, product=None):
    if isinstance(product, dict) and product.get("supplierAlias"):
        return product["supplierAlias"]
    stem = Path(path).stem
    return stem[len("Rezdy-"):].rsplit("-", 1)[0] if stem.startswith("Rezdy-") else stem


def iter_products(fields=None):
    """Yield (pid, supplier, product_dict). Skips API-error stubs.

    ~10 files in data/Rezdy are dead stubs:
    {"error": "Failed to fetch from Rezdy API", "status": 500}
    """
    for path in sorted(RAW_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:                                          # noqa: BLE001
            continue
        # Rezdy nests everything under "product" (Critical Rule 6).
        p = data.get("product", data)
        if not isinstance(p, dict) or "error" in data:
            continue
        if fields and not any(isinstance(p.get(f), str) and p[f].strip()
                              for f in fields):
            continue
        yield product_id_of(path), supplier_of(path, p), p


def load_raw(pid):
    """-> (product_name, {field: converted_text}) for one product."""
    hits = list(RAW_DIR.glob(f"Rezdy-*-{pid}.json"))
    if len(hits) != 1:
        raise RuntimeError(f"expected 1 raw file for {pid}, found {len(hits)}")
    p = json.loads(hits[0].read_text(encoding="utf-8")).get("product", {})
    return (p.get("name") or ""), {f: html_to_markdown(p.get(f) or "")
                                   for f in FIELDS}
