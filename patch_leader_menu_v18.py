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
 delete g.dataset.textX;delete g.dataset.textY;
 return {x:(p2.x+p3.x)/2,y:p2.y-fs*.85};
}
'''
s=s[:start]+auto+s[end:]

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

# --- 2. Layer menu hard-close. ---
open_pat="const m=$('imageContextMenu');m.classList.add('open');m.setAttribute('aria-hidden','false');"
open_rep="const m=$('imageContextMenu');m.style.display='';m.style.pointerEvents='auto';m.classList.add('open');m.setAttribute('aria-hidden','false');"
count=s.count(open_pat)
if count<1:
    raise SystemExit('v18: imageContextMenu open path not found')
s=s.replace(open_pat,open_rep)

anchor='// ---------- Native KB911 project format ----------'
pos=s.find(anchor)
if pos<0:
    raise SystemExit('v18: project anchor not found')
cleanup=r'''
// KB911_V18_LEADER_TEXT_LOCK_AND_MENU_CLOSE
$('imageContextMenu').addEventListener('click',e=>{
 if(!e.target.closest('button[data-layer]'))return;
 setTimeout(()=>{
   const m=$('imageContextMenu');
   m.classList.remove('open');
   m.setAttribute('aria-hidden','true');
   m.style.pointerEvents='none';
   m.style.display='none';
 },0);
},false);

'''
s=s[:pos]+cleanup+s[pos:]

if "data-leader-handle':'text'" in s or 'data-leader-handle="text"' in s:
    raise SystemExit('v18: independent leader text handle still present')
if marker not in s:
    raise SystemExit('v18 marker missing')
if "m.style.display='none'" not in s:
    raise SystemExit('v18: hard menu close missing')

p.write_text(s,encoding='utf-8',newline='')
print('v18: leader text locked to shelf; layer menu hard-close applied')
