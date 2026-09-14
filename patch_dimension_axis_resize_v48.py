from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V48_DIMENSION_AXIS_END_RESIZE'
if marker in s:
    print('v48 already applied')
    raise SystemExit(0)

# Insert endpoint-axis resize priority into the existing v42 capture handler,
# immediately before the sticky Dimension creation branch. This prevents a
# drag on an existing dimension end from accidentally creating a new dimension.
v42=s.find('// KB911_V42_MAGNET_AND_ACTIVE_CENTER_HANDLE')
if v42<0:
    raise SystemExit('v48: v42 marker missing')
toolpos=s.find(" if(tool==='dimension'){",v42)
if toolpos<0:
    raise SystemExit('v48: dimension tool branch missing')
priority=r''' const axisEndV48=e.target.closest?.('.kb-dim-axis-end-v48');
 if(axisEndV48){
  const ownerV48=findOwner(axisEndV48.dataset.owner,'dimension');
  if(kbIsAnchoredDimV40(ownerV48)){
   const mV48=kbAnchoredDimGeomV40(ownerV48),keyV48=axisEndV48.dataset.axisEndV48==='start'?'p1':'p2';
   kbDimAxisDragV48={obj:ownerV48,key:keyV48,start:p,base:keyV48==='p1'?{...mV48.a1}:{...mV48.a2},ux:mV48.ux,uy:mV48.uy,length:mV48.L};
   selected=ownerV48;lastEditable=ownerV48;drawSelection();
   paper.setPointerCapture?.(e.pointerId);
   e.preventDefault();e.stopImmediatePropagation();return;
  }
 }
'''
s=s[:toolpos]+priority+s[toolpos:]

# While axis-resizing, suppress only the magnetic hover marker. Existing
# snapping/dragging behavior for every other interaction remains unchanged.
old="if(tool!=='dimension'||kbDimDraftV40||kbDimLineDragV40||kbDimAnchorDragV40)return;"
new="if(tool!=='dimension'||kbDimDraftV40||kbDimLineDragV40||kbDimAnchorDragV40||kbDimAxisDragV48)return;"
if s.count(old)!=1:
    raise SystemExit(f'v48: expected one v42 hover guard, got {s.count(old)}')
s=s.replace(old,new,1)

anchor='\nsetPage();\ninitKB911Project();\nkbHistoryStart();'
if s.count(anchor)!=1:
    raise SystemExit('v48: startup anchor missing')

code=r'''

// KB911_V48_DIMENSION_AXIS_END_RESIZE
// The arrow/slash end stretches only along the current dimension axis.
// The blue reference-point circles keep their existing free movement and are
// deliberately kept above these invisible hit areas so they still change angle.
let kbDimAxisDragV48=null;
function kbDimAxisCursorV48(m,p){
 const ax=Math.abs(m.ux),ay=Math.abs(m.uy),mid={x:(m.q1.x+m.q2.x)/2,y:(m.q1.y+m.q2.y)/2};
 if(ay>=.86)return p.y<=mid.y?'n-resize':'s-resize';
 if(ax>=.86)return p.x<=mid.x?'w-resize':'e-resize';
 const dx=p.x-mid.x,dy=p.y-mid.y;
 return dx*dy>=0?'nwse-resize':'nesw-resize';
}
const kbDrawAnchoredDimHandlesBeforeV48=kbDrawAnchoredDimHandlesV40;
kbDrawAnchoredDimHandlesV40=function(g,hoverOnly=false){
 kbDrawAnchoredDimHandlesBeforeV48(g,hoverOnly);
 if(!kbIsAnchoredDimV40(g))return;
 const m=kbAnchoredDimGeomV40(g),r=Math.max(2.8,Math.min(4.4,(+g.dataset.arrowSize||5)*.72));
 const anchors=[...paper.querySelectorAll('.kb-dim-anchor-v40')].filter(n=>n.dataset.owner===g.dataset.id);
 [[m.q1,'start'],[m.q2,'end']].forEach(([p,k])=>{
  paper.appendChild(el('circle',{cx:p.x,cy:p.y,r,fill:'transparent',stroke:'none','pointer-events':'all',cursor:kbDimAxisCursorV48(m,p),class:'kb-dim-axis-end-v48 selection-ui','data-owner':g.dataset.id,'data-axis-end-v48':k}));
 });
 // Exact blue anchor circles remain the topmost targets for free-angle editing.
 anchors.forEach(n=>paper.appendChild(n));
};

paper.addEventListener('pointermove',e=>{
 if(!kbDimAxisDragV48)return;
 const d=kbDimAxisDragV48,p=pt(e);
 let delta=(p.x-d.start.x)*d.ux+(p.y-d.start.y)*d.uy;
 const minLen=.5;
 if(d.key==='p1')delta=Math.min(delta,d.length-minLen);
 else delta=Math.max(delta,-(d.length-minLen));
 const q={x:d.base.x+d.ux*delta,y:d.base.y+d.uy*delta};
 d.obj.dataset[d.key]=`${q.x},${q.y}`;
 renderDim(d.obj);drawSelection();
 e.preventDefault();e.stopImmediatePropagation();
},true);
window.addEventListener('pointerup',()=>{
 if(!kbDimAxisDragV48)return;
 const g=kbDimAxisDragV48.obj;kbDimAxisDragV48=null;
 renderDim(g);selected=g;lastEditable=g;drawSelection();
 setStatus('Длина размера изменена вдоль его оси');
},true);
window.addEventListener('pointercancel',()=>{kbDimAxisDragV48=null},true);
'''

s=s.replace(anchor,code+anchor,1)
for token in [marker,'axisEndV48','kbDimAxisDragV48','kbDimAxisCursorV48','kb-dim-axis-end-v48',"'n-resize'","'s-resize'",'anchors.forEach(n=>paper.appendChild(n))','d.obj.dataset[d.key]']:
    if token not in s: raise SystemExit('v48 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v48: arrow/slash endpoints resize only along dimension axis; blue anchors remain free-angle handles')
