from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')
marker = 'KB911_V39_MEASUREMENT_GRID'
if marker in s:
    print('v39 already applied')
    raise SystemExit(0)

# ---- visual layer + sidebar controls -------------------------------------------------
if s.count('</head>') != 1:
    raise SystemExit('v39: expected one </head>')
style = r'''<style id="kb911MeasurementGridV39Style">
/* KB911_V39_MEASUREMENT_GRID */
#measurePanelV39 .m39-status{font-size:11px;line-height:1.35;color:#4b5563;background:#f6f8fb;border:1px solid #e0e4ea;border-radius:5px;padding:6px 7px;margin:7px 0}
#measurePanelV39 .m39-row{display:flex;gap:6px;align-items:center;margin-top:6px}
#measurePanelV39 .m39-row>*{min-width:0}
#measurePanelV39 .m39-row button{flex:1;height:30px;padding:0 6px;font-size:12px}
#measurePanelV39 input[type=text],#measurePanelV39 input[type=number],#measurePanelV39 select{height:30px;width:100%;font-size:12px}
#measurePanelV39 .m39-two{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:6px}
#measurePanelV39 .m39-check{display:flex;align-items:center;gap:6px;font-size:12px;margin-top:7px}
#measurePanelV39 .m39-sub{font-size:11px;color:#6b7280;margin-top:5px}
#measurePanelV39 #measureClearV39{width:100%;height:29px;margin-top:8px}
#dimValueModeRowV39{display:grid;grid-template-columns:72px 92px 1fr;gap:6px;align-items:center;margin:-1px 0 8px}
#dimValueModeRowV39 .dp-label{margin:0}
#dimValueModeV39{height:29px}
#dimAutoHintV39{font-size:11px;color:#5e6672;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#dimText.kb-auto-value-v39{background:#eef5ff;color:#173e85}
</style>
'''
s = s.replace('</head>', style + '</head>', 1)

panel_anchor = '  <div class="group" id="savePanel">'
if s.count(panel_anchor) != 1:
    raise SystemExit(f'v39: savePanel anchor count {s.count(panel_anchor)}')
panel = r'''  <div class="group" id="measurePanelV39" data-v39="KB911_V39_MEASUREMENT_GRID">
    <b>Измерительная сетка</b>
    <div id="measureStatusV39" class="m39-status">Выберите или откалибруйте изображение.</div>
    <div class="label">Известный размер, мм</div>
    <input id="measureKnownV39" type="text" inputmode="decimal" placeholder="Например: 2400">
    <div class="m39-row"><button id="measureBaseV39" type="button">1-й эталон</button><button id="measureXV39" type="button">Эталон X</button><button id="measureYV39" type="button">Эталон Y</button></div>
    <div class="m39-sub">Выберите размер на чертеже, введите его точное значение и назначьте эталоном. Первый эталон задаёт общий масштаб; X/Y позволяют уточнить растяжение по осям.</div>
    <div class="m39-two">
      <div><div class="label">Шаг сетки, мм</div><input id="measureStepV39" type="number" min="0.1" max="10000" step="1" value="10"></div>
      <div><div class="label">Точность</div><select id="measurePrecisionV39"><option value="1" selected>1 мм</option><option value="0.1">0,1 мм</option><option value="0.01">0,01 мм</option></select></div>
    </div>
    <label class="m39-check"><input id="measureShowGridV39" type="checkbox" checked> Показывать сетку</label>
    <label class="m39-check"><input id="measureSnapV39" type="checkbox"> Привязка размеров к сетке</label>
    <button id="measureClearV39" type="button">Сбросить калибровку</button>
  </div>
'''
s = s.replace(panel_anchor, panel + panel_anchor, 1)

# Dimension value mode: automatic calculated value remains optional, so old/manual
# drawings stay fully editable.
grid_anchor = '    <div class="dp-grid">'
if s.count(grid_anchor) != 1:
    raise SystemExit(f'v39: dimension grid anchor count {s.count(grid_anchor)}')
mode_row = r'''    <div id="dimValueModeRowV39"><div class="dp-label">Значение</div><select id="dimValueModeV39"><option value="auto">Авто</option><option value="manual">Вручную</option></select><div id="dimAutoHintV39">Ручное значение</div></div>
'''
s = s.replace(grid_anchor, mode_row + grid_anchor, 1)

# ---- runtime ------------------------------------------------------------------------
startup_anchor = '\nsetPage();\ninitKB911Project();\nkbHistoryStart();'
if s.count(startup_anchor) != 1:
    raise SystemExit(f'v39: startup anchor count {s.count(startup_anchor)}')

core = r'''

// KB911_V39_MEASUREMENT_GRID
// Calibration lives on each image as data-* attributes. Therefore the existing
// lossless SVG project snapshots, autosave and Undo/Redo preserve it without a
// project-format migration. The visible grid is a sibling overlay and is never
// saved or exported.
let kbMeasureTargetIdV39=null;
let kbMeasureBusyV39=0;
let kbMeasureRecalcTimerV39=null;
let kbMeasureMutationTimerV39=null;

function kbMeasureNumV39(v){
 const n=parseFloat(String(v??'').trim().replace(',','.'));
 return Number.isFinite(n)?n:NaN;
}
function kbMeasureImageByIdV39(id){
 if(id==null||id==='')return null;
 return [...paper.querySelectorAll('image[data-type="image"]')].find(n=>String(n.dataset.id)===String(id))||null;
}
function kbMeasureImagesV39(){return [...paper.querySelectorAll('image[data-type="image"]')]}
function kbMeasureHasCalibrationV39(img){
 if(!img)return false;
 const sx=kbMeasureNumV39(img.dataset.calScaleX),sy=kbMeasureNumV39(img.dataset.calScaleY);
 return sx>0&&sy>0;
}
function kbMeasureImageDefaultsV39(img){
 if(!img)return;
 if(!img.dataset.measureGridStep)img.dataset.measureGridStep='10';
 if(!img.dataset.measurePrecision)img.dataset.measurePrecision='1';
 if(img.dataset.measureGridShow==null)img.dataset.measureGridShow='1';
 if(img.dataset.measureSnap==null)img.dataset.measureSnap='0';
 const r=imageRect(img);
 if(!img.dataset.calImageW)img.dataset.calImageW=String(r.w);
 if(!img.dataset.calImageH)img.dataset.calImageH=String(r.h);
}
function kbMeasurePointInImageV39(p,img,margin=0){
 if(!p||!img)return false;const r=imageRect(img);
 return p.x>=r.x-margin&&p.x<=r.x+r.w+margin&&p.y>=r.y-margin&&p.y<=r.y+r.h+margin;
}
function kbMeasureDistanceToImageV39(p,img){
 const r=imageRect(img),dx=Math.max(r.x-p.x,0,p.x-(r.x+r.w)),dy=Math.max(r.y-p.y,0,p.y-(r.y+r.h));
 return Math.hypot(dx,dy);
}
function kbMeasureFindImageForSegmentV39(p1,p2,calibratedOnly=false){
 const imgs=kbMeasureImagesV39().filter(i=>!calibratedOnly||kbMeasureHasCalibrationV39(i));
 if(!imgs.length)return null;
 const target=kbMeasureImageByIdV39(kbMeasureTargetIdV39);
 const mid={x:(p1.x+p2.x)/2,y:(p1.y+p2.y)/2};
 if(target&&imgs.includes(target)&&(kbMeasurePointInImageV39(p1,target,2)&&kbMeasurePointInImageV39(p2,target,2)))return target;
 for(const img of [...imgs].reverse())if(kbMeasurePointInImageV39(p1,img,1)&&kbMeasurePointInImageV39(p2,img,1))return img;
 for(const img of [...imgs].reverse())if(kbMeasurePointInImageV39(mid,img,1))return img;
 if(target&&imgs.includes(target)){const r=imageRect(target);if(kbMeasureDistanceToImageV39(mid,target)<Math.max(r.w,r.h)*.35)return target}
 let best=null,bd=Infinity;for(const img of imgs){const d=kbMeasureDistanceToImageV39(mid,img);if(d<bd){bd=d;best=img}}
 if(best){const r=imageRect(best);if(bd<Math.max(r.w,r.h)*.30)return best}
 return imgs.length===1?imgs[0]:null;
}
function kbMeasureImageForDimV39(g,calibratedOnly=true){
 if(!g||g.dataset?.type!=='dimension')return null;
 const bound=kbMeasureImageByIdV39(g.dataset.calImageId);
 if(bound&&(!calibratedOnly||kbMeasureHasCalibrationV39(bound)))return bound;
 const p1=parsePt(g.dataset.p1),p2=parsePt(g.dataset.p2);
 return kbMeasureFindImageForSegmentV39(p1,p2,calibratedOnly);
}
function kbMeasurePrecisionV39(img){
 const p=kbMeasureNumV39(img?.dataset.measurePrecision);
 return [1,.1,.01].includes(p)?p:1;
}
function kbMeasureFormatV39(value,img){
 const p=kbMeasurePrecisionV39(img),q=Math.round(value/p)*p,d=p===1?0:p===.1?1:2;
 return q.toFixed(d).replace('.',',');
}
function kbMeasureValueV39(g,img=null){
 img=img||kbMeasureImageForDimV39(g,true);if(!img)return null;
 const sx=kbMeasureNumV39(img.dataset.calScaleX),sy=kbMeasureNumV39(img.dataset.calScaleY);if(!(sx>0&&sy>0))return null;
 const a=parsePt(g.dataset.p1),b=parsePt(g.dataset.p2),dx=(b.x-a.x)*sx,dy=(b.y-a.y)*sy;
 const v=Math.hypot(dx,dy);return Number.isFinite(v)?v:null;
}
function kbMeasureReferenceIdAttrV39(role){return role==='uniform'?'calBaseId':role==='x'?'calXId':'calYId'}
function kbMeasureParentImageV39(g){return kbMeasureImageByIdV39(g?.dataset.calImageId)}
function kbMeasureParentScaleV39(g,schedule=true){
 if(!g||g.dataset?.type!=='dimension'||!g.dataset.calRole)return null;
 const img=kbMeasureParentImageV39(g),known=kbMeasureNumV39(g.dataset.calKnown);if(!img||!(known>0))return null;
 kbMeasureImageDefaultsV39(img);
 const a=parsePt(g.dataset.p1),b=parsePt(g.dataset.p2),dx=Math.abs(b.x-a.x),dy=Math.abs(b.y-a.y),role=g.dataset.calRole;
 if(role==='uniform'){
  const L=Math.hypot(dx,dy);if(!(L>.0001))return null;const sc=known/L;
  if(!img.dataset.calXId||String(img.dataset.calXId)===String(g.dataset.id))img.dataset.calScaleX=String(sc);
  if(!img.dataset.calYId||String(img.dataset.calYId)===String(g.dataset.id))img.dataset.calScaleY=String(sc);
  img.dataset.calBaseId=String(g.dataset.id);
 }else if(role==='x'){
  if(!(dx>.0001))return null;img.dataset.calScaleX=String(known/dx);img.dataset.calXId=String(g.dataset.id);
  if(!(kbMeasureNumV39(img.dataset.calScaleY)>0))img.dataset.calScaleY=img.dataset.calScaleX;
 }else if(role==='y'){
  if(!(dy>.0001))return null;img.dataset.calScaleY=String(known/dy);img.dataset.calYId=String(g.dataset.id);
  if(!(kbMeasureNumV39(img.dataset.calScaleX)>0))img.dataset.calScaleX=img.dataset.calScaleY;
 }
 const r=imageRect(img);img.dataset.calImageW=String(r.w);img.dataset.calImageH=String(r.h);
 if(schedule)kbMeasureScheduleRecalcV39(img);
 return img;
}
function kbMeasureRecalcImageV39(img){
 if(!img||!kbMeasureHasCalibrationV39(img))return;
 kbMeasureBusyV39++;
 try{
  for(const g of paper.querySelectorAll('g[data-type="dimension"][data-auto-value="1"]')){
   if(String(g.dataset.calImageId)!==String(img.dataset.id))continue;
   const v=kbMeasureValueV39(g,img);if(v==null)continue;g.dataset.value=kbMeasureFormatV39(v,img);kbRenderDimBaseV39(g);
  }
 }finally{kbMeasureBusyV39--}
 if(selected?.dataset.type==='dimension')kbMeasureSyncDimModeUiV39(selected);
 kbMeasureRenderGridV39();kbMeasureUpdatePanelV39();
}
function kbMeasureScheduleRecalcV39(img){
 clearTimeout(kbMeasureRecalcTimerV39);const id=img?.dataset.id;
 kbMeasureRecalcTimerV39=setTimeout(()=>{const x=kbMeasureImageByIdV39(id);if(x)kbMeasureRecalcImageV39(x)},0);
}
function kbMeasureAdjustImageScaleV39(img){
 if(!kbMeasureHasCalibrationV39(img))return;
 const r=imageRect(img),ow=kbMeasureNumV39(img.dataset.calImageW),oh=kbMeasureNumV39(img.dataset.calImageH);
 if(ow>0&&oh>0){
  if(Math.abs(r.w-ow)>.0001)img.dataset.calScaleX=String(kbMeasureNumV39(img.dataset.calScaleX)*ow/r.w);
  if(Math.abs(r.h-oh)>.0001)img.dataset.calScaleY=String(kbMeasureNumV39(img.dataset.calScaleY)*oh/r.h);
 }
 img.dataset.calImageW=String(r.w);img.dataset.calImageH=String(r.h);
}
function kbMeasureGridOverlayV39(){
 let o=document.getElementById('kbMeasureGridOverlayV39');if(o)return o;
 o=document.createElementNS(NS,'svg');o.id='kbMeasureGridOverlayV39';o.setAttribute('aria-hidden','true');
 Object.assign(o.style,{position:'absolute',left:'0',top:'0',width:'100%',height:'100%',pointerEvents:'none',zIndex:'6',overflow:'hidden'});
 wrap.appendChild(o);return o;
}
function kbMeasureRenderGridV39(){
 const o=kbMeasureGridOverlayV39();o.setAttribute('viewBox',`0 0 ${page.w} ${page.h}`);while(o.firstChild)o.removeChild(o.firstChild);
 for(const img of kbMeasureImagesV39()){
  if(!kbMeasureHasCalibrationV39(img)||img.dataset.measureGridShow==='0')continue;
  kbMeasureImageDefaultsV39(img);const r=imageRect(img),sx=kbMeasureNumV39(img.dataset.calScaleX),sy=kbMeasureNumV39(img.dataset.calScaleY),step=Math.max(.1,kbMeasureNumV39(img.dataset.measureGridStep)||10),dx=step/sx,dy=step/sy;
  if(!(dx>0&&dy>0))continue;
  const gx=Math.floor(r.w/dx)+1,gy=Math.floor(r.h/dy)+1;if(gx>1200||gy>1200)continue;
  const g=el('g',{'data-grid-image':img.dataset.id});
  for(let i=0;i<=gx;i++){const x=r.x+i*dx;if(x>r.x+r.w+.001)break;const major=i%10===0;g.appendChild(el('line',{x1:x,y1:r.y,x2:x,y2:r.y+r.h,stroke:major?'#3978c5':'#6f9fd6','stroke-width':major?'.24':'.11',opacity:major?'.48':'.28','vector-effect':'non-scaling-stroke'}))}
  for(let i=0;i<=gy;i++){const y=r.y+i*dy;if(y>r.y+r.h+.001)break;const major=i%10===0;g.appendChild(el('line',{x1:r.x,y1:y,x2:r.x+r.w,y2:y,stroke:major?'#3978c5':'#6f9fd6','stroke-width':major?'.24':'.11',opacity:major?'.48':'.28','vector-effect':'non-scaling-stroke'}))}
  g.appendChild(el('rect',{x:r.x,y:r.y,width:r.w,height:r.h,fill:'none',stroke:'#3978c5','stroke-width':'.25',opacity:'.55','stroke-dasharray':'2 1','vector-effect':'non-scaling-stroke'}));
  o.appendChild(g);
 }
}
function kbMeasureSnapPointV39(p){
 if(!(tool==='dimension'||endpointDrag))return p;
 let img=kbMeasureFindImageForSegmentV39(p,p,true);if(!img||img.dataset.measureSnap!=='1')return p;
 const sx=kbMeasureNumV39(img.dataset.calScaleX),sy=kbMeasureNumV39(img.dataset.calScaleY),step=Math.max(.1,kbMeasureNumV39(img.dataset.measureGridStep)||10),r=imageRect(img);
 return{x:r.x+Math.round((p.x-r.x)*sx/step)*step/sx,y:r.y+Math.round((p.y-r.y)*sy/step)*step/sy};
}
function kbMeasureSelectedDimV39(){
 if(selected?.dataset.type==='dimension')return selected;
 if(lastEditable?.isConnected&&lastEditable.dataset?.type==='dimension')return lastEditable;
 return null;
}
function kbMeasureDetachRoleV39(img,role,except=null){
 const attr=kbMeasureReferenceIdAttrV39(role),id=img?.dataset?.[attr];if(!id)return;
 const old=findOwner(id,'dimension');if(old&&old!==except){delete old.dataset.calRole;delete old.dataset.calKnown;if(old.dataset.autoValue==null)old.dataset.autoValue='0'}
 delete img.dataset[attr];
}
function kbMeasureAssignReferenceV39(role){
 const g=kbMeasureSelectedDimV39(),known=kbMeasureNumV39($('measureKnownV39').value);
 if(!g){setStatus('Сначала выберите размер, который будет эталоном');return}
 if(!(known>0)){setStatus('Введите точный известный размер в миллиметрах');$('measureKnownV39').focus();return}
 const a=parsePt(g.dataset.p1),b=parsePt(g.dataset.p2);let img=kbMeasureImageForDimV39(g,false)||kbMeasureImageByIdV39(kbMeasureTargetIdV39);
 if(!img){setStatus('Эталон должен относиться к загруженной картинке');return}
 if(role==='x'&&Math.abs(b.x-a.x)<.001){setStatus('Для эталона X нужен горизонтальный размер');return}
 if(role==='y'&&Math.abs(b.y-a.y)<.001){setStatus('Для эталона Y нужен вертикальный размер');return}
 kbMeasureTargetIdV39=img.dataset.id;kbMeasureImageDefaultsV39(img);
 // A new first reference intentionally resets axis-specific parents. X/Y buttons
 // then add independent correction on top of that base scale.
 if(role==='uniform'){
  for(const rr of ['uniform','x','y'])kbMeasureDetachRoleV39(img,rr,g);
  delete img.dataset.calXId;delete img.dataset.calYId;
 }else{
  kbMeasureDetachRoleV39(img,role,g);
  if(g.dataset.calRole&&g.dataset.calRole!==role){const prev=kbMeasureReferenceIdAttrV39(g.dataset.calRole);if(String(img.dataset[prev])===String(g.dataset.id))delete img.dataset[prev]}
 }
 g.dataset.autoValue='0';g.dataset.calImageId=String(img.dataset.id);g.dataset.calRole=role;g.dataset.calKnown=String(known);g.dataset.value=String(known).replace('.',',');
 if(role==='uniform'){const L=Math.hypot(b.x-a.x,b.y-a.y),sc=known/L;img.dataset.calScaleX=String(sc);img.dataset.calScaleY=String(sc);img.dataset.calBaseId=String(g.dataset.id)}
 else if(role==='x'){img.dataset.calScaleX=String(known/Math.abs(b.x-a.x));img.dataset.calXId=String(g.dataset.id);if(!(kbMeasureNumV39(img.dataset.calScaleY)>0))img.dataset.calScaleY=img.dataset.calScaleX}
 else{img.dataset.calScaleY=String(known/Math.abs(b.y-a.y));img.dataset.calYId=String(g.dataset.id);if(!(kbMeasureNumV39(img.dataset.calScaleX)>0))img.dataset.calScaleX=img.dataset.calScaleY}
 const r=imageRect(img);img.dataset.calImageW=String(r.w);img.dataset.calImageH=String(r.h);
 kbRenderDimBaseV39(g);kbMeasureRecalcImageV39(img);kbMeasureSyncDimModeUiV39(g);kbMeasureUpdatePanelV39();kbMeasureRenderGridV39();
 try{kbHistorySchedule(0)}catch{}
 setStatus(role==='uniform'?'Первый эталон установлен. Новые размеры рассчитываются автоматически':`Эталон ${role.toUpperCase()} установлен. Масштаб по оси уточнён`);
}
function kbMeasureClearCalibrationV39(){
 const img=kbMeasureResolveTargetV39();if(!img||!kbMeasureHasCalibrationV39(img)){setStatus('Нет активной калибровки');return}
 for(const g of paper.querySelectorAll('g[data-type="dimension"]')){
  if(String(g.dataset.calImageId)!==String(img.dataset.id))continue;
  if(g.dataset.autoValue==='1')g.dataset.autoValue='0';delete g.dataset.calImageId;delete g.dataset.calRole;delete g.dataset.calKnown;
 }
 for(const k of ['calScaleX','calScaleY','calBaseId','calXId','calYId','calImageW','calImageH'])delete img.dataset[k];
 kbMeasureRenderGridV39();kbMeasureUpdatePanelV39();if(selected?.dataset.type==='dimension')kbMeasureSyncDimModeUiV39(selected);try{kbHistorySchedule(0)}catch{}setStatus('Калибровка изображения сброшена. Размеры оставлены с последними значениями');
}
function kbMeasureResolveTargetV39(){
 if(selected?.dataset.type==='image'){kbMeasureTargetIdV39=selected.dataset.id;return selected}
 if(selected?.dataset.type==='dimension'){const x=kbMeasureImageForDimV39(selected,false);if(x){kbMeasureTargetIdV39=x.dataset.id;return x}}
 const active=kbMeasureImageByIdV39(kbMeasureTargetIdV39);if(active)return active;
 const calibrated=kbMeasureImagesV39().find(kbMeasureHasCalibrationV39);if(calibrated){kbMeasureTargetIdV39=calibrated.dataset.id;return calibrated}
 const first=kbMeasureImagesV39()[0]||null;if(first)kbMeasureTargetIdV39=first.dataset.id;return first;
}
function kbMeasureUpdatePanelV39(){
 const img=kbMeasureResolveTargetV39(),st=$('measureStatusV39');if(!img){st.textContent='На листе нет картинки. Загрузите изображение и нанесите известный размер.';return}
 kbMeasureImageDefaultsV39(img);const calibrated=kbMeasureHasCalibrationV39(img),sx=kbMeasureNumV39(img.dataset.calScaleX),sy=kbMeasureNumV39(img.dataset.calScaleY);
 st.textContent=calibrated?`Картинка #${img.dataset.id} · X ${sx.toFixed(4)} мм/ед. · Y ${sy.toFixed(4)} мм/ед.`:`Картинка #${img.dataset.id} · не откалибрована`;
 $('measureStepV39').value=img.dataset.measureGridStep||10;$('measurePrecisionV39').value=img.dataset.measurePrecision||'1';$('measureShowGridV39').checked=img.dataset.measureGridShow!=='0';$('measureSnapV39').checked=img.dataset.measureSnap==='1';
 const g=kbMeasureSelectedDimV39();if(g?.dataset.calKnown&&document.activeElement!==$('measureKnownV39'))$('measureKnownV39').value=String(g.dataset.calKnown).replace('.',',');
}
function kbMeasureSyncDimModeUiV39(g){
 const sel=$('dimValueModeV39'),hint=$('dimAutoHintV39'),input=$('dimText');if(!sel||!hint||!input||!g||g.dataset?.type!=='dimension')return;
 const parent=!!g.dataset.calRole,auto=!parent&&g.dataset.autoValue==='1';sel.value=auto?'auto':'manual';sel.disabled=parent;input.readOnly=auto;input.classList.toggle('kb-auto-value-v39',auto);
 if(parent)hint.textContent=`Эталон ${g.dataset.calRole==='uniform'?'1':g.dataset.calRole.toUpperCase()} · ${String(g.dataset.calKnown||g.dataset.value||'')} мм`;
 else if(auto){const img=kbMeasureImageForDimV39(g,true);hint.textContent=img?`Авто · картинка #${img.dataset.id}`:'Авто · нет калибровки'}
 else hint.textContent='Ручное значение';
}
function kbMeasureSetDimModeV39(mode){
 const g=kbMeasureSelectedDimV39();if(!g||g.dataset.calRole)return;
 if(mode==='manual'){g.dataset.autoValue='0';delete g.dataset.calImageId;$('dimText').readOnly=false;$('dimText').classList.remove('kb-auto-value-v39');kbMeasureSyncDimModeUiV39(g);try{kbHistorySchedule(0)}catch{};return}
 const img=kbMeasureImageForDimV39(g,true);if(!img){$('dimValueModeV39').value='manual';setStatus('Для автоматического значения сначала задайте эталонный размер');return}
 g.dataset.autoValue='1';g.dataset.calImageId=String(img.dataset.id);const v=kbMeasureValueV39(g,img);if(v!=null)g.dataset.value=kbMeasureFormatV39(v,img);kbRenderDimBaseV39(g);$('dimText').value=g.dataset.value||'';kbMeasureSyncDimModeUiV39(g);try{kbHistorySchedule(0)}catch{};
}
function kbMeasureAdoptNewDimV39(g){
 if(!g||g.dataset?.type!=='dimension'||g.id==='preview-v32'||g.classList?.contains('kb-dim-preview-v32'))return;
 // A pasted calibration parent must not silently become a second parent.
 if(g.dataset.calRole){const img=kbMeasureImageByIdV39(g.dataset.calImageId),attr=kbMeasureReferenceIdAttrV39(g.dataset.calRole);if(!img||String(img.dataset[attr])!==String(g.dataset.id)){delete g.dataset.calRole;delete g.dataset.calKnown;g.dataset.autoValue='0'}}
 if(g.dataset.autoValue==null){const img=kbMeasureImageForDimV39(g,true);g.dataset.autoValue=img?'1':'0';if(img)g.dataset.calImageId=String(img.dataset.id)}
 if(g.dataset.autoValue==='1'){const img=kbMeasureImageForDimV39(g,true),v=kbMeasureValueV39(g,img);if(img&&v!=null){g.dataset.calImageId=String(img.dataset.id);g.dataset.value=kbMeasureFormatV39(v,img);kbRenderDimBaseV39(g)}}
 if(selected===g){$('dimText').value=g.dataset.value||'';kbMeasureSyncDimModeUiV39(g)}
}
function kbMeasureRefreshAllV39(){
 for(const img of kbMeasureImagesV39()){if(kbMeasureHasCalibrationV39(img)){kbMeasureImageDefaultsV39(img);kbMeasureAdjustImageScaleV39(img)}}
 for(const g of paper.querySelectorAll('g[data-type="dimension"]')){
  if(g.dataset.autoValue==null)g.dataset.autoValue='0';
  if(g.dataset.calRole)kbMeasureParentScaleV39(g,false);
 }
 for(const img of kbMeasureImagesV39())if(kbMeasureHasCalibrationV39(img))kbMeasureRecalcImageV39(img);
 kbMeasureRenderGridV39();kbMeasureUpdatePanelV39();
}

// Wrap existing stable functions rather than rewriting their internal geometry.
const kbRenderDimBaseV39=renderDim;
renderDim=function(g){
 if(!g||g.dataset?.type!=='dimension'||kbMeasureBusyV39)return kbRenderDimBaseV39(g);
 kbMeasureBusyV39++;
 try{
  if(g.dataset.calRole)kbMeasureParentScaleV39(g,true);
  if(g.dataset.autoValue==='1'){const img=kbMeasureImageForDimV39(g,true),v=kbMeasureValueV39(g,img);if(img&&v!=null){g.dataset.calImageId=String(img.dataset.id);g.dataset.value=kbMeasureFormatV39(v,img)}}
  return kbRenderDimBaseV39(g);
 }finally{kbMeasureBusyV39--}
};
const kbPtBaseV39=pt;
pt=function(e){return kbMeasureSnapPointV39(kbPtBaseV39(e))};
const kbSyncDimPropsBaseV39=syncDimProps;
syncDimProps=function(){const r=kbSyncDimPropsBaseV39();if(selected?.dataset.type==='dimension')kbMeasureSyncDimModeUiV39(selected);return r};
const kbSelectBaseV39=select;
select=function(n){const r=kbSelectBaseV39(n);if(n?.dataset.type==='image')kbMeasureTargetIdV39=n.dataset.id;else if(n?.dataset.type==='dimension'){const img=kbMeasureImageForDimV39(n,false);if(img)kbMeasureTargetIdV39=img.dataset.id}kbMeasureUpdatePanelV39();return r};
const kbLoadSheetBaseV39=kbLoadSheet;
kbLoadSheet=function(index){const r=kbLoadSheetBaseV39(index);kbMeasureTargetIdV39=null;setTimeout(kbMeasureRefreshAllV39,0);return r};
const kbCommitEditorsForExportBaseV39=commitEditorsForExport;
commitEditorsForExport=function(){kbMeasureRefreshAllV39();return kbCommitEditorsForExportBaseV39()};

$('measureBaseV39').onclick=()=>kbMeasureAssignReferenceV39('uniform');
$('measureXV39').onclick=()=>kbMeasureAssignReferenceV39('x');
$('measureYV39').onclick=()=>kbMeasureAssignReferenceV39('y');
$('measureClearV39').onclick=kbMeasureClearCalibrationV39;
$('dimValueModeV39').onchange=()=>kbMeasureSetDimModeV39($('dimValueModeV39').value);
$('measureStepV39').onchange=()=>{const img=kbMeasureResolveTargetV39(),v=kbMeasureNumV39($('measureStepV39').value);if(!img||!(v>0))return;img.dataset.measureGridStep=String(v);kbMeasureRenderGridV39();try{kbHistorySchedule(0)}catch{}};
$('measurePrecisionV39').onchange=()=>{const img=kbMeasureResolveTargetV39();if(!img)return;img.dataset.measurePrecision=$('measurePrecisionV39').value;kbMeasureRecalcImageV39(img);try{kbHistorySchedule(0)}catch{}};
$('measureShowGridV39').onchange=()=>{const img=kbMeasureResolveTargetV39();if(!img)return;img.dataset.measureGridShow=$('measureShowGridV39').checked?'1':'0';kbMeasureRenderGridV39();try{kbHistorySchedule(0)}catch{}};
$('measureSnapV39').onchange=()=>{const img=kbMeasureResolveTargetV39();if(!img)return;img.dataset.measureSnap=$('measureSnapV39').checked?'1':'0';try{kbHistorySchedule(0)}catch{}};

// Parent value edits recalibrate instantly. Ordinary auto dimensions are read-only.
document.addEventListener('input',e=>{if(e.target!==$('dimText')||selected?.dataset.type!=='dimension'||!selected.dataset.calRole)return;const v=kbMeasureNumV39(e.target.value);if(v>0){selected.dataset.calKnown=String(v);kbMeasureParentScaleV39(selected,true)}},true);
document.addEventListener('change',e=>{if(e.target===$('paperSize')||e.target===$('orientation'))setTimeout(kbMeasureRenderGridV39,0)},true);

const kbMeasureObserverV39=new MutationObserver(records=>{
 let need=false;
 for(const m of records){
  if(m.type==='childList')for(const n of m.addedNodes){if(n?.nodeType===1&&n.matches?.('g[data-type="dimension"]'))kbMeasureAdoptNewDimV39(n);if(n?.nodeType===1&&n.matches?.('image[data-type="image"]'))need=true}
  const img=m.target?.nodeType===1?(m.target.matches?.('image[data-type="image"]')?m.target:null):null;
  if(img){if(m.attributeName==='width'||m.attributeName==='height')kbMeasureAdjustImageScaleV39(img);need=true}
 }
 if(need){clearTimeout(kbMeasureMutationTimerV39);kbMeasureMutationTimerV39=setTimeout(kbMeasureRefreshAllV39,20)}
});
kbMeasureObserverV39.observe(paper,{subtree:true,childList:true,attributes:true,attributeFilter:['x','y','width','height','data-cal-scale-x','data-cal-scale-y','data-measure-grid-step','data-measure-grid-show']});

// Existing dimensions from pre-v39 projects remain manual by default.
paper.querySelectorAll('g[data-type="dimension"]').forEach(g=>{if(g.dataset.autoValue==null)g.dataset.autoValue='0'});
setTimeout(kbMeasureRefreshAllV39,0);
'''

s = s.replace(startup_anchor, core + startup_anchor, 1)

# Static guards: the grid must stay outside paper snapshots/exports, and automatic
# dimensions must remain an explicit opt-in state stored on each dimension.
for token in [
    marker,
    'id="measurePanelV39"',
    'id="dimValueModeV39"',
    'function kbMeasureAssignReferenceV39(role)',
    'data-auto-value="1"',
    "wrap.appendChild(o)",
    'const kbRenderDimBaseV39=renderDim',
    'const kbLoadSheetBaseV39=kbLoadSheet',
    "img.dataset.calScaleX",
    "img.dataset.calScaleY",
    "kbMeasureSnapPointV39"
]:
    if token not in s:
        raise SystemExit('v39 guard failed: ' + token)

p.write_text(s, encoding='utf-8', newline='')
print('v39: calibrated per-image grid, one/two reference dimensions, snapping and automatic measured dimensions installed')
