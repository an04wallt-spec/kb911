from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='// KB911_V25_LINE_MIDPOINT_DELETE_AND_HANDLE_SIZE'
if marker in s:
    print('v25 already applied')
    raise SystemExit(0)

# Match leader handles to the large dimension endpoint handle (r=.72).
s=s.replace("r:1.55,class:'handle selection-ui leader-handle'","r:.72,class:'handle selection-ui leader-handle'")
if "r:1.55,class:'handle selection-ui leader-handle'" in s:
    raise SystemExit('v25: leader handle radius replacement incomplete')

# Match line handles to the same large dimension endpoint handle size.
s=s.replace("r:1.55,class:'handle selection-ui simple-line-handle'","r:.72,class:'handle selection-ui simple-line-handle'")
if "r:1.55,class:'handle selection-ui simple-line-handle'" in s:
    raise SystemExit('v25: line handle radius replacement incomplete')

# Track which line point was explicitly clicked. Only the middle point can be deleted.
anchor="let simpleLineDraft=null,simpleLinePreview=null,simpleLineDrag=null,simpleLinePopupDrag=null;"
if anchor not in s: raise SystemExit('v25: line state anchor not found')
s=s.replace(anchor,anchor+"\nlet simpleLineSelectedHandle=null;",1)

old="selected=g;lastEditable=g;simpleLineDrag={obj:g,kind:h.dataset.lineHandle,start:p,p1:pts.p1,p2:pts.p2,p3:pts.p3};"
new="selected=g;lastEditable=g;simpleLineSelectedHandle=(h.dataset.lineHandle==='p2'?'p2':null);simpleLineDrag={obj:g,kind:h.dataset.lineHandle,start:p,p1:pts.p1,p2:pts.p2,p3:pts.p3};"
if old not in s: raise SystemExit('v25: line handle pointer block not found')
s=s.replace(old,new,1)

old="selected=obj;lastEditable=obj;drawSelection();simpleLineDrag={obj,start:p,kind:'move',p1:pts.p1,p2:pts.p2,p3:pts.p3};"
new="selected=obj;lastEditable=obj;simpleLineSelectedHandle=null;drawSelection();simpleLineDrag={obj,start:p,kind:'move',p1:pts.p1,p2:pts.p2,p3:pts.p3};"
if old not in s: raise SystemExit('v25: line object pointer block not found')
s=s.replace(old,new,1)

# Straight mode: retain p2 in data for backwards compatibility/copy-paste, but render and expose only endpoints.
old="const {p1,p2,p3}=simpleLinePts(g),c=g.dataset.lineColor||'#111111',lw=Math.max(.1,+g.dataset.lineWidth||.4),dash=simpleLineDash(g.dataset.lineStyle||'solid');\n const attrs={d:`M ${p1.x} ${p1.y} L ${p2.x} ${p2.y} L ${p3.x} ${p3.y}`,fill:'none',stroke:c,'stroke-width':lw,'stroke-linecap':'butt','stroke-linejoin':'miter','vector-effect':'non-scaling-stroke'};"
new="const {p1,p2,p3}=simpleLinePts(g),c=g.dataset.lineColor||'#111111',lw=Math.max(.1,+g.dataset.lineWidth||.4),dash=simpleLineDash(g.dataset.lineStyle||'solid'),straight=g.dataset.straight==='1';\n const attrs={d:straight?`M ${p1.x} ${p1.y} L ${p3.x} ${p3.y}`:`M ${p1.x} ${p1.y} L ${p2.x} ${p2.y} L ${p3.x} ${p3.y}`,fill:'none',stroke:c,'stroke-width':lw,'stroke-linecap':'butt','stroke-linejoin':'miter','vector-effect':'non-scaling-stroke'};"
if old not in s: raise SystemExit('v25: renderSimpleLine geometry block not found')
s=s.replace(old,new,1)

old="const {p1,p2,p3}=simpleLinePts(g);\n [[p1,'p1'],[p2,'p2'],[p3,'p3']].forEach(([q,k])=>paper.appendChild(el('circle',{cx:q.x,cy:q.y,r:.72,class:'handle selection-ui simple-line-handle','data-owner':g.dataset.id,'data-line-handle':k,style:'cursor:crosshair;fill:#fff;stroke:#2563eb;stroke-width:.55'})));"
new="const {p1,p2,p3}=simpleLinePts(g),pts=g.dataset.straight==='1'?[[p1,'p1'],[p3,'p3']]:[[p1,'p1'],[p2,'p2'],[p3,'p3']];\n pts.forEach(([q,k])=>paper.appendChild(el('circle',{cx:q.x,cy:q.y,r:.72,class:'handle selection-ui simple-line-handle','data-owner':g.dataset.id,'data-line-handle':k,style:'cursor:crosshair;fill:#fff;stroke:#2563eb;stroke-width:.55'})));"
if old not in s: raise SystemExit('v25: drawSimpleLineHandles block not found')
s=s.replace(old,new,1)

# Prevent the older generic Delete handler from deleting the whole line when p2 is the active point.
old="if((e.key==='Delete'||e.key==='Backspace')&&selected&&!inField){if(selected===lastEditable)lastEditable=null;selected.remove();clearSelection()}"
new="if((e.key==='Delete'||e.key==='Backspace')&&selected&&!inField&&!(selected?.dataset.type==='line'&&simpleLineSelectedHandle==='p2')){if(selected===lastEditable)lastEditable=null;selected.remove();clearSelection()}"
if old not in s: raise SystemExit('v25: generic delete handler not found')
s=s.replace(old,new,1)

# Keep line paste centered visually for straight lines.
old="const cx=(p1.x+p2.x+p3.x)/3,cy=(p1.y+p2.y+p3.y)/3,dx=p.x-cx,dy=p.y-cy;"
new="const straight=data.straight==='1',cx=straight?(p1.x+p3.x)/2:(p1.x+p2.x+p3.x)/3,cy=straight?(p1.y+p3.y)/2:(p1.y+p2.y+p3.y)/3,dx=p.x-cx,dy=p.y-cy;"
if old in s:
    s=s.replace(old,new,1)

# Delete the selected middle point -> straight line between p1 and p3.
native='// ---------- Native KB911 project format ----------'
pos=s.find(native)
if pos<0: raise SystemExit('v25: native anchor not found')
code=r'''
// KB911_V25_LINE_MIDPOINT_DELETE_AND_HANDLE_SIZE
document.addEventListener('keydown',e=>{
 const inField=['INPUT','TEXTAREA','SELECT'].includes(document.activeElement?.tagName);
 if((e.key==='Delete'||e.key==='Backspace')&&!inField&&selected?.dataset.type==='line'&&simpleLineSelectedHandle==='p2'&&selected.dataset.straight!=='1'){
  e.preventDefault();e.stopImmediatePropagation();
  selected.dataset.straight='1';simpleLineSelectedHandle=null;
  renderSimpleLine(selected);drawSelection();
  setStatus('Центральная точка удалена — линия стала прямой');
 }
},true);

'''
s=s[:pos]+code+s[pos:]

checks=[marker,"r:.72,class:'handle selection-ui leader-handle'","r:.72,class:'handle selection-ui simple-line-handle'","selected.dataset.straight='1'","simpleLineSelectedHandle==='p2'","straight?`M ${p1.x} ${p1.y} L ${p3.x} ${p3.y}`"]
for token in checks:
    if token not in s: raise SystemExit('v25 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v25: leader/line handles match dimension endpoints; line midpoint Delete makes straight line')
