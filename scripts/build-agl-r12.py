#!/usr/bin/env python3
"""Writes assets/agl-r12.js: the 7 cases added in round twelve (approvals), with results, a plain-words
walk-through and five new controls. Reads the lab's results files. Run: python3 scripts/build-agl-r12.py"""
import json, glob
LAB = "/home/claude/ai-governance-lab"
res = json.load(open(sorted(glob.glob(f"{LAB}/results/round-12/*-v3.json"))[-1]))
first = json.load(open(sorted(glob.glob(f"{LAB}/results/round-12/*-v3.json"))[0]))
mut = json.load(open(sorted(glob.glob(f"{LAB}/results/round-12/*-mutations.json"))[-1]))
rows = {r["id"]: r for r in res["results"]}
T = {
"F1": dict(what="A person raises a payment change and then approves it themselves. Asked with no rule against it, and with a four-eyes rule: the approver must be someone other than the requester.",
  steps=[["note","Meera raises a payment of 40,000 to a vendor. She is also allowed to approve payments."],
         ["miss","With no rule, she approves her own request and it runs. Nobody else ever looked."],
         ["stop","With a four-eyes rule, her own approval is refused and the request waits for someone else."]],
  result="Self-approval accepted; four-eyes refuses it.", why="An approval only means something if it comes from a second person. The rule has to be in the system, not in a policy document."),
"F2": dict(what="After a request is approved, the requester edits the amount before it runs. Asked when the approval is tied only to the request number, and when it is tied to a fingerprint of the exact content that was approved.",
  steps=[["note","Arun approves a payment of 40,000. Then the requester changes it to 4,000,000."],
         ["miss","If the approval is tied only to the request number, the edited request runs under Arun's approval."],
         ["stop","If the approval is tied to a fingerprint of what Arun saw, the edit voids it and the request must be approved again."]],
  result="Edited request runs under the old approval; the fingerprint refuses it.", why="Approve what was shown, not a number that can point at something else later."),
"F3": dict(what="An approver is shown 20 requests at once and approves them all with one click; one of the 20 is far over the normal limit. Asked when batch approval has no limit, and when high-risk requests are excluded from batches.",
  steps=[["note","Nineteen requests are for 5,000. One has been changed to 900,000."],
         ["miss","With no limit, one click approves all twenty, including the big one."],
         ["stop","If high-risk items are left out of batches, nineteen are approved and the big one is held back for a separate look."]],
  result="Big item passes in a batch; excluding high-risk items holds it back.", why="People approve what is easy to approve. Make the risky item hard to approve by accident."),
"F4": dict(what="A request is approved on Monday and the system runs it on Thursday. Asked with no expiry on approvals, and with approvals that lapse after 24 hours.",
  steps=[["note","The approval was true on Monday. By Thursday the vendor, the budget or the person may have changed."],
         ["miss","With no expiry, the three-day-old approval still runs."],
         ["stop","With a 24-hour lapse, it is refused and has to be asked for again."]],
  result="Stale approval runs; a 24-hour lapse refuses it.", why="An approval is a statement about a moment. It should not be good forever."),
"F5": dict(what="The only approver for a queue of pending requests leaves the company. Asked when the queue stays with the leaver, and when pending requests move to the approver's manager on departure.",
  steps=[["note","Arun is the approver for a queue. He leaves. Three requests are still waiting."],
         ["miss","If the queue stays with Arun, nobody can act on it, and the requests wait for a person who no longer exists."],
         ["ok","If pending requests move to Arun's manager when he leaves, Kiran can act on them."]],
  result="Queue stuck with the leaver; reassignment holds.", why="Work assigned to a person should not die, or sit unseen, when the person goes. This is the leaver process applied to approvals."),
"F6": dict(what="Two approvers are asked about the same request: one approves and one denies. Asked when any one approval is enough, and when a single denial wins.",
  steps=[["note","Arun denies the request. Dev approves it a minute later."],
         ["miss","With 'any one approval', the request runs even though Arun said no."],
         ["stop","With deny-wins, one no is enough and the request does not run."]],
  result="Approval beats denial; deny-wins refuses.", why="When approvers disagree, the safe default is to stop and talk, not to let the more generous one win."),
"F7": dict(what="Two people each approve the other's requests, and nobody else ever looks at either request.",
  steps=[["note","Meera approves Arun's request. Arun approves Meera's. Every rule is on: different people, exact content, in time, no batch."],
         ["miss","Both requests run. Each rule is satisfied, and the arrangement is invisible to the system."]],
  result="Not caught. This is a limit.", why="Rules can check who approved and what. They cannot see why two people always approve each other. That needs someone to look at patterns."),
}
cases = [{"id": r["id"], "track": r["track"], "title": r["title"], "expected": r["expected"], "actual": r["actual"], "verdict": r["verdict"],
          "expected_in_words": r["expected_in_words"]} for r in rows.values()]
assert set(T) == set(rows), set(T) ^ set(rows)
controls = [
 ("C58", "The approver must be a different person from the requester (four-eyes)",
  ["F1"], "A.5.3", "AC-5", "", "164.308(a)(4)(i)", ""),
 ("C59", "An approval is tied to a fingerprint of the exact content approved, and lapses after a set time",
  ["F2","F4"], "A.8.32, A.5.3", "CM-3, AC-5", "6.5.1", "", ""),
 ("C60", "High-risk requests are left out of batch approval and need their own look",
  ["F3"], "A.8.2, A.5.3", "AC-6, AC-5", "7.2.1", "", ""),
 ("C61", "When an approver leaves, requests waiting for them move to a named person",
  ["F5"], "A.5.18, A.6.5", "AC-2, PS-4", "", "164.308(a)(3)(ii)(C)", ""),
 ("C62", "A single denial stops a request, even if another approver said yes",
  ["F6"], "A.5.3", "AC-5", "", "", ""),
]
noticed = sum(1 for m in mut if m["case_notices"])
out = {"when": "25 Oct 2026", "round": 12, "run": res["meta"]["run_at_utc"], "cases_sha256": res["meta"]["cases_sha256"], "counts": res["meta"]["counts"],
       "first_run": {"as_expected": first["meta"]["counts"].get("as expected", 0), "total": len(first["results"])},
       "mutations": {"noticed": noticed, "total": len(mut)},
       "cases": cases, "text": T,
       "controls": [{"id": a, "control": b, "cases": c, "iso27001": d, "nist80053": e, "pci": f, "hipaa": g, "india": h} for a,b,c,d,e,f,g,h in controls]}
open("assets/agl-r12.js", "w").write("/* Round twelve: 7 cases added on 25 Oct 2026 (approvals). Made-up data only. Generated by scripts/build-agl-r12.py */\nwindow.AGL_R12 = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n")
print(len(cases), "cases", len(controls), "controls", noticed, "of", len(mut), "noticed")
