import csv, json, re, sys
SITE="/home/claude/work/site/ca-mfa-lab"; ME="/home/claude/ca-mfa-lab"
cat=list(csv.DictReader(open(SITE+"/ca-mfa-catalogue-v1.3.csv",encoding="utf-8")))
add=list(csv.DictReader(open(ME+"/catalogue-v1.4-additions.csv",encoding="utf-8")))
chk={"W01":("Confirmed","GitHub Docs OIDC reference: a trust condition must be set; the branch appears in the subject only when no environment is used and the run is not from a pull request."),
     "W05":("Confirmed with a qualifier","SonicWall advisory SNWLID-2026-0014 (6 Nov 2026) as quoted by SecurityWeek and others; CISA KEV. Vendor page itself not opened. SonicWall lists no workaround."),
     "W09":("Confirmed","RFC 9449 (DPoP), September 2023."),
     "W11":("Partly confirmed","MCP authorization specification (2026-07-28 text) on issuer validation. Research notes on the SDK flaw not re-read.")}
for a in add:
    a["run"]="5"
    c,n=chk.get(a["id"],("Not part of this check",""))
    a["source_check"]=c; a["source_note"]=n

UPD={
"M06":("NIST SP 800-63B-4, Appendix B (syncable authenticators); FIDO Alliance (not read)","Confirmed, with a qualifier","Read Appendix B on 14 Nov 2026 through a page fetch summary. It does not directly cover losing one device. Its Table 5 says synced keys are reachable through cloud account recovery and tells implementers to bind multiple authenticators at AAL2 and above to support recovery, to notify the user of recovery activity, and to require AAL2 to add authenticators. Syncable authenticators cannot be used at AAL3. The loss-of-one-device behaviour in this case is my model, not NIST text."),
"Z20":("T-Minus 365; Cloud Capsule; Exchange Team blog, 27 Jan 2026 (updated 29 Jan)","Confirmed","Exchange Team post: SMTP AUTH Basic authentication is unchanged until December 2026. At the end of December 2026 it is disabled by default for existing tenants (admins can turn it back on) and unavailable by default for new tenants. A final removal date is to be announced in the second half of 2027. The March to April 2026 dates were put on hold. Dates have moved before, so check Microsoft's page before acting. Read through a page fetch summary."),
"Y06":("NetSPI, nested app authentication bypass; TROOPERS 2026 talk abstract","Confirmed, with a qualifier","NetSPI reports it told Microsoft on 17 March 2026, Microsoft rated it medium and deployed a fix, and a retest returned Conditional Access blocking errors for the flows it found. Read in NetSPI excerpts and a news write-up, not the full post. Other researchers presented further nested app paths at TROOPERS 2026, so the fix covers the named flows, not every path. I have not read Microsoft's own statement."),
"Y10":("RSA, how attackers bypass MFA (excerpt); Duo documentation and blog","Confirmed, with a qualifier","Duo's Windows Logon installers default to fail closed from version 4.3.0 and defaulted to fail open before. Duo's FAQ says Duo Legacy AD Protection fails open by default. A Duo blog describes a real case where an authentication proxy was configured to fail open. The row describes a deployment set to fail open, not a current product default."),
"W05":("SonicWall advisory SNWLID-2026-0014, revision 1.1 (vendor page); CISA KEV entry; SecurityWeek","Confirmed","Read on SonicWall's own page on 14 Nov 2026 (revision 1.1, last updated 9 Nov). The description, the SAML-only NOTE, the affected builds (7.3.3-7015 and older, 8.2.2-8015 and older), the fixed builds (7.3.4-7013 and 8.2.3-8015) and the CISA KEV listing agree with the earlier write-ups. The page says SonicWall investigated a report indicating potential exploitation. Correction: my earlier notes said there is no workaround. Revision 1.1 (9 Nov) added one: if SAML is in use and an upgrade is not possible, disable or delete the active LDAP, RADIUS and TACACS+ servers. That matches control A in the model. The revision table dates version 1.0 as 5 Nov, while the header says first published 6 Nov."),
"W11":("GitHub advisory GHSA-qx49-fqc8-xw99 as read in the CSA research note (30 Sep 2026), The Hacker News and WorkOS; MCP authorization specification","Confirmed, with a qualifier","MCP Python SDK advisory (28 Sep 2026, CVSS 7.5): a malicious MCP server could make the client send its client secret, authorization code and PKCE verifier to an endpoint the server chose, because the SDK did not check the issuer on a fallback discovery path. Affected 1.9.1 to 1.29.1 and 2.0.0 to 2.1.1; fixed in 1.30.0 and 2.2.0. I did not open the GitHub advisory itself. The Hacker News reports no attacks. MCP authorization specification (2026-07-28 text) on issuer validation read earlier."),
}
for r in cat+add:
    u=UPD.get(r["id"])
    if u: r["source"],r["source_check"],r["source_note"]=u
G=("Confirmed","GitHub Docs OIDC reference, read live on 14 Nov 2026 through a page fetch summary: the immutable subject format adds owner and repository IDs; repositories created after 15 July 2026 use it by default, older ones can opt in, and renames and transfers after that date also move to it. Not available on GitHub Enterprise Server. A trust condition must be set; the branch appears in the subject only when no environment is used and the run is not from a pull request.")
for r in add:
    if r["id"]=="W01": r["source_check"],r["source_note"]=G
FIELDS=["id","run","group","use_case","kind","source","status","source_check","source_note"]
add6=list(csv.DictReader(open(ME+"/catalogue-v1.7-additions.csv",encoding="utf-8")))
for r in cat:
    if r["id"] in ("E01","E02","E03"): r["run"]="4"
allrows=cat+add+add6
with open(ME+"/ca-mfa-catalogue-v1.7.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); [w.writerow({k:r.get(k,"") for k in FIELDS}) for r in allrows]
res={}; 
r1=json.load(open(SITE+"/evidence/results-run1.json"))["rows"]
for x in r1: res[x["id"]]={"cols":["No control","Control on","Control off alone"],"res":x["result"],"guess":x["guess"],"match":x["match"],"limres":x.get("limit_result"),"limdiff":bool(x.get("limit_diff"))}
r2=json.load(open(SITE+"/evidence/results-run2.json"))
r3=json.load(open(SITE+"/evidence/results-run3.json"))
r5=json.load(open(ME+"/evidence/results-run5.json"))["rows"]
r6=json.load(open(ME+"/evidence/results-run6.json"))["rows"]
C5=["None on","All on","Off A","Off B","Off C"]
for run,rows in ((2,r2),(3,r3),(5,r5),(6,r6)):
    for x in rows:
        pair=None
        if x.get("pair_off"): pair={"off":x["pair_off"],"result":x["pair_result"],"guess":x["pair_guess"]}
        ok=(not x["diffs"]) and (pair is None or pair["result"]==pair["guess"])
        res[x["id"]]={"cols":C5,"res":x["result"],"guess":x["guess"],"match":ok,"diffs":x["diffs"],"controls":x["controls"],**({"assumes":x["assumes"]} if x.get("assumes") else {}),**({"pair":pair} if pair else {})}
def parse(path,pat):
    d={}
    for line in open(path,encoding="utf-8"):
        m=re.match(pat,line.rstrip("\n"))
        if not m: continue
        f=[x.strip() for x in m.group(2).split(" | ")]
        d[m.group(1)]=f
    return d
g1=parse(SITE+"/evidence/guesses/guesses-run1.md",r"^([A-Z]\d{2}) \| (.*)$")
g2=parse(SITE+"/evidence/guesses/guesses-run2.md",r"^([A-Z]\d{2}) \| (.*)$")
g3=parse(SITE+"/evidence/guesses/guesses-run3.md",r"^([A-Z]\d{2}) \| (.*)$")
g5=parse(SITE+"/evidence/guesses/guesses-run5.md",r"^(W\d{2}) \| (.*)$")
g6=parse(ME+"/guesses-run6.md",r"^(G\d{2}) \| (.*)$")
for cid,f in g1.items():
    if cid in res: res[cid]["g1"]={"none":f[0],"with":f[1],"off":f[2],"limit":f[3] if len(f)>3 else ""}
for g in (g2,g3,g5,g6):
    for cid,f in g.items():
        if cid in res:
            res[cid]["ctl"]=f[0]; res[cid]["bad"]=f[1]
            m=re.search(r"\((.*)\)\s*$",f[-1]); res[cid]["note"]=m.group(1) if m else ""
sys.path.insert(0,"/home/claude/work/fw"); import stages as _st
STAGE_OF={c:k for k,_n,_q,_c,ids in _st.STAGES for c in ids.split()}
out=[]
for r in allrows:
    cid=r["id"]; d={"id":cid,"run":int(r["run"]),"group":r["group"],"use":r["use_case"],"kind":r["kind"],"src":r["source"],"status":r["status"],"check":r["source_check"],"snote":r["source_note"]}
    d.update(res.get(cid,{})); d["stage"]=STAGE_OF[cid]
    out.append(d)
tally={"1":[41,41],"2":[45,39],"3":[16,16],"5":[12,12],"6":[10,10]}
sens=json.load(open(ME+"/evidence/results-run5.json"))["sensitivity"]+json.load(open(ME+"/evidence/results-run6.json"))["sensitivity"]
js="/* Generated from the lab's own result files. Not hand edited. */\nwindow.CA_CASES="+json.dumps(out,ensure_ascii=False,separators=(",",":"))+";\nwindow.CA_STAGES="+json.dumps([{"id":k,"name":n,"q":q,"controls":c} for k,n,q,c,_ in _st.STAGES],ensure_ascii=False)+";\nwindow.CA_TALLY="+json.dumps(tally)+";\nwindow.CA_SENS="+json.dumps(sens,ensure_ascii=False,separators=(",",":"))+";\n"
open("/home/claude/work/out/ca-mfa-lab/data/cases.js","w",encoding="utf-8").write(js)
print(len(out),"cases;", sum(1 for o in out if "res" in o),"with results;", len(js),"bytes")
print([o["id"] for o in out if "res" not in o])
print(sorted({o["group"] for o in out}))
