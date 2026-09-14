from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')

marker = 'KB911_V39_CALIBRATION_GRID'
if marker in s:
    print('v39 already applied')
    raise SystemExit(0)

def replace_once(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'v39 {label}: expected one anchor, got {count}')
    s = s.replace(old, new, 1)

save_anchor = '  <div class="group" id="savePanel">'
panel = r'''  <div class="group" id="calibrationPanel" data-v39="KB911_V39_CALIBRATION_GRID">
    <b>Измерительная сетка</b>
    <div class="hint" style="margin:5px 0 8px">1 эталон задаёт единый масштаб. 2 эталона уточняют масштаб отдельно по X/Y.</div>
    <div id="calibrationStatus" class="hint" style="margin-bottom:8px">Масштаб не задан</div>
    <div class="cal-v39-row">
      <label>Шаг, мм<input id="calGridStep" type="number" min="0.1" max="100000" step="1" value="100"></label>
      <label>Точность<select id="calPrecision"><option value="1" selected>1 мм</option><option value="0.1">0,1 мм</option><option value="0.01">0,01 мм</option></select></label>
    </div>
    <label class="frame-toggle"><input id="calGridVisible" type="checkbox" checked> Показать сетку</label>
    <label class="frame-toggle"><input id="calGridSnap" type="checkbox"> Привязка размера к сетке</label>
    <button id="calibrationClear" style="width:100%;margin-top:3px">Сбросить калибровку</button>
  </div>
'''
replace_once(save_anchor, panel + save_anchor, 'calibration panel')

actions_anchor = '    <div class="dp-actions"><button id="dimSetDefault">По умолчанию</button><button id="dimPopupOk" class="primary">OK</button></div>'
calc_row = r'''    <div class="dp-full kb-dim-calc-v39">
      <label><input id="dimAutoValue" type="checkbox"> Автоматическое значение</label>
      <span id="dimCalcState">Ручной размер</span>
      <button id="dimMakeParent" type="button">Сделать эталоном</button>
    </div>
'''
replace_once(actions_anchor, calc_row + actions_anchor, 'dimension calculation row')

style = r'''<style id="kb911CalibrationGridV39Style">
/* KB911_V39_CALIBRATION_GRID */
#calibrationPanel .cal-v39-row{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-bottom:5px}
#calibrationPanel .cal-v39-row label{font-size:11px;color:#555}
#calibrationPanel .cal-v39-row input,#calibrationPanel .cal-v39-row select{display:block;width:100%;height:28px;margin-top:2px}
.kb-dim-calc-v39{display:grid;grid-template-columns:auto 1fr auto;gap:8px;align-items:center;margin-top:8px;padding-top:8px;border-top:1px solid #ddd}
.kb-dim-calc-v39 label{white-space:nowrap}.kb-dim-calc-v39 #dimCalcState{font-size:11px;color:#667085;text-align:center}
.kb-cal-grid-v39{pointer-events:none}
</style>
'''
replace_once('</head>', style + '</head>', 'style')

js = r'''
// KB911_V39_CALIBRATION_GRID
let kbCalibrationBusyV39=false,kbCalImageHintV39=null,kbGridMutationBusyV39=false;

function kbNumV39(v){
 const n=Number(String(v??'').trim().replace(',','.'));
 return Number.isFinite(n)?n:NaN;
}
function kbDimDeltaV39(g){
 const p1=parsePt(g.dataset.p1||'0,0'),p2=parsePt(g.dataset.p2||'0,0');
 return {p1,p2,dx:p2.x-p1.x,dy:p2.y-p1.y,L:Math.hypot(p2.x-p1.x,p2.y-p1.y)};
}
function kbImagesV39(){return [...paper.querySelectorAll('image[data-type="image"]')]}
function kbContainsV39(img,p,tol=1.5){
 const r=imageRect(img);
 return p.x>=r.x-tol&&p.x<=r.x+r.w+tol&&p.y>=r.y-tol&&p.y<=r.y+r.h+tol;
}
function kbFindImageForSegmentV39(p1,p2,calibratedOnly=false){
 let imgs=kbImagesV39().filter(i=>!calibratedOnly||(+i.dataset.calScaleX>0&&+i.dataset.calScaleY>0));
 let c=imgs.filter(i=>kbContainsV39(i,p1)&&kbContainsV39(i,p2));
 if(!c.length){
   const m={x:(p1.x+p2.x)/2,y:(p1.y+p2.y)/2};
   c=imgs.filter(i=>kbContainsV39(i,m,3));
 }
 if(!c.length&&imgs.length===1)c=imgs;
 return c.length?c[c.length-1]:null;
}
function kbImageByRuntimeIdV39(id){return kbImagesV39().find(i=>String(i.dataset.id)===String(id))||null}
function kbImageByGroupV39(group){return kbImagesV39().find(i=>i.dataset.calGroup===group)||null}
function kbGroupKeyV39(){return 'cal-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,8)}
function kbParentsForGroupV39(group){
 return [...paper.querySelectorAll('g[data-type="dimension"]')]
   .filter(g=>g.dataset.calMode==='parent'&&g.dataset.calGroup===group)
   .sort((a,b)=>(+a.dataset.calParentOrder||99)-(+b.dataset.calParentOrder||99));
}
function kbDecimalsV39(step){
 const t=String(step);
 if(t.includes('e-'))return Math.min(6,+t.split('e-')[1]||0);
 const i=t.indexOf('.');return i<0?0:Math.min(6,t.length-i-1);
}
function kbFormatMeasuredV39(value,precision){
 const p=Math.max(.000001,kbNumV39(precision)||1),n=Math.round(value/p)*p,d=kbDecimalsV39(p);
 return d?n.toFixed(d).replace(/\.?0+$/,''):String(Math.round(n));
}
function kbApplySettingsToImageV39(img,parent){
 img.dataset.calGridStep=String(Math.max(.1,kbNumV39(parent?.dataset.calGridStep)||100));
 img.dataset.calPrecision=String(Math.max(.000001,kbNumV39(parent?.dataset.calPrecision)||1));
 img.dataset.calGridVisible=(parent?.dataset.calGridVisible??'1');
 img.dataset.calGridSnap=(parent?.dataset.calGridSnap??'0');
}
function kbCopySettingsToParentsV39(img){
 const group=img?.dataset.calGroup;if(!group)return;
 for(const p of kbParentsForGroupV39(group)){
   p.dataset.calGridStep=img.dataset.calGridStep||'100';
   p.dataset.calPrecision=img.dataset.calPrecision||'1';
   p.dataset.calGridVisible=img.dataset.calGridVisible??'1';
   p.dataset.calGridSnap=img.dataset.calGridSnap??'0';
 }
}
function kbAutoValueV39(g,img){
 const {dx,dy}=kbDimDeltaV39(g),sx=+img.dataset.calScaleX,sy=+img.dataset.calScaleY;
 if(!(sx>0&&sy>0))return null;
 return Math.sqrt((dx*sx)**2+(dy*sy)**2);
}
function kbUpdateAutoDimensionV39(g,img=null){
 if(!g||g.dataset.type!=='dimension'||g.dataset.calMode!=='auto')return false;
 img=img||kbImageByGroupV39(g.dataset.calGroup)||kbImageByRuntimeIdV39(g.dataset.calImageId);
 if(!img){
   const d=kbDimDeltaV39(g);img=kbFindImageForSegmentV39(d.p1,d.p2,true);
 }
 if(!img)return false;
 const v=kbAutoValueV39(g,img);if(!(v>=0))return false;
 g.dataset.calGroup=img.dataset.calGroup||g.dataset.calGroup||'';
 g.dataset.calImageId=img.dataset.id||'';
 g.dataset.value=kbFormatMeasuredV39(v,img.dataset.calPrecision||'1');
 return true;
}
function kbCalibrationClearImageAttrsV39(img){
 for(const k of ['calGroup','calScaleX','calScaleY','calSolve','calOriginX','calOriginY','calGridStep','calPrecision','calGridVisible','calGridSnap'])delete img.dataset[k];
}
function kbSolveCalibrationV39(img,quiet=false){
 if(!img)return 'none';
 const group=img.dataset.calGroup;if(!group)return 'none';
 let parents=kbParentsForGroupV39(group);
 if(!parents.length){kbCalibrationClearImageAttrsV39(img);return 'none'}
 parents=parents.slice(0,2);
 parents.forEach((g,i)=>{g.dataset.calParentOrder=String(i+1);g.dataset.calImageId=img.dataset.id||'';g.dataset.calGroup=group});
 const first=parents[0],a=kbDimDeltaV39(first),known1=kbNumV39(first.dataset.calKnownValue||first.dataset.value);
 if(!(known1>0&&a.L>1e-9))return 'invalid';
 let sx=known1/a.L,sy=sx,mode='uniform';
 if(parents.length>1){
   const second=parents[1],b=kbDimDeltaV39(second),known2=kbNumV39(second.dataset.calKnownValue||second.dataset.value);
   const A1=a.dx*a.dx,B1=a.dy*a.dy,C1=known1*known1,A2=b.dx*b.dx,B2=b.dy*b.dy,C2=known2*known2;
   const det=A1*B2-A2*B1,scale=Math.abs(A1*B2)+Math.abs(A2*B1)+1;
   if(known2>0&&b.L>1e-9&&Math.abs(det)>scale*1e-7){
     const sx2=(C1*B2-C2*B1)/det,sy2=(A1*C2-A2*C1)/det;
     if(sx2>0&&sy2>0&&Number.isFinite(sx2)&&Number.isFinite(sy2)){sx=Math.sqrt(sx2);sy=Math.sqrt(sy2);mode='xy'}
   }
 }
 img.dataset.calScaleX=String(sx);img.dataset.calScaleY=String(sy);img.dataset.calSolve=mode;
 img.dataset.calOriginX=String(a.p1.x);img.dataset.calOriginY=String(a.p1.y);
 kbApplySettingsToImageV39(img,first);kbCopySettingsToParentsV39(img);
 kbCalibrationBusyV39=true;
 try{
   for(const g of paper.querySelectorAll('g[data-type="dimension"]')){
     if(g.dataset.calMode==='auto'&&g.dataset.calGroup===group){
       kbUpdateAutoDimensionV39(g,img);kbBaseRenderDimV39(g);
     }
   }
 }finally{kbCalibrationBusyV39=false}
 kbRenderAllCalibrationGridsV39();
 if(!quiet)kbUpdateCalibrationPanelV39(img);
 return mode;
}
function kbBindBlankDimensionsV39(img){
 const group=img?.dataset.calGroup;if(!group)return;
 for(const g of paper.querySelectorAll('g[data-type="dimension"]')){
   if(g.dataset.calMode||String(g.dataset.value||'').trim())continue;
   const d=kbDimDeltaV39(g),hit=kbFindImageForSegmentV39(d.p1,d.p2,false);
   if(hit!==img)continue;
   g.dataset.calMode='auto';g.dataset.calGroup=group;g.dataset.calImageId=img.dataset.id||'';
   kbUpdateAutoDimensionV39(g,img);kbBaseRenderDimV39(g);
 }
}
function kbRenderGridForImageV39(img){
 if(!img||!(+img.dataset.calScaleX>0&&+img.dataset.calScaleY>0)||img.dataset.calGridVisible==='0')return;
 const step=Math.max(.1,kbNumV39(img.dataset.calGridStep)||100),sx=+img.dataset.calScaleX,sy=+img.dataset.calScaleY;
 const dx=step/sx,dy=step/sy;if(!(dx>0&&dy>0&&Number.isFinite(dx)&&Number.isFinite(dy)))return;
 const r=imageRect(img),ox=kbNumV39(img.dataset.calOriginX),oy=kbNumV39(img.dataset.calOriginY);
 const originX=Number.isFinite(ox)?ox:r.x,originY=Number.isFinite(oy)?oy:r.y;
 const kx0=Math.ceil((r.x-originX)/dx),kx1=Math.floor((r.x+r.w-originX)/dx);
 const ky0=Math.ceil((r.y-originY)/dy),ky1=Math.floor((r.y+r.h-originY)/dy);
 const nx=Math.max(0,kx1-kx0+1),ny=Math.max(0,ky1-ky0+1),strideX=Math.max(1,Math.ceil(nx/350)),strideY=Math.max(1,Math.ceil(ny/350));
 const g=el('g',{'class':'kb-cal-grid-v39','data-kb-cal-grid-v39':img.dataset.id||'','pointer-events':'none'});
 for(let k=kx0;k<=kx1;k+=strideX){
   const x=originX+k*dx,major=Math.abs(k)%5===0;
   g.appendChild(el('line',{x1:x,y1:r.y,x2:x,y2:r.y+r.h,stroke:'#64748b','stroke-width':major?'.18':'.10',opacity:major?'.34':'.18','vector-effect':'non-scaling-stroke'}));
 }
 for(let k=ky0;k<=ky1;k+=strideY){
   const y=originY+k*dy,major=Math.abs(k)%5===0;
   g.appendChild(el('line',{x1:r.x,y1:y,x2:r.x+r.w,y2:y,stroke:'#64748b','stroke-width':major?'.18':'.10',opacity:major?'.34':'.18','vector-effect':'non-scaling-stroke'}));
 }
 img.parentNode?.insertBefore(g,img.nextSibling);
}
function kbRenderAllCalibrationGridsV39(){
 if(kbGridMutationBusyV39)return;
 kbGridMutationBusyV39=true;
 try{
   paper.querySelectorAll('[data-kb-cal-grid-v39]').forEach(n=>n.remove());
   for(const img of kbImagesV39())kbRenderGridForImageV39(img);
 }finally{kbGridMutationBusyV39=false}
}
function kbImageForSelectedV39(){
 const q=selected;
 if(q?.dataset.type==='image')return q;
 if(q?.dataset.type==='dimension'){
   const linked=kbImageByGroupV39(q.dataset.calGroup)||kbImageByRuntimeIdV39(q.dataset.calImageId);
   if(linked)return linked;
   const d=kbDimDeltaV39(q);return kbFindImageForSegmentV39(d.p1,d.p2,false);
 }
 if(kbCalImageHintV39?.isConnected)return kbCalImageHintV39;
 return kbImagesV39().find(i=>i.dataset.calGroup)||null;
}
function kbUpdateCalibrationPanelV39(preferred=null){
 const img=preferred||kbImageForSelectedV39();if(img)kbCalImageHintV39=img;
 const st=$('calibrationStatus');if(!st)return;
 if(!img){st.textContent='Выберите размер или изображение';return}
 if(!(+img.dataset.calScaleX>0&&+img.dataset.calScaleY>0)){
   st.textContent='Масштаб не задан. Нанесите известный размер и сделайте его эталоном.';return;
 }
 const parents=kbParentsForGroupV39(img.dataset.calGroup);
 st.textContent=img.dataset.calSolve==='xy'?'2 эталона · X/Y откалиброваны':'1 эталон · единый масштаб';
 $('calGridStep').value=img.dataset.calGridStep||'100';
 $('calPrecision').value=img.dataset.calPrecision||'1';
 $('calGridVisible').checked=img.dataset.calGridVisible!=='0';
 $('calGridSnap').checked=img.dataset.calGridSnap==='1';
 if(parents.length===2&&img.dataset.calSolve!=='xy')st.textContent='2-й эталон требует другого направления';
}
function kbSyncDimCalcUiV39(){
 const g=selected;if(!g||g.dataset.type!=='dimension')return;
 const mode=g.dataset.calMode||'manual',state=$('dimCalcState'),auto=$('dimAutoValue'),btn=$('dimMakeParent');
 auto.checked=mode==='auto';auto.disabled=mode==='parent';
 if(mode==='parent'){state.textContent='Эталон '+(g.dataset.calParentOrder||'');btn.textContent='Обновить эталон'}
 else if(mode==='auto'){state.textContent='Авто по сетке';btn.textContent='Сделать эталоном'}
 else{state.textContent='Ручной размер';btn.textContent='Сделать эталоном'}
}
function kbSetImageSettingV39(key,value){
 const img=kbImageForSelectedV39();
 if(!img||!img.dataset.calGroup){setStatus('Сначала задайте эталонный размер');kbUpdateCalibrationPanelV39(img);return false}
 img.dataset[key]=String(value);kbCopySettingsToParentsV39(img);
 kbSolveCalibrationV39(img,true);kbUpdateCalibrationPanelV39(img);
 try{kbHistorySchedule(0)}catch{}
 return true;
}
function kbMakeSelectedParentV39(){
 const g=selected;if(!g||g.dataset.type!=='dimension'){setStatus('Сначала выберите размер с точно известным значением');return}
 const known=kbNumV39(g.dataset.value);
 if(!(known>0)){setStatus('Введите точное известное значение размера, затем нажмите «Сделать эталоном»');$('dimText')?.focus();return}
 const d=kbDimDeltaV39(g),img=kbFindImageForSegmentV39(d.p1,d.p2,false);
 if(!img){setStatus('Эталон должен находиться на загруженном изображении');return}
 let group=img.dataset.calGroup||g.dataset.calGroup||kbGroupKeyV39();
 if(img.dataset.calGroup&&g.dataset.calGroup&&img.dataset.calGroup!==g.dataset.calGroup)group=img.dataset.calGroup;
 img.dataset.calGroup=group;kbCalImageHintV39=img;
 let parents=kbParentsForGroupV39(group).filter(x=>x!==g);
 if(parents.length>=2){setStatus('Для изображения уже заданы два эталона. Сначала сбросьте калибровку.');return}
 const old={mode:g.dataset.calMode,group:g.dataset.calGroup,image:g.dataset.calImageId,order:g.dataset.calParentOrder,known:g.dataset.calKnownValue};
 g.dataset.calMode='parent';g.dataset.calGroup=group;g.dataset.calImageId=img.dataset.id||'';g.dataset.calParentOrder=String(parents.length+1);g.dataset.calKnownValue=String(known);
 if(parents.length===0){
   g.dataset.calGridStep=$('calGridStep').value||'100';g.dataset.calPrecision=$('calPrecision').value||'1';
   g.dataset.calGridVisible=$('calGridVisible').checked?'1':'0';g.dataset.calGridSnap=$('calGridSnap').checked?'1':'0';
 }else{
   const p=parents[0];g.dataset.calGridStep=p.dataset.calGridStep||'100';g.dataset.calPrecision=p.dataset.calPrecision||'1';
   g.dataset.calGridVisible=p.dataset.calGridVisible??'1';g.dataset.calGridSnap=p.dataset.calGridSnap??'0';
 }
 const solved=kbSolveCalibrationV39(img,true);
 if(parents.length===1&&solved!=='xy'){
   const map={calMode:'mode',calGroup:'group',calImageId:'image',calParentOrder:'order',calKnownValue:'known'};
   for(const k of Object.keys(map)){const v=old[map[k]];if(v==null)delete g.dataset[k];else g.dataset[k]=v}
   kbSolveCalibrationV39(img,true);kbUpdateCalibrationPanelV39(img);kbSyncDimCalcUiV39();
   setStatus('Второй эталон должен быть направлен иначе, чтобы вычислить отдельные масштабы X/Y');return;
 }
 kbBindBlankDimensionsV39(img);kbSolveCalibrationV39(img,true);kbUpdateCalibrationPanelV39(img);kbSyncDimCalcUiV39();
 setStatus(solved==='xy'?'Калибровка по двум эталонам готова — размеры X/Y уточнены':'Калибровка готова — следующие размеры рассчитываются автоматически');
 try{kbHistorySchedule(0)}catch{}
}
function kbClearCalibrationV39(){
 const img=kbImageForSelectedV39();if(!img?.dataset.calGroup){setStatus('На выбранном изображении калибровка не задана');return}
 const group=img.dataset.calGroup;
 for(const g of paper.querySelectorAll('g[data-type="dimension"]')){
   if(g.dataset.calGroup!==group)continue;
   if(g.dataset.calMode==='auto'||g.dataset.calMode==='parent')g.dataset.calMode='manual';
   for(const k of ['calGroup','calImageId','calParentOrder','calKnownValue','calGridStep','calPrecision','calGridVisible','calGridSnap'])delete g.dataset[k];
 }
 kbCalibrationClearImageAttrsV39(img);kbRenderAllCalibrationGridsV39();kbUpdateCalibrationPanelV39(img);kbSyncDimCalcUiV39();
 setStatus('Калибровка сброшена. Текущие числовые значения размеров сохранены.');
 try{kbHistorySchedule(0)}catch{}
}
function kbRehydrateCalibrationsV39(){
 kbImagesV39().forEach(kbCalibrationClearImageAttrsV39);
 const groups=new Map();
 for(const g of paper.querySelectorAll('g[data-type="dimension"]')){
   if(g.dataset.calMode!=='parent'||!g.dataset.calGroup)continue;
   if(!groups.has(g.dataset.calGroup))groups.set(g.dataset.calGroup,[]);
   groups.get(g.dataset.calGroup).push(g);
 }
 for(const [group,arr] of groups){
   arr.sort((a,b)=>(+a.dataset.calParentOrder||99)-(+b.dataset.calParentOrder||99));
   const d=kbDimDeltaV39(arr[0]),img=kbFindImageForSegmentV39(d.p1,d.p2,false);if(!img)continue;
   img.dataset.calGroup=group;arr.slice(0,2).forEach((g,i)=>g.dataset.calParentOrder=String(i+1));
   kbSolveCalibrationV39(img,true);
 }
 for(const g of paper.querySelectorAll('g[data-type="dimension"]')){
   if(g.dataset.calMode!=='auto'||!g.dataset.calGroup)continue;
   const img=kbImageByGroupV39(g.dataset.calGroup);if(img){g.dataset.calImageId=img.dataset.id||'';kbUpdateAutoDimensionV39(g,img);kbBaseRenderDimV39(g)}
 }
 kbRenderAllCalibrationGridsV39();kbUpdateCalibrationPanelV39();
}

const kbBaseRenderDimV39=renderDim;
renderDim=function(g){
 if(g?.dataset.type==='dimension'&&!kbCalibrationBusyV39){
   if(g.dataset.calMode==='parent'){
     const img=kbImageByGroupV39(g.dataset.calGroup)||kbImageByRuntimeIdV39(g.dataset.calImageId);
     if(img)kbSolveCalibrationV39(img,true);
   }else if(g.dataset.calMode==='auto')kbUpdateAutoDimensionV39(g);
 }
 return kbBaseRenderDimV39(g);
};

const kbBaseCreateDimV39=createDim;
createDim=function(p1,p2){
 kbBaseCreateDimV39(p1,p2);
 const g=selected;if(!g||g.dataset.type!=='dimension')return;
 const img=kbFindImageForSegmentV39(p1,p2,true);
 if(img?.dataset.calGroup){
   g.dataset.calMode='auto';g.dataset.calGroup=img.dataset.calGroup;g.dataset.calImageId=img.dataset.id||'';
   kbUpdateAutoDimensionV39(g,img);renderDim(g);syncDimProps();kbSyncDimCalcUiV39();
   setStatus('Размер рассчитан автоматически. Введите число вручную — он станет ручным.');
 }
};

const kbBaseSyncDimPropsV39=syncDimProps;
syncDimProps=function(){kbBaseSyncDimPropsV39();kbSyncDimCalcUiV39();kbUpdateCalibrationPanelV39()};

$('dimText').addEventListener('input',()=>{
 const g=selected;if(!g||g.dataset.type!=='dimension')return;
 if(g.dataset.calMode==='auto'){g.dataset.calMode='manual';kbSyncDimCalcUiV39()}
 else if(g.dataset.calMode==='parent'){const n=kbNumV39($('dimText').value);if(n>0)g.dataset.calKnownValue=String(n)}
},true);
$('dimAutoValue').addEventListener('change',()=>{
 const g=selected;if(!g||g.dataset.type!=='dimension')return;
 if(g.dataset.calMode==='parent'){$('dimAutoValue').checked=false;return}
 if($('dimAutoValue').checked){
   const d=kbDimDeltaV39(g),img=kbImageByGroupV39(g.dataset.calGroup)||kbFindImageForSegmentV39(d.p1,d.p2,true);
   if(!img?.dataset.calGroup){$('dimAutoValue').checked=false;setStatus('Для этого изображения сначала нужен эталонный размер');return}
   g.dataset.calMode='auto';g.dataset.calGroup=img.dataset.calGroup;g.dataset.calImageId=img.dataset.id||'';kbUpdateAutoDimensionV39(g,img);renderDim(g);syncDimProps();
 }else g.dataset.calMode='manual';
 kbSyncDimCalcUiV39();try{kbHistorySchedule(0)}catch{}
});
$('dimMakeParent').onclick=kbMakeSelectedParentV39;
$('calibrationClear').onclick=kbClearCalibrationV39;
$('calGridStep').addEventListener('change',()=>{const v=Math.max(.1,kbNumV39($('calGridStep').value)||100);$('calGridStep').value=String(v);kbSetImageSettingV39('calGridStep',v)});
$('calPrecision').addEventListener('change',()=>kbSetImageSettingV39('calPrecision',$('calPrecision').value));
$('calGridVisible').addEventListener('change',()=>kbSetImageSettingV39('calGridVisible',$('calGridVisible').checked?'1':'0'));
$('calGridSnap').addEventListener('change',()=>kbSetImageSettingV39('calGridSnap',$('calGridSnap').checked?'1':'0'));

const kbBasePtV39=pt;
pt=function(e){
 const q=kbBasePtV39(e);if(tool!=='dimension')return q;
 let img=null;if(dimDraft?.p1)img=kbFindImageForSegmentV39(dimDraft.p1,dimDraft.p1,true);
 if(!img)img=kbFindImageForSegmentV39(q,q,true);
 if(!img||img.dataset.calGridSnap!=='1')return q;
 const sx=+img.dataset.calScaleX,sy=+img.dataset.calScaleY,step=Math.max(.1,kbNumV39(img.dataset.calGridStep)||100),gx=step/sx,gy=step/sy;
 const ox=kbNumV39(img.dataset.calOriginX),oy=kbNumV39(img.dataset.calOriginY);
 if(!(gx>0&&gy>0&&Number.isFinite(ox)&&Number.isFinite(oy)))return q;
 return{x:ox+Math.round((q.x-ox)/gx)*gx,y:oy+Math.round((q.y-oy)/gy)*gy};
};

if(typeof kbClearSheetObjects==='function'){
 const kbBaseClearSheetObjectsV39=kbClearSheetObjects;
 kbClearSheetObjects=function(){paper.querySelectorAll('[data-kb-cal-grid-v39]').forEach(n=>n.remove());kbBaseClearSheetObjectsV39()}
}
if(typeof kbLoadSheet==='function'){
 const kbBaseLoadSheetV39=kbLoadSheet;
 kbLoadSheet=function(index){kbBaseLoadSheetV39(index);setTimeout(kbRehydrateCalibrationsV39,0)}
}
if(typeof kbHistorySvg==='function'){
 kbHistorySvg=function(){
  return [...paper.children].filter(n=>
   !n.classList?.contains('selection-ui')&&!n.hasAttribute?.('data-kb-cal-grid-v39')&&n.dataset?.type!=='frame'&&
   n!==dimPreview&&n!==textPreview&&n!==leaderPreview&&n!==simpleLinePreview&&n!==pasteDraft?.ghost
  ).map(n=>n.outerHTML).join('');
 }
}
if(typeof kbHistoryRelevantMutation==='function'){
 const kbBaseHistoryRelevantMutationV39=kbHistoryRelevantMutation;
 kbHistoryRelevantMutation=function(m){
   const n=m.type==='childList'?(m.addedNodes[0]||m.removedNodes[0]||m.target):m.target,node=n?.nodeType===1?n:n?.parentElement;
   if(node?.closest?.('[data-kb-cal-grid-v39]')||node?.hasAttribute?.('data-kb-cal-grid-v39'))return false;
   return kbBaseHistoryRelevantMutationV39(m);
 }
}

const kbBaseSelectV39=select;
select=function(n){kbBaseSelectV39(n);setTimeout(()=>{kbSyncDimCalcUiV39();kbUpdateCalibrationPanelV39()},0)};
const kbBaseClearSelectionV39=clearSelection;
clearSelection=function(){kbBaseClearSelectionV39();setTimeout(()=>kbUpdateCalibrationPanelV39(),0)};

const kbGridObserverV39=new MutationObserver(records=>{
 if(kbGridMutationBusyV39)return;
 let redraw=false,rehydrate=false;
 for(const m of records){
   if(m.type==='attributes'&&m.target?.dataset?.type==='image')redraw=true;
   if(m.type==='childList'){
     for(const n of [...m.addedNodes,...m.removedNodes]){
       if(n?.nodeType!==1)continue;
       if(n.dataset?.type==='image')rehydrate=true;
       if(n.dataset?.type==='dimension'&&n.dataset?.calMode==='parent')rehydrate=true;
     }
   }
 }
 if(rehydrate)setTimeout(kbRehydrateCalibrationsV39,0);else if(redraw)requestAnimationFrame(kbRenderAllCalibrationGridsV39);
});
kbGridObserverV39.observe(paper,{subtree:true,childList:true,attributes:true,attributeFilter:['x','y','width','height']});

setTimeout(()=>{kbRehydrateCalibrationsV39();kbUpdateCalibrationPanelV39()},0);
'''

idx = s.rfind('</script>')
if idx < 0:
    raise SystemExit('v39: closing script tag not found')
s = s[:idx] + js + '\n' + s[idx:]

for token in [
    marker,
    'id="calibrationPanel"',
    'id="dimAutoValue"',
    'id="dimMakeParent"',
    'function kbSolveCalibrationV39(',
    'function kbRenderGridForImageV39(',
    'const kbBaseCreateDimV39=createDim;',
    "g.dataset.calMode='auto'",
    'kbGridObserverV39.observe('
]:
    if token not in s:
        raise SystemExit('v39 guard failed: ' + token)

p.write_text(s, encoding='utf-8', newline='')
print('v39: calibrated measurement grid and automatic dimensions installed')
