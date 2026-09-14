from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')

marker = 'KB911_V40_ANCHORED_DIMENSIONS_AND_POINT_SNAP'
if marker in s:
    print('v40 already applied')
    raise SystemExit(0)

# Keep legacy dimensions completely intact.  V40 is an additive model used by
# newly-created dimensions only, so old .KB911 projects remain visually and
# behaviorally compatible with the stable v38 build.
style = r'''<style id="kb911DimensionAnchorV40">
/* KB911_V40_ANCHORED_DIMENSIONS_AND_POINT_SNAP */
.kb-dim-snap-v40{fill:#fff;stroke:#006cff;stroke-width:.7;vector-effect:non-scaling-stroke;pointer-events:none}
.kb-dim-anchor-v40{fill:#fff;stroke:#006cff;stroke-width:.55;vector-effect:non-scaling-stroke}
.kb-dim-line-handle-v40{fill:#006cff;stroke:#fff;stroke-width:.45;vector-effect:non-scaling-stroke}
</style>
'''
if s.count('</head>') != 1:
    raise SystemExit('v40: expected one </head>')
s = s.replace('</head>', style + '</head>', 1)

anchor = '\nsetPage();\ninitKB911Project();\nkbHistoryStart();'
if s.count(anchor) != 1:
    raise SystemExit(f'v40: startup anchor count {s.count(anchor)}')

code = r'''

// KB911_V40_ANCHORED_DIMENSIONS_AND_POINT_SNAP
// New dimension model:
//   data-p1 / data-p2 = immutable object/reference points;
//   data-dim-offset   = signed perpendicular distance of the dimension line.
// Moving the line never changes p1/p2.  Legacy dimensions (without
// data-anchor-model="v40") continue to use the stable v38 renderer/interaction.
const kbLegacyDimGeomV40=dimGeom;
const kbLegacyRenderDimV40=renderDim;
const kbLegacyDrawDimHandlesV40=drawDimHandles;
let kbDimDraftV40=null,kbDimLineDragV40=null,kbDimAnchorDragV40=null,kbDimSnapMarkV40=null;

function kbIsAnchoredDimV40(g){return g?.dataset?.type==='dimension'&&g.dataset.anchorModel==='v40'}
function kbAnchoredDimGeomV40(g){
 const a1=parsePt(g.dataset.p1||'0,0'),a2=parsePt(g.dataset.p2||'0,0'),vx=a2.x-a1.x,vy=a2.y-a1.y,L=Math.hypot(vx,vy)||1,ux=vx/L,uy=vy/L,nx=-uy,ny=ux,offset=+(g.dataset.dimOffset||0);
 const q1={x:a1.x+nx*offset,y:a1.y+ny*offset},q2={x:a2.x+nx*offset,y:a2.y+ny*offset};
 return{a1,a2,q1,q2,ux,uy,nx,ny,L,offset};
}

// Existing helpers that ask for dimGeom (notably label-side dragging) should
// see the visible dimension line, while the true reference points stay in data.
dimGeom=function(g){
 if(!kbIsAnchoredDimV40(g))return kbLegacyDimGeomV40(g);
 const m=kbAnchoredDimGeomV40(g),ts=+(g.dataset.tailSize||0);
 return{p1:m.q1,p2:m.q2,ux:m.ux,uy:m.uy,nx:m.nx,ny:m.ny,ts};
};

function kbRenderAnchoredDimV40(g){
 while(g.firstChild)g.removeChild(g.firstChild);
 const m=kbAnchoredDimGeomV40(g),lw=+g.dataset.lineWidth||.4,c=g.dataset.lineColor||'#111',fs=+g.dataset.fontSize||4,as=+g.dataset.arrowSize||5,aa=+g.dataset.arrowAngle||10;
 const over=Math.max(0,Math.min(80,+(g.dataset.tailSize??2))),side=m.offset<0?-1:1;
 const e1={x:m.q1.x+m.nx*side*over,y:m.q1.y+m.ny*side*over},e2={x:m.q2.x+m.nx*side*over,y:m.q2.y+m.ny*side*over};
 // Witness/extension lines always start at the exact selected object points.
 g.appendChild(el('line',{x1:m.a1.x,y1:m.a1.y,x2:e1.x,y2:e1.y,stroke:c,'stroke-width':lw,'vector-effect':'non-scaling-stroke','pointer-events':'none',class:'dim-extension-v40'}));
 g.appendChild(el('line',{x1:m.a2.x,y1:m.a2.y,x2:e2.x,y2:e2.y,stroke:c,'stroke-width':lw,'vector-effect':'non-scaling-stroke','pointer-events':'none',class:'dim-extension-v40'}));
 g.appendChild(el('line',{x1:m.q1.x,y1:m.q1.y,x2:m.q2.x,y2:m.q2.y,stroke:c,'stroke-width':lw,'vector-effect':'non-scaling-stroke'}));
 drawArrow(g,m.q1,m.ux,m.uy,as,aa,c,lw,1,g.dataset.arrow);
 drawArrow(g,m.q2,m.ux,m.uy,as,aa,c,lw,-1,g.dataset.arrow);
 const mid={x:(m.q1.x+m.q2.x)/2,y:(m.q1.y+m.q2.y)/2},ang=Math.atan2(m.q2.y-m.q1.y,m.q2.x-m.q1.x)*180/Math.PI;
 let ta=ang;if(ta>90||ta<-90)ta+=180;
 let tx=-m.uy,ty=m.ux;if(ty>0){tx=-tx;ty=-ty}
 const off=(fs*.9+1.1)*(g.dataset.labelSide==='below'?-1:1),tm={x:mid.x+tx*off,y:mid.y+ty*off};
 const label=(g.dataset.prefix||'')+(g.dataset.value||'…')+(g.dataset.suffix||'');
 const t=el('text',{x:tm.x,y:tm.y,'text-anchor':'middle','dominant-baseline':'central','font-family':g.dataset.font||'Bahnschrift','font-size':fs,'font-weight':g.dataset.bold==='1'?'700':'400','font-style':g.dataset.italic==='1'?'italic':'normal',fill:g.dataset.textColor||c,transform:`rotate(${ta} ${tm.x} ${tm.y})`,class:'dim-label'});t.textContent=label;
 // Wide transparent hit target belongs to the dimension line itself.
 g.appendChild(el('line',{x1:m.q1.x,y1:m.q1.y,x2:m.q2.x,y2:m.q2.y,class:'dim-hit'}));
 g.appendChild(el('rect',{x:tm.x-Math.max(8,label.length*fs*.6)/2-2,y:tm.y-fs*.85-1,width:Math.max(8,label.length*fs*.6)+4,height:fs*1.7+2,fill:'transparent',transform:t.getAttribute('transform'),class:'dim-label-grab','pointer-events':'all'}));
 g.appendChild(t);
}
renderDim=function(g){if(kbIsAnchoredDimV40(g))return kbRenderAnchoredDimV40(g);return kbLegacyRenderDimV40(g)};

function kbDrawAnchoredDimHandlesV40(g,hoverOnly=false){
 const m=kbAnchoredDimGeomV40(g),r=hoverOnly?.58:.68;
 [[m.a1,'start'],[m.a2,'end']].forEach(([p,k])=>paper.appendChild(el('circle',{cx:p.x,cy:p.y,r,class:`dim-end-handle dim-handle-${k} kb-dim-anchor-v40 selection-ui`,'data-owner':g.dataset.id,'data-anchor-v40':k})));
 paper.appendChild(el('circle',{cx:(m.q1.x+m.q2.x)/2,cy:(m.q1.y+m.q2.y)/2,r,class:'dim-tail-handle kb-dim-line-handle-v40 selection-ui','data-owner':g.dataset.id,'data-line-handle-v40':'1'}));
}
drawDimHandles=function(g,hoverOnly=false){if(kbIsAnchoredDimV40(g))return kbDrawAnchoredDimHandlesV40(g,hoverOnly);return kbLegacyDrawDimHandlesV40(g,hoverOnly)};

function kbSnapRadiusMmV40(){const r=paper.getBoundingClientRect();return Math.max(.35,10*page.w/Math.max(1,r.width))}
function kbClearSnapMarkV40(){kbDimSnapMarkV40?.remove();kbDimSnapMarkV40=null}
function kbShowSnapMarkV40(p){
 kbClearSnapMarkV40();
 kbDimSnapMarkV40=el('circle',{cx:p.x,cy:p.y,r:Math.max(.8,kbSnapRadiusMmV40()*.32),class:'kb-dim-snap-v40 selection-ui'});paper.appendChild(kbDimSnapMarkV40);
}
function kbNearestDimAnchorV40(p,exclude=null){
 const lim=kbSnapRadiusMmV40();let best=null,bestD=lim;
 paper.querySelectorAll('g[data-type="dimension"][data-anchor-model="v40"]').forEach(g=>{
  if(g===exclude)return;
  for(const key of ['p1','p2']){const q=parsePt(g.dataset[key]),d=Math.hypot(p.x-q.x,p.y-q.y);if(d<=bestD){bestD=d;best={x:q.x,y:q.y}}}
 });
 return best;
}
function kbSnapDimPointV40(p,axisBase=null,exclude=null){
 const exact=kbNearestDimAnchorV40(p,exclude);
 if(exact){kbShowSnapMarkV40(exact);return{x:exact.x,y:exact.y,snapped:true}}
 let q={x:p.x,y:p.y},snapped=false;
 if(axisBase){
  const lim=kbSnapRadiusMmV40(),dx=Math.abs(p.x-axisBase.x),dy=Math.abs(p.y-axisBase.y);
  if(dx<=lim&&dx<=dy){q.x=axisBase.x;snapped=true}
  else if(dy<=lim){q.y=axisBase.y;snapped=true}
 }
 if(snapped)kbShowSnapMarkV40(q);else kbClearSnapMarkV40();
 return{x:q.x,y:q.y,snapped};
}

function kbDraftPreviewV40(){
 if(!kbDimDraftV40)return;
 if(kbDimDraftV40.preview){kbDimDraftV40.preview.remove();kbDimDraftV40.preview=null}
 const d=kbDimDraftV40;
 if(d.stage==='anchors'){
  d.preview=el('line',{x1:d.p1.x,y1:d.p1.y,x2:d.p2.x,y2:d.p2.y,stroke:'#006cff','stroke-width':'1.25','stroke-dasharray':'4 1.35','stroke-linecap':'round','pointer-events':'none','vector-effect':'non-scaling-stroke',class:'selection-ui'});paper.appendChild(d.preview);return;
 }
 const z=dimDefaults,g=el('g',{'data-type':'dimension','data-id':'preview-v40','data-anchor-model':'v40','data-p1':`${d.p1.x},${d.p1.y}`,'data-p2':`${d.p2.x},${d.p2.y}`,'data-dim-offset':String(d.offset||0),'data-value':'','data-prefix':z.prefix||'','data-suffix':z.suffix||'','data-arrow':z.arrow||'slim','data-arrow-size':z.arrowSize||'5','data-arrow-angle':z.arrowAngle||'10','data-tail-size':z.tailSize??'2','data-line-width':z.lineWidth||'0.40','data-line-color':'#111111','data-font':z.font||'Bahnschrift','data-font-size':z.fontSize||'4','data-text-color':'#111111','data-bold':z.bold?'1':'0','data-italic':z.italic?'1':'0',class:'selection-ui'});
 kbRenderAnchoredDimV40(g);g.querySelectorAll('*').forEach(n=>n.setAttribute('pointer-events','none'));d.preview=g;paper.appendChild(g);
}
function kbCancelDimensionDraftV40(){
 if(kbDimDraftV40?.preview)kbDimDraftV40.preview.remove();kbDimDraftV40=null;kbClearSnapMarkV40();
}
function kbCreateAnchoredDimensionV40(p1,p2,offset){
 const d=dimDefaults,g=el('g',{'data-type':'dimension','data-id':uid++,'data-anchor-model':'v40','data-p1':`${p1.x},${p1.y}`,'data-p2':`${p2.x},${p2.y}`,'data-dim-offset':String(offset||0),'data-value':'','data-prefix':d.prefix,'data-suffix':d.suffix,'data-arrow':d.arrow,'data-arrow-size':d.arrowSize,'data-arrow-angle':d.arrowAngle,'data-tail-size':d.tailSize??'2','data-line-width':d.lineWidth,'data-line-color':d.lineColor,'data-font':d.font,'data-font-size':d.fontSize,'data-text-color':d.textColor,'data-bold':d.bold?'1':'0','data-italic':d.italic?'1':'0'});
 appendContent(g);renderDim(g);select(g);setTool('dimension-edit',true);setTimeout(()=>{$('dimText').focus();$('dimText').select()},0);return g;
}

// Switching away from the dimension tool also removes an unfinished V40 draft.
const kbSetToolBeforeV40=setTool;
setTool=function(t,force=false){if(t!=='dimension')kbCancelDimensionDraftV40();return kbSetToolBeforeV40(t,force)};

// Capture phase owns the new dimension interaction before the legacy v38
// pointer handlers can move the stored reference points.
paper.addEventListener('pointerdown',e=>{
 if(e.button!==0)return;
 const p=pt(e),obj=groupType(e.target);
 if(tool==='dimension'){
  e.preventDefault();e.stopImmediatePropagation();
  if(kbDimDraftV40?.stage==='offset'){
   const d=kbDimDraftV40;kbDimDraftV40=null;d.preview?.remove();kbClearSnapMarkV40();kbCreateAnchoredDimensionV40(d.p1,d.p2,d.offset||0);return;
  }
  const q=kbSnapDimPointV40(p,null,null);kbDimDraftV40={stage:'anchors',p1:{x:q.x,y:q.y},p2:{x:q.x,y:q.y},preview:null};kbDraftPreviewV40();paper.setPointerCapture?.(e.pointerId);setStatus('Размер: укажите две опорные точки изделия');return;
 }
 if(!kbIsAnchoredDimV40(obj))return;
 if(e.target.closest?.('.dim-label,.dim-label-grab'))return; // existing text-side gesture keeps ownership
 selected=obj;lastEditable=obj;showProps();drawSelection();
 if(e.target.classList?.contains('kb-dim-anchor-v40')){
  const key=e.target.dataset.anchorV40==='start'?'p1':'p2',other=key==='p1'?'p2':'p1';kbDimAnchorDragV40={obj,key,other};e.preventDefault();e.stopImmediatePropagation();return;
 }
 const m=kbAnchoredDimGeomV40(obj);kbDimLineDragV40={obj,start:p,startOffset:m.offset,nx:m.nx,ny:m.ny};e.preventDefault();e.stopImmediatePropagation();
},true);

paper.addEventListener('pointermove',e=>{
 const p=pt(e);
 if(kbDimDraftV40){
  e.preventDefault();e.stopImmediatePropagation();
  const d=kbDimDraftV40;
  if(d.stage==='anchors'){
   const q=kbSnapDimPointV40(p,d.p1,null);d.p2={x:q.x,y:q.y};kbDraftPreviewV40();
  }else{
   const vx=d.p2.x-d.p1.x,vy=d.p2.y-d.p1.y,L=Math.hypot(vx,vy)||1,nx=-vy/L,ny=vx/L,mid={x:(d.p1.x+d.p2.x)/2,y:(d.p1.y+d.p2.y)/2};d.offset=(p.x-mid.x)*nx+(p.y-mid.y)*ny;kbClearSnapMarkV40();kbDraftPreviewV40();
  }
  return;
 }
 if(kbDimAnchorDragV40){
  const d=kbDimAnchorDragV40,other=parsePt(d.obj.dataset[d.other]),q=kbSnapDimPointV40(p,other,d.obj);d.obj.dataset[d.key]=`${q.x},${q.y}`;renderDim(d.obj);drawSelection();e.preventDefault();e.stopImmediatePropagation();return;
 }
 if(kbDimLineDragV40){
  const d=kbDimLineDragV40,delta=(p.x-d.start.x)*d.nx+(p.y-d.start.y)*d.ny;d.obj.dataset.dimOffset=String(d.startOffset+delta);renderDim(d.obj);drawSelection();e.preventDefault();e.stopImmediatePropagation();return;
 }
},true);

window.addEventListener('pointerup',e=>{
 if(kbDimDraftV40?.stage==='anchors'){
  const d=kbDimDraftV40;
  if(Math.hypot(d.p2.x-d.p1.x,d.p2.y-d.p1.y)>1.2){d.stage='offset';d.offset=0;kbClearSnapMarkV40();kbDraftPreviewV40();setStatus('Опорные точки зафиксированы. Теперь отведите размерную линию вверх или вниз и щёлкните')}
  else kbCancelDimensionDraftV40();
 }
 if(kbDimAnchorDragV40||kbDimLineDragV40){kbDimAnchorDragV40=null;kbDimLineDragV40=null;kbClearSnapMarkV40();try{kbHistorySchedule(0)}catch{}}
},true);
window.addEventListener('pointercancel',()=>{kbDimAnchorDragV40=null;kbDimLineDragV40=null;kbClearSnapMarkV40()},true);

document.addEventListener('keydown',e=>{if(e.key==='Escape')kbCancelDimensionDraftV40()},true);

// The old "tail height" field now has the CAD meaning appropriate to the new
// model: how far witness lines protrude beyond the dimension line.  It no longer
// moves either reference point.
try{const n=$('tailSize')?.parentElement?.querySelector('.dp-label');if(n)n.textContent='Вынос за размерную линию, мм'}catch{}
'''

s = s.replace(anchor, code + anchor, 1)

for token in [
    marker,
    "'data-anchor-model':'v40'",
    'data-dim-offset',
    'kbNearestDimAnchorV40',
    'kbDimLineDragV40',
    "n.textContent='Вынос за размерную линию, мм'",
    "setStatus('Опорные точки зафиксированы. Теперь отведите размерную линию вверх или вниз и щёлкните')"
]:
    if token not in s:
        raise SystemExit('v40 guard failed: ' + token)

p.write_text(s, encoding='utf-8', newline='')
print('v40: anchored dimension geometry and point-to-point magnetic snapping installed')
