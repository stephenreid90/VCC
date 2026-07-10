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
    <div class="sub" style="margin-top:6px;"><span style="color:var(--info-tx);">▮</span> Muddle Through (live) · <span style="color:var(--user-tx);">▮</span> your scenarios · <span style="color:var(--warning-tx);">▮</span> average broker · dashed = market</div></div>
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
  var LSKEY='vcc_userscen_'+CFG.companyShort;
  var liveVals={}; CFG.sliders.forEach(function(s){ liveVals[s.k]=s.def; });
  var st=liveVals;                 // working slider state = current target's vals (by reference)
  var target='live';               // 'live' | user-id | null (read-only built-in)
  var applyGlobal=false;
  var user=loadUser();
  user.forEach(function(u){ CFG.scenarios.push({n:u.name, v:0, kind:'user', uid:u.id}); });

  function loadUser(){ try{ return JSON.parse(localStorage.getItem(LSKEY))||[]; }catch(e){ return []; } }
  function saveUser(){ try{ localStorage.setItem(LSKEY, JSON.stringify(user)); }catch(e){} }
  function findUser(id){ for(var i=0;i<user.length;i++){ if(user[i].id===id) return user[i]; } return null; }
  function scenByUid(id){ for(var i=0;i<CFG.scenarios.length;i++){ if(CFG.scenarios[i].uid===id) return CFG.scenarios[i]; } return null; }
  function sliderByKey(k){ for(var i=0;i<CFG.sliders.length;i++){ if(CFG.sliders[i].k===k) return CFG.sliders[i]; } return null; }
  function activeScen(){ return CFG.scenarios[CFG.activeIdx]; }

  function fmt(s,v){ return v.toFixed(s.dec)+s.suf; }
  function computeVals(vals){
    var p=CFG.cp, Re=vals.re/100, g=vals.g/100, m=vals.m, tax=vals.tax/100, x=vals[p.xKey];
    var term=Math.pow((p.re0-p.g0)/(Re-g), p.wTerm);
    return p.base*term*(m/p.m0)*((1-tax)/(1-p.tax0))*(1+(x-p.x0)*p.xk);
  }
  function compute(){ return computeVals(st); }
  user.forEach(function(u){ var sc=scenByUid(u.id); if(sc) sc.v=computeVals(u.vals); });

  // apply one input change to every editable scenario (global mode)
  function propagate(k,v){
    liveVals[k]=v; CFG.scenarios[CFG.liveIdx].v=computeVals(liveVals);
    user.forEach(function(u){ u.vals[k]=v; var sc=scenByUid(u.id); if(sc) sc.v=computeVals(u.vals); });
    saveUser();
  }
  // set input k=v on the current target, honouring the global toggle; refresh sliders + bars
  function setInput(k,v){
    st[k]=v;
    if(applyGlobal){ propagate(k,v); }
    else if(target!=='live'){ var u=findUser(target); if(u){ u.vals=st; saveUser(); } }
    syncSliders(); render();
  }

  function updateCards(v){
    var sc=activeScen(); var show=(v!==undefined && v!==null)?v:sc.v;
    document.getElementById('pv').textContent=show.toFixed(CFG.dp);
    var vm=(show/CFG.market-1)*100, vb=(show/CFG.broker-1)*100;
    var em=document.getElementById('vmkt'); em.textContent=(vm>=0?'+':'')+vm.toFixed(0)+'%'; em.style.color=vm>=0?'var(--success-tx)':'var(--danger-tx)';
    document.getElementById('vbr').textContent=(vb>=0?'+':'')+vb.toFixed(0)+'%';
  }
  function render(){
    if(target===null){ updateCards(); drawBars(); return; }
    var v=compute();
    var sc=(target==='live')?CFG.scenarios[CFG.liveIdx]:scenByUid(target);
    if(sc) sc.v=v;
    if(target!=='live'){ var u=findUser(target); if(u){ u.vals=st; saveUser(); } }
    updateCards(v); drawBars();
  }

  function barColor(k){ return k==='live'?'var(--info-bg)':k==='broker'?'var(--warning-bg)':k==='user'?'var(--user-bg)':'var(--tertiary)'; }
  function txtColor(k){ return k==='live'?'var(--info-tx)':k==='broker'?'var(--warning-tx)':k==='user'?'var(--user-tx)':'var(--text)'; }
  function drawBars(){
    var h='<div style="position:relative;">', mkt=CFG.market/CFG.scale*100;
    CFG.scenarios.forEach(function(s,i){
      var w=Math.max(0,Math.min(100,s.v/CFG.scale*100)), sel=(i===CFG.activeIdx);
      var del=(s.kind==='user')?'<span class="delu" data-uid="'+s.uid+'" title="delete scenario" style="cursor:pointer; color:var(--text3); padding:0 3px;">×</span>':'';
      h+='<div class="scbar" data-i="'+i+'" style="display:flex; align-items:center; gap:8px; margin-bottom:5px; cursor:pointer; border-radius:5px; padding:1px 2px; '+(sel?'background:var(--secondary);':'')+'">'
       +'<div style="width:122px; font-size:12px; color:'+(sel?'var(--text)':'var(--text2)')+'; font-weight:'+(sel?'500':'400')+'; text-align:right; flex:none; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">'+del+s.n+'</div>'
       +'<div style="flex:1; position:relative; height:19px;"><div style="height:19px; width:'+w+'%; background:'+barColor(s.kind)+'; border-radius:4px; '+(sel?'outline:1.5px solid var(--bdinfo);':'')+'"></div>'
       +'<div style="position:absolute; top:1px; left:calc('+w+'% + 6px); font-size:12px; font-weight:500; color:'+txtColor(s.kind)+'; white-space:nowrap;">'+s.v.toFixed(CFG.dp)+'</div></div></div>';
    });
    h+='<div style="position:absolute; left:130px; right:0; top:0; bottom:14px; pointer-events:none;"><div style="position:absolute; left:'+mkt+'%; top:0; bottom:0; border-left:1.5px dashed var(--text2);"></div></div></div>';
    var bx=document.getElementById('bars'); bx.innerHTML=h;
    Array.prototype.forEach.call(bx.querySelectorAll('.scbar'),function(el){ el.addEventListener('click',function(){ selectBar(parseInt(el.getAttribute('data-i'))); }); });
    Array.prototype.forEach.call(bx.querySelectorAll('.delu'),function(el){ el.addEventListener('click',function(ev){ ev.stopPropagation(); delScenario(el.getAttribute('data-uid')); }); });
  }

  function selectBar(i){
    CFG.activeIdx=i; var sc=CFG.scenarios[i];
    if(sc.kind==='live'){ target='live'; st=liveVals; slidersEnabled(true); syncSliders(); }
    else if(sc.kind==='user'){ target=sc.uid; st=findUser(sc.uid).vals; slidersEnabled(true); syncSliders(); }
    else { target=null; slidersEnabled(false); }
    document.getElementById('selscen').textContent=sc.n;
    updateEditingUI(); updateCards(); drawBars();
    setPanel('world'); markExplore('world');
  }

  // sliders
  var sl=document.getElementById('sliders'); var inputs={};
  CFG.sliders.forEach(function(s){
    var row=document.createElement('div'); row.style.margin='10px 0';
    row.innerHTML='<div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;"><span style="color:var(--text2);">'+s.label+'</span><span style="font-weight:500;" id="o_'+s.k+'"></span></div>';
    var inp=document.createElement('input'); inp.type='range'; inp.min=s.min; inp.max=s.max; inp.step=s.step; inp.value=st[s.k];
    inp.addEventListener('input',function(){ setInput(s.k, parseFloat(inp.value)); });
    row.appendChild(inp); sl.appendChild(row); inputs[s.k]=inp;
    document.getElementById('o_'+s.k).textContent=fmt(s,st[s.k]);
  });
  function syncSliders(){ CFG.sliders.forEach(function(s){ inputs[s.k].value=st[s.k]; var o=document.getElementById('o_'+s.k); if(o) o.textContent=fmt(s,st[s.k]); }); }
  function slidersEnabled(on){ sl.style.opacity=on?'1':'0.45'; sl.style.pointerEvents=on?'auto':'none'; }

  function updateEditingUI(){
    var e=document.getElementById('editing'); if(!e) return; var sc=activeScen();
    if(target==='live') e.innerHTML='editing <b>Muddle Through</b> (live)';
    else if(target===null) e.innerHTML='exploring <b>'+sc.n+'</b> — read-only; pick Muddle Through or a user scenario to edit inputs';
    else e.innerHTML='editing your scenario <b>'+sc.n+'</b> — changes save in this browser';
  }

  document.getElementById('reset').addEventListener('click',function(){ if(target===null) return; CFG.sliders.forEach(function(s){ st[s.k]=s.def; }); if(target!=='live'){ var u=findUser(target); if(u){ u.vals=st; saveUser(); } } syncSliders(); render(); });
  document.getElementById('allassum').addEventListener('click',function(){ setPanel('assum'); markExplore('assum'); openDetail('assum'); });
  document.getElementById('applyall').addEventListener('change',function(){ applyGlobal=this.checked; });
  document.getElementById('addscen').addEventListener('click',function(){
    var name=prompt('Name your scenario (starts from Muddle Through, then flex the inputs):','My scenario '+(user.length+1));
    if(!name) return; name=(''+name).slice(0,40);
    var vals={}; CFG.sliders.forEach(function(s){ vals[s.k]=s.def; });
    var id='u'+Date.now(); user.push({id:id,name:name,vals:vals,forces:{}}); saveUser();
    CFG.scenarios.push({n:name, v:computeVals(vals), kind:'user', uid:id});
    selectBar(CFG.scenarios.length-1);
  });
  function delScenario(id){
    user=user.filter(function(u){ return u.id!==id; }); saveUser();
    CFG.scenarios=CFG.scenarios.filter(function(sc){ return sc.uid!==id; });
    if(target===id){ selectBar(CFG.liveIdx); } else { if(CFG.activeIdx>=CFG.scenarios.length) CFG.activeIdx=CFG.liveIdx; drawBars(); }
  }

  // explore
  var ex=document.getElementById('explore'); var exBtns={};
  Object.keys(CFG.titles).forEach(function(k){ var b=document.createElement('button'); b.textContent=CFG.titles[k]; b.style.fontSize='12px'; b.addEventListener('click',function(){ setPanel(k); markExplore(k); }); ex.appendChild(b); exBtns[k]=b; });
  function markExplore(k){ Object.keys(exBtns).forEach(function(j){ exBtns[j].style.borderColor='var(--bd2)'; }); if(exBtns[k]) exBtns[k].style.borderColor='var(--bdinfo)'; }
  function setPanel(k){
    var d=document.getElementById('detail'); if(d) d.innerHTML='';
    document.getElementById('panel').innerHTML='<div style="font-weight:500; margin-bottom:4px;">'+CFG.titles[k]+'</div><div style="color:var(--text2);">'+CFG.snap[k]+'</div>';
    if(k==='world'){ var t=document.getElementById('wsnaptitle'); if(t) t.textContent=activeScen().n; }
    var m=document.querySelector('#panel .more'); if(m){ m.addEventListener('click',function(){ openDetail(m.getAttribute('data-k')); }); }
  }

  function posb(p){ var bg,tx; if(p==='more favourable'){bg='var(--success-bg)';tx='var(--success-tx)';} else if(p==='less favourable'){bg='var(--danger-bg)';tx='var(--danger-tx)';} else {bg='var(--secondary)';tx='var(--text2)';} return '<span style="font-size:11px; padding:1px 7px; border-radius:6px; background:'+bg+'; color:'+tx+';">'+p+'</span>'; }
  function esc(t){ return (''+t).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;'); }

  function editableInputsTable(){
    var h='<table style="width:100%; font-size:13px;">';
    CFG.sliders.forEach(function(s){
      h+='<tr><td style="padding:4px 8px 4px 0; color:var(--text2);">'+s.label+'</td><td style="padding:4px 0; text-align:right; white-space:nowrap;"><input class="assumInp" data-k="'+s.k+'" type="number" min="'+s.min+'" max="'+s.max+'" step="'+s.step+'" value="'+st[s.k]+'" style="width:82px; text-align:right; font:inherit; padding:2px 6px; border:0.5px solid var(--bd2); border-radius:6px; background:var(--primary); color:var(--text);"> <span class="sub">'+(s.suf.trim()||'')+'</span></td></tr>';
    });
    return h+'</table>';
  }
  function interactiveForces(sc){
    var u=findUser(sc.uid); u.forces=u.forces||{}; var fd=CFG.forcesData;
    var h='<p>'+fd.intro+'</p><p class="sub" style="margin-top:-4px;">The <b>Impact</b> column is editable for your scenario — record how you think each force shifts under it. (Annotation for now; the production engine will feed these into the number.)</p><table style="width:100%; font-size:13px;"><tr><td class="sub" style="padding:4px 8px 4px 0;">Force</td><td class="sub" style="padding:4px 8px;">Industry (rating &amp; why)</td><td class="sub" style="padding:4px 8px;">Company vs industry</td><td class="sub" style="padding:4px 0; text-align:right;">Impact (yours)</td></tr>';
    fd.rows.forEach(function(r,i){ var imp=(u.forces[i]!==undefined)?u.forces[i]:r[4];
      h+='<tr style="border-top:0.5px solid var(--bd);"><td style="padding:7px 8px 7px 0; font-weight:500; white-space:nowrap; vertical-align:top;">'+r[0]+'</td><td style="padding:7px 8px; vertical-align:top; max-width:220px;"><span style="font-weight:500;">'+r[1]+'</span><div style="color:var(--text2); margin-top:2px; font-size:12px;">'+r[2]+'</div></td><td style="padding:7px 8px; vertical-align:top;">'+posb(r[3])+'<div style="color:var(--text2); margin-top:3px; font-size:12px;">'+r[5]+'</div></td><td style="padding:7px 0 7px 8px; text-align:right; vertical-align:top;"><input class="forceInp" data-i="'+i+'" value="'+esc(imp)+'" style="width:92px; text-align:right; font:inherit; font-size:12px; padding:2px 6px; border:0.5px solid var(--bd2); border-radius:6px; background:var(--primary); color:var(--text);"></td></tr>';
    });
    return h+'</table><div style="margin-top:10px; background:var(--secondary); border-radius:8px; padding:10px;"><b>Baseline net offset:</b> '+fd.net+'</div>';
  }
  function userWorldHTML(sc){
    var u=findUser(sc.uid); var rows='';
    CFG.sliders.forEach(function(s){ var uv=u.vals[s.k], dv=s.def, chg=(uv!==dv);
      rows+='<tr style="border-top:0.5px solid var(--bd);"><td style="padding:5px 8px 5px 0; color:var(--text2);">'+s.label+'</td><td style="padding:5px 8px; text-align:right; '+(chg?'font-weight:600;':'color:var(--text3);')+'">'+fmt(s,uv)+'</td><td style="padding:5px 0; text-align:right; color:var(--text3);">'+(chg?('was '+fmt(s,dv)):'—')+'</td></tr>'; });
    var vm=(sc.v/CFG.market-1)*100;
    return '<p style="margin-top:0;">Your own scenario, starting from Muddle Through and re-priced live by the browser-side reduced-form. Value <b>'+CFG.ccy+' '+sc.v.toFixed(CFG.dp)+'</b> ('+(vm>=0?'+':'')+vm.toFixed(0)+'% vs market).</p><table style="width:100%; font-size:13px;"><tr><td class="sub" style="padding:2px 8px 2px 0;">Input</td><td class="sub" style="padding:2px 8px; text-align:right;">Your value</td><td class="sub" style="padding:2px 0; text-align:right;">vs MT</td></tr>'+rows+'</table><p class="sub" style="margin-top:8px;">Edit these on the <b>Assumptions</b> tab (or the sliders), and the Five Forces impacts on the <b>Five Forces</b> tab. Excel download of your scenario as a formula workbook is coming next.</p>';
  }
  function detailHTML(k){
    if(k==='world'){ var sc=activeScen(); if(sc.kind==='user'){ return userWorldHTML(sc); } var nm=sc.n;
      var wd=(CFG.worldDesc&&CFG.worldDesc[nm])?'<div class="thytag" style="color:var(--text3); margin:0 0 4px;">The world</div>'+CFG.worldDesc[nm]:'';
      var cn='<div class="thytag" style="color:var(--text3); margin:14px 0 4px;">What it means for '+CFG.companyShort+'</div>'+(CFG.narr[nm]||CFG.narr._placeholder);
      return wd+cn; }
    if(k==='forces'){ var scf=activeScen(); if(scf.kind==='user'){ return interactiveForces(scf); } return CFG.detail.forces; }
    if(k==='assum'){ var head='';
      if(target!==null){ var lab=(target==='live')?'Muddle Through (live)':activeScen().n;
        head='<div style="border:0.5px solid var(--bd); border-left:2.5px solid var(--user-tx); border-radius:8px; padding:11px 13px; margin-bottom:12px;"><div style="font-weight:600; margin-bottom:2px;">Your inputs — '+lab+'</div><div class="sub" style="margin-bottom:8px;">the value-material inputs; type to override (syncs with the sliders and the live value). The full assumption set is below.</div>'+editableInputsTable()+'</div>'; }
      return head+CFG.detail.assum; }
    if(k==='discount'){ return CFG.detail.discount + (CFG.beta? '<div style="margin-top:14px;"><button id="openbw" style="font-size:13px; padding:6px 12px;">\u03b2 / cost-of-capital workbench \u2192</button><div id="bwrap" style="margin-top:10px;"></div></div>' : ''); }
    if(k==='dcf'){ return CFG.dcf+'<button style="margin-top:12px; font-size:13px; padding:6px 12px;" id="dlbtn">⤓ download all scenarios to Excel</button><div style="font-size:11px; color:var(--text3); margin-top:4px;">one tab per scenario</div>'; }
    return CFG.detail[k]||'';
  }
  function wireEditable(k,d){
    if(k==='assum'){ Array.prototype.forEach.call(d.querySelectorAll('.assumInp'),function(inp){ inp.addEventListener('change',function(){ var key=inp.getAttribute('data-k'); var s=sliderByKey(key); var v=parseFloat(inp.value); if(isNaN(v)){ inp.value=st[key]; return; } v=Math.max(s.min,Math.min(s.max,v)); inp.value=v; setInput(key,v); }); }); }
    if(k==='discount'){ var ob=d.querySelector('#openbw'); if(ob) ob.addEventListener('click',function(){ bwInit(); bwRender(d.querySelector('#bwrap')); ob.style.display='none'; }); }
    if(k==='forces'){ Array.prototype.forEach.call(d.querySelectorAll('.forceInp'),function(inp){ inp.addEventListener('change',function(){ var i=+inp.getAttribute('data-i'); var u=findUser(target); if(!u) return; u.forces=u.forces||{}; u.forces[i]=inp.value; saveUser(); }); }); }
  }
  function openDetail(k){
    var d=document.getElementById('detail');
    d.innerHTML='<div class="detailcard"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;"><h4>'+CFG.titles[k]+'</h4><button id="closeov" aria-label="close" style="padding:2px 9px;">×</button></div><div>'+detailHTML(k)+'</div></div>';
    document.getElementById('closeov').addEventListener('click',function(){ d.innerHTML=''; });
    var dl=document.getElementById('dlbtn'); if(dl) dl.addEventListener('click',function(){ alert('In the live tool this downloads the '+CFG.companyShort+' scenario workbook — one tab per scenario (coming in the next increment).'); });
    wireEditable(k,d);
    d.scrollIntoView({behavior:'smooth', block:'nearest'});
  }

  // ---- Workstream D: cost-of-capital / beta workbench (MOCK data via CFG.beta) ----
  var BW=CFG.beta; var bs=null;
  function bwInit(){
    bs={ idx:BW.indexDefault, win:BW.windowDefault, rf:BW.rf, erp:BW.erp, alpha:BW.alpha,
         relever:false, targetDE:(BW.subject.de||0), showCand:false, comps:BW.comparables.slice(), plot:null };
    bs.comps.forEach(function(c){ c._sel=c.selected; });
    var f=bs.comps.filter(function(c){return c._sel;})[0]; bs.plot=f?f.name:(bs.comps[0]&&bs.comps[0].name);
  }
  function betaOf(c){ var d=c._added?c._data:c.data; return d[bs.idx][bs.win].beta; }
  function pointsOf(c){ var d=c._added?c._data:c.data; return d[bs.idx][bs.win].points; }
  function unlev(bl,tax,de){ return bl/(1+(1-tax)*de); }
  function relev(bu,tax,de){ return bu*(1+(1-tax)*de); }
  function median(a){ if(!a.length) return 0; var b=a.slice().sort(function(x,y){return x-y;}); var m=Math.floor(b.length/2); return b.length%2?b[m]:(b[m-1]+b[m])/2; }
  function selectedComps(){ return bs.comps.filter(function(c){return c._sel;}); }
  function aggBeta(){ var sc=selectedComps(); if(!sc.length) return {beta:0,medL:0,medU:0};
    var medL=median(sc.map(function(c){return betaOf(c);}));
    var medU=median(sc.map(function(c){return unlev(betaOf(c),c.tax,c.gearingDE);}));
    var beta=bs.relever?relev(medU,BW.subject.tax,bs.targetDE):medL;
    return {beta:beta, medL:medL, medU:medU}; }
  function reOf(beta){ return bs.rf + beta*bs.erp + bs.alpha; }
  function impliedDiscount(re){ var t=BW.toDiscount; return (t.mode==='wacc')?(t.wE*re+(1-t.wE)*t.kdAfterTax):re; }
  function jsScatter(beta){ var pts=[]; for(var i=0;i<26;i++){ var x=(Math.random()-0.5)*0.05; pts.push([Math.round(x*1e4)/1e4, Math.round((beta*x+(Math.random()-0.5)*0.016)*1e4)/1e4]); } return pts; }
  function addCand(i){ var cd=BW.candidates[i]; if(cd.addable===false) return;
    var data={}; BW.indices.forEach(function(ix){ data[ix]={}; BW.windows.forEach(function(w){ data[ix][w]={beta:cd.betaHint, points:jsScatter(cd.betaHint)}; }); });
    bs.comps.push({name:cd.name,ticker:cd.ticker,why:cd.why,tax:cd.tax,gearingDE:cd.gearingDE,_sel:true,_added:true,_data:data}); }
  function numField(id,label,v,step){ return '<div><div class="sub">'+label+'</div><input type="number" id="'+id+'" value="'+v+'" step="'+step+'" style="width:74px; font:inherit; padding:3px 6px; border:0.5px solid var(--bd2); border-radius:6px; background:var(--primary); color:var(--text);"></div>'; }
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
  function bwRender(cont){ if(!cont) return;
    var agg=aggBeta(), re=reOf(agg.beta), disc=impliedDiscount(re), t=BW.toDiscount, h='';
    h+='<div style="background:var(--warning-bg); color:var(--warning-tx); border-radius:8px; padding:8px 10px; font-size:12px; margin-bottom:10px;"><b>Mock data.</b> Betas and scatter points are synthetic placeholders shaped like the eventual EODHD feed (peer price series + indices + gearing/tax). To be sourced from Ben&rsquo;s pipeline.</div>';
    h+='<div style="display:flex; flex-wrap:wrap; gap:12px 18px; align-items:flex-end; margin-bottom:12px;">'+numField('bw_rf','Risk-free %',bs.rf,0.05)+numField('bw_erp','ERP %',bs.erp,0.05)+numField('bw_alpha','Alpha %',bs.alpha,0.1);
    h+='<div><div class="sub">Index</div><select id="bw_idx" style="font:inherit; padding:3px 6px; border:0.5px solid var(--bd2); border-radius:6px; background:var(--primary); color:var(--text);">'+BW.indices.map(function(ix){return '<option'+(ix===bs.idx?' selected':'')+'>'+ix+'</option>';}).join('')+'</select></div>';
    h+='<div><div class="sub">Estimation window</div>'+BW.windows.map(function(w){return '<button class="bw_win" data-w="'+w+'" style="font-size:12px; margin-right:4px; '+(w===bs.win?'border-color:var(--bdinfo); color:var(--info-tx);':'')+'">'+w+'</button>';}).join('')+'</div></div>';
    if(!BW.bank){ h+='<label style="display:flex; align-items:center; gap:6px; font-size:12px; color:var(--text2); margin-bottom:10px; flex-wrap:wrap;"><input type="checkbox" id="bw_relev" '+(bs.relever?'checked':'')+'> unlever peers → relever at subject gearing D/E <input type="number" id="bw_de" value="'+bs.targetDE+'" step="0.05" min="0" '+(bs.relever?'':'disabled')+' style="width:64px; font:inherit; padding:2px 6px; border:0.5px solid var(--bd2); border-radius:6px; background:var(--primary); color:var(--text);"></label>'; }
    else { h+='<div class="sub" style="margin-bottom:10px;">Relevering is not applied to banks — beta is used directly (deposits/wholesale funding are operating inputs, not financing).</div>'; }
    h+='<table style="width:100%; font-size:13px;"><tr><td class="sub"></td><td class="sub" style="padding:2px 8px 2px 0;">Comparable</td><td class="sub" style="padding:2px 8px; text-align:right;">Levered β</td><td class="sub" style="padding:2px 8px; text-align:right;">Unlevered β</td><td class="sub"></td></tr>';
    h+='<tr style="border-top:0.5px solid var(--bd);"><td></td><td style="padding:6px 8px 6px 0;"><b>'+BW.subject.name+'</b> <span class="sub">'+BW.subject.ticker+' · subject</span><div class="sub" style="color:var(--danger-tx);">'+BW.subject.measuredNote+'</div></td><td style="padding:6px 8px; text-align:right; font-weight:600;">'+BW.subject.selectedBeta.toFixed(2)+'</td><td style="padding:6px 8px; text-align:right; color:var(--text3);">'+(BW.bank?'—':unlev(BW.subject.selectedBeta,BW.subject.tax,BW.subject.de).toFixed(2))+'</td><td></td></tr>';
    bs.comps.forEach(function(c,ci){ var bl=betaOf(c), bu=unlev(bl,c.tax,c.gearingDE);
      h+='<tr style="border-top:0.5px solid var(--bd);"><td style="padding:6px 4px 6px 0; vertical-align:top;"><input type="checkbox" class="bw_sel" data-ci="'+ci+'" '+(c._sel?'checked':'')+'></td><td style="padding:6px 8px 6px 0;">'+c.name+' <span class="sub">'+c.ticker+'</span>'+(c._added?' <span class="sub" style="color:var(--user-tx);">added</span>':'')+'<details class="thy" style="margin-top:4px;"><summary>why comparable</summary><div class="thybody">'+c.why+'</div></details></td><td style="padding:6px 8px; text-align:right; '+(c._sel?'font-weight:600;':'color:var(--text3);')+'">'+bl.toFixed(2)+'</td><td style="padding:6px 8px; text-align:right; color:var(--text2);">'+(BW.bank?'—':bu.toFixed(2))+'</td><td style="padding:6px 0; text-align:right; vertical-align:top;"><button class="bw_plot" data-name="'+c.name+'" style="font-size:11px; padding:2px 7px; '+(bs.plot===c.name?'border-color:var(--bdinfo);':'')+'">plot</button></td></tr>'; });
    h+='</table>';
    h+='<div style="margin-top:8px;"><button id="bw_find" style="font-size:12px;">'+(bs.showCand?'− hide candidates':'✦ find more comparables')+'</button>';
    if(bs.showCand){ h+='<div style="margin-top:8px; border:0.5px dashed var(--bd2); border-radius:8px; padding:8px 10px;"><div class="sub" style="margin-bottom:6px;">Suggested by the &lsquo;find comparables&rsquo; step — the analyst / AI-judgment part; each comes with a rationale to accept or reject:</div>';
      BW.candidates.forEach(function(cd,i){ h+='<div style="display:flex; gap:8px; align-items:flex-start; margin-bottom:7px;"><button class="bw_add" data-i="'+i+'" '+(cd.addable===false?'disabled title="privately held — no listed beta"':'')+' style="font-size:11px; padding:2px 8px; flex:none;">+ add</button><div style="font-size:12.5px;"><b>'+cd.name+'</b> <span class="sub">'+cd.ticker+' · β≈'+cd.betaHint.toFixed(2)+'</span><div style="color:var(--text2);">'+cd.why+'</div></div></div>'; });
      h+='</div>'; } h+='</div>';
    var pc=bs.comps.filter(function(c){return c.name===bs.plot;})[0];
    if(pc){ h+='<div style="margin-top:12px;"><div class="hd" style="margin-bottom:4px;">Beta regression — '+pc.name+' vs '+bs.idx+' <span class="sub">('+bs.win+')</span></div>'+scatterSVG(pc)+'</div>'; }
    h+='<div style="margin-top:12px; background:var(--secondary); border-radius:8px; padding:11px 13px;">';
    h+='<div style="font-size:13px;">Selected peers ('+selectedComps().length+'): median levered β <b>'+agg.medL.toFixed(2)+'</b>'+(BW.bank?'':' · median unlevered <b>'+agg.medU.toFixed(2)+'</b>')+'</div>';
    h+='<div style="font-size:13px; margin-top:4px;">→ subject β <b>'+agg.beta.toFixed(2)+'</b>'+(bs.relever?(' (relevered at D/E '+bs.targetDE+')'):'')+' · documented judgment '+BW.subject.selectedBeta.toFixed(2)+'</div>';
    h+='<div style="font-size:13px; margin-top:4px;">→ R<sub>e</sub> = '+bs.rf.toFixed(2)+'% + β×'+bs.erp.toFixed(2)+'%'+(bs.alpha?(' + α '+bs.alpha.toFixed(2)+'%'):'')+' = <b>'+re.toFixed(2)+'%</b>'+(t.mode==='wacc'?(' → implied '+t.label+' <b>'+disc.toFixed(2)+'%</b>'):'')+'</div>';
    h+='<button id="bw_apply" style="margin-top:8px; font-size:12px;">apply to the discount-rate slider ('+disc.toFixed(2)+'%)</button></div>';
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
    Array.prototype.forEach.call(cont.querySelectorAll('.bw_sel'),function(cb){ cb.addEventListener('change',function(){ bs.comps[+cb.getAttribute('data-ci')]._sel=cb.checked; bwRender(cont); }); });
    Array.prototype.forEach.call(cont.querySelectorAll('.bw_plot'),function(b){ b.addEventListener('click',function(){ bs.plot=b.getAttribute('data-name'); bwRender(cont); }); });
    on('bw_find','click',function(){ bs.showCand=!bs.showCand; bwRender(cont); });
    Array.prototype.forEach.call(cont.querySelectorAll('.bw_add'),function(b){ b.addEventListener('click',function(){ addCand(+b.getAttribute('data-i')); bwRender(cont); }); });
    on('bw_apply','click',function(){ if(target===null){ alert('Pick Muddle Through or a user scenario first, then apply.'); return; } var s=sliderByKey('re'); var v=impliedDiscount(reOf(aggBeta().beta)); v=Math.max(s.min,Math.min(s.max,v)); setInput('re',v); alert('Applied — discount rate set to '+v.toFixed(2)+'% for '+(target==='live'?'Muddle Through':'your scenario')+'.'); });
  }

  // init
  document.getElementById('selscen').textContent=CFG.scenarios[CFG.activeIdx].n;
  document.getElementById('topnote').innerHTML=CFG.topnote;
  document.getElementById('footnote').innerHTML=CFG.footnote;
  document.getElementById('mklab').textContent=CFG.mklab;
  document.getElementById('brlab').textContent=CFG.brlab;
  document.getElementById('m4lab').textContent=CFG.metric4.label;
  document.getElementById('m4val').textContent=CFG.metric4.value;
  if(CFG.pvsub) document.getElementById('pvsub').textContent=CFG.pvsub;
  updateEditingUI(); slidersEnabled(true);
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
    cfg['forcesData']=cfg['_forces']
    for kk in ['_forces','_position','_discount','_assum','_drtheory']: cfg.pop(kk, None)
    html=SCAFFOLD.replace('__CFG__', json.dumps(cfg)).replace('__COMPANY__', cfg['company']).replace('__CCYNOTE__', cfg['ccynote']).replace('__CCY__', cfg['ccy'])
    out=os.path.join(OUTDIR, '%s_scenario_interface.html'%key)
    open(out,'w',encoding='utf-8').write(html)
    print('wrote',out,len(html),'bytes')
