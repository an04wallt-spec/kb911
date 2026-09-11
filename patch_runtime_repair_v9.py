from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')

marker='// KB911_V9_RUNTIME_REPAIR'
if marker in s:
    print('runtime repair already applied')
    raise SystemExit(0)

# Leader UI can exist while the actual runtime functions are missing. Inject a
# complete self-contained leader runtime after all previous feature patches.
anchor="$('leaderText').oninput="
if anchor not in s:
    raise SystemExit('leader controls anchor not found')

leader_runtime=r'''
// KB911_V9_RUNTIME_REPAIR
function leaderPts(g){
 const p1=parsePt(g.dataset.p1||'0,0'),p2=parsePt(g.dataset.p2||'0,0');
 const dir=(+g.dataset.dir||1),shelf=Math.max(8,+g.dataset.shelf||40);
 return {p1,p2,p3:{x:p2.x+dir*shelf,y:p2.y},dir,shelf};
}
function renderLeader(g){
 while(g.firstChild)g.removeChild(g.firstChild);
 const {p1,p2,p3}=leaderPts(g),c=g.dataset.lineColor||dimDefaults.lineColor||'#111111',lw=+(g.dataset.lineWidth||dimDefaults.lineWidth||.4),as=+(g.dataset.arrowSize||dimDefaults.arrowSize||5),aa=+(g.dataset.arrowAngle||dimDefaults.arrowAngle||10),sty=g.dataset.arrow||dimDefaults.arrow||'slim';
 g.appendChild(el('line',{x1:p1.x,y1:p1.y,x2:p2.x,y2:p2.y,stroke:c,'stroke-width':lw,'vector-effect':'non-scaling-stroke'}));
 g.appendChild(el('line',{x1:p2.x,y1:p2.y,x2:p3.x,y2:p3.y,stroke:c,'stroke-width':lw,'vector-effect':'non-scaling-stroke'}));
 const len=Math.hypot(p2.x-p1.x,p2.y-p1.y)||1,ux=(p2.x-p1.x)/len,uy=(p2.y-p1.y)/len;
 drawArrow(g,p1,ux,uy,as,aa,c,lw,1,sty);
 const fs=+g.dataset.fontSize||4,t=el('text',{x:(p2.x+p3.x)/2,y:p2.y-fs*.85,'text-anchor':'middle','dominant-baseline':'central','font-family':g.dataset.font||'Bahnschrift','font-size':fs,'font-weight':g.dataset.bold==='1'?'700':'400','font-style':g.dataset.italic==='1'?'italic':'normal',fill:g.dataset.textColor||c});
 t.textContent=g.dataset.value||'Сноска';g.appendChild(t);
 g.appendChild(el('path',{d:`M ${p1.x} ${p1.y} L ${p2.x} ${p2.y} L ${p3.x} ${p3.y}`,fill:'none',stroke:'transparent','stroke-width':7,class:'leader-hit hover-movable'}));
}
function drawLeaderHandles(g){
 if(!g||g.dataset.type!=='leader')return;
 const {p1,p2,p3}=leaderPts(g);
 [[p1,'p1'],[p2,'p2'],[p3,'p3']].forEach(([p,k])=>paper.appendChild(el('circle',{cx:p.x,cy:p.y,r:.72,class:'handle selection-ui leader-handle','data-owner':g.dataset.id,'data-leader-handle':k})));
}
function createLeader(p1,p2){
 const d=dimDefaults,dir=p2.x>=p1.x?1:-1,g=el('g',{'data-type':'leader','data-id':uid++,'data-p1':`${p1.x},${p1.y}`,'data-p2':`${p2.x},${p2.y}`,'data-dir':String(dir),'data-shelf':'40','data-value':'Сноска','data-font':'Bahnschrift','data-font-size':d.fontSize||'4','data-bold':d.bold?'1':'0','data-italic':d.italic?'1':'0','data-arrow':d.arrow||'slim','data-arrow-size':d.arrowSize||'5','data-arrow-angle':d.arrowAngle||'10','data-line-width':d.lineWidth||'.4','data-line-color':d.lineColor||'#111111','data-text-color':d.textColor||'#111111'});
 appendContent(g);renderLeader(g);selected=g;lastEditable=g;drawSelection();openLeaderPopup(g);setStatus('Сноска создана. Двойной клик — редактирование');
}
function openLeaderPopup(g){
 if(!g||g.dataset.type!=='leader')return;
 selected=g;lastEditable=g;
 $('leaderText').value=g.dataset.value||'';$('leaderShelf').value=g.dataset.shelf||40;$('leaderFontSize').value=g.dataset.fontSize||4;$('leaderBold').checked=g.dataset.bold==='1';$('leaderItalic').checked=g.dataset.italic==='1';
 const q=$('leaderPopup');q.style.display='block';q.classList.add('open');q.setAttribute('aria-hidden','false');
 if(!q.style.left){q.style.left=Math.max(10,(innerWidth-320)/2)+'px';q.style.top=Math.max(60,(innerHeight-260)/2)+'px'}
}
function closeLeaderPopup(){const q=$('leaderPopup');if(!q)return;q.classList.remove('open');q.style.display='none';q.setAttribute('aria-hidden','true')}

paper.addEventListener('pointerdown',e=>{
 const p=pt(e),obj=groupType(e.target);
 if(tool==='leader'){
   e.preventDefault();e.stopImmediatePropagation();
   leaderDraft={p1:p,p2:p};
   leaderPreview=el('path',{d:`M ${p.x} ${p.y} L ${p.x} ${p.y}`,fill:'none',stroke:'#2563eb','stroke-width':'.5','stroke-dasharray':'2 1','pointer-events':'none'});paper.appendChild(leaderPreview);return;
 }
 if(e.target.classList?.contains('leader-handle')){
   const g=findOwner(e.target.dataset.owner,'leader');if(!g)return;
   selected=g;leaderDrag={obj:g,kind:e.target.dataset.leaderHandle,start:p,p1:parsePt(g.dataset.p1),p2:parsePt(g.dataset.p2),shelf:+g.dataset.shelf||40};e.preventDefault();e.stopImmediatePropagation();return;
 }
 if(obj?.dataset.type==='leader'){
   selected=obj;lastEditable=obj;drawSelection();leaderDrag={obj,start:p,kind:'move',p1:parsePt(obj.dataset.p1),p2:parsePt(obj.dataset.p2)};e.preventDefault();e.stopImmediatePropagation();
 }
},true);
paper.addEventListener('pointermove',e=>{
 const p=pt(e);
 if(leaderDraft&&tool==='leader'){
   leaderDraft.p2=p;const dir=p.x>=leaderDraft.p1.x?1:-1,p3x=p.x+dir*40;leaderPreview?.setAttribute('d',`M ${leaderDraft.p1.x} ${leaderDraft.p1.y} L ${p.x} ${p.y} L ${p3x} ${p.y}`);e.preventDefault();e.stopImmediatePropagation();return;
 }
 if(!leaderDrag)return;
 const d=leaderDrag,g=d.obj;
 if(d.kind==='move'){const dx=p.x-d.start.x,dy=p.y-d.start.y;g.dataset.p1=`${d.p1.x+dx},${d.p1.y+dy}`;g.dataset.p2=`${d.p2.x+dx},${d.p2.y+dy}`}
 else if(d.kind==='p1')g.dataset.p1=`${p.x},${p.y}`;
 else if(d.kind==='p2'){g.dataset.p2=`${p.x},${p.y}`;g.dataset.dir=p.x>=parsePt(g.dataset.p1).x?'1':'-1'}
 else if(d.kind==='p3'){const p2=parsePt(g.dataset.p2);g.dataset.shelf=String(Math.max(8,Math.abs(p.x-p2.x)));g.dataset.dir=p.x>=p2.x?'1':'-1'}
 renderLeader(g);drawSelection();e.preventDefault();e.stopImmediatePropagation();
},true);
window.addEventListener('pointerup',e=>{
 if(leaderDraft&&tool==='leader'){
   const p2=pt(e),p1=leaderDraft.p1;leaderDraft=null;leaderPreview?.remove();leaderPreview=null;
   if(Math.hypot(p2.x-p1.x,p2.y-p1.y)>2)createLeader(p1,p2);
 }
 leaderDrag=null;
},true);
paper.addEventListener('dblclick',e=>{const obj=groupType(e.target);if(obj?.dataset.type==='leader'){e.preventDefault();e.stopImmediatePropagation();openLeaderPopup(obj)}},true);
'''
s=s.replace(anchor,leader_runtime+'\n'+anchor,1)

# Do not try to infer startup scale from an unfinished layout. Re-run exactly the
# same page-change path that works when the user changes paper size manually.
startup=r'''
window.addEventListener('load',()=>{
 setTimeout(()=>{
   try{
     const ps=$('paperSize'),ori=$('orientation');
     if(ps&&ori){ps.value='A3';ori.value='landscape';ps.dispatchEvent(new Event('change',{bubbles:true}));}
     setTimeout(()=>{try{window.KB911_fitToViewport&&window.KB911_fitToViewport()}catch{}},260);
   }catch{}
 },650);
});
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('closing script tag missing')
s=s[:idx]+startup+s[idx:]

# Build-time checks: leader must be executable, not just present in the toolbar.
for token in ['function renderLeader(','function createLeader(','function drawLeaderHandles(','KB911_V9_RUNTIME_REPAIR']:
    assert token in s, 'missing leader runtime: '+token
assert "kind==='pdf'?[100,300,600]" in s, 'PDF DPI cap missing'

p.write_text(s,encoding='utf-8',newline='')
print('Runtime repair v9 applied: leader restored and startup A3 reinitialization added')
