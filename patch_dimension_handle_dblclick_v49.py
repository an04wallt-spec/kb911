from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V49_DIMENSION_HANDLE_LOGICAL_DBLCLICK'
if marker in s:
    print('v49 already applied')
    raise SystemExit(0)

# The blue SVG handles are selection UI. Some interaction paths redraw that UI
# after the first click, so the browser no longer sees the second click as being
# on the same DOM node and native dblclick can be lost. Detect the logical
# handle (dimension id + handle role) before v42 consumes pointerdown.
needle=" const directHandleV42=e.target.closest?.('.kb-dim-anchor-v40,.kb-dim-line-handle-v40');"
if s.count(needle)!=1:
    raise SystemExit(f'v49: expected one v42 direct-handle anchor, got {s.count(needle)}')

priority=r''' // KB911_V49_DIMENSION_HANDLE_LOGICAL_DBLCLICK
 const logicalHandleV49=e.target.closest?.('.kb-dim-anchor-v40,.kb-dim-line-handle-v40');
 if(logicalHandleV49){
  const ownerV49=findOwner(logicalHandleV49.dataset.owner,'dimension');
  if(kbIsAnchoredDimV40(ownerV49)){
   const kindV49=logicalHandleV49.classList.contains('kb-dim-line-handle-v40')
    ?'center':('anchor-'+(logicalHandleV49.dataset.anchorV40||''));
   const nowV49=performance.now(),prevV49=kbDimHandleTapV49;
   const secondV49=prevV49&&prevV49.owner===ownerV49.dataset.id&&prevV49.kind===kindV49&&
    nowV49-prevV49.time<=480&&Math.hypot(e.clientX-prevV49.x,e.clientY-prevV49.y)<=10;
   if(secondV49){
    kbDimHandleTapV49=null;
    kbDimAnchorDragV40=null;kbDimLineDragV40=null;kbDimAxisDragV48=null;kbClearSnapMarkV40();
    e.preventDefault();e.stopImmediatePropagation();
    kbOpenDimensionEditorV47(ownerV49);return;
   }
   kbDimHandleTapV49={owner:ownerV49.dataset.id,kind:kindV49,time:nowV49,x:e.clientX,y:e.clientY,pointerId:e.pointerId};
  }
 }
'''
s=s.replace(needle,priority+needle,1)

anchor='\nsetPage();\ninitKB911Project();\nkbHistoryStart();'
if s.count(anchor)!=1:
    raise SystemExit('v49: startup anchor missing')

code=r'''

// Logical double-click state for dimension selection handles. Movement cancels
// the candidate, so a normal drag never turns into an editor double-click.
let kbDimHandleTapV49=null;
window.addEventListener('pointermove',e=>{
 const c=kbDimHandleTapV49;
 if(c&&c.pointerId===e.pointerId&&Math.hypot(e.clientX-c.x,e.clientY-c.y)>6)kbDimHandleTapV49=null;
},true);
window.addEventListener('pointercancel',e=>{
 if(kbDimHandleTapV49?.pointerId===e.pointerId)kbDimHandleTapV49=null;
},true);
'''
s=s.replace(anchor,code+anchor,1)

for token in [marker,'logicalHandleV49','kbDimHandleTapV49','secondV49','kbOpenDimensionEditorV47(ownerV49)','Math.hypot(e.clientX-c.x,e.clientY-c.y)>6']:
    if token not in s: raise SystemExit('v49 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v49: logical double-click restored on all three blue dimension handles')
