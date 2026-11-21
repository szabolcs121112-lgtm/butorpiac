import re,json,sys
FX={'RON':5.3482,'RSD':117.62,'BAM':1.95583,'BGN':1.95583,'EUR':1,'CHF':0.9223,'PLN':4.4583,'CZK':24.469,'HUF':373.55}
CUR=[('lei','RON'),('RSD','RSD'),('KM','BAM'),('лв','BGN'),('Kč','CZK'),('Ft','HUF'),('zł','PLN'),('CHF','CHF'),('€','EUR')]
def num(s):
    s=s.replace('‒','').replace('‒','').replace('–','').replace(' ','').replace('\xa0','').replace("'",'').replace('’','')
    s=re.sub(r'[,.]-$','',s)
    if re.search(r',\d\d$',s): s=s[:-3].replace('.','').replace(',','')+'.'+s[-2:]
    elif re.search(r'\.\d\d$',s) and s.count('.')==1: pass
    else: s=s.replace('.','').replace(',','')
    return float(s)
def prices(t,cc):
    sym=[k for k,v in CUR if v==cc][0]
    if cc=='CHF':
        ps=re.findall(r"CHF\s?(\d[\d'’]*(?:\.\d\d|\.-)?)",t)
    else:
        ps=re.findall(r'(\d+(?:[ \xa0.]\d{3})*(?:,\d\d|,[‒‒–-])?)\s?'+re.escape(sym),t)
    return [num(p) for p in ps if p.strip()]
def typ(s):
    s=s.lower()
    if re.search(r'sarok|rohov|narożn|narozn|ecksofa|wohnlandschaft|u-alak|kotn|kutn|ugaon|colț|colţ|ъглов|obliki črke u|oblik u|u-oblik|formă de u',s) and not re.search(r'sessel|fotel ',s[:12]): return 'Sarokülő'
    if re.search(r'fotel|křeslo|kreslo|sessel|fauteuil|naslonjač|фотьойл',s): return 'Fotel'
    if re.search(r'ágy|postel|posteľ|lóżko|łóżko|bett|boxspring|lit |krevet|pat |легл|spalnic',s) and not re.search(r'ágyazható|rozkládací|rozkladacia|schlaf|rozkładan|bettsofa|eckbett',s): return 'Franciaágy'
    if re.search(r'sarok|rohov|narożn|eck|wohnlandschaft|u-alak|u sedac',s): return 'Sarokülő'
    if re.search(r'souprava|súprava|garnit|komplet|zestaw|sedežna',s): return 'Garnitúra'
    return 'Kanapé'
def band(e,t):
    if e>3500: return None
    if e<600: return 'ágy 600 € alatt' if t=='Franciaágy' else None
    for a,b in [(600,1500),(1500,2000),(2000,2500),(2500,3000),(3000,3500)]:
        if e<b or b==3500: return f'{a}–{b} €'
