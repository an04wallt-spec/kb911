from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='// KB911_V17_LEADER_CORE_IN_SCOPE'
if marker in s:
    print('v17 already applied')
    raise SystemExit(0)

# Work ONLY inside the original application IIFE where $, selected, leaderPts,
# renderLeader, drawSelection, etc. actually live. Previous late patches were
# appended outside this scope and therefore never controlled the live UI.

# 1) Replace leader rendering with support for an independently positioned text.
a=s.find('function renderLeader(g){', s.find('function leaderPts(g){'))
b=s.find('function drawLeaderHandles(g){', a)
if a<0 or b<0:
    raise SystemExit('leader render block not found')
render=r'''function kbLeaderTextPointV17(g){
 const {p2,p3}=leaderPts(g),fs=+g.dataset.fontSize||4;
 const dx=+g.dataset.textX,dy=+g.dataset.textY;
 return {x:Number.isFinite(dx)?dx:(p2.x+p3.x)/2,y:Number.isFinite(dy)?dy:p2.y-fs*.85};
}
function renderLeader(g){
 while(g.firstChild)g.removeChild(g.firstChild);
 const {p1,p2,p3}=leaderPts(g),c=g.dataset.lineColor||dimDefaults.lineColor||'#111111',lw=+(g.dataset.lineWidth||dimDefaults.lineWidth||.4),as=+(g.dataset.arrowSize||dimDefaults.arrowSize||5),aa=+(g.dataset.arrowAngle||dimDefaults.arrowAngle||10),sty=g.dataset.arrow||dimDefaults.arrow||'slim';
 g.appendChild(el('line',{x1:p1.x,y1:p1.y,x2:p2.x,y2:p2.y,stroke:c,'stroke-width':lw,'vector-effect':'non-scaling-stroke'}));
 g.appendChild(el('line',{x1:p2.x,y1:p2.y,x2:p3.x,y2:p3.y,stroke:c,'stroke-width':lw,'vector-effect':'non-scaling-stroke'}));
 const len=Math.hypot(p2.x-p1.x,p2.y-p1.y)||1,ux=(p2.x-p1.x)/len,uy=(p2.y-p1.y)/len;
 drawArrow(g,p1,ux,uy,as,aa,c,lw,1,sty);
 const fs=+g.dataset.fontSize||4,tp=kbLeaderTextPointV17(g),t=el('text',{x:tp.x,y:tp.y,'text-anchor':'middle','dominant-baseline':'central','font-family':g.dataset.font||'Bahnschrift','font-size':fs,'font-weight':g.dataset.bold==='1'?'700':'400','font-style':g.dataset.italic==='1'?'italic':'normal',fill:g.dataset.textColor||c});
 t.textContent=g.dataset.value||'Сноска';g.appendChild(t);
 g.appendChild(el('path',{d:`M ${p1.x} ${p1.y} L ${p2.x} ${p2.y} L ${p3.x} ${p3.y}`,fill:'none',stroke:'transparent','stroke-width':8,class:'leader-hit hover-movable'}));
}
'''
s=s[:a]+render+s[b:]

# 2) Replace handles. Three round geometry handles + one square text handle.
a=s.find('function drawLeaderHandles(g){', s.find('function kbLeaderTextPointV17'))
b=s.find('function createLeader(p1,p2){', a)
if a<0 or b<0:
    raise SystemExit('leader handles block not found')
handles=r'''function drawLeaderHandles(g){
 if(!g||g.dataset.type!=='leader')return;
 const {p1,p2,p3}=leaderPts(g),tp=kbLeaderTextPointV17(g);
 [[p1,'p1'],[p2,'p2'],[p3,'p3']].forEach(([q,k])=>paper.appendChild(el('circle',{cx:q.x,cy:q.y,r:1.55,class:'handle selection-ui leader-handle','data-owner':g.dataset.id,'data-leader-handle':k,style:'cursor:crosshair;fill:#fff;stroke:#2563eb;stroke-width:.55'})));
 paper.appendChild(el('rect',{x:tp.x-1.8,y:tp.y-1.8,width:3.6,height:3.6,rx:.55,ry:.55,class:'handle selection-ui leader-handle','data-owner':g.dataset.id,'data-leader-handle':'text',style:'cursor:move;fill:#fff;stroke:#2563eb;stroke-width:.55'}));
}
'''
s=s[:a]+handles+s[b:]

# Ensure the common selection path knows leaders.
needle="if(selected.dataset.type==='image'){drawImageHandles(selected);return}}"
if needle in s:
    s=s.replace(needle,"if(selected.dataset.type==='image'){drawImageHandles(selected);return}if(selected.dataset.type==='leader'){drawLeaderHandles(selected);return}}",1)
elif "if(selected.dataset.type==='leader'){drawLeaderHandles(selected);return}" not in s:
    raise SystemExit('drawSelection leader branch not found')

# 3) Replace the ORIGINAL leader pointer pipeline in-scope. Handle detection is
# deliberately before tool==='leader' so editing works even immediately after
# creating a leader while that tool is still active.
close_i=s.find('function closeLeaderPopup()')
a=s.find("paper.addEventListener('pointerdown',e=>{", close_i)
b=s.find("paper.addEventListener('dblclick',e=>", a)
if close_i<0 or a<0 or b<0:
    raise SystemExit('leader pointer pipeline not found')
# include through pointerup block, but leave dblclick itself in place
pipeline=r'''paper.addEventListener('pointerdown',e=>{
 const p=pt(e),obj=groupType(e.target);
 const h=e.target.closest?.('.leader-handle');
 if(h){
   const g=findOwner(h.dataset.owner,'leader');if(!g)return;
   const kind=h.dataset.leaderHandle;
   const tp=kbLeaderTextPointV17(g);
   selected=g;lastEditable=g;
   leaderDrag={obj:g,kind,start:p,p1:parsePt(g.dataset.p1),p2:parsePt(g.dataset.p2),shelf:+g.dataset.shelf||40,textX:tp.x,textY:tp.y};
   e.preventDefault();e.stopImmediatePropagation();return;
 }
 if(tool==='leader'){
   e.preventDefault();e.stopImmediatePropagation();
   leaderDraft={p1:p,p2:p};
   leaderPreview=el('path',{d:`M ${p.x} ${p.y} L ${p.x} ${p.y}`,fill:'none',stroke:'#2563eb','stroke-width':'.5','stroke-dasharray':'2 1','pointer-events':'none'});paper.appendChild(leaderPreview);return;
 }
 if(obj?.dataset.type==='leader'){
   const tp=kbLeaderTextPointV17(obj);
   selected=obj;lastEditable=obj;drawSelection();
   leaderDrag={obj,start:p,kind:'move',p1:parsePt(obj.dataset.p1),p2:parsePt(obj.dataset.p2),textX:tp.x,textY:tp.y};
   e.preventDefault();e.stopImmediatePropagation();
 }
},true);
paper.addEventListener('pointermove',e=>{
 const p=pt(e);
 if(leaderDraft&&tool==='leader'){
   leaderDraft.p2=p;const dir=p.x>=leaderDraft.p1.x?1:-1,p3x=p.x+dir*40;leaderPreview?.setAttribute('d',`M ${leaderDraft.p1.x} ${leaderDraft.p1.y} L ${p.x} ${p.y} L ${p3x} ${p.y}`);e.preventDefault();e.stopImmediatePropagation();return;
 }
 if(!leaderDrag)return;
 const d=leaderDrag,g=d.obj;
 if(d.kind==='move'){
   const dx=p.x-d.start.x,dy=p.y-d.start.y;
   g.dataset.p1=`${d.p1.x+dx},${d.p1.y+dy}`;g.dataset.p2=`${d.p2.x+dx},${d.p2.y+dy}`;
   g.dataset.textX=String(d.textX+dx);g.dataset.textY=String(d.textY+dy);
 }else if(d.kind==='p1'){
   g.dataset.p1=`${p.x},${p.y}`;
 }else if(d.kind==='p2'){
   const dx=p.x-d.p2.x,dy=p.y-d.p2.y;
   g.dataset.p2=`${p.x},${p.y}`;
   g.dataset.textX=String(d.textX+dx);g.dataset.textY=String(d.textY+dy);
 }else if(d.kind==='p3'){
   const p2=parsePt(g.dataset.p2);g.dataset.shelf=String(Math.max(8,Math.abs(p.x-p2.x)));g.dataset.dir=p.x>=p2.x?'1':'-1';
 }else if(d.kind==='text'){
   g.dataset.textX=String(p.x);g.dataset.textY=String(p.y);
 }
 renderLeader(g);drawSelection();e.preventDefault();e.stopImmediatePropagation();
},true);
window.addEventListener('pointerup',e=>{
 if(leaderDraft&&tool==='leader'){
   const p2=pt(e),p1=leaderDraft.p1;leaderDraft=null;leaderPreview?.remove();leaderPreview=null;
   if(Math.hypot(p2.x-p1.x,p2.y-p1.y)>2)createLeader(p1,p2);
 }
 leaderDrag=null;
},true);
'''
s=s[:a]+pipeline+s[b:]

# 4) Add popup dragging INSIDE the same IIFE/scope, immediately after leader dblclick.
dbl="paper.addEventListener('dblclick',e=>{const obj=groupType(e.target);if(obj?.dataset.type==='leader'){e.preventDefault();e.stopImmediatePropagation();openLeaderPopup(obj)}},true);"
pos=s.find(dbl, close_i)
if pos<0:
    raise SystemExit('leader dblclick anchor not found')
pos+=len(dbl)
popup=r'''

// KB911_V17_LEADER_CORE_IN_SCOPE
let kbLeaderPopupDragV17=null;
const kbLeaderPopupV17=$('leaderPopup'),kbLeaderHeaderV17=$('leaderPopupHeader');
kbLeaderHeaderV17.addEventListener('pointerdown',e=>{
 if(e.target.id==='leaderPopupClose')return;
 const r=kbLeaderPopupV17.getBoundingClientRect();
 kbLeaderPopupDragV17={id:e.pointerId,dx:e.clientX-r.left,dy:e.clientY-r.top};
 try{kbLeaderHeaderV17.setPointerCapture(e.pointerId)}catch{}
 e.preventDefault();e.stopImmediatePropagation();
},true);
kbLeaderHeaderV17.addEventListener('pointermove',e=>{
 const d=kbLeaderPopupDragV17;if(!d||d.id!==e.pointerId)return;
 kbLeaderPopupV17.style.left=Math.max(0,Math.min(innerWidth-kbLeaderPopupV17.offsetWidth,e.clientX-d.dx))+'px';
 kbLeaderPopupV17.style.top=Math.max(0,Math.min(innerHeight-kbLeaderPopupV17.offsetHeight,e.clientY-d.dy))+'px';
 e.preventDefault();e.stopImmediatePropagation();
},true);
function kbLeaderPopupEndV17(e){
 if(!kbLeaderPopupDragV17)return;
 try{kbLeaderHeaderV17.releasePointerCapture(kbLeaderPopupDragV17.id)}catch{}
 kbLeaderPopupDragV17=null;e?.preventDefault?.();e?.stopImmediatePropagation?.();
}
kbLeaderHeaderV17.addEventListener('pointerup',kbLeaderPopupEndV17,true);
kbLeaderHeaderV17.addEventListener('pointercancel',kbLeaderPopupEndV17,true);
'''
s=s[:pos]+popup+s[pos:]

for token in ['KB911_V17_LEADER_CORE_IN_SCOPE','kbLeaderTextPointV17','data-leader-handle\':\'text','kbLeaderPopupDragV17']:
    if token not in s:
        raise SystemExit('v17 guard missing: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v17 leader editing integrated inside live application scope')
