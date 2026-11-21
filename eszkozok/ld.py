"""Böngészőből kimentett listák (b*.txt) -> nyers JSONL.
Fájlformátum: fejléc sor ORSZÁG|Áruház|https://alap.url, utána soronként: /utvonal | látható szöveg árakkal [KARTYA kártyás ár] | kép URL
Használat: python3 ld.py raw.jsonl b1.txt b2.txt ..."""
import json,sys,re
from p import *
out=open(sys.argv[1],'a',encoding='utf8')
for fn in sys.argv[2:]:
  cc=st=base=None
  for L in open(fn,encoding='utf8'):
    L=L.rstrip('\n')
    if not L.strip(): continue
    if not L.startswith('/') and not L.startswith('http') and L.count('|')==2 and ' | ' not in L:
      cc,st,base=L.split('|'); continue
    path,tx,img=[x.strip() for x in L.split(' | ')]
    out.write(json.dumps(dict(cc=cc,store=st,base=base,path=path,tx=tx,img=img),ensure_ascii=False)+'\n')
