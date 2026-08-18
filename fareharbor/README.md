# Fareharbor

The supplier this work started on, and the only one taken all the way through.
Each folder below is one stage of the pipeline; each folder inside those is one
run, with its own README, prompt, scripts, input and reports.

| Stage | What happens here |
|---|---|
| [`model-choice/`](model-choice/) | Deciding **which model** runs the extraction. 13 models on 10 products, then 3 models on 30 hard ones — which is how `gpt-5.6-luna` was chosen. |
| [`description/`](description/) | Extracting the **description** side, oldest run first: V4.4 → the luna runs → V5.3 heading-gated on 500, then 1,000, then the full 11,069-product catalogue. |
| [`booking/`](booking/) | Extracting the **booking-notes** side. A separate set of 25 columns, built from a census of all 8,244 products that have booking notes. |
| [`checker/`](checker/) | The **independent AI checker** that reads the supplier's original against every extracted box and reports what went wrong. |
| [`unified/`](unified/) | Both extractions plus the API's own fields, **joined into one row per product**. |

Start at [`description/v5_3_full_run/`](description/v5_3_full_run/) for the
full-catalogue result, or [`../README.md`](../README.md) for the numbers on
every run in one table.
