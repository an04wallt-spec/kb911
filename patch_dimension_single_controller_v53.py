from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V53_SINGLE_DIMENSION_CONTROLLER'
if marker in s:
    print('v53 already applied')
    raise SystemExit(0)

# v51 installed a window-capture controller. Disable its runtime handlers
# explicitly instead of stacking another active controller on top of it.
# The guard is evaluated when events fire, after v53 has initialized.
v51=s.find('// KB911_V51_DIMENSION_HANDLE_OWNER')
if v51<0:
    raise SystemExit('v53: v51 marker missing')
startup='\nsetPage();\ninitKB911Project();\nkbHistoryStart();'
end=s.find(startup,v51)
if end<0:
    raise SystemExit('v53: startup anchor after v51 missing')
block=s[v51:end]
for sig in [
    "window.addEventListener('pointerdown',e=>{",
    "window.addEventListener('pointermove',e=>{",
    "window.addEventListener('pointerup',e=>{",
    "window.addEventListener('pointercancel',e=>{"
]:
    if sig not in block:
        raise SystemExit('v53: expected v51 handler missing: '+sig)
    block=block.replace(sig,sig+"\n if(window.kbDimV53Installed)return;",1)
s=s[:v51]+block+s[end:]

code=r'''

// KB911_V53_SINGLE_DIMENSION_CONTROLLER
// Exactly one controller owns the three anchored-dimension handle gestures.
// It accepts only the primary (left) mouse button. Right/middle buttons can
// never start or continue a dimension edit, and stale drag state is cleared.
window.kbDimV53Installed=true;
let kbDimDragV53=null;
let kbDimTapV53=null;

function kbDimClearLegacyV53(){
 kbDimDirectDragV51=null;
 kbDimLineDragV40=null;
 kbDimAnchorDragV40=null;
 kbDimAxisDragV48=null;
 kbClearSnapMarkV40();
}
function kbDimHandleV53(target){
 return target?.closest?.('.kb-dim-line-handle-v40,.kb-dim-anchor-v40,.kb-dim-axis-end-v48')||null;
}
function kbDimKindV53(h){
 if(h.classList.contains('kb-dim-line-handle-v40'))return 'center';
 if(h.classList.contains('kb-dim-axis-end-v48'))return 'axis-'+(h.dataset.axisEndV48||'');
 if(h.classList.contains('kb-dim-anchor-v40'))return 'anchor-'+(h.dataset.anchorV40||'');
 return '';
}
function kbDimFinishV53(e,cancel=false){
 const d=kbDimDragV53;
 kbDimDragV53=null;
 kbDimClearLegacyV53();
 try{if(paper.hasPointerCapture?.(e.pointerId))paper.releasePointerCapture(e.pointerId)}catch{}
 if(!d)return;
 if(!cancel){
  renderDim(d.obj);selected=d.obj;lastEditable=d.obj;drawSelection();
  try{kbHistorySchedule(0)}catch{}
  if(d.mode==='center')setStatus('Размерная линия перенесена');
  else if(d.mode==='axis')setStatus('Длина размера изменена');
  else setStatus('Опорная точка размера перемещена');
 }
}

window.addEventListener('pointerdown',e=>{
 const h=kbDimHandleV53(e.target);
 // Any non-left press cancels stale dimension drag state. It never edits.
 if(e.button!==0){
  kbDimDragV53=null;kbDimClearLegacyV53();
  return;
 }
 if(!h)return;
 const g=findOwner(h.dataset.owner,'dimension');
 if(!kbIsAnchoredDimV40(g))return;

 kbDimClearLegacyV53();
 const kind=kbDimKindV53(h),now=performance.now(),prev=kbDimTapV53;
 const second=prev&&prev.owner===g.dataset.id&&prev.kind===kind&&
  now-prev.time<=480&&Math.hypot(e.clientX-prev.x,e.clientY-prev.y)<=10;
 if(second){
  kbDimTapV53=null;e.preventDefault();e.stopImmediatePropagation();
  kbOpenDimensionEditorV47(g);return;
 }
 kbDimTapV53={owner:g.dataset.id,kind,time:now,x:e.clientX,y:e.clientY,pointerId:e.pointerId};

 const p0=pt(e),m=kbAnchoredDimGeomV40(g);
 if(h.classList.contains('kb-dim-line-handle-v40')){
  // Center handle: ONLY perpendicular translation of the dimension line.
  kbDimDragV53={mode:'center',obj:g,pointerId:e.pointerId,start:p0,
   startOffset:m.offset,nx:m.nx,ny:m.ny};
 }else if(h.classList.contains('kb-dim-axis-end-v48')){
  // Arrow/slash end: ONLY one endpoint changes along the original axis.
  const key=h.dataset.axisEndV48==='start'?'p1':'p2';
  kbDimDragV53={mode:'axis',obj:g,pointerId:e.pointerId,key,start:p0,
   base:key==='p1'?{...m.a1}:{...m.a2},ux:m.ux,uy:m.uy,length:m.L};
 }else{
  // Blue endpoint circle: free reference-point movement, including angle change.
  const key=h.dataset.anchorV40==='start'?'p1':'p2';
  kbDimDragV53={mode:'anchor',obj:g,pointerId:e.pointerId,key,
   other:key==='p1'?'p2':'p1'};
 }
 selected=g;lastEditable=g;showProps();
 try{paper.setPointerCapture?.(e.pointerId)}catch{}
 e.preventDefault();e.stopImmediatePropagation();
},true);

window.addEventListener('pointermove',e=>{
 const d=kbDimDragV53;
 if(!d||d.pointerId!==e.pointerId)return;
 // A drag exists only while the LEFT button is physically down.
 if((e.buttons&1)===0){kbDimFinishV53(e,true);return}
 if(kbDimTapV53&&Math.hypot(e.clientX-kbDimTapV53.x,e.clientY-kbDimTapV53.y)>6)kbDimTapV53=null;
 const p=pt(e);
 if(d.mode==='center'){
  const delta=(p.x-d.start.x)*d.nx+(p.y-d.start.y)*d.ny;
  d.obj.dataset.dimOffset=String(d.startOffset+delta);
 }else if(d.mode==='axis'){
  let delta=(p.x-d.start.x)*d.ux+(p.y-d.start.y)*d.uy;
  const minLen=.5;
  if(d.key==='p1')delta=Math.min(delta,d.length-minLen);
  else delta=Math.max(delta,-(d.length-minLen));
  const q={x:d.base.x+d.ux*delta,y:d.base.y+d.uy*delta};
  // Only this endpoint changes. dimOffset and the opposite endpoint stay fixed.
  d.obj.dataset[d.key]=`${q.x},${q.y}`;
 }else{
  const other=parsePt(d.obj.dataset[d.other]);
  const q=kbSnapDimPointV40(p,other,d.obj);
  d.obj.dataset[d.key]=`${q.x},${q.y}`;
 }
 renderDim(d.obj);selected=d.obj;lastEditable=d.obj;drawSelection();
 e.preventDefault();e.stopImmediatePropagation();
},true);

window.addEventListener('pointerup',e=>{
 const d=kbDimDragV53;
 if(!d||d.pointerId!==e.pointerId)return;
 // Only a left-button release can commit a left-button drag.
 if(e.button!==0){kbDimFinishV53(e,true);return}
 kbDimFinishV53(e,false);
 e.preventDefault();e.stopImmediatePropagation();
},true);
window.addEventListener('pointercancel',e=>{
 if(kbDimDragV53?.pointerId===e.pointerId)kbDimFinishV53(e,true);
 if(kbDimTapV53?.pointerId===e.pointerId)kbDimTapV53=null;
},true);

// Context/right click on dimension selection handles is inert for geometry.
window.addEventListener('contextmenu',e=>{
 if(!kbDimHandleV53(e.target))return;
 kbDimDragV53=null;kbDimClearLegacyV53();
},true);
'''

if s.count(startup)!=1:
    raise SystemExit('v53: startup anchor count changed')
s=s.replace(startup,code+startup,1)

for token in [
 marker,'window.kbDimV53Installed=true','(e.buttons&1)===0',
 "mode:'center'","mode:'axis'","mode:'anchor'",
 "d.obj.dataset.dimOffset=String(d.startOffset+delta)",
 'Only this endpoint changes','e.button!==0',
 'kbDimClearLegacyV53','kbDimFinishV53'
]:
    if token not in s:
        raise SystemExit('v53 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v53: one left-button-only controller owns center move, axis length and free anchors; right button cannot edit dimensions')
