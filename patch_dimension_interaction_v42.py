from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')
marker = 'KB911_V42_MAGNET_AND_ACTIVE_CENTER_HANDLE'
if marker in s:
    print('v42 dimension interaction already applied')
    raise SystemExit(0)

old = """paper.addEventListener('pointerdown',e=>{\n if(e.button!==0)return;\n const p=pt(e),obj=groupType(e.target);\n if(tool==='dimension'){"""
new = """paper.addEventListener('pointerdown',e=>{\n if(e.button!==0)return;\n const p=pt(e),obj=groupType(e.target);\n // KB911_V42_MAGNET_AND_ACTIVE_CENTER_HANDLE\n // Existing anchored handles take priority over the persistent creation tool.\n const directHandleV42=e.target.closest?.('.kb-dim-anchor-v40,.kb-dim-line-handle-v40');\n if(directHandleV42){\n  const ownerV42=findOwner(directHandleV42.dataset.owner,'dimension');\n  if(kbIsAnchoredDimV40(ownerV42)){\n   selected=ownerV42;lastEditable=ownerV42;drawSelection();\n   if(directHandleV42.classList.contains('kb-dim-anchor-v40')){\n    const keyV42=directHandleV42.dataset.anchorV40==='start'?'p1':'p2',otherV42=keyV42==='p1'?'p2':'p1';\n    kbDimAnchorDragV40={obj:ownerV42,key:keyV42,other:otherV42};\n   }else{\n    const mV42=kbAnchoredDimGeomV40(ownerV42);\n    kbDimLineDragV40={obj:ownerV42,start:p,startOffset:mV42.offset,nx:mV42.nx,ny:mV42.ny};\n   }\n   e.preventDefault();e.stopImmediatePropagation();return;\n  }\n }\n if(tool==='dimension'){"""
if s.count(old) != 1:
    raise SystemExit(f'v42: expected one primary v40 pointerdown anchor, got {s.count(old)}')
s = s.replace(old, new, 1)

anchor = '\nsetPage();\ninitKB911Project();\nkbHistoryStart();'
if s.count(anchor) != 1:
    raise SystemExit('v42: startup anchor missing')

style = r'''<style id="kb911DimensionInteractionV42">
/* KB911_V42_MAGNET_AND_ACTIVE_CENTER_HANDLE */
.kb-dim-line-handle-v40{cursor:move!important;pointer-events:all!important;fill:#2563eb!important;fill-opacity:.88!important;stroke:#fff!important}
</style>
'''
if s.count('</head>') != 1:
    raise SystemExit('v42: expected one </head>')
s = s.replace('</head>', style + '</head>', 1)

code = r'''

kbSnapRadiusMmV40=function(){
 const r=paper.getBoundingClientRect();
 return Math.max(.35,14*page.w/Math.max(1,r.width));
};

paper.addEventListener('pointermove',e=>{
 if(tool!=='dimension'||kbDimDraftV40||kbDimLineDragV40||kbDimAnchorDragV40)return;
 const exact=kbNearestDimAnchorV40(pt(e),null);
 if(exact)kbShowSnapMarkV40(exact);else kbClearSnapMarkV40();
},true);
paper.addEventListener('pointerleave',()=>{if(tool==='dimension'&&!kbDimDraftV40)kbClearSnapMarkV40()},true);
'''
s = s.replace(anchor, code + anchor, 1)

for token in [
    marker,
    'directHandleV42',
    'kbDimLineDragV40={obj:ownerV42',
    '14*page.w',
    "if(tool!=='dimension'||kbDimDraftV40",
    'pointer-events:all!important'
]:
    if token not in s:
        raise SystemExit('v42 guard failed: ' + token)

p.write_text(s, encoding='utf-8', newline='')
print('v42: magnetic anchors restored and center handle now moves the full dimension line')
