/* Privileged access lab page: map animation, workflows, results. No inline script, to fit the site CSP. */
new MutationObserver(()=>{for(const c of document.querySelectorAll('.stack td:not([data-l])')){let i=0,p=c;while(p=p.previousElementSibling)i+=p.colSpan;c.dataset.l=c.closest('table').rows[0].cells[i]?.textContent||''}}).observe(document,{childList:true,subtree:true})
{
const C={red:'var(--red)',blue:'var(--blue)',amber:'var(--amber)',green:'var(--green)',ink:'var(--ink)',mute:'var(--mute)'};
const N={
admins:[24,96,150,'Admins','people'],devs:[24,166,150,'Developers','people'],vendors:[24,236,150,'Vendors','third parties'],workloads:[24,306,150,'Service accounts','workloads, RPA'],agents:[24,376,150,'AI agents','and MCP tools'],bg:[24,520,150,'Break-glass','sealed, offline'],
idp:[214,96,160,'Identity provider','SSO, agent IDs'],mfa:[214,166,160,'Phishing-resistant','passkey, smart card'],posture:[214,236,160,'Device and network','posture, ZTNA'],wid:[214,306,160,'Workload identity','OIDC, SPIFFE'],agentid:[214,376,160,'Agent registry','owner, scope, expiry'],drv:[214,520,160,'Vault HA and DR','tested failover'],
pdp:[414,96,170,'Policy decision','eligibility, tier'],itsm:[414,166,170,'ITSM ticket check','system matches?'],approve:[414,236,170,'Approver','person; AI only advises'],iga:[414,306,170,'Governance and SoD','who may hold it'],risk:[414,376,170,'Risk signals','ITDR, UEBA'],
vault:[630,96,178,'Vault and rotation','PASM'],jit:[630,158,178,'Just-in-time grant','ephemeral, time-boxed'],session:[630,220,178,'Session broker','isolate, record, block'],remote:[630,282,178,'Remote access broker','no VPN'],pedm:[630,344,178,'Endpoint privilege','elevate the app'],secrets:[630,406,178,'Secrets manager','pipelines, apps'],gateway:[630,468,178,'Agent gateway','checks each call'],pki:[630,530,178,'PKI, HSM, keys','signing, certificates'],
win:[852,96,158,'Windows and AD'],linux:[852,158,158,'Linux and Unix'],db:[852,220,158,'Databases'],cloud:[852,282,158,'AWS, Azure, GCP'],k8s:[852,344,158,'Kubernetes, CI/CD'],saas:[852,406,158,'SaaS admin'],social:[852,468,158,'Social accounts'],
sap:[1026,96,158,'SAP'],jde:[1026,158,158,'JD Edwards'],ibmi:[1026,220,158,'IBM i (AS/400)'],zos:[1026,282,158,'Mainframe z/OS'],net:[1026,344,158,'Network devices'],ot:[1026,406,158,'OT and ICS'],ep:[1026,468,158,'Endpoints'],
siem:[852,650,158,'SIEM'],soar:[1026,650,158,'SOAR'],itdr:[630,650,178,'ITDR and UEBA'],store:[414,650,170,'Evidence store'],grc:[214,650,160,'GRC and reviews']};
const H=n=>n[4]?46:40;
const F=[
{id:'human',name:'Human admin',c:C.red,nodes:['admins','idp','mfa','pdp','itsm','approve','jit','session','win','siem'],steps:['Asks for a role for a task, with a ticket','Signs in through the IdP','Proves it with a passkey or smart card, not SMS','Policy checks eligibility and tier','The ticket must name the same system','A person approves Tier 0; Tier 1 rules can auto-approve','A time-boxed grant, no standing role','The session is isolated and recorded','Change made on the domain controller','Grant, session and removal land in the SIEM'],why:'Lab: round 1 cases 01 to 05, 08, 11.'},
{id:'vendor',name:'Vendor',c:C.green,nodes:['vendors','idp','mfa','posture','pdp','itsm','remote','session','ot','siem'],steps:['A vendor engineer needs the plant','Signs in as a named person, not a shared login','Phishing-resistant MFA','Device and network posture checked','Policy: vendor, one target, 2 hours','The work order must be approved','Remote access broker, no VPN account','Session recorded; dangerous commands blocked','Reaches the OT boundary, read-only by default','Everything logged'],why:'Lab: round 3 cases 04 and 08.'},
{id:'workload',name:'Workload',c:C.blue,nodes:['workloads','wid','pdp','secrets','k8s','siem'],steps:['A pipeline or service needs a credential','Proves itself with workload identity, not a stored key','Policy: this workload, this target, this scope','Secrets manager issues a short-lived credential','Deploys to the cluster','Issue and use are logged'],why:'Lab: round 3 cases 06 and 07; the NHI lab.'},
{id:'agent',name:'AI agent',c:C.amber,nodes:['agents','agentid','pdp','approve','gateway','jit','cloud','siem'],steps:['An agent plans a task that needs admin','Registered: owner, scope, expiry','Policy checks the plan, not just the agent','A person approves the plan; the AI approver only recommends','The gateway checks every call against the plan','A per-task token, narrower for each sub-agent','Acts on the cloud account','Every call is tied to the agent and the person it acts for'],why:'Lab: round 1 cases 07, 12, 16; round 3 case 05.'},
{id:'erp',name:'ERP firefighter',c:C.ink,nodes:['admins','idp','mfa','pdp','iga','approve','jit','session','sap','siem'],steps:['A production issue needs emergency rights in SAP','Signs in through the IdP','Phishing-resistant MFA','Policy: firefighter ID, reason required','Governance checks segregation of duties','The business owner approves','Firefighter ID for hours, not days','Session recorded','Fix made in SAP','The owner reviews the log afterwards'],why:'Applies equally to JD Edwards, IBM i and mainframe firecall IDs.'},
{id:'bg',name:'Break-glass',c:C.mute,dash:true,nodes:['admins','bg','win','siem'],steps:['The IdP or vault is down','Two people open the sealed account','Used on the system that needs it','The alert fires the moment it is used; the password is changed after'],why:'Break-glass never depends on the IdP, vault or MFA it exists to bypass. Lab: round 1 case 06.'}];

const svg=document.getElementById('arch');
const ns='http://www.w3.org/2000/svg';
const el=(t,a,p)=>{const e=document.createElementNS(ns,t);for(const k in a)e.setAttribute(k,a[k]);(p||svg).appendChild(e);return e};
const box=id=>{const n=N[id];return{x:n[0],y:n[1],w:n[2],h:H(n),cx:n[0]+n[2]/2,cy:n[1]+H(n)/2}};
function seg(a,b){const A=box(a),B=box(b);
 if(Math.abs(A.x-B.x)<5){ if(B.y>A.y+H(N[a])+30){const x=A.x-10;return `M${A.x},${A.cy} C${x-20},${A.cy} ${x-20},${B.cy} ${B.x},${B.cy}`} return B.y>A.y?`M${A.cx},${A.y+A.h} L${B.cx},${B.y}`:`M${A.cx},${A.y} L${B.cx},${B.y+B.h}`}
 if(B.y>A.y+A.h+60&&Math.abs(A.cx-B.cx)<200){return `M${A.cx},${A.y+A.h} C${A.cx},${A.y+A.h+60} ${B.cx},${B.y-60} ${B.cx},${B.y}`}
 if(B.x>A.x){const m=(A.x+A.w+B.x)/2;return `M${A.x+A.w},${A.cy} C${m},${A.cy} ${m},${B.cy} ${B.x},${B.cy}`}
 const m=(A.x+B.x+B.w)/2;return `M${A.x},${A.cy} C${m},${A.cy} ${m},${B.cy} ${B.x+B.w},${B.cy}`}
const route=f=>f.nodes.slice(1).map((n,i)=>seg(f.nodes[i],n)).join(' ');

el('rect',{x:616,y:52,width:206,height:530,rx:14,style:'fill:var(--t0)'});
el('rect',{x:200,y:636,width:986,height:68,rx:12,style:'fill:var(--line)',opacity:.5});
[['Who asks',24],['Prove who',214],['Decide',414],['Tier 0: privilege services',630],['The estate',852]].forEach(([t,x])=>{const e=el('text',{x,y:40,style:'fill:var(--ink);font-weight:800;font-size:15px'});e.textContent=t});
const er=el('text',{x:24,y:676,style:'fill:var(--ink);font-weight:800;font-size:15px'});er.textContent='Evidence rail';
const er2=el('text',{x:24,y:694,style:'fill:var(--mute);font-size:12px'});er2.textContent='every line ends here';
const gLines=el('g',{}),gNodes=el('g',{});
const paths={};
F.forEach(f=>{paths[f.id]=el('path',{d:route(f),fill:'none',class:'ln idle',style:`stroke:${f.c}`,'stroke-width':4,'stroke-linecap':'round',opacity:.18},gLines);
 let acc=0;f.cum=[0];f.nodes.slice(1).forEach((n,i)=>{const t=el('path',{d:seg(f.nodes[i],n),fill:'none'});acc+=t.getTotalLength();t.remove();f.cum.push(acc)})});
const nodeEls={};
for(const id in N){const n=N[id],b=box(id);const g=el('g',{},gNodes);
 const r=el('rect',{x:b.x,y:b.y,width:b.w,height:b.h,rx:10,style:'fill:var(--node);stroke:var(--line)','stroke-width':2},g);
 const t=el('text',{x:b.x+12,y:n[4]?b.y+20:b.cy+5,style:'fill:var(--ink);font-weight:700;font-size:13.5px'},g);t.textContent=n[3];
 if(n[4]){const s=el('text',{x:b.x+12,y:b.y+36,style:'fill:var(--mute);font-size:12px'},g);s.textContent=n[4]}
 nodeEls[id]=r}
const tok=el('circle',{r:9,style:'fill:var(--ink);stroke:var(--bg)','stroke-width':3,opacity:0});
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
let cur=null,raf=0,t0=0,auto=!reduce,cycle=0;
const btns=document.getElementById('lineBtns'),story=document.getElementById('story');
btns.innerHTML=F.map(f=>`<button type="button" data-f="${f.id}" aria-pressed="false"><span class="sw" style="background:${f.c}${f.dash?';opacity:.6':''}"></span>${f.name}</button>`).join('');
function show(id,user){if(user)auto=false;const f=F.find(x=>x.id===id);cur=f;
 F.forEach(x=>{const P=paths[x.id],sel=x.id===id;P.setAttribute('opacity',sel?1:.2);P.setAttribute('stroke-width',sel?6:4);P.classList.toggle('idle',!sel&&!reduce);P.style.transition='none';P.style.strokeDasharray='';P.style.strokeDashoffset=''});
 const P=paths[id];
 if(f.dash){P.style.strokeDasharray='10 8'}else if(!reduce){const L=P.getTotalLength();P.style.strokeDasharray=L;P.style.strokeDashoffset=L;P.getBoundingClientRect();P.style.transition='stroke-dashoffset 1s ease-out';P.style.strokeDashoffset=0}
 for(const k in nodeEls){const on=f.nodes.includes(k);nodeEls[k].style.stroke=on?f.c:'var(--line)';nodeEls[k].style.fill='var(--node)';nodeEls[k].setAttribute('stroke-width',on?3:2)}
 if(reduce)f.nodes.forEach(k=>nodeEls[k].style.fill=`color-mix(in srgb, ${f.c} 20%, var(--node))`);
 btns.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.f===id));
 story.style.borderColor=f.c;
 story.innerHTML=`<h3>${f.name} line</h3><ol>${f.steps.map((s,i)=>`<li><b>${N[f.nodes[i]][3]}.</b> ${s}</li>`).join('')}</ol><p class="why">${f.why}</p>`;
 tok.style.fill=f.c;cancelAnimationFrame(raf);
 if(reduce){tok.setAttribute('opacity',0);return}
 t0=performance.now()+900;tok.setAttribute('opacity',1);raf=requestAnimationFrame(step)}
function step(now){const p=paths[cur.id],L=p.getTotalLength(),dur=Math.max(4500,L*5.5);const k=Math.max(0,(now-t0)/dur);
 const d=Math.min(k,1)*L;cur.nodes.forEach((n,i)=>{nodeEls[n].style.fill=d>=cur.cum[i]-2?`color-mix(in srgb, ${cur.c} 22%, var(--node))`:'var(--node)'});
 if(k>=1.3){if(auto){cycle=(cycle+1)%F.length;show(F[cycle].id);return}t0=now+300}
 const pt=p.getPointAtLength(Math.min(k,1)*L);tok.setAttribute('cx',pt.x);tok.setAttribute('cy',pt.y);raf=requestAnimationFrame(step)}
btns.addEventListener('click',e=>{const b=e.target.closest('button');if(b){cycle=F.findIndex(x=>x.id===b.dataset.f);show(b.dataset.f,true)}});
show('human');

const E=[
['Windows and Active Directory','Domain and Enterprise Admins, krbtgt, local Administrator, service accounts with SPNs','RDP through the session broker, from a Tier 0 admin workstation','Rotated after each checkout; a unique local admin password per machine','A Tier 0 account signing in to a Tier 2 machine; krbtgt rolls forward only, twice'],
['Linux and Unix','root, sudo groups, SSH keys','SSH through the broker; sudo rules from central policy','Vaulted passwords and keys; short-lived SSH certificates where possible','authorized_keys files nobody manages; keys copied between hosts'],
['Databases','sys, sa, postgres, DBA roles, schema owners','Native client through a broker or proxy, with query logging','DBA passwords rotated; application connection strings from the secrets manager','Application accounts shared by people; DBA reads of production data with no ticket'],
['AWS, Azure, GCP','Root, global and organisation admins, owner roles','Federated roles from the IdP, activated just in time','Root sealed behind a hardware key; no long-lived access keys','Standing owner roles; keys in code; hidden paths to admin that CIEM finds'],
['Kubernetes and CI/CD','cluster-admin, service account tokens, deploy identities','kubectl through an access proxy with JIT; pipelines sign in with OIDC','No static cloud keys in pipelines; short tokens','Privileged pods, readable tokens, side branches that can sign (round 3 cases 06, 07)'],
['SaaS admin','M365, Salesforce, Workday, ServiceNow tenant admins, integration users','SSO with phishing-resistant MFA; JIT where the SaaS supports it','Integration secrets vaulted; OAuth app consent reviewed','Admins exempt from conditional access; OAuth tokens with no owner'],
['SAP','SAP*, DDIC, firefighter IDs, users with SAP_ALL, RFC users','Emergency (firefighter) access with a reason and an owner review of the log','SAP* and DDIC locked until needed; RFC passwords vaulted','SAP_ALL left on dialog users; firefighter logs nobody reads'],
['JD Edwards','System and database owner accounts, broad security overrides','Client or web through the broker; role changes through governance','System and database passwords vaulted and rotated','Security changes outside change control; segregation of duties between roles'],
['IBM i (AS/400)','QSECOFR, profiles with *ALLOBJ or *SECADM','5250 sessions through the broker; elevation per task','QSECOFR held in the vault; profile swaps logged','Many profiles with *ALLOBJ; programs that adopt authority'],
['Mainframe z/OS','RACF SPECIAL and OPERATIONS, UID 0 in UNIX System Services','3270 sessions through the broker; firecall IDs for emergencies','Firecall passwords vaulted, used once, then changed','SPECIAL spread widely; firecall IDs never revoked'],
['Network devices','enable and privilege 15, local admin, SNMP','TACACS+ or RADIUS backed by the IdP; SSH through the broker','Local fallback accounts vaulted; SNMPv3 only','One shared local admin on hundreds of devices; config backups holding secrets'],
['OT and ICS','Engineering workstation admins, PLC and HMI accounts, vendor accounts','Through an IT/OT boundary broker; read-only by default; writes need a second person on site','Site-local vault or sealed envelope; vendor accounts off by default','A broker that depends on the corporate IdP (round 3 case 08); OT owners decide, safety first'],
['Endpoints','Local admin rights, developers who need installs','The endpoint privilege manager elevates the app, not the user','Local admin removed; unique local passwords rotated','Blanket exceptions for whole teams'],
['Social and brand accounts','Company pages, ad accounts, shared logins','Named users with page roles where the platform allows; shared logins only through a vaulted, recorded browser session','Passwords and recovery codes vaulted; MFA on every owner','Ex-staff still page admins; agency logins; recovery phone tied to one person'],
['Machine identities','Service accounts, API keys, certificates, bots','Workload identity first; the vault for what can\'t move','An owner, an expiry and a rotation date on every record','No owner; keys older than the people who made them'],
['AI agents','Agents with tool access, MCP servers','Agent registry, then a per-task token, then a gateway that checks each call','No shared keys; tokens die at the end of the task','Sub-agents inheriting the parent\'s admin (round 3 case 05); injected instructions (round 1 case 07)']];
const G=[['Core infrastructure','k-red'],['Cloud and DevOps','k-blue'],['Business apps and legacy','k-amber'],['Edge and plant','k-green'],['Brand','k-violet'],['Machines and AI','k-ink']];
const GI=[0,0,0,1,1,1,2,2,2,2,3,3,3,4,5,5];
document.querySelector('#estateT tbody').innerHTML=E.map((r,i)=>`<tr>${r.map((c,j)=>`<td>${j?c:`<span class="gchip ${G[GI[i]][1]}">${G[GI[i]][0]}</span><br>${c}`}</td>`).join('')}</tr>`).join('');

const M=[['Device-bound passkey or security key',100,'var(--green)','Phishing-resistant. Can meet AAL3 when the key cannot leave the device.'],['Smart card (PIV, CAC)',100,'var(--green)','Phishing-resistant PKI. CISA calls FIDO and PKI the gold standard.'],['Synced passkey',85,'var(--green)','Phishing-resistant, but the key is copied between devices, so it does not meet AAL3.'],['Push with number matching',50,'var(--amber)','An interim step in CISA guidance. Still open to fatigue and real-time relay.'],['Authenticator app code (TOTP)',38,'var(--amber)','A fake sign-in page can pass the code on within its 30 seconds.'],['SMS or voice code',14,'var(--red)','Marked restricted in NIST SP 800-63B-4: SIM swap, interception and relay.']];
const mt=document.getElementById('meter');
mt.innerHTML=M.map(m=>`<span class="lbl">${m[0]}</span><span class="bar" style="--w:${m[1]}%;--k:${m[2]}"><i></i></span><span class="note">${m[3]}</span>`).join('');
requestAnimationFrame(()=>requestAnimationFrame(()=>mt.classList.add('go')));

const CF=[['ISO/IEC 27001:2022, Annex A 8.2','Allocate and manage privileged access rights, restricted and reviewed','Decide column, just-in-time grant, reviews'],['ISO/IEC 27001:2022, Annex A 5.18','Grant, review and remove access rights','Governance and SoD; movers and leavers (round 3 cases 02, 03)'],['NIST SP 800-53 Rev. 5, AC-2 and AC-6','Account management; least privilege, including privileged accounts','Policy decision, JIT, standing admin count'],['NIST SP 800-53 Rev. 5, AU-2 and AU-12','Decide what to log and generate the records','Evidence rail: SIEM, evidence store'],['NIST SP 800-207 (zero trust)','A policy decision point decides each request; enforcement points carry it out','Decide column is the PDP; session broker and agent gateway are PEPs'],['NIST SP 800-63B-4','Authenticator strength; phishing-resistant options','Prove who: passkeys and smart cards for admins'],['PCI DSS v4.0.1, Requirements 7, 8 and 10','Need to know; identify and authenticate with MFA; log and monitor','Decide, Prove who, Evidence rail'],['CIS Controls v8, Controls 5 and 6','Account management; access control management, MFA for admin access','Discovery, vault, MFA'],['SOC 2, CC6.1 to CC6.3','Logical access, provisioning and removal','Governance, JIT, removal at the end of the window']];
document.querySelector('#compT tbody').innerHTML=CF.map(r=>`<tr>${r.map(c=>`<td>${c}</td>`).join('')}</tr>`).join('');

const GL=[['PAM','Privileged access management: the whole practice of controlling admin power','var(--red)'],['PASM','Vaulting admin passwords and running their sessions through a broker','var(--red)'],['PEDM','Elevating one app or command on a machine instead of making the user an admin','var(--blue)'],['PUM','Privileged user management: which people hold admin accounts and what they may do with them; on Unix often delegated sudo rules','var(--blue)'],['JIT','Just in time: the right is granted for a task and removed when it ends','var(--amber)'],['ZSP','Zero standing privilege: nobody holds admin rights between tasks','var(--amber)'],['Ephemeral access','A credential created for one session and destroyed after it; nothing left to steal','var(--amber)'],['Remote PAM','Brokered, recorded access for remote staff and vendors, without a VPN account','var(--green)'],['CIEM','Finding and trimming excess permissions in cloud accounts','var(--green)'],['ITDR','Spotting attacks on the identity layer itself: odd resets, new admins, token theft','var(--violet,#7c3aed)'],['NHI','Non-human identities: service accounts, keys, certificates, workloads, AI agents','var(--violet,#7c3aed)'],['Tier 0','Anything that can change identity or the PAM layer itself','var(--ink)'],['Break-glass','A sealed account for when the IdP or vault is down, never dependent on them','var(--ink)'],['Zero trust','No request is trusted for where it comes from; each one is decided and enforced (NIST SP 800-207)','var(--blue)'],['AAL','Authenticator assurance level in NIST SP 800-63B: AAL3 needs a phishing-resistant key that can\'t be copied','var(--green)']];
document.getElementById('gloss').innerHTML=GL.map(g=>`<div style="--k:${g[2]}"><b>${g[0]}</b>${g[1]}</div>`).join('');

if(!reduce){document.querySelectorAll('.big[data-n]').forEach(b=>{const n=+b.dataset.n,f=b.dataset.f,t1=performance.now();const fmt=v=>f.replace('#',Math.round(v).toLocaleString('en-US'));const tick=now=>{const k=Math.min(1,(now-t1)/1400),e=1-(1-k)**3;b.textContent=fmt(n*e);if(k<1)requestAnimationFrame(tick)};requestAnimationFrame(tick)})}

const X='<span class="na">Not on pages read</span>';
const V=[
['Discovery of accounts and identities','Account discovery; Secure AI Agents scans for agents','Identity Security Insights; Password Safe discovery','Continuous Identity Discovery',X],
['Vault and rotation (PASM)','Privilege Cloud or PAM Self-Hosted: Vault, rotation (CPM)','Password Safe','Secret Server; Credential Manager','Injects credentials at the gateway; works alongside a vault'],
['Session isolation and recording','Privileged Session Manager, for RDP and SSH','Password Safe sessions; Privileged Remote Access','Secret Server sessions; Connection Manager; platform session recording','Proxy sessions with recording'],
['Just-in-time and zero standing privilege','Secure Infrastructure Access; Secure Cloud Access','Entitle','Delinea Platform JIT; StrongDM runtime authorization','Just-in-time access requests'],
['Endpoint privilege (PEDM)','Endpoint Privilege Manager','Endpoint Privilege Management for Windows and Mac, and for Linux','Privilege Manager; Privilege Control for Servers',X],
['Remote and vendor access','Remote Access (vendor PAM)','Privileged Remote Access; Remote Support','Privileged Remote Access','Access through gateways, no VPN'],
['Secrets and workload identity','Secrets Management (formerly Conjur), Secrets Hub; SPIFFE/SVID for workloads','Password Safe secrets; Workload Credentials','Secret Server, including external cloud secret stores',X],
['Cloud entitlements (CIEM)','Secure Cloud Access','Entitle (CIEM)','Privilege Control for Cloud Entitlements',X],
['Threat detection on identity (ITDR)','CORA AI anomaly detection','Identity Security Insights','Identity Threat Protection; Privileged Behavior Analytics',X],
['Workforce SSO and MFA','Workforce Identity: SSO, adaptive MFA','Integrates with your IdP','Platform identity and federation services','Integrates with your IdP'],
['Governance and SoD (SAP, JD Edwards)','Identity governance',X,'Fastpath access control and certification',X],
['Certificates and PKI','Certificate and PKI management',X,X,X],
['Controls for AI agents','Secure AI Agents; MCP server capability','AI Agent Security (GA 21 Oct 2026); NHI Governance','Runtime authorization for agents, from StrongDM','Leash, open-source runtime policy for agents'],
['AI inside the product','CORA AI assistant and domain agents','PathfinderAI; Pathfinder MCP server','Iris AI; Iris Approver, which can decide or only recommend',X]];
document.querySelector('#capT tbody').innerHTML=V.map(r=>`<tr>${r.map(c=>`<td>${c}</td>`).join('')}</tr>`).join('');

const W=[
{n:'Admin activation',c:C.red,cases:'Round 1 cases 01 to 04, 08, 11',s:[['Admin','Asks for a role for one task, with a ticket',''],['IdP','Passkey or smart card','Not SMS, TOTP or push: those can be relayed (case 11)'],['Policy','Checks eligibility, tier and the two-grant combination','Pair rule (case 04)'],['ITSM','The ticket must name the same system','Ticket match (case 05)'],['Approver','A person approves Tier 0; rules approve the rest',''],['PAM','Grant with a hard end time, 8 hours total','Extension limit (case 03)'],['Broker','Session recorded; token bound to the device','Device binding (case 08)'],['PAM','At the end: role removed, sessions closed, tokens expire','Removal is not enough on its own (case 02)'],['SIEM','Activation, session and removal are on record','']],why:'The window is the control. What matters is whether access really ends when it closes.'},
{n:'AI approver',c:C.amber,cases:'Round 1 case 12',s:[['Request','Arrives with a ticket and a free-text reason',''],['Rules','Code checks system, ticket and hours first','Code checks (control b)'],['AI','Reads structured fields only, never the free text','Fields only (control c)'],['AI','Recommends approve, deny or unsure','Recommend mode (control a)'],['Person','Decides every Tier 0 request and every "unsure"',''],['Log','The AI\'s recommendation is stored next to the human decision','']],why:'An AI that decides alone can be talked into anything a reason field can say. Keep it advising.'},
{n:'Agent at machine speed',c:C.amber,cases:'Round 1 cases 07, 16; round 3 case 05',s:[['Agent','Submits a plan for a database migration',''],['Person','Approves the plan, not each call','Plan approval (case 16)'],['Broker','Exchanges for a per-task token','Task-bound token (case 07)'],['Gateway','Checks every call against the plan','Steps outside the plan are blocked'],['Sub-agent','Gets its own narrower token; depth limit of 1','Token exchange (round 3 case 05)'],['Broker','The token dies when the task ends','No hours of admin left over']],why:'People approve plans. Rules approve calls. Nothing waits in a queue that fills faster than people can read it.'},
{n:'Changing the PAM rules',c:C.red,cases:'Round 1 case 13',s:[['Tool admin','Activates their own JIT role for the PAM tool','No standing tool admins (control c)'],['Second person','Approves the rule change','Two-person rule (control a)'],['PAM','Applies the change',''],['SOC','Alert fires within minutes','An alert does not block (control b)'],['Owner','Reviews the diff the next day','']],why:'The PAM tool is Tier 0. Whoever changes its rules can give themselves anything.'},
{n:'SOC response',c:C.blue,cases:'Round 1 cases 09, 10',s:[['SIEM','New secret or new owner made during a window','Persistence alert'],['SOC','Triage in minutes, not at the next review',''],['Broker','Suspends the session and the grant',''],['Vault','Rotates what was touched',''],['IGA','Removes admin given outside the workflow','Removal, not just a flag (case 10)'],['SOC','Closes with the evidence attached','']],why:'Finding the back door is half the job. Removing it is the half auditors ask about.'},
{n:'Vendor session',c:C.green,cases:'Round 3 case 04',s:[['Vendor','Needs a Tier 0 server for a fix',''],['ITSM','Approved ticket, 2 hours at most','Per-session approval (control b)'],['Broker','Vendor signs in to the broker; no VPN account exists','Broker only (control a)'],['Broker','Session recorded; dangerous commands blocked','Command block (control c)'],['PAM','Access ends with the ticket window','']],why:'A standing vendor VPN account is a door that is open when nobody is looking.'},
{n:'Admin account recovery',c:C.red,cases:'Round 3 case 01',s:[['Caller','Rings the help desk to reset an admin',''],['Help desk','Video check against the HR photo, callback to the manager on file','Control a'],['Policy','No SMS or email recovery for admin accounts','Control b'],['IdP','New authenticator enrolled',''],['PAM','It can\'t activate admin for 24 hours; owner and SOC told at once','Hold (control c)']],why:'Attackers in 2026 don\'t break MFA. They ask the help desk to reset it.'},
{n:'OT change while IT is down',c:C.green,cases:'Round 3 case 08',s:[['Plant','Ransomware has taken down the corporate IdP and vault',''],['Plant','Engineers open the site-local break-glass account','Site-local break-glass (control b)'],['Boundary broker','Attackers in IT still can\'t reach the PLC','Broker rule (control a)'],['PLC','Read-only from remote; the write needs a second person on site','Control c'],['Plant','Change recorded locally; the account is rotated after','']],why:'OT can\'t wait for IT to recover, and must not be reachable from the network that is on fire.'}];
const wt=document.getElementById('wtabs'),ws=document.getElementById('wsteps'),wside=document.getElementById('wside'),wplay=document.getElementById('wplay');
wt.innerHTML=W.map((w,i)=>`<button type="button" role="tab" data-i="${i}" aria-pressed="false"><span class="sw" style="background:${w.c}"></span>${w.n}</button>`).join('');
let wi=0,si=0,timer=0,playing=!reduce;
function wshow(i){wi=i;si=0;const w=W[i];
 wt.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',+b.dataset.i===i));
 ws.style.setProperty('--c',w.c);
 ws.innerHTML=w.s.map((s,k)=>`<li><span class="dot">${k+1}</span><div><span class="lane">${s[0]}</span><div>${s[1]}</div>${s[2]?`<span class="gate">${s[2]}</span>`:''}</div></li>`).join('');
 wside.innerHTML=`<h3>${w.n}</h3><p>${w.why}</p><p class="src">Tested in: ${w.cases}.</p>`;
 paint();clearInterval(timer);if(playing)timer=setInterval(tick,1600)}
function paint(){const li=ws.children;ws.classList.toggle('dim',playing);for(let k=0;k<li.length;k++){li[k].classList.toggle('on',playing&&k===si);li[k].classList.toggle('done',playing&&k<si)}}
function tick(){si++;if(si>=W[wi].s.length+1){wshow((wi+1)%W.length);return}paint()}
wt.addEventListener('click',e=>{const b=e.target.closest('button');if(b)wshow(+b.dataset.i)});
wplay.addEventListener('click',()=>{playing=!playing;wplay.textContent=playing?'Pause':'Play';if(playing){timer=setInterval(tick,1600)}else{clearInterval(timer)}paint()});
document.getElementById('wreplay').addEventListener('click',()=>{playing=true;wplay.textContent='Pause';wshow(wi)});
if(!playing)wplay.textContent='Play';
wshow(0);


const S=[['Verizon, 2026 DBIR announcement','https://www.verizon.com/about/news/breach%2Dindustry%2Dwide%2Ddbir%2Dfinds'],['SpyCloud, takeaways from the 2026 DBIR','https://spycloud.com/blog/top-takeaways-from-the-2026-verizon-data-breach-investigations-report/'],['Delinea, 2026 DBIR: why fundamentals still matter','https://delinea.com/blog/2026-verizon-dbir-cybersecurity-fundamentals-still-matter'],['Help Net Security on Cisco Talos help desk vishing, 30 Oct 2026','https://www.helpnetsecurity.com/2026/10/30/cisco-talos-it-help-desk-vishing/'],['Coveware by Veeam, identity-led extortion','https://www.veeam.com/blog/identity-led-extortion-scattered-spider-cyber-threats.html'],['ReliaQuest threat spotlight, Dec 2025 to Feb 2026','https://reliaquest.com/blog/threat-spotlight-whats-trending-top-cyber-attacker-techniques-december-2025-february-2026/'],['BeyondTrust, AI Agent Security general availability','https://www.beyondtrust.com/press/ai-agent-security-general-availability'],['Delinea, 2026 Identity Security Report','https://delinea.com/news/2026-identity-security-report-the-ai-enforcement-gap'],['Palo Alto Networks, Idira identity security','https://www.paloaltonetworks.com/identity-security'],['Gartner, Magic Quadrant for PAM abstract, 21 Oct 2026','https://www.gartner.com/en/documents/8528809'],['Palo Alto Networks on the 2026 Magic Quadrant','https://www.paloaltonetworks.com/blog/2026/10/palo-alto-networks-named-a-leader-in-the-2026-gartner-magic-quadrant-for-privileged-access-management/'],['BeyondTrust on the 2026 Magic Quadrant','https://www.beyondtrust.com/press/2026-gartner-magic-quadrant-privileged-access-management-leader'],['Idira on Gartner Critical Capabilities 2026','https://www.paloaltonetworks.com/blog/identity-security/gartner-critical-capabilities-privileged-access-management/'],['Delinea completes StrongDM acquisition','https://delinea.com/news/delinea-acquires-strongdm-to-secure-ai-with-continuous-authorization'],['BeyondTrust products','https://www.beyondtrust.com/solutions/industry/enterprise'],['Delinea Platform docs','https://docs.delinea.com/online-help/delinea-platform/getting-started/index.htm'],['Idira CORA AI docs','https://docs.cyberark.com/ai/latest/en/ai/coraai-introduction/'],['NIST SP 800-63B-4, Digital Identity Guidelines: Authentication','https://pages.nist.gov/800-63-4/sp800-63b.html'],['NIST SP 800-207, Zero Trust Architecture','https://csrc.nist.gov/pubs/sp/800/207/final'],['CISA, Implementing phishing-resistant MFA','https://www.cisa.gov/sites/default/files/publications/fact-sheet-implementing-phishing-resistant-mfa-508c.pdf'],['NIST SP 800-53 Rev. 5','https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final']];
document.getElementById('srcs').innerHTML=S.map(s=>`<li><a href="${s[1]}">${s[0]}</a></li>`).join('');

// ---- Lab results, read from the committed evidence files so the page always matches them
const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const SET=['No controls','All on','a off','b off','c off'];
const NOTE={'PA-R1-07|1':'The scope rule still refused the 3 injected requests, so only 27 activations held admin. The guess counted all 30 tasks.','PA-R1-13|0':'JIT on the tool admin role stops an outsider, but a real tool admin\'s activation is approved and nothing then stops them. Flagged before the run.','PA-R3-05|0':'The sub-agent\'s own sub-agent got the parent\'s token too. The guess missed the grandchild; disclosed before the run.'};
const JOINTCASES=new Set();
function parseGuess(md){const out={};md.split(/^### /m).slice(1).forEach(sec=>{const id=(sec.match(/^(PA-R\d-\d\d)/)||[])[1];if(!id)return;
 const title=sec.split('\n')[0].replace(id,'').replace(/\(gap \d\)/,'').trim();
 const scn=(sec.match(/^Scenario:\s*(.+)$/m)||[])[1]||'';const ctl=(sec.match(/^Controls:\s*(.+)$/m)||[])[1]||'';
 const cs={};ctl.replace(/\(([abc])\)\s*([^]*?)(?=;\s*\([abc]\)|\.\s*$|$)/g,(m,k,t)=>{cs[k]=t.trim().replace(/\.$/,'')});
 out[id]={title,scn,cs}});return out}
const get=u=>fetch(u,{cache:'no-cache'}).then(r=>{if(!r.ok)throw new Error(u);return r})
const base='/pam-lab/evidence/';
Promise.all([get(base+'results-round-1.json').then(r=>r.json()),get(base+'results-round-3.json').then(r=>r.json()),get(base+'guesses/guesses-round-1.md').then(r=>r.text()),get(base+'guesses/guesses-round-3.md').then(r=>r.text())]).then(([j1,j3,g1,g3])=>{
 const G=Object.assign(parseGuess(g1),parseGuess(g3));
 const all=[];[[j1,'1'],[j3,'3']].forEach(([j,rd])=>{j.joint.forEach(x=>JOINTCASES.add(x.id));j.rows.forEach(r=>all.push(Object.assign({rd},r)))});
 // scoreboard
 const sc=document.getElementById('score');sc.innerHTML=all.map((r,i)=>`<i class="${r.mismatch.length?'miss':'ok'}" title="${esc(r.id)}: ${r.mismatch.length?'missed':'matched'}" style="transition-delay:${i*40}ms"></i>`).join('');
 requestAnimationFrame(()=>requestAnimationFrame(()=>sc.classList.add('go')));
 // group rows by case
 const byCase={};all.forEach(r=>{(byCase[r.id]=byCase[r.id]||{id:r.id,rd:r.rd,rows:[]}).rows.push(r)});
 const cases=Object.values(byCase);
 cases.forEach(c=>{c.miss=c.rows.some(r=>r.mismatch.length);c.noticed=new Set(c.rows.flatMap(r=>r.noticed));c.layer=c.rows.some(r=>!r.noticed.length)&&JOINTCASES.has(c.id)});
 const card=c=>{const g=G[c.id]||{title:'',scn:'',cs:{}};const cls=c.miss?'miss':(c.layer?'layer':'');
  const ctrls=['a','b','c'].map(k=>g.cs[k]?`<li class="${c.noticed.has(k)?'n':''}"><i>${k}</i>${esc(g.cs[k])}</li>`:'').join('');
  const rows=c.rows.map((r,ri)=>{const lbl=r.counted.replace(/^second count:\s*/,'');
   const cells=r.model.map((v,k)=>{const miss=r.guess[k]!==v,nb=k>1&&v!==r.model[1];return `<span class="cell${miss?' miss':''}${nb?' nb':''}"><small>${SET[k]}</small><b>${esc(v)}</b>${miss?`<s>guess ${esc(r.guess[k])}</s>`:''}</span>`}).join('');
   const note=NOTE[c.id+'|'+ri];return `<div class="crow"><span class="lbl">${esc(lbl)}</span><div class="cells">${cells}</div>${note?`<p class="mnote">${esc(note)}</p>`:''}</div>`}).join('');
  return `<article class="case ${cls}" data-rd="${c.rd}" data-miss="${c.miss}" data-layer="${c.layer}" style="--k:${c.miss?'var(--red)':c.layer?'var(--blue)':'var(--green)'}"><header><span class="cid">${esc(c.id)}</span><b>${esc(g.title)}</b>${c.miss?'<span class="badge">Missed, explained</span>':'<span class="badge">Matched</span>'}${c.layer?'<span class="badge lay">Layered</span>':''}</header><p class="scn">${esc(g.scn)}</p><ul class="ctrls">${ctrls}</ul>${rows}</article>`};
 const box=document.getElementById('cases');box.innerHTML=cases.map(card).join('');
 const fl=document.getElementById('rfilter');fl.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;const f=b.dataset.r;
  fl.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',x===b));
  box.querySelectorAll('.case').forEach(a=>{a.hidden=!(f==='all'||a.dataset.rd===f||(f==='miss'&&a.dataset.miss==='true')||(f==='layer'&&a.dataset.layer==='true'))})});
 // joint checks and sensitivity
 const jt=[];[j1,j3].forEach(j=>j.joint.forEach(x=>jt.push(`<tr><td>${esc(x.id)}</td><td>${esc(x.check)}</td><td>${esc(x.guess.map(v=>v===null?'not stated':v).join(', '))}</td><td>${esc(x.model.join(', '))}</td><td>${x.match?'Matched':'Missed'}</td></tr>`)));
 document.querySelector('#jointT tbody').innerHTML=jt.join('');
 const st=[];[[j1,'1'],[j3,'3']].forEach(([j,rd])=>j.sensitivity.forEach(x=>st.push(`<tr><td>${rd}</td><td><code>${esc(x.param)}</code></td><td>${esc(x.was)}</td><td>${esc(x.now)}</td><td>${esc(x.cases_that_move.join(', ')||'none')}</td></tr>`)));
 document.querySelector('#sensT tbody').innerHTML=st.join('');
}).catch(()=>{});
const cp=document.getElementById('copyrun');cp.addEventListener('click',()=>{const t=document.getElementById('runcmd').textContent;(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(()=>{cp.textContent='Copied'},()=>{cp.textContent='Select and copy'});setTimeout(()=>{cp.textContent='Copy'},2000)});
}
