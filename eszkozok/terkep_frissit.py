"""A bútorpiac-térkép (artifact) beágyazott VALOS adatainak frissítése a termekek.csv-ből.
Használat: python3 terkep_frissit.py <terkep.html be> <adatbazis mappa> <terkep.html ki> [kor.json]
kor.json (nem kötelező): {"naplo":[{d,o,ag,t,ok}], "ug":{"DE-1":["XXXLutz (21)",..]}, "utolso":"...", "kimutatas":"..."}
 - naplo: az új sorok a lista elejére kerülnek; ug: ügynökönként felülírja; utolso/kimutatas: felülírja."""
import re,json,csv,sys,os
src,D,dst=sys.argv[1:4]
s=open(src,encoding='utf-8').read();m=re.search(r'VALOS\s*=\s*',s);obj,end=json.JSONDecoder().raw_decode(s[m.end():])
rows=list(csv.DictReader(open(os.path.join(D,'termekek.csv'),encoding='utf-8-sig'),delimiter=';'))
def band(b): return int(b.split('.')[0]) if b[:1].isdigit() else 0
db=[dict(d=r['gyujtes_datum'],o=r['orszag'],a=r['aruhaz'],n=r['termek'],tp=r['tipus'],ar=round(float(r['ar_eur'])),s=band(r['arsav']),
   sz=r['szovet'] or '–',lb=r['lab'] or '–',f=[x.strip() for x in re.split(r'[;,]',r['funkciok']) if x.strip()],
   lf=bool(r['lab']) and 'lábfotó' not in r['statusz'],st=r['statusz'],ag=r['ugynok'],id=int(r['id'])) for r in rows]
obj['db']=sorted(db,key=lambda x:-x['id'])
if len(sys.argv)>4:
    k=json.load(open(sys.argv[4],encoding='utf-8'))
    obj['naplo']=k.get('naplo',[])+obj.get('naplo',[])
    obj.setdefault('ug',{}).update(k.get('ug',{}))
    for f in ('utolso','kimutatas'):
        if f in k: obj[f]=k[f]
s=s[:m.end()]+json.dumps(obj,ensure_ascii=False)+s[m.end()+end:]
open(dst,'w',encoding='utf-8').write(s);print(len(db),'termék a térképen')
