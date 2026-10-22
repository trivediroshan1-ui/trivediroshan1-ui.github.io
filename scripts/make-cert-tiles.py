import re,html
p='resume/index.html'
s=open(p).read()
hues={'SailPoint':(262,'IDENTITY'),'CyberArk':(200,'PAM'),'BeyondTrust':(22,'PAM'),'Identity Management Institute':(36,'IAM'),'AWS':(222,'CLOUD')}
def slug(t): return re.sub(r'[^a-z0-9]+','-',t.lower()).strip('-')[:40]
def wrap(t,n=26):
    w=t.split();L=[];c=''
    for x in w:
        if len(c+' '+x)>n and c: L.append(c);c=x
        else: c=(c+' '+x).strip()
    L.append(c);return L[:3]
def tile(issuer,title,dates,exp):
    label={'Identity Management Institute':'IMI'}.get(issuer,issuer)
    h=next(v[0] for k,v in hues.items() if issuer.startswith(k))
    sat=8 if exp else 55
    bg1=f'hsl({h},{sat}%,{20 if exp else 24}%)';bg2=f'hsl({h+30},{sat}%,{12 if exp else 14}%)'
    acc=f'hsl({h},{sat+10 if not exp else 6}%,{78 if not exp else 66}%)'
    L=wrap(title);y0=60 if len(L)>2 else 74
    t=''.join(f'<text x="20" y="{y0+i*20}" font-size="16" font-weight="700" fill="#fff">{html.escape(l)}</text>' for i,l in enumerate(L))
    mark='EXPIRED' if exp else 'ACTIVE'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 150" role="img" aria-label="{html.escape(issuer)}: {html.escape(title)}, {html.escape(dates)}" font-family="system-ui,-apple-system,Segoe UI,Roboto,sans-serif"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/></linearGradient></defs><rect width="280" height="150" rx="14" fill="url(#g)"/><rect x="8" y="8" width="264" height="134" rx="9" fill="none" stroke="{acc}" stroke-opacity=".45" stroke-dasharray="3 4"/><text x="20" y="36" font-size="11" letter-spacing="2" font-weight="700" fill="{acc}">{html.escape(label.upper())}</text>{t}<text x="20" y="134" font-size="11" fill="{acc}">{html.escape(dates)}</text><text x="260" y="134" font-size="10" letter-spacing="1.5" font-weight="700" text-anchor="end" fill="{acc}">{mark}</text></svg>'''
def fix(m):
    li=m.group(0)
    b=re.search(r'<b>(.*?)</b>',li).group(1);sm=re.search(r'<small>(.*?)</small>',li).group(1)
    iss,dates=[x.strip() for x in re.split(r'&middot;',sm)]
    dates=dates.replace('&ndash;','to').replace('&amp;','&')
    exp='is-expired' in li
    title=html.unescape(b)
    f=f'assets/certs/{slug(iss)}-{slug(title)}.svg'
    open(f,'w').write(tile(html.unescape(iss),title,html.unescape(dates),exp))
    li=re.sub(r'<span class="cred-i".*?</span>',f'<img class="cred-img" src="/{f}" alt="" width="280" height="150" loading="lazy">',li,count=1,flags=re.S)
    return li
s=re.sub(r'<li class="cred[^"]*">.*?</li>',fix,s,flags=re.S)
open(p,'w').write(s)
