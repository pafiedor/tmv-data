# The Sponsor of Last Resort — data and classification

Companion files to *The Sponsor of Last Resort*, The Macro Prudential View
(themacroprudentialview.substack.com), on who bears the loss when a fund's own
group buys it out of a run: Rule 17a-9 in the United States, Article 35 of the
MMF Regulation in the EU, and the Chinese rules behind the PBoC's Bond Market
NBFI Swap Facility (October 2026).

The files reproduce the piece's two US figures: the sponsor support reported on
Form N-CR in March 2020, and the share of collateral pledged to the Federal
Reserve's Money Market Mutual Fund Liquidity Facility (MMLF) that the borrower
bought from its own fund family.

## Files

| File | What it is |
|---|---|
| `section-11s-mmlf-transaction-specific-disclosures-03-31-22.xlsx` | The Federal Reserve's section 11(s) MMLF transaction file, published 31 March 2022, unchanged. One row per pledged security; loans dated 23 March to 23 April 2020. |
| `mmlf_own_family.py` | Classifies each row's selling fund as the borrower's own family, another named sponsor's, or unattributed, and writes the three CSVs below. Run in this folder (`python3 mmlf_own_family.py`); needs pandas and openpyxl. |
| `mmlf_rows_classified.csv` | Every row of the Fed file with the classification (`own` / `other` / `unattributed`). |
| `mmlf_own_family_summary.csv` | Totals by borrower: collateral, own-family, unattributed, own share, upper-bound share. |
| `mmlf_unattributed_sellers.csv` | The sellers the file names only by abbreviation or a generic master-fund name, with amounts by borrower. |
| `ncr2020-reconciliation.csv` | Every Form N-CR and N-CR/A filed in the first half of 2020 (EDGAR form indexes 2020 Q1 and Q2; Q2 has none), with accession number, support type, provider, date and amount, and which filings are amendments that consolidate earlier ones. |

## Method and results

- Value field: `Amortized Cost`, which the Fed defines as the amortised cost or
  fair value of the pledged security and the price the borrower paid the fund.
  It sums to the loan amounts (USD 58.01bn). Rows that repeat a CUSIP within a
  loan are separate pledges and are kept.
- Own family: the seller's name matches the borrower group's fund brands
  (regexes in the script: e.g. Goldman Sachs = "goldman", "GS", "GSAM",
  "Financial Square"). Other: the seller matches a named sponsor that is not the
  borrower's. Unattributed: everything else.
- Result: USD 115.1m own-family of USD 58.01bn, 0.20% (all Goldman Sachs's
  broker-dealer, 25 March 2020). Upper bound treating every unattributed seller
  as the borrower's own: 2.96%. Restricted to the four borrowers whose groups ran
  money market funds (State Street, JPMorgan, Goldman Sachs, BNY Mellon): 0.23%
  of USD 50.25bn, upper bound 2.99%.
- N-CR: six unique Rule 17a-9 purchases totalling USD 3,996,532,321.32 (BNY
  Mellon USD 2,153,825,614.32; Goldman Sachs USD 1,842,706,707) and one capital
  contribution of USD 89,000.

## Caveats

Seller attribution is by fund name in March 2020 and could misassign a fund
whose sponsor changed. Five Goldman Financial Square securities pledged on
25 March 2020 do not appear in any Goldman N-CR filing; the files do not show
why. Corrections welcome.
