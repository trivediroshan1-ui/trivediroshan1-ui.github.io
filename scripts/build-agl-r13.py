#!/usr/bin/env python3
"""Writes assets/agl-r13.js: the 6 cases added in round thirteen (search by meaning), with results from the real run on the Mac,
a plain-words walk-through and four new controls. Reads the lab's results files. Run: python3 scripts/build-agl-r13.py"""
import json
LAB = "/home/claude/ai-governance-lab/results/round-13"
def load(n): return json.load(open(f"{LAB}/{n}"))
REAL = "20261024-235928-v3.json"          # Mac, real model, the first run that worked
FAILED = "20261024-235333-v3.json"        # Mac, NumPy 2: every case errored
TOY = "20261024-234459-v3.json"           # sandbox, toy embedder
MUT_OK = "20261025-000134-mutations.json" # Mac, real model, fixed checker
MUT_BAD = "20261024-235645-mutations.json"# Mac, NumPy 2: every case errored, checker still said 5 of 5
MUT_TOY = "20261024-234459-mutations.json"
real, failed, toy = load(REAL), load(FAILED), load(TOY)
mut, mbad, mtoy = load(MUT_OK), load(MUT_BAD), load(MUT_TOY)
rows = {r["id"]: r for r in real["results"]}
assert real["meta"]["embedder"].startswith("sentence-transformers") and real["meta"]["counts"] == {"as expected": 6}
assert failed["meta"]["counts"] == {"not run": 6}
assert all(m["valid"] for m in mut) and all(m["normal"] != m["with_control_off"] for m in mut)
assert all(str(m["normal"]).startswith("error") for m in mbad)
T = {
"S1": dict(what="A support agent asks about pay in words that share nothing with the HR salary document. Asked with no permission check, and with the live permission check before the documents are used.",
  steps=[["note","The question is: what are employees paid, how are pay bands changing? None of those words appear in the HR salary document, so keyword search would not find it."],
         ["note","The assistant turns the question and every document into numbers and looks for the closest meaning (an embedding model, all-MiniLM-L6-v2 on the Mac)."],
         ["miss","With no permission check, the HR salary document comes back as a close match and its text reaches the support agent."],
         ["stop","With the live permission check before retrieval, the document is never offered to the agent."]],
  result="Search by meaning found the HR text and leaked it with no check; the live check held.", why="Search by meaning finds documents that keyword search misses, so a missing permission check leaks more, not less. This case relies on the model ranking that document in its top three, and the real model did."),
"S2": dict(what="The same pay question, with the permission check in place, when the answer shows its sources. Asked when the source list shows every match, and when it shows only what the person may see.",
  steps=[["note","The permission check keeps the HR text out of the answer."],
         ["miss","If the source list shows every match, the support agent still sees the title Salary review 2026."],
         ["stop","If it shows only sources the person may see, the title is not shown."]],
  result="The HR title leaked when every match was shown; it stayed hidden otherwise.", why="A title can tell someone that a document exists. The list of sources has to follow the same permissions as the text."),
"S3": dict(what="Search keeps only its single best match, and the best match is a restricted document. Asked when the permission filter runs after the ranking, and when it runs before.",
  steps=[["note","For the pay question, the single best match is the HR salary document."],
         ["miss","If the filter runs after the ranking, that match is removed and nothing is left. Nothing leaks, but the person gets no answer at all."],
         ["ok","If the filter runs before the ranking, the person gets the best document they are allowed to see (the panel pay table) and no restricted text."]],
  result="Filter after the ranking gave an empty answer; filter before gave the best allowed document.", why="Restricted documents can crowd out the allowed ones. This is a usefulness problem, not a leak, and the order of the two steps decides it."),
"S4": dict(what="A customer note holds an Aadhaar-format number (made up) and is found by meaning. Asked with the number masked when the notes are indexed, and without masking.",
  steps=[["note","The question is about a customer's address and ID number on file. The note is found by meaning."],
         ["miss","Without masking when the notes are indexed, the number appears in the answer."],
         ["stop","With masking at indexing time, the answer shows [AADHAAR]. How the note was found makes no difference."]],
  result="The number showed without masking and was hidden with it.", why="Mask when the text goes in, not when it is found. Then every way of finding it is covered."),
"S5": dict(what="An HR person moves to Support and then asks about pay by meaning. Asked when permissions are checked against the copy taken at indexing time, and against the live directory.",
  steps=[["note","The directory changes the moment the person moves. The index copy of who may read what does not."],
         ["miss","If permissions come from the copy, the former HR person still sees HR text."],
         ["stop","If they come from the live directory, they do not."]],
  result="The stale copy still leaked; the live check held.", why="This is round nine's result again, and it holds for search by meaning too: check the live directory, not a copy."),
"S6": dict(what="Two documents are open to everyone: one says who sits on a panel, the other what that panel's members are paid. Asked by meaning how much the named person earns, with all the live checks on.",
  steps=[["note","The staff directory says Meera Iyer sits on the Risk review panel. The panel pay table says its members are paid band 9. Each is fine to read alone."],
         ["note","The question: how much is Meera Iyer paid on the Risk review panel?"],
         ["miss","Meaning search finds both documents, and the answer puts the two facts together. No control here sees it."]],
  result="Not caught. This is a limit.", why="Permissions are checked one document at a time. They cannot see that two harmless documents add up to something that is not harmless."),
}
cases = [{"id": r["id"], "track": r["track"], "title": r["title"], "expected": r["expected"], "actual": r["actual"], "verdict": r["verdict"],
          "expected_in_words": r["expected_in_words"]} for r in rows.values()]
assert set(T) == set(rows), set(T) ^ set(rows)
controls = [
 ("C63", "Permissions are read from the live directory before any document is used, however the document was found (keywords or meaning)", ["S1","S5"], "A.5.15, A.8.3", "AC-3, AC-6", "7.2.1, 7.2.2", "164.312(a)(1)", ""),
 ("C64", "The permission filter runs before the ranking, so restricted documents cannot crowd out what the person may read", ["S3"], "A.8.3", "AC-3", "", "", ""),
 ("C65", "The list of sources follows the person: a title is not shown if the text is not", ["S2"], "A.5.15, A.8.3", "AC-3, SC-4", "7.2.1", "164.312(a)(1)", ""),
 ("C66", "Personal numbers are masked when text is indexed, so they are hidden however the document is found", ["S4"], "A.5.34, A.8.11", "SI-12", "3.4.1", "164.502(b)", "DPDP Act (minimisation, purpose)"),
]
out = {"when": "25 Oct 2026", "round": 13, "run": real["meta"]["run_at_utc"], "cases_sha256": real["meta"]["cases_sha256"], "counts": real["meta"]["counts"],
       "embedder": real["meta"]["embedder"], "machine": real["meta"]["machine"], "python": real["meta"]["python"], "commit": real["meta"]["commit"],
       "failed_first": {"run": failed["meta"]["run_at_utc"], "not_run": failed["meta"]["counts"]["not run"], "seconds": failed["meta"]["seconds"], "good_seconds": real["meta"]["seconds"]},
       "toy": {"run": toy["meta"]["run_at_utc"], "as_expected": toy["meta"]["counts"]["as expected"], "noticed": sum(1 for m in mtoy if m["case_notices"]), "total": len(mtoy)},
       "mutations": {"noticed": sum(1 for m in mut if m["case_notices"]), "total": len(mut), "run": MUT_OK[:15]},
       "bad_mutations": {"run": MUT_BAD[:15], "claimed": sum(1 for m in mbad if m["case_notices"]), "total": len(mbad)},
       "cases": cases, "text": T,
       "controls": [{"id": a, "control": b, "cases": c, "iso27001": d, "nist80053": e, "pci": f, "hipaa": g, "india": h} for a,b,c,d,e,f,g,h in controls]}
open("assets/agl-r13.js", "w").write("/* Round thirteen: 6 cases added on 25 Oct 2026 (search by meaning). Made-up data only. Generated by scripts/build-agl-r13.py */\nwindow.AGL_R13 = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n")
print(len(cases), "cases", len(controls), "controls", out["mutations"], out["toy"])
