from pathlib import Path
import re, sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/KB911.html')
s=p.read_text(encoding='utf-8')

def must_replace(old,new,count=1):
    global s
    if old not in s:
        raise SystemExit('KB911 patch: expected fragment not found: '+old[:120])
    s=s.replace(old,new,count)

def must_sub(pattern,repl,count=1):
    global s
    s2,n=re.subn(pattern,repl,s,count=count,flags=re.S)
    if n!=count:
        raise SystemExit(f'KB911 patch: regex matched {n}, expected {count}: {pattern[:100]}')
    s=s2

# Dimension rotate controls and donation menu styling.
must_replace(
".dim-hover-line{stroke:#2563eb;stroke-width:.28;fill:none;opacity:.8;pointer-events:none;vector-effect:non-scaling-stroke}\n",
".dim-hover-line{stroke:#2563eb;stroke-width:.28;fill:none;opacity:.8;pointer-events:none;vector-effect:non-scaling-stroke}.dim-rotate-handle{fill:#fff;stroke:#2563eb;stroke-width:.30;cursor:grab;vector-effect:non-scaling-stroke}.dim-rotate-stem{stroke:#2563eb;stroke-width:.28;vector-effect:non-scaling-stroke}\n")
must_replace("@media print{", "aside.right button{height:29px}#donateWrap{position:relative;margin-top:10px}#donateBtn{width:100%;font-weight:600;display:flex;align-items:center;justify-content:center;gap:5px}#donateBtn img{width:24px;height:24px;object-fit:contain}#donateMenu{display:none;position:fixed;z-index:75;background:#fff;border:1px solid #c8c8ce;border-radius:7px;box-shadow:0 10px 28px rgba(0,0,0,.18);padding:10px;font-size:12px;line-height:1.35;white-space:normal}#donateMenu.open{display:block}#donateQrArea{display:none;text-align:center;margin-top:8px}#donateMenu.open~#donateQrArea{display:block}#donateQrImage{display:block;width:min(100%,210px);height:auto;aspect-ratio:1;margin:auto;image-rendering:auto}\n@media print{")

# Donation placeholder under the logo controls.
must_replace(
'    <input id="frameLogoFile" type="file" accept="image/*" hidden>\n    <div class="hint">',
'    <input id="frameLogoFile" type="file" accept="image/*" hidden>\n    <div id="donateWrap"><button id="donateBtn">♥ Попрошайка ▾</button><div id="donateMenu"><button type="button">Варианты поддержки добавим позже</button></div></div>\n    <div class="hint">')

# State for hover-only manipulation and dimension rotation.
must_replace('hoverDim=null,lastEditable=null','hoverDim=null,hoverText=null,lastEditable=null')
must_replace('tailDrag=null,rotateDrag=null,popupDrag=null','tailDrag=null,rotateDrag=null,dimRotateDrag=null,popupDrag=null')

# Handle drawing: lower dimension endpoint circles are half the upper circles; both text and dimensions expose move/rotate handles on hover.
must_sub(r"function drawDimHandles\(g,hoverOnly=false\)\{.*?\nfunction drawTextHandles", r'''function drawDimHandles(g,hoverOnly=false){if(!g||g.dataset.type!=='dimension')return;const{p1,p2,nx,ny,ts}=dimGeom(g);[[p1,'start'],[p2,'end']].forEach(([p,k])=>{const lower={x:p.x-nx*ts/2,y:p.y-ny*ts/2},upper={x:p.x+nx*ts/2,y:p.y+ny*ts/2};paper.appendChild(el('line',{x1:lower.x,y1:lower.y,x2:upper.x,y2:upper.y,class:'dim-hover-line selection-ui'}));paper.appendChild(el('circle',{cx:lower.x,cy:lower.y,r:hoverOnly?.25:.29,class:`dim-end-handle dim-handle-${k} selection-ui`,'data-owner':g.dataset.id}));paper.appendChild(el('circle',{cx:upper.x,cy:upper.y,r:hoverOnly?.50:.58,class:`dim-tail-handle dim-tail-${k} selection-ui`,'data-owner':g.dataset.id}))});const mid={x:(p1.x+p2.x)/2,y:(p1.y+p2.y)/2},rh=ts/2+6,rx=mid.x+nx*rh,ry=mid.y+ny*rh;paper.appendChild(el('line',{x1:mid.x,y1:mid.y,x2:rx,y2:ry,class:'dim-rotate-stem selection-ui'}));paper.appendChild(el('circle',{cx:rx,cy:ry,r:hoverOnly?.75:.9,class:'dim-rotate-handle selection-ui','data-owner':g.dataset.id}))}
function drawTextHandles''')
must_sub(r"function drawTextHandles\(g\)\{.*?\nfunction drawSelection", r'''function drawTextHandles(g){const x=+g.dataset.x,y=+g.dataset.y,w=+g.dataset.w,h=+g.dataset.h,a=+g.dataset.angle||0,cx=x+w/2,cy=y+h/2;const grp=el('g',{class:'selection-ui',transform:`rotate(${a} ${cx} ${cy})`});grp.appendChild(el('rect',{x,y,width:w,height:h,rx:2.5,ry:2.5,class:'text-selection'}));grp.appendChild(el('rect',{x:x+w-1.7,y:y+h-1.7,width:3.4,height:3.4,rx:.7,ry:.7,class:'resize-handle','data-owner':g.dataset.id}));grp.appendChild(el('line',{x1:cx,y1:y,x2:cx,y2:y-8,class:'rotate-stem'}));grp.appendChild(el('circle',{cx,cy:y-8,r:1.5,class:'rotate-handle','data-owner':g.dataset.id}));paper.appendChild(grp)}
function drawSelection''')
must_sub(r"function drawSelection\(\)\{.*?\nfunction showProps", r'''function drawSelection(){clearUI();if(!selected){if(hoverDim){drawDimHandles(hoverDim,true);return}if(hoverText){drawTextHandles(hoverText);return}return}if(selected.dataset.type==='dimension'){drawDimHandles(selected,false);return}if(selected.dataset.type==='text'){drawTextHandles(selected);return}if(selected.dataset.type==='image'){drawImageHandles(selected);return}}
function showProps''')
must_sub(r"function showProps\(\)\{.*?\nfunction appendContent", r'''function showProps(){const t=selected?.dataset.type;$('noSelection').hidden=!!t;$('imageProps').hidden=t!=='image';if(t!=='dimension')closeDimPopup();if(t!=='text')closeTextPopup();if(t==='image'){const r=imageRect(selected);$('imageOpacity').value=selected.getAttribute('opacity')||1;$('imageW').value=r.w.toFixed(1);$('imageH').value=r.h.toFixed(1)}}
function appendContent''')

# Creation still opens properties; finished objects only open properties on double click.
must_sub(r"function createDim\(p1,p2\)\{.*?\nfunction drawArrow", r'''function createDim(p1,p2){const d=dimDefaults,g=el('g',{'data-type':'dimension','data-id':uid++,'data-p1':`${p1.x},${p1.y}`,'data-p2':`${p2.x},${p2.y}`,'data-value':'','data-prefix':d.prefix,'data-suffix':d.suffix,'data-arrow':d.arrow,'data-arrow-size':d.arrowSize,'data-arrow-angle':d.arrowAngle,'data-tail-size':d.tailSize,'data-line-width':d.lineWidth,'data-line-color':d.lineColor,'data-font':d.font,'data-font-size':d.fontSize,'data-text-color':d.textColor,'data-bold':d.bold?'1':'0','data-italic':d.italic?'1':'0'});appendContent(g);renderDim(g);select(g);setTool('dimension-edit',true);syncDimProps();openDimPopup();setTimeout(()=>{$('dimText').focus();$('dimText').select()},0)}
function drawArrow''')
must_sub(r"function createTextBox\(x,y,w,h\)\{.*?\nfunction renderText", r'''function createTextBox(x,y,w,h){const d=builtText,g=el('g',{'data-type':'text','data-id':uid++,'data-x':x,'data-y':y,'data-w':Math.max(12,w),'data-h':Math.max(8,h),'data-font':d.font,'data-font-size':d.fontSize,'data-text-color':d.textColor,'data-bg':d.bg,'data-bg-opacity':d.bgOpacity,'data-bold':d.bold?'1':'0','data-angle':d.angle||'0','data-align':d.align||'center','data-value':''});appendContent(g);renderText(g);select(g);setTool('text-edit',true);syncTextProps();openTextPopup();setStatus('Введите текст. Для фиксации нажмите OK, Esc или Ctrl+Enter');setTimeout(()=>editText(g),0)}
function renderText''')
s=s.replace('Надпись активна. При необходимости подправьте параметры и нажмите OK','Надпись активна. Двойной клик — свойства; наведение — перенос и поворот')

# Pointer rules. Add owner-aware text manipulation and dimension rotation without opening property windows.
must_replace(
" if(e.target.classList?.contains('rotate-handle')&&selected?.dataset.type==='text'){const g=selected,x=+g.dataset.x,y=+g.dataset.y,w=+g.dataset.w,h=+g.dataset.h;rotateDrag={obj:g,cx:x+w/2,cy:y+h/2,startAngle:+g.dataset.angle||0,startPointer:Math.atan2(p.y-(y+h/2),p.x-(x+w/2))*180/Math.PI};e.preventDefault();return}\n if(e.target.classList?.contains('resize-handle')&&selected?.dataset.type==='text'){textResize={obj:selected,start:p,w:+selected.dataset.w,h:+selected.dataset.h};e.preventDefault();return}",
" if(e.target.classList?.contains('rotate-handle')){const g=(selected?.dataset.type==='text'?selected:findOwner(e.target.dataset.owner,'text'));if(g){if(selected!==g){selected=g;showProps();drawSelection()}const x=+g.dataset.x,y=+g.dataset.y,w=+g.dataset.w,h=+g.dataset.h;rotateDrag={obj:g,cx:x+w/2,cy:y+h/2,startAngle:+g.dataset.angle||0,startPointer:Math.atan2(p.y-(y+h/2),p.x-(x+w/2))*180/Math.PI};e.preventDefault();return}}\n if(e.target.classList?.contains('dim-rotate-handle')){const g=(selected?.dataset.type==='dimension'?selected:findOwner(e.target.dataset.owner,'dimension'));if(g){if(selected!==g){selected=g;showProps();drawSelection()}const p1=parsePt(g.dataset.p1),p2=parsePt(g.dataset.p2),cx=(p1.x+p2.x)/2,cy=(p1.y+p2.y)/2;dimRotateDrag={obj:g,cx,cy,p1,p2,startPointer:Math.atan2(p.y-cy,p.x-cx)};e.preventDefault();return}}\n if(e.target.classList?.contains('resize-handle')){const g=(selected?.dataset.type==='text'?selected:findOwner(e.target.dataset.owner,'text'));if(g){if(selected!==g){selected=g;showProps();drawSelection()}textResize={obj:g,start:p,w:+g.dataset.w,h:+g.dataset.h};e.preventDefault();return}}")
must_replace("if(obj?.dataset.type==='dimension'&&obj!==selected)select(obj);\n if(obj?.dataset.type==='text'&&obj!==selected){selected=obj;showProps();drawSelection()}", "if(obj?.dataset.type==='dimension'&&obj!==selected){selected=obj;showProps();drawSelection()}\n if(obj?.dataset.type==='text'&&obj!==selected){selected=obj;showProps();drawSelection()}")
# Clicking the dimension text is a move operation now; editing is double-click only.
s=s.replace(" if(e.target.classList?.contains('dim-label')&&obj.dataset.type==='dimension'){setTimeout(()=>{$('dimText').focus();$('dimText').select()},0);return}\n","")

must_sub(r"paper\.addEventListener\('dblclick',e=>\{.*?\}\);", "paper.addEventListener('dblclick',e=>{const obj=groupType(e.target);if(!obj)return;e.preventDefault();if(obj.dataset.type==='text'){select(obj);setTool('text-edit',true);syncTextProps();openTextPopup();setStatus('Редактирование надписи')}else if(obj.dataset.type==='dimension'){select(obj);setTool('dimension-edit',true);syncDimProps();openDimPopup()}else if(obj.dataset.type==='image'){drag=null;imageResize=null;activeImage=obj;select(obj);tool='image-edit';setStatus('Режим картинки включён двойным кликом: теперь её можно перемещать или менять размер. Esc — зафиксировать')}});")

must_sub(r"if\(!dimDraft&&!textDraft&&!drag&&!textResize&&!imageResize&&!endpointDrag&&!tailDrag&&!rotateDrag&&tool!=='dimension'&&tool!=='text'\)\{.*?\}\n if\(dimDraft", "if(!dimDraft&&!textDraft&&!drag&&!textResize&&!imageResize&&!endpointDrag&&!tailDrag&&!rotateDrag&&!dimRotateDrag&&tool!=='dimension'&&tool!=='text'){const hd=groupType(e.target),nd=hd?.dataset.type==='dimension'?hd:null,nt=hd?.dataset.type==='text'?hd:null;if(nd!==hoverDim||nt!==hoverText){hoverDim=nd;hoverText=nt;if(nd||nt)lastEditable=nd||nt;if(!selected)drawSelection()}}\n if(dimDraft")

must_replace(" if(rotateDrag){", " if(dimRotateDrag){const d=dimRotateDrag,a=Math.atan2(p.y-d.cy,p.x-d.cx)-d.startPointer,ca=Math.cos(a),sa=Math.sin(a),rot=q=>({x:d.cx+(q.x-d.cx)*ca-(q.y-d.cy)*sa,y:d.cy+(q.x-d.cx)*sa+(q.y-d.cy)*ca});const q1=rot(d.p1),q2=rot(d.p2);d.obj.dataset.p1=`${q1.x},${q1.y}`;d.obj.dataset.p2=`${q2.x},${q2.y}`;renderDim(d.obj);drawSelection();return}\n if(rotateDrag){",1)
# pointer-up cleanup can be minified in different forms; cover both common forms.
s=s.replace('rotateDrag=null;drag=null','rotateDrag=null;dimRotateDrag=null;drag=null')
s=s.replace('rotateDrag=null;textResize=null','rotateDrag=null;dimRotateDrag=null;textResize=null')

# Donation dropdown behavior.
must_replace("$('frameEnabled').onchange=", "function kbPlaceDonateMenu(){const btn=$('donateBtn'),menu=$('donateMenu');if(!menu.classList.contains('open'))return;const r=btn.getBoundingClientRect();menu.style.left=r.left+'px';menu.style.width=r.width+'px';menu.style.top=Math.max(6,r.top-menu.offsetHeight-6)+'px'}\nfunction kbCloseDonateMenu(){const m=$('donateMenu');m.classList.remove('open');$('donateBtn').setAttribute('aria-expanded','false')}\n$('donateBtn').onclick=e=>{e.stopPropagation();const m=$('donateMenu'),open=!m.classList.contains('open');m.classList.toggle('open',open);$('donateBtn').setAttribute('aria-expanded',String(open));if(open)kbPlaceDonateMenu()};$('donateMenu').addEventListener('click',e=>e.stopPropagation());window.addEventListener('click',e=>{if(!e.target.closest('#donateWrap'))kbCloseDonateMenu()});window.addEventListener('scroll',kbPlaceDonateMenu,true);window.addEventListener('resize',kbPlaceDonateMenu);\n$('frameEnabled').onchange=")


p.write_text(s,encoding='utf-8',newline='')
print('KB911 UI patch applied:',len(s.encode('utf-8')),'bytes')
