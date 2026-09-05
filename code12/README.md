# Code 12 — data and decoder

Companion files to *Code 12*, The Macro Prudential View
(themacroprudentialview.substack.com), on the Italian Treasury's auction-window
demand series and the euro-area dealer-reporting format behind it.

The Italian Treasury (MEF) publishes, in each annual *Rapporto sul Debito
Pubblico*, a stacked monthly bar chart of the composition by investor type of
the orders its Specialists report around nominal BTP auctions. It has never
published the numbers as a table. These files are the numbers read off the
chart geometry of ten editions (2016–2025), the code that reads them, and the
survey note the piece refers to.

## Files

| File | What it is |
|---|---|
| `mef_auction_orders_all.csv` | 240 monthly observations: one row per (edition, year, month), share of each investor category in per cent, three decimals. |
| `mef_auction_orders_annual.csv` | Annual means by calendar year, using the later of the two editions that draw each year, with the other edition's hedge-fund reading beside it and the window definition. This is the table in the piece. |
| `mef_series_comparison.csv` | Hedge-fund share in the auction window against MEF's stated share of dealers' gross turnover with final clients, with the edition each figure is quoted from. |
| `mef_decode.py` | The decoder: finds the chart on a given page, binds legend swatches to fill colours, reads each month's segment heights. |
| `mef_series.py` | Runs the decoder over the ten editions and writes the monthly file. |
| `mef_annual.py` | Builds the annual file from the monthly file. |
| `dmo_order_side_survey.md` | The survey of ten euro-area issuers referred to in the piece, with the documents examined. |

## Columns (`mef_auction_orders_all.csv`)

`edition` — Rapporto edition (year of the report). `year`, `month` — the
calendar month the bar represents; each edition draws two calendar years.
`raw_sum_pct` — the column's height relative to the chart's 100% line, a check
that the column was read whole (all rows sit within 99.9 and 100.13). `n_series` —
number of legend entries bound in that edition (seven; six in the 2019 edition,
which does not draw Corporate & Retail). Then one column per category:
`hedge_funds` ("Fondi Hedge"), `asset_managers` ("Fondi gestione" / "Fondi
d'investimento"), `banks` ("Banche"), `official` ("Banche Centrali ed altre
entità pubbliche"), `insurers`, `pension`, `corporate_retail`.

An **empty cell** means no segment was drawn for that category in that month.
MEF sets a category's contribution to zero where its monthly flows were null or
negative, so the annual script treats empty as zero.

## What the series is, and is not

- It is MEF's own demand **proxy**: dealers' client flows selected in a window
  around each auction, from the harmonised dealer returns. MEF calls it "una
  buona proxy della domanda in asta". It is not a record of bids.
- Negative monthly flows are floored at zero for the chart, which raises the
  share of any category that is a net seller in some months relative to a
  signed treatment.
- Eurosystem purchases are excluded from the returns altogether.
- The window changed between the 2017 and 2018 editions (announcement to the
  day after the auction → day after announcement to the day before
  settlement). 2017 is read on both definitions: 31.2 and 31.0.
- Consecutive editions overlap by a year; the largest disagreement between two
  readings of the same year is 0.7 points (hedge funds).
- MEF's stated annual figures, where it gives them, are the figures of record.
  The decode sits within about 2.4 points of every one of them; MEF does not
  say how its annual figures are computed and the decode gives simple means of
  monthly shares.

## Reproducing

The MEF PDFs are not redistributed here. Download the ten editions of the
*Rapporto sul Debito Pubblico* (2016–2025) from the Treasury's site and save
them as `pdfs/Rapporto-<edition>.pdf`. The 0-based page index of the chart in
each edition is in `PAGES` in `mef_decode.py`.

```
pip install pdfplumber pypdf pandas
MEF_PDF_DIR=pdfs python3 mef_series.py     # writes mef_auction_orders_all.csv
python3 mef_annual.py                       # writes mef_auction_orders_annual.csv
```

The decoder works on the PDF's vector content: bars are filled rectangles,
charts are located by their clip rectangles, legend swatches are bound to
labels by proximity, and the 2017 edition — whose swatches sit outside the
clip band — uses an explicit palette taken from the 2016 edition
(`LEGEND_OVERRIDE`). Some editions draw a segment twice; the decoder
de-duplicates on geometry and fill.

## Licence

Data files: CC BY 4.0. Code: MIT. The underlying charts are the Italian
Treasury's; cite the *Rapporto sul Debito Pubblico* for the source and this
repository for the decode.
