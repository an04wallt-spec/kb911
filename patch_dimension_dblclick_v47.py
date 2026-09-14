from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V47_DIMENSION_DBLCLICK_ANYWHERE'
if marker in s:
    print('v47 already applied')
    raise SystemExit(0)

# v42 already gives direct dimension handles priority over the sticky Dimension
# creation tool. Extend that exact interaction point only for the new invisible
# witness-line hit zone, so a click there selects the existing dimension instead
# of starting/moving anything. This keeps single-click/drag behavior unchanged
# everywhere else.
v42=s.find('// KB911_V42_MAGNET_AND_ACTIVE_CENTER_HANDLE')
if v42<0:
    raise SystemExit('v47: v42 interaction marker missing')
toolpos=s.find(" if(tool==='dimension'){",v42)
if toolpos<0:
    raise SystemExit('v47: v42 dimension-tool branch missing')
priority=r''' const editHitV47=e.target.closest?.('.kb-dim-edit-hit-v47');
 if(editHitV47){
  const ownerV47=findOwner(editHitV47.dataset.owner,'dimension')||groupType(editHitV47);
  if(ownerV47?.dataset?.type==='dimension'){
   selected=ownerV47;lastEditable=ownerV47;drawSelection();
   e.preventDefault();e.stopImmediatePropagation();return;
  }
 }
'''
s=s[:toolpos]+priority+s[toolpos:]

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

// Witness/extension lines were intentionally non-interactive. Add only an
// invisible 8 px non-scaling hit target; the visible line and its geometry are
// left untouched. data-owner lets the target resolve back to the dimension.
const kbRenderAnchoredDimBeforeV47=kbRenderAnchoredDimV40;
kbRenderAnchoredDimV40=function(g){
 kbRenderAnchoredDimBeforeV47(g);
 const ext=[...g.querySelectorAll('.dim-extension-v40')];
 ext.forEach(line=>{
  const hit=el('line',{
   x1:line.getAttribute('x1'),y1:line.getAttribute('y1'),
   x2:line.getAttribute('x2'),y2:line.getAttribute('y2'),
   stroke:'transparent','stroke-width':8,'vector-effect':'non-scaling-stroke',
   'pointer-events':'stroke','data-owner':g.dataset.id,
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
for token in [marker,'editHitV47','kbDimensionOwnerV47','kbOpenDimensionEditorV47','kb-dim-edit-hit-v47',"'data-owner':g.dataset.id","vector-effect':'non-scaling-stroke'", "paper.addEventListener('dblclick'","setTool('dimension-edit',true);syncDimProps();openDimPopup()"]:
    if token not in s: raise SystemExit('v47 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v47: double-click anywhere on a dimension opens full settings without changing existing drag behavior')
