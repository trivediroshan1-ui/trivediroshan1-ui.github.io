#!/usr/bin/env python3
"""Builds ca-mfa-lab/ca-mfa-lab-book.pdf: 'Who signs in?' Made-up data. Reads the lab's own data files.
Usage: python3 build_ca_book.py OUT.pdf"""
import sys, os, json, re, hashlib
sys.path.insert(0, "/home/claude/work/site/scripts"); sys.path.insert(0, "/home/claude/work/fw")
from book_lib import *
import book_lib as BL
import stages as STG

OUT = sys.argv[1] if len(sys.argv) > 1 else "ca-mfa-lab-book.pdf"
EDITION = "14 November 2026"
txt = open("/home/claude/work/out/ca-mfa-lab/data/cases.js", encoding="utf-8").read()
CASES = json.loads(re.search(r"window.CA_CASES=(\[.*?\]);\n", txt, re.S).group(1))
SENS = json.loads(re.search(r"window.CA_SENS=(\[.*?\]);", txt, re.S).group(1))
SRC = json.load(open("/home/claude/work/book/sources.json", encoding="utf-8"))
P5 = json.load(open("/home/claude/ca-mfa-lab/evidence/results-run5.json"))["params"]
P6 = json.load(open("/home/claude/ca-mfa-lab/evidence/results-run6.json"))["params"]
BY = {c["id"]: c for c in CASES}
RUN = [c for c in CASES if c.get("res")]
WRONG = [c for c in RUN if c.get("match") is False]
assert (len(CASES), len(RUN), len(WRONG)) == (130, 124, 6), (len(CASES), len(RUN), len(WRONG))
HASH = {1: "2675a0efa8937fb5ade0910e89c5a2d77ffb4964560bc4778de1157d7305bb62", 2: "f7c8439b21cda129254f4ff6559534afad7833dc880c64408f4dfe82fc2687e2",
        3: "a09daa459851a1d9628d21ceeb51c5fd11bd37c6481b39ec0ab9b2e20205cd98", 4: "38f544b069739445cd057b9569970de89870e4cde688f7f6af93e82f248fd94a",
        5: "bc344bbd00d01d169c0dbde94d83fc628ec973dcbbb067d1c2cad3f74a65e63a", 6: "1abdbf110b58375570d3472f3aefc697b41931f236a53001c1f9d836f01ec22f"}
SCOL = ["#6d5bd0", "#1aa6c9", "#2d6fd4", "#c98a1b", "#1a8a66", "#c93a53", "#7a5a3a"]
STAGES = [dict(id=k, name=n, q=q, ctl=c, ids=i.split(), col=hexc(SCOL[j]), tint=hexc(SCOL[j] + "1f")) for j, (k, n, q, c, i) in enumerate(STG.STAGES)]
SBY = {s["id"]: s for s in STAGES}
IN_C, OUT_C, NA_C = hexc("#c93a53"), hexc("#1a8a66"), hexc("#94a3b8")

def single_in(c):
    r = c["res"]
    return ("in" in r[2:]) if len(r) == 5 else (r[1] == "out" and r[2] == "in")

# ---------------------------------------------------------------- flowables
class ChainDiagram(Flowable):
    """The access chain: seven coloured links, read left to right, top row then bottom row."""
    def wrap(self, aw, ah): self.w = aw; self.h = 84 * mm; return aw, self.h
    def draw(self):
        c = self.canv; gap = 4 * mm; n1 = 4; bw = (self.w - gap * (n1 - 1)) / n1; bh = 30 * mm
        pos = [(i * (bw + gap), self.h - bh - 4 * mm) for i in range(4)] + [((i + 0.5) * (bw + gap), 4 * mm) for i in range(3)]
        for i, s in enumerate(STAGES):
            x, y = pos[i]
            rbox(c, x, y, bw, bh, fill=hexc("#f6f8fd"), stroke=s["col"], lw=1.4)
            c.setFillColor(s["col"]); c.roundRect(x, y + bh - 7 * mm, bw, 7 * mm, 2 * mm, 0, 1); c.rect(x, y + bh - 7 * mm, bw, 3 * mm, 0, 1)
            fit_text(c, x + 2.5 * mm, y + bh - 7 * mm, bw - 5 * mm, 7 * mm, s["name"], "BodyB", 9.2, colors.white, valign="middle")
            fit_text(c, x + 2.5 * mm, y + 8 * mm, bw - 5 * mm, bh - 16.5 * mm, s["q"], "Body", 8.2, INK)
            cnt = len(s["ids"]); fit_text(c, x + 2.5 * mm, y + 1.5 * mm, bw - 5 * mm, 5.5 * mm, f"{cnt} cases", "BodyB", 8.4, s["col"], valign="middle")
        for i in range(3): arrow(c, [(pos[i][0] + bw + 0.5 * mm, pos[i][1] + 15 * mm), (pos[i + 1][0] - 0.5 * mm, pos[i + 1][1] + 15 * mm)], MUTED)
        arrow(c, [(pos[3][0] + bw / 2, pos[3][1]), (pos[3][0] + bw / 2, pos[3][1] - 6 * mm), (pos[4][0] + bw / 2, pos[4][1] + bh + 6 * mm), (pos[4][0] + bw / 2, pos[4][1] + bh)], MUTED)
        for i in range(4, 6): arrow(c, [(pos[i][0] + bw + 0.5 * mm, pos[i][1] + 15 * mm), (pos[i + 1][0] - 0.5 * mm, pos[i + 1][1] + 15 * mm)], MUTED)

class CaseGrid(Flowable):
    """Script output against my guess, one cell per column. Red = bad outcome happens, green = stopped."""
    def __init__(self, c): super().__init__(); self.c = c
    def wrap(self, aw, ah): self.w = aw; return aw, 17 * mm
    def draw(self):
        c = self.canv; cs = self.c; cols = cs["cols"]; n = len(cols); lab = 22 * mm; cw = (self.w - lab) / n; rh = 5.2 * mm
        c.setFont("BodyB", 7.6); c.setFillColor(MUTED)
        for i, h in enumerate(cols): c.drawCentredString(lab + cw * i + cw / 2, 13 * mm, h)
        for r, (name, vals) in enumerate((("Output", cs["res"]), ("My guess", cs["guess"]))):
            y = 6.6 * mm - r * (rh + 1 * mm)
            c.setFont("BodyB", 8); c.setFillColor(INK); c.drawString(0, y + 1.6 * mm, name)
            for i, v in enumerate(vals):
                x = lab + cw * i + 0.8 * mm; ww = cw - 1.6 * mm
                col = IN_C if v == "in" else OUT_C if v == "out" else NA_C
                c.setFillColor(col); c.roundRect(x, y, ww, rh, 1.2 * mm, 0, 1)
                c.setFillColor(colors.white); c.setFont("BodyB", 7.8)
                c.drawCentredString(x + ww / 2, y + 1.6 * mm, {"in": "happens", "out": "stopped"}.get(v, "not tested"))
                if r == 1 and v in ("in", "out") and v != cs["res"][i] and cs["res"][i] != "-":
                    c.setStrokeColor(colors.HexColor("#111827")); c.setLineWidth(1.6); c.roundRect(x - 0.6 * mm, y - 0.6 * mm, ww + 1.2 * mm, rh + 1.2 * mm, 1.4 * mm, 1, 0)

def case_block(cs):
    s = SBY[cs["stage"]]
    head = Paragraph(f'<font color="{s["col"].hexval()}">{cs["id"]}</font>&nbsp;&nbsp;{esc(cs["use"])}', S["casehead"])
    meta = P(f'{esc(s["name"])} &middot; Run {cs["run"]} &middot; {esc(cs["group"])}', "small")
    out = [head, meta]
    rows = []
    if cs.get("bad"): rows.append(["Bad outcome", esc(cs["bad"])])
    if cs.get("ctl"): rows.append(["Controls", esc(cs["ctl"])])
    if cs.get("g1") and isinstance(cs["g1"], dict):
        g = cs["g1"]; rows.append(["What I wrote first", esc(f'{g.get("none","")} / {g.get("with","")} / {g.get("off","")}')])
        if g.get("limit"): rows.append(["Limit I expected", esc(g["limit"])])
    if rows: out.append(table(rows, [32, CW / mm - 32], head=False, zebra=False, col_styles="first-bold"))
    if cs.get("res"):
        out.append(Spacer(1, 2 * mm)); out.append(CaseGrid(cs))
        notes = []
        if cs.get("pair"):
            p_ = cs["pair"]; notes.append(f'Two controls off together ({" and ".join(p_["off"])}): output {p_["result"]}, I guessed {p_["guess"]}.' + (" This was the wrong guess." if p_["result"] != p_["guess"] else ""))
        if cs.get("match") is False and cs.get("diffs"): notes.append("A cell with a dark outline is where my guess was wrong.")
        if cs.get("note"): notes.append("My reasoning when I guessed: " + cs["note"])
        if cs.get("assumes"): notes.append("Assumes: " + cs["assumes"])
        for n_ in notes: out.append(P(esc(n_), "small"))
    else:
        out.append(P("Not run. It needs a real tenant, a hardware key, a real agent product or a person on the phone. Steps and my prediction are in chapter 15.", "small"))
    chk = cs.get("check", "")
    out.append(P(f'Source: {esc(cs.get("src",""))}. Source read: {esc("not read yet" if chk == "Not part of this check" else chk)}.', "tiny"))
    out.append(Spacer(1, 3 * mm)); out.append(Rule())
    return KeepTogether(out)

# ---------------------------------------------------------------- document
class CABook(BL.Book):
    def __init__(self, fn):
        super().__init__(fn)
        self.title = "Who signs in? Conditional access, MFA, SSO and AI agents, tested in public"
        self.subject = "A 130-case lab on sign-in, single sign-on, recovery and AI agent identity"
        self.keywords = "conditional access, MFA, SSO, passkeys, OAuth, AI agents, identity"
    def draw_main(self, c, doc):
        c.saveState()
        col = SBY[doc.stage]["col"] if getattr(doc, "stage", None) else CYAN
        c.setFillColor(col); c.rect(0, H - 3 * mm, W, 3 * mm, 0, 1)
        c.setFont("Body", 8); c.setFillColor(MUTED)
        c.drawString(LEFT, H - 11 * mm, "Who signs in? Tested in public")
        c.drawRightString(W - RIGHT, H - 11 * mm, getattr(doc, "chapter", ""))
        c.setStrokeColor(LINE); c.setLineWidth(0.5); c.line(LEFT, H - 13 * mm, W - RIGHT, H - 13 * mm); c.line(LEFT, 14 * mm, W - RIGHT, 14 * mm)
        c.drawString(LEFT, 9.2 * mm, "Roshan Trivedi  |  roshantrivedi.co.in/ca-mfa-lab/  |  CC BY 4.0  |  Made-up data only")
        c.setFont("BodyB", 9); c.setFillColor(NAVY); c.drawRightString(W - RIGHT, 9.2 * mm, str(doc.page))
        c.restoreState()
    def afterFlowable(self, f):
        if isinstance(f, StageMark): self.stage = f.sid; return
        super().afterFlowable(f)

class StageMark(Flowable):
    def __init__(self, sid): super().__init__(); self.sid = sid
    def wrap(self, aw, ah): return 0, 0
    def draw(self): pass

def cover(c, doc):
    c.saveState(); c.setFillColor(NAVY); c.rect(0, 0, W, H, 0, 1)
    for i, s in enumerate(STAGES):
        x = 22 * mm + i * 25 * mm; y = H - 92 * mm
        c.setStrokeColor(s["col"]); c.setLineWidth(5); c.circle(x, y, 9 * mm, 1, 0)
        c.setFillColor(s["col"]); c.setFont("Head", 15); c.drawCentredString(x, y - 5, str(i + 1))
    c.setFillColor(hexc("#9fb0d4")); c.setFont("BodyB", 10); c.drawString(22 * mm, H - 40 * mm, "CONDITIONAL ACCESS  ·  MFA  ·  SSO  ·  AI AGENTS")
    c.setFillColor(colors.white); c.setFont("Head", 44); c.drawString(22 * mm, H - 62 * mm, "Who signs in?")
    c.setFont("Body", 15); c.setFillColor(hexc("#c8d3ee"))
    for j, ln in enumerate(["130 cases on made-up data. Every guess written,", "hashed and committed before any code ran.", "Six of them were wrong."]):
        c.drawString(22 * mm, H - 120 * mm - j * 7.5 * mm, ln)
    y0 = 92 * mm
    for k, (num, lab, col) in enumerate([("130", "cases", CYAN), ("124", "run on models", GREEN), ("6", "wrong guesses", RED), ("7", "links in the chain", AMBER)]):
        x = 22 * mm + k * 42 * mm
        c.setFillColor(col); c.rect(x, y0, 36 * mm, 1.6 * mm, 0, 1)
        c.setFillColor(colors.white); c.setFont("Head", 30); c.drawString(x, y0 - 13 * mm, num)
        c.setFont("Body", 10); c.setFillColor(hexc("#c8d3ee")); c.drawString(x, y0 - 19 * mm, lab)
    c.setFillColor(colors.white); c.setFont("BodyB", 13); c.drawString(22 * mm, 40 * mm, "Roshan Trivedi")
    c.setFont("Body", 10); c.setFillColor(hexc("#9fb0d4"))
    c.drawString(22 * mm, 33 * mm, f"Edition 1, {EDITION}  ·  roshantrivedi.co.in/ca-mfa-lab/  ·  CC BY 4.0")
    c.drawString(22 * mm, 27 * mm, "Independent work on my own time. Nothing here describes any employer's or client's systems.")
    c.restoreState()

def back(c, doc):
    c.saveState(); c.setFillColor(NAVY); c.rect(0, 0, W, H, 0, 1)
    c.setFillColor(colors.white); c.setFont("Head", 22); c.drawString(22 * mm, H - 60 * mm, "Run it yourself")
    c.setFont("Body", 11.5); c.setFillColor(hexc("#c8d3ee"))
    lines = ["Every guess file, script and result in this book is public. The scripts use only",
             "Python's standard library, check the guess file's hash before they run, and write",
             "the same results file on any machine. On 14 November 2026 they gave byte-identical",
             "results on a second computer.", "",
             "If your product behaves differently from one of my models, report an exception.",
             "It goes next to my result, and my result stays.", "",
             "roshantrivedi.co.in/ca-mfa-lab/"]
    for j, ln in enumerate(lines): c.drawString(22 * mm, H - 75 * mm - j * 6.6 * mm, ln)
    for i, s in enumerate(STAGES): c.setFillColor(s["col"]); c.rect(22 * mm + i * 24 * mm, 40 * mm, 20 * mm, 3 * mm, 0, 1)
    c.restoreState()

BL.Book.cover_art = staticmethod(cover); BL.Book.back_art = staticmethod(back)

# ---------------------------------------------------------------- content
story = []
def add(x):
    if isinstance(x, list): story.extend(x)
    else: story.append(x)
def chapter(num, title, kicker, color=CYAN, sub="", stage=None):
    add(StageMark(stage)); add(ChapterMark(title)); add(NextPageTemplate("main")); add(PageBreak()); add(ChapterHead(num, title, kicker, color, sub)); add(Spacer(1, 4 * mm))
def ps(*texts):
    for t in texts: add(P(t))

add(NextPageTemplate("cover")); add(Spacer(1, 1))
# front matter
add(StageMark(None)); add(ChapterMark("")); add(NextPageTemplate("main")); add(PageBreak())
FRONT = st("H2front", fontName="Head", fontSize=18, leading=22, spaceBefore=6, spaceAfter=6, textColor=NAVY)
add(Paragraph("How to read this book", FRONT))
ps("This is the long version of a public lab I ran on conditional access, MFA, 2FA, single sign-on and AI agent identity. "
   "If you have five minutes, read the short version on the next page and chapter 3. If you have an afternoon, read the link chapters for the parts of sign-in you own.",
   "Everything here runs on made-up data for a made-up company. A case is a small rule model written in Python. It shows whether my reasoning about a control holds together. "
   "It does not show how any vendor's product behaves, and nothing in it describes any employer's or client's systems.",
   "Throughout the book, red means the bad outcome happens and green means it is stopped. Each of the seven links in the framework has its own colour, and the band at the top of each page shows which link you are reading.")
add(Callout("The rule that holds the book together", "For every case I wrote my guess first, saved it, took its SHA-256 hash and committed it before a line of the model existed. A guess file cannot be changed later without its hash changing. When a guess was wrong, it stays in the book as wrong.", "violet"))
add(Paragraph("Contents", FRONT)); add(make_toc())

chapter("", "The short version", "Read this if you read nothing else")
add(Tiles([("130", "cases in the register", CYAN), ("124", "run on small models", GREEN), ("118", "guesses matched", VIOLET), ("6", "guesses wrong, all in one run", RED)]))
ps("I ran 124 of the 130 cases. 118 matched the guess I had locked before any code. Six did not, and all six were in Run 2, the run where each case had two or three controls working together.",
   "The score is the least useful result. Four things I would tell a team that owns sign-in:")
add(numbered([
    "MFA was often not the control that decided the outcome. A stolen integration token never triggers a sign-in. A password reset that does not kill refresh tokens leaves a stolen session alive. A recovery path weaker than sign-in lets an attacker enroll their own authenticator.",
    "The largest group of cases sits in link 4, Decide: a rule that does not cover the sign-in, an exception that grew, a legacy protocol that skips MFA. It holds 33 of the 130 cases and 3 of my 6 wrong guesses.",
    "For AI agents, the controls that decided Run 6 were plain ones: a named human owner, an identity that expires with the task, and a check at the resource against the human's own rights. Narrowing a sub-agent's token and rotating its credential did not decide anything.",
    "Each result rests on an assumption I chose. When I changed one assumption at a time, results flipped. A pass in this book holds only while its assumption holds."]))
ps("Six cases need a real tenant, a hardware key, a real agent product or a person on the phone. They are written up as hand tests for anyone to run, with my predictions locked.")

chapter(1, "The problem", "Why sign-in still fails after MFA", CYAN)
ps("Most organisations have MFA switched on and single sign-on in front of their main apps. Attackers still get in, and the reports usually say MFA was in place. That is the gap this lab looks at.",
   "Sign-in controls fail in two opposite ways. When a control is too hard, people route around it: an exclusion group, a legacy protocol kept for printers, a help desk that resets MFA to keep a caller happy. When it is too easy, it becomes a side door: a push prompt a tired user approves, a recovery path weaker than sign-in, a token that lives for 90 days.",
   "A control mapping sheet tells you a control exists. It does not tell you where the control stops. I wanted to find where each one stops, and I wanted my wrong guesses on the record.")
add(P("Who this is for", "h2"))
add(bullets(["People who own an identity provider, conditional access policies or SSO for apps.",
             "Security architects reviewing MFA, recovery or federation designs.",
             "Teams building AI agents that sign in, call APIs or act for people.",
             "Auditors who want to know what evidence would show a control works."]))
add(P("What is new since the first runs", "h2"))
ps("The first three runs covered MFA methods, SSO protocols, recovery and policy logic. Run 5 added cases from incidents in 2025 and 2026: CI/CD cloud trust, stolen integration tokens, privileged APIs and MCP sign-in. Run 6 added AI agent identity: cross-app access, sub-agents, agents that outlive their project or lose their owner.")

chapter(2, "Scope and method", "What is in, what is out, and how each case was run", CYAN)
add(P("In scope", "h2"))
add(bullets(["MFA and 2FA methods: SMS, TOTP, push, number matching, passkeys and security keys.",
             "Single sign-on: SAML, OpenID Connect and OAuth flows, federation and signing keys.",
             "Conditional access policy logic, context signals, exceptions and emergency accounts.",
             "Account recovery and help desk resets.",
             "Tokens: scope, lifetime, binding, refresh and revocation.",
             "CI/CD cloud trust, API integrations, MCP clients and servers, and AI agents acting for people."]))
add(P("Out of scope", "h2"))
add(bullets(["How any named product behaves. I did not test vendors.", "Real tenants, real people and real data. Six hand tests are left for readers.", "Performance, cost and user experience."]))
add(P("How a case was run", "h2"))
add(numbered(["Pick a failure from the catalogue and the controls that should stop it. Write down the bad outcome first, so I know what I am counting.",
              "Write the expected result with no controls, with all controls on, and with each control switched off on its own.",
              "Save the guesses, hash the file with SHA-256 and commit it. Merge it before any model code exists.",
              "Write the model, run it, and compare the output with the parsed guess file. The script refuses to run if the guess file's hash differs.",
              "Record every miss. Fix my own coding mistakes in the open and keep the first-pass files.",
              "For Runs 5 and 6, change one assumption at a time and record which results flip."]))
add(P("The six runs", "h2"))
add(table([["Run", "What it covered", "Cases", "Matched", "Guess file SHA-256 (first 16)"],
           ["1", "Single controls: MFA methods, SSO protocols, recovery", "41", "41 of 41", HASH[1][:16]],
           ["2", "Two or three controls working together", "45", "39 of 45", HASH[2][:16]],
           ["3", "Step-up, federation, mobile, passkeys, agents and MCP", "16", "16 of 16", HASH[3][:16]],
           ["4", "Hand tests E01 to E03 (predictions only)", "3", "not run", HASH[4][:16]],
           ["5", "CI/CD, APIs and integrations, agents, recovery", "12", "12 of 12", HASH[5][:16]],
           ["6", "AI agent identity, plus hand tests E04 to E06", "10 + 3", "10 of 10", HASH[6][:16]]],
          [12, 74, 18, 22, 48]))
add(Callout("Why the perfect runs prove little", "I wrote each model after its guesses. A perfect score shows that my model and my reasoning agree. Nothing outside me tested the guesses. Run 2 was the only run that caught me out, and it taught me the most.", "warn"))

chapter(3, "The framework: the access chain", "Seven links every sign-in passes through", VIOLET)
ps("Every sign-in, and every action an agent takes for a person, passes through seven links. A case belongs to the link where its deciding control sits. A weak link anywhere lets the bad outcome through, however strong MFA is at link 2.")
add(ChainDiagram()); add(P("Figure 1. The access chain. Read left to right, top row then bottom row. Each box shows the question the link asks and how many cases sit in it.", "cap"))
rows = [["Link", "The question", "Controls that decide it", "Cases", "Run", "One off lets it in", "Wrong"]]
for s in STAGES:
    cs = [BY[i] for i in s["ids"]]; rn = [c for c in cs if c.get("res")]
    rows.append([f'<font color="{s["col"].hexval()}"><b>{esc(s["name"])}</b></font>', esc(s["q"]), esc(s["ctl"]), str(len(cs)), str(len(rn)), str(sum(single_in(c) for c in rn)), str(sum(c.get("match") is False for c in rn))])
add(table(rows, [28, 36, 62, 12, 10, 14, 12]))
ps("Two counts stand out. Link 4, Decide, holds a quarter of the cases and half the wrong guesses. Link 6, Act, has the highest share of cases where switching off one control on its own let the bad outcome in: 12 of the 13 run.")

for k, s in enumerate(STAGES):
    cs = [BY[i] for i in s["ids"]]
    chapter(4 + k, s["name"].split(". ", 1)[1], f"Link {k + 1} of 7", s["col"], s["q"], stage=s["id"])
    rn = [c for c in cs if c.get("res")]
    add(Tiles([(str(len(cs)), "cases in this link", s["col"]), (str(len(rn)), "run on models", GREEN),
               (str(sum(single_in(c) for c in rn)), "where one control off lets it in", RED), (str(sum(c.get("match") is False for c in rn)), "wrong guesses", AMBER)]))
    ps(f'Controls that decide this link: {esc(s["ctl"])}.',
       "Each case below shows the bad outcome, the controls, and two rows of results: what the script produced and what I guessed beforehand. Columns read left to right: no controls, all controls, then each control switched off on its own.")
    for c in sorted(cs, key=lambda x: (x["run"], x["id"])): add(case_block(c))

chapter(11, "What I got wrong", "Six wrong guesses, five kinds of mistake", RED)
ps("All six wrong guesses were in Run 2. Read together, they fall into five kinds of mistake. Each one is a habit I now check for before I write a guess.")
for t_, d_ in [("I did not say what I was counting (C01, C03).", "I defined the bad outcome as an account takeover that nobody notices. The change notice and the exclusion alert make any takeover noticed, so removing the SMS fallback or the exclusion review alone never produced the bad outcome."),
               ("I treated controls as independent (A05).", "For guest sign-ins, trusting the home tenant's MFA claim means a weak MFA at home satisfies the requirement in mine. Adding my own guest MFA rule did not help, and with the trust on, all controls on still let the bad outcome in."),
               ("I picked the wrong control as the one that mattered (Z21).", "I said refresh token lifetime did not matter. The bad outcome was the attacker still having access after 24 hours, which the refresh token lifetime decides. My wrong guess was in the pair test with two controls off together."),
               ("I did not think through a control's own scope (X07).", "The trusted-network exception was limited to the managed office. Guest wifi in the same range was not trusted, so MFA was required and the attacker was stopped without the device rule."),
               ("I counted a convention as a control (A03).", "Separate admin accounts are a habit, not enforcement. I had the two cases reversed: with only separate accounts nothing stops the admin account reaching a risky app, while the group block does stop the daily account.")]:
    add(Callout(t_, esc(d_), "bad"))
add(P("One mistake in my own code", "h2"))
ps("In the first pass of Run 2, my model said approval stops an unauthorised console change (P11). An unauthorised change skips approval by definition, so only the log can show it. I fixed the model and kept the first-pass script and results in the repository. This was a coding mistake, not a wrong guess, and I count it separately.")

chapter(12, "What changes the answer", "One assumption at a time", AMBER)
ps("Every model rests on assumptions I chose: how fast an attacker replays a token, how often people read a prompt, how long a session lasts. For Runs 5 and 6 I changed one assumption at a time and re-ran. This table lists every change and what it did.")
rows = [["Assumption changed", "Cases that flipped", "What happened"]]
for x in SENS:
    fl = x["flips"]
    what = "No change." if not fl else "; ".join(f'{f["id"]}: {" ".join(f["was"])} became {" ".join(f["now"])}' for f in fl)
    rows.append([esc(x["change"]), esc(", ".join(f["id"] for f in fl) or "none"), esc(what)])
add(table(rows, [64, 26, 84]))
ps("Read the flips as a list of what to check in your own setup. If your people almost always read a confirmation prompt, approval does real work. If your continuous evaluation only watches the network, an attacker who looks local gets past it. If your secret scanner does not read build logs, it will not find a secret leaked in one.")

chapter(13, "What companies are suffering", "Dated events behind the cases", RED)
ps("The cases come from public reports. Each event below has a date, the lab cases it relates to, the kind of source, and how far I trust it. Companies appear because the sources name them. A name here says nothing about that company's controls today.")
rows = [["Date", "What was reported", "Cases", "Source and trust"]]
for e in SRC["events"]:
    rows.append([esc(e["date"]), esc(e["what"]), esc(e["cases"]), esc(e["stype"] + ". " + e["trust"])])
add(table(rows, [20, 82, 18, 54]))

chapter(14, "Research and development: where vendors and standards are going", "What I read, and how far to trust it", BLUE if hasattr(BL, "BLUE") else CYAN)
ps("I searched once, in November 2026, for what identity vendors and standards bodies are building for non-human identity, AI agents, MFA and SSO. Most of what came back is vendor material or a write-up of it, so each row says what kind of source it is. Product claims are the vendor's.")
rnd = [["Who", "What (date)", "Source type", "Used in"],
       ["Okta", "Agent SSO generally available, built on Cross App Access; short-lived tokens in place of stored credentials; agent authorization moved to the identity provider. The release does not say how revocation works (24 Aug 2026).", "Vendor press release, read", "G01, E04"],
       ["Okta", "Okta for AI Agents generally available (30 Apr 2026); Blueprint Alliance for a reference architecture to secure agents (22 Sep 2026).", "Secondary write-up citing Okta", "Context"],
       ["Okta", "Argues that SSO and MFA leave session-hijack gaps that continuous identity checks close.", "Vendor blog, excerpt", "G07, E06"],
       ["Ping Identity", "Enterprise Personal Agent Access for agents employees run themselves (1 Sep 2026); admin agents for Gemini Enterprise that reset passwords and end sessions on request (late Sep 2026).", "News excerpts", "G02, G06, E05"],
       ["Cloud Security Alliance", "Defining Non-Human Identity: six risk areas for all non-human identities; for agents, a human sponsor each, minimal short-lived delegated access limited to the human's own permissions, and logs naming delegator, agent and intent (22 Jul 2026).", "Industry research, read", "G03, G04, G05, G10"],
       ["IETF", "AIMS, an emerging draft framework for agent identity using certificates.", "Vendor explainer of a draft", "G08 (verify)"],
       ["MCP project", "Authorization specification, 2026-07-28 revision: clients find the authorization server from protected resource metadata and check the issuer.", "Specification, read", "W11, Y11, Y12"],
       ["GitHub", "Immutable OIDC subject claims with owner and repository IDs for repositories created after 15 July 2026.", "Vendor documentation, read", "W01"],
       ["Microsoft", "SMTP AUTH Basic authentication disabled by default for existing tenants at the end of December 2026; final removal date due in the second half of 2027.", "Vendor announcement, read", "Z20"],
       ["SANS", "2026 survey: the challenge has moved from buying identity tools to making them work.", "Survey, excerpt", "Context"]]
add(table(rnd, [26, 92, 34, 22]))
add(Callout("What I could test from this", "Everything that is rule logic went into Run 6 as a model. Everything that needs the real product went into the hand tests E04 to E06. None of it tests a vendor's product.", "info"))

chapter(15, "The lab for your people", "Run it, break it, report what you find", GREEN)
add(P("Run the scripts", "h2"))
add(numbered(["Install Python 3. The scripts use only the standard library.",
              "Download a script and its guess file from roshantrivedi.co.in/ca-mfa-lab/evidence/.",
              "Check the guess file's hash with <font name='Mono'>shasum -a 256</font>. It should match the table in appendix A.",
              "Run it, for example <font name='Mono'>python3 -I run6.py guesses-run6.md</font>. Each case prints its output, my guess and OK or MISMATCH.",
              "Open the script, change one value in PARAMS, run it again, and see which cases change."]))
add(P("The six hand tests", "h2"))
ps("These need something a model cannot stand in for. Use a throwaway test tenant, made-up users and a spare key. Never call a real help desk, and never put a tenant name, password, code or token in your notes.")
add(table([["Test", "What it checks", "Link"]] + [[c["id"], esc(c["use"]), esc(SBY[c["stage"]]["name"])] for c in CASES if c["run"] == 4], [14, 120, 40]))
add(P("Report an exception", "h2"))
ps("If you test any case in a real product and it behaves differently from my model, use the exception form on the lab's GitHub. It asks for the case ID, the product and version, what you saw and how you checked. Accepted exceptions go next to my result with a date, and my result stays.")
add(P("Run it as a team workshop", "h2"))
add(numbered(["Pick one link from chapter 3 that your team owns.",
              "Before anyone opens the results, each person writes a guess for three cases in that link.",
              "Compare the guesses, then open the case pages and play each case one column at a time.",
              "For every case where someone was surprised, write down the assumption that would make your own setup different.",
              "Turn the surprises into checks: a policy review, a test in a test tenant, or a question for your vendor."]))

chapter(16, "Conclusion", "What I would check first", VIOLET)
ps("If I owned sign-in for an organisation tomorrow, I would not start with a new MFA method. I would start with these:")
add(numbered(["Which sign-ins does no rule cover? Look for the default, the exceptions and the legacy paths.",
              "Is account recovery at least as strong as sign-in, including the help desk?",
              "Does a password reset end refresh tokens and sessions, everywhere?",
              "Does every privileged action check fresh MFA on the server, for keys and service tokens too?",
              "Does every agent have a named owner, an expiry tied to its task, and a resource that checks the human's own rights?",
              "When access is revoked, how long does each kind of token keep working?"]))
ps("This lab cannot tell you how your product behaves. It can tell you which questions to ask, and what the answer depends on. The six hand tests and the exception form are there so people with real tenants can tell me where I am wrong.")

add(StageMark(None)); add(ChapterMark("Evidence")); add(NextPageTemplate("main")); add(PageBreak())
add(ChapterHead("A", "Evidence", "Hashes, reproduction and assumptions", MUTED))
add(P("Guess files", "h2"))
add(table([["Run", "File", "SHA-256"]] + [[str(r), f"guesses-run{r}.md", f'<font name="Mono" size="7">{HASH[r]}</font>'] for r in range(1, 7)], [12, 36, 126]))
add(P("Reproduction", "h2"))
ps("On 14 November 2026 I reran all five scripts on a second machine, a Mac with macOS on x86_64 and Python 3.9.6. Every results file came out byte for byte identical to the published one. The log had 119 lines ending in OK and 5 ending in MISMATCH, the five Run 2 cases where my guess was wrong. The sixth wrong guess, Z21, is in a pair test that the per-case line does not show.")
add(P("Assumptions in Runs 5 and 6", "h2"))
add(table([["Run", "Parameter", "Value"]] + [["5", esc(k), esc(str(v))] for k, v in P5.items()] + [["6", esc(k), esc(str(v))] for k, v in P6.items()], [12, 70, 92]))
ps("Runs 1 to 3 keep their assumptions in the header of each script.")

add(ChapterMark("The full register")); add(NextPageTemplate("main")); add(PageBreak())
add(ChapterHead("B", "The full register", "All 130 rows", MUTED))
rows = [["ID", "Case", "Link", "Run", "Result", "Source read"]]
for c in CASES:
    res = "not run" if not c.get("res") else ("guess wrong" if c.get("match") is False else "guess matched")
    rows.append([c["id"], esc(c["use"]), esc(SBY[c["stage"]]["name"].split(". ", 1)[1]), str(c["run"]), res, esc("not read yet" if c.get("check") == "Not part of this check" else c.get("check", ""))])
add(table(rows, [11, 86, 24, 9, 20, 24]))

add(ChapterMark("Glossary")); add(NextPageTemplate("main")); add(PageBreak())
add(ChapterHead("C", "Glossary", "Terms in plain words", MUTED))
GL = [("AAL", "Authenticator assurance level in NIST SP 800-63B. AAL3 needs a hardware-bound key that cannot be copied."),
 ("Access token", "A short-lived credential an app presents to an API. Whoever holds it can usually use it."),
 ("AiTM", "Adversary in the middle. A phishing proxy that relays the real sign-in and steals the session cookie after MFA."),
 ("Assertion", "A signed statement from an identity provider that a user signed in, for example a SAML assertion."),
 ("Audience", "The app or API a token or assertion is meant for. An app that does not check it may accept a token meant for another."),
 ("Authorization server", "The service that issues OAuth tokens."),
 ("Break-glass account", "An emergency account kept outside normal rules so admins are not locked out."),
 ("Conditional access", "Rules that decide whether a sign-in is allowed, blocked or needs more proof, based on user, app, device and context."),
 ("Consent phishing", "Tricking a user into granting a malicious app access, with no password stolen."),
 ("Continuous access evaluation", "Re-checking a session after sign-in when something changes, such as a revoked user or a new network."),
 ("Cross App Access", "An approach where an AI agent gets access to a second app through the enterprise identity provider."),
 ("Device code flow", "An OAuth flow for devices without a keyboard. Attackers use it to get a victim to approve their code."),
 ("DPoP", "Demonstrating Proof of Possession (RFC 9449). Binds a token to a key so a copied token fails from another machine."),
 ("Exclusion group", "A group left out of a policy. It tends to grow."),
 ("Federation", "Trusting another identity provider's sign-ins and claims."),
 ("FIDO2 and WebAuthn", "Standards behind passkeys and security keys. The key signs only for the real site's origin."),
 ("Golden SAML", "Forging SAML assertions with a stolen identity provider signing key."),
 ("Help desk reset", "Staff resetting a password or MFA for a caller. A common way in for social engineers."),
 ("Identity provider (IdP)", "The service that signs users in and vouches for them to apps."),
 ("Issuer", "The identity provider or authorization server named in a token or metadata."),
 ("Legacy authentication", "Old sign-in protocols, such as SMTP AUTH with a password, that cannot do MFA."),
 ("MCP", "Model Context Protocol. A way for AI applications to connect to tools and data. Its authorization uses OAuth."),
 ("MFA, 2FA", "Signing in with more than one kind of proof. 2FA means exactly two."),
 ("Nonce", "A one-time value that ties a response to the request that asked for it."),
 ("Number matching", "A push prompt where the user types a number shown on the sign-in screen, which stops blind approval."),
 ("OIDC", "OpenID Connect. A sign-in layer on top of OAuth that issues ID tokens."),
 ("OAuth", "A framework for granting apps limited access to resources with tokens."),
 ("On behalf of", "An agent or service acting for a person. The token should carry who that person is."),
 ("Passkey", "A FIDO credential that replaces a password. It can be synced across devices or bound to one."),
 ("Phishing-resistant MFA", "MFA a look-alike site cannot relay, such as passkeys and security keys."),
 ("PKCE", "Proof Key for Code Exchange. Stops an intercepted authorization code from being used by someone else."),
 ("Privileged access", "Access that can change security settings, data or other people's access."),
 ("Push fatigue", "Sending prompts until a tired user approves one."),
 ("Redirect URI", "Where an authorization server sends the code or token. It must match exactly."),
 ("Refresh token", "A longer-lived credential that gets new access tokens without signing in again."),
 ("Report-only mode", "Running a policy that logs what it would do without enforcing it."),
 ("ROPC", "Resource owner password credentials. Sending a password straight to the token endpoint, which cannot do MFA."),
 ("SAML", "Security Assertion Markup Language. An older SSO standard based on signed XML assertions."),
 ("Service account", "An account used by software, not a person."),
 ("Session", "The period after sign-in when a cookie or token keeps a user signed in."),
 ("SIM swap", "Moving a phone number to an attacker's SIM to receive SMS codes."),
 ("SSO", "Single sign-on. One sign-in at the identity provider gives access to many apps."),
 ("Step-up", "Asking for fresh, stronger proof before a sensitive action."),
 ("Sub-agent", "An agent started by another agent to do part of a task."),
 ("Token binding", "Tying a token to a device or key so it cannot be used elsewhere."),
 ("Token exchange", "Swapping one token for another with narrower scope, for example when delegating (RFC 8693)."),
 ("TOTP", "Time-based one-time password from an authenticator app."),
 ("Trusted location", "A network range a policy treats as safer, often to skip MFA."),
 ("Workload identity", "An identity for software, such as a pipeline or a cloud function, that uses short-lived federated tokens.")]
add(table([["Term", "Meaning"]] + [[f"<b>{esc(a)}</b>", esc(b)] for a, b in GL], [42, 132]))

add(ChapterMark("Sources")); add(NextPageTemplate("main")); add(PageBreak())
add(ChapterHead("D", "Sources", "Standards, documents and events", MUTED))
add(P("Standards and documents", "h2"))
add(table([["Document", "Kind", "What it says that matters here", "Cases"]] + [[esc(x["doc"]) + "<br/>" + "<br/>".join(f'<font size="6.6" color="#5b6785">{esc(u)}</font>' for u in x["links"]), esc(x["kind"]), esc(x["says"]), esc(x["cases"])] for x in SRC["stds"]], [52, 24, 78, 20]))
add(P("Events", "h2"))
add(table([["Date", "Event", "Links"]] + [[esc(e["date"]), esc(e["what"][:180] + ("..." if len(e["what"]) > 180 else "")), "<br/>".join(f'<font size="6.6">{esc(u)}</font>' for u in e["links"])] for e in SRC["events"]], [22, 82, 70]))
ps("Each catalogue row also has its own source, listed in the register on the website. Where I read only an excerpt or a summary, the register says so.")
add(NextPageTemplate("back")); add(PageBreak()); add(Spacer(1, 1))

doc = CABook(OUT)
doc.multiBuild(story)
print("pages:", doc.page)
