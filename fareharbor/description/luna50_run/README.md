# Run 50 Products Through gpt-5.6-luna

**You need:** Python, an OpenAI API key, and about 15 minutes (mostly waiting).

Everything needed is already in this folder. The prompt and all the product
text are baked into the batch file — you are not building anything, just
submitting a prepared job and sending back what comes out.

---

## Quick version

```bash
pip install openai pandas openpyxl

# Windows
set OPENAI_API_KEY=sk-your-key-here
# Mac / Linux
export OPENAI_API_KEY=sk-your-key-here

python run_luna50.py       # submits and waits (3-15 min)
python check_luna50.py     # checks it worked, builds a spreadsheet
```

Then send back **`luna50_output.jsonl`** and **`luna50_review.xlsx`**.

---

## Step by step

### 1. Install

```bash
pip install openai pandas openpyxl
```

`openai` is required. `pandas` and `openpyxl` are only for the spreadsheet in
step 4 — without them everything still runs, you just get a plain summary.

### 2. Set your API key

The key is read from an environment variable. **Do not paste it into any file
in this folder** — these files go back into a shared repo.

```bash
# Windows (Command Prompt)
set OPENAI_API_KEY=sk-your-key-here

# Windows (PowerShell)
$env:OPENAI_API_KEY = "sk-your-key-here"

# Mac / Linux
export OPENAI_API_KEY=sk-your-key-here
```

The key must have Batch API access and some credit. This run costs roughly
**20-30 US cents**.

### 3. Run it

```bash
python run_luna50.py
```

You'll see:

```
Uploading luna50_batch_input.jsonl (93 requests, 1652 KB)...
Submitted. Batch ID: batch_abc123...
  [   30s] in_progress   12/93 done, 0 failed
  [   60s] in_progress   47/93 done, 0 failed
  ...
Done. 93 responses written to luna50_output.jsonl
```

**Usually 3-15 minutes.** OpenAI allows itself up to 24 hours, so occasionally
it is slower — that is normal, not a fault.

**Safe to interrupt.** Press Ctrl+C, close your laptop, whatever. The batch ID
is saved to `luna50_batch_id.json` the moment it is submitted, so re-running
the script **resumes the same job**. It will not submit twice or charge twice.

### 4. Check it worked

```bash
python check_luna50.py
```

```
  responses received   : 93 of 93 expected
  products with output : 50 of 50

  TECHNICAL FAILURES (not model quality):
    HTTP errors        : 0
    unparseable JSON   : 0
    truncated          : 0

  EXTRACTION QUALITY:
    word ratio overall : 0.946   (~1.0 good, >1.1 repeating, <0.9 dropping)
    duplicate sentences: 22
    avg fields filled  : 10.0 of 28

  RUN LOOKS CLEAN -- send the results back.
```

If it says **RUN LOOKS CLEAN**, you're done.

If it lists failures, **send the results back anyway** with a copy of what it
printed. A partial run is still useful and the failures are themselves data.

### 5. Send back

| File | What it is |
|---|---|
| `luna50_output.jsonl` | The raw model responses — **the important one** |
| `luna50_review.xlsx` | Readable spreadsheet with per-product numbers |

---

## What the numbers mean

Only relevant if you're curious — you don't need to interpret anything.

**word ratio** — words the model wrote ÷ words the supplier wrote.
Around 1.0 is right. Above 1.1 means it repeated itself. Below 0.9 means it
dropped content. A different model scored 1.187 on an earlier run and was
rejected for exactly that.

**duplicate sentences** — the same sentence placed in two different fields.
That makes the same paragraph render twice on the website, so it matters.
Counted per side only: cancellation and accessibility genuinely appear in both
the description and the booking notes, and that's correct, not a fault.

**fields filled** — how many of 28 fields got content. Low is not automatically
bad; most products simply don't have an itinerary or a cancellation policy, and
an honest blank beats an invented answer.

---

## If something goes wrong

| Message | Fix |
|---|---|
| `OPENAI_API_KEY is not set` | Step 2. In a new terminal, set it again — it doesn't persist between windows. |
| `openai package not installed` | `pip install openai` |
| `luna50_batch_input.jsonl not found` | Run the command from *inside* this folder (`cd fareharbor/description/luna50_run`). |
| `insufficient_quota` / 429 | The key has no credit, or Batch access isn't enabled. |
| Stuck at `in_progress` for ages | Normal. Leave it, or Ctrl+C and re-run later to resume. |
| Want to genuinely start over | Delete `luna50_batch_id.json`, then re-run. **This submits a new batch and charges again.** |

---

## What this is testing

`gpt-5.6-luna` is the model chosen to run the Fareharbor product extraction —
it takes messy supplier text and sorts it into fields like "What's Included",
"Meeting Point" and "Duration".

It was picked on a 30-product test ([`../../model-choice/hard30_run/`](../../model-choice/hard30_run/)) where
it matched a model costing **10x more** on faithfulness to the source, for
**$49 versus $487** across the full catalogue.

These 50 products are **different products**, deliberately chosen as difficult
ones, with **zero overlap** with that earlier test. The point is to confirm the
choice holds on evidence it hasn't already seen.

## Files in this folder

| File | |
|---|---|
| `luna50_batch_input.jsonl` | 93 prepared requests, prompt included. **Don't edit.** |
| `luna50_raw_text.json` | The original supplier text, for checking results against |
| `luna50_products.json` | The 50 product IDs and how they were chosen |
| `run_luna50.py` | Submits and waits |
| `check_luna50.py` | Verifies and builds the spreadsheet |

**Note:** 50 products but 93 requests, not 100. Seven products have no
booking-notes text, so those requests were left out deliberately — sending an
empty prompt wastes a call and invites the model to invent something to fill
the gap.
