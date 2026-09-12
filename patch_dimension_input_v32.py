from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        raise SystemExit(f'v32 dimension input: expected {count}, got {n}: {old[:140]}')
    s = s.replace(old, new, count)

# Zero is a valid projection length.
rep('id="tailSize" class="dp-field" type="number" min="1" max="40" step="0.5" value="7"',
    'id="tailSize" class="dp-field" type="number" min="0" max="40" step="0.5" value="7"')
rep('ts=+g.dataset.tailSize||7;return{p1,p2,ux,uy,nx,ny,ts}',
    'ts=g.dataset.tailSize==null?7:+g.dataset.tailSize;return{p1,p2,ux,uy,nx,ny,ts}')
rep("$('tailSize').value=g.dataset.tailSize||7;", "$('tailSize').value=g.dataset.tailSize??7;")
rep("tailSize:g.dataset.tailSize||'7',", "tailSize:g.dataset.tailSize??'7',")
rep('down=+g.dataset.tailSize||7,up=+(g.dataset.upperTailSize??g.dataset.upperTailP1??g.dataset.upperTailP2??3),radius=',
    'down=g.dataset.tailSize==null?7:+g.dataset.tailSize,up=+(g.dataset.upperTailSize??g.dataset.upperTailP1??g.dataset.upperTailP2??3),radius=')
rep('aa=+g.dataset.arrowAngle||10,down=+g.dataset.tailSize||7,{nx:dnx,ny:dny}=dimDownNormal(g);',
    'aa=+g.dataset.arrowAngle||10,down=g.dataset.tailSize==null?7:+g.dataset.tailSize,{nx:dnx,ny:dny}=dimDownNormal(g);')

# First gesture: make the base line unmistakable over images.
rep("stroke:'#085cff','stroke-width':'.9','stroke-dasharray':'3 1.2'",
    "stroke:'#006cff','stroke-width':'1.35','stroke-dasharray':'4 1.35','stroke-linecap':'round'")

anchor = '// KB911_V31_STICKY_CREATION_TOOLS'
helper = r'''// KB911_V32_DIMENSION_INPUT_PREVIEW
function kbDimensionPreviewNodeV32(d){
 const z=dimDefaults,g=el('g',{
  'data-type':'dimension','data-id':'preview-v32',
  'data-p1':`${d.p1.x},${d.p1.y}`,'data-p2':`${d.p2.x},${d.p2.y}`,
  'data-value':'','data-prefix':z.prefix||'','data-suffix':z.suffix||'',
  'data-arrow':z.arrow||'slim','data-arrow-size':z.arrowSize||'5','data-arrow-angle':z.arrowAngle||'10',
  'data-tail-size':String(d.down??2),'data-upper-tail-size':String(d.up??2),
  'data-line-width':z.lineWidth||'0.40','data-line-color':'#111111',
  'data-font':z.font||'Bahnschrift','data-font-size':z.fontSize||'4','data-text-color':'#111111',
  'data-bold':z.bold?'1':'0','data-italic':z.italic?'1':'0'
 });
 g.classList.add('kb-dim-preview-v32');
 g.style.pointerEvents='none';
 return g;
}
function kbRefreshDimensionPreviewV32(d){
 if(!dimPreview||!dimPreview.classList?.contains('kb-dim-preview-v32'))return;
 dimPreview.dataset.tailSize=String(d.down??0);
 dimPreview.dataset.upperTailSize=String(d.up??0);
 renderDim(dimPreview);
 dimPreview.querySelectorAll('*').forEach(n=>n.setAttribute('pointer-events','none'));
}
function kbStartDimensionProjectionPreviewV32(d){
 dimPreview?.remove();
 dimPreview=kbDimensionPreviewNodeV32(d);
 appendContent(dimPreview);
 kbRefreshDimensionPreviewV32(d);
}
function kbDimensionProjectionLengthsV32(signed){
 const dead=1.35;
 if(Math.abs(signed)<=dead)return{down:0,up:0};
 const long=Math.max(2,Math.min(300,Math.abs(signed)));
 return signed<0?{down:long,up:2}:{down:2,up:long};
}

'''
rep(anchor, helper + anchor)

old_move = "if(dimDraft&&tool==='dimension'){if(dimDraft.stage==='line'){dimDraft.p2=p;dimPreview?.setAttribute('d',`M ${dimDraft.p1.x} ${dimDraft.p1.y} L ${p.x} ${p.y}`)}else{const d=dimDraft,{nx,ny}=dimDownNormal({dataset:{p1:`${d.p1.x},${d.p1.y}`,p2:`${d.p2.x},${d.p2.y}`}}),mid={x:(d.p1.x+d.p2.x)/2,y:(d.p1.y+d.p2.y)/2},signed=(p.x-mid.x)*nx+(p.y-mid.y)*ny;d.down=Math.max(2,Math.min(300,signed<0?-signed:2));d.up=Math.max(2,Math.min(300,signed>0?signed:2));const a=d.p1,b=d.p2,trace=q=>`M ${q.x-nx*d.up} ${q.y-ny*d.up} L ${q.x+nx*d.down} ${q.y+ny*d.down}`;dimPreview?.setAttribute('d',`M ${a.x} ${a.y} L ${b.x} ${b.y} ${trace(a)} ${trace(b)}`)}return}"
new_move = "if(dimDraft&&tool==='dimension'){if(dimDraft.stage==='line'){dimDraft.p2=p;dimPreview?.setAttribute('d',`M ${dimDraft.p1.x} ${dimDraft.p1.y} L ${p.x} ${p.y}`)}else{const d=dimDraft,{nx,ny}=dimDownNormal({dataset:{p1:`${d.p1.x},${d.p1.y}`,p2:`${d.p2.x},${d.p2.y}`}}),mid={x:(d.p1.x+d.p2.x)/2,y:(d.p1.y+d.p2.y)/2},signed=(p.x-mid.x)*nx+(p.y-mid.y)*ny,lens=kbDimensionProjectionLengthsV32(signed);d.down=lens.down;d.up=lens.up;kbRefreshDimensionPreviewV32(d)}return}"
rep(old_move, new_move)

old_up = "if(dimDraft?.stage==='line'&&tool==='dimension'){const p2=pt(e),p1=dimDraft.p1;if(Math.hypot(p2.x-p1.x,p2.y-p1.y)>2){dimDraft.p2=p2;dimDraft.stage='projection';dimDraft.up=2;dimDraft.down=2;setStatus('Размер: отведите указатель для выпуска линий, затем щёлкните для фиксации')}else{dimDraft=null;dimPreview?.remove();dimPreview=null}}"
new_up = "if(dimDraft?.stage==='line'&&tool==='dimension'){const p2=pt(e),p1=dimDraft.p1;if(Math.hypot(p2.x-p1.x,p2.y-p1.y)>2){dimDraft.p2=p2;dimDraft.stage='projection';dimDraft.up=2;dimDraft.down=2;kbStartDimensionProjectionPreviewV32(dimDraft);setStatus('Размер: выберите сторону и длину выпусков. На линии — выпуски 0. Щелчок — зафиксировать')}else{dimDraft=null;dimPreview?.remove();dimPreview=null}}"
rep(old_up, new_up)

# Existing dimensions use the same central zero dead-zone.
old_tail = "if(tailDrag){const g=tailDrag.obj,{p1,p2}=dimGeom(g),{nx,ny}=dimDownNormal(g),mid={x:(p1.x+p2.x)/2,y:(p1.y+p2.y)/2},d=(p.x-mid.x)*nx+(p.y-mid.y)*ny;g.dataset.tailSize=Math.max(2,Math.min(300,d<0?-d:2)).toFixed(2);g.dataset.upperTailSize=Math.max(2,Math.min(300,d>0?d:2)).toFixed(2);$('tailSize').value=(+g.dataset.tailSize).toFixed(1);renderDim(g);drawSelection();captureDimDefaults(g);return}"
new_tail = "if(tailDrag){const g=tailDrag.obj,{p1,p2}=dimGeom(g),{nx,ny}=dimDownNormal(g),mid={x:(p1.x+p2.x)/2,y:(p1.y+p2.y)/2},d=(p.x-mid.x)*nx+(p.y-mid.y)*ny,lens=kbDimensionProjectionLengthsV32(d);g.dataset.tailSize=String(lens.down);g.dataset.upperTailSize=String(lens.up);$('tailSize').value=(+g.dataset.tailSize).toFixed(1);renderDim(g);drawSelection();captureDimDefaults(g);return}"
rep(old_tail, new_tail)

# With both projections at zero there are no extension-line elements at all.
rep("function drawAsymTail(g,p,nx,ny,down,c,lw,up=3){const a=",
    "function drawAsymTail(g,p,nx,ny,down,c,lw,up=3){if(!(down>0||up>0))return;const a=")

for token in [
    'KB911_V32_DIMENSION_INPUT_PREVIEW',
    "stroke:'#006cff'",
    'kbStartDimensionProjectionPreviewV32(dimDraft)',
    'if(Math.abs(signed)<=dead)return{down:0,up:0}',
    'g.dataset.tailSize==null?7:+g.dataset.tailSize',
    'min="0" max="40"'
]:
    if token not in s:
        raise SystemExit('v32 dimension input guard failed: ' + token)

p.write_text(s, encoding='utf-8', newline='')
print('v32 dimension input preview and zero projections installed')
