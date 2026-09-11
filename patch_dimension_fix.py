from pathlib import Path
import re
p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')

# Completely remove dimension rotation UI/styles and interaction.
s=re.sub(r'\.dim-rotate-handle\{.*?\}\.dim-rotate-stem\{.*?\}', '', s, flags=re.S)

# Correct visual handle sizes: the visually lower circles must be half the upper ones.
pat=r"function drawDimHandles\(g,hoverOnly=false\)\{.*?\nfunction drawTextHandles"
repl="""function drawDimHandles(g,hoverOnly=false){if(!g||g.dataset.type!=='dimension')return;const{p1,p2,nx,ny,ts}=dimGeom(g);[[p1,'start'],[p2,'end']].forEach(([p,k])=>{const lower={x:p.x-nx*ts/2,y:p.y-ny*ts/2},upper={x:p.x+nx*ts/2,y:p.y+ny*ts/2};paper.appendChild(el('line',{x1:lower.x,y1:lower.y,x2:upper.x,y2:upper.y,class:'dim-hover-line selection-ui'}));paper.appendChild(el('circle',{cx:lower.x,cy:lower.y,r:hoverOnly?.50:.58,class:`dim-end-handle dim-handle-${k} selection-ui`,'data-owner':g.dataset.id}));paper.appendChild(el('circle',{cx:upper.x,cy:upper.y,r:hoverOnly?.25:.29,class:`dim-tail-handle dim-tail-${k} selection-ui`,'data-owner':g.dataset.id}))})}\nfunction drawTextHandles"""
s,n=re.subn(pat,repl,s,count=1,flags=re.S)
if n!=1: raise SystemExit('dimension handle function not found')

# Remove dimension-rotation pointer-down block if present.
s=re.sub(r"\n if\(e\.target\.classList\?\.contains\('dim-rotate-handle'\)\)\{.*?return\}\}", '', s, count=1, flags=re.S)
# Remove dimension-rotation pointer-move block if present.
s=re.sub(r"\n if\(dimRotateDrag\)\{.*?return\}", '', s, count=1, flags=re.S)

p.write_text(s,encoding='utf-8',newline='')
print('Dimension rotation disabled; handle sizes corrected')
