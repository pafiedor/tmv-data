"""Share of MMLF collateral bought from the borrower's own fund family.

Input: refs/fed_mmlf_section11s_transactions_2022-03-31.xlsx (Federal Reserve
Section 11(s) MMLF transaction-specific disclosures, published 31 Mar 2022).
One row per pledged CUSIP; 'Amortized Cost' is the collateral amount per row
(the 'Loan Amount' column repeats per loan, so it is not summed).

Each seller is classified as own-family (the borrower's group sponsors the
fund), other-family, or unattributed (an abbreviation or generic master-fund
name whose sponsor is not stated in the file). Reported:
  central = own-family / total
  upper bound = (own-family + all unattributed sellers bought by that
                 borrower) / total, i.e. every unattributed seller is treated
                 as the borrower's own fund.
Output: mmlf_own_family_summary.csv, mmlf_unattributed_sellers.csv.
"""
import pathlib, re
import pandas as pd
HERE = pathlib.Path(__file__).resolve().parent
df = pd.read_excel(HERE / "section-11s-mmlf-transaction-specific-disclosures-03-31-22.xlsx", sheet_name="MMLF 11(s) Data")
df.columns = [c.strip() for c in df.columns]
df["seller"] = df["Money Market Mutual Fund Seller"].astype(str).str.replace("\xa0", " ").str.strip()

OWN = {  # borrower -> regex for its own fund family
    "MMLF STATE STREET B&TC": r"state street|\bssga\b",
    "MMLF JP MORGAN SCTYS LLC": r"jp ?morgan|\bjpm\b",
    "MMLF GOLDMAN SACHS BROK DLR": r"goldman|\bgs\b|gsam|financial square",
    "MMLF CITIGROUP GLOBAL MKTS": r"\bciti",
    "MMLF CREDIT SUISSE NY": r"credit suisse",
    "MMLF BK OF NY MELLON": r"dreyfus|\bbny\b|mellon",
    "MMLF BK OF NOVA SCOTIA NYA": r"scotia",
    "MMLF RBC CAP MKTS": r"\brbc\b|royal bank",
    "MMLF ROYAL BK OF CANADA NY BR": r"\brbc\b|royal bank",
}
KNOWN = r"(blackrock|tempfund|tempcash|plan investment fund|dfa |dws |dreyfus|federated|fidelity|financial square|goldman|\bgs |gsam|jp ?morgan|jpm|invesco|morgan stanley|msilf|msift|northern|pgim|prudential|schwab|state street|t\. rowe|ubs|usaa|wells fargo|western asset|first american|heritage money market|cash investment money market|prime master fund|prime cnav master fund)"
def cls(row):
    s = row.seller.lower(); b = row.Borrower
    if re.search(OWN.get(b, r"$^"), s): return "own"
    if re.search(KNOWN, s): return "other"
    return "unattributed"
df["class"] = df.apply(cls, axis=1)
tot = df["Amortized Cost"].sum()
rows = []
for b, d in df.groupby("Borrower"):
    a = d.groupby("class")["Amortized Cost"].sum()
    rows.append({"borrower": b, "total_usd": d["Amortized Cost"].sum(), "own_usd": a.get("own", 0.0),
                 "unattributed_usd": a.get("unattributed", 0.0)})
out = pd.DataFrame(rows).sort_values("total_usd", ascending=False)
own = out.own_usd.sum(); un = out.unattributed_usd.sum()
out.loc[len(out)] = {"borrower": "ALL", "total_usd": tot, "own_usd": own, "unattributed_usd": un}
out["own_share"] = out.own_usd / out.total_usd
out["upper_bound_share"] = (out.own_usd + out.unattributed_usd) / out.total_usd
out.to_csv(HERE / "mmlf_own_family_summary.csv", index=False)
ua = df[df["class"] == "unattributed"].groupby(["seller", "Borrower"])["Amortized Cost"].sum().reset_index()
ua.to_csv(HERE / "mmlf_unattributed_sellers.csv", index=False)
df[["Loan Date","Borrower","Loan ID Number","CUSIP","seller","Amortized Cost","Collateral Type","class"]].to_csv(HERE / "mmlf_rows_classified.csv", index=False)
print(f"loan dates {df['Loan Date'].min():%Y-%m-%d} to {df['Loan Date'].max():%Y-%m-%d}; rows {len(df)}")
print(out.assign(total_bn=out.total_usd/1e9, own_mn=out.own_usd/1e6, unattr_mn=out.unattributed_usd/1e6)[["borrower","total_bn","own_mn","unattr_mn","own_share","upper_bound_share"]].round(4).to_string(index=False))
print(); print(ua.assign(mn=ua["Amortized Cost"]/1e6).drop(columns="Amortized Cost").round(1).to_string(index=False))
