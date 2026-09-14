from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V51_DIMENSION_HANDLE_OWNER'
if marker in s:
    print('v51 already applied')
    raise SystemExit(0)

anchor='\nsetPage();\ninitKB911Project();\nkbHistoryStart();'
if s.count(anchor)!=1:
    raise SystemExit('v51: startup anchor missing')

code=r'''

// KB911_V51_DIMENSION_HANDLE_OWNER
// One early capture owner for all anchored-dimension editing handles.  It runs
// on window capture before legacy paper listeners, eliminating handler-order
// conflicts without changing dimension rendering or unrelated tools.
let kbDimDirectDragV51=null;
let kbDimHandleTapV51=null;

function kbDimHandleKindV51(h){
 if(h.classList.contains('kb-dim-line-handle-v40'))return 'center';
 if(h.classList.contains('kb-dim-anchor-v40'))return 'anchor-'+(h.dataset.anchorV40||'');
 if(h.classList.contains('kb-dim-axis-end-v48'))return 'axis-'+(h.dataset.axisEndV48||'');
 return '';
}
function kbDimOpenFromHandleV51(g){
 kbDimDirectDragV51=null;
 kbDimAnchorDragV40=null;kbDimLineDragV40=null;kbDimAxisDragV48=null;
 kbClearSnapMarkV40();
 kbOpenDimensionEditorV47(g);
}

window.addEventListener('pointerdown',e=>{
 if(e.button!==0)return;
 const h=e.target.closest?.('.kb-dim-line-handle-v40,.kb-dim-anchor-v40,.kb-dim-axis-end-v48');
 if(!h)return;
 const g=findOwner(h.dataset.owner,'dimension');
 if(!kbIsAnchoredDimV40(g))return;
 const kind=kbDimHandleKindV51(h),now=performance.now(),prev=kbDimHandleTapV51;
 const second=prev&&prev.owner===g.dataset.id&&prev.kind===kind&&now-prev.time<=480&&Math.hypot(e.clientX-prev.x,e.clientY-prev.y)<=10;
 if(second){
  kbDimHandleTapV51=null;
  e.preventDefault();e.stopImmediatePropagation();
  kbDimOpenFromHandleV51(g);return;
 }
 kbDimHandleTapV51={owner:g.dataset.id,kind,time:now,x:e.clientX,y:e.clientY,pointerId:e.pointerId};
 const p=pt(e),m=kbAnchoredDimGeomV40(g);
 if(h.classList.contains('kb-dim-line-handle-v40')){
  kbDimDirectDragV51={mode:'center',obj:g,start:p,startOffset:m.offset,nx:m.nx,ny:m.ny,pointerId:e.pointerId};
 }else if(h.classList.contains('kb-dim-axis-end-v48')){
  const key=h.dataset.axisEndV48==='start'?'p1':'p2';
  kbDimDirectDragV51={mode:'axis',obj:g,key,start:p,base:key==='p1'?{...m.a1}:{...m.a2},ux:m.ux,uy:m.uy,length:m.L,pointerId:e.pointerId};
 }else{
  const key=h.dataset.anchorV40==='start'?'p1':'p2',other=key==='p1'?'p2':'p1';
  kbDimDirectDragV51={mode:'anchor',obj:g,key,other,pointerId:e.pointerId};
 }
 selected=g;lastEditable=g;showProps();drawSelection();
 try{paper.setPointerCapture?.(e.pointerId)}catch{}
 e.preventDefault();e.stopImmediatePropagation();
},true);

window.addEventListener('pointermove',e=>{
 const d=kbDimDirectDragV51;
 if(!d||d.pointerId!==e.pointerId)return;
 const p=pt(e);
 if(kbDimHandleTapV51&&Math.hypot(e.clientX-kbDimHandleTapV51.x,e.clientY-kbDimHandleTapV51.y)>6)kbDimHandleTapV51=null;
 if(d.mode==='center'){
  const delta=(p.x-d.start.x)*d.nx+(p.y-d.start.y)*d.ny;
  d.obj.dataset.dimOffset=String(d.startOffset+delta);
 }else if(d.mode==='axis'){
  let delta=(p.x-d.start.x)*d.ux+(p.y-d.start.y)*d.uy;
  const minLen=.5;
  if(d.key==='p1')delta=Math.min(delta,d.length-minLen);
  else delta=Math.max(delta,-(d.length-minLen));
  const q={x:d.base.x+d.ux*delta,y:d.base.y+d.uy*delta};
  d.obj.dataset[d.key]=`${q.x},${q.y}`;
 }else if(d.mode==='anchor'){
  const other=parsePt(d.obj.dataset[d.other]),q=kbSnapDimPointV40(p,other,d.obj);
  d.obj.dataset[d.key]=`${q.x},${q.y}`;
 }
 renderDim(d.obj);selected=d.obj;lastEditable=d.obj;drawSelection();
 e.preventDefault();e.stopImmediatePropagation();
},true);

window.addEventListener('pointerup',e=>{
 const d=kbDimDirectDragV51;
 if(!d||d.pointerId!==e.pointerId)return;
 kbDimDirectDragV51=null;kbClearSnapMarkV40();
 renderDim(d.obj);selected=d.obj;lastEditable=d.obj;drawSelection();
 try{kbHistorySchedule(0)}catch{}
 if(d.mode==='center')setStatus('Положение размерной линии изменено');
 else if(d.mode==='axis')setStatus('Длина размера изменена вдоль его оси');
 else setStatus('Опорная точка размера перемещена');
 e.preventDefault();e.stopImmediatePropagation();
},true);
window.addEventListener('pointercancel',e=>{
 if(kbDimDirectDragV51?.pointerId===e.pointerId)kbDimDirectDragV51=null;
 if(kbDimHandleTapV51?.pointerId===e.pointerId)kbDimHandleTapV51=null;
},true);
'''

s=s.replace(anchor,code+anchor,1)
for token in [marker,'kbDimDirectDragV51',"mode:'center'","mode:'axis'","mode:'anchor'",'kbDimOpenFromHandleV51','window.addEventListener(\'pointerdown\'',"d.obj.dataset.dimOffset=String(d.startOffset+delta)","d.obj.dataset[d.key]=`${q.x},${q.y}`"]:
    if token not in s:
        raise SystemExit('v51 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v51: one early owner now controls center/axis/anchor dimension handles and their double-click')
