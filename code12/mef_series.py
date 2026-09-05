import json, re, collections, warnings, statistics
warnings.filterwarnings('ignore')
import pdfplumber
from mef_decode import hf_chart, PAGES, norm  # run: MEF_PDF_DIR=pdfs python3 mef_series.py
import csv

import os
BASE=os.path.join(os.environ.get('MEF_PDF_DIR','pdfs'),'Rapporto-%d.pdf')
CANON={'fondigestione':'asset_managers',"fondid'investimento":'asset_managers','banche':'banks','fondihedge':'hedge_funds',
       'bancheCentralialtreentitàpubbliche':'official','compagnieassicurative':'insurers','fondipensione':'pension',
       'corporate&retail':'corporate_retail'}
def canon(lbl):
    n=norm(lbl)
    if 'hedge' in n: return 'hedge_funds'
    if n.startswith('banchecentrali'): return 'official'
    if n=='banche': return 'banks'
    if 'gestione' in n or "investimento" in n: return 'asset_managers'
    if 'assicurat' in n: return 'insurers'
    if 'pensione' in n: return 'pension'
    if 'corporate' in n: return 'corporate_retail'
    return 'UNK:'+lbl

rows=[]
caps={}
for y,pg in PAGES.items():

    r=hf_chart(BASE%y, pg, edition=y)
    # caption year range
    p=pdfplumber.open(BASE%y).pages[pg]
    t=p.extract_text() or ''
    m=re.search(r'ANNI\s*(\d{4})\s*[-–]\s*(\d{4})', re.sub(r'\s+',' ',t.upper()))
    caps[y]=m.groups() if m else None
    y0 = int(m.group(1)) if m else y-1
    cmap={k:canon(v) for k,v in r['legend'].items()}
    n=r['n_months']
    for mo in r['months']:
        idx=mo['i']
        yr = y0 + idx//12; mth = idx%12 + 1
        d={'edition':y,'year':yr,'month':mth,'raw_sum_pct':mo['raw_sum_pct'],'n_series':len(r['legend'])}
        for k,v in mo['shares'].items():
            d[cmap.get(k,'UNK')] = v
        rows.append(d)
print('captions:',caps)
cats=['hedge_funds','asset_managers','banks','official','insurers','pension','corporate_retail']
with open('mef_auction_orders_all.csv','w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=['edition','year','month','raw_sum_pct','n_series']+cats)
    w.writeheader()
    for r0 in rows:
        w.writerow({k: (round(r0.get(k),3) if isinstance(r0.get(k),float) else r0.get(k,'')) for k in w.fieldnames})
# annual means
print('\nAnnual simple means of monthly shares (hedge_funds), by edition:')
agg=collections.defaultdict(list)
for r0 in rows: agg[(r0['edition'],r0['year'])].append(r0.get('hedge_funds',0.0))
for k in sorted(agg): print('  ed%d %d  n=%2d  HF=%.1f'%(k[0],k[1],len(agg[k]),sum(agg[k])/len(agg[k])))
