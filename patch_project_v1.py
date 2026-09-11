from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')

def rep(a,b,n=1):
    global s
    if a not in s:
        raise SystemExit('patch_project_v1 missing fragment: '+a[:140])
    s=s.replace(a,b,n)

# Layer terminology is universal for all drawable objects.
rep('<button data-layer="front">Поверх других картинок</button>\n  <button data-layer="back">Под другими картинками</button>',
    '<button data-layer="front">На передний план</button>\n  <button data-layer="back">На задний план</button>')

# Multi-sheet project panel. Keep it separate from export and frame modules.
project_panel='''  <div class="group" id="projectPanel">\n    <b>Проект KB911</b>\n    <div class="hint" style="margin-bottom:8px">Один файл проекта может содержать несколько листов.</div>\n    <div class="label">Название проекта</div>\n    <input id="projectName" type="text" value="Проект KB911" style="width:100%;margin-bottom:7px">\n    <div class="label">Текущий лист</div>\n    <select id="projectSheet" style="width:100%;margin-bottom:6px"></select>\n    <input id="projectSheetName" type="text" value="Лист 1" style="width:100%;margin-bottom:6px">\n    <div class="project-row">\n      <button id="projectSheetAdd">+ Лист</button><button id="projectSheetDup">Дублировать</button><button id="projectSheetDel" class="mini" title="Удалить лист">×</button>\n    </div>\n    <button id="projectOpen" style="width:100%;margin-top:8px">Открыть проект .KB911</button>\n    <button id="projectSaveAs" class="primary" style="width:100%;margin-top:6px">Сохранить как .KB911</button>\n    <input id="projectFile" type="file" accept=".kb911,application/json" hidden>\n  </div>\n'''
rep('  <div class="group" id="savePanel">', project_panel+'  <div class="group" id="savePanel">')

# Compact styling for sheet controls.
rep('@media print{', '#projectPanel .project-row{display:flex;gap:6px}#projectPanel .project-row button{flex:1}#projectPanel .project-row .mini{flex:0 0 34px}\n@media print{')

# Add generic layer management and project model before the final setPage().
anchor='setPage();\n})();'
code=r'''
// ---------- Universal object layering ----------
let kbLayerTarget=null;
function kbDrawableObject(target){const o=groupType(target);return o&&['image','dimension','text','leader'].includes(o.dataset?.type)?o:null}
function kbMoveLayer(obj,where){
 if(!obj||!obj.isConnected)return;
 clearUI();
 const content=[...paper.children].filter(n=>n!==obj&&['image','dimension','text','leader'].includes(n.dataset?.type));
 if(where==='front'){
   const frame=paper.querySelector('[data-type="frame"]');
   if(frame)paper.insertBefore(obj,frame);else paper.appendChild(obj);
   setStatus('Объект перенесён на передний план');
 }else{
   if(content.length)paper.insertBefore(obj,content[0]);
   setStatus('Объект перенесён на задний план');
 }
 selected=obj;drawSelection();
}
paper.addEventListener('contextmenu',e=>{
 const obj=kbDrawableObject(e.target);if(!obj)return;
 e.preventDefault();e.stopImmediatePropagation();kbLayerTarget=obj;selected=obj;clearUI();drawSelection();
 const m=$('imageContextMenu');m.classList.add('open');m.setAttribute('aria-hidden','false');
 const w=205,h=76;m.style.left=Math.min(e.clientX,innerWidth-w-6)+'px';m.style.top=Math.min(e.clientY,innerHeight-h-6)+'px';
},true);
$('imageContextMenu').addEventListener('click',e=>{
 const b=e.target.closest('button[data-layer]');if(!b||!kbLayerTarget)return;
 e.preventDefault();e.stopImmediatePropagation();kbMoveLayer(kbLayerTarget,b.dataset.layer);closeImageMenu();kbLayerTarget=null;
},true);

// ---------- Native KB911 project format ----------
let kbProject={name:'Проект KB911',sheets:[],current:0};
const kbFrameDefaults={enabled:false,company:true,logoEnabled:false,name:'',logo:null,stroke:.3,inset:5};
function kbClone(v){return JSON.parse(JSON.stringify(v))}
function kbSheetName(i){return 'Лист '+(i+1)}
function kbSnapshotSheet(name){
 const objects=[];
 for(const n of [...paper.children]){
   const type=n.dataset?.type;
   if(type==='image')objects.push({type:'image',src:n.getAttribute('href')||'',x:+n.getAttribute('x'),y:+n.getAttribute('y'),w:+n.getAttribute('width'),h:+n.getAttribute('height'),ratio:+n.dataset.ratio||1,opacity:+(n.getAttribute('opacity')||1)});
   else if(['dimension','text','leader'].includes(type))objects.push({type,data:{...n.dataset}});
 }
 return {name:name||'Лист',paperSize:$('paperSize').value,orientation:$('orientation').value,frame:kbClone(frameState),objects};
}
function kbSyncCurrentSheet(){
 if(!kbProject.sheets.length)return;
 const name=($('projectSheetName')?.value||kbProject.sheets[kbProject.current]?.name||kbSheetName(kbProject.current)).trim()||kbSheetName(kbProject.current);
 kbProject.sheets[kbProject.current]=kbSnapshotSheet(name);
}
function kbUpdateProjectUI(){
 $('projectName').value=kbProject.name||'Проект KB911';
 const sel=$('projectSheet');sel.innerHTML='';
 kbProject.sheets.forEach((sh,i)=>{const o=document.createElement('option');o.value=i;o.textContent=sh.name||kbSheetName(i);sel.appendChild(o)});
 sel.value=String(kbProject.current);
 $('projectSheetName').value=kbProject.sheets[kbProject.current]?.name||kbSheetName(kbProject.current);
}
function kbClearSheetObjects(){
 clearSelection();activeImage=null;tool=null;closeDimPopup();closeTextPopup();try{closeLeaderPopup()}catch{}
 paper.querySelectorAll('[data-type="image"],[data-type="dimension"],[data-type="text"],[data-type="leader"],[data-type="frame"]').forEach(n=>n.remove());
}
function kbRestoreDatasetGroup(type,data){
 let g;
 if(type==='dimension')g=cloneDimFromData(data);
 else if(type==='text')g=cloneTextFromData(data);
 else {g=el('g',{'data-type':'leader','data-id':uid++});for(const[k,v]of Object.entries(data||{})){if(!['type','id'].includes(k))g.dataset[k]=v}}
 appendContent(g);if(type==='dimension')renderDim(g);else if(type==='text')renderText(g);else renderLeader(g);
}
function kbLoadSheet(index){
 if(index<0||index>=kbProject.sheets.length)return;
 const sh=kbProject.sheets[index];kbProject.current=index;kbClearSheetObjects();
 frameState=Object.assign({},kbFrameDefaults,kbClone(sh.frame||{}));
 $('paperSize').value=sh.paperSize||'A3';$('orientation').value=sh.orientation||'landscape';
 $('frameEnabled').checked=!!frameState.enabled;$('frameCompanyEnabled').checked=!!frameState.company;$('frameLogoEnabled').checked=!!frameState.logoEnabled;$('frameCompanyName').value=frameState.name||'';
 try{refreshFrameParamLabels()}catch{}
 setPage();
 for(const o of sh.objects||[]){
   if(o.type==='image'){
     const n=el('image',{href:o.src||'',x:o.x||0,y:o.y||0,width:o.w||10,height:o.h||10,preserveAspectRatio:'none','data-type':'image','data-id':uid++,'data-ratio':String(o.ratio||1),opacity:String(o.opacity??1)});appendContent(n);
   }else if(['dimension','text','leader'].includes(o.type))kbRestoreDatasetGroup(o.type,o.data||{});
 }
 renderFrame();clearSelection();kbUpdateProjectUI();setStatus('Открыт '+(sh.name||kbSheetName(index)));
}
function kbNewBlankSheet(){
 kbSyncCurrentSheet();const cur=kbProject.sheets[kbProject.current]||kbSnapshotSheet('Лист 1');
 const sh={name:kbSheetName(kbProject.sheets.length),paperSize:cur.paperSize||'A3',orientation:cur.orientation||'landscape',frame:kbClone(cur.frame||kbFrameDefaults),objects:[]};
 kbProject.sheets.push(sh);kbLoadSheet(kbProject.sheets.length-1);
}
function kbDuplicateSheet(){
 kbSyncCurrentSheet();const sh=kbClone(kbProject.sheets[kbProject.current]);sh.name=(sh.name||kbSheetName(kbProject.current))+' — копия';kbProject.sheets.splice(kbProject.current+1,0,sh);kbLoadSheet(kbProject.current+1);
}
function kbDeleteSheet(){
 if(kbProject.sheets.length<=1){setStatus('В проекте должен остаться хотя бы один лист');return}
 const name=kbProject.sheets[kbProject.current]?.name||'лист';if(!confirm('Удалить «'+name+'» из проекта?'))return;
 kbProject.sheets.splice(kbProject.current,1);kbProject.current=Math.min(kbProject.current,kbProject.sheets.length-1);kbLoadSheet(kbProject.current);
}
function kbPackProject(){
 kbSyncCurrentSheet();kbProject.name=($('projectName').value||'Проект KB911').trim()||'Проект KB911';
 const assets={},assetByData=new Map();let ai=1;
 const putAsset=data=>{if(!data)return null;if(assetByData.has(data))return assetByData.get(data);const id='asset'+ai++;assetByData.set(data,id);assets[id]=data;return id};
 const sheets=kbProject.sheets.map(sh=>{
   const x=kbClone(sh),logo=x.frame?.logo||null;if(x.frame){x.frame.logoAsset=putAsset(logo);delete x.frame.logo}
   x.objects=(x.objects||[]).map(o=>{const z=kbClone(o);if(z.type==='image'){z.asset=putAsset(z.src);delete z.src}return z});return x;
 });
 return {app:'KB911',format:'KB911 Project',version:1,name:kbProject.name,assets,dimDefaults:kbClone(dimDefaults),textDefaults:kbClone(textDefaults),sheets};
}
function kbUnpackProject(data){
 if(!data||data.app!=='KB911'||!Array.isArray(data.sheets)||!data.sheets.length)throw new Error('Это не файл проекта KB911');
 const assets=data.assets||{};
 const sheets=data.sheets.map((sh,i)=>{const x=kbClone(sh);x.name=x.name||kbSheetName(i);if(x.frame){x.frame.logo=x.frame.logoAsset?assets[x.frame.logoAsset]||null:(x.frame.logo||null);delete x.frame.logoAsset}x.objects=(x.objects||[]).map(o=>{const z=kbClone(o);if(z.type==='image'){z.src=z.asset?assets[z.asset]||'':(z.src||'');delete z.asset}return z});return x});
 if(data.dimDefaults){dimDefaults=Object.assign({},builtDim,data.dimDefaults);saveStore('mm.dimDefaults.v2',dimDefaults)}
 if(data.textDefaults)textDefaults=Object.assign({},builtText,data.textDefaults);
 return {name:data.name||'Проект KB911',sheets,current:0};
}
function kbSafeFileName(s){return(String(s||'Проект KB911').trim().replace(/[\\/:*?"<>|]+/g,'_')||'Проект KB911')+'.kb911'}
async function kbSaveProjectAs(){
 const packed=kbPackProject(),name=kbSafeFileName(packed.name),blob=new Blob([JSON.stringify(packed)],{type:'application/json'});let handle=null;
 if(window.showSaveFilePicker){try{handle=await window.showSaveFilePicker({id:'kb911-project',suggestedName:name,types:[{description:'Проект KB911',accept:{'application/json':['.kb911']}}]})}catch(e){if(e?.name==='AbortError'){setStatus('Сохранение проекта отменено');return};console.error(e)}}
 if(handle){const w=await handle.createWritable();await w.write(blob);await w.close();setStatus('Проект сохранён: '+(handle.name||name))}else{downloadBlob(blob,name);setStatus('Проект сохранён: '+name)}
}
async function kbReadProjectFile(file){
 const txt=await file.text(),data=JSON.parse(txt);kbProject=kbUnpackProject(data);kbLoadSheet(0);setStatus('Проект открыт: '+(file.name||kbProject.name));
}
async function kbOpenProject(){
 if(window.showOpenFilePicker){try{const[h]=await window.showOpenFilePicker({id:'kb911-project-open',multiple:false,types:[{description:'Проект KB911',accept:{'application/json':['.kb911']}}]});if(h){await kbReadProjectFile(await h.getFile());return}}catch(e){if(e?.name==='AbortError')return;console.error(e)}}
 $('projectFile').click();
}
function initKB911Project(){
 kbProject={name:'Проект KB911',sheets:[kbSnapshotSheet('Лист 1')],current:0};kbUpdateProjectUI();
 $('projectName').addEventListener('input',()=>{kbProject.name=$('projectName').value});
 $('projectSheetName').addEventListener('input',()=>{const n=$('projectSheetName').value||kbSheetName(kbProject.current);kbProject.sheets[kbProject.current].name=n;const o=$('projectSheet').options[kbProject.current];if(o)o.textContent=n});
 $('projectSheet').addEventListener('change',e=>{const next=+e.target.value;if(next===kbProject.current)return;kbSyncCurrentSheet();kbLoadSheet(next)});
 $('projectSheetAdd').onclick=kbNewBlankSheet;$('projectSheetDup').onclick=kbDuplicateSheet;$('projectSheetDel').onclick=kbDeleteSheet;
 $('projectSaveAs').onclick=()=>kbSaveProjectAs().catch(e=>{console.error(e);alert('Не удалось сохранить проект: '+(e?.message||e))});
 $('projectOpen').onclick=()=>kbOpenProject().catch(e=>{console.error(e);alert('Не удалось открыть проект: '+(e?.message||e))});
 $('projectFile').onchange=e=>{const f=e.target.files?.[0];if(f)kbReadProjectFile(f).catch(err=>alert('Не удалось открыть проект: '+(err?.message||err)));e.target.value=''};
}

setPage();
initKB911Project();
})();'''
rep(anchor,code)

p.write_text(s,encoding='utf-8',newline='')
print('Universal layers and KB911 multi-sheet projects applied')
