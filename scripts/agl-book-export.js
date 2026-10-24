// Dumps the lab data the book needs as JSON (run with node, prints to stdout).
global.window = {};
const path = require("path");
const a = path.join(__dirname, "..", "assets");
require(path.join(a, "agl-data.js"));
require(path.join(a, "agl-cases.js"));
const F = require(path.join(a, "agl-try-filters.js")) || window.AGLF;
const AGLF = window.AGLF || F;
const D = window.AGL, C = window.AGL_CASES;
const order = {};
[1, 2, 3, 4].forEach(r => D.cases[r].forEach(c => { (order[c.id] = order[c.id] || { id: c.id, track: c.track, title: c.title, rounds: {} }).rounds[r] = { expected: c.expected, actual: c.actual, verdict: c.verdict }; }));
const V = AGLF.variants(11);
const variants = {};
V.forEach(v => { (variants[v.id] = variants[v.id] || []).push({ name: v.name, v1: AGLF.judge(AGLF.detectors.v1, v), v2: AGLF.judge(AGLF.detectors.v2, v), v3: AGLF.judge(AGLF.detectors.v3, v) }); });
console.log(JSON.stringify({ cases: Object.values(order), steps: C, variants, controls: D.controls, trackp: D.trackp, held: D.held, rounds: D.rounds, stages: D.stages, modules: D.modules }));
