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

# Both projections have one length shared by the left and right tails.
replace_once(
    "down=+g.dataset.tailSize||7,up=3;[[p1,'start'],[p2,'end']].forEach(([p,k])=>{const upper=",
    "down=+g.dataset.tailSize||7,up=+(g.dataset.upperTailSize??g.dataset.upperTailP1??g.dataset.upperTailP2??3);[[p1,'start'],[p2,'end']].forEach(([p,k])=>{const upper="
)
replace_once(
    "function drawAsymTail(g,p,nx,ny,down,c,lw){const a={x:p.x-nx*3,y:p.y-ny*3}",
    "function drawAsymTail(g,p,nx,ny,down,c,lw,up=3){const a={x:p.x-nx*up,y:p.y-ny*up}"
)
replace_once(
    "drawAsymTail(g,p1,dnx,dny,down,c,lw);drawAsymTail(g,p2,dnx,dny,down,c,lw);",
    "drawAsymTail(g,p1,dnx,dny,down,c,lw,+(g.dataset.upperTailSize??g.dataset.upperTailP1??g.dataset.upperTailP2??3));drawAsymTail(g,p2,dnx,dny,down,c,lw,+(g.dataset.upperTailSize??g.dataset.upperTailP1??g.dataset.upperTailP2??3));"
)

# Exactly three controls: two equal-sized end circles at the lower tail tips,
# and one equal-sized circle on the dimension line for both projections.
start = s.index('function drawDimHandles(g,hoverOnly=false){', s.index('function dimDownNormal(g)'))
end = s.index('function drawAsymTail(', start)
s = s[:start] + r'''function drawDimHandles(g,hoverOnly=false){
 if(!g||g.dataset.type!=='dimension')return;
 const {p1,p2}=dimGeom(g),{nx,ny}=dimDownNormal(g),down=+g.dataset.tailSize||7,up=+(g.dataset.upperTailSize??g.dataset.upperTailP1??g.dataset.upperTailP2??3),radius=hoverOnly?.58:.68;
 [[p1,'start'],[p2,'end']].forEach(([p,k])=>{
  const upper={x:p.x-nx*up,y:p.y-ny*up},lower={x:p.x+nx*down,y:p.y+ny*down};
  paper.appendChild(el('line',{x1:upper.x,y1:upper.y,x2:lower.x,y2:lower.y,class:'dim-hover-line selection-ui'}));
  paper.appendChild(el('circle',{cx:lower.x,cy:lower.y,r:radius,class:`dim-end-handle dim-handle-${k} selection-ui`,'data-owner':g.dataset.id}));
 });
 paper.appendChild(el('circle',{cx:(p1.x+p2.x)/2,cy:(p1.y+p2.y)/2,r:radius,class:'dim-tail-handle dim-tail-center selection-ui','data-owner':g.dataset.id}));
}
''' + s[end:]

# End grips once again move endpoints in either direction. The central grip
# changes the shared upper/lower projection lengths in either direction.
replace_once(
    "if(tailDrag){const g=tailDrag.obj,{nx,ny}=dimDownNormal(g),base=parsePt(g.dataset[tailDrag.end]||g.dataset.p1),d=(p.x-base.x)*nx+(p.y-base.y)*ny;g.dataset.tailSize=Math.max(.5,Math.min(300,d));$('tailSize').value=(+g.dataset.tailSize).toFixed(1);renderDim(g);drawSelection();captureDimDefaults(g);return}",
    "if(tailDrag){const g=tailDrag.obj,{p1,p2}=dimGeom(g),{nx,ny}=dimDownNormal(g),mid={x:(p1.x+p2.x)/2,y:(p1.y+p2.y)/2},d=(p.x-mid.x)*nx+(p.y-mid.y)*ny;g.dataset.tailSize=Math.max(2,Math.min(300,d<0?-d:2)).toFixed(2);g.dataset.upperTailSize=Math.max(2,Math.min(300,d>0?d:2)).toFixed(2);$('tailSize').value=(+g.dataset.tailSize).toFixed(1);renderDim(g);drawSelection();captureDimDefaults(g);return}"
)

# Building a dimension has two deliberate gestures. Drag and release the base
# line, then move the pointer to preview the projections and click to finish.
replace_once(
    "dimDraft={p1:p,p2:p};\n   dimPreview=el('line',{x1:p.x,y1:p.y,x2:p.x,y2:p.y,stroke:'#2563eb','stroke-width':'.5','stroke-dasharray':'2 1','vector-effect':'non-scaling-stroke'});",
    "if(dimDraft?.stage==='projection'){const d=dimDraft;dimDraft=null;dimPreview?.remove();dimPreview=null;createDim(d.p1,d.p2);if(selected?.dataset.type==='dimension'){selected.dataset.tailSize=d.down;selected.dataset.upperTailSize=d.up;renderDim(selected);drawSelection();syncDimProps()}e.preventDefault();return}\n   dimDraft={p1:p,p2:p,stage:'line'};\n   dimPreview=el('path',{d:`M ${p.x} ${p.y} L ${p.x} ${p.y}`,fill:'none',stroke:'#085cff','stroke-width':'.9','stroke-dasharray':'3 1.2','pointer-events':'none','vector-effect':'non-scaling-stroke'});"
)
replace_once(
    "if(dimDraft&&tool==='dimension'){dimDraft.p2=p;dimPreview?.setAttribute('x2',p.x);dimPreview?.setAttribute('y2',p.y);return}",
    "if(dimDraft&&tool==='dimension'){if(dimDraft.stage==='line'){dimDraft.p2=p;dimPreview?.setAttribute('d',`M ${dimDraft.p1.x} ${dimDraft.p1.y} L ${p.x} ${p.y}`)}else{const d=dimDraft,{nx,ny}=dimDownNormal({dataset:{p1:`${d.p1.x},${d.p1.y}`,p2:`${d.p2.x},${d.p2.y}`}}),mid={x:(d.p1.x+d.p2.x)/2,y:(d.p1.y+d.p2.y)/2},signed=(p.x-mid.x)*nx+(p.y-mid.y)*ny;d.down=Math.max(2,Math.min(300,signed<0?-signed:2));d.up=Math.max(2,Math.min(300,signed>0?signed:2));const a=d.p1,b=d.p2,trace=q=>`M ${q.x-nx*d.up} ${q.y-ny*d.up} L ${q.x+nx*d.down} ${q.y+ny*d.down}`;dimPreview?.setAttribute('d',`M ${a.x} ${a.y} L ${b.x} ${b.y} ${trace(a)} ${trace(b)}`)}return}"
)
replace_once(
    "if(dimDraft&&tool==='dimension'){const p2=pt(e),p1=dimDraft.p1;dimDraft=null;dimPreview?.remove();dimPreview=null;if(Math.hypot(p2.x-p1.x,p2.y-p1.y)>2)createDim(p1,p2)}",
    "if(dimDraft?.stage==='line'&&tool==='dimension'){const p2=pt(e),p1=dimDraft.p1;if(Math.hypot(p2.x-p1.x,p2.y-p1.y)>2){dimDraft.p2=p2;dimDraft.stage='projection';dimDraft.up=2;dimDraft.down=2;setStatus('Размер: отведите указатель для выпуска линий, затем щёлкните для фиксации')}else{dimDraft=null;dimPreview?.remove();dimPreview=null}}"
)
replace_once(
    "dimDraft=null;textDraft=null;if(textPreview){textPreview.remove();textPreview=null}",
    "dimDraft=null;textDraft=null;if(dimPreview){dimPreview.remove();dimPreview=null}if(textPreview){textPreview.remove();textPreview=null}"
)

p.write_text(s, encoding='utf-8', newline='')
print('Dimension digits can be dragged across the line to change side')
