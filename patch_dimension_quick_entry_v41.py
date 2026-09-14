from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')
marker = 'KB911_V41_QUICK_DIMENSION_VALUE'
if marker in s:
    print('v41 quick dimension entry already applied')
    raise SystemExit(0)

style = r'''<style id="kb911QuickDimensionV41">
/* KB911_V41_QUICK_DIMENSION_VALUE */
.kb-dim-anchor-v40{fill:#ffffff!important;fill-opacity:.34!important;stroke:#006cff!important;stroke-opacity:.82!important}
#kbQuickDimValueV41{position:fixed;z-index:10020;width:92px;height:31px;box-sizing:border-box;border:2px solid #1672e8;border-radius:7px;background:rgba(255,255,255,.92);box-shadow:0 5px 18px rgba(0,0,0,.18);font:600 15px Bahnschrift,Segoe UI,Arial,sans-serif;text-align:center;color:#171b21;outline:none;padding:3px 8px;transform:translate(-50%,-50%)}
#kbQuickDimValueV41::placeholder{color:#68717c;opacity:.9;letter-spacing:2px}
#kbQuickDimValueV41:focus{border-color:#005fcc;box-shadow:0 0 0 3px rgba(22,114,232,.16),0 5px 18px rgba(0,0,0,.18)}
</style>
'''
if s.count('</head>') != 1:
    raise SystemExit('v41 quick: expected one </head>')
s = s.replace('</head>', style + '</head>', 1)

anchor = '\nsetPage();\ninitKB911Project();\nkbHistoryStart();'
if s.count(anchor) != 1:
    raise SystemExit(f'v41 quick: startup anchor count {s.count(anchor)}')

code = r'''

// KB911_V41_QUICK_DIMENSION_VALUE
let kbQuickDimInputV41=null,kbQuickDimObjectV41=null;
function kbRemoveQuickDimInputV41(){
 if(kbQuickDimInputV41){kbQuickDimInputV41.remove();kbQuickDimInputV41=null}
 kbQuickDimObjectV41=null;
}
function kbQuickDimScreenPointV41(g){
 const m=kbAnchoredDimGeomV40(g),mid={x:(m.q1.x+m.q2.x)/2,y:(m.q1.y+m.q2.y)/2};
 let nx=-m.uy,ny=m.ux;if(ny>0){nx=-nx;ny=-ny}
 const fs=+g.dataset.fontSize||4,off=fs*.9+1.1,q={x:mid.x+nx*off,y:mid.y+ny*off};
 const r=paper.getBoundingClientRect();
 return{x:r.left+q.x/page.w*r.width,y:r.top+q.y/page.h*r.height};
}
function kbFinishQuickDimV41(commit=true){
 const input=kbQuickDimInputV41,g=kbQuickDimObjectV41;
 if(!input||!g)return;
 if(commit){
  const value=input.value.trim();
  if(value)g.dataset.value=value;
  renderDim(g);
  try{kbHistorySchedule(0)}catch{}
 }
 kbRemoveQuickDimInputV41();closeDimPopup();
 if(selected===g){clearUI();selected=null}
 if(typeof kbResumeStickyToolV31==='function')kbResumeStickyToolV31('Размер зафиксирован');
 else setTool('dimension',true);
}
function kbOpenQuickDimInputV41(g){
 kbRemoveQuickDimInputV41();closeDimPopup();closeTextPopup();
 const input=document.createElement('input');input.id='kbQuickDimValueV41';input.type='text';input.inputMode='decimal';input.autocomplete='off';input.placeholder='...';input.setAttribute('aria-label','Значение размера');
 const q=kbQuickDimScreenPointV41(g);input.style.left=q.x+'px';input.style.top=q.y+'px';
 input.addEventListener('pointerdown',e=>e.stopPropagation());
 input.addEventListener('keydown',e=>{
  if(e.key==='Enter'){e.preventDefault();e.stopPropagation();kbFinishQuickDimV41(true)}
  else if(e.key==='Tab'){kbFinishQuickDimV41(true)}
 });
 input.addEventListener('blur',()=>{if(kbQuickDimInputV41===input)setTimeout(()=>{if(kbQuickDimInputV41===input)kbFinishQuickDimV41(true)},0)},{once:true});
 document.body.appendChild(input);kbQuickDimInputV41=input;kbQuickDimObjectV41=g;
 requestAnimationFrame(()=>{input.focus();input.select()});
 setStatus('Введите значение размера и нажмите Enter');
}

// New dimensions no longer open the full properties dialog. Geometry is fixed
// first, then a compact ellipsis field appears exactly where the dimension text
// belongs. Double-click remains the route to full dimension properties.
kbCreateAnchoredDimensionV40=function(p1,p2,offset){
 const d=dimDefaults,g=el('g',{'data-type':'dimension','data-id':uid++,'data-anchor-model':'v40','data-p1':`${p1.x},${p1.y}`,'data-p2':`${p2.x},${p2.y}`,'data-dim-offset':String(offset||0),'data-value':'','data-prefix':d.prefix,'data-suffix':d.suffix,'data-arrow':d.arrow,'data-arrow-size':d.arrowSize,'data-arrow-angle':d.arrowAngle,'data-tail-size':d.tailSize??'2','data-line-width':d.lineWidth,'data-line-color':d.lineColor,'data-font':d.font,'data-font-size':d.fontSize,'data-text-color':d.textColor,'data-bold':d.bold?'1':'0','data-italic':d.italic?'1':'0'});
 appendContent(g);renderDim(g);clearUI();selected=g;lastEditable=g;drawSelection();closeDimPopup();
 setTimeout(()=>kbOpenQuickDimInputV41(g),0);return g;
};

window.addEventListener('resize',()=>{if(kbQuickDimInputV41&&kbQuickDimObjectV41){const q=kbQuickDimScreenPointV41(kbQuickDimObjectV41);kbQuickDimInputV41.style.left=q.x+'px';kbQuickDimInputV41.style.top=q.y+'px'}});
viewport?.addEventListener?.('scroll',()=>{if(kbQuickDimInputV41&&kbQuickDimObjectV41){const q=kbQuickDimScreenPointV41(kbQuickDimObjectV41);kbQuickDimInputV41.style.left=q.x+'px';kbQuickDimInputV41.style.top=q.y+'px'}},{passive:true});
'''

s = s.replace(anchor, code + anchor, 1)
for token in [
    marker,
    "fill-opacity:.34",
    "input.placeholder='...'",
    "kbOpenQuickDimInputV41(g)",
    "closeDimPopup();",
    "if(e.key==='Enter')"
]:
    if token not in s:
        raise SystemExit('v41 quick guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v41: translucent anchor handles and compact ellipsis dimension value entry installed')
