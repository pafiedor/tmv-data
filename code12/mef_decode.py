import os, sys, pdfplumber, pypdf, re, collections, json, statistics, warnings
warnings.filterwarnings('ignore')
def norm(s): return re.sub(r'\s+','',s).lower()
PCT=re.compile(r'^\d+\s*%$')

def clip_rects(path,pg):
    rd=pypdf.PdfReader(path); data=rd.pages[pg].get_contents().get_data().decode('latin-1')
    out=set()
    for m in re.finditer(r'(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+re\s*\n?\s*W\*?\s*\n?\s*n', data):
        x,y,w,h=[float(g) for g in m.groups()]
        if 100<w<560 and 40<h<420: out.add((round(x,2),round(y,2),round(w,2),round(h,2)))
    return sorted(out, key=lambda c:c[2]*c[3])

def charts(path,pg):
    pdf=pdfplumber.open(path); p=pdf.pages[pg]; PH=p.height
    _raw=[r for r in p.rects if 2.5<(r['x1']-r['x0'])<9.5]
    # Some editions (2017) draw a segment twice with different stroke colours;
    # dedup on geometry+fill or column sums are inflated and the chart is rejected.
    _seen=set(); allbars=[]
    for r in _raw:
        k=(round(r['x0'],2),round(r['top'],2),round(r['bottom'],2),str(r['non_stroking_color']))
        if k in _seen: continue
        _seen.add(k); allbars.append(r)
    words=[w for w in p.extract_words(use_text_flow=False) if not PCT.match(w['text'])]
    out=[]
    for (cx,cy,cw,ch) in clip_rects(path,pg):
        top=PH-(cy+ch); bot=PH-cy
        inb=[r for r in allbars if r['x0']>=cx-0.6 and r['x1']<=cx+cw+0.6 and r['top']>=top-1.5 and r['bottom']<=bot+8.0]
        if len(inb)<40: continue
        cols=collections.defaultdict(list)
        for r in inb: cols[round(r['x0'],0)].append(r)
        sums={x:sum(r['bottom']-r['top'] for r in rs) for x,rs in cols.items()}
        S=statistics.median(sorted(sums.values())[-max(6,len(sums)//2):])
        month_x=sorted([x for x,s in sums.items() if abs(s-S)/S < 0.025])
        if len(month_x)<12: continue
        # even spacing check
        d=[month_x[i+1]-month_x[i] for i in range(len(month_x)-1)]
        if max(d)-min(d) > 2.0: continue
        sw=[r for r in allbars if bot-1 < r['top'] < bot+140 and (r['bottom']-r['top'])<9.5]
        legmap={}
        for s in sorted(sw,key=lambda r:(round(r['x0'],0),r['top'])):
            cyy=(s['top']+s['bottom'])/2
            cand=sorted([w for w in words if abs((w['top']+w['bottom'])/2-cyy)<4.5
                         and w['x0']>=s['x1']-1 and w['x0']<s['x1']+240], key=lambda w:w['x0'])
            acc=[]
            for w in cand:
                if not acc and w['x0']-s['x1']>18: break
                if acc and w['x0']-acc[-1]['x1']>25: break
                acc.append(w)
            l=' '.join(w['text'] for w in acc)
            if l: legmap.setdefault(str(s['non_stroking_color']),l)
        months=[]
        for i,x in enumerate(month_x):
            rs=cols[x]; tot=sums[x]
            dd=collections.defaultdict(float)
            for r in rs: dd[str(r['non_stroking_color'])]+=(r['bottom']-r['top'])
            months.append({'i':i,'raw_sum_pct':round(100*tot/S,2),
                           'shares':{k:round(100*v/tot,3) for k,v in dd.items()}})
        out.append({'clip':(cx,cy,cw,ch),'S':S,'n_months':len(month_x),'legend':legmap,'months':months})
    return out


# The 2017 edition's counterparty chart has no legend swatches the binder can
# reach (they sit outside the clip band). Its palette is the 2016 edition's,
# whose legend WAS bound automatically; five of seven colours match exactly,
# including all three large categories. Applied only when auto-binding fails.
LEGEND_OVERRIDE = {
    2017: {
        "(0.0235, 0.275, 0.0863)": "Fondi gestione",
        "(0.843, 0.784, 0.0)":     "Fondi Hedge",
        "(0.627, 0.051, 0.0)":     "Banche",
        "(0.325, 0.553, 0.835)":   "Banche Centrali ed altre entita pubbliche",
        "(0.863, 0.902, 0.627)":   "Corporate&Retail",
        "(0.784, 0.298, 0.0588)":  "Compagnie assicurative",
        "(0.725, 0.804, 0.588)":   "Fondi pensione",
    },
}

def hf_chart(path,pg,edition=None):
    cs=charts(path,pg)
    good=[c for c in cs if any('fondihedge' in norm(v) for v in c['legend'].values())]
    if not good and edition in LEGEND_OVERRIDE:
        om=LEGEND_OVERRIDE[edition]
        for c in cs:
            fills={k for m in c['months'] for k in m['shares']}
            if len(fills & set(om))>=5:
                c['legend']={k:v for k,v in om.items() if k in fills}
                c['legend_source']='override'
                good=[c]; break
    if not good: raise RuntimeError('no HF chart among %d: %s'%(len(cs),[list(c['legend'].values()) for c in cs]))
    good.sort(key=lambda c:(-len(c['legend']), c['clip'][2]*c['clip'][3]))
    return good[0]

# 0-based page index of the nominal-BTP auction-order chart in each edition's PDF.
PAGES={2016:89,2017:79,2018:78,2019:71,2020:77,2021:70,2022:74,2023:69,2024:66,2025:66}
# Directory holding Rapporto-<edition>.pdf; override with MEF_PDF_DIR or first argv.
PDF_DIR=(sys.argv[1] if len(sys.argv)>1 else os.environ.get('MEF_PDF_DIR','pdfs'))
if __name__=='__main__':
    allr={}
    for y,pg in PAGES.items():
        try:
            r=hf_chart(os.path.join(PDF_DIR, f'Rapporto-{y}.pdf'),pg,edition=y)
            print(y,'months',r['n_months'],'nleg',len(r['legend']),
                  'rawsum %.2f'%(sum(m['raw_sum_pct'] for m in r['months'])/len(r['months'])),
                  '|', ', '.join(sorted(r['legend'].values())), flush=True)
            allr[y]=r
        except Exception as e: print(y,'FAIL',str(e)[:400],flush=True)
    json.dump({str(k):v for k,v in allr.items()},open('decoded_all.json','w'),ensure_ascii=False)
