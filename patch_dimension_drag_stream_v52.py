from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V52_DIMENSION_DRAG_STREAM'
if marker in s:
    print('v52 already applied')
    raise SystemExit(0)

# v51 correctly owns the dimension handles, but it redraws selection UI during
# pointerdown. The handle being pressed is itself selection UI, so removing it
# can terminate the WebView2 pointer stream before dragging starts. Capture the
# pointer on the stable paper element first and leave the pressed handle alive
# until the first pointermove.
old=""" selected=g;lastEditable=g;showProps();drawSelection();
 try{paper.setPointerCapture?.(e.pointerId)}catch{}
 e.preventDefault();e.stopImmediatePropagation();
},true);"""
new=""" // KB911_V52_DIMENSION_DRAG_STREAM
 selected=g;lastEditable=g;showProps();
 // Do NOT redraw selection here: h is a temporary SVG selection handle and
 // deleting it during pointerdown can cancel the drag in WebView2.
 try{paper.setPointerCapture?.(e.pointerId)}catch{}
 e.preventDefault();e.stopImmediatePropagation();
},true);"""
if s.count(old)!=1:
    raise SystemExit(f'v52: expected one v51 pointerdown tail, got {s.count(old)}')
s=s.replace(old,new,1)

# Release capture explicitly after the transaction. This is not required by the
# pointer spec, but keeps WebView2 state deterministic after repeated drags.
old_up=""" kbDimDirectDragV51=null;kbClearSnapMarkV40();
 renderDim(d.obj);selected=d.obj;lastEditable=d.obj;drawSelection();
 try{kbHistorySchedule(0)}catch{}"""
new_up=""" kbDimDirectDragV51=null;kbClearSnapMarkV40();
 try{if(paper.hasPointerCapture?.(e.pointerId))paper.releasePointerCapture(e.pointerId)}catch{}
 renderDim(d.obj);selected=d.obj;lastEditable=d.obj;drawSelection();
 try{kbHistorySchedule(0)}catch{}"""
if s.count(old_up)!=1:
    raise SystemExit(f'v52: expected one v51 pointerup block, got {s.count(old_up)}')
s=s.replace(old_up,new_up,1)

for token in [marker,'Do NOT redraw selection here','paper.setPointerCapture?.(e.pointerId)','paper.releasePointerCapture(e.pointerId)',"if(d.mode==='center')","else if(d.mode==='axis')"]:
    if token not in s:
        raise SystemExit('v52 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v52: pressed dimension handles stay alive through pointerdown; center and axis drags keep pointer stream')
