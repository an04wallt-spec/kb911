from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V40_HANDLE_OWNER_FIX'
if marker in s:
    print('v40 handle-owner fix already applied')
    raise SystemExit(0)
anchor='\nsetPage();\ninitKB911Project();\nkbHistoryStart();'
if s.count(anchor)!=1:
    raise SystemExit('v40 handle fix: startup anchor missing')
code=r'''
// KB911_V40_HANDLE_OWNER_FIX
// Selection handles are direct children of <svg>, not children of the dimension
// group. Resolve them through data-owner before the legacy bubble handlers see
// the event.
paper.addEventListener('pointerdown',e=>{
 if(e.button!==0)return;
 const h=e.target;
 if(!h.classList?.contains('kb-dim-anchor-v40')&&!h.classList?.contains('kb-dim-line-handle-v40'))return;
 const g=findOwner(h.dataset.owner,'dimension');if(!kbIsAnchoredDimV40(g))return;
 selected=g;lastEditable=g;showProps();drawSelection();
 const p=pt(e);
 if(h.classList.contains('kb-dim-anchor-v40')){
  const key=h.dataset.anchorV40==='start'?'p1':'p2',other=key==='p1'?'p2':'p1';
  kbDimAnchorDragV40={obj:g,key,other};
 }else{
  const m=kbAnchoredDimGeomV40(g);kbDimLineDragV40={obj:g,start:p,startOffset:m.offset,nx:m.nx,ny:m.ny};
 }
 e.preventDefault();e.stopImmediatePropagation();
},true);
'''
s=s.replace(anchor,code+anchor,1)
if marker not in s:raise SystemExit('v40 handle fix guard failed')
p.write_text(s,encoding='utf-8',newline='')
print('v40: anchored dimension handles resolve owner correctly')
