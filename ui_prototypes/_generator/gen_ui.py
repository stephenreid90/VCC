# -*- coding: utf-8 -*-
import json, re, sys, os

SCAFFOLD = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VCC scenario valuation — __COMPANY__ (prototype)</title>
<style>
:root{ --bg:#faf9f5; --primary:#fff; --secondary:#f1efe8; --tertiary:#e8e6dd; --text:#1f1e1b; --text2:#5f5e5a; --text3:#8a8980; --bd:rgba(0,0,0,0.12); --bd2:rgba(0,0,0,0.24); --bdinfo:#378ADD; --info-bg:#E6F1FB; --info-tx:#0C447C; --success-bg:#E1F5EE; --success-tx:#0F6E56; --warning-bg:#FAEEDA; --warning-tx:#854F0B; --danger-bg:#FCEBEB; --danger-tx:#A32D2D; --rmd:8px; --rlg:12px; }
@media (prefers-color-scheme: dark){ :root{ --bg:#1a1916; --primary:#24231f; --secondary:#2c2b27; --tertiary:#34332e; --text:#f2f1ec; --text2:#b6b4ab; --text3:#88867e; --bd:rgba(255,255,255,0.14); --bd2:rgba(255,255,255,0.26); --info-bg:#0C447C; --info-tx:#B5D4F4; --success-bg:#085041; --success-tx:#9FE1CB; --warning-bg:#633806; --warning-tx:#FAC775; --danger-bg:#791F1F; --danger-tx:#F7C1C1; } }
*{box-sizing:border-box;}
body{margin:0; background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; line-height:1.6;}
.wrap{max-width:880px; margin:0 auto; padding:24px 20px 60px;}
.card{background:var(--primary); border:0.5px solid var(--bd); border-radius:var(--rlg);}
.metric{background:var(--secondary); border-radius:var(--rmd); padding:1rem;}
button{font:inherit; background:transparent; color:var(--text); border:0.5px solid var(--bd2); border-radius:var(--rmd); padding:5px 10px; cursor:pointer;}
button:hover{background:var(--secondary);}
input[type=range]{width:100%; accent-color:var(--bdinfo);}
table{border-collapse:collapse;}
.more{color:var(--info-tx); cursor:pointer; font-weight:500;}
.hd{font-size:14px; font-weight:500;} .sub{font-size:11px; color:var(--text3);}
.detailcard{background:var(--primary); border:0.5px solid var(--bd); border-left:2.5px solid var(--bdinfo); border-radius:var(--rmd); padding:1rem 1.15rem; margin-top:10px; font-size:13px; line-height:1.65;}
.detailcard h4{margin:0; font-size:15px; font-weight:600;}
details.thy{border:0.5px solid var(--bd); border-radius:var(--rmd); margin-top:7px; background:var(--secondary);}
details.thy>summary{cursor:pointer; padding:7px 10px; font-size:12.5px; font-weight:500; list-style:none;}
details.thy>summary::-webkit-details-marker{display:none;}
details.thy>summary::before{content:"\25B8"; color:var(--text3); display:inline-block; width:1em;}
details.thy[open]>summary::before{content:"\25BE";}
details.thy .thybody{padding:2px 12px 11px 22px; font-size:12.5px;}
.thytag{font-size:10.5px; font-weight:600; letter-spacing:.03em; text-transform:uppercase;}
</style></head>
<body><div class="wrap">
<div style="display:flex; justify-content:space-between; align-items:baseline; flex-wrap:wrap; gap:8px; margin-bottom:4px;">
  <div style="font-size:20px; font-weight:600;">VCC scenario valuation</div>
  <div style="font-size:13px; color:var(--text2);">__COMPANY__ · exploring: <span id="selscen" style="color:var(--text); font-weight:500;"></span> · __CCYNOTE__</div>
</div>
<div class="sub" id="topnote" style="margin-bottom:18px;"></div>
<div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin-bottom:1.5rem;">
  <div class="metric"><div style="font-size:13px; color:var(--text2);">Value per share</div><div style="font-size:24px; font-weight:600;"><span id="pv"></span><span style="font-size:13px; color:var(--text2);"> __CCY__</span></div><div style="font-size:12px; color:var(--text3);" id="pvsub"></div></div>
  <div class="metric"><div style="font-size:13px; color:var(--text2);" id="mklab"></div><div style="font-size:24px; font-weight:600;" id="vmkt"></div></div>
  <div class="metric"><div style="font-size:13px; color:var(--text2);" id="brlab"></div><div style="font-size:24px; font-weight:600;" id="vbr"></div></div>
  <div class="metric"><div style="font-size:13px; color:var(--text2);" id="m4lab"></div><div style="font-size:24px; font-weight:600;" id="m4val"></div></div>
</div>
<div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:1.5rem; margin-bottom:1.5rem;">
  <div><div class="hd">Top 5 value drivers <span style="font-weight:400; color:var(--text3); font-size:12px;">— flex to see impact</span></div>
    <div class="sub" style="margin-bottom:6px;">illustrative response · full set under Assumptions</div>
    <div id="sliders"></div>
    <div style="display:flex; gap:8px; margin-top:8px;"><button id="reset">↻ reset</button><button id="allassum">all assumptions &amp; rationale</button></div></div>
  <div><div class="hd">Outcomes across scenarios <span style="font-weight:400; color:var(--text3); font-size:12px;">(__CCY__/share)</span></div>
    <div class="sub" style="margin-bottom:6px;">click a scenario to explore its build-up</div>
    <div id="bars"></div>
    <div class="sub" style="margin-top:6px;"><span style="color:var(--info-tx);">▮</span> Muddle Through (live) · <span style="color:var(--warning-tx);">▮</span> average broker · dashed = market</div></div>
</div>
<div style="border-top:0.5px solid var(--bd); padding-top:1rem;">
  <div class="hd" style="margin-bottom:8px;">Explore the build-up</div>
  <div id="explore" style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:12px;"></div>
  <div id="panel" class="metric" style="min-height:110px; font-size:13px;"></div>
  <div id="detail"></div></div>
<div class="sub" id="footnote" style="margin-top:28px; border-top:0.5px solid var(--bd); padding-top:12px;"></div>
</div>
<script>
var CFG=__CFG__;
(function(){
  var st={}; CFG.sliders.forEach(function(s){ st[s.k]=s.def; });
  function fmt(s,v){ return v.toFixed(s.dec)+s.suf; }
  function val(k){ return st[k]; }
  function compute(){
    var p=CFG.cp, Re=val('re')/100, g=val('g')/100, m=val('m'), tax=val('tax')/100, x=val(p.xKey);
    var term=Math.pow((p.re0-p.g0)/(Re-g), p.wTerm);
    var primary=p.base*term*(m/p.m0)*((1-tax)/(1-p.tax0))*(1+(x-p.x0)*p.xk);
    return primary;
  }
  function render(){
    var v=compute();
    document.getElementById('pv').textContent=v.toFixed(CFG.dp);
    var vm=(v/CFG.market-1)*100, vb=(v/CFG.broker-1)*100;
    var em=document.getElementById('vmkt'); em.textContent=(vm>=0?'+':'')+vm.toFixed(0)+'%'; em.style.color=vm>=0?'var(--success-tx)':'var(--danger-tx)';
    document.getElementById('vbr').textContent=(vb>=0?'+':'')+vb.toFixed(0)+'%';
    CFG.scenarios[CFG.liveIdx].v=v; drawBars();
  }
  function barColor(k){ return k==='live'?'var(--info-bg)':k==='broker'?'var(--warning-bg)':'var(--tertiary)'; }
  function txtColor(k){ return k==='live'?'var(--info-tx)':k==='broker'?'var(--warning-tx)':'var(--text)'; }
  function drawBars(){
    var h='<div style="position:relative;">', mkt=CFG.market/CFG.scale*100;
    CFG.scenarios.forEach(function(s,i){
      var w=Math.min(100,s.v/CFG.scale*100), sel=(i===CFG.activeIdx);
      h+='<div data-i="'+i+'" class="scbar" style="display:flex; align-items:center; gap:8px; margin-bottom:5px; cursor:pointer; border-radius:5px; padding:1px 2px; '+(sel?'background:var(--secondary);':'')+'">'
       +'<div style="width:122px; font-size:12px; color:'+(sel?'var(--text)':'var(--text2)')+'; font-weight:'+(sel?'500':'400')+'; text-align:right; flex:none;">'+s.n+'</div>'
       +'<div style="flex:1; position:relative; height:19px;"><div style="height:19px; width:'+w+'%; background:'+barColor(s.kind)+'; border-radius:4px; '+(sel?'outline:1.5px solid var(--bdinfo);':'')+'"></div>'
       +'<div style="position:absolute; top:1px; left:calc('+w+'% + 6px); font-size:12px; font-weight:500; color:'+txtColor(s.kind)+'; white-space:nowrap;">'+s.v.toFixed(CFG.dp)+'</div></div></div>';
    });
    h+='<div style="position:absolute; left:130px; right:0; top:0; bottom:14px; pointer-events:none;"><div style="position:absolute; left:'+mkt+'%; top:0; bottom:0; border-left:1.5px dashed var(--text2);"></div></div></div>';
    var bx=document.getElementById('bars'); bx.innerHTML=h;
    Array.prototype.forEach.call(bx.querySelectorAll('.scbar'),function(el){ el.addEventListener('click',function(){ CFG.activeIdx=parseInt(el.getAttribute('data-i')); document.getElementById('selscen').textContent=CFG.scenarios[CFG.activeIdx].n; drawBars(); setPanel('world'); markExplore('world'); }); });
  }
  var sl=document.getElementById('sliders');
  CFG.sliders.forEach(function(s){
    var row=document.createElement('div'); row.style.margin='10px 0';
    row.innerHTML='<div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;"><span style="color:var(--text2);">'+s.label+'</span><span style="font-weight:500;" id="o_'+s.k+'"></span></div>';
    var inp=document.createElement('input'); inp.type='range'; inp.min=s.min; inp.max=s.max; inp.step=s.step; inp.value=st[s.k];
    inp.addEventListener('input',function(){ st[s.k]=parseFloat(inp.value); document.getElementById('o_'+s.k).textContent=fmt(s,st[s.k]); render(); });
    row.appendChild(inp); sl.appendChild(row); document.getElementById('o_'+s.k).textContent=fmt(s,st[s.k]);
  });
  document.getElementById('reset').addEventListener('click',function(){ CFG.sliders.forEach(function(s){ st[s.k]=s.def; }); sl.querySelectorAll('input').forEach(function(inp,i){ inp.value=st[CFG.sliders[i].k]; document.getElementById('o_'+CFG.sliders[i].k).textContent=fmt(CFG.sliders[i],st[CFG.sliders[i].k]); }); render(); });
  document.getElementById('allassum').addEventListener('click',function(){ setPanel('assum'); markExplore('assum'); openDetail('assum'); });

  var ex=document.getElementById('explore'); var exBtns={};
  Object.keys(CFG.titles).forEach(function(k){ var b=document.createElement('button'); b.textContent=CFG.titles[k]; b.style.fontSize='12px'; b.addEventListener('click',function(){ setPanel(k); markExplore(k); }); ex.appendChild(b); exBtns[k]=b; });
  function markExplore(k){ Object.keys(exBtns).forEach(function(j){ exBtns[j].style.borderColor='var(--bd2)'; }); if(exBtns[k]) exBtns[k].style.borderColor='var(--bdinfo)'; }
  function setPanel(k){
    var d=document.getElementById('detail'); if(d) d.innerHTML='';
    document.getElementById('panel').innerHTML='<div style="font-weight:500; margin-bottom:4px;">'+CFG.titles[k]+'</div><div style="color:var(--text2);">'+CFG.snap[k]+'</div>';
    if(k==='world'){ var t=document.getElementById('wsnaptitle'); if(t) t.textContent=CFG.scenarios[CFG.activeIdx].n; }
    var m=document.querySelector('#panel .more'); if(m){ m.addEventListener('click',function(){ openDetail(m.getAttribute('data-k')); }); }
  }
  function detailHTML(k){
    if(k==='world'){ var nm=CFG.scenarios[CFG.activeIdx].n;
      var wd=(CFG.worldDesc&&CFG.worldDesc[nm])?'<div class="thytag" style="color:var(--text3); margin:0 0 4px;">The world</div>'+CFG.worldDesc[nm]:'';
      var cn='<div class="thytag" style="color:var(--text3); margin:14px 0 4px;">What it means for '+CFG.companyShort+'</div>'+(CFG.narr[nm]||CFG.narr._placeholder);
      return wd+cn; }
    if(k==='dcf'){ return CFG.dcf+'<button style="margin-top:12px; font-size:13px; padding:6px 12px;" id="dlbtn">⤓ download all scenarios to Excel</button><div style="font-size:11px; color:var(--text3); margin-top:4px;">one tab per scenario</div>'; }
    return CFG.detail[k]||'';
  }
  function openDetail(k){
    var d=document.getElementById('detail');
    d.innerHTML='<div class="detailcard"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;"><h4>'+CFG.titles[k]+'</h4><button id="closeov" aria-label="close" style="padding:2px 9px;">×</button></div><div>'+detailHTML(k)+'</div></div>';
    document.getElementById('closeov').addEventListener('click',function(){ d.innerHTML=''; });
    var dl=document.getElementById('dlbtn'); if(dl) dl.addEventListener('click',function(){ alert('In the live tool this downloads the '+CFG.companyShort+' scenario workbook — one tab per scenario.'); });
    d.scrollIntoView({behavior:'smooth', block:'nearest'});
  }
  document.getElementById('selscen').textContent=CFG.scenarios[CFG.liveIdx].n;
  document.getElementById('topnote').innerHTML=CFG.topnote;
  document.getElementById('footnote').innerHTML=CFG.footnote;
  document.getElementById('mklab').textContent=CFG.mklab;
  document.getElementById('brlab').textContent=CFG.brlab;
  document.getElementById('m4lab').textContent=CFG.metric4.label;
  document.getElementById('m4val').textContent=CFG.metric4.value;
  if(CFG.pvsub) document.getElementById('pvsub').textContent=CFG.pvsub;
  setPanel('forces'); markExplore('forces'); render();
})();
</script></body></html>"""

def tag(t):
    m={'disclosed':'success','derived':'info','judgment':'warning'}; c=m[t]
    return '<span style="font-size:11px; padding:1px 7px; border-radius:6px; background:var(--%s-bg); color:var(--%s-tx);">%s</span>'%(c,c,t)
def posbadge(p):
    if p=='more favourable': bg,tx='var(--success-bg)','var(--success-tx)'
    elif p=='less favourable': bg,tx='var(--danger-bg)','var(--danger-tx)'
    else: bg,tx='var(--secondary)','var(--text2)'
    return '<span style="font-size:11px; padding:1px 7px; border-radius:6px; background:%s; color:%s;">%s</span>'%(bg,tx,p)
def forces_table(intro, rows, net):
    # rows: [force, industry_rating, industry_rationale, position, impact, mechanism]
    h='<p>%s</p><table style="width:100%%; font-size:13px;"><tr><td class="sub" style="padding:4px 8px 4px 0;">Force</td><td class="sub" style="padding:4px 8px;">Industry (rating &amp; why)</td><td class="sub" style="padding:4px 8px;">Company vs industry</td><td class="sub" style="padding:4px 0; text-align:right;">Impact</td></tr>'%intro
    for r in rows:
        h+='<tr style="border-top:0.5px solid var(--bd);"><td style="padding:7px 8px 7px 0; font-weight:500; white-space:nowrap; vertical-align:top;">%s</td><td style="padding:7px 8px; vertical-align:top; max-width:220px;"><span style="font-weight:500;">%s</span><div style="color:var(--text2); margin-top:2px; font-size:12px;">%s</div></td><td style="padding:7px 8px; vertical-align:top;">%s<div style="color:var(--text2); margin-top:3px; font-size:12px;">%s</div></td><td style="padding:7px 0 7px 8px; text-align:right; font-weight:500; vertical-align:top; white-space:nowrap;">%s</td></tr>'%(r[0],r[1],r[2],posbadge(r[3]),r[5],r[4])
    h+='</table><div style="margin-top:10px; background:var(--secondary); border-radius:8px; padding:10px;"><b>Net company offset:</b> %s</div>'%net
    return h
def dr_theory_html(rows):
    # rows: [label, proper, ier, did]
    h='<div style="margin-top:12px; border-top:0.5px solid var(--bd); padding-top:10px;"><div class="hd" style="margin-bottom:2px;">Practical theory — the proper approach vs what we did</div><div class="sub" style="margin-bottom:6px;">click any element to compare the textbook approach with what this valuation did</div>'
    for r in rows:
        h+='<details class="thy"><summary>%s</summary><div class="thybody">'%r[0]
        h+='<div class="thytag" style="color:var(--success-tx);">The proper approach</div><div style="margin:2px 0 8px;">%s</div>'%r[1]
        h+='<div class="thytag" style="color:var(--info-tx);">In market practice</div><div style="margin:2px 0 8px; color:var(--text2);">%s</div>'%r[2]
        h+='<div class="thytag" style="color:var(--warning-tx);">What we did (VCC)</div><div style="margin:2px 0 0;">%s</div>'%r[3]
        h+='</div></details>'
    return h+'</div>'

def assum_table(rows):
    h='<p>Tags: %s stated · %s calculated · %s analyst call.</p><table style="width:100%%; font-size:13px;">'%(tag('disclosed'),tag('derived'),tag('judgment'))
    for r in rows:
        h+='<tr style="border-bottom:0.5px solid var(--bd);"><td style="padding:6px 8px 6px 0; font-weight:500; white-space:nowrap; vertical-align:top;">%s</td><td style="padding:6px 8px; white-space:nowrap; vertical-align:top;">%s</td><td style="padding:6px 8px; vertical-align:top;">%s</td><td style="padding:6px 0; color:var(--text2); vertical-align:top;">%s</td></tr>'%(r[0],r[1],tag(r[2]),r[3])
    return h+'</table>'

OUTDIR=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CFGS=json.load(open('/tmp/cfgs.json'))
for key,cfg in CFGS.items():
    cfg['detail']={
        'forces': forces_table(cfg['_forces']['intro'], cfg['_forces']['rows'], cfg['_forces']['net']),
        'position': cfg['_position'],
        'discount': cfg['_discount'] + dr_theory_html(cfg.get('_drtheory', [])),
        'assum': assum_table(cfg['_assum'])
    }
    for kk in ['_forces','_position','_discount','_assum','_drtheory']: cfg.pop(kk, None)
    html=SCAFFOLD.replace('__CFG__', json.dumps(cfg)).replace('__COMPANY__', cfg['company']).replace('__CCYNOTE__', cfg['ccynote']).replace('__CCY__', cfg['ccy'])
    out=os.path.join(OUTDIR, '%s_scenario_interface.html'%key)
    open(out,'w',encoding='utf-8').write(html)
    print('wrote',out,len(html),'bytes')
