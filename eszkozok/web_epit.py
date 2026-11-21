"""termekek.csv -> weboldal adatai (termekek.json + th/<id>.jpg bélyegképek).
Használat: python3 web_epit.py <adatbazis mappa> <kepek mappa> <web mappa>"""
import csv,json,os,sys
from PIL import Image
D,K,W=sys.argv[1:4]
G={'Német és osztrák piac':'DACH','Benelux':'BNL','Környező országok':'KOR','Balkán':'BAL'}
def fl(v):
    try: return float(v) if v not in ('',None) else None
    except ValueError: return None
rows=list(csv.DictReader(open(os.path.join(D,'termekek.csv'),encoding='utf-8-sig'),delimiter=';'))
os.makedirs(os.path.join(W,'th'),exist_ok=True);out=[];nimg=0
for r in rows:
    i=int(r['id']);th=os.path.join(W,'th',f'{i}.jpg');src=os.path.join(K,r['kep_butor'].replace('\\','/')) if r['kep_butor'] else ''
    if not os.path.exists(th) and src and os.path.exists(src):
        try:
            im=Image.open(src).convert('RGB');im.thumbnail((220,220));im.save(th,'JPEG',quality=80)
        except Exception as e: print('kép hiba',i,e)
    has=os.path.exists(th);nimg+=has
    b=r['arsav'];b=int(b.split('.')[0]) if b[:1].isdigit() else 0
    out.append(dict(id=i,g=G.get(r['piaccsoport'],r['piaccsoport']),o=r['orszag'],a=r['aruhaz'],n=r['termek'],m=r['marka'],t=r['tipus'],
      p=fl(r['ar_eur']),k=fl(r['akcios_ar_eur']),x=fl(r['athuzott_ar_eur']),b=b,sz=r['szovet'],sc=r['szovet_csoport'],l=r['lab'],
      f=[x.strip() for x in r['funkciok'].split(';') if x.strip()],r=r['ertekelesek'],u=r['forras'],
      az=[x for x in r['azonos_modell'].split(',') if x],img=has,op=r['eredeti_ar'],cur=r['penznem']))
json.dump(out,open(os.path.join(W,'termekek.json'),'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print(len(out),'termék,',nimg,'képpel')
