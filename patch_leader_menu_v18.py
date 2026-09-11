from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='// KB911_V18_LEADER_TEXT_LOCK_AND_MENU_CLOSE'
if marker in s:
    print('v18 already applied')
    raise SystemExit(0)

# --- 1. Leader text is automatic again: no independent text handle/position. ---
start=s.find('function kbLeaderTextPointV17(g){')
end=s.find('function renderLeader(g){', start)
if start<0 or end<0:
    raise SystemExit('v18: kbLeaderTextPointV17 not found')
auto=r'''function kbLeaderTextPointV17(g){
 const {p2,p3}=leaderPts(g),fs=+g.dataset.fontSize||4;
 // Old projects/builds may contain manual text coordinates. They are obsolete.
 delete g.dataset.textX;delete g.dataset.textY;
 return {x:(p2.x+p3.x)/2,y:p2.y-fs*.85};
}
'''
s=s[:start]+auto+s[end:]

# Replace the live handles function produced by v17 with geometry handles only.
start=s.find('function drawLeaderHandles(g){', s.find('function kbLeaderTextPointV17'))
end=s.find('function createLeader(p1,p2){', start)
if start<0 or end<0:
    raise SystemExit('v18: live drawLeaderHandles not found')
handles=r'''function drawLeaderHandles(g){
 if(!g||g.dataset.type!=='leader')return;
 const {p1,p2,p3}=leaderPts(g);
 [[p1,'p1'],[p2,'p2'],[p3,'p3']].forEach(([q,k])=>paper.appendChild(el('circle',{cx:q.x,cy:q.y,r:1.55,class:'handle selection-ui leader-handle','data-owner':g.dataset.id,'data-leader-handle':k,style:'cursor:crosshair;fill:#fff;stroke:#2563eb;stroke-width:.55'})));
}
'''
s=s[:start]+handles+s[end:]

# Remove manual text state from the live leader pointer pipeline.
repls=[
("   const tp=kbLeaderTextPointV17(g);\n   selected=g;lastEditable=g;\n   leaderDrag={obj:g,kind,start:p,p1:parsePt(g.dataset.p1),p2:parsePt(g.dataset.p2),shelf:+g.dataset.shelf||40,textX:tp.x,textY:tp.y};",
 "   selected=g;lastEditable=g;\n   leaderDrag={obj:g,kind,start:p,p1:parsePt(g.dataset.p1),p2:parsePt(g.dataset.p2),shelf:+g.dataset.shelf||40};"),
("   const tp=kbLeaderTextPointV17(obj);\n   selected=obj;lastEditable=obj;drawSelection();\n   leaderDrag={obj,start:p,kind:'move',p1:parsePt(obj.dataset.p1),p2:parsePt(obj.dataset.p2),textX:tp.x,textY:tp.y};",
 "   selected=obj;lastEditable=obj;drawSelection();\n   leaderDrag={obj,start:p,kind:'move',p1:parsePt(obj.dataset.p1),p2:parsePt(obj.dataset.p2)};"),
("   g.dataset.p1=`${d.p1.x+dx},${d.p1.y+dy}`;g.dataset.p2=`${d.p2.x+dx},${d.p2.y+dy}`;\n   g.dataset.textX=String(d.textX+dx);g.dataset.textY=String(d.textY+dy);",
 "   g.dataset.p1=`${d.p1.x+dx},${d.p1.y+dy}`;g.dataset.p2=`${d.p2.x+dx},${d.p2.y+dy}`;"),
("   const dx=p.x-d.p2.x,dy=p.y-d.p2.y;\n   g.dataset.p2=`${p.x},${p.y}`;\n   g.dataset.textX=String(d.textX+dx);g.dataset.textY=String(d.textY+dy);",
 "   g.dataset.p2=`${p.x},${p.y}`;"),
(" }else if(d.kind==='text'){\n   g.dataset.textX=String(p.x);g.dataset.textY=String(p.y);\n }\n renderLeader(g);drawSelection();",
 " }\n renderLeader(g);drawSelection();")
]
for old,new in repls:
    if old not in s:
        raise SystemExit('v18: leader pipeline fragment not found: '+old[:90])
    s=s.replace(old,new,1)

# --- 2. Context layer menu must always disappear after an action. ---
old="function closeImageMenu(){$('imageContextMenu').classList.remove('open');$('imageContextMenu').setAttribute('aria-hidden','true')}"
new="function closeImageMenu(){const m=$('imageContextMenu');m.classList.remove('open');m.setAttribute('aria-hidden','true');m.style.pointerEvents='none';m.style.display='none'}"
if old not in s:
    raise SystemExit('v18: closeImageMenu not found')
s=s.replace(old,new,1)

# Every way of opening the menu clears the hard-close inline styles.
s=s.replace("const m=$('imageContextMenu');m.classList.add('open');m.setAttribute('aria-hidden','false');",
            "const m=$('imageContextMenu');m.style.display='';m.style.pointerEvents='auto';m.classList.add('open');m.setAttribute('aria-hidden','false');")

# Belt-and-suspenders: after a layer button click, close it again on the next tick.
# This prevents any older bubbling handler from leaving/reopening the menu.
anchor='// ---------- Native KB911 project format ----------'
pos=s.find(anchor)
if pos<0:
    raise SystemExit('v18: project anchor not found')
cleanup=r'''
// KB911_V18_LEADER_TEXT_LOCK_AND_MENU_CLOSE
$('imageContextMenu').addEventListener('click',e=>{
 if(!e.target.closest('button[data-layer]'))return;
 setTimeout(()=>{closeImageMenu()},0);
},false);

'''
s=s[:pos]+cleanup+s[pos:]

# Final guards for the behavior we actually want.
if "data-leader-handle':'text'" in s or "data-leader-handle\":\"text" in s:
    raise SystemExit('v18: independent leader text handle still present')
if "d.kind==='text'" in s:
    raise SystemExit('v18: independent leader text drag still present')
if marker not in s:
    raise SystemExit('v18 marker missing')

p.write_text(s,encoding='utf-8',newline='')
print('v18: leader text locked to shelf; layer menu hard-close applied')
