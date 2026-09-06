# The German Short in Grand Cayman — data and extraction

Companion files to *The German Short in Grand Cayman*, The Macro Prudential View
(themacroprudentialview.substack.com), on the country-of-issuer short positions
that the Cayman Islands Monetary Authority publishes for the funds it
regulates, and the same positions as they appear in the Cayman Islands'
submission to the IMF's Coordinated Portfolio Investment Survey.

CIMA's Investments Statistical Digest has carried a table called "Portfolio
Investments by Jurisdiction" in every edition since 2015 — long and short
positions by country of issuer, split into equities, short-term debt,
long-term debt and (long side) master funds — as PDF figures to 2019 and as
Infogram embeds from 2020. It has never published the table as a download.
These files are the ten tables as extracted, the IMF series read from the
Portfolio Investment Positions dataset with the Cayman Islands as reporter,
the reconciliation between the two for 2023 and 2024, and the auxiliary
series the piece uses.

## Files

| File | What it is |
|---|---|
| `isd_jurisdiction_all.csv` | 3,295 rows, long format: every jurisdiction row of the "Portfolio Investments by Jurisdiction" table in every edition 2015–2024, both columns of each edition (so restatements are kept), long and short by instrument. US$ bn. |
| `isd_key_jurisdictions_two_reads.csv` | Germany, France, United States, United Kingdom, Japan and Total by year, with the current-edition and next-edition (restated) reading of each cell side by side. The 2018 German long rows are taken from the 2019 edition's restatement (see anomalies). |
| `imf_pip_cym_counterparts.csv` | IMF Portfolio Investment Positions, reporter Cayman Islands, sector total economy, annual 2015–2024: `P_F3SNP_L_P_USD` (short or negative positions, long-term debt), `P_F3_L_P_USD` (long-term debt), `P_TSNP_P_USD` (total short or negative positions), `P_TOTINV_P_USD`, by counterpart economy (DEU, FRA, ITA, ESP, NLD, BEL, AUT, USA, GBR, JPN, CAN) and the world aggregate G001. US$ bn. Publication of 11 March 2026. |
| `imf_pip_cym_semiannual.csv` | The same indicators at semi-annual frequency, 2019-S1 to 2025-S1. The 2024-S1 and 2025-S1 observations repeat the preceding December values. |
| `imf_pip_cym_holder_sectors.csv` | The long-term debt long positions by holder sector (S1 total economy; S122 deposit-taking corporations; S12P, S12R other financial corporations; S12QU insurance and pension funds; S123 money market funds) for Germany and the world, 2015–2024, read 6 September 2026. Short indicators are published at S1 only. The counterpart-sector dimension carries only the total for this reporter. |
| `discrepancy_2023_2024_digest_vs_imf.csv` | For 2023 and 2024, country by country: digest and IMF gross long, gross short and net, all instruments and long-term debt, with the gross gaps. The table behind the "matched amounts" paragraph. |
| `ecb_usd_eur_yearend.csv` | ECB euro reference rate, USD per EUR, last business day of each year 2015–2024 (EXR.D.USD.EUR.SP00.A). |
| `finanzagentur_umlaufvolumen_yearend.csv` | Federal securities outstanding at 31 December 2014–2025, total, Bubills, Zusatzemissionen, own holdings (Eigenbestand), from the Finanzagentur's `schuldenbericht_dt.xlsx` (sheet `rpgUmlaufvolumen`). Not used as a ratio in the piece; released because it was built. |
| `cima_2024_Investments_Digest_extract.json` | All 32 tables and the text blocks of the 2024 edition's Infogram (`window.infographicData`), with the Infogram metadata (created 2025-07-17, updated 2026-01-30, fetched 2026-09-05). |
| `isd_2020_edition_tables.txt` … `isd_2023_edition_tables.txt` | The jurisdiction tables of the 2020–2023 Infogram editions as read in the browser, each block carrying the browser-side checksum. |
| `isd_pdf_editions_tables.txt` | The jurisdiction tables of the 2015–2019 PDF editions, transcribed from the PDF text layer, with page and figure references. |
| `build_isd_dataset.py` | Builds `isd_jurisdiction_all.csv` from the five text files and the JSON. Run in this folder; no dependencies beyond the standard library. |
| `verify_ck.py` | Recomputes the browser-side checksum of every block in the edition text files (`python3 verify_ck.py isd_202*_edition_tables.txt`). |

## Columns (`isd_jurisdiction_all.csv`)

`edition` — the digest edition (e.g. "ISD 2021"). `source` — page and figure
(PDF editions) or Infogram URL (2020 on). `column_year` — the year the column
refers to; each edition prints two, so each year appears in two editions
except 2015 and 2024. `jurisdiction` — as printed. `side` — long or short.
`instrument` — total, equities, st_debt, lt_debt, master_funds (long side
only). `value_usd_bn` — US$ bn, sign as printed (shorts negative).
`unit_published` — the 2023 and 2024 editions publish US$ millions; converted
and flagged. `note` — anomalies, see below.

## How the tables were read

PDF editions (2015–2019): the text layer, read with pdf.js in the browser and
transcribed; row and column sums were checked against the printed totals.
Infogram editions (2020–2024): the page's `window.infographicData` object,
walked to `elements.content.content.entities[id].props.chartData.data`; each
table was rendered to text in the browser with a checksum (the sum of the
absolute value of the first number in every cell), which `verify_ck.py`
recomputes. The 2023 edition is no longer linked from CIMA's archive page but
is live at Infogram id `1733fec4-2e19-4caf-894b-9c1847e2a9a4`.

The IMF series were read from `api.imf.org` (SDMX 2.1, dataflow
IMF.STA,PIP), key `CYM.<accounting entry>.<indicator>.<sector>.<counterpart
sector>.<counterpart>.<freq>`; the counterparts file has a checksum of
98,841.56 over 473 values.

## Source anomalies, kept verbatim

- 2018 PDF edition: the German and Irish long rows are scrambled with each
  other; the 2019 edition restates 2018 Germany long as LT 20, ST 11,
  equities 11, total 42. `isd_key_jurisdictions_two_reads.csv` uses the
  restatement; `isd_jurisdiction_all.csv` keeps both as printed, with a note.
- 2020 edition, US 2019 short-term debt short printed as (5) where the 2019
  PDF has −50; the column sum fails by 45. Kept as printed, noted.
- 2018 edition prints Canada's short equities at −50 with a row total of −6;
  the 2019 edition restates the total as −55.
- The 2024 edition's 2024 column prints total shorts of US$2,396bn against
  529bn in its 2023 column and 475bn in the IMF series for 2024; the digest's
  gross long and gross short exceed the IMF's by nearly the same amount in
  every country while nets agree within 1–3%. The piece treats which column
  continues the 2015–2023 series as unresolved; CIMA has been asked.

## What the series is, and is not

- Positions are reported only for countries reaching 10% of a fund's net
  asset value (FAR Completion Guide FAR-016-22-04, section 12); the tables
  are of positions above that line, 6% of the digest's own all-funds short
  book in 2015, 13% in 2023 and 46% in the 2024 column.
- No fund count is published for any country row.
- Long-term debt is by country of issuer; no issuer-sector split is published
  in either compilation.
- Digest positions are as at each fund's own financial year-end; the CPIS
  reference date is 31 December; the relation between the two is not
  published.

## Licence

Data files: CC BY 4.0. Code: MIT. The underlying tables are CIMA's and the
IMF's; cite the Investments Statistical Digest and the Portfolio Investment
Positions dataset for the source and this repository for the extraction.
