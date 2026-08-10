# Which prompt to use

## Description side → `SYSTEM_PROMPT_FH_DESC_V4_8_3.txt`

That is the current version. Use it unless you have a reason not to.

## Booking side → `SYSTEM_PROMPT_FH_BOOKING_V4_7.txt`

Unchanged throughout this work, and still current. It was held constant on
purpose so that any change in quality could be attributed to the description-side
edits alone.

---

## The others are history, not alternatives

| File | Why it is still here |
|---|---|
| `SYSTEM_PROMPT_FH_DESC_V4_8.txt` | First itinerary rework. Trimmed rows out of good itineraries |
| `SYSTEM_PROMPT_FH_DESC_V4_8_1.txt` | Fixed the trimming. Let airport parking back in, and leaked the raw `itinerary:` label |
| `SYSTEM_PROMPT_FH_DESC_V4_8_2.txt` | Added the `redo_desc_faqs` field and fixed three itinerary defects |
| `SYSTEM_PROMPT_FH_DESC_V4_8_3.txt` | **Current.** Added What's Included heading-gating |

They are kept so any version can be re-run and compared. `PROMPT_VERSION_LOG.md`
in `../issues/` records what each one fixed and what it broke.

## Running a specific version

```bash
cd ../code
python run_extraction.py                    # V4.8.3, the default
python run_extraction.py --version 4.8.1    # any older version
```

⚠️ **V4.8.2 added a 16th output field, `redo_desc_faqs`.** Rolling back to
V4.8.1 or earlier drops that field from the output.
