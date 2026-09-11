from pathlib import Path
import re
p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')

def rep(a,b,n=1):
    global s
    if a not in s: raise SystemExit('patch_frame_params missing fragment: '+a[:120])
    s=s.replace(a,b,n)

# Replace static frame hint with editable numeric spans. Editing starts only on double click.
rep('<div class="hint">Контур 0,3 мм, отступ от края листа 5 мм. Название и логотип можно включать независимо.</div>',
    '<div class="hint">Контур <span id="frameStrokeEdit" class="frame-param" title="Двойной щелчок — изменить толщину рамки">0,3</span> мм, отступ от края листа <span id="frameInsetEdit" class="frame-param" title="Двойной щелчок — изменить отступ рамки">5</span> мм. Название и логотип можно включать независимо.</div>')

# Visual affordance without making them look like regular inputs.
rep('@media print{', '#framePanel .frame-param{font-weight:700;color:#2563eb;border-bottom:1px dotted #2563eb;cursor:text;padding:0 1px}#framePanel .frame-param.editing{background:#fff;border:1px solid #8bbcf3;border-radius:3px;outline:none;min-width:22px;display:inline-block;text-align:center}\n@media print{')

# Frame state gets persisted editable values.
rep("let activeImage=null,imageUndo=null,saveKind='png',frameState={enabled:false,company:true,logoEnabled:false,name:'',logo:null};",
    "let activeImage=null,imageUndo=null,saveKind='png',frameState={enabled:false,company:true,logoEnabled:false,name:'',logo:null,stroke:.3,inset:5};")

# Use the dynamic values in renderFrame.
rep("const g=el('g',{'data-type':'frame','pointer-events':'none'});const inset=5,sw=.3,rad=2;",
    "const g=el('g',{'data-type':'frame','pointer-events':'none'});const inset=Math.max(1,Math.min(40,+frameState.inset||5)),sw=Math.max(.05,Math.min(5,+frameState.stroke||.3)),rad=2;")

# Add inline double-click editor and persistence before frame event handlers.
anchor="$('frameEnabled').onchange="
code=r'''function fmtFrameParam(v){return String(v).replace('.',',')}\nfunction refreshFrameParamLabels(){if($('frameStrokeEdit'))$('frameStrokeEdit').textContent=fmtFrameParam(frameState.stroke);if($('frameInsetEdit'))$('frameInsetEdit').textContent=fmtFrameParam(frameState.inset)}\nfunction saveFrameParams(){saveStore('kb911.frameParams',{stroke:frameState.stroke,inset:frameState.inset})}\n(function(){const fp=readStore('kb911.frameParams');if(Number.isFinite(+fp.stroke))frameState.stroke=Math.max(.05,Math.min(5,+fp.stroke));if(Number.isFinite(+fp.inset))frameState.inset=Math.max(1,Math.min(40,+fp.inset));refreshFrameParamLabels()})();\nfunction beginFrameParamEdit(span,key,min,max,step){if(!span||span.classList.contains('editing'))return;span.classList.add('editing');span.contentEditable='true';span.textContent=String(frameState[key]).replace('.',',');span.focus();const sel=window.getSelection(),r=document.createRange();r.selectNodeContents(span);sel.removeAllRanges();sel.addRange(r);const finish=cancel=>{if(!span.classList.contains('editing'))return;let raw=span.textContent.trim().replace(',','.');let v=Number(raw);if(cancel||!Number.isFinite(v))v=frameState[key];v=Math.max(min,Math.min(max,Math.round(v/step)*step));frameState[key]=+v.toFixed(key==='stroke'?2:1);span.contentEditable='false';span.classList.remove('editing');refreshFrameParamLabels();saveFrameParams();renderFrame()};span.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();finish(false)}else if(e.key==='Escape'){e.preventDefault();finish(true)}};span.onblur=()=>finish(false)}\n$('frameStrokeEdit')?.addEventListener('dblclick',e=>{e.preventDefault();beginFrameParamEdit(e.currentTarget,'stroke',.05,5,.05)});\n$('frameInsetEdit')?.addEventListener('dblclick',e=>{e.preventDefault();beginFrameParamEdit(e.currentTarget,'inset',1,40,.5)});\n'''
if anchor not in s: raise SystemExit('frame handlers anchor not found')
s=s.replace(anchor,code+anchor,1)

p.write_text(s,encoding='utf-8',newline='')
print('Editable frame stroke/inset parameters applied')
