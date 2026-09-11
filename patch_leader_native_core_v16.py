from pathlib import Path
p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='// KB911_V16_LEADER_NATIVE_CORE'
if marker in s:
    print('v16 already applied'); raise SystemExit(0)

# Integrate the newer leader handles into the ORIGINAL leader pointer pipeline.
old=""" if(e.target.classList?.contains('leader-handle')){\n   const g=findOwner(e.target.dataset.owner,'leader');if(!g)return;\n   selected=g;leaderDrag={obj:g,kind:e.target.dataset.leaderHandle,start:p,p1:parsePt(g.dataset.p1),p2:parsePt(g.dataset.p2),shelf:+g.dataset.shelf||40};e.preventDefault();e.stopImmediatePropagation();return;\n }"""
new=""" const kbH=e.target.closest?.('.leader-handle,.kb-leader-edit-handle');\n if(kbH){\n   const g=findOwner(kbH.dataset.owner,'leader');if(!g)return;\n   const kind=kbH.dataset.leaderHandle||kbH.dataset.kbLeaderHandle;\n   selected=g;lastEditable=g;leaderDrag={obj:g,kind,start:p,p1:parsePt(g.dataset.p1),p2:parsePt(g.dataset.p2),shelf:+g.dataset.shelf||40,textX:+g.dataset.textX,textY:+g.dataset.textY};\n   e.preventDefault();e.stopImmediatePropagation();return;\n }"""
if old not in s: raise SystemExit('v16 original leader handle block not found')
s=s.replace(old,new,1)

old=""" if(d.kind==='move'){const dx=p.x-d.start.x,dy=p.y-d.start.y;g.dataset.p1=`${d.p1.x+dx},${d.p1.y+dy}`;g.dataset.p2=`${d.p2.x+dx},${d.p2.y+dy}`}\n else if(d.kind==='p1')g.dataset.p1=`${p.x},${p.y}`;\n else if(d.kind==='p2'){g.dataset.p2=`${p.x},${p.y}`;g.dataset.dir=p.x>=parsePt(g.dataset.p1).x?'1':'-1'}\n else if(d.kind==='p3'){const p2=parsePt(g.dataset.p2);g.dataset.shelf=String(Math.max(8,Math.abs(p.x-p2.x)));g.dataset.dir=p.x>=p2.x?'1':'-1'}\n renderLeader(g);drawSelection();e.preventDefault();e.stopImmediatePropagation();"""
new=""" if(d.kind==='move'){const dx=p.x-d.start.x,dy=p.y-d.start.y;g.dataset.p1=`${d.p1.x+dx},${d.p1.y+dy}`;g.dataset.p2=`${d.p2.x+dx},${d.p2.y+dy}`;if(Number.isFinite(d.textX)&&Number.isFinite(d.textY)){g.dataset.textX=String(d.textX+dx);g.dataset.textY=String(d.textY+dy)}}\n else if(d.kind==='p1')g.dataset.p1=`${p.x},${p.y}`;\n else if(d.kind==='p2'){g.dataset.p2=`${p.x},${p.y}`;g.dataset.dir=p.x>=parsePt(g.dataset.p1).x?'1':'-1'}\n else if(d.kind==='p3'){const p2=parsePt(g.dataset.p2);g.dataset.shelf=String(Math.max(8,Math.abs(p.x-p2.x)));g.dataset.dir=p.x>=p2.x?'1':'-1'}\n else if(d.kind==='text'){g.dataset.textX=String(p.x);g.dataset.textY=String(p.y)}\n renderLeader(g);drawSelection();e.preventDefault();e.stopImmediatePropagation();"""
if old not in s: raise SystemExit('v16 original leader move block not found')
s=s.replace(old,new,1)

idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end not found')
code=r'''

// KB911_V16_LEADER_NATIVE_CORE
// The original leader handler now owns p1/p2/p3/text dragging. Make the four
// handles deliberately visible and easy to grab at normal A3 zoom.
drawLeaderHandles=function(g){
 if(!g||g.dataset.type!=='leader')return;
 const {p1,p2,p3}=leaderPts(g),tp=kbLeaderTextPoint(g);
 [[p1,'p1'],[p2,'p2'],[p3,'p3']].forEach(([p,k])=>paper.appendChild(el('circle',{cx:p.x,cy:p.y,r:1.6,class:'handle selection-ui kb-leader-edit-handle','data-owner':g.dataset.id,'data-kb-leader-handle':k,style:'cursor:crosshair;fill:#fff;stroke:#2563eb;stroke-width:.55'})));
 paper.appendChild(el('rect',{x:tp.x-1.8,y:tp.y-1.8,width:3.6,height:3.6,rx:.55,ry:.55,class:'handle selection-ui kb-leader-edit-handle','data-owner':g.dataset.id,'data-kb-leader-handle':'text',style:'cursor:move;fill:#fff;stroke:#2563eb;stroke-width:.55'}));
};
window.KB911_LEADER_CORE_V16={nativePipeline:true,handles:['p1','p2','p3','text']};
'''
s=s[:idx]+code+s[idx:]
for token in ['KB911_V16_LEADER_NATIVE_CORE',"closest?.('.leader-handle,.kb-leader-edit-handle')","else if(d.kind==='text')",'KB911_LEADER_CORE_V16']:
    if token not in s: raise SystemExit('v16 token missing '+token)
p.write_text(s,encoding='utf-8',newline='')
print('v16 leader handles integrated into original leader core')
