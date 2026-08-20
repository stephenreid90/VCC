#!/usr/bin/env python3
"""Generate OPEN_ITEMS.html from design/open_items.json.

The durable successor to ``design/reviews/review_tracker_2026-08-13.html``, which was
tied to one review and would have gone stale the moment anything else was raised.

Items live in ``design/open_items.json``; edit that, then re-run this. Schema per item:

    id         short label, e.g. "12b", "M4", "WC-1"
    source     where it came from, e.g. "fable-2026-08-13", "triage-2026-08-13"
    area       grouping, e.g. "Methodology", "Data", "UI/UX"
    issue      what is wrong (HTML permitted)
    treatment  what we intend to do about it (HTML permitted)
    questions  list of open-question ids that block it, e.g. ["Q3"]
    status     DONE | PLANNED | NEEDS | CLOSED | BACKLOG
    batch      free text, e.g. "Batch 4"

Open questions live in ``design/open_questions.json``: id, question, blocks.

Run::

    python scripts/build_open_items.py
"""

from __future__ import annotations

import datetime as _dt
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ITEMS = ROOT / "design" / "open_items.json"
QUESTIONS = ROOT / "design" / "open_questions.json"
OUT = ROOT / "OPEN_ITEMS.html"

LABEL = {
    "DONE": "Done",
    "PLANNED": "Planned",
    "NEEDS": "Needs Stephen",
    "CLOSED": "Closed",
    "BACKLOG": "Backlog",
}
ORDER = ["NEEDS", "DONE", "PLANNED", "CLOSED", "BACKLOG"]

CSS_FILE = ROOT / "design" / "open_items.css"
# Presentation lives in a stylesheet, not here: the SSOT ratchet scans .py files
# for register values and CSS constants (font weights, line heights, percentages)
# collide with them. Keeping it out of Python keeps the lint signal clean.



def build() -> str:
    items = json.loads(ITEMS.read_text(encoding="utf-8"))
    questions = (
        json.loads(QUESTIONS.read_text(encoding="utf-8")) if QUESTIONS.exists() else []
    )
    now = _dt.date.today().isoformat()
    sources = sorted({i.get("source", "") for i in items if i.get("source")})

    counts = {k: 0 for k in ORDER}
    for i in items:
        counts[i["status"]] = counts.get(i["status"], 0) + 1

    tally = "".join(
        f'<div class="tcard"><div class="n" style="color:var(--'
        f'{ {"NEEDS":"need","DONE":"done","PLANNED":"plan","CLOSED":"closed","BACKLOG":"back"}[k] }-tx);">'
        f'{counts.get(k,0)}</div><div class="l">{LABEL[k]}</div></div>'
        for k in ORDER
    )

    filters = "".join(
        f'<button data-f="{k}" aria-pressed="false">{LABEL[k]}</button>' for k in ORDER
    )
    src_filters = "".join(
        f'<button data-f="src:{html.escape(s)}" aria-pressed="false">{html.escape(s)}</button>'
        for s in sources
    )

    qrows = "".join(
        f'<tr><td class="id"><span class="q">{html.escape(q["id"])}</span></td>'
        f'<td>{q["question"]}</td><td class="sec">{html.escape(q.get("blocks",""))}</td></tr>'
        for q in questions
    )

    return f"""<!DOCTYPE html>
<html lang="en-AU"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VCC — open items</title><style>{CSS_FILE.read_text(encoding="utf-8")}</style></head><body><div class="wrap">
<h1>VCC — open items</h1>
<p class="sub">Generated {now} by <code>scripts/build_open_items.py</code> from
<code>design/open_items.json</code>. Edit the JSON, not this file.</p>
<div class="tally">{tally}</div>
<div class="bar" id="bar">
<button data-f="all" aria-pressed="true">All</button>{filters}{src_filters}
<input type="search" id="q" placeholder="Search…" aria-label="Search items">
<span id="count"></span></div>
<table><thead><tr><th>#</th><th>Area</th><th>Issue</th><th>Proposed treatment</th>
<th>Your input</th><th>Status</th></tr></thead><tbody id="rows"></tbody></table>
<h2>Open questions</h2>
<table><thead><tr><th>Q</th><th>Question</th><th>Blocks</th></tr></thead><tbody>{qrows}</tbody></table>
</div>
<script>
var D={json.dumps(items, ensure_ascii=False)};
var LABEL={json.dumps(LABEL)};
var filter="all", term="";
function render(){{
  var h="", n=0;
  D.forEach(function(r){{
    var ok = filter==="all" || (filter.indexOf("src:")===0 ? r.source===filter.slice(4) : r.status===filter);
    var hay=(r.id+" "+r.area+" "+r.issue+" "+r.treatment+" "+(r.questions||[]).join(" ")).toLowerCase().replace(/<[^>]+>/g,"");
    if(!ok || (term && hay.indexOf(term)<0)) return;
    n++;
    var qs=(r.questions||[]).map(function(x){{return '<span class="q">'+x+'</span>';}}).join("");
    h+='<tr><td class="id">'+r.id+'</td><td class="sec">'+r.area+'</td><td class="issue">'+r.issue+'</td>'
     +'<td class="treat">'+r.treatment+'</td><td class="inp">'+qs+'</td>'
     +'<td class="st"><span class="pill s-'+r.status+'">'+LABEL[r.status]+'</span>'
     +(r.batch?'<span class="batch">'+r.batch+'</span>':'')+'</td></tr>';
  }});
  document.getElementById("rows").innerHTML = h || '<tr><td colspan="6" style="color:var(--text3);padding:20px 12px;">No items match.</td></tr>';
  document.getElementById("count").textContent = n+" of "+D.length+" items";
}}
Array.prototype.forEach.call(document.querySelectorAll("#bar button"),function(b){{
  b.addEventListener("click",function(){{
    Array.prototype.forEach.call(document.querySelectorAll("#bar button"),function(o){{o.setAttribute("aria-pressed","false");}});
    b.setAttribute("aria-pressed","true"); filter=b.getAttribute("data-f"); render();
  }});
}});
document.getElementById("q").addEventListener("input",function(){{term=this.value.toLowerCase();render();}});
render();
</script></body></html>
"""


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"OPEN_ITEMS.html written from {ITEMS.name}")
