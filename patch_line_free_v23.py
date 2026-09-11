from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='// KB911_V23_FREE_THREE_POINT_LINE'
if marker in s:
    print('v23 already applied')
    raise SystemExit(0)

# --- Remove the direct physical-print feature added in v20. ---
print_button='    <button id="printSheet" style="width:100%;margin-top:6px">Печать</button>\n'
if print_button not in s:
    raise SystemExit('v23: print button not found')
s=s.replace(print_button,'',1)

p0=s.find('// KB911_V20_PRINT_RESTORE')
p1=s.find('// KB911_V21_IMAGE_MENU_COMPAT',p0)
if p0<0 or p1<0 or p1<=p0:
    raise SystemExit('v23: v20 print runtime range not found')
s=s[:p0]+s[p1:]

# --- Free three-point polyline geometry. Backward-compatible with v22 lines. ---
old="""function simpleLinePts(g){
 const p1=parsePt(g.dataset.p1||'0,0'),p2=parsePt(g.dataset.p2||'0,0'),dir=(+g.dataset.dir||1),shelf=Math.max(0,+g.dataset.shelf||40);
 return {p1,p2,p3:{x:p2.x+dir*shelf,y:p2.y},dir,shelf};
}"""
new="""function simpleLinePts(g){
 const p1=parsePt(g.dataset.p1||'0,0'),p2=parsePt(g.dataset.p2||'0,0');
 let p3;
 if(g.dataset.p3){p3=parsePt(g.dataset.p3)}
 else{const dir=(+g.dataset.dir||1),shelf=Math.max(0,+g.dataset.shelf||40);p3={x:p2.x+dir*shelf,y:p2.y}}
 return {p1,p2,p3};
}"""
if old not in s: raise SystemExit('v23: simpleLinePts v22 block not found')
s=s.replace(old,new,1)

old="""function createSimpleLine(p1,p2){
 const dir=p2.x>=p1.x?1:-1,g=el('g',{'data-type':'line','data-id':uid++,'data-p1':`${p1.x},${p1.y}`,'data-p2':`${p2.x},${p2.y}`,'data-dir':String(dir),'data-shelf':'40','data-line-width':simpleLineDefaults.lineWidth,'data-line-color':simpleLineDefaults.lineColor,'data-line-style':simpleLineDefaults.lineStyle});
 appendContent(g);renderSimpleLine(g);selected=g;lastEditable=g;drawSelection();openSimpleLinePopup(g);setStatus('Линия создана. Три точки позволяют менять её геометрию')
}"""
new="""function createSimpleLine(p1,p2,p3){
 const g=el('g',{'data-type':'line','data-id':uid++,'data-p1':`${p1.x},${p1.y}`,'data-p2':`${p2.x},${p2.y}`,'data-p3':`${p3.x},${p3.y}`,'data-line-width':simpleLineDefaults.lineWidth,'data-line-color':simpleLineDefaults.lineColor,'data-line-style':simpleLineDefaults.lineStyle});
 appendContent(g);renderSimpleLine(g);selected=g;lastEditable=g;drawSelection();openSimpleLinePopup(g);setStatus('Линия создана. Все три точки можно перемещать независимо')
}"""
if old not in s: raise SystemExit('v23: createSimpleLine v22 block not found')
s=s.replace(old,new,1)

# Replace only the v22 line pointer pipeline; leave leader/dimension/text/image handlers untouched.
anchor="const kbDrawSelectionBeforeLineV22=drawSelection;\ndrawSelection=function(){kbDrawSelectionBeforeLineV22();if(selected?.dataset.type==='line'){clearUI();drawSimpleLineHandles(selected)}};\n\n"
a=s.find(anchor)
if a<0: raise SystemExit('v23: line selection anchor not found')
a+=len(anchor)
end_line="paper.addEventListener('dblclick',e=>{const obj=groupType(e.target);if(obj?.dataset.type==='line'){e.preventDefault();e.stopImmediatePropagation();openSimpleLinePopup(obj)}},true);"
b=s.find(end_line,a)
if b<0: raise SystemExit('v23: line dblclick end not found')
b+=len(end_line)

pipeline=r'''paper.addEventListener('pointerdown',e=>{
 const p=pt(e),obj=groupType(e.target),h=e.target.closest?.('.simple-line-handle');
 if(h){
   const g=paper.querySelector(`[data-type="line"][data-id="${h.dataset.owner}"]`);if(!g)return;
   const pts=simpleLinePts(g);if(!g.dataset.p3)g.dataset.p3=`${pts.p3.x},${pts.p3.y}`;
   selected=g;lastEditable=g;simpleLineDrag={obj:g,kind:h.dataset.lineHandle,start:p,p1:pts.p1,p2:pts.p2,p3:pts.p3};
   e.preventDefault();e.stopImmediatePropagation();return;
 }
 if(tool==='line'){
   e.preventDefault();e.stopImmediatePropagation();
   if(!simpleLineDraft){
     simpleLineDraft={stage:1,p1:p,p2:null};
     simpleLinePreview=el('path',{d:`M ${p.x} ${p.y} L ${p.x} ${p.y}`,fill:'none',stroke:'#2563eb','stroke-width':'.5','stroke-dasharray':'2 1','pointer-events':'none'});
     paper.appendChild(simpleLinePreview);setStatus('Линия: укажите точку излома');return;
   }
   if(simpleLineDraft.stage===1){
     if(Math.hypot(p.x-simpleLineDraft.p1.x,p.y-simpleLineDraft.p1.y)<1)return;
     simpleLineDraft.p2=p;simpleLineDraft.stage=2;
     simpleLinePreview?.setAttribute('d',`M ${simpleLineDraft.p1.x} ${simpleLineDraft.p1.y} L ${p.x} ${p.y} L ${p.x} ${p.y}`);
     setStatus('Линия: укажите конечную точку');return;
   }
   if(simpleLineDraft.stage===2){
     const p1=simpleLineDraft.p1,p2=simpleLineDraft.p2,p3=p;
     if(Math.hypot(p3.x-p2.x,p3.y-p2.y)<1)return;
     simpleLineDraft=null;simpleLinePreview?.remove();simpleLinePreview=null;
     createSimpleLine(p1,p2,p3);return;
   }
 }
 if(obj?.dataset.type==='line'){
   const pts=simpleLinePts(obj);if(!obj.dataset.p3)obj.dataset.p3=`${pts.p3.x},${pts.p3.y}`;
   selected=obj;lastEditable=obj;drawSelection();simpleLineDrag={obj,start:p,kind:'move',p1:pts.p1,p2:pts.p2,p3:pts.p3};
   e.preventDefault();e.stopImmediatePropagation();
 }
},true);
paper.addEventListener('pointermove',e=>{
 const p=pt(e);
 if(simpleLineDraft&&tool==='line'){
   const d=simpleLineDraft;
   if(d.stage===1)simpleLinePreview?.setAttribute('d',`M ${d.p1.x} ${d.p1.y} L ${p.x} ${p.y}`);
   else if(d.stage===2)simpleLinePreview?.setAttribute('d',`M ${d.p1.x} ${d.p1.y} L ${d.p2.x} ${d.p2.y} L ${p.x} ${p.y}`);
   e.preventDefault();e.stopImmediatePropagation();return;
 }
 if(!simpleLineDrag)return;
 const d=simpleLineDrag,g=d.obj;
 if(d.kind==='move'){
   const dx=p.x-d.start.x,dy=p.y-d.start.y;
   g.dataset.p1=`${d.p1.x+dx},${d.p1.y+dy}`;g.dataset.p2=`${d.p2.x+dx},${d.p2.y+dy}`;g.dataset.p3=`${d.p3.x+dx},${d.p3.y+dy}`;
 }else if(d.kind==='p1')g.dataset.p1=`${p.x},${p.y}`;
 else if(d.kind==='p2')g.dataset.p2=`${p.x},${p.y}`;
 else if(d.kind==='p3')g.dataset.p3=`${p.x},${p.y}`;
 renderSimpleLine(g);drawSelection();e.preventDefault();e.stopImmediatePropagation();
},true);
window.addEventListener('pointerup',()=>{simpleLineDrag=null},true);
paper.addEventListener('dblclick',e=>{const obj=groupType(e.target);if(obj?.dataset.type==='line'){e.preventDefault();e.stopImmediatePropagation();openSimpleLinePopup(obj)}},true);'''
s=s[:a]+pipeline+s[b:]

# Update tool hint: construction is now three independent clicks.
s=s.replace("setStatus('Линия: поставьте первую точку и протяните к точке излома')","setStatus('Линия: щёлкните начало → точку излома → конец')")

# Put an explicit marker into the live runtime for final-EXE verification.
native='// ---------- Native KB911 project format ----------'
pos=s.find(native)
if pos<0: raise SystemExit('v23: native anchor not found')
s=s[:pos]+marker+'\n'+s[pos:]

# Guards: no direct print UI/runtime, free p3 exists, old shelf-constrained drag is gone.
checks=[
 marker,
 "data-p3':`${p3.x},${p3.y}`",
 "simpleLineDraft={stage:1,p1:p,p2:null}",
 "g.dataset.p3=`${p.x},${p.y}`",
 "Линия: укажите конечную точку"
]
for token in checks:
    if token not in s: raise SystemExit('v23 guard failed: '+token)
for forbidden in ['id="printSheet"','function kbPrintCurrentSheetV20()','window.print()']:
    if forbidden in s: raise SystemExit('v23 print removal failed: '+forbidden)

p.write_text(s,encoding='utf-8',newline='')
print('v23: free three-point line drawing applied; direct physical print removed')
