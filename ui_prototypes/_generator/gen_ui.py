# -*- coding: utf-8 -*-
import json, re, sys, os

SCAFFOLD = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VCC scenario valuation — __COMPANY__ (prototype)</title>
<style>
:root{ --bg:#faf9f5; --primary:#fff; --secondary:#f1efe8; --tertiary:#e8e6dd; --text:#1f1e1b; --text2:#5f5e5a; --text3:#8a8980; --bd:rgba(0,0,0,0.12); --bd2:rgba(0,0,0,0.24); --bdinfo:#378ADD; --info-bg:#E6F1FB; --info-tx:#0C447C; --success-bg:#E1F5EE; --success-tx:#0F6E56; --warning-bg:#FAEEDA; --warning-tx:#854F0B; --danger-bg:#FCEBEB; --danger-tx:#A32D2D; --user-bg:#ECE6FA; --user-tx:#5B3FA8; --rmd:8px; --rlg:12px; }
@media (prefers-color-scheme: dark){ :root{ --bg:#1a1916; --primary:#24231f; --secondary:#2c2b27; --tertiary:#34332e; --text:#f2f1ec; --text2:#b6b4ab; --text3:#88867e; --bd:rgba(255,255,255,0.14); --bd2:rgba(255,255,255,0.26); --info-bg:#0C447C; --info-tx:#B5D4F4; --success-bg:#085041; --success-tx:#9FE1CB; --warning-bg:#633806; --warning-tx:#FAC775; --danger-bg:#791F1F; --danger-tx:#F7C1C1; --user-bg:#3A2E63; --user-tx:#C9B8F2; } }
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
  <div class="metric"><div style="font-size:13px; color:var(--text2);">Discount rate</div><div style="font-size:24px; font-weight:600;"><span id="wacchip"></span></div><div style="font-size:12px; color:var(--text3);" id="waccsub"></div></div>
</div>
<div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:1.5rem; margin-bottom:1.5rem;">
  <div><div class="hd">Top 5 value drivers <span style="font-weight:400; color:var(--text3); font-size:12px;">— flex to see impact</span></div>
    <div class="sub" style="margin-bottom:6px;">illustrative response · full set under Assumptions</div>
    <div id="sliders"></div>
    <div style="display:flex; gap:8px; margin-top:8px;"><button id="reset">↻ reset</button><button id="allassum">all assumptions &amp; rationale</button></div>
    <label style="display:flex; align-items:center; gap:6px; margin-top:8px; font-size:12px; color:var(--text2); cursor:pointer;"><input type="checkbox" id="applyall" style="accent-color:var(--bdinfo);"> apply input changes to <b>&nbsp;all editable scenarios&nbsp;</b> (global), not just this one</label></div>
  <div><div class="hd">Outcomes across scenarios <span style="font-weight:400; color:var(--text3); font-size:12px;">(__CCY__/share)</span></div>
    <div class="sub" style="margin-bottom:6px;">click a scenario to explore its build-up</div>
    <div id="bars"></div>
    <div style="display:flex; align-items:center; gap:10px; margin-top:8px; flex-wrap:wrap;"><button id="addscen" style="font-size:12px;">+ add your scenario</button><span class="sub" id="editing"></span></div>
    <div class="sub" style="margin-top:6px;"><span style="color:var(--info-tx);">▮</span> Muddle Through · <span style="color:var(--user-tx);">▮</span> your scenarios · <span style="color:var(--warning-tx);">▮</span> average broker · dashed = market</div></div>
</div>
<div style="border-top:0.5px solid var(--bd); padding-top:1rem;">
  <div class="hd" style="margin-bottom:8px;">Explore the build-up for the selected scenario</div>
  <div id="explore" style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:12px;"></div>
  <div id="panel"></div>
  <div id="detail"></div></div>
<div class="sub" id="footnote" style="margin-top:28px; border-top:0.5px solid var(--bd); padding-top:12px;"></div>
</div>
<script>
var CFG=__CFG__;

/* The self-contained xlsx writer (VCCXLSX), the generic workbook builder
   (VCCBOOK) and the DNL rich book (DNLRICH) were removed on 23 Aug 2026.
   Every company now ships a pre-built, formula-linked workbook as CFG.xlsxB64,
   generated by engine_workbook.py, so vccDownload() returned before it ever
   reached them - roughly 435 lines and 32 KB inlined into every page for a
   path no company took. The pre-built book is also the better artefact: it is
   formulas linking to an Assumptions sheet rather than pasted values. */


// ===== VCC formula-workbook download (self-contained; DNL gets the rich book) =====
function vccDownload(){ try{
  if(CFG.xlsxB64){
    var _bin=atob(CFG.xlsxB64), _n=_bin.length, _arr=new Uint8Array(_n);
    for(var _i=0;_i<_n;_i++){ _arr[_i]=_bin.charCodeAt(_i); }
    var _b=new Blob([_arr],{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
    var _u=URL.createObjectURL(_b), _a=document.createElement('a');
    _a.href=_u; _a.download=CFG.xlsxName||(CFG.companyShort+'_workbook.xlsx'); document.body.appendChild(_a); _a.click();
    setTimeout(function(){ URL.revokeObjectURL(_u); if(_a.parentNode) _a.parentNode.removeChild(_a); },1500);
    return;
  }
  // No pre-built workbook means the build step failed, which is worth saying out
  // loud rather than handing the reader a silent no-op.
  throw new Error('no pre-built workbook embedded for '+CFG.companyShort);
}catch(e){ alert('Workbook export failed: '+(e&&e.message?e.message:e)); } }

(function(){
  var LS='vcc_ws_'+CFG.companyShort;
  var applyGlobal=false;
  var singleWacc=CFG.cp.re0*100;
  function defaultVals(){ var o={}; CFG.sliders.forEach(function(s){ o[s.k]=s.def; }); return o; }
  function sliderByKey(k){ for(var i=0;i<CFG.sliders.length;i++){ if(CFG.sliders[i].k===k) return CFG.sliders[i]; } return null; }
  function activeScen(){ return CFG.scenarios[CFG.activeIdx]; }
  function fmt(s,v){ return v.toFixed(s.dec)+s.suf; }
  function computeVals(vals){ var p=CFG.cp, Re=vals.re/100, g=vals.g/100, m=vals.m, tax=vals.tax/100, x=vals[p.xKey];
    var term=Math.pow((p.re0-p.g0)/(Re-g), p.wTerm);
    return p.base*term*(m/p.m0)*((1-tax)/(1-p.tax0))*(1+(x-p.x0)*p.xk); }
  function ratio(vals){ return computeVals(vals)/CFG.cp.base; }
  function _pvAvg(path, reFrac){ var num=0, den=0; for(var i=0;i<path.length;i++){ var df=Math.pow(1+reFrac,-(i+0.5)); num+=path[i]*df; den+=df; } return den? num/den : 0; }
  function _effBps(imp, reFrac){ if(!imp) return 0; if(imp.path) return _pvAvg(imp.path, reFrac); return imp.bps||0; }
  function _parseBps(v, fb){ if(v===undefined||v===null||v==='') return fb; if(Array.isArray(v)) return null; var f=parseFloat(String(v).replace(/\u2212/g,'-').replace(/[^0-9.+-]/g,'')); return isNaN(f)? fb : f; }
  // Five-Forces -> driver offsets (delta from the assessed impact, so leaving cells untouched moves nothing).
  function forcesOffsets(sc){ var out={}; var fd=CFG.forcesData, imp=fd&&fd.impacts; if(!imp||sc.kind==='broker') return out;
    var reFrac=((sc.vals&&sc.vals.re!=null)?sc.vals.re:singleWacc)/100, xKey=CFG.cp.xKey, xk=CFG.cp.xk;
    imp.forEach(function(m,i){ if(!m||!m.drv) return; var assessed=_effBps(m, reFrac);
      var ov=(sc.forces&&sc.forces[i]!==undefined)?sc.forces[i]:null, user;
      if(ov===null) user=assessed; else if(Array.isArray(ov)) user=_pvAvg(ov, reFrac); else user=_parseBps(ov, assessed);
      var d=user-assessed; if(!d) return;
      var dv=(m.drv===xKey)? d*(xk<0?-1:1) : d/100; out[m.drv]=(out[m.drv]||0)+dv; });
    return out; }
  function valsWithForces(sc){ var off=forcesOffsets(sc); var v={}; for(var k in sc.vals){ v[k]=sc.vals[k]; }
    for(var key in off){ v[key]=(v[key]!=null?v[key]:0)+off[key]; } return v; }
  function scVal(sc){ return (sc.kind==='broker')? sc.v : sc.anchor*ratio(valsWithForces(sc)); }
  function editableScens(){ return CFG.scenarios.filter(function(sc){ return sc.kind!=='broker'; }); }
  function isOverridden(sc){ if(sc.kind==='broker') return false; var d=defaultVals(); for(var i=0;i<CFG.sliders.length;i++){ var k=CFG.sliders[i].k; if(sc.vals[k]!==d[k]) return true; } for(var f in (sc.forces||{})){ if(sc.forces.hasOwnProperty(f)) return true; } return false; }

  // ---- persistence: user scenarios + world-case overrides, per company ----
  function loadLS(){ try{ return JSON.parse(localStorage.getItem(LS))||{}; }catch(e){ return {}; } }
  function saveLS(){ var us=[], wo={};
    CFG.scenarios.forEach(function(sc){ if(sc.kind==='user'){ us.push({id:sc.uid,name:sc.n,vals:sc.vals,forces:sc.forces||{}}); }
      else if(sc.kind!=='broker' && isOverridden(sc)){ wo[sc.n]={vals:sc.vals,forces:sc.forces||{}}; } });
    try{ localStorage.setItem(LS, JSON.stringify({user:us, world:wo})); }catch(e){} }
  var _stored=loadLS(); var _ust=_stored.user||[]; var _wov=_stored.world||{};

  // ---- initialise every scenario with an anchor (its assessed value) + an editable input set ----
  CFG.scenarios.forEach(function(sc){ if(sc.kind==='broker') return;
    sc.anchor=sc.v; var ov=_wov[sc.n]||{}; sc.vals=ov.vals||defaultVals(); sc.forces=ov.forces||{}; sc.v=scVal(sc); });
  _ust.forEach(function(u){ var sc={n:u.name, kind:'user', uid:u.id, anchor:CFG.cp.base, vals:u.vals||defaultVals(), forces:u.forces||{}}; sc.v=scVal(sc); CFG.scenarios.push(sc); });

  function updateCards(v){ var sc=activeScen(); var show=(v!==undefined&&v!==null)?v:sc.v;
    document.getElementById('pv').textContent=show.toFixed(CFG.dp);
    var vm=(show/CFG.market-1)*100, vb=(show/CFG.broker-1)*100;
    var em=document.getElementById('vmkt'); em.textContent=(vm>=0?'+':'')+vm.toFixed(0)+'%'; em.style.color=vm>=0?'var(--success-tx)':'var(--danger-tx)';
    document.getElementById('vbr').textContent=(vb>=0?'+':'')+vb.toFixed(0)+'%'; }
  function render(){ var a=activeScen(); if(a.kind!=='broker') a.v=scVal(a); updateCards(a.v); drawBars(); }
  function updateWacc(){ var el=document.getElementById('wacchip'); if(el) el.textContent=singleWacc.toFixed(2)+'%'; var sub=document.getElementById('waccsub'); if(sub) sub.textContent='single '+((CFG.beta&&CFG.beta.toDiscount&&CFG.beta.toDiscount.label)||'WACC')+' · all scenarios'; }

  // ---- one input change on the active scenario; global => every editable scenario ----
  function setInput(k,v){ var a=activeScen(); if(a.kind==='broker') return;
    if(k==='re' && applyGlobal){ singleWacc=v; }
    if(applyGlobal){ editableScens().forEach(function(sc){ sc.vals[k]=v; sc.v=scVal(sc); }); }
    else { a.vals[k]=v; a.v=scVal(a); }
    saveLS(); syncSliders(); updateCards(activeScen().v); drawBars(); }

  function barColor(k){ return k==='live'?'var(--info-bg)':k==='broker'?'var(--warning-bg)':k==='user'?'var(--user-bg)':'var(--tertiary)'; }
  function txtColor(k){ return k==='live'?'var(--info-tx)':k==='broker'?'var(--warning-tx)':k==='user'?'var(--user-tx)':'var(--text)'; }
  function drawBars(){ var h='<div style="position:relative;">', mkt=CFG.market/CFG.scale*100;
    CFG.scenarios.forEach(function(s,i){ var w=Math.max(0,Math.min(100,s.v/CFG.scale*100)), sel=(i===CFG.activeIdx);
      var od=(s.kind!=='broker'&&isOverridden(s))?'<span title="adjusted from the assessed case" style="color:var(--user-tx);"> ✎</span>':'';
      var del=(s.kind==='user')?'<span class="delu" data-uid="'+s.uid+'" title="delete scenario" style="cursor:pointer; color:var(--text3); padding:0 3px;">×</span>':'';
      var wr=(s.kind!=='broker'&&s.vals&&Math.abs((s.vals.re!=null?s.vals.re:singleWacc)-singleWacc)>1e-9)?'<span title="per-scenario discount-rate override — differs from the single WACC" style="color:var(--warning-tx); font-weight:500; font-size:11px;"> · r '+s.vals.re.toFixed(2)+'%</span>':'';
      h+='<div class="scbar" data-i="'+i+'" style="display:flex; align-items:center; gap:8px; margin-bottom:5px; cursor:pointer; border-radius:5px; padding:1px 2px; '+(sel?'background:var(--secondary);':'')+'">'
       +'<div style="width:122px; font-size:12px; color:'+(sel?'var(--text)':'var(--text2)')+'; font-weight:'+(sel?'500':'400')+'; text-align:right; flex:none; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">'+del+esc(s.n)+od+'</div>'
       +'<div style="flex:1; position:relative; height:19px;"><div style="height:19px; width:'+w+'%; background:'+barColor(s.kind)+'; border-radius:4px; '+(sel?'outline:1.5px solid var(--bdinfo);':'')+'"></div>'
       +'<div style="position:absolute; top:1px; left:calc('+w+'% + 6px); font-size:12px; font-weight:500; color:'+txtColor(s.kind)+'; white-space:nowrap;">'+s.v.toFixed(CFG.dp)+wr+'</div></div></div>';
    });
    h+='<div style="position:absolute; left:130px; right:0; top:0; bottom:14px; pointer-events:none;"><div style="position:absolute; left:'+mkt+'%; top:0; bottom:0; border-left:1.5px dashed var(--text2);"></div></div></div>';
    var bx=document.getElementById('bars'); bx.innerHTML=h;
    Array.prototype.forEach.call(bx.querySelectorAll('.scbar'),function(el){ el.addEventListener('click',function(){ selectBar(parseInt(el.getAttribute('data-i'))); }); });
    Array.prototype.forEach.call(bx.querySelectorAll('.delu'),function(el){ el.addEventListener('click',function(ev){ ev.stopPropagation(); delScenario(el.getAttribute('data-uid')); }); });
    updateWacc();
  }

  function selectScenario(i){ CFG.activeIdx=i; var sc=CFG.scenarios[i];
    if(sc.kind!=='broker'){ st=sc.vals; slidersEnabled(true); syncSliders(); } else { slidersEnabled(false); }
    document.getElementById('selscen').textContent=sc.n; updateEditingUI(); updateCards(sc.v); drawBars(); }
  function selectBar(i){ selectScenario(i); markExplore('world'); openDetail('world'); }

  // sliders (edit the active scenario's vals)
  var st=defaultVals();
  var sl=document.getElementById('sliders'); var inputs={};
  CFG.sliders.forEach(function(s){ var row=document.createElement('div'); row.style.margin='10px 0';
    row.innerHTML='<div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;"><span style="color:var(--text2);">'+s.label+'</span><span style="font-weight:500;" id="o_'+s.k+'"></span></div>';
    var inp=document.createElement('input'); inp.type='range'; inp.min=s.min; inp.max=s.max; inp.step=s.step; inp.value=st[s.k];
    inp.addEventListener('input',function(){ setInput(s.k, parseFloat(inp.value)); });
    row.appendChild(inp); sl.appendChild(row); inputs[s.k]=inp; document.getElementById('o_'+s.k).textContent=fmt(s,st[s.k]); });
  function syncSliders(){ CFG.sliders.forEach(function(s){ inputs[s.k].value=st[s.k]; var o=document.getElementById('o_'+s.k); if(o) o.textContent=fmt(s,st[s.k]); }); }
  function slidersEnabled(on){ sl.style.opacity=on?'1':'0.45'; sl.style.pointerEvents=on?'auto':'none'; }
  function updateEditingUI(){ var e=document.getElementById('editing'); if(!e) return; var sc=activeScen();
    if(sc.kind==='broker') e.innerHTML='<b>'+esc(sc.n)+'</b> — reference line, not editable';
    else if(sc.kind==='user') e.innerHTML='editing your scenario <b>'+esc(sc.n)+'</b> — changes save in this browser';
    else e.innerHTML='editing <b>'+esc(sc.n)+'</b> (our assessed case) — flex any input; ↻ reset restores it'; }

  document.getElementById('reset').addEventListener('click',function(){ var a=activeScen(); if(a.kind==='broker') return; a.vals=defaultVals(); a.forces={}; a.v=scVal(a); st=a.vals; saveLS(); syncSliders(); updateCards(a.v); drawBars(); });
  document.getElementById('allassum').addEventListener('click',function(){ setPanel('assum'); markExplore('assum'); openDetail('assum'); });
  document.getElementById('applyall').addEventListener('change',function(){ applyGlobal=this.checked; });
  document.getElementById('addscen').addEventListener('click',function(){ var name=prompt('Name your scenario (starts from Muddle Through, then flex any input):','My scenario '+(CFG.scenarios.filter(function(s){return s.kind==='user';}).length+1));
    if(!name) return; name=(''+name).slice(0,40); var sc={n:name, kind:'user', uid:'u'+Date.now(), anchor:CFG.cp.base, vals:defaultVals(), forces:{}}; sc.v=scVal(sc);
    CFG.scenarios.push(sc); saveLS(); selectBar(CFG.scenarios.length-1); });
  function delScenario(id){ var gone=-1;
    for(var i=0;i<CFG.scenarios.length;i++){ if(CFG.scenarios[i].uid===id){ gone=i; break; } }
    CFG.scenarios=CFG.scenarios.filter(function(sc){ return sc.uid!==id; });
    // keep the selection on the SAME scenario: deleting a bar above the active one
    // shifts every later index down by one. Previously activeIdx was left alone and
    // the selection silently jumped to a neighbouring world.
    if(gone>-1 && gone<CFG.activeIdx) CFG.activeIdx--;
    else if(gone===CFG.activeIdx) CFG.activeIdx=(CFG.liveIdx!=null?CFG.liveIdx:0);
    if(CFG.activeIdx>=CFG.scenarios.length) CFG.activeIdx=CFG.scenarios.length-1;
    if(CFG.activeIdx<0) CFG.activeIdx=0;
    saveLS(); selectBar(CFG.activeIdx); }

  // explore — clicking a tab opens the detailed content directly (no brief snapshot)
  var ex=document.getElementById('explore'); var exBtns={};
  Object.keys(CFG.titles).forEach(function(k){ var b=document.createElement('button'); b.textContent=CFG.titles[k]; b.style.fontSize='12px'; b.addEventListener('click',function(){ markExplore(k); openDetail(k); }); ex.appendChild(b); exBtns[k]=b; });
  var allBtn=document.createElement('button'); allBtn.textContent='⊕ open all'; allBtn.style.fontSize='12px'; allBtn.addEventListener('click',function(){ openAll(); }); ex.appendChild(allBtn);
  function markExplore(k){ Object.keys(exBtns).forEach(function(j){ exBtns[j].style.borderColor='var(--bd2)'; }); allBtn.style.borderColor='var(--bd2)'; if(exBtns[k]) exBtns[k].style.borderColor='var(--bdinfo)'; document.getElementById('panel').innerHTML=''; }
  function setPanel(k){ markExplore(k); openDetail(k); }
  function openAll(){ Object.keys(exBtns).forEach(function(j){ exBtns[j].style.borderColor='var(--bd2)'; }); allBtn.style.borderColor='var(--bdinfo)'; document.getElementById('panel').innerHTML='';
    var d=document.getElementById('detail'); var h='';
    Object.keys(CFG.titles).forEach(function(k){ h+='<div class="detailcard"><h4 style="margin-bottom:8px;">'+CFG.titles[k]+'</h4><div>'+detailHTML(k)+'</div></div>'; });
    d.innerHTML=h; wireEditable('assum',d); wireEditable('forces',d); wireEditable('discount',d);
    var _mw=d.querySelector('#mwrap'); if(_mw){ muInit(); mwRender(_mw); }
    var dl=d.querySelector('#dlbtn'); if(dl) dl.addEventListener('click',function(){ vccDownload(); });
    d.scrollIntoView({behavior:'smooth', block:'nearest'}); }

  function esc(t){ return (''+t).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;'); }
  function editableInputsTable(){ var h='<table style="width:100%; font-size:13px;">';
    CFG.sliders.forEach(function(s){ h+='<tr><td style="padding:4px 8px 4px 0; color:var(--text2);">'+s.label+'</td><td style="padding:4px 0; text-align:right; white-space:nowrap;"><input class="assumInp" data-k="'+s.k+'" type="number" min="'+s.min+'" max="'+s.max+'" step="'+s.step+'" value="'+st[s.k]+'" style="width:82px; text-align:right; font:inherit; padding:2px 6px; border:0.5px solid var(--bd2); border-radius:6px; background:var(--primary); color:var(--text);"> <span class="sub">'+(s.suf.trim()||'')+'</span></td></tr>'; });
    return h+'</table>'; }
  function forcesMatrix(){ var fd=CFG.forcesData; var imp=fd.impacts||[]; var es=editableScens(); var act=activeScen();
    var reFrac=((act&&act.vals&&act.vals.re!=null)?act.vals.re:singleWacc)/100;
    function dlab(k){ var s=sliderByKey(k); return s? s.label : k; }
    var h='<div style="margin-top:14px; border-top:0.5px solid var(--bd); padding-top:10px;"><div class="hd" style="margin-bottom:2px;">Assessed impact — and per-scenario override</div><div class="sub" style="margin-bottom:8px;">The company-vs-industry position above is <b>structural</b>, so each scenario column defaults to the <b>assessed</b> impact. Overrides now flow into the number through the reduced-form — each force routes to the driver it moves, as a delta from the assessed case, so leaving cells untouched changes nothing. Transitory forces are PV-collapsed here; the per-year engine (M2) will consume the full path natively.</div><div style="overflow-x:auto;"><table style="font-size:12px; border-collapse:collapse; white-space:nowrap;"><tr><td class="sub" style="padding:3px 8px 3px 0; position:sticky; left:0; background:var(--primary);">Force</td><td class="sub" style="padding:3px 8px;">Routes to</td><td class="sub" style="padding:3px 8px;">Assessed</td>';
    es.forEach(function(sc){ h+='<td class="sub" style="padding:3px 8px; '+(sc===act?"color:var(--info-tx); font-weight:600;":"")+'">'+sc.n+'</td>'; });
    h+='</tr>';
    fd.rows.forEach(function(r,i){ var m=imp[i]||{};
      h+='<tr style="border-top:0.5px solid var(--bd);"><td style="padding:5px 8px 5px 0; font-weight:500; position:sticky; left:0; background:var(--primary);">'+r[0]+'</td>';
      if(!m.drv){ h+='<td class="sub" style="padding:5px 8px; color:var(--text3);">—</td><td class="sub" style="padding:5px 8px; color:var(--text2);">'+r[4]+'</td>';
        es.forEach(function(){ h+='<td class="sub" style="padding:3px 6px; color:var(--text3); text-align:center;">—</td>'; }); h+='</tr>'; return; }
      var assessed=_effBps(m, reFrac), isPath=!!m.path;
      h+='<td class="sub" style="padding:5px 8px; color:var(--text2);">&rarr; '+dlab(m.drv)+'</td>';
      h+='<td class="sub" style="padding:5px 8px; color:var(--text2);">'+(isPath? (Math.round(assessed)+' bps*') : (m.bps+' bps'))+'</td>';
      es.forEach(function(sc,si){ var ov=sc.forces&&sc.forces[i];
        if(isPath){ var eff=Array.isArray(ov)? _pvAvg(ov, reFrac) : assessed; h+='<td class="sub" style="padding:3px 6px; text-align:center; color:var(--text2);">'+Math.round(eff)+(Array.isArray(ov)?' <span style="color:var(--user-tx);">&#9998;</span>':'')+'</td>'; }
        else { var val=(ov!==undefined&&!Array.isArray(ov))? ov : Math.round(assessed); h+='<td style="padding:3px 6px;"><input class="fm" data-si="'+si+'" data-i="'+i+'" type="number" step="1" value="'+esc(val)+'" style="width:60px; font:inherit; font-size:12px; padding:2px 5px; border:0.5px solid var(--bd2); border-radius:5px; background:var(--primary); color:var(--text);"></td>'; }
      }); h+='</tr>'; });
    h+='</table></div>';
    var pr='';
    imp.forEach(function(m,i){ if(m&&m.path){ var ov=(act.forces&&Array.isArray(act.forces[i]))?act.forces[i]:m.path; var cells='';
      ['FY27','FY28','FY29','FY30','FY31'].forEach(function(y,yi){ cells+='<td style="padding:2px 5px; text-align:center;"><div class="sub" style="font-size:10px;">'+y+'</div><input class="fy" data-i="'+i+'" data-y="'+yi+'" type="number" step="1" value="'+esc(ov[yi])+'" style="width:52px; font:inherit; font-size:12px; padding:2px 4px; border:0.5px solid var(--bd2); border-radius:5px; background:var(--primary); color:var(--text);"></td>'; });
      pr+='<tr><td class="sub" style="padding:4px 10px 4px 0; white-space:nowrap;">'+fd.rows[i][0]+'</td>'+cells+'</tr>'; } });
    if(pr){ h+='<div style="margin-top:12px; border-top:0.5px solid var(--bd); padding-top:8px;"><div class="hd" style="margin-bottom:2px;">Year-by-year path — transitory forces ('+act.n+')</div><div class="sub" style="margin-bottom:6px;">Edit per-year bps for the active scenario; the assessed column PV-collapses this path. The engine (M2) will use the path directly.</div><table style="border-collapse:collapse;">'+pr+'</table></div>'; }
    return h+'</div>'; }
  function userWorldHTML(sc){ var rows='';
    CFG.sliders.forEach(function(s){ var uv=sc.vals[s.k], dv=s.def, chg=(uv!==dv);
      rows+='<tr style="border-top:0.5px solid var(--bd);"><td style="padding:5px 8px 5px 0; color:var(--text2);">'+s.label+'</td><td style="padding:5px 8px; text-align:right; '+(chg?'font-weight:600;':'color:var(--text3);')+'">'+fmt(s,uv)+'</td><td style="padding:5px 0; text-align:right; color:var(--text3);">'+(chg?('was '+fmt(s,dv)):'—')+'</td></tr>'; });
    var vm=(sc.v/CFG.market-1)*100;
    return '<p style="margin-top:0;">Your own scenario, starting from Muddle Through and re-priced live by the browser-side reduced-form. Value <b>'+CFG.ccy+' '+sc.v.toFixed(CFG.dp)+'</b> ('+(vm>=0?'+':'')+vm.toFixed(0)+'% vs market).</p><table style="width:100%; font-size:13px;"><tr><td class="sub" style="padding:2px 8px 2px 0;">Input</td><td class="sub" style="padding:2px 8px; text-align:right;">Your value</td><td class="sub" style="padding:2px 0; text-align:right;">vs MT</td></tr>'+rows+'</table><p class="sub" style="margin-top:8px;">Edit these on the <b>Assumptions</b> tab (or the sliders), the discount rate in the <b>β workbench</b>, and the Five Forces impacts on the <b>Five Forces</b> tab.</p>'; }
  function worldOverrideNote(sc){ if(!isOverridden(sc)) return ''; return '<div style="margin-top:10px; background:var(--secondary); border-radius:8px; padding:9px 11px; font-size:12.5px;"><b>You&rsquo;ve adjusted this case.</b> Value now <b>'+CFG.ccy+' '+sc.v.toFixed(CFG.dp)+'</b> vs the assessed <b>'+CFG.ccy+' '+sc.anchor.toFixed(CFG.dp)+'</b>. ↻ reset restores it.</div>'; }
  function workingsHTML(){
    var w = CFG.dcfDetail && CFG.dcfDetail.workings; if(!w) return '';
    var h='<div style="margin-top:14px; border-top:0.5px solid var(--bd); padding-top:10px;"><div class="hd" style="margin-bottom:2px;">'+w.title+'</div><div class="sub" style="margin-bottom:8px;">'+w.note+'</div><div style="overflow-x:auto;"><table style="font-size:12px; border-collapse:collapse; white-space:nowrap;">';
    h+='<tr><td class="sub" style="padding:3px 8px 3px 0; position:sticky; left:0; background:var(--primary);"></td>'+w.years.map(function(y){return '<td class="sub" style="padding:3px 8px; text-align:right;">'+y+'</td>';}).join('')+'</tr>';
    w.rows.forEach(function(r){
      h+='<tr style="border-top:0.5px solid var(--bd2);"><td style="padding:4px 8px 4px 0; position:sticky; left:0; background:var(--primary);">'+r.label+'</td>'+r.vals.map(function(v){return '<td style="padding:4px 8px; text-align:right;">'+(r.pct?(v*100).toFixed(1)+'%':Math.round(v).toLocaleString())+'</td>';}).join('')+'</tr>';
    });
    h+='</table></div><div class="sub" style="margin-top:6px;">Straight from the production engine \u2014 the same per-year build behind the headline and the downloadable workbook.</div></div>';
    return h;
  }
  function detailHTML(k){
    if(k==='world'){ var sc=activeScen(); if(sc.kind==='user'){ return userWorldHTML(sc); } var nm=sc.n;
      var wd=(CFG.worldDesc&&CFG.worldDesc[nm])?'<div class="thytag" style="color:var(--text3); margin:0 0 4px;">The world</div>'+CFG.worldDesc[nm]:'';
      var cn='<div class="thytag" style="color:var(--text3); margin:14px 0 4px;">What it means for '+CFG.companyShort+'</div>'+(CFG.narr[nm]||CFG.narr._placeholder);
      return wd+cn+worldOverrideNote(sc); }
    if(k==='forces'){ return CFG.detail.forces + forcesMatrix(); }
    if(k==='assum'){ var lab=activeScen().n; var head='';
      if(activeScen().kind!=='broker'){ head='<div style="border:0.5px solid var(--bd); border-left:2.5px solid var(--user-tx); border-radius:8px; padding:11px 13px; margin-bottom:12px;"><div style="font-weight:600; margin-bottom:2px;">Your inputs — '+lab+'</div><div class="sub" style="margin-bottom:8px;">the value-material inputs; type to override (syncs with the sliders and the live value). The full assumption set is below.</div>'+editableInputsTable()+'</div>'; }
      return head+CFG.detail.assum; }
    if(k==='dcf'){ var _dlcap=CFG.xlsxB64?'full audited formula workbook · all six scenarios, DCF build, WACC, tax &amp; equity bridges, comparables/β, Porter&#39;s · engine-sourced, links to one Assumptions sheet':'formula workbook · DCF to equity, discount build, comparables/β &amp; charts (DNL) · includes your edits';var _dllab=CFG.xlsxB64?'⤓ download full valuation workbook (Excel)':'⤓ download all scenarios to Excel';var _dl='<button style="margin-top:12px; font-size:13px; padding:6px 12px;" id="dlbtn">'+_dllab+'</button><div style="font-size:11px; color:var(--text3); margin-top:4px;">'+_dlcap+'</div>';
      var _nar='<p>'+CFG.dcfIntro+'</p>'; CFG.dcfRows.forEach(function(r){ if(r[2]){ _nar+='<details class="thy"><summary style="display:flex; justify-content:space-between; align-items:center;"><span>'+r[0]+'</span><span style="font-weight:600; margin-left:auto;">'+r[1]+'</span></summary><div class="thybody">'+r[2]+'</div></details>'; } else { _nar+='<div style="display:flex; justify-content:space-between; padding:8px 10px; margin-top:5px; font-weight:600; border-top:1px solid var(--bd2);"><span>'+r[0]+'</span><span>'+r[1]+'</span></div>'; } });
      if(!CFG.richbook){ return _nar+workingsHTML()+_dl; }
      var _sc=activeScen(); if(_sc.kind==='broker'){ _sc=muScenByKind('live')||_sc; }
      var _tg='<div style="display:flex; gap:6px; align-items:center; margin-bottom:10px;"><span class="sub">View:</span><button class="dcf_view" data-v="narr" style="font-size:12px; '+(dcfView==='narr'?'border-color:var(--bdinfo); color:var(--info-tx);':'')+'">Narrative</button><button class="dcf_view" data-v="table" style="font-size:12px; '+(dcfView==='table'?'border-color:var(--bdinfo); color:var(--info-tx);':'')+'">DCF table</button></div>';
      return _tg+(dcfView==='table'?dcfTableHTML(_sc):_nar)+_dl; }
    if(k==='discount'){ var _bw = CFG.beta? '<div style="margin:8px 0 4px;"><button id="openbw" style="font-size:13px; padding:6px 12px;">β / cost-of-capital workbench →</button><div id="bwrap" style="margin-top:10px;"></div></div>' : ''; return CFG.detail.discount.indexOf('<!--BWSLOT-->')>=0 ? CFG.detail.discount.replace('<!--BWSLOT-->', _bw) : CFG.detail.discount + _bw; }
    if(k==='multiples'){ return '<div id="mwrap"></div>'; }
    return CFG.detail[k]||''; }
  function wireEditable(k,d){
    if(k==='assum'){ Array.prototype.forEach.call(d.querySelectorAll('.assumInp'),function(inp){ inp.addEventListener('change',function(){ var key=inp.getAttribute('data-k'); var s=sliderByKey(key); var v=parseFloat(inp.value); if(isNaN(v)){ inp.value=st[key]; return; } v=Math.max(s.min,Math.min(s.max,v)); inp.value=v; setInput(key,v); }); }); }
    if(k==='forces'){ var es=editableScens();
      Array.prototype.forEach.call(d.querySelectorAll('.fm'),function(inp){ inp.addEventListener('change',function(){ var sc=es[+inp.getAttribute('data-si')]; if(!sc) return; sc.forces=sc.forces||{}; var i=+inp.getAttribute('data-i'); var f=parseFloat(inp.value); if(isNaN(f)) delete sc.forces[i]; else sc.forces[i]=f; sc.v=scVal(sc); saveLS(); drawBars(); updateCards(activeScen().v); }); });
      Array.prototype.forEach.call(d.querySelectorAll('.fy'),function(inp){ inp.addEventListener('change',function(){ var a=activeScen(); if(a.kind==='broker') return; var i=+inp.getAttribute('data-i'), y=+inp.getAttribute('data-y'); a.forces=a.forces||{}; var base=(CFG.forcesData.impacts[i]&&CFG.forcesData.impacts[i].path)||[]; var arr=Array.isArray(a.forces[i])?a.forces[i].slice():base.slice(); var f=parseFloat(inp.value); arr[y]=isNaN(f)?0:f; a.forces[i]=arr; a.v=scVal(a); saveLS(); drawBars(); updateCards(a.v); openDetail('forces', true); }); });
    }
    if(k==='discount'){ bwInit(); var _bwr=d.querySelector('#bwrap'); if(_bwr) bwRender(_bwr); var ob=d.querySelector('#openbw'); if(ob) ob.style.display='none'; }
    if(k==='multiples'){ var mw=d.querySelector('#mwrap'); if(mw){ muInit(); mwRender(mw); } }
    if(k==='dcf'){ Array.prototype.forEach.call(d.querySelectorAll('.dcf_view'),function(b){ b.addEventListener('click',function(){ dcfView=b.getAttribute('data-v'); openDetail('dcf', true); }); }); }
  }
  function openDetail(k,skipScroll){ var d=document.getElementById('detail');
    d.innerHTML='<div class="detailcard"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;"><h4>'+CFG.titles[k]+'</h4><button id="closeov" aria-label="close" style="padding:2px 9px;">×</button></div><div>'+detailHTML(k)+'</div></div>';
    document.getElementById('closeov').addEventListener('click',function(){ d.innerHTML=''; });
    var dl=document.getElementById('dlbtn'); if(dl) dl.addEventListener('click',function(){ vccDownload(); });
    wireEditable(k,d); if(!skipScroll) d.scrollIntoView({behavior:'smooth', block:'nearest'}); }

  // ---- Workstream D: cost-of-capital / beta workbench (MOCK data via CFG.beta) ----
  var BW=CFG.beta; var bs=null;
  function bwInit(){
    bs={ idx:BW.indexDefault, win:BW.windowDefault, rf:BW.rf, erp:BW.erp, alpha:BW.alpha,
         relever:false, targetDE:(BW.subject.de||0), showCand:false, showWider:false, comps:BW.comparables.slice(), plot:null, betaOv:null };
    bs.comps.forEach(function(c){ if(c._sel===undefined) c._sel=c.selected; });
    // beta plots start collapsed; each opens inline under its comparable on click
  }
  function betaOf(c){ var d=c._added?c._data:c.data; return d[bs.idx][bs.win].beta; }
  function pointsOf(c){ var d=c._added?c._data:c.data; return d[bs.idx][bs.win].points; }
  function unlev(bl,tax,de){ return bl/(1+(1-tax)*de); }
  function relev(bu,tax,de){ return bu*(1+(1-tax)*de); }
  function median(a){ if(!a.length) return 0; var b=a.slice().sort(function(x,y){return x-y;}); var m=Math.floor(b.length/2); return b.length%2?b[m]:(b[m-1]+b[m])/2; }
  function selectedComps(){ return bs.comps.filter(function(c){return c._sel;}); }
  function _lvl(v,a,b){ return (v==null)?-1:(v<a?0:(v<b?1:2)); }
  function _bandChip(l){ if(l<0) return ''; var t=['low','med','high'][l], c=['var(--success-tx)','var(--text2)','var(--danger-tx)'][l]; return ' <span style="font-size:10px; color:'+c+';">'+t+'</span>'; }
  function aggBeta(){ var sc=selectedComps(); if(!sc.length) return {beta:0,medL:0,medU:0};
    var medL=median(sc.map(function(c){return betaOf(c);}));
    var medU=median(sc.map(function(c){return unlev(betaOf(c),c.tax,c.gearingDE);}));
    var beta=bs.relever?relev(medU,BW.subject.tax,bs.targetDE):medL;
    return {beta:beta, medL:medL, medU:medU}; }
  function effBeta(){ var d=aggBeta().beta; return (bs.betaOv!=null && !isNaN(bs.betaOv))?bs.betaOv:d; }
  function reOf(beta){ return bs.rf + beta*bs.erp + bs.alpha; }
  function impliedDiscount(re){ var t=BW.toDiscount; return (t.mode==='wacc')?(t.wE*re+(1-t.wE)*t.kdAfterTax):re; }
  function jsScatter(beta){ var pts=[]; for(var i=0;i<26;i++){ var x=(Math.random()-0.5)*0.05; pts.push([Math.round(x*1e4)/1e4, Math.round((beta*x+(Math.random()-0.5)*0.016)*1e4)/1e4]); } return pts; }
  function addCandObj(cd){ if(cd.addable===false) return;
    var data={}; BW.indices.forEach(function(ix){ data[ix]={}; BW.windows.forEach(function(w){ data[ix][w]={beta:cd.betaHint, points:jsScatter(cd.betaHint)}; }); });
    bs.comps.push({name:cd.name,ticker:cd.ticker,why:cd.why||'Added by you.',tax:(cd.tax!=null?cd.tax:0.30),gearingDE:(cd.gearingDE!=null?cd.gearingDE:0),_sel:true,_added:true,_data:data}); }
  function candRow(cd,cls,i){ return '<div style="display:flex; gap:8px; align-items:flex-start; margin-bottom:7px;"><button class="'+cls+'" data-i="'+i+'" '+(cd.addable===false?'disabled title="privately held — no listed beta"':'')+' style="font-size:11px; padding:2px 8px; flex:none;">+ add</button><div style="font-size:12.5px;"><b>'+cd.name+'</b> <span class="sub">'+cd.ticker+' · \u03b2\u2248'+cd.betaHint.toFixed(2)+'</span><div style="color:var(--text2);">'+cd.why+'</div></div></div>'; }
  function numField(id,label,v,step){ return '<div><div class="sub">'+label+'</div><input type="number" id="'+id+'" value="'+v+'" step="'+step+'" style="width:74px; font:inherit; padding:3px 6px; border:0.5px solid var(--bd2); border-radius:6px; background:var(--primary); color:var(--text);"></div>'; }
  function betaStats(pts){ var n=pts.length, mx=0, my=0; pts.forEach(function(p){ mx+=p[0]; my+=p[1]; }); mx/=n; my/=n;
    var sxx=0,sxy=0,syy=0; pts.forEach(function(p){ var dx=p[0]-mx, dy=p[1]-my; sxx+=dx*dx; sxy+=dx*dy; syy+=dy*dy; });
    var b=sxy/sxx, a=my-b*mx, ssr=0; pts.forEach(function(p){ var e=p[1]-(a+b*p[0]); ssr+=e*e; });
    var r2=1-ssr/syy, se=Math.sqrt((ssr/(n-2))/sxx); return {b:b, r2:r2, se:se, t0:b/se, t1:(b-1)/se, n:n}; }
  function scatterSVG(c){ var pts=pointsOf(c), b=betaOf(c), W=400,H=210,pad=24;
    var xs=pts.map(function(p){return p[0];}), ys=pts.map(function(p){return p[1];});
    var xmax=Math.max.apply(null,xs.map(Math.abs))*1.12||0.05, ymax=Math.max.apply(null,ys.map(Math.abs))*1.12||0.05;
    function X(x){ return pad+(x+xmax)/(2*xmax)*(W-2*pad); } function Y(y){ return H-pad-(y+ymax)/(2*ymax)*(H-2*pad); }
    var mx=xs.reduce(function(a,b){return a+b;},0)/xs.length, my=ys.reduce(function(a,b){return a+b;},0)/ys.length;
    var s='<svg viewBox="0 0 '+W+' '+H+'" style="width:100%; max-width:440px; background:var(--primary); border:0.5px solid var(--bd); border-radius:8px;">';
    s+='<line x1="'+X(-xmax)+'" y1="'+Y(0)+'" x2="'+X(xmax)+'" y2="'+Y(0)+'" stroke="var(--bd2)" stroke-width="0.5"/>';
    s+='<line x1="'+X(0)+'" y1="'+Y(-ymax)+'" x2="'+X(0)+'" y2="'+Y(ymax)+'" stroke="var(--bd2)" stroke-width="0.5"/>';
    s+='<line x1="'+X(-xmax)+'" y1="'+Y(my+b*(-xmax-mx))+'" x2="'+X(xmax)+'" y2="'+Y(my+b*(xmax-mx))+'" stroke="var(--bdinfo)" stroke-width="1.5"/>';
    pts.forEach(function(p){ s+='<circle cx="'+X(p[0])+'" cy="'+Y(p[1])+'" r="2.4" fill="var(--user-tx)" opacity="0.75"/>'; });
    s+='<text x="'+(W-pad)+'" y="18" text-anchor="end" font-size="12" fill="var(--text2)">slope β = '+b.toFixed(2)+'</text>';
    s+='<text x="'+(W-pad)+'" y="'+(H-6)+'" text-anchor="end" font-size="9" fill="var(--text3)">index return →</text></svg>'; return s; }
  function bwPlotBlock(pc){ var stt=betaStats(pointsOf(pc)), sig=Math.abs(stt.t1)>2, verdict=sig?('<b style="color:'+(stt.b>1?'var(--danger-tx)':'var(--info-tx)')+';">significantly '+(stt.b>1?'above':'below')+' 1</b>'):'<b>not distinguishable from 1</b>';
    return '<div class="sub" style="margin:2px 0 4px;">Regression of '+pc.name+' returns vs '+bs.idx+' ('+bs.win+') — slope = β</div>'+scatterSVG(pc)+'<div class="sub" style="margin-top:5px; line-height:1.55;">n='+stt.n+' · R² '+stt.r2.toFixed(2)+' · SE(β) '+stt.se.toFixed(2)+' · t(β vs 0) '+stt.t0.toFixed(1)+' · <b>t(β vs 1) '+stt.t1.toFixed(1)+'</b> → β is '+verdict+' at ~95%.</div>'; }
  function bwRender(cont){ if(!cont) return;
    var agg=aggBeta(), eb=effBeta(), re=reOf(eb), disc=impliedDiscount(re), t=BW.toDiscount, h='';
    h+='<div style="background:var(--info-bg); color:var(--info-tx); border-radius:8px; padding:8px 10px; font-size:12px; margin-bottom:10px;"><b>Single '+(t.label||'WACC')+' · '+singleWacc.toFixed(2)+'%</b> — one rate per company per valuation date (methodology §3.5; cross-cutting convention 1). Scenarios differ in cash flows, not in the discount rate. Applying below updates the single rate for <b>all</b> scenarios; tick “this scenario only” to record a deliberate per-scenario override.</div>';
    h+='<div style="background:var(--warning-bg); color:var(--warning-tx); border-radius:8px; padding:8px 10px; font-size:12px; margin-bottom:10px;"><b>Mock data.</b> Betas and scatter points are synthetic placeholders shaped like the eventual EODHD feed (peer price series + indices + gearing/tax). To be sourced from Ben&rsquo;s pipeline.</div>';
    h+='<div style="display:flex; flex-wrap:wrap; gap:18px; align-items:flex-start; margin-bottom:8px;"><div style="flex:1 1 300px; min-width:250px;">';
    h+='<div style="font-weight:600; font-size:14px; margin:2px 0 4px;">Build the discount rate</div><div class="sub" style="margin-bottom:10px;">Set the components (or select peers for β); the rate updates live. Choose how to apply it on the right.</div>';
    h+='<div style="display:flex; flex-wrap:wrap; gap:12px 18px; align-items:flex-end; margin-bottom:12px;">'+numField('bw_rf','Risk-free %',bs.rf,0.05)+numField('bw_erp','ERP %',bs.erp,0.05)+numField('bw_alpha','Alpha %',bs.alpha,0.1);
    h+='<div><div class="sub">Index</div><select id="bw_idx" style="font:inherit; padding:3px 6px; border:0.5px solid var(--bd2); border-radius:6px; background:var(--primary); color:var(--text);">'+BW.indices.map(function(ix){return '<option'+(ix===bs.idx?' selected':'')+'>'+ix+'</option>';}).join('')+'</select></div>';
    h+='<div><div class="sub">Estimation window</div>'+BW.windows.map(function(w){return '<button class="bw_win" data-w="'+w+'" style="font-size:12px; margin-right:4px; '+(w===bs.win?'border-color:var(--bdinfo); color:var(--info-tx);':'')+'">'+w+'</button>';}).join('')+'</div></div>';
    if(!BW.bank){ h+='<label style="display:flex; align-items:center; gap:6px; font-size:12px; color:var(--text2); margin-bottom:4px; flex-wrap:wrap;"><input type="checkbox" id="bw_relev" '+(bs.relever?'checked':'')+'> use asset betas: unlever peers, re-lever at DNL gearing D/E <input type="number" id="bw_de" value="'+bs.targetDE+'" step="0.05" min="0" '+(bs.relever?'':'disabled')+' style="width:60px; font:inherit; padding:2px 6px; border:0.5px solid var(--bd2); border-radius:6px; background:var(--primary); color:var(--text);"></label><div class="sub" style="margin-bottom:10px; font-size:11.5px;">off = median of peers’ levered β · on = Hamada re-lever (the proper triangulation) at DNL’s gearing, and reveals the D/E box</div>'; }
    else { h+='<div class="sub" style="margin-bottom:10px;">Relevering is not applied to banks — beta is used directly (deposits/wholesale funding are operating inputs, not financing).</div>'; }
    h+='</div>';
    h+='<div style="flex:1 1 250px; min-width:240px;">';
    h+='<div style="background:var(--secondary); border-radius:8px; padding:11px 13px;">';
    h+='<div style="font-weight:600; font-size:13px; margin-bottom:6px;">The rate you built</div>';
    h+='<div style="font-size:13px;">Selected peers ('+selectedComps().length+'): median levered β <b>'+agg.medL.toFixed(2)+'</b>'+(BW.bank?'':' · median unlevered <b>'+agg.medU.toFixed(2)+'</b>')+'</div>';
    h+='<div style="font-size:13px; margin-top:6px; display:flex; align-items:center; gap:7px; flex-wrap:wrap;">→ subject β <input type="number" id="bw_beta" value="'+eb.toFixed(2)+'" step="0.05" style="width:66px; font:inherit; padding:2px 6px; border:0.5px solid var(--bd2); border-radius:6px; background:var(--primary); color:var(--text);">'+(bs.betaOv!=null?'<span class="sub" style="color:var(--user-tx);">your pick</span>':'<span class="sub">= peer-triangulated</span>')+'</div>';
    h+='<div class="sub" style="margin-top:3px; line-height:1.5;">Triangulate, then choose — not necessarily the average. Peer median levered <b>'+agg.medL.toFixed(2)+'</b>'+(BW.bank?'':(bs.relever?(' · relevered '+relev(agg.medU,BW.subject.tax,bs.targetDE).toFixed(2)):(' · unlevered '+agg.medU.toFixed(2))))+' · documented judgment <b>'+BW.subject.selectedBeta.toFixed(2)+'</b>'+(bs.betaOv!=null?' · <a href="#" id="bw_beta_reset" style="color:var(--info-tx);">↺ use peer-triangulated</a>':'')+'</div>';
    h+='<div style="font-size:13px; margin-top:4px;">→ R<sub>e</sub> = '+bs.rf.toFixed(2)+'% + '+eb.toFixed(2)+'×'+bs.erp.toFixed(2)+'%'+(bs.alpha?(' + α '+bs.alpha.toFixed(2)+'%'):'')+' = <b>'+re.toFixed(2)+'%</b>'+(t.mode==='wacc'?(' → implied '+t.label+' <b>'+disc.toFixed(2)+'%</b>'):'')+'</div>';
    h+='<div style="margin-top:10px; border-top:0.5px solid var(--bd2); padding-top:9px;"><div style="font-weight:600; font-size:13px; margin-bottom:6px;">Apply this rate ('+disc.toFixed(2)+'%)</div>';
    h+='<label style="display:flex; gap:7px; align-items:flex-start; font-size:12.5px; margin-bottom:5px; cursor:pointer;"><input type="radio" name="bw_scope" value="all" checked style="margin-top:2px;"><span><b>To all scenarios</b> — sets the single '+(t.label||'WACC')+' (the disciplined default).</span></label>';
    h+='<label style="display:flex; gap:7px; align-items:flex-start; font-size:12.5px; margin-bottom:9px; cursor:pointer;"><input type="radio" name="bw_scope" value="one" style="margin-top:2px;"><span><b>To this scenario only</b> — a deliberate per-scenario override, flagged on its bar.</span></label>';
    h+='<button id="bw_apply" style="font-size:13px; padding:5px 14px;">apply →</button></div></div>';
    h+='</div></div>';
    h+='<table style="width:100%; font-size:13px;"><tr><td class="sub"></td><td class="sub" style="padding:2px 8px 2px 0;">Comparable</td><td class="sub" style="padding:2px 8px; text-align:right;">Levered β</td><td class="sub" style="padding:2px 8px; text-align:right;">Unlevered β</td><td class="sub"></td></tr>';
    h+='<tr style="border-top:0.5px solid var(--bd);"><td></td><td style="padding:6px 8px 6px 0;"><b>'+BW.subject.name+'</b> <span class="sub">'+BW.subject.ticker+' · subject</span><div class="sub" style="color:var(--danger-tx);">'+BW.subject.measuredNote+'</div></td><td style="padding:6px 8px; text-align:right; font-weight:600;">'+BW.subject.selectedBeta.toFixed(2)+'</td><td style="padding:6px 8px; text-align:right; color:var(--text3);">'+(BW.bank?'—':unlev(BW.subject.selectedBeta,BW.subject.tax,BW.subject.de).toFixed(2))+'</td><td></td></tr>';
    bs.comps.forEach(function(c,ci){ var bl=betaOf(c), bu=unlev(bl,c.tax,c.gearingDE);
      h+='<tr style="border-top:0.5px solid var(--bd);"><td style="padding:6px 4px 6px 0; vertical-align:top;"><input type="checkbox" class="bw_sel" data-ci="'+ci+'" '+(c._sel?'checked':'')+'></td><td style="padding:6px 8px 6px 0;">'+c.name+' <span class="sub">'+c.ticker+'</span>'+(c._added?' <span class="sub" style="color:var(--user-tx);">added</span>':'')+'<details class="thy" style="margin-top:4px;"><summary>why comparable</summary><div class="thybody">'+c.why+'</div></details></td><td style="padding:6px 8px; text-align:right; '+(c._sel?'font-weight:600;':'color:var(--text3);')+'">'+bl.toFixed(2)+'</td><td style="padding:6px 8px; text-align:right; color:var(--text2);">'+(BW.bank?'—':bu.toFixed(2))+'</td><td style="padding:6px 0; text-align:right; vertical-align:top;"><button class="bw_plot" data-name="'+c.name+'" style="font-size:11px; padding:2px 7px; '+(bs.plot===c.name?'border-color:var(--bdinfo); color:var(--info-tx);':'')+'">'+(bs.plot===c.name?'hide':'plot')+'</button></td></tr>'; if(bs.plot===c.name){ h+='<tr><td colspan="5" style="padding:0 8px 12px;">'+bwPlotBlock(c)+'</td></tr>'; } });
    h+='</table>';
    if(BW.subject.det){ var _dc=[BW.subject].concat(bs.comps.filter(function(c){return c._sel;}));
      h+='<details class="thy" style="margin-top:12px;" open><summary>Beta determinants — why these asset betas</summary><div class="thybody">';
      h+='<div class="sub" style="margin-bottom:8px; line-height:1.55;">A stock’s equity (levered) beta rests on three fundamentals. <b>Financial leverage</b> gears the asset beta up — the levered-vs-unlevered gap (Hamada). The underlying <b>asset beta</b> is itself driven by <b>operational leverage</b> (fixed-cost intensity — how far a revenue move amplifies into profit) and the <b>cyclicality of revenues &amp; cash flows</b> (how tightly the top line tracks the economic cycle). Reading peers on all three explains, and disciplines, the beta you pick.</div>';
      // Gated on BW.mock rather than printed unconditionally: the warning was
      // right by coincidence (all three datasets are currently mock) and would
      // have kept firing once the feed returned, which is how a warning stops
      // being read. Item 11, batch 6.
      if(BW.mock){ h+='<div class="sub" style="margin-bottom:8px; color:var(--warning-tx);"><b>Illustrative mock data.</b> Ben&rsquo;s EODHD feed is temporarily down, so the figures below are placeholders. Calculation methods are footnoted underneath.</div>'; }
      h+='<div style="overflow-x:auto;"><table style="font-size:12px; border-collapse:collapse; white-space:nowrap; width:100%;"><tr><td class="sub" style="padding:3px 8px 3px 0;">Company</td><td class="sub" style="padding:3px 8px; text-align:right;">Financial leverage<sup>1</sup><br>D/E · ND/EBITDA</td><td class="sub" style="padding:3px 8px; text-align:right;">Operational leverage<sup>2</sup><br>DOL</td><td class="sub" style="padding:3px 8px; text-align:right;">Revenue cyclicality<sup>3</sup><br>cycle corr.</td><td class="sub" style="padding:3px 8px; text-align:right;">Asset β<sup>4</sup></td></tr>';
      _dc.forEach(function(c){ var d=c.det||{}, isSub=(c===BW.subject); var de=isSub?BW.subject.de:c.gearingDE;
        var ab=isSub?(BW.bank?BW.subject.selectedBeta:unlev(BW.subject.selectedBeta,BW.subject.tax,BW.subject.de)):unlev(betaOf(c),c.tax,c.gearingDE);
        h+='<tr style="border-top:0.5px solid var(--bd);"><td style="padding:5px 8px 5px 0;">'+(isSub?'<b>'+c.name+'</b> <span class="sub">subject</span>':c.name)+'</td>';
        h+='<td style="padding:5px 8px; text-align:right;">'+de.toFixed(2)+' · '+(d.ndeb!=null?d.ndeb.toFixed(1)+'×':'—')+_bandChip(_lvl(d.ndeb,1.5,2.5))+'</td>';
        h+='<td style="padding:5px 8px; text-align:right;">'+(d.dol!=null?d.dol.toFixed(1)+'×':'—')+_bandChip(_lvl(d.dol,1.6,2.2))+'</td>';
        h+='<td style="padding:5px 8px; text-align:right;">'+(d.cyc!=null?d.cyc.toFixed(2):'—')+_bandChip(_lvl(d.cyc,0.5,0.7))+'</td>';
        h+='<td style="padding:5px 8px; text-align:right; font-weight:600;">'+ab.toFixed(2)+'</td></tr>'; });
      h+='</table></div>';
      h+='<ol style="font-size:11.5px; color:var(--text2); line-height:1.5; margin:8px 0 0; padding-left:18px;">';
      h+='<li><b>Financial leverage</b> — from reported gearing: net debt ÷ EBITDA and D/E. <span style="color:var(--warning-tx);">Mocked (EODHD down).</span></li>';
      h+='<li><b>Operational leverage (DOL)</b> — how far a revenue move amplifies into EBIT: DOL = %ΔEBIT ÷ %ΔRevenue measured across the cycle, ≈ 1 + (fixed costs ÷ EBIT) from a cost-structure split. <span style="color:var(--warning-tx);">Mocked estimate — not yet computed from data.</span></li>';
      h+='<li><b>Revenue cyclicality</b> — the correlation (or regression β) of real revenue growth against GDP / industrial-production growth over a full cycle. <span style="color:var(--warning-tx);">Mocked estimate — not yet computed from data.</span></li>';
      h+='<li><b>Asset β (unlevered)</b> — Hamada unlevering, computed live from the levered β, tax and gearing: β<sub>u</sub> = β<sub>l</sub> ÷ (1 + (1−tax)·D/E).</li>';
      h+='</ol>';
      if(BW.detNote) h+='<div class="sub" style="margin-top:8px; line-height:1.55;">'+BW.detNote+'</div>';
      h+='</div></details>';
    }
    h+='<div style="margin-top:8px;"><button id="bw_find" style="font-size:12px;">'+(bs.showCand?'− hide candidates':'✦ find more comparables')+'</button>';
    if(bs.showCand){ h+='<div style="margin-top:8px; border:0.5px dashed var(--bd2); border-radius:8px; padding:8px 10px;">';
      h+='<div class="sub" style="margin-bottom:4px;">Add any company you consider comparable, even if it is not listed here:</div><div style="display:flex; gap:6px; align-items:flex-end; flex-wrap:wrap; margin-bottom:10px;"><div><div class="sub">Name</div><input id="bw_cn" placeholder="company" style="width:120px; font:inherit; font-size:12px; padding:2px 6px; border:0.5px solid var(--bd2); border-radius:5px; background:var(--primary); color:var(--text);"></div><div><div class="sub">Ticker</div><input id="bw_ct" placeholder="TICK" style="width:74px; font:inherit; font-size:12px; padding:2px 6px; border:0.5px solid var(--bd2); border-radius:5px; background:var(--primary); color:var(--text);"></div><div><div class="sub">β (est.)</div><input id="bw_cb" type="number" step="0.05" value="1.00" style="width:64px; font:inherit; font-size:12px; padding:2px 6px; border:0.5px solid var(--bd2); border-radius:5px; background:var(--primary); color:var(--text);"></div><button id="bw_cadd" style="font-size:11px;">+ add</button></div>';
      h+='<div class="sub" style="margin-bottom:6px;">Suggested by the &lsquo;find comparables&rsquo; step — the analyst / AI-judgment part; each comes with a rationale to accept or reject:</div>';
      BW.candidates.forEach(function(cd,i){ h+=candRow(cd,'bw_add',i); });
      h+='<div style="margin-top:8px;"><button id="bw_wider" style="font-size:12px;">'+(bs.showWider?'− hide wider search':'⌕ search wider')+'</button>';
      if(bs.showWider && BW.candidates2){ h+='<div style="margin-top:6px;"><div class="sub" style="margin-bottom:6px;">Broader search — adjacent names with a weaker but arguable rationale:</div>'; BW.candidates2.forEach(function(cd,i){ h+=candRow(cd,'bw_add2',i); }); h+='</div>'; }
      h+='</div></div>'; } h+='</div>';
    cont.innerHTML=h; bwWire(cont);
  }
  function bwWire(cont){
    function on(id,ev,fn){ var e=cont.querySelector('#'+id); if(e) e.addEventListener(ev,fn); }
    on('bw_rf','change',function(){ bs.rf=parseFloat(this.value)||0; bwRender(cont); });
    on('bw_erp','change',function(){ bs.erp=parseFloat(this.value)||0; bwRender(cont); });
    on('bw_alpha','change',function(){ bs.alpha=parseFloat(this.value)||0; bwRender(cont); });
    on('bw_idx','change',function(){ bs.idx=this.value; bwRender(cont); });
    Array.prototype.forEach.call(cont.querySelectorAll('.bw_win'),function(b){ b.addEventListener('click',function(){ bs.win=b.getAttribute('data-w'); bwRender(cont); }); });
    on('bw_relev','change',function(){ bs.relever=this.checked; bwRender(cont); });
    on('bw_de','change',function(){ bs.targetDE=parseFloat(this.value)||0; bwRender(cont); });
    on('bw_beta','change',function(){ var v=parseFloat(this.value); bs.betaOv=isNaN(v)?null:v; bwRender(cont); });
    on('bw_beta_reset','click',function(e){ e.preventDefault(); bs.betaOv=null; bwRender(cont); });
    Array.prototype.forEach.call(cont.querySelectorAll('.bw_sel'),function(cb){ cb.addEventListener('change',function(){ bs.comps[+cb.getAttribute('data-ci')]._sel=cb.checked; bwRender(cont); }); });
    Array.prototype.forEach.call(cont.querySelectorAll('.bw_plot'),function(b){ b.addEventListener('click',function(){ var nm=b.getAttribute('data-name'); bs.plot=(bs.plot===nm)?null:nm; bwRender(cont); }); });
    on('bw_find','click',function(){ bs.showCand=!bs.showCand; bwRender(cont); });
    on('bw_wider','click',function(){ bs.showWider=!bs.showWider; bwRender(cont); });
    on('bw_cadd','click',function(){ var cn=cont.querySelector('#bw_cn'), ct=cont.querySelector('#bw_ct'), cb=cont.querySelector('#bw_cb'); var nm=cn?cn.value:'', bv=cb?parseFloat(cb.value):NaN; if(!nm||isNaN(bv)){ alert('Enter a name and an estimated beta.'); return; } addCandObj({name:nm, ticker:(ct&&ct.value)||'—', why:'Added by you as a comparable.', betaHint:bv, tax:0.30, gearingDE:0, addable:true}); bwRender(cont); });
    Array.prototype.forEach.call(cont.querySelectorAll('.bw_add'),function(b){ b.addEventListener('click',function(){ addCandObj(BW.candidates[+b.getAttribute('data-i')]); bwRender(cont); }); });
    Array.prototype.forEach.call(cont.querySelectorAll('.bw_add2'),function(b){ b.addEventListener('click',function(){ addCandObj(BW.candidates2[+b.getAttribute('data-i')]); bwRender(cont); }); });
    on('bw_apply','click',function(){ var scopeEl=cont.querySelector('input[name=bw_scope]:checked'); var thisOnly=scopeEl&&scopeEl.value==='one'; var s=sliderByKey('re'); var v=impliedDiscount(reOf(effBeta())); v=Math.max(s.min,Math.min(s.max,v));
      if(thisOnly){ var a=activeScen(); if(a.kind==='broker'){ alert('Select an editable scenario first.'); return; } a.vals.re=v; a.v=scVal(a); saveLS(); syncSliders(); updateCards(a.v); drawBars(); alert('Per-scenario override — '+a.n+' discount rate set to '+v.toFixed(2)+'% (the single WACC stays '+singleWacc.toFixed(2)+'%).'); }
      else { singleWacc=v; editableScens().forEach(function(sc){ sc.vals.re=v; sc.v=scVal(sc); }); saveLS(); syncSliders(); updateCards(activeScen().v); drawBars(); alert('Single WACC set to '+v.toFixed(2)+'% for all scenarios.'); } });
  }

  // ---- Multiples view: implied-by-DCF + cross-check (MU=CFG.multiples; DNL only) ----
  var MU=CFG.multiples; var ms=null; var dcfView='narr';
  function ensurePeerSel(){ if(BW&&BW.comparables){ BW.comparables.forEach(function(c){ if(c._sel===undefined) c._sel=c.selected; }); } }
  function _earn(c,field){ var f=c.mfin; if(!f) return null; var e=f[field]; if(e==null) return null; var bdef=MU.bases[ms.basis], pk=(bdef&&bdef.peerKey)?bdef.peerKey:ms.basis; var v=(typeof e==='object')?e[pk]:e; if(v!=null&&bdef&&bdef.peerGrow) v=v*bdef.peerGrow; return v; }
  // Lease-neutral EV/EBITDAR basis: GATED on MU.leaseNeutral (lease-heavy archetypes only). DNL/WBC/CSL carry no leaseNeutral, so this stays dormant for them.
  // Schema: MU.leaseNeutral = { capMult, peer, peerNote, note, subject:{ rent, leaseLiabInND } }; each peer mfin also carries { rent, leaseLiab }.
  function muMetrics(){ var m=MU.metrics.slice(); if(MU.leaseNeutral){ m.push({k:'evebitdar',label:'EV / EBITDAR',kind:'evr',field:'ebitdar',peer:MU.leaseNeutral.peer,peerNote:MU.leaseNeutral.peerNote}); } return m; }
  function muEbitdar(b){ return b.ebitda + (MU.leaseNeutral?MU.leaseNeutral.subject.rent:0); }
  function muAdjBridge(){ var LN=MU.leaseNeutral; return CFG.netDebt - (LN.subject.leaseLiabInND||0) + LN.subject.rent*LN.capMult; }
  function muComp(c){ var f=c.mfin; if(!f) return null; var mc=f.price*f.shares, ev=mc+f.netDebt, eb=_earn(c,'ebitda'), ei=_earn(c,'ebit'), ni=_earn(c,'ni'); var o={mktcap:mc, ev:ev, evebitda:ev/eb, evebit:ev/ei, pe:mc/ni}; if(MU.leaseNeutral){ var LN=MU.leaseNeutral, rent=(f.rent||0), ebr=eb+rent, evadj=ev-(f.leaseLiab||0)+rent*LN.capMult; o.evebitdar=evadj/ebr; } return o; }
  function peerMult(m){ if(!BW||!BW.comparables) return m.peer; var v=BW.comparables.filter(function(c){return c._sel&&c.mfin;}).map(function(c){return muComp(c)[m.k];}); return v.length?median(v):m.peer; }
  function muInit(){ ensurePeerSel(); if(!ms) ms={ basis:MU.baseDefault, metric:MU.metricDefault, refMode:'peer', custom:'' }; }
  function muMetric(){ var ml=muMetrics(); for(var i=0;i<ml.length;i++){ if(ml[i].k===ms.metric) return ml[i]; } return ml[0]; }
  function muBase(){ return MU.bases[ms.basis]; }
  function muEV(v){ return v*CFG.shares+CFG.netDebt; }
  function muIsEV(m){ return m.kind==='ev'||m.kind==='evr'; }
  function muDen(m,b){ return m.kind==='evr'?muEbitdar(b):b[m.field]; }
  function muEVof(m,v){ return m.kind==='evr'?(v*CFG.shares+muAdjBridge()):muEV(v); }
  function muBridge(m){ return m.kind==='evr'?muAdjBridge():CFG.netDebt; }
  function muImplied(v,m,b){ return muIsEV(m)? muEVof(m,v)/muDen(m,b) : v*CFG.shares/muDen(m,b); }
  function muValue(x,m,b){ return muIsEV(m)? (x*muDen(m,b)-muBridge(m))/CFG.shares : x*muDen(m,b)/CFG.shares; }
  function muRefMult(m,mkt){ if(ms.refMode==='market') return mkt; if(ms.refMode==='custom'){ var c=parseFloat(ms.custom); return isNaN(c)?peerMult(m):c; } return peerMult(m); }
  function muScenByKind(k){ for(var i=0;i<CFG.scenarios.length;i++){ if(CFG.scenarios[i].kind===k) return CFG.scenarios[i]; } return null; }
  function muX(x){ return x.toFixed(1)+'×'; }
  function muN(x){ return Math.round(x).toLocaleString(); }
  function mwCompsWorkbench(){ if(!BW||!BW.comparables) return ''; var cs=BW.comparables, m=muMetric();
    var h='<div class="hd" style="margin:4px 0 4px;">Comparable company multiples — workbench <span class="sub" style="font-weight:400;">(mock · editable · same peer set as the β workbench)</span></div>';
    h+='<div class="sub" style="margin-bottom:6px; color:var(--warning-tx);">Mock inputs, each peer in its own local currency — edit any input cell to recompute; multiples are currency-neutral. Validate to reported statements when the EODHD feed returns.</div>';
    h+='<div style="overflow-x:auto;"><table style="font-size:12px; border-collapse:collapse; white-space:nowrap;">';
    h+='<tr><td class="sub" style="padding:3px 8px 3px 0;"></td>';
    cs.forEach(function(c,ci){ h+='<td class="sub" style="padding:3px 8px; text-align:right;"><label style="cursor:pointer;"><input type="checkbox" class="mu_comp" data-ci="'+ci+'" '+(c._sel?'checked':'')+' style="vertical-align:middle;"> '+c.name+'</label><div style="font-weight:400; color:var(--text3);">'+(c.mfin?c.mfin.ccy:'')+'</div></td>'; });
    h+='<td class="sub" style="padding:3px 8px; text-align:right; color:var(--info-tx);">Median<br>(selected)</td></tr>';
    function fval(c,field,basis){ var f=c.mfin; if(!f) return null; var e=f[field]; if(e==null) return null; return basis?((typeof e==='object')?e[ms.basis]:e):e; }
    function inRow(label,field,step,basis){ var tag=basis?' <span class="sub">('+MU.bases[ms.basis].label.split(' ')[0].toLowerCase()+')</span>':''; var r='<tr style="border-top:0.5px solid var(--bd);"><td style="padding:4px 8px 4px 0; color:var(--text2);">'+label+tag+'</td>';
      cs.forEach(function(c,ci){ var v=fval(c,field,basis); r+='<td style="padding:3px 4px; text-align:right;">'+(v!=null?'<input type="number" class="mu_fin" data-ci="'+ci+'" data-f="'+field+'" data-basis="'+(basis?'1':'')+'" value="'+v+'" step="'+step+'" style="width:78px; text-align:right; font:inherit; font-size:11.5px; padding:2px 4px; border:0.5px solid var(--bd2); border-radius:5px; background:var(--primary); color:var(--text);">':'—')+'</td>'; });
      return r+'<td></td></tr>'; }
    function derRow(label,key,mult){ var hi=(mult&&key===m.field); var r='<tr style="border-top:0.5px solid var(--bd);'+(hi?' background:var(--secondary);':'')+'"><td style="padding:4px 8px 4px 0; '+(mult?'font-weight:600;':'color:var(--text2);')+'">'+label+'</td>';
      cs.forEach(function(c){ var cc=muComp(c), v=cc?cc[key]:null; r+='<td style="padding:4px 8px; text-align:right; '+(c._sel?'':'color:var(--text3);')+(mult?' font-weight:600;':'')+'">'+(v!=null?(mult?muX(v):Math.round(v).toLocaleString()):'—')+'</td>'; });
      var medv=mult?peerMult({k:key,peer:null}):null; return r+'<td style="padding:4px 8px; text-align:right; color:var(--info-tx); font-weight:600;">'+(mult&&medv!=null?muX(medv):'')+'</td></tr>'; }
    h+=inRow('Price','price','0.01')+inRow('Shares (m)','shares','1')+derRow('Market cap','mktcap',false)+inRow('Net debt','netDebt','1')+derRow('Enterprise value','ev',false);
    h+=inRow('EBITDA','ebitda','1',true)+inRow('EBIT','ebit','1',true)+inRow('Net income','ni','1',true);
    if(MU.leaseNeutral){ h+=inRow('Annual rent / lease cost','rent','1',false); }
    h+=derRow('EV / EBITDA','evebitda',true)+derRow('EV / EBIT','evebit',true)+derRow('P / E','pe',true);
    if(MU.leaseNeutral){ h+=derRow('EV / EBITDAR','evebitdar',true); }
    h+='</table></div><div class="sub" style="margin:5px 0 12px; line-height:1.5;">The EBITDA / EBIT / net income rows follow the selected earnings basis (top toggle) — switching it moves the subject and the peers together, so the comparison stays like-for-like (market cap, net debt and EV are current market values, unchanged by basis). Tick/untick a peer (top row) to change the set — this drives the median and the peer-median lines below, and stays in sync with the β workbench (Sasol excluded by default). Derived cells (market cap, EV, the three multiples) recompute live; edits are session-only.</div>';
    if(MU.leaseNeutral){ var LN=MU.leaseNeutral; h+='<div class="sub" style="margin:0 0 12px; line-height:1.5; color:var(--warning-tx);"><b>Lease-neutral basis (lease-heavy archetype).</b> EBITDAR adds annual rent back to EBITDA, and enterprise value is re-capitalised on one house rule &mdash; each name&rsquo;s reported lease liability stripped out and a uniform rent &times; '+LN.capMult+' added back &mdash; applied identically to the subject and every peer. This removes each company&rsquo;s own tenure judgment and the AASB 16-vs-US GAAP (ASC 842) EBITDA difference, so EV/EBITDAR compares like with like. '+(LN.note||'')+'</div>'; }
    return h; }
  function mwRender(cont){ if(!cont||!MU) return; var m=muMetric(), b=muBase(), h='';
    h+='<p style="margin-top:0;">Two lenses on the same value. <b>Implied by each scenario</b> divides every DCF outcome by a common earnings base to show the multiple it pays; the <b>cross-check</b> runs it the other way — a reference multiple × earnings gives a value to set beside the intrinsic range.</p>';
    h+='<div class="sub" style="margin-bottom:10px; color:var(--warning-tx);">'+MU.note+'</div>';
    h+='<div style="display:flex; gap:16px; flex-wrap:wrap; align-items:flex-start; margin-bottom:10px;">';
    h+='<div><div class="sub" style="margin-bottom:3px;">Earnings basis (subject &amp; peers)</div>';
    Object.keys(MU.bases).forEach(function(bk){ h+='<button class="mu_basis" data-b="'+bk+'" style="font-size:12px; margin-right:4px; '+(bk===ms.basis?'border-color:var(--bdinfo); color:var(--info-tx);':'')+'">'+MU.bases[bk].label+'</button>'; });
    h+='</div><div><div class="sub" style="margin-bottom:3px;">Multiple</div>';
    muMetrics().forEach(function(mm){ h+='<button class="mu_metric" data-m="'+mm.k+'" style="font-size:12px; margin-right:4px; '+(mm.k===ms.metric?'border-color:var(--bdinfo); color:var(--info-tx);':'')+'">'+mm.label+'</button>'; });
    h+='</div></div>';
    h+='<div style="background:var(--secondary); border-radius:8px; padding:9px 11px; font-size:12.5px; margin-bottom:12px;"><b>'+b.label+'</b>'+(b.consensus?' <span class="sub">(our build)</span>':'')+' ('+CFG.ccy+' m): EBITDA '+muN(b.ebitda)+(MU.leaseNeutral?' · EBITDAR '+muN(muEbitdar(b)):'')+' · EBIT '+muN(b.ebit)+' · net income '+muN(b.ni)+' · EPS '+CFG.ccy+' '+(b.ni/CFG.shares).toFixed(2)+(b.consensus?'<div style="margin-top:5px; padding-top:5px; border-top:0.5px solid var(--bd);"><b>Consensus</b> <span class="sub" style="color:var(--warning-tx);">(mock — pending EODHD / broker feed)</span> ('+CFG.ccy+' m): EBITDA '+muN(b.consensus.ebitda)+' · EBIT '+muN(b.consensus.ebit)+' · net income '+muN(b.consensus.ni)+' · EPS '+CFG.ccy+' '+(b.consensus.ni/CFG.shares).toFixed(2)+'</div>':'')+'<div class="sub" style="margin-top:4px;">'+b.note+'</div>'+(b.consensus?'<div class="sub" style="margin-top:3px;">The implied multiples below are computed on the <b>our-build</b> earnings, so they tie to the DCF; consensus is shown alongside for comparison.</div>':'')+'</div>';
    h+=mwCompsWorkbench();
    var mkt=muImplied(CFG.market,m,b);
    h+='<div class="hd" style="margin:4px 0 4px;">Implied '+m.label+' by scenario</div><div style="overflow-x:auto;"><table style="font-size:12.5px; border-collapse:collapse; width:100%; white-space:nowrap;">';
    h+='<tr><td class="sub" style="padding:3px 8px 3px 0;">Scenario</td><td class="sub" style="padding:3px 8px; text-align:right;">Value / share</td>'+(muIsEV(m)?'<td class="sub" style="padding:3px 8px; text-align:right;">'+(m.kind==='evr'?'Adj. EV':'EV')+'</td>':'')+'<td class="sub" style="padding:3px 8px; text-align:right;">Implied '+m.label+'</td></tr>';
    CFG.scenarios.slice().sort(function(a,c){return c.v-a.v;}).forEach(function(sc){ var im=muImplied(sc.v,m,b), isB=(sc.kind==='broker');
      h+='<tr style="border-top:0.5px solid var(--bd);"><td style="padding:5px 8px 5px 0; '+(sc===activeScen()?'font-weight:600; color:var(--info-tx);':'')+'">'+sc.n+(isB?' <span class="sub">(ref)</span>':'')+'</td><td style="padding:5px 8px; text-align:right;">'+CFG.ccy+' '+sc.v.toFixed(CFG.dp)+'</td>'+(muIsEV(m)?'<td style="padding:5px 8px; text-align:right; color:var(--text2);">'+muN(muEVof(m,sc.v))+'</td>':'')+'<td style="padding:5px 8px; text-align:right; font-weight:600;">'+muX(im)+'</td></tr>'; });
    h+='<tr style="border-top:1px solid var(--bd2);"><td style="padding:5px 8px 5px 0; color:var(--text2);">Market-implied (price '+CFG.ccy+' '+CFG.market.toFixed(CFG.dp)+')</td><td></td>'+(muIsEV(m)?'<td></td>':'')+'<td style="padding:5px 8px; text-align:right; color:var(--text2);">'+muX(mkt)+'</td></tr>';
    h+='<tr><td style="padding:5px 8px 5px 0; color:var(--warning-tx);">Peer median (mock, selected peers)</td><td></td>'+(muIsEV(m)?'<td></td>':'')+'<td style="padding:5px 8px; text-align:right; color:var(--warning-tx);">'+muX(peerMult(m))+'</td></tr>';
    h+='</table></div><div class="sub" style="margin-top:6px; line-height:1.5;">The denominator is held at the '+b.label.toLowerCase()+' base, so this reads each scenario as a multiple of <i>today’s</i> earnings — higher-value scenarios pay up to a higher multiple. Where a scenario sits above the peer median, the DCF is asking the market to re-rate.</div>';
    h+='<div class="hd" style="margin:16px 0 4px;">Cross-check — value from a '+m.label+' multiple</div>';
    h+='<div style="display:flex; gap:8px; align-items:flex-end; flex-wrap:wrap; margin-bottom:8px;"><div><div class="sub" style="margin-bottom:3px;">Reference</div>';
    [['peer','Peer median'],['market','Market'],['custom','Custom']].forEach(function(r){ h+='<button class="mu_ref" data-r="'+r[0]+'" style="font-size:12px; margin-right:4px; '+(r[0]===ms.refMode?'border-color:var(--bdinfo); color:var(--info-tx);':'')+'">'+r[1]+'</button>'; });
    var rm=muRefMult(m,mkt);
    h+='</div><div><div class="sub" style="margin-bottom:3px;">Multiple</div><input id="mu_custom" type="number" step="0.5" value="'+rm.toFixed(1)+'" '+(ms.refMode==='custom'?'':'disabled')+' style="width:80px; font:inherit; padding:3px 6px; border:0.5px solid var(--bd2); border-radius:6px; background:var(--primary); color:var(--text);"></div></div>';
    var pv=muValue(rm,m,b), mt=muScenByKind('live'), evs=editableScens().map(function(s){return s.v;}), lo=Math.min.apply(null,evs), hi=Math.max.apply(null,evs);
    h+='<div style="background:var(--secondary); border-radius:8px; padding:11px 13px;"><div style="font-size:13px;">'+muX(rm)+' '+m.label+' × '+CFG.ccy+' '+muN(muDen(m,b))+' m'+(muIsEV(m)?(' = '+(m.kind==='evr'?'adj. EV':'EV')+' '+muN(rm*muDen(m,b))+' → less '+(m.kind==='evr'?'adjusted net obligations':'net debt')+' '+muN(muBridge(m))+' → equity '+muN(rm*muDen(m,b)-muBridge(m))):'')+'</div><div style="font-size:15px; font-weight:600; margin-top:5px;">→ '+CFG.ccy+' '+pv.toFixed(CFG.dp)+' per share</div><div class="sub" style="margin-top:5px;">vs Muddle Through '+CFG.ccy+' '+(mt?mt.v.toFixed(CFG.dp):'—')+' · vs market '+CFG.ccy+' '+CFG.market.toFixed(CFG.dp)+' · DCF scenario range '+CFG.ccy+' '+lo.toFixed(CFG.dp)+'–'+hi.toFixed(CFG.dp)+'</div></div>';
    cont.innerHTML=h; mwWire(cont);
  }
  function mwWire(cont){ function on(sel,ev,fn){ Array.prototype.forEach.call(cont.querySelectorAll(sel),function(e){ e.addEventListener(ev,fn); }); }
    on('.mu_basis','click',function(){ ms.basis=this.getAttribute('data-b'); mwRender(cont); });
    on('.mu_metric','click',function(){ ms.metric=this.getAttribute('data-m'); mwRender(cont); });
    on('.mu_ref','click',function(){ ms.refMode=this.getAttribute('data-r'); mwRender(cont); });
    on('.mu_comp','click',function(){ var ci=+this.getAttribute('data-ci'); if(BW&&BW.comparables[ci]){ BW.comparables[ci]._sel=this.checked; } mwRender(cont); });
    on('.mu_fin','change',function(){ var ci=+this.getAttribute('data-ci'), f=this.getAttribute('data-f'), isB=this.getAttribute('data-basis')==='1', v=parseFloat(this.value); var mf=(BW&&BW.comparables[ci])?BW.comparables[ci].mfin:null; if(mf&&!isNaN(v)){ if(isB){ if(mf[f]==null||typeof mf[f]!=='object') mf[f]={}; mf[f][ms.basis]=v; } else { mf[f]=v; } } mwRender(cont); });
    var ci=cont.querySelector('#mu_custom'); if(ci) ci.addEventListener('change',function(){ ms.custom=this.value; ms.refMode='custom'; mwRender(cont); });
  }

  function dcfTableHTML(sc){ var v=sc.vals||{}, re=(v.re!=null?+v.re:CFG.cp.re0*100), g=(v.g!=null?+v.g:CFG.cp.g0*100), gr=5;
    var reF=re/100, gF=g/100, grF=gr/100, per=sc.v, ev=per*CFG.shares+CFG.netDebt;
    var den=0; for(var t=1;t<=5;t++){ den+=Math.pow(1+grF,t-1)/Math.pow(1+reF,t); }
    den+=Math.pow(1+grF,4)*(1+gF)/((reF-gF)*Math.pow(1+reF,5));
    var F1=ev/den, yrs=['FY27','FY28','FY29','FY30','FY31'], fc=[],df=[],pv=[], pvexp=0;
    for(var t=0;t<5;t++){ var f=F1*Math.pow(1+grF,t), d=1/Math.pow(1+reF,t+1); fc.push(f); df.push(d); pv.push(f*d); pvexp+=f*d; }
    var tv=fc[4]*(1+gF)/(reF-gF), pvterm=tv/Math.pow(1+reF,5), evchk=pvexp+pvterm;
    function n0(x){ return Math.round(x).toLocaleString(); }
    var h='<p style="margin-top:0;">Traditional DCF for the selected scenario <b>'+sc.n+'</b> — an explicit five-year FCFF stream discounted at the scenario rate, bridged from enterprise value to equity. Reduced-form-consistent: the explicit stream reconstructs the headline EV (tie check below). '+CFG.ccy+' m unless noted.</p>';
    h+='<div class="sub" style="margin-bottom:8px;">Discount rate '+re.toFixed(2)+'% · terminal growth '+g.toFixed(2)+'% · near-term FCFF growth '+gr.toFixed(0)+'% · net debt '+n0(CFG.netDebt)+' · shares '+n0(CFG.shares)+'m.</div>';
    h+='<div style="overflow-x:auto;"><table style="font-size:12px; border-collapse:collapse; white-space:nowrap; width:100%;">';
    h+='<tr><td class="sub" style="padding:3px 8px 3px 0;">Explicit period</td>'+yrs.map(function(y){return '<td class="sub" style="padding:3px 8px; text-align:right;">'+y+'</td>';}).join('')+'</tr>';
    h+='<tr style="border-top:0.5px solid var(--bd);"><td style="padding:5px 8px 5px 0;">FCFF</td>'+fc.map(function(f){return '<td style="padding:5px 8px; text-align:right;">'+n0(f)+'</td>';}).join('')+'</tr>';
    h+='<tr><td style="padding:5px 8px 5px 0;">Discount factor</td>'+df.map(function(d){return '<td style="padding:5px 8px; text-align:right; color:var(--text2);">'+d.toFixed(3)+'</td>';}).join('')+'</tr>';
    h+='<tr><td style="padding:5px 8px 5px 0; font-weight:500;">PV of FCFF</td>'+pv.map(function(x){return '<td style="padding:5px 8px; text-align:right; font-weight:500;">'+n0(x)+'</td>';}).join('')+'</tr>';
    h+='</table></div>';
    function row(l,val,bold,paren){ return '<tr style="border-top:0.5px solid var(--bd);"><td style="padding:6px 8px 6px 0; '+(bold?'font-weight:600;':'')+'">'+l+'</td><td style="padding:6px 0; text-align:right; '+(bold?'font-weight:600;':'')+'">'+(paren?'('+n0(Math.abs(val))+')':n0(val))+'</td></tr>'; }
    h+='<table style="width:100%; font-size:13px; margin-top:8px;">';
    h+=row('Sum PV of explicit FCFF (FY27–FY31)',pvexp);
    h+=row('Terminal value (Gordon, g '+g.toFixed(2)+'%)',tv);
    h+=row('PV of terminal value',pvterm);
    h+=row('Enterprise value',evchk,true);
    h+=row('Less: net debt',-CFG.netDebt,false,true);
    h+=row('Equity value',evchk-CFG.netDebt,true);
    h+='<tr style="border-top:0.5px solid var(--bd);"><td style="padding:6px 8px 6px 0;">÷ shares (m)</td><td style="padding:6px 0; text-align:right;">'+n0(CFG.shares)+'</td></tr>';
    h+='<tr style="border-top:1px solid var(--bd2);"><td style="padding:6px 8px 6px 0; font-weight:700;">Value per share ('+CFG.ccy+')</td><td style="padding:6px 0; text-align:right; font-weight:700;">'+per.toFixed(CFG.dp)+'</td></tr>';
    h+='</table>';
    h+='<div class="sub" style="margin-top:6px;">Tie check: reconstructed EV '+n0(evchk)+' vs headline EV '+n0(ev)+' (Δ '+(evchk-ev).toFixed(1)+'). Terminal value is ~'+Math.round(pvterm/evchk*100)+'% of enterprise value. FCFF year 1 solved so the explicit stream reproduces the reduced-form EV; when the full DCF engine lands, its per-year projection lines replace this cascade in place.</div>';
    var dd=CFG.dcfDetail;
    if(dd){
      h+='<details class="thy" style="margin-top:10px;"><summary>Net debt — breakdown</summary><div class="thybody"><table style="width:100%; font-size:12.5px;">';
      dd.netDebt.forEach(function(r){ var bold=(r[2]==='sub'||r[2]==='tot'); h+='<tr style="'+(bold?'border-top:0.5px solid var(--bd2);':'')+'"><td style="padding:4px 8px 4px 0; '+(bold?'font-weight:600;':'')+'">'+r[0]+'</td><td style="padding:4px 0; text-align:right; '+(bold?'font-weight:600;':'')+'">'+(r[1]<0?'('+Math.abs(r[1]).toLocaleString()+')':r[1].toLocaleString())+'</td></tr>'; });
      h+='</table><div class="sub" style="margin-top:6px; line-height:1.5;">'+dd.netDebtNote+'</div></div></details>';
      if(dd.leaseMat){ var lm=dd.leaseMat;
        var evPct=lm.liab/lm.ev*100, psImp=lm.liab/lm.shares, psPct=psImp/CFG.cp.base*100, cRep=lm.leaseCost/lm.ebitdaRep*100, cFwd=lm.leaseCost/lm.ebitdaFwd*100;
        h+='<details class="thy" open><summary>Lease materiality (AASB 16)</summary><div class="thybody" style="font-size:12.5px; line-height:1.6;"><table style="width:100%; font-size:12.5px;">';
        h+='<tr><td style="padding:3px 8px 3px 0;">AASB 16 lease liability</td><td style="text-align:right;">'+CFG.ccy+' '+lm.liab+'m</td></tr>';
        h+='<tr><td style="padding:3px 8px 3px 0;">&nbsp;&nbsp;÷ enterprise value ('+lm.ev.toLocaleString()+')</td><td style="text-align:right;">'+evPct.toFixed(1)+'%</td></tr>';
        h+='<tr><td style="padding:3px 8px 3px 0;">&nbsp;&nbsp;per-share impact (÷ '+lm.shares.toLocaleString()+'m shares)</td><td style="text-align:right;">'+CFG.ccy+' '+psImp.toFixed(2)+' (~'+psPct.toFixed(0)+'% of value)</td></tr>';
        h+='<tr><td style="padding:3px 8px 3px 0;">Annual lease cost (est. RoU dep + interest ≈ '+lm.leaseCost+'m)</td><td></td></tr>';
        h+='<tr><td style="padding:3px 8px 3px 0;">&nbsp;&nbsp;÷ EBITDA — reported '+lm.ebitdaRep+' / forward '+lm.ebitdaFwd+'</td><td style="text-align:right;">'+cRep.toFixed(1)+'% / '+cFwd.toFixed(1)+'%</td></tr>';
        h+='</table><div class="sub" style="margin-top:6px; line-height:1.5;">Gate: if the lease liability exceeds ~'+lm.threshold+' of EV, or annual lease cost exceeds ~'+lm.threshold+' of EBITDA, the name is <b>lease-sensitive</b> and the cross-company multiples switch to a lease-neutral (EV/EBITDAR) basis — stripping out tenure-judgment and AASB 16-vs-US GAAP differences. Below that, Approach A (leases in net debt) suffices.</div>';
        h+='<div style="margin-top:8px; display:inline-block; padding:4px 10px; border-radius:6px; font-weight:600; background:var(--secondary);">Verdict: '+lm.verdict+' — Approach A applied (leases in net debt); no lease-neutral peer basis needed for DNL.</div>';
        h+='</div></details>';
      }
      h+='<details class="thy"><summary>Terminal value — calculation</summary><div class="thybody" style="font-size:12.5px; line-height:1.7;">Gordon growth on the final explicit year:<br>Terminal-year FCFF = FY31 FCFF '+n0(fc[4])+' × (1 + g '+g.toFixed(2)+'%) = '+n0(fc[4]*(1+gF))+'<br>Terminal value = '+n0(fc[4]*(1+gF))+' ÷ (Re '+re.toFixed(2)+'% − g '+g.toFixed(2)+'%) = <b>'+n0(tv)+'</b><br>PV of terminal value = '+n0(tv)+' ÷ (1 + Re)⁵ = <b>'+n0(pvterm)+'</b><br>Terminal value is ~'+Math.round(pvterm/evchk*100)+'% of enterprise value.</div></details>';
      if(sc.kind==='live' && dd.mt){ var mt=dd.mt;
        h+='<details class="thy" open><summary>Operating build — revenue × margin → EBIT (Muddle Through)</summary><div class="thybody"><div style="overflow-x:auto;"><table style="font-size:12px; border-collapse:collapse; white-space:nowrap; width:100%;">';
        h+='<tr><td class="sub" style="padding:3px 8px 3px 0;"></td>'+mt.years.map(function(y){return '<td class="sub" style="padding:3px 8px; text-align:right;">'+y+'</td>';}).join('')+'</tr>';
        h+='<tr style="border-top:0.5px solid var(--bd);"><td style="padding:4px 8px 4px 0;">Revenue</td>'+mt.revenue.map(function(v){return '<td style="padding:4px 8px; text-align:right;">'+v.toLocaleString()+'</td>';}).join('')+'</tr>';
        h+='<tr><td style="padding:4px 8px 4px 0; color:var(--text2);">growth %</td>'+mt.revenue.map(function(v,i){var g2=(i===0)?null:(v/mt.revenue[i-1]-1)*100; return '<td style="padding:4px 8px; text-align:right; color:var(--text3);">'+(g2==null?'—':g2.toFixed(1)+'%')+'</td>';}).join('')+'</tr>';
        h+='<tr><td style="padding:4px 8px 4px 0; color:var(--text2);">EBIT margin (base '+mt.baseMargin+'% + peer-gap − gas)</td>'+mt.ebit.map(function(e,i){return '<td style="padding:4px 8px; text-align:right;">'+(e/mt.revenue[i]*100).toFixed(1)+'%</td>';}).join('')+'</tr>';
        h+='<tr style="border-top:0.5px solid var(--bd);"><td style="padding:4px 8px 4px 0; font-weight:600;">EBIT</td>'+mt.ebit.map(function(v){return '<td style="padding:4px 8px; text-align:right; font-weight:600;">'+v.toLocaleString()+'</td>';}).join('')+'</tr>';
        h+='<tr><td style="padding:4px 8px 4px 0; color:var(--text2);">applied tax %</td>'+mt.taxGlide.map(function(t){return '<td style="padding:4px 8px; text-align:right; color:var(--text3);">'+t.toFixed(2)+'%</td>';}).join('')+'</tr>';
        h+='<tr><td style="padding:4px 8px 4px 0;">NOPAT = EBIT × (1−tax)</td>'+mt.ebit.map(function(e,i){return '<td style="padding:4px 8px; text-align:right;">'+Math.round(e*(1-mt.taxGlide[i]/100)).toLocaleString()+'</td>';}).join('')+'</tr>';
        h+='</table></div><div class="sub" style="margin-top:6px; line-height:1.5;">'+mt.note+'</div></div></details>';
      } else if(dd.mt){ h+='<details class="thy"><summary>Operating build — revenue × margin → EBIT</summary><div class="thybody"><div class="sub" style="line-height:1.5;">The revenue × margin operating build is shown for the Muddle Through base case (audited-workbook §11 traceability). Per-scenario operating projections arrive with the DCF engine; this scenario uses the reduced-form reconstruction above, which reproduces its enterprise value.</div></div></details>'; }
    }
    return h; }

  // init
  selectScenario(CFG.activeIdx);
  document.getElementById('topnote').innerHTML=CFG.topnote;
  document.getElementById('footnote').innerHTML=CFG.footnote;
  document.getElementById('mklab').textContent=CFG.mklab;
  document.getElementById('brlab').textContent=CFG.brlab;
  document.getElementById('m4lab').textContent=CFG.metric4.label;
  document.getElementById('m4val').textContent=CFG.metric4.value;
  if(CFG.pvsub) document.getElementById('pvsub').textContent=CFG.pvsub;
  markExplore('forces'); openDetail('forces', true);
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
    # rows: [label, bestpractice, did]
    h='<div style="margin-top:12px; border-top:0.5px solid var(--bd); padding-top:10px;"><div class="hd" style="margin-bottom:2px;">Practical theory — best practice vs what we did</div><div class="sub" style="margin-bottom:6px;">click any element to compare the best-practice approach with what this valuation did</div>'
    for r in rows:
        h+='<details class="thy"><summary>%s</summary><div class="thybody">'%r[0]
        h+='<div class="thytag" style="color:var(--success-tx);">Best practice</div><div style="margin:2px 0 8px;">%s</div>'%r[1]
        h+='<div class="thytag" style="color:var(--warning-tx);">What we did (VCC)</div><div style="margin:2px 0 0;">%s</div>'%r[2]
        h+='</div></details>'
    return h+'</div>'

def assum_table(rows):
    h='<p>Tags: %s stated · %s calculated · %s analyst call.</p><table style="width:100%%; font-size:13px;">'%(tag('disclosed'),tag('derived'),tag('judgment'))
    for r in rows:
        h+='<tr style="border-bottom:0.5px solid var(--bd);"><td style="padding:6px 8px 6px 0; font-weight:500; white-space:nowrap; vertical-align:top;">%s</td><td style="padding:6px 8px; white-space:nowrap; vertical-align:top;">%s</td><td style="padding:6px 8px; vertical-align:top;">%s</td><td style="padding:6px 0; color:var(--text2); vertical-align:top;">%s</td></tr>'%(r[0],r[1],tag(r[2]),r[3])
    return h+'</table>'

def _fmtm(v):
    if v is None: return ''
    n='{:,.0f}'.format(abs(v))
    return '('+n+')' if v<0 else n

def financials_html(fin):
    yrs=fin['years']; real=fin['real']
    def hdr():
        h='<tr><td class="sub" style="padding:4px 8px 4px 0;"></td>'
        for i,y in enumerate(yrs):
            badge='' if real[i] else ' <span style="font-size:9px; color:var(--warning-tx);">mock</span>'
            st='' if real[i] else 'color:var(--text3);'
            h+='<td class="sub" style="padding:4px 8px; text-align:right; %s">%s%s</td>'%(st,y,badge)
        return h+'</tr>'
    def rws(items):
        h=''
        for it in items:
            lbl=it[0]; vals=it[1]; bold=len(it)>2 and it[2]; fw='font-weight:600;' if bold else ''
            h+='<tr style="border-top:0.5px solid var(--bd);"><td style="padding:5px 8px 5px 0; %s white-space:nowrap;">%s</td>'%(fw,lbl)
            for i,v in enumerate(vals):
                col='' if real[i] else 'color:var(--text3);'
                h+='<td style="padding:5px 8px; text-align:right; %s %s">%s</td>'%(fw,col,_fmtm(v))
            h+='</tr>'
        return h
    def tbl(title,items):
        return '<div class="hd" style="margin:14px 0 4px;">%s</div><div style="overflow-x:auto;"><table style="font-size:12px; border-collapse:collapse; white-space:nowrap; width:100%%;">%s%s</table></div>'%(title,hdr(),rws(items))
    h='<p>%s</p>'%fin['intro']
    h+='<div class="sub" style="margin-bottom:4px; color:var(--warning-tx);">%s</div>'%fin['note']
    h+='<div class="sub" style="margin-bottom:2px;">All figures %s &middot; financial year to %s.</div>'%(fin['ccy'],fin['fye'])
    h+=tbl('Income statement',fin['pl']); h+=tbl('Balance sheet',fin['bs']); h+=tbl('Cash flow',fin['cf'])
    if fin.get('foot'): h+='<div class="sub" style="margin-top:10px; line-height:1.5;">%s</div>'%fin['foot']
    return h

OUTDIR=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
import os as _os
_CFGP=_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'cfgs_gen.json')
CFGS=json.load(open(_CFGP if _os.path.exists(_CFGP) else '/tmp/cfgs.json'))
for key,cfg in CFGS.items():
    cfg['detail']={
        'forces': forces_table(cfg['_forces']['intro'], cfg['_forces']['rows'], cfg['_forces']['net']),
        'position': cfg['_position'],
        'discount': cfg['_discount'] + '<!--BWSLOT-->' + dr_theory_html(cfg.get('_drtheory', [])),
        'assum': assum_table(cfg['_assum'])
    }
    cfg['forcesData']=cfg['_forces']
    if '_financials' in cfg: cfg['detail']['financials']=financials_html(cfg['_financials'])
    for kk in ['_forces','_position','_discount','_assum','_drtheory','_financials']: cfg.pop(kk, None)
    html=SCAFFOLD.replace('__CFG__', json.dumps(cfg)).replace('__COMPANY__', cfg['company']).replace('__CCYNOTE__', cfg['ccynote']).replace('__CCY__', cfg['ccy'])
    out=os.path.join(OUTDIR, '%s_scenario_interface.html'%key)
    open(out,'w',encoding='utf-8').write(html)
    print('wrote',out,len(html),'bytes')
