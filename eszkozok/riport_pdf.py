"""Háromnyelvű PDF-kimutatás (HU/EN/DE). Használat: PK_DB=.. PK_TH=.. PK_DATUM=.. python3 riport_pdf.py HU|EN|DE
TH mappa: <id>.jpg (400 px bútor), <id>_szovet.jpg, <id>_lab.jpg bélyegképek."""
import csv,sys,os
DB=os.environ.get('PK_DB','/mnt/user-data/outputs/Piackutatas/adatbazis');TH=os.environ.get('PK_TH','/home/claude/riport/th');OUTD=os.environ.get('PK_OUT','/mnt/user-data/outputs/Piackutatas/kimutatasok');DATUM=os.environ.get('PK_DATUM','2026-11-21')
from i18n3 import T,tr,LANG
from collections import Counter
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
F='/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('S',F+'DejaVuSans.ttf'));pdfmetrics.registerFont(TTFont('SB',F+'DejaVuSans-Bold.ttf'));pdfmetrics.registerFont(TTFont('SR',F+'DejaVuSerif.ttf'))
from reportlab.lib.fonts import addMapping
from reportlab.platypus import Image as RLImage
import os
def sm(i,t,w):
    p=f'{TH}/{i}_{t}.jpg'
    return RLImage(p,width=w,height=w) if os.path.exists(p) else None
def cellimg(i,t,txt,w):
    im=sm(i,t,w)
    if im is None: return Paragraph(txt,C)
    return Table([[im],[Paragraph(txt,C)]],colWidths=[None],style=[('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),1)])
def lnk(u,i):
    if not u.startswith('http'): return ''
    u=u.replace('&','&amp;')
    t=T['prod'] if (i>=47 or '/artikel/' in u) else T['list']
    return f'<br/><a href="{u}" color="#1a5fb4"><u>{t}</u></a>'
def pic(i,w):
    p=f'{TH}/{i}.jpg'
    if not os.path.exists(p): return Paragraph('<font color="#9a978f">'+T['nophoto']+'</font>',C)
    from PIL import Image as PI
    iw,ih=PI.open(p).size; h=w*ih/iw
    return RLImage(p,width=w,height=h)
addMapping('S',0,0,'S');addMapping('S',1,0,'SB');addMapping('S',0,1,'S');addMapping('S',1,1,'SB')
INK=HexColor('#1f1e1b');MUT=HexColor('#6b6962');LINE=HexColor('#dcd9d0');PANEL=HexColor('#f5f3ee')
R=[r for r in csv.DictReader(open(DB+'/termekek.csv',encoding='utf-8-sig'),delimiter=';') if r['piaccsoport'] in ('Német és osztrák piac','Benelux','Környező országok','Balkán')]
for r in R: r['ar']=float(r['ar_eur'])
SAV=[('1. ársáv','600–1 500 €','#2a78d6'),('2. ársáv','1 500–2 000 €','#6250d6'),('3. ársáv','2 000–2 500 €','#e87ba4'),('4. ársáv','2 500–3 000 €','#eb6834'),('5. ársáv','3 000–3 500 €','#8a5a2b'),('ágy 600 € alatt','franciaágyak 600 € alatt','#1baf7a')]
PIAC=['Német és osztrák piac','Benelux','Környező országok','Balkán']
st=lambda n,**k:ParagraphStyle(n,fontName=k.get('f','S'),fontSize=k.get('s',9),leading=k.get('l',k.get('s',9)*1.3),textColor=k.get('c',INK),spaceAfter=k.get('a',0),spaceBefore=k.get('b',0))
H1=st('h1',f='SR',s=24,l=28,a=4);H2=st('h2',f='SR',s=16,l=20,a=4,b=2);H3=st('h3',f='SB',s=10.5,a=3,b=8);P=st('p',s=9,a=4);M=st('m',s=8,c=MUT,a=4);C=st('c',s=7.4,l=9.2);CB=st('cb',f='SB',s=7.4,l=9.2,c=white)
fmt=lambda x:f"{x:,.0f}".replace(',',' ')
def fmt2(v):
    try: return f"{float(v):,.2f}".replace(',',' ').replace('.',',').replace(',00','')
    except: return ''
def tbl(data,widths,head_col):
    t=Table(data,colWidths=widths,repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor(head_col)),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,1),(-1,-1),0.4,LINE),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,PANEL]),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3),('TOPPADDING',(0,0),(-1,-1),2.5),('BOTTOMPADDING',(0,0),(-1,-1),2.5)]))
    return t
def counts(L,key,split=False,n=5):
    c=Counter()
    for r in L:
        v=r[key]
        if not v: continue
        if split: [c.update([x.strip()]) for x in v.split(';') if x.strip()]
        else: c.update([v])
    return ', '.join(f'{tr(k)} ({v})' for k,v in c.most_common(n)) or '–'
def foot(cv,doc):
    cv.saveState();cv.setFont('S',7);cv.setFillColor(MUT)
    cv.drawString(15*mm,8*mm,T['foot']);cv.drawRightString(doc.pagesize[0]-15*mm,8*mm,T['page'].format(doc.page));cv.restoreState()
out=f'{OUTD}/kimutatas_{DATUM}_nemet-osztrak_benelux_kornyezo_balkan_{LANG}.pdf'
doc=SimpleDocTemplate(out,pagesize=landscape(A4),leftMargin=15*mm,rightMargin=15*mm,topMargin=13*mm,bottomMargin=14*mm,title=T['title'])
W=doc.width;E=[]
E+= [Paragraph(T['h1'],H1),Paragraph(T['sub'].format(len(R),len(set(r['aruhaz'] for r in R))),M),Spacer(1,4)]
E.append(Paragraph(T['intro'],P))
E.append(Paragraph(T['sum'],H2))
d=[[Paragraph(x,CB) for x in T['sumh']]]
for s,rg,col in SAV:
    L=[r for r in R if r['arsav']==s]
    if not L: d.append([Paragraph(x,C) for x in [tr(s),tr(rg),'0','–','–','–','–','–']]);continue
    d.append([Paragraph(f'<b>{tr(s)}</b>',C),Paragraph(tr(rg),C),Paragraph(str(len(L)),C),Paragraph(fmt(sum(r['ar'] for r in L)/len(L))+' €',C),Paragraph(fmt(min(r['ar'] for r in L))+' €',C),Paragraph(fmt(max(r['ar'] for r in L))+' €',C),Paragraph(counts(L,'szovet_csoport',n=3),C),Paragraph(counts(L,'tipus',n=3),C)])
E.append(tbl(d,[W*x for x in (.09,.11,.06,.08,.08,.08,.28,.22)],'#3d3b36'))
E.append(Paragraph(T['stores'],H2))
d=[[Paragraph(x,CB) for x in T['storesh']]]
for a in sorted(set(r['aruhaz'] for r in R),key=lambda a:-sum(1 for r in R if r['aruhaz']==a)):
    L=[r for r in R if r['aruhaz']==a]
    d.append([Paragraph(f'<b>{a}</b>',C),Paragraph(', '.join(sorted(set(r['orszag'] for r in L))),C),Paragraph(str(len(L)),C),Paragraph(fmt(sum(r['ar'] for r in L)/len(L))+' €',C),Paragraph(counts(L,'arsav',n=6),C)])
E.append(tbl(d,[W*x for x in (.18,.08,.07,.09,.58)],'#3d3b36'))
E.append(PageBreak())
for s,rg,col in SAV:
    L=[r for r in R if r['arsav']==s]
    E.append(Paragraph(f'<font color="{col}">■</font> {tr(s)} · {tr(rg)}',H2))
    if not L: E.append(Paragraph(T['emptyband'],M));continue
    E.append(Paragraph(T['bandsub'].format(len(L),fmt(sum(r['ar'] for r in L)/len(L))),M))
    agg=[[Paragraph(x,CB) for x in T['aggh']],[Paragraph(counts(L,'tipus'),C),Paragraph(counts(L,'szovet_csoport'),C),Paragraph(counts(L,'lab',n=4),C),Paragraph(counts(L,'funkciok',split=True,n=6),C)]]
    E.append(tbl(agg,[W*.16,W*.2,W*.3,W*.34],col));E.append(Spacer(1,4))
    E.append(Paragraph(T['strip'],H3))
    fc=Counter(r['szovet_csoport'] for r in L if r['szovet_csoport'])
    cells=[]
    for g,nn in fc.most_common(6):
        ex=[r for r in L if r['szovet_csoport']==g and os.path.exists(f"{TH}/{r['id']}_szovet.jpg")]
        if not ex: ex=[r for r in R if r['szovet_csoport']==g and os.path.exists(f"{TH}/{r['id']}_szovet.jpg")]
        im=sm(ex[0]['id'],'szovet',52) if ex else Paragraph('<font color="#9a978f">'+T['nophoto']+'</font>',C)
        cells.append([im,Paragraph(f'<b>{tr(g)}</b><br/>{nn} '+T['pcs']+(f'<br/><font color="#6b6962">{T["eg"]} {ex[0]["marka"] or ex[0]["aruhaz"]}</font>' if ex else ''),C)])
    def lk(l):
        l=l.lower()
        if not l: return None
        col_='fekete' if 'fekete' in l else 'króm/ezüst' if ('króm' in l or 'ezüst' in l) else 'fa' if ('fa' in l or 'tölgy' in l or 'bükk' in l) else 'egyéb'
        mat='fém' if any(x in l for x in ('fém','vas','alumínium','metall')) else 'műanyag' if 'műanyag' in l else 'fa' if ('fa' in l or 'tölgy' in l or 'bükk' in l) else 'szánkótalp' if 'szánkó' in l else 'nincs megadva'
        if mat=='nincs megadva': return f'{col_} láb' if col_!='egyéb' else 'egyéb láb'
        return f'{mat}, {col_}' if col_ not in ('egyéb',) else mat
    lc=Counter(lk(r['lab']) for r in L if lk(r['lab']))
    lcells=[]
    for g,nn in lc.most_common(5):
        ex=[r for r in R if lk(r['lab'])==g and os.path.exists(f"{TH}/{r['id']}_lab.jpg")]
        im=sm(ex[0]['id'],'lab',52) if ex else Paragraph('<font color="#9a978f">'+T['nolegphoto']+'</font>',C)
        lcells.append([im,Paragraph(f'<b>{tr(g)}</b><br/>{nn} '+T['pcs'],C)])
    def strip(cs,title):
        if not cs: return
        row=[Paragraph(f'<b>{title}</b>',C)]+[Table([[c[0]],[c[1]]],style=[('LEFTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),1)]) for c in cs]
        t=Table([row],colWidths=[W*.1]+[W*.15]*len(cs),hAlign='LEFT');t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),3)]));E.append(t);E.append(Spacer(1,3))
    strip(cells,T['fabrics']);strip(lcells,T['legs'])
    for p in PIAC:
        PL=sorted([r for r in L if r['piaccsoport']==p],key=lambda r:r['ar'])
        E.append(Paragraph(f'{tr(p)} – {len(PL)} '+T['pcs']+(f' · {T["avg"]} {fmt(sum(r["ar"] for r in PL)/len(PL))} €' if PL else ''),H3))
        if not PL: E.append(Paragraph(T['emptygrp'],M));continue
        d=[[Paragraph(x,CB) for x in T['prodh']]]
        for r in PL:
            d.append([pic(r['id'],W*.095-6),Paragraph(f'<b>{r["termek"]}</b>'+(f'<br/><font color="#6b6962">{r["marka"]}</font>' if r['marka'] and r['marka']!=r['aruhaz'] else '')+lnk(r['forras'],int(r['id'])),C),Paragraph(f'{r["aruhaz"]} ({r["orszag"]})',C),Paragraph(tr(r['tipus']),C),Paragraph('<b>'+fmt2(r['ar_eur'])+' €</b>',C),Paragraph((fmt2(r['akcios_ar_eur'])+' €') if r['akcios_ar_eur'] else '–',C),Paragraph((fmt2(r.get('athuzott_ar_eur',''))+' €') if r.get('athuzott_ar_eur') else '–',C),cellimg(r['id'],'szovet',tr(r['szovet']) or '–',34),cellimg(r['id'],'lab',tr(r['lab']) or '<font color="#b07a00">'+T['legmiss']+'</font>',34),Paragraph(', '.join(tr(x.strip()) for x in r['funkciok'].split(';') if x.strip()) or '–',C)])
        E.append(tbl(d,[W*x for x in (.095,.17,.08,.06,.06,.065,.06,.12,.135,.155)],col))
    E.append(PageBreak())
# analyst
n=len(R);lab=sum(1 for r in R if not r['lab']);ert=sum(1 for r in R if not r['ertekelesek'])
th=[r for r in R if r.get('athuzott_ar_eur')];disc=round(sum(1-r['ar']/float(r['athuzott_ar_eur']) for r in th)/len(th)*100)
E.append(Paragraph(T['analyst'],H2))
G={p:[r['ar'] for r in R if r['piaccsoport']==p] for p in PIAC}
CO={c:[r['ar'] for r in R if r['orszag']==c] for c in ('DE','AT','NL','BE','LU','CH','PL','CZ','SK','HU','SI','HR','RS','RO','BG')}
cs=', '.join(f'{c} {fmt(sum(v)/len(v))} €' for c,v in CO.items() if v)
thn=[r for r in R if r.get('athuzott_ar_eur')];discn=round(sum(1-r['ar']/float(r['athuzott_ar_eur']) for r in thn)/len(thn)*100)
eros=sum(1 for r in thn if float(r['athuzott_ar_eur'])>=2*r['ar'])
items=T['items'](n,len(set(r['aruhaz'] for r in R)),[len(G[p]) for p in PIAC],[fmt(sum(G[p])/len(G[p])) for p in PIAC],cs,len(thn),discn,eros)

d=[[Paragraph(x,CB) for x in T['anh']]]+[[Paragraph(f'<b>{a}</b>',C),Paragraph(b,C),Paragraph(c,C)] for a,b,c in items]
E.append(tbl(d,[W*.15,W*.45,W*.4],'#3d3b36'))
E.append(Spacer(1,8));E.append(Paragraph(T['src'],M))
doc.build(E,onFirstPage=foot,onLaterPages=foot)
print(out)
