from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='// KB911_V24_LINE_COPY_PASTE'
if marker in s:
    print('v24 already applied')
    raise SystemExit(0)

anchor='// ---------- Native KB911 project format ----------'
pos=s.find(anchor)
if pos<0: raise SystemExit('v24: native project anchor not found')

code=r'''
// KB911_V24_LINE_COPY_PASTE
let kbLineClipboardV24=null,kbLinePasteV24=null;
function kbCloneLineV24(data){
 const g=el('g',{'data-type':'line','data-id':uid++,'data-p1':data.p1,'data-p2':data.p2,'data-p3':data.p3,'data-line-width':data.lineWidth||'0.40','data-line-color':data.lineColor||'#111111','data-line-style':data.lineStyle||'solid'});
 for(const [k,v] of Object.entries(data||{})){
  if(!['type','id','p1','p2','p3','lineWidth','lineColor','lineStyle'].includes(k))g.dataset[k]=v;
 }
 return g;
}
function kbMoveLineDataToV24(data,p){
 const p1=parsePt(data.p1),p2=parsePt(data.p2),p3=parsePt(data.p3);
 const cx=(p1.x+p2.x+p3.x)/3,cy=(p1.y+p2.y+p3.y)/3,dx=p.x-cx,dy=p.y-cy;
 return {...data,p1:`${p1.x+dx},${p1.y+dy}`,p2:`${p2.x+dx},${p2.y+dy}`,p3:`${p3.x+dx},${p3.y+dy}`};
}
function kbCancelLinePasteV24(){
 if(kbLinePasteV24?.ghost)kbLinePasteV24.ghost.remove();
 kbLinePasteV24=null;paper.style.cursor='';
}
function kbUpdateLinePasteV24(p){
 if(!kbLinePasteV24)return;
 const moved=kbMoveLineDataToV24(kbLinePasteV24.base,p);kbLinePasteV24.data=moved;
 if(!kbLinePasteV24.ghost){
  const g=kbCloneLineV24(moved);g.style.opacity='.45';g.style.pointerEvents='none';paper.appendChild(g);kbLinePasteV24.ghost=g;
 }else{
  kbLinePasteV24.ghost.dataset.p1=moved.p1;kbLinePasteV24.ghost.dataset.p2=moved.p2;kbLinePasteV24.ghost.dataset.p3=moved.p3;
 }
 renderSimpleLine(kbLinePasteV24.ghost);
}
function kbStartLinePasteV24(){
 if(!kbLineClipboardV24)return;
 kbCancelLinePasteV24();
 kbLinePasteV24={base:{...kbLineClipboardV24},data:null,ghost:null};paper.style.cursor='copy';
 kbUpdateLinePasteV24({x:page.w/2,y:page.h/2});setStatus('Линия в режиме вставки — переместите мышь и щёлкните в нужном месте');
}
function kbPlaceLinePasteV24(){
 if(!kbLinePasteV24?.data)return;
 const g=kbCloneLineV24(kbLinePasteV24.data);appendContent(g);renderSimpleLine(g);selected=g;lastEditable=g;kbCancelLinePasteV24();drawSelection();setStatus('Линия вставлена');
}

document.addEventListener('keydown',e=>{
 const ctrl=e.ctrlKey||e.metaKey;
 if(ctrl&&(e.code==='KeyC'||String(e.key).toLowerCase()==='c'||e.key==='с'||e.key==='С')&&selected?.dataset.type==='line'){
  e.preventDefault();e.stopImmediatePropagation();kbCancelLinePasteV24();kbLineClipboardV24={...selected.dataset};setStatus('Линия скопирована. Ctrl+V — вставить');return;
 }
 if(ctrl&&(e.code==='KeyV'||String(e.key).toLowerCase()==='v'||e.key==='м'||e.key==='М')&&kbLineClipboardV24){
  e.preventDefault();e.stopImmediatePropagation();closeSimpleLinePopup();clearUI();kbStartLinePasteV24();return;
 }
 if(e.key==='Escape'&&kbLinePasteV24){e.preventDefault();e.stopImmediatePropagation();kbCancelLinePasteV24();setStatus('Вставка линии отменена')}
},true);
paper.addEventListener('pointermove',e=>{if(!kbLinePasteV24)return;kbUpdateLinePasteV24(pt(e));e.preventDefault();e.stopImmediatePropagation()},true);
paper.addEventListener('pointerdown',e=>{if(!kbLinePasteV24)return;e.preventDefault();e.stopImmediatePropagation();kbUpdateLinePasteV24(pt(e));kbPlaceLinePasteV24()},true);

'''
s=s[:pos]+code+s[pos:]

for token in [marker,'kbLineClipboardV24','kbStartLinePasteV24','kbPlaceLinePasteV24',"selected?.dataset.type==='line'"]:
    if token not in s: raise SystemExit('v24 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v24: line Ctrl+C/Ctrl+V added')
