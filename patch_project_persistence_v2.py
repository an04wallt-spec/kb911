from pathlib import Path
import re

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')

# Replace v1 object-descriptor snapshots with lossless SVG snapshots.
# Selection UI and generated frame are excluded; the frame is stored separately
# and rebuilt from frameState. Everything drawable (including image data URLs,
# leaders, dimensions, text and future SVG objects) is preserved verbatim.
old = r'''function kbSnapshotSheet(name){
 const objects=[];
 for(const n of [...paper.children]){
   const type=n.dataset?.type;
   if(type==='image')objects.push({type:'image',src:n.getAttribute('href')||'',x:+n.getAttribute('x'),y:+n.getAttribute('y'),w:+n.getAttribute('width'),h:+n.getAttribute('height'),ratio:+n.dataset.ratio||1,opacity:+(n.getAttribute('opacity')||1)});
   else if(['dimension','text','leader'].includes(type))objects.push({type,data:{...n.dataset}});
 }
 return {name:name||'Лист',paperSize:$('paperSize').value,orientation:$('orientation').value,frame:kbClone(frameState),objects};
}'''
new = r'''function kbSnapshotSheet(name){
 document.getElementById('liveTextEditor')?.blur();
 const nodes=[];
 for(const n of [...paper.children]){
   if(n.classList?.contains('selection-ui'))continue;
   if(n.dataset?.type==='frame')continue;
   // Store exact SVG markup. Image href data URLs are embedded in outerHTML,
   // so a project is self-contained and independent of original image files.
   nodes.push(n.outerHTML);
 }
 return {name:name||'Лист',paperSize:$('paperSize').value,orientation:$('orientation').value,frame:kbClone(frameState),svg:nodes.join('')};
}'''
if old not in s:
    raise SystemExit('kbSnapshotSheet v1 block not found')
s=s.replace(old,new,1)

old_load = r'''function kbLoadSheet(index){
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
}'''
new_load = r'''function kbLoadSheet(index){
 if(index<0||index>=kbProject.sheets.length)return;
 const sh=kbProject.sheets[index];kbProject.current=index;kbClearSheetObjects();
 frameState=Object.assign({},kbFrameDefaults,kbClone(sh.frame||{}));
 $('paperSize').value=sh.paperSize||'A3';$('orientation').value=sh.orientation||'landscape';
 $('frameEnabled').checked=!!frameState.enabled;$('frameCompanyEnabled').checked=!!frameState.company;$('frameLogoEnabled').checked=!!frameState.logoEnabled;$('frameCompanyName').value=frameState.name||'';
 try{refreshFrameParamLabels()}catch{}
 setPage();
 if(typeof sh.svg==='string'){
   // Parse through an SVG container so namespaces and image href attributes are
   // restored correctly in WebView2. Delegated event handlers continue to work.
   const temp=document.createElementNS(NS,'svg');temp.innerHTML=sh.svg;
   for(const n of [...temp.children])appendContent(n);
   let maxId=0;paper.querySelectorAll('[data-id]').forEach(n=>{const v=+n.dataset.id||0;if(v>maxId)maxId=v});
   uid=Math.max(uid,maxId+1);
 }else{
   // Backward compatibility with v1 projects already saved by earlier builds.
   for(const o of sh.objects||[]){
     if(o.type==='image'){
       const n=el('image',{href:o.src||'',x:o.x||0,y:o.y||0,width:o.w||10,height:o.h||10,preserveAspectRatio:'none','data-type':'image','data-id':uid++,'data-ratio':String(o.ratio||1),opacity:String(o.opacity??1)});appendContent(n);
     }else if(['dimension','text','leader'].includes(o.type))kbRestoreDatasetGroup(o.type,o.data||{});
   }
 }
 renderFrame();clearSelection();kbUpdateProjectUI();setStatus('Открыт '+(sh.name||kbSheetName(index)));
}'''
if old_load not in s:
    raise SystemExit('kbLoadSheet v1 block not found')
s=s.replace(old_load,new_load,1)

# v2 project packing: do not extract image/logo assets out of the SVG snapshot.
# This deliberately favors lossless reliability over clever deduplication.
pat_pack=r"function kbPackProject\(\)\{.*?\n\}\nfunction kbUnpackProject"
repl_pack=r'''function kbPackProject(){
 kbSyncCurrentSheet();kbProject.name=($('projectName').value||'Проект KB911').trim()||'Проект KB911';
 return {app:'KB911',format:'KB911 Project',version:2,name:kbProject.name,dimDefaults:kbClone(dimDefaults),textDefaults:kbClone(textDefaults),sheets:kbClone(kbProject.sheets)};
}
function kbUnpackProject'''
s,n=re.subn(pat_pack,repl_pack,s,count=1,flags=re.S)
if n!=1:
    raise SystemExit('kbPackProject block not found')

# Replace unpacker while retaining backward compatibility with version 1 assets.
pat_unpack=r"function kbUnpackProject\(data\)\{.*?\n\}\nfunction kbSafeFileName"
repl_unpack=r'''function kbUnpackProject(data){
 if(!data||data.app!=='KB911'||!Array.isArray(data.sheets)||!data.sheets.length)throw new Error('Это не файл проекта KB911');
 const assets=data.assets||{};
 const sheets=data.sheets.map((sh,i)=>{
   const x=kbClone(sh);x.name=x.name||kbSheetName(i);
   // Version 1 compatibility: restore extracted logo/image assets so the old
   // descriptor loader can still open projects saved before v2.
   if(typeof x.svg!=='string'){
     if(x.frame){x.frame.logo=x.frame.logoAsset?assets[x.frame.logoAsset]||null:(x.frame.logo||null);delete x.frame.logoAsset}
     x.objects=(x.objects||[]).map(o=>{const z=kbClone(o);if(z.type==='image'){z.src=z.asset?assets[z.asset]||'':(z.src||'');delete z.asset}return z});
   }
   return x;
 });
 if(data.dimDefaults){dimDefaults=Object.assign({},builtDim,data.dimDefaults);saveStore('mm.dimDefaults.v2',dimDefaults)}
 if(data.textDefaults)textDefaults=Object.assign({},builtText,data.textDefaults);
 return {name:data.name||'Проект KB911',sheets,current:0};
}
function kbSafeFileName'''
s,n=re.subn(pat_unpack,repl_unpack,s,count=1,flags=re.S)
if n!=1:
    raise SystemExit('kbUnpackProject block not found')

p.write_text(s,encoding='utf-8',newline='')
print('Lossless KB911 project persistence v2 applied')
