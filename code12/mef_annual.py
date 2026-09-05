"""Annual table from the monthly file (mef_auction_orders_all.csv).

Rule: for each calendar year use the later of the two editions that draw it;
report the other edition's hedge-fund reading beside it. Empty cells in the
monthly file (no segment drawn) count as zero, which is MEF's own treatment
of null-or-negative months. Window: editions 2016-17 use the old definition
(announcement to the day after the auction); 2018 onward the new one (day
after announcement to the day before settlement).
"""
import math
import pandas as pd
def r1(x):  # round half up (avoids banker's rounding on exact .x5 means)
    return math.floor(x*10+0.5)/10
CATS = ['hedge_funds','asset_managers','banks','official','insurers','pension','corporate_retail']
d = pd.read_csv('mef_auction_orders_all.csv')
d[CATS] = d[CATS].fillna(0.0)
m = d.groupby(['edition','year'])[CATS].mean().apply(lambda col: col.map(r1))
n = d.groupby(['edition','year']).size().rename('n_months')
rows = []
for year in sorted(d.year.unique()):
    eds = sorted(d.loc[d.year == year, 'edition'].unique())
    use, other = eds[-1], (eds[0] if len(eds) > 1 else None)
    r = {'year': year, 'edition_used': use, 'n_months': int(n[(use, year)])}
    r.update(m.loc[(use, year)].to_dict())
    r['also_in_edition'] = other if other else ''
    r['hedge_funds_other_edition'] = m.loc[(other, year), 'hedge_funds'] if other else ''
    r['window_basis'] = ('OLD (announcement to day after auction)' if use <= 2017
                         else 'NEW (day after announcement to day before settlement)')
    rows.append(r)
out = pd.DataFrame(rows)
out.to_csv('mef_auction_orders_annual.csv', index=False)
print(out[['year','edition_used'] + CATS + ['also_in_edition','hedge_funds_other_edition']].to_string(index=False))
