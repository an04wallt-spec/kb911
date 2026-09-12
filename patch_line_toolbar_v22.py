from pathlib import Path
import re

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='// KB911_V22_LINE_TOOL_AND_REDO'
if marker in s:
    print('v22 already applied')
    raise SystemExit(0)

# --- Toolbar: Line after leader, compact center label, image redo button. ---
old='<button data-tool="leader">Сноска</button>'
if old not in s: raise SystemExit('v22: leader toolbar button not found')
s=s.replace(old, old+'\n  <button data-tool="line">Линия</button>',1)

if '<button id="centerImage">Центрировать картинку</button>' not in s:
    raise SystemExit('v22: centerImage button not found')
s=s.replace('<button id="centerImage">Центрировать картинку</button>','<button id="centerImage">По центру</button>',1)

old='<button id="undoImage" class="mini" title="Вернуть картинку обратно" aria-label="Вернуть картинку обратно">↶</button>'
if old not in s: raise SystemExit('v22: undoImage button not found')
s=s.replace(old,old+'<button id="redoImage" class="mini" title="Вернуть отменённое положение картинки" aria-label="Вернуть отменённое положение картинки">↷</button>',1)

# Slightly smaller status font so the longer tool hints fit the fixed header.
s=s.replace('#status{height:34px;flex:1;min-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#111;font-size:14px;',
            '#status{height:34px;flex:1;min-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#111;font-size:12px;',1)
s=s.replace('#status{height:34px;flex:1;min-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#111;font-size:12px;',
            '#status{height:34px;flex:1;min-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#fff;font-size:12px;',1)
s=s.replace('background:#f4f4f6;border:1px solid #c9c9cf;border-radius:6px}',
            'background:#2563eb;border:1px solid #2563eb;border-radius:6px}',1)

# --- Compact line settings popup. ---
script_anchor='<script>\n(()=>{'
pos=s.find(script_anchor)
if pos<0: raise SystemExit('v22: script anchor not found')
line_popup=r'''
<div id="linePopup" aria-hidden="true" style="position:fixed;z-index:46;width:286px;background:#f7f7f8;border:1px solid #9b9ba0;border-radius:7px;box-shadow:0 14px 40px rgba(0,0,0,.24);display:none;overflow:hidden">
 <div id="linePopupHeader" style="height:32px;display:flex;align-items:center;padding:0 9px;background:#fff;border-bottom:1px solid #d5d5da;cursor:move;font-weight:600;font-size:13px;user-select:none">Линия <span style="flex:1"></span><button id="linePopupClose" class="mini">×</button></div>
 <div style="padding:9px">
  <div class="row">
   <div style="flex:1"><div class="label">Толщина, мм</div><input id="simpleLineWidth" type="number" min="0.1" max="5" step="0.05" value="0.40" style="width:100%"></div>
   <div style="flex:1"><div class="label">Тип линии</div><select id="simpleLineStyle" style="width:100%"><option value="solid">Сплошная</option><option value="dash" selected>Пунктирная</option><option value="dashdot">Пунктир с точкой</option></select></div>
  </div>
  <div class="label">Цвет линии</div><div class="color-row"><input id="simpleLineColor" type="color" value="#ff0000"><span>Линия</span></div>
  <div class="tp-actions"><button id="lineOk" class="primary">OK</button></div>
 </div>
</div>
'''
s=s[:pos]+line_popup+s[pos:]

# Print layout must not include the floating line editor.
s=s.replace('#dimPopup,#textPopup,#leaderPopup,#saveDialog,#imageContextMenu,.selection-ui',
            '#dimPopup,#textPopup,#leaderPopup,#linePopup,#saveDialog,#imageContextMenu,.selection-ui')

# --- Image undo/redo: retain existing one-step behavior, but expose a true redo. ---
s=s.replace('let activeImage=null,imageUndo=null,saveKind=', 'let activeImage=null,imageUndo=null,imageRedo=null,saveKind=',1)

pat=r"function rememberImageGeometry\(g\)\{if\(!g\|\|g\.dataset\.type!=='image'\)return;const r=imageRect\(g\);imageUndo=\{id:g\.dataset\.id,x:r\.x,y:r\.y,w:r\.w,h:r\.h\}\}"
rep="function rememberImageGeometry(g){if(!g||g.dataset.type!=='image')return;const r=imageRect(g);imageUndo={id:g.dataset.id,x:r.x,y:r.y,w:r.w,h:r.h};imageRedo=null}"
s,n=re.subn(pat,rep,s,count=1)
if n!=1: raise SystemExit('v22: rememberImageGeometry not found')

u0=s.find("$('undoImage').onclick=()=>{")
u1=s.find("$('paperSize').onchange",u0)
if u0<0 or u1<0: raise SystemExit('v22: image undo handler range not found')
undo_redo=r'''$('undoImage').onclick=()=>{
 if(!imageUndo){setStatus('Нет предыдущего положения картинки');return}
 const i=[...paper.querySelectorAll('image[data-type=image]')].find(n=>n.dataset.id===imageUndo.id);
 if(!i){imageUndo=null;setStatus('Картинка для возврата не найдена');return}
 const cur=imageRect(i),old={...imageUndo};
 imageRedo={id:i.dataset.id,x:cur.x,y:cur.y,w:cur.w,h:cur.h};imageUndo=null;
 i.setAttribute('x',old.x);i.setAttribute('y',old.y);i.setAttribute('width',old.w);i.setAttribute('height',old.h);
 if(selected===i)drawSelection();setStatus('Предыдущее положение картинки восстановлено. ↷ — вернуть отменённое')
};
$('redoImage').onclick=()=>{
 if(!imageRedo){setStatus('Нет отменённого положения картинки');return}
 const i=[...paper.querySelectorAll('image[data-type=image]')].find(n=>n.dataset.id===imageRedo.id);
 if(!i){imageRedo=null;setStatus('Картинка для возврата не найдена');return}
 const cur=imageRect(i),next={...imageRedo};
 imageUndo={id:i.dataset.id,x:cur.x,y:cur.y,w:cur.w,h:cur.h};imageRedo=null;
 i.setAttribute('x',next.x);i.setAttribute('y',next.y);i.setAttribute('width',next.w);i.setAttribute('height',next.h);
 if(selected===i)drawSelection();setStatus('Отменённое положение картинки возвращено')
};
'''
s=s[:u0]+undo_redo+s[u1:]

# --- Line tool status in the proven tool switch. ---
needle="else if(tool==='leader')setStatus('Сноска: поставьте точку стрелки и протяните к началу полки');else if(!tool)"
if needle not in s: raise SystemExit('v22: setTool leader status anchor not found')
s=s.replace(needle,"else if(tool==='leader')setStatus('Сноска: поставьте точку стрелки и протяните к началу полки');else if(tool==='line')setStatus('Линия: поставьте первую точку и протяните к точке излома');else if(!tool)",1)

# --- Line runtime lives inside the existing application IIFE. ---
anchor='// ---------- Native KB911 project format ----------'
pos=s.find(anchor)
if pos<0: raise SystemExit('v22: native project anchor not found')
code=r'''
// KB911_V22_LINE_TOOL_AND_REDO
let simpleLineDraft=null,simpleLinePreview=null,simpleLineDrag=null,simpleLinePopupDrag=null;
let simpleLineDefaults={lineWidth:'0.40',lineColor:'#ff0000',lineStyle:'dash'};
function simpleLinePts(g){
 const p1=parsePt(g.dataset.p1||'0,0'),p2=parsePt(g.dataset.p2||'0,0'),dir=(+g.dataset.dir||1),shelf=Math.max(0,+g.dataset.shelf||40);
 return {p1,p2,p3:{x:p2.x+dir*shelf,y:p2.y},dir,shelf};
}
function simpleLineDash(style){return style==='dash'?'4 2':style==='dashdot'?'4 2 .8 2':''}
function renderSimpleLine(g){
 while(g.firstChild)g.removeChild(g.firstChild);
 const {p1,p2,p3}=simpleLinePts(g),c=g.dataset.lineColor||'#111111',lw=Math.max(.1,+g.dataset.lineWidth||.4),dash=simpleLineDash(g.dataset.lineStyle||'solid');
 const attrs={d:`M ${p1.x} ${p1.y} L ${p2.x} ${p2.y} L ${p3.x} ${p3.y}`,fill:'none',stroke:c,'stroke-width':lw,'stroke-linecap':'butt','stroke-linejoin':'miter','vector-effect':'non-scaling-stroke'};
 if(dash)attrs['stroke-dasharray']=dash;
 g.appendChild(el('path',attrs));
 g.appendChild(el('path',{d:attrs.d,fill:'none',stroke:'transparent','stroke-width':8,class:'simple-line-hit hover-movable'}));
}
function drawSimpleLineHandles(g){
 if(!g||g.dataset.type!=='line')return;
 const {p1,p2,p3}=simpleLinePts(g);
 [[p1,'p1'],[p2,'p2'],[p3,'p3']].forEach(([q,k])=>paper.appendChild(el('circle',{cx:q.x,cy:q.y,r:1.55,class:'handle selection-ui simple-line-handle','data-owner':g.dataset.id,'data-line-handle':k,style:'cursor:crosshair;fill:#fff;stroke:#2563eb;stroke-width:.55'})));
}
function openSimpleLinePopup(g){
 if(!g||g.dataset.type!=='line')return;selected=g;lastEditable=g;
 $('simpleLineWidth').value=g.dataset.lineWidth||simpleLineDefaults.lineWidth;
 $('simpleLineStyle').value=g.dataset.lineStyle||simpleLineDefaults.lineStyle;
 $('simpleLineColor').value=g.dataset.lineColor||simpleLineDefaults.lineColor;
 const q=$('linePopup');q.style.display='block';q.classList.add('open');q.setAttribute('aria-hidden','false');
 if(!q.style.left){q.style.left=Math.max(10,(innerWidth-q.offsetWidth)/2)+'px';q.style.top=Math.max(60,(innerHeight-q.offsetHeight)/2)+'px'}
}
function closeSimpleLinePopup(){const q=$('linePopup');if(!q)return;q.classList.remove('open');q.style.display='none';q.setAttribute('aria-hidden','true')}
function createSimpleLine(p1,p2){
 const dir=p2.x>=p1.x?1:-1,g=el('g',{'data-type':'line','data-id':uid++,'data-p1':`${p1.x},${p1.y}`,'data-p2':`${p2.x},${p2.y}`,'data-dir':String(dir),'data-shelf':'40','data-line-width':simpleLineDefaults.lineWidth,'data-line-color':simpleLineDefaults.lineColor,'data-line-style':simpleLineDefaults.lineStyle});
 appendContent(g);renderSimpleLine(g);selected=g;lastEditable=g;drawSelection();openSimpleLinePopup(g);setStatus('Линия создана. Три точки позволяют менять её геометрию')
}

// Add line handles to the established selection renderer without changing the proven leader path.
const kbDrawSelectionBeforeLineV22=drawSelection;
drawSelection=function(){kbDrawSelectionBeforeLineV22();if(selected?.dataset.type==='line'){clearUI();drawSimpleLineHandles(selected)}};

paper.addEventListener('pointerdown',e=>{
 const p=pt(e),obj=groupType(e.target),h=e.target.closest?.('.simple-line-handle');
 if(h){
   const g=paper.querySelector(`[data-type="line"][data-id="${h.dataset.owner}"]`);if(!g)return;
   selected=g;lastEditable=g;simpleLineDrag={obj:g,kind:h.dataset.lineHandle,start:p,p1:parsePt(g.dataset.p1),p2:parsePt(g.dataset.p2),shelf:+g.dataset.shelf||40};
   e.preventDefault();e.stopImmediatePropagation();return;
 }
 if(tool==='line'){
   e.preventDefault();e.stopImmediatePropagation();
   simpleLineDraft={p1:p,p2:p};simpleLinePreview=el('path',{d:`M ${p.x} ${p.y} L ${p.x} ${p.y} L ${p.x+40} ${p.y}`,fill:'none',stroke:'#2563eb','stroke-width':'.5','stroke-dasharray':'2 1','pointer-events':'none'});paper.appendChild(simpleLinePreview);return;
 }
 if(obj?.dataset.type==='line'){
   selected=obj;lastEditable=obj;drawSelection();simpleLineDrag={obj,start:p,kind:'move',p1:parsePt(obj.dataset.p1),p2:parsePt(obj.dataset.p2)};
   e.preventDefault();e.stopImmediatePropagation();
 }
},true);
paper.addEventListener('pointermove',e=>{
 const p=pt(e);
 if(simpleLineDraft&&tool==='line'){
   simpleLineDraft.p2=p;const dir=p.x>=simpleLineDraft.p1.x?1:-1,p3x=p.x+dir*40;
   simpleLinePreview?.setAttribute('d',`M ${simpleLineDraft.p1.x} ${simpleLineDraft.p1.y} L ${p.x} ${p.y} L ${p3x} ${p.y}`);
   e.preventDefault();e.stopImmediatePropagation();return;
 }
 if(!simpleLineDrag)return;
 const d=simpleLineDrag,g=d.obj;
 if(d.kind==='move'){const dx=p.x-d.start.x,dy=p.y-d.start.y;g.dataset.p1=`${d.p1.x+dx},${d.p1.y+dy}`;g.dataset.p2=`${d.p2.x+dx},${d.p2.y+dy}`}
 else if(d.kind==='p1')g.dataset.p1=`${p.x},${p.y}`;
 else if(d.kind==='p2')g.dataset.p2=`${p.x},${p.y}`;
 else if(d.kind==='p3'){const p2=parsePt(g.dataset.p2);g.dataset.shelf=String(Math.max(0,Math.abs(p.x-p2.x)));g.dataset.dir=p.x>=p2.x?'1':'-1'}
 renderSimpleLine(g);drawSelection();e.preventDefault();e.stopImmediatePropagation();
},true);
window.addEventListener('pointerup',e=>{
 if(simpleLineDraft&&tool==='line'){
   const p2=pt(e),p1=simpleLineDraft.p1;simpleLineDraft=null;simpleLinePreview?.remove();simpleLinePreview=null;
   if(Math.hypot(p2.x-p1.x,p2.y-p1.y)>2)createSimpleLine(p1,p2)
 }
 simpleLineDrag=null;
},true);
paper.addEventListener('dblclick',e=>{const obj=groupType(e.target);if(obj?.dataset.type==='line'){e.preventDefault();e.stopImmediatePropagation();openSimpleLinePopup(obj)}},true);

$('simpleLineWidth').oninput=()=>{if(selected?.dataset.type!=='line')return;selected.dataset.lineWidth=$('simpleLineWidth').value;simpleLineDefaults.lineWidth=$('simpleLineWidth').value;renderSimpleLine(selected);drawSelection()};
$('simpleLineStyle').onchange=()=>{if(selected?.dataset.type!=='line')return;selected.dataset.lineStyle=$('simpleLineStyle').value;simpleLineDefaults.lineStyle=$('simpleLineStyle').value;renderSimpleLine(selected);drawSelection()};
$('simpleLineColor').oninput=()=>{if(selected?.dataset.type!=='line')return;selected.dataset.lineColor=$('simpleLineColor').value;simpleLineDefaults.lineColor=$('simpleLineColor').value;renderSimpleLine(selected);drawSelection()};
$('linePopupClose').onclick=closeSimpleLinePopup;
$('lineOk').onclick=()=>{closeSimpleLinePopup();clearSelection();setTool(null,true);setStatus('Линия зафиксирована')};

window.addEventListener('pointerdown',e=>{
 const header=e.target.closest?.('#linePopupHeader');if(!header||e.target.id==='linePopupClose')return;
 const q=$('linePopup'),r=q.getBoundingClientRect();simpleLinePopupDrag={id:e.pointerId,dx:e.clientX-r.left,dy:e.clientY-r.top};
 try{header.setPointerCapture(e.pointerId)}catch{}e.preventDefault();e.stopImmediatePropagation();
},true);
window.addEventListener('pointermove',e=>{
 const d=simpleLinePopupDrag;if(!d||d.id!==e.pointerId)return;const q=$('linePopup');
 q.style.left=Math.max(0,Math.min(innerWidth-q.offsetWidth,e.clientX-d.dx))+'px';q.style.top=Math.max(0,Math.min(innerHeight-q.offsetHeight,e.clientY-d.dy))+'px';
 e.preventDefault();e.stopImmediatePropagation();
},true);
window.addEventListener('pointerup',e=>{if(simpleLinePopupDrag&&simpleLinePopupDrag.id===e.pointerId)simpleLinePopupDrag=null},true);
window.addEventListener('pointercancel',e=>{if(simpleLinePopupDrag&&simpleLinePopupDrag.id===e.pointerId)simpleLinePopupDrag=null},true);

document.addEventListener('keydown',e=>{
 if(e.key!=='Escape')return;
 if(simpleLineDraft){simpleLineDraft=null;simpleLinePreview?.remove();simpleLinePreview=null}
 simpleLineDrag=null;closeSimpleLinePopup();
},true);

'''
s=s[:pos]+code+s[pos:]

# --- Export support: line group renders with the same generic SVG path renderer. ---
s=s.replace("g[data-type=\"dimension\"]')||n.matches?.('g[data-type=\"leader\"]')",
            "g[data-type=\"dimension\"]')||n.matches?.('g[data-type=\"leader\"]')||n.matches?.('g[data-type=\"line\"]')")
s=s.replace("g[data-type=\"dimension\"]'))drawDimensionObject(ctx,n);else if(n.matches?.('g[data-type=\"text\"]'))",
            "g[data-type=\"dimension\"]')||n.matches?.('g[data-type=\"line\"]'))drawDimensionObject(ctx,n);else if(n.matches?.('g[data-type=\"text\"]'))")

# Canvas fallback must honor SVG dash patterns used by the new line tool.
old="function drawSvgPath(ctx,n){ctx.save();const path=new Path2D(n.getAttribute('d')||'');const fill=n.getAttribute('fill'),stroke=n.getAttribute('stroke');"
new="function drawSvgPath(ctx,n){ctx.save();const path=new Path2D(n.getAttribute('d')||'');const fill=n.getAttribute('fill'),stroke=n.getAttribute('stroke'),dash=n.getAttribute('stroke-dasharray');if(dash&&dash!=='none')ctx.setLineDash(dash.trim().split(/[ ,]+/).map(Number).filter(Number.isFinite));"
if old in s:s=s.replace(old,new,1)

# A few generic object lists are safe to extend so line objects behave like other movable SVG annotations.
s=s.replace("['image','dimension','text','leader']","['image','dimension','text','leader','line']")

for token in [marker,'data-tool="line"','id="linePopup"','function renderSimpleLine(','function drawSimpleLineHandles(','id="redoImage"','function simpleLineDash(']:
    if token not in s: raise SystemExit('v22 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v22: line tool, line settings, compact toolbar label and image redo applied')
