# V5.3 description — full catalogue

Every Fareharbor product with a description: **11,069**. 167 products have no description and were skipped.

## Run integrity

| | |
|---|---|
| Products | **11,069** |
| Responses parsed | **11,069 of 11,069** (one needed a JSON repair) |
| Truncated | **0** |
| Wrong key count | **0** |
| Mean content retention | **99.4%** |
| Products at 100% retention | **10,853** (98.0%) |
| Products with no finding at all | **8,450** (76.3%) |

Retention is **higher** at full scale than on the random-1,000 (99.17%) or
the hardest-500. Every earlier set was difficulty-selected, so those are
the pessimistic end rather than the typical case.

## Findings

| Finding | Count | Products | Verified? |
|---|---|---|---|
| duplicated sentences | 80 | 80 | no — upper bound |
| untraceable (possible invention) | 71 | 71 | no — upper bound |
| missing sentences (content loss) | 268 | 161 | no — upper bound |
| filled with no heading | 3,422 | 2,372 | **yes — ~90% real** (40 sampled) |
| itinerary lines without a signal | 1,929 | 241 | **yes — ~90% real** (40 sampled) |
| dropped informative headings | 158 | 142 | no — upper bound |
| included lines that are purchasable | 0 | 0 | no — upper bound |
| pricing with no figure | 9 | 9 | no — upper bound |
| cancellation with no refund | 2 | 2 | no — upper bound |
| markdown junk | 2 | 1 | no — upper bound |

### What was verified, and why

On the booking run the same two flags were mostly the scorer's own fault —
`filled with no heading` went from 245 to 0 once the heading mapper was
fixed. So both were sampled here before being reported. **They hold up:**
about 90% of each is real.

Example: product `529030` filled `cancellation` when its only headings are
`Duration`, `Ticket Prices:` and `About`. Nothing licensed that column.

That the gate leaks more here than on the curated samples is expected —
every earlier set was heading-rich by selection, and the full catalogue
contains thousands of products with sparse or no headings.

**The other counts are NOT verified** and should be read as upper bounds.
Across this project roughly a quarter of what any detector reports has
turned out to be the detector rather than the model.

## Known issues carried forward

- **Duplication** — the one hard gate that fails. Three prompt versions
  failed to fix it on smaller runs; it needs the deterministic
  post-processing pass, not more wording.
- **Difficulty ratings** (`Difficulty: Hard`) wrongly fill `restrictions`.
  Reproducible across runs, and a two-line prompt fix.
- **Content loss** does not shrink with easier products, which is why the
  `recovered_content` pass built for the booking side should be applied
  here too.