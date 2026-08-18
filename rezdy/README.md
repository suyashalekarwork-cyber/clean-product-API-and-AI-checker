# Rezdy

The second supplier. The heading-gating rule proved on Fareharbor —
*a field fills only when the supplier wrote a heading naming it* — applied here
for the first time.

| Stage | What happens here |
|---|---|
| [`description/`](description/) | Extracting the **description** side. One run so far: [`rezdy_desc_100_run/`](description/rezdy_desc_100_run/), 100 products, the hardest in the catalogue, read by hand. |

Rezdy's raw text is **HTML** where Fareharbor's is markdown, so it is converted
to headings before the same gate is applied. Otherwise the rule is unchanged.

Headline: supplier words kept goes from **71.8% to 98.6%**, and fields available
from 9 to 21. The old method was silently dropping more than a quarter of every
supplier's text.
