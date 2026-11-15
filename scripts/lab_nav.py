"""One sub-nav shape for all four labs. Same labels, same order; a lab leaves a label out when it has no page for it.
Used by add-lab-nav.py and by the page generators, so regenerating a page never brings the old nav back."""
import html

ALL = ("/labs/", "All labs")
LABS = {
    "ca": dict(
        name="Conditional access, MFA and AI agent lab",
        primary=[("Overview", "/ca-mfa-lab/"), ("How it works", "/ca-mfa-lab/framework/"),
                 ("Results", "/ca-mfa-lab/#result"), ("Cases", "/ca-mfa-lab/register/"),
                 ("What I got wrong", "/ca-mfa-lab/what-i-got-wrong/"), ("Try it", "/ca-mfa-lab/virtual-lab/"),
                 ("Book", "/ca-mfa-lab/ca-mfa-lab-book.pdf")],
        more=[("The method", "/ca-mfa-lab/method/"), ("Run 4", "/ca-mfa-lab/run-4/"), ("Run it in the browser", "/ca-mfa-lab/virtual-lab/run/"),
              ("Sources and events", "/ca-mfa-lab/sources/"), ("How I test", "/method/"), ("Related: NHI lab", "/nhi-lab/")]),
    "nhi": dict(
        name="Non-human identity lab",
        primary=[("Overview", "/nhi-lab/"), ("How it works", "/nhi-lab/framework/"),
                 ("Results", "/nhi-lab/audit/"), ("Cases", "/nhi-lab/register/"),
                 ("What I got wrong", "/nhi-lab/audit/#wrong"), ("Try it", "/nhi-lab/explainer/"),
                 ("Book", "/nhi-lab/nhi-lab-book.pdf")],
        more=[("The method", "/nhi-lab/method/"), ("Sources and market", "/nhi-lab/market/"), ("Round 18", "/nhi-lab/round-18/"), ("Round 19", "/nhi-lab/round-19/"),
              ("Stage 2", "/nhi-lab/stage-2/"), ("Roadmap", "/nhi-lab/roadmap/"), ("How I test", "/method/")]),
    "agl": dict(
        name="AI governance lab",
        primary=[("Overview", "/ai-governance-lab/"), ("How it works", "/ai-governance-lab/diagrams/"),
                 ("Results", "/ai-governance-lab/evidence/"), ("Cases", "/ai-governance-lab/cases/"),
                 ("What I got wrong", "/ai-governance-lab/what-i-got-wrong/"), ("Try it", "/ai-governance-lab/try/"),
                 ("Book", "/assets/ai-governance-lab-book.pdf")],
        more=[("Implement it", "/ai-governance-lab/implement/"), ("Run it", "/ai-governance-lab/run/"),
              ("Mac commands", "/ai-governance-lab/mac/"), ("The story", "/ai-governance-lab/story/"),
              ("Transcripts", "/ai-governance-lab/transcripts/"), ("Appendix", "/ai-governance-lab/appendix/"),
              ("Rounds 5 to 13", "/ai-governance-lab/#rounds"), ("Standards map", "/ai-governance-lab/frameworks/"), ("Errata", "/ai-governance-lab/errata/"), ("How I test", "/method/")]),
    "mcp": dict(
        name="MCP lab",
        primary=[("Overview", "/mcp-lab/"), ("How it works", "/mcp-lab/in-depth/"),
                 ("Results", "/mcp-lab/results/"), ("Cases", "/mcp-lab/use-cases/"),
                 ("What I got wrong", "/mcp-lab/#wrong"), ("Try it", "/mcp-lab/portal/"),
                 ("Book", "/assets/who-approved-that-book.pdf")],
        more=[("What the numbers mean", "/mcp-lab/#numbers"), ("Browser lab", "/mcp-human-approval-gateway/"),
              ("Full report (PDF)", "/assets/humangate-mcp-lab-final-report.pdf"), ("How I test", "/method/")]),
}

def lab_of(path):
    if path.startswith("/ai-governance-lab/round-"):
        return "agl"
    for k, v in LABS.items():
        for t, h in v["primary"] + v["more"]:
            if h.split("#")[0] == path and not t.startswith("Related") and h != "/method/":
                return k
    raise KeyError(path)

def render(lab, path):
    """path like '/nhi-lab/register/' marks the matching link as the current page."""
    v = LABS[lab]
    def li(t, h):
        cur = ' aria-current="page"' if (h == path or (h.endswith("/#rounds") and path.startswith(h.split("#")[0] + "round-"))) else ""
        return f'<li><a href="{h}"{cur}>{html.escape(t)}</a></li>'
    main = "".join(li(t, h) for t, h in v["primary"])
    more = ""
    if v["more"]:
        more = '<ul class="ln-more" aria-label="More pages in this lab">' + "".join(li(t, h) for t, h in v["more"]) + "</ul>"
    return (f'<nav class="lab-nav" aria-label="{html.escape(v["name"])} pages"><div class="ln-top">'
            f'<a class="ln-all" href="{ALL[0]}">{ALL[1]}</a><ul>{main}</ul></div>{more}</nav>')
