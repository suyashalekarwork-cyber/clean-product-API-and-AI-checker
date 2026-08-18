# How to run this

Two things you can do. The first is free.

---

## Option A — review what is already here (free, no key, 1 minute)

Four completed runs are in the repo. You can review them without running
anything or spending anything.

```bash
git clone https://github.com/suyashalekarwork-cyber/clean-product-API-and-AI-checker.git
cd clean-product-API-and-AI-checker/fareharbor/description/luna100_run

pip install pandas openpyxl
cd code
python review_output.py
```

That writes `reports/section_review.xlsx` — open it and start on the **Checks**
sheet.

**You don't even need that much.** These three files are already in the repo and
open in Excel as-is:

| File | What it shows |
|---|---|
| `data/luna100_source_input.xlsx` | What goes **in** — the supplier's own text |
| `extracted/luna100_v4_8_3_extracted.xlsx` | What comes **out** — 100 products x 29 fields |
| `reports/section_review.xlsx` | The output checked against the source |

---

## Option B — run the extraction yourself (~$0.42, 3–4 minutes)

### 1. Get an OpenAI API key

<https://platform.openai.com/api-keys> → **Create new secret key** → copy it.
It starts `sk-...` and is only shown once.

The account needs credit on it — <https://platform.openai.com/settings/organization/billing>.
$5 covers this run many times over.

### 2. Put the key in a file

From the repo root:

```bash
cp .env.example .env
```

Open `.env` in any text editor and set the key:

```
OPENAI_API_KEY=sk-your-key-here
```

`.env` is gitignored — it will not be committed. **Do not paste the key into any
`.py` file or into a message.**

### 3. Install what it needs

```bash
pip install openai python-dotenv pandas openpyxl
```

### 4. Do a dry run first — free, no API call

```bash
cd fareharbor/description/luna100_run/code
python run_extraction.py --build
```

Expected:

```
Built batch_input_v4_8_3.jsonl: 166 requests (3836 KB), 34 empty sides skipped
--build: nothing submitted, no cost incurred.
```

If that works, the key and the data are fine. **166 requests** = 100 product
descriptions + 66 booking notes; 34 products have no booking text.

### 5. Run it

```bash
python run_extraction.py
```

It submits the batch, then prints progress every 30 seconds:

```
Submitted. Batch ID: batch_6a797adba1788190a669c2a92039a303
  [    0s] validating   0/0 failed=0
  [   91s] in_progress  29/166 failed=0
  [  213s] completed    166/166 failed=0

Done. 166/166 responses -> output/luna100_v4_8_3_output.jsonl
```

Safe to interrupt. The batch id is saved the moment the job is submitted, so
re-running resumes the same job rather than paying for a second one.

### 6. Review it

```bash
python review_output.py        # writes reports/section_review.xlsx
python export_extracted.py     # writes extracted/*.csv, *.json, *.xlsx
```

---

## Running an older prompt version

```bash
python run_extraction.py --version 4.8.1
```

Versions: `4.8`, `4.8.1`, `4.8.2`, `4.8.3` (default).
See `prompts/WHICH_PROMPT_TO_USE.md`.

⚠️ V4.8.2 added a 16th output field, `redo_desc_faqs`. Rolling back to V4.8.1 or
earlier drops that field from the output.

---

## Reading the review workbook

`reports/section_review.xlsx`, 7 sheets. Start at **Checks**.

| Sheet | |
|---|---|
| `Read_Me` | What each field is supposed to contain |
| `Summary` | Counts, parse failures, checks passing |
| **`Checks`** | **14 known issues, each PASS/FAIL with the failing product ids** |
| `Itinerary` · `FAQ` · `Whats_Included` | Per product, with the **raw supplier text in the same row** |
| `All_Products` | Word retention and any invented words, all 100 |

Rows with an issue sort to the top. **YOUR VERDICT** and **YOUR COMMENT** columns
are blank for your notes.

The raw text sits in the row deliberately. Every finding in this work was checked
against the supplier's own text, and several early findings turned out to be
wrong once that check was applied.

---

## If something breaks

| Problem | Fix |
|---|---|
| `OPENAI_API_KEY not set` | `.env` is missing or the key line is wrong. It must read `OPENAI_API_KEY=sk-...` with no quotes |
| `insufficient_quota` | The account has no credit — add some in billing |
| `ModuleNotFoundError` | `pip install openai python-dotenv pandas openpyxl` |
| `no run output found` | You are not in `fareharbor/description/luna100_run/code`, or the extraction has not run yet |
| A run seems stuck | Batches can take up to 24h at busy times. These have finished in 3–4 minutes. Ctrl-C is safe; re-run to resume |
| Excel says a file is locked | Close the workbook before re-running the scripts |

---

## Cost

| | |
|---|---|
| One run of 100 products | **~$0.42** |
| All 23,034 products | ~$49 |

Uses the OpenAI **Batch API**, which is half price and returns within 24 hours.
Every run here finished in under 4 minutes.
