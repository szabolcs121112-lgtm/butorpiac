"""Nyers JSONL -> termekek.csv, kepek_lista.csv, arelozmeny.csv (hozzáfűzés).
Használat: python3 feldolgoz.py <adatbazis mappa> <raw.jsonl> <dátum ÉÉÉÉ-HH-NN> [det.json] [rv.json]
- Ha a termék linkje már szerepel az adatbázisban: NEM lesz új termék, csak új sor az arelozmeny.csv-ben (heti árfrissítés).
- det.json: {termék-kulcs: [szövet, láb]}, rv.json: {termék-kulcs: értékelésszám} – a termékoldalakról, nem kötelező."""
import csv,json,re,unicodedata,collections,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from p import FX,prices,typ
D=sys.argv[1].rstrip('/')+'/'; RAW=sys.argv[2]; DATUM=sys.argv[3]
old=list(csv.DictReader(open(D+'termekek.csv',encoding='utf-8-sig'),delimiter=';'))
hdr=list(old[0].keys())
raw=[json.loads(l) for l in open(RAW,encoding='utf8')]
det=json.load(open(sys.argv[4])) if len(sys.argv)>4 else {}; rv=json.load(open(sys.argv[5])) if len(sys.argv)>5 else {}
CUR={'DE':'EUR','AT':'EUR','NL':'EUR','BE':'EUR','LU':'EUR','SK':'EUR','SI':'EUR','HR':'EUR','BG':'EUR','CH':'CHF','PL':'PLN','CZ':'CZK','HU':'HUF','BA':'BAM','RS':'RSD','RO':'RON'}
PCS={'DE':'Német és osztrák piac','AT':'Német és osztrák piac','NL':'Benelux','BE':'Benelux','LU':'Benelux'}
PCS.update({c:'Környező országok' for c in ('CH','PL','CZ','SK','HU')}); PCS.update({c:'Balkán' for c in ('SI','HR','BA','RS','RO','BG')})
oldurl={x['forras']:x for x in old}; frissit=[]
def band(p,t):
    if p>3500: return None
    if p<600: return 'ágy 600 € alatt' if t=='Franciaágy' else None
    for i,(a,b) in enumerate([(600,1500),(1500,2000),(2000,2500),(2500,3000),(3000,3500.01)]):
        if a<=p<b: return f'{i+1}. ársáv'
def slug(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode()
    return re.sub(r'[^A-Za-z0-9]+','-',s).strip('-')[:45].strip('-')
def art(u):
    m=re.search(r'-(\d{9,12}[A-Z]?)/?$',u) or re.search(r'-(s\d{8})/?$',u)
    return m.group(1) if m else None
COL=r'(szürk\w*|sed\w*|šed\w*|siv\w*|béž\w*|bézs|krém\w*|antracit\w*|fekete|čern\w*|čiern\w*|beige|grau|weiss|zöld|zelen\w*|kék|modr\w*|niebiesk\w*|beżow\w*|szar\w*|taupe|žlt\w*|türkiz|piros|ružov\w*|mentazöld|barn\w*|hned\w*)'
nid=max(int(x['id']) for x in old)+1
oldart=collections.defaultdict(list)
for x in old:
    a=art(x['forras']); 
    if a: oldart[a].append(x['id'])
rows=[];imgs=[];hist=[];skip=[];reg=collections.Counter();seen=set()
for r in raw:
    url=r['base']+r['path']
    if url in seen: continue
    seen.add(url)
    known=oldurl.get(url)
    cc=r['cc'];cur=CUR[cc];tx0=r['tx'].split('KARTYA')[0];ps=prices(tx0,cur);kp=prices(r['tx'].split('KARTYA')[1],cur) if 'KARTYA' in r['tx'] else []
    if not ps: skip.append(('ár nem olvasható',r['tx'][:50]));continue
    act=min(ps); ath=max(ps) if len(ps)>1 and max(ps)>act else None
    ak=round(kp[0]/FX[cur],2) if kp else ''
    eur=round(act/FX[cur],2); athe=round(ath/FX[cur],2) if ath else ''
    if known:
        hist.append([known['id'],DATUM,eur,ak,url]); frissit.append((known['id'],known['ar_eur'],eur)); continue
    name=re.split(r'\s(?:XXXLutz|XXXLesnina|Lesnina XXXL|Möbelix|mömax|IKEA|Kondela|ASKO|Agata|VOX|micasa|Mobexpert|Videnov)\b',tx0)[0]
    name=re.sub(r'\s*(statt|místo|namiesto|zamiast|helyett|od)?\s*(CHF\s*)?[\d\s.,‒-]+(Kč|Ft|zł|€|CHF|\.-)?\**\s*$','',name).strip()
    name=re.sub(r'(\s(statt|místo|namiesto|od))?(\s(CHF\s)?\d[\d\s.,‒\'-]*(Kč|Ft|zł|€|\.-)?\**)+$','',name).strip()
    t=typ(name)
    b=band(eur,t)
    if not b: skip.append(('sávon kívül',cc,r['store'],name[:40],eur));continue
    i=nid;nid+=1; reg[(cc,r['store'])]+=1
    mk=''
    m=re.search(r"(Hom`in|Welnova|Stylife|Beldomo System|Modern Living|Bessagi Home|Based|Ti'me|Carryhome|Xora|P & B|MID\.YOU|Cantus|Livetastic|Dieter Knoll|Lomoco|Hom`in|Beldomo Style|Based|Premium Living|Johann Jakob|Hom'In|Bloomingloft|edy&liv|PURA VIDA|Edition|Tom Tailor)",r['tx'])
    if m: mk=m.group(1)
    elif r['store'].startswith('IKEA'): mk='IKEA'
    else: mk=r['store'].split(' (')[0]
    key=r['path'].strip('/').split('/')[-1]
    dd=det.get(key,['',''])
    sz=dd[0]
    if not sz:
        mm=re.search(r'(textil|látka|tkanina|Stoff|szövet|kord|Cord|Leder|koža|kůže|bőr)',name,re.I); sz=mm.group(1) if mm else ''
    grp='bőr' if re.search(r'bőr|leder|koža|kůže|skóra',sz+' '+name,re.I) else ('kord' if re.search(r'kord|cord|sztruks',sz+name,re.I) else ('zsenília' if re.search(r'zsenília|ženil|žinil',sz,re.I) else ('szövet' if sz else 'ismeretlen')))
    col=re.search(COL,name,re.I)
    lab=dd[1] if dd[1] not in ('','—') else ''
    img=r['img']; ext='png' if '.png' in img else ('webp' if '.webp' in img else ('avif' if '.avif' in img else 'jpg'))
    folder=f"{cc}\\{re.sub(r'[^A-Za-z0-9-]+','-',r['store'].replace('ö','oe').replace('ü','ue').replace('á','a').replace('ó','o')).strip('-')}\\{i}_{slug((mk+' '+name) if mk not in name else name)}"
    fn=[]
    if t!='Franciaágy' and re.search(r'ágyaz|rozkl|rozkład|bett|schlaf|spania',name,re.I): fn.append('ágyfunkció')
    if re.search(r'relax',name+sz,re.I): fn.append('relax')
    if re.search(r'U-alak|tvare U|\bU\b|U alak',name): fn.append('U-alak')
    if ath and ath>=2*act: fn.append('erős áthúzás')
    st='továbbengedve, képre vár' if lab else 'továbbengedve, lábadat hiányzik – visszaküldve'
    rows.append(dict(id=i,gyujtes_datum=DATUM,orszag=cc,piaccsoport=PCS[cc],aruhaz=r['store'],termek=name,marka=mk,tipus=t,ar_eur=eur,akcios_ar_eur=ak,athuzott_ar_eur=athe,eredeti_ar=act,penznem=cur,arsav=b,szovet=sz,szovet_csoport=grp,lab=lab,lab_foto='hiányzik – az ügynök tovább keresi',kep_butor=folder+'\\butor_1.'+ext,kep_szovet='hiányzik',kep_lab='hiányzik',funkciok='; '.join(fn),ertekelesek=rv.get(key,''),nepszeruseg_helyezes=reg[(cc,r['store'])],statusz=st,forras=url,ugynok=f'{cc}-1',azonos_modell=''))
    imgs.append([i,'butor',img,folder+'\\butor_1.'+ext,url])
    hist.append([i,DATUM,eur,ak,url])
# azonos modell
byart=collections.defaultdict(list)
for x in rows:
    a=art(x['forras'])
    if a: byart[a].append(x)
for a,xs in byart.items():
    ids=[str(x['id']) for x in xs]+oldart.get(a,[])
    if len(ids)>1:
        for x in xs: x['azonos_modell']=','.join(j for j in ids if j!=str(x['id']))
w=csv.DictWriter(open(D+'termekek.csv','a',encoding='utf-8',newline=''),fieldnames=hdr,delimiter=';');[w.writerow(x) for x in rows]
cw=csv.writer(open(D+'kepek_lista.csv','a',encoding='utf-8',newline=''),delimiter=';');cw.writerows(imgs)
cw=csv.writer(open(D+'arelozmeny.csv','a',encoding='utf-8',newline=''),delimiter=';');cw.writerows(hist)
json.dump(dict(skip=skip,frissit=frissit,reg={f'{k[0]}|{k[1]}':v for k,v in reg.items()}),open(RAW+'.meta.json','w'),ensure_ascii=False,indent=1)
print(len(rows),'új termék;',len(frissit),'ismert termék árfrissítése')
if rows: print('id',rows[0]['id'],'-',rows[-1]['id'])
print(collections.Counter(x['orszag'] for x in rows)); print(collections.Counter(x['arsav'] for x in rows)); print(collections.Counter(x['tipus'] for x in rows))
print('azonos:',[(x['id'],x['azonos_modell']) for x in rows if x['azonos_modell']])
print('skip',skip)
for x in rows[:300]: print(x['id'],x['orszag'],x['aruhaz'][:10],'|',x['termek'][:45],'|',x['tipus'],x['ar_eur'],x['athuzott_ar_eur'],x['arsav'],x['funkciok'])
