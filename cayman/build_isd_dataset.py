"""Build isd_jurisdiction_all.csv from the CIMA Investments
Statistical Digest jurisdiction-of-issuer tables, 2015–2024 editions.

Sources (all read 5 Sep 2026):
  - PDF editions 2015–2019: text layers transcribed in isd_pdf_editions_tables.txt
  - Infogram editions 2020–2024: window.infographicData tables in
    isd_<year>_edition_tables.txt (checksummed) and the 2024 extract JSON.

Long format, one row per (edition, column_year, jurisdiction, side, instrument).
Values in US$ billions as published (the 2023 and 2024 editions publish US$
millions; converted /1000 and flagged in `unit_published`). Negative = short.
"""
import csv, json, re, sys, os

ROWS = []
LONG_COLS = ['total', 'equities', 'master_funds', 'st_debt', 'lt_debt']
SHORT_COLS = ['total', 'equities', 'st_debt', 'lt_debt']

def num(s):
    s = s.strip()
    if s in ('', '-', 'N/A'):
        return None
    neg = s.startswith('(') or s.startswith('-')
    s2 = re.sub(r'[^\d.]', '', s)
    if s2 == '':
        return None
    v = float(s2)
    return -v if neg else v

def add(edition, source, col_year, jur, side, inst, val, unit_pub, note=''):
    if val is None:
        return
    ROWS.append(dict(edition=edition, source=source, column_year=col_year,
                     jurisdiction=jur.strip(), side=side, instrument=inst,
                     value_usd_bn=round(val, 3), unit_published=unit_pub, note=note))

# ---------- PDF editions ----------
txt = open('isd_pdf_editions_tables.txt', encoding='utf-8').read()
for block in re.split(r'\n### ', txt)[1:]:
    head, _, body = block.partition('\n')
    m = re.match(r'(\d{4}) (long|short) \| file=(\S+) page=(\d+) figure=(\S+) \|.*years: ([\d,]+)', head)
    if not m:
        continue
    ed, side, fname, page, fig, years = m.groups()
    years = years.split(',')
    cols = LONG_COLS if side == 'long' else SHORT_COLS
    src = f'ISD {ed} PDF {fname} p.{page} Fig.{fig}'
    body = body.split('\n\n')[0]
    for line in body.strip().split('\n'):
        parts = [p.strip() for p in line.split('|')]
        jur, vals = parts[0], parts[1:]
        assert len(vals) == len(cols) * len(years), (head, line)
        for ci, c in enumerate(cols):
            for yi, y in enumerate(years):
                add(f'ISD {ed}', src, int(y), jur, side, c, num(vals[ci * len(years) + yi]), 'US$ bn')

# ---------- Infogram editions 2020–2023 (checksummed text files) ----------
for ed in ['2020', '2021', '2022', '2023']:
    t = open(f'isd_{ed}_edition_tables.txt', encoding='utf-8').read()
    src_url = re.search(r'SOURCE: (\S+)', t).group(1)
    unit = 'US$ m' if ed == '2023' else 'US$ bn'
    scale = 1000.0 if unit == 'US$ m' else 1.0
    for block in re.split(r'\n### ', t)[1:]:
        head, _, body = block.partition('\n')
        key = head.split()[0]
        if key not in ('long', 'short'):
            continue
        side = key
        cols = LONG_COLS if side == 'long' else SHORT_COLS
        lines = body.split('\n\n')[0].strip().split('\n')
        # find the year header row (first row whose non-empty cells are all years)
        yrow = None
        for i, line in enumerate(lines[:3]):
            cells = [c.strip() for c in line.split('|')]
            ys = [c for c in cells if c]
            if ys and all(re.fullmatch(r'\d{4}', c) for c in ys):
                yrow = i; years = ys[:2]; break
        assert yrow is not None, (ed, side)
        for line in lines[yrow + 1:]:
            parts = [p.strip() for p in line.split('|')]
            jur, vals = parts[0], parts[1:]
            if not jur:
                continue
            assert len(vals) == len(cols) * 2, (ed, side, line)
            for ci, c in enumerate(cols):
                for yi, y in enumerate(years):
                    v = num(vals[ci * 2 + yi])
                    if v is not None:
                        v = v / scale
                    add(f'ISD {ed}', f'ISD {ed} Infogram {src_url}', int(y), jur, side, c, v, unit)

# ---------- 2024 edition (extract JSON) ----------
J = json.load(open('cima_2024_Investments_Digest_extract.json', encoding='utf-8'))
T = J['tables']
src24 = 'ISD 2024 Infogram ' + J['meta']['url']
def sheet(tid):
    return T[tid]['sheets'][0]
# long: a594c90b..., short: d40dbfae...
for tid, side in [('a594c90b-7d2e-454b-ad54-06267e92c22b', 'long'), ('d40dbfae-03ec-43be-b255-f3d221eb38a4', 'short')]:
    s = sheet(tid)
    cols = LONG_COLS if side == 'long' else SHORT_COLS
    years = [str(c).strip() for c in s[1][1:]]
    for r in s[2:]:
        jur = str(r[0]).strip()
        vals = [('' if c is None else str(c)) for c in r[1:]]
        assert len(vals) == len(cols) * 2, (side, r)
        for ci, c in enumerate(cols):
            for yi in range(2):
                v = num(vals[ci * 2 + yi])
                if v is not None:
                    v = v / 1000.0
                add('ISD 2024', src24, int(years[ci * 2 + yi]), jur, side, c, v, 'US$ m')

# ---------- normalise jurisdiction names ----------
NORM = {'United kingdom': 'United Kingdom', 'Hong Kong SAR': 'Hong Kong'}
for r in ROWS:
    r['jurisdiction'] = NORM.get(r['jurisdiction'], r['jurisdiction'])

os.makedirs('out', exist_ok=True)
with open('isd_jurisdiction_all.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(ROWS[0].keys()))
    w.writeheader(); w.writerows(ROWS)
print('rows', len(ROWS))

# ---------- arithmetic checks ----------
import collections
D = collections.defaultdict(dict)
for r in ROWS:
    D[(r['edition'], r['column_year'], r['side'], r['jurisdiction'])][r['instrument']] = r['value_usd_bn']
bad = 0
for (ed, y, side, jur), d in D.items():
    parts = [k for k in d if k != 'total']
    if 'total' in d and len(parts) == (4 if side == 'long' else 3):
        s = sum(d[k] for k in parts)
        tol = 2.5 if ed not in ('ISD 2023', 'ISD 2024') else 0.01
        if abs(s - d['total']) > tol:
            bad += 1
            print(f'ROW-SUM {ed} {y} {side} {jur}: parts={s:.2f} total={d["total"]:.2f}')
# column sums vs Total row
cols_by = collections.defaultdict(lambda: collections.defaultdict(float))
tot_by = {}
for r in ROWS:
    k = (r['edition'], r['column_year'], r['side'], r['instrument'])
    if r['jurisdiction'] == 'Total':
        tot_by[k] = r['value_usd_bn']
    else:
        cols_by[k][r['jurisdiction']] += r['value_usd_bn']
for k, d in cols_by.items():
    s = sum(d.values())
    if k in tot_by:
        tol = max(3.0, 0.01 * abs(tot_by[k])) if k[0] not in ('ISD 2023', 'ISD 2024') else 0.05
        if abs(s - tot_by[k]) > tol:
            bad += 1
            print(f'COL-SUM {k}: rows={s:.2f} total={tot_by[k]:.2f}')
print('arithmetic anomalies:', bad)
