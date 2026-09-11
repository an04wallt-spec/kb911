from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='// KB911_V10_CORE_INTERACTIONS'
if marker in s:
    print('core interactions already restored')
    raise SystemExit(0)

# A recent feature patch accidentally removed the original paper pointerdown handler.
# That single regression disabled dimension creation, image dragging/resizing and
# ordinary object dragging while leaving pointermove/pointerup code in place.
# Restore the proven interaction entry point, adapted to the current asymmetric
# dimension tails and current no-popup-on-simple-selection behavior.
anchor="paper.addEventListener('contextmenu',e=>"
if anchor not in s:
    raise SystemExit('contextmenu anchor not found')

core=r'''
// KB911_V10_CORE_INTERACTIONS
paper.addEventListener('pointerdown',e=>{
 const p=pt(e),obj=groupType(e.target);
 if(obj&&['dimension','text','leader'].includes(obj.dataset?.type))lastEditable=obj;
 if(pasteDraft){e.preventDefault();updatePasteGhost(p);placePaste();return}
 if(tool==='dimension'){
   dimDraft={p1:p,p2:p};
   dimPreview=el('line',{x1:p.x,y1:p.y,x2:p.x,y2:p.y,stroke:'#2563eb','stroke-width':'.5','stroke-dasharray':'2 1','vector-effect':'non-scaling-stroke'});
   paper.appendChild(dimPreview);paper.setPointerCapture?.(e.pointerId);return;
 }
 if(tool==='text'){
   textDraft={p1:p,p2:p};
   textPreview=el('rect',{x:p.x,y:p.y,width:0,height:0,rx:3,ry:3,class:'text-draft'});
   paper.appendChild(textPreview);paper.setPointerCapture?.(e.pointerId);return;
 }
 if(e.target.classList?.contains('image-handle')){
   const g=selected?.dataset.type==='image'?selected:findOwner(e.target.dataset.owner,'image');
   if(g&&activeImage===g){const r=imageRect(g);imageResize={obj:g,corner:e.target.dataset.corner,start:p,...r};e.preventDefault();return}
 }
 if(e.target.classList?.contains('rotate-handle')&&selected?.dataset.type==='text'){
   const g=selected,x=+g.dataset.x,y=+g.dataset.y,w=+g.dataset.w,h=+g.dataset.h;
   rotateDrag={obj:g,cx:x+w/2,cy:y+h/2,startAngle:+g.dataset.angle||0,startPointer:Math.atan2(p.y-(y+h/2),p.x-(x+w/2))*180/Math.PI};e.preventDefault();return;
 }
 if(e.target.classList?.contains('resize-handle')&&selected?.dataset.type==='text'){
   textResize={obj:selected,start:p,w:+selected.dataset.w,h:+selected.dataset.h};e.preventDefault();return;
 }
 if(e.target.classList?.contains('dim-handle-start')||e.target.classList?.contains('dim-handle-end')){
   const id=e.target.dataset.owner,g=selected?.dataset.type==='dimension'?selected:findOwner(id,'dimension');
   if(g){if(selected!==g){selected=g;showProps();drawSelection()}const end=e.target.classList.contains('dim-handle-start')?'p1':'p2',center=parsePt(g.dataset[end]);endpointDrag={obj:g,end,offX:center.x-p.x,offY:center.y-p.y};e.preventDefault();return}
 }
 if(e.target.classList?.contains('dim-tail-handle')){
   const id=e.target.dataset.owner,g=selected?.dataset.type==='dimension'?selected:findOwner(id,'dimension');
   if(g){if(selected!==g){selected=g;showProps();drawSelection()}const end=e.target.classList.contains('dim-tail-end')?'p2':'p1';tailDrag={obj:g,end};e.preventDefault();return}
 }
 if(obj?.dataset.type==='dimension'&&obj!==selected){selected=obj;showProps();drawSelection()}
 if(obj?.dataset.type==='text'&&obj!==selected){selected=obj;showProps();drawSelection()}
 if(!obj)return;
 if(e.target.classList?.contains('dim-label')&&obj.dataset.type==='dimension')return;
 drag={obj,start:p};
 if(obj.dataset.type==='dimension'){drag.p1=parsePt(obj.dataset.p1);drag.p2=parsePt(obj.dataset.p2)}
 else if(obj.dataset.type==='text'){drag.x=+obj.dataset.x;drag.y=+obj.dataset.y}
 else if(obj.dataset.type==='image'){
   if(activeImage!==obj){drag=null;return}
   rememberImageGeometry(obj);drag.x=+obj.getAttribute('x');drag.y=+obj.getAttribute('y');
 }
});
'''
s=s.replace(anchor,core+'\n'+anchor,1)

# Build guards. These exact pieces are the minimum interaction backbone that was
# present in the last known-good KB911.html.
checks=[
    'KB911_V10_CORE_INTERACTIONS',
    "if(tool==='dimension')",
    "if(e.target.classList?.contains('image-handle'))",
    "if(activeImage!==obj){drag=null;return}",
    "drag={obj,start:p}",
    "window.addEventListener('pointerup'",
    "paper.addEventListener('pointermove'",
    "paper.addEventListener('dblclick'"
]
for token in checks:
    if token not in s: raise SystemExit('core interaction guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('Core interactions v10 restored from last known-good KB911 behavior')
