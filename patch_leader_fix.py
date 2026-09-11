from pathlib import Path
p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')

def rep(a,b,n=1):
    global s
    if a not in s:
        raise SystemExit('patch_leader_fix missing fragment: '+a[:140])
    s=s.replace(a,b,n)

# A leader must start even when the arrow point is placed on top of an image/object.
rep("if(tool==='leader'&&!obj){e.preventDefault();e.stopImmediatePropagation();leaderDraft={p1:p,p2:p};leaderPreview=el('path',{d:`M ${p.x} ${p.y} L ${p.x} ${p.y}`,fill:'none',stroke:'#2563eb','stroke-width':'.5','stroke-dasharray':'2 1'});paper.appendChild(leaderPreview);return}",
    "if(tool==='leader'){e.preventDefault();e.stopImmediatePropagation();leaderDraft={p1:p,p2:p};leaderPreview=el('path',{d:`M ${p.x} ${p.y} L ${p.x} ${p.y}`,fill:'none',stroke:'#2563eb','stroke-width':'.5','stroke-dasharray':'2 1'});paper.appendChild(leaderPreview);paper.setPointerCapture?.(e.pointerId);return}")

# Export leaders exactly like other SVG line objects.
rep("else if(n.matches?.('g[data-type=\"dimension\"]'))drawDimensionObject(ctx,n);else if(n.matches?.('g[data-type=\"text\"]'))",
    "else if(n.matches?.('g[data-type=\"dimension\"]')||n.matches?.('g[data-type=\"leader\"]'))drawDimensionObject(ctx,n);else if(n.matches?.('g[data-type=\"text\"]'))")

# Close leader editor before export and clear unfinished leader on Escape.
rep("function commitEditorsForExport(){const ta=document.getElementById('liveTextEditor');if(ta)ta.blur();closeDimPopup();closeTextPopup();closeImageMenu();clearSelection()}",
    "function commitEditorsForExport(){const ta=document.getElementById('liveTextEditor');if(ta)ta.blur();closeDimPopup();closeTextPopup();closeLeaderPopup();closeImageMenu();clearSelection()}")
rep("dimDraft=null;textDraft=null;dimPreview?.remove();textPreview?.remove();dimPreview=textPreview=null;activeImage=null;clearSelection();setTool(null,true)",
    "dimDraft=null;textDraft=null;leaderDraft=null;dimPreview?.remove();textPreview?.remove();leaderPreview?.remove();dimPreview=textPreview=leaderPreview=null;leaderDrag=null;closeLeaderPopup();activeImage=null;clearSelection();setTool(null,true)")

# Keep the toolbar state clean after finishing a leader.
rep("$('leaderOk').onclick=()=>{closeLeaderPopup();clearSelection();setTool(null,true);setStatus('Сноска зафиксирована')}",
    "$('leaderOk').onclick=()=>{closeLeaderPopup();leaderDraft=null;leaderPreview?.remove();leaderPreview=null;leaderDrag=null;clearSelection();setTool(null,true);setStatus('Сноска зафиксирована')}")

p.write_text(s,encoding='utf-8',newline='')
print('Leader creation/export fix applied')
