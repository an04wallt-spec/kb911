from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')

def replace_once(old, new):
    global s
    if s.count(old) != 1:
        raise SystemExit(f'dimension label side: expected one occurrence, got {s.count(old)}: {old[:90]}')
    s = s.replace(old, new, 1)

def replace_both(old, new):
    global s
    if s.count(old) != 2:
        raise SystemExit(f'dimension label side: expected two renderers, got {s.count(old)}: {old[:90]}')
    s = s.replace(old, new)

# The choice belongs to each dimension. Missing data in existing projects retains
# the established placement above the line.
replace_once(
    "const off=fs*.9+1.1,tm={x:mid.x+nx*off,y:mid.y+ny*off};",
    "const off=(fs*.9+1.1)*(g.dataset.labelSide==='below'?-1:1),tm={x:mid.x+nx*off,y:mid.y+ny*off};"
)
replace_once(
    "const off=fs*.9+1.1,tm={x:mid.x+nx*off,y:mid.y+ny*off},label=",
    "const off=(fs*.9+1.1)*(g.dataset.labelSide==='below'?-1:1),tm={x:mid.x+nx*off,y:mid.y+ny*off},label="
)

replace_once('.dim-label{cursor:text}', '.dim-label{cursor:grab;touch-action:none}')

# The broad transparent line hit stroke is drawn after the text in the old
# renderer and intercepts clicks on most digits. Put a transparent grab area
# above that stroke, so the pointer reliably starts on the number itself.
replace_both(
    "g.appendChild(t);g.appendChild(el('line',{x1:p1.x,y1:p1.y,x2:p2.x,y2:p2.y,class:'dim-hit'}))",
    "g.appendChild(el('line',{x1:p1.x,y1:p1.y,x2:p2.x,y2:p2.y,class:'dim-hit'}));g.appendChild(el('rect',{x:tm.x-Math.max(8,label.length*fs*.6)/2-2,y:tm.y-fs*.85-1,width:Math.max(8,label.length*fs*.6)+4,height:fs*1.7+2,fill:'transparent',transform:t.getAttribute('transform'),class:'dim-label-grab','pointer-events':'all'}));g.appendChild(t)"
)
replace_once('.dim-label{cursor:grab;touch-action:none}', '.dim-label,.dim-label-grab{cursor:grab;touch-action:none}')

# Capture only gestures starting on the digits; keep all established dimension
# line, endpoint, and tail handlers as they are.
anchor = '// ---------- Native KB911 project format ----------'
code = r'''// KB911_DIMENSION_LABEL_DRAG_SIDE
let kbDimensionLabelDrag=null;
paper.addEventListener('pointerdown',e=>{
 if(e.button!==0||tool==='dimension'||pasteDraft||!e.target.closest?.('.dim-label,.dim-label-grab'))return;
 const g=groupType(e.target);if(g?.dataset.type!=='dimension')return;
 if(selected!==g){selected=g;showProps();drawSelection()}
 lastEditable=g;kbDimensionLabelDrag={obj:g,id:e.pointerId};
 paper.setPointerCapture?.(e.pointerId);
 e.stopImmediatePropagation();
},true);
paper.addEventListener('pointermove',e=>{
 const d=kbDimensionLabelDrag;if(!d||d.id!==e.pointerId)return;
 const {p1,p2,uy}=dimGeom(d.obj),ux=(p2.x-p1.x)/(Math.hypot(p2.x-p1.x,p2.y-p1.y)||1);
 let nx=-uy,ny=ux;if(ny>0){nx=-nx;ny=-ny}
 const midX=(p1.x+p2.x)/2,midY=(p1.y+p2.y)/2,q=pt(e),signed=(q.x-midX)*nx+(q.y-midY)*ny;
 const side=signed>.4?'above':signed<-.4?'below':null;
 if(side&&d.obj.dataset.labelSide!==side){d.obj.dataset.labelSide=side;renderDim(d.obj);drawSelection()}
 e.preventDefault();e.stopImmediatePropagation();
},true);
function kbFinishDimensionLabelDrag(e){
 if(!kbDimensionLabelDrag||kbDimensionLabelDrag.id!==e.pointerId)return;
 kbDimensionLabelDrag=null;
 if(paper.hasPointerCapture?.(e.pointerId))paper.releasePointerCapture(e.pointerId);
}
window.addEventListener('pointerup',kbFinishDimensionLabelDrag,true);
window.addEventListener('pointercancel',kbFinishDimensionLabelDrag,true);

'''
replace_once(anchor, code + anchor)

p.write_text(s, encoding='utf-8', newline='')
print('Dimension digits can be dragged across the line to change side')
