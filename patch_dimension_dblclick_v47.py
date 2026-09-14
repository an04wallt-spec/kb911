from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V47_DIMENSION_DBLCLICK_ANYWHERE'
if marker in s:
    print('v47 already applied')
    raise SystemExit(0)

anchor='\nsetPage();\ninitKB911Project();\nkbHistoryStart();'
if s.count(anchor)!=1:
    raise SystemExit('v47: startup anchor missing')

code=r'''

// KB911_V47_DIMENSION_DBLCLICK_ANYWHERE
// Any visible/interactive part of a dimension opens the full dimension editor
// on double click. Selection handles are direct SVG children, therefore they
// are resolved through data-owner as well as through the dimension <g> itself.
function kbDimensionOwnerV47(target){
 if(!target)return null;
 const owned=target.closest?.('[data-owner]');
 if(owned?.dataset?.owner){
  const g=findOwner(owned.dataset.owner,'dimension');
  if(g)return g;
 }
 const direct=target.closest?.('g[data-type="dimension"]');
 if(direct)return direct;
 const obj=groupType(target);
 return obj?.dataset?.type==='dimension'?obj:null;
}
function kbOpenDimensionEditorV47(g){
 if(!g||g.dataset.type!=='dimension')return;
 kbDimLineDragV40=null;kbDimAnchorDragV40=null;kbClearSnapMarkV40();
 if(typeof kbCancelDimensionDraftV40==='function')kbCancelDimensionDraftV40();
 selected=g;lastEditable=g;drawSelection();
 setTool('dimension-edit',true);syncDimProps();openDimPopup();
 setStatus('Настройки размера');
}

// Anchored witness/extension lines were intentionally non-interactive. Add a
// generous transparent hit zone so even a tiny 20–50 mm dimension is easy to
// edit without changing its visible geometry.
const kbRenderAnchoredDimBeforeV47=kbRenderAnchoredDimV40;
kbRenderAnchoredDimV40=function(g){
 kbRenderAnchoredDimBeforeV47(g);
 const ext=[...g.querySelectorAll('.dim-extension-v40')];
 ext.forEach(line=>{
  const hit=el('line',{
   x1:line.getAttribute('x1'),y1:line.getAttribute('y1'),
   x2:line.getAttribute('x2'),y2:line.getAttribute('y2'),
   stroke:'transparent','stroke-width':7,'pointer-events':'stroke',
   class:'kb-dim-edit-hit-v47'
  });
  g.appendChild(hit);
 });
};

paper.addEventListener('dblclick',e=>{
 const g=kbDimensionOwnerV47(e.target);
 if(!g)return;
 e.preventDefault();e.stopImmediatePropagation();
 kbOpenDimensionEditorV47(g);
},true);
'''

s=s.replace(anchor,code+anchor,1)
for token in [marker,'kbDimensionOwnerV47','kbOpenDimensionEditorV47','kb-dim-edit-hit-v47',"paper.addEventListener('dblclick'","setTool('dimension-edit',true);syncDimProps();openDimPopup()"]:
    if token not in s: raise SystemExit('v47 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v47: double-click anywhere on a dimension opens full settings')
