from pathlib import Path
p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='// KB911_V13_LEADER_EXPORT_REPAIR'
if marker in s:
    print('v13 already applied'); raise SystemExit(0)
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end not found')
code=r'''

// KB911_V13_LEADER_EXPORT_REPAIR
// Leader editing uses its own handle class/state so it cannot conflict with the
// older leader runtime. Handles are redrawn only after pointer-up; this avoids
// removing the active SVG handle while it is being dragged.
function kbLeaderTextPoint(g){
 const q=leaderPts(g),fs=+g.dataset.fontSize||4;
 const def={x:(q.p2.x+q.p3.x)/2,y:q.p2.y-fs*.85};
 return {x:Number.isFinite(+g.dataset.textX)?+g.dataset.textX:def.x,
         y:Number.isFinite(+g.dataset.textY)?+g.dataset.textY:def.y};
}
renderLeader=function(g){
 while(g.firstChild)g.removeChild(g.firstChild);
 const {p1,p2,p3}=leaderPts(g),c=g.dataset.lineColor||dimDefaults.lineColor||'#111111',lw=+(g.dataset.lineWidth||dimDefaults.lineWidth||.4),as=+(g.dataset.arrowSize||dimDefaults.arrowSize||5),aa=+(g.dataset.arrowAngle||dimDefaults.arrowAngle||10),sty=g.dataset.arrow||dimDefaults.arrow||'slim';
 g.appendChild(el('line',{x1:p1.x,y1:p1.y,x2:p2.x,y2:p2.y,stroke:c,'stroke-width':lw,'vector-effect':'non-scaling-stroke'}));
 g.appendChild(el('line',{x1:p2.x,y1:p2.y,x2:p3.x,y2:p3.y,stroke:c,'stroke-width':lw,'vector-effect':'non-scaling-stroke'}));
 const len=Math.hypot(p2.x-p1.x,p2.y-p1.y)||1,ux=(p2.x-p1.x)/len,uy=(p2.y-p1.y)/len;
 drawArrow(g,p1,ux,uy,as,aa,c,lw,1,sty);
 const fs=+g.dataset.fontSize||4,tp=kbLeaderTextPoint(g),t=el('text',{x:tp.x,y:tp.y,'text-anchor':'middle','dominant-baseline':'central','font-family':g.dataset.font||'Bahnschrift','font-size':fs,'font-weight':g.dataset.bold==='1'?'700':'400','font-style':g.dataset.italic==='1'?'italic':'normal',fill:g.dataset.textColor||c});
 t.textContent=g.dataset.value||'Сноска';g.appendChild(t);
 g.appendChild(el('path',{d:`M ${p1.x} ${p1.y} L ${p2.x} ${p2.y} L ${p3.x} ${p3.y}`,fill:'none',stroke:'transparent','stroke-width':8,class:'leader-hit hover-movable'}));
};
drawLeaderHandles=function(g){
 if(!g||g.dataset.type!=='leader')return;
 const {p1,p2,p3}=leaderPts(g),tp=kbLeaderTextPoint(g);
 [[p1,'p1'],[p2,'p2'],[p3,'p3']].forEach(([p,k])=>paper.appendChild(el('circle',{cx:p.x,cy:p.y,r:1.05,class:'handle selection-ui kb-leader-edit-handle','data-owner':g.dataset.id,'data-kb-leader-handle':k,style:'cursor:crosshair'})));
 paper.appendChild(el('rect',{x:tp.x-1.35,y:tp.y-1.35,width:2.7,height:2.7,rx:.45,ry:.45,class:'handle selection-ui kb-leader-edit-handle','data-owner':g.dataset.id,'data-kb-leader-handle':'text',style:'cursor:move'}));
};
let kbLeaderEdit=null,kbLeaderPopupDrag=null;
paper.addEventListener('pointerdown',e=>{
 const h=e.target.closest?.('.kb-leader-edit-handle');if(!h)return;
 const g=findOwner(h.dataset.owner,'leader');if(!g)return;
 const p=pt(e),kind=h.dataset.kbLeaderHandle;
 selected=g;lastEditable=g;
 kbLeaderEdit={obj:g,kind,start:p,p1:parsePt(g.dataset.p1),p2:parsePt(g.dataset.p2),shelf:+g.dataset.shelf||40,text:kbLeaderTextPoint(g)};
 e.preventDefault();e.stopImmediatePropagation();
},true);
window.addEventListener('pointermove',e=>{
 if(!kbLeaderEdit)return;
 const p=pt(e),d=kbLeaderEdit,g=d.obj;
 if(d.kind==='p1')g.dataset.p1=`${p.x},${p.y}`;
 else if(d.kind==='p2'){
   const dx=p.x-d.p2.x,dy=p.y-d.p2.y;
   g.dataset.p2=`${p.x},${p.y}`;
   if(Number.isFinite(+g.dataset.textX)){g.dataset.textX=String(d.text.x+dx);g.dataset.textY=String(d.text.y+dy)}
 }
 else if(d.kind==='p3'){
   const p2=parsePt(g.dataset.p2);g.dataset.dir=p.x>=p2.x?'1':'-1';g.dataset.shelf=String(Math.max(8,Math.abs(p.x-p2.x)));
 }
 else if(d.kind==='text'){g.dataset.textX=String(p.x);g.dataset.textY=String(p.y)}
 renderLeader(g);e.preventDefault();e.stopPropagation();
},true);
window.addEventListener('pointerup',e=>{
 if(!kbLeaderEdit)return;
 kbLeaderEdit=null;drawSelection();e.preventDefault();e.stopPropagation();
},true);

// Make the leader properties window draggable just like dimension/text windows.
$('leaderPopup').addEventListener('pointerdown',e=>e.stopPropagation());
$('leaderPopupHeader').addEventListener('pointerdown',e=>{
 if(e.target.id==='leaderPopupClose')return;
 const q=$('leaderPopup'),r=q.getBoundingClientRect();
 kbLeaderPopupDrag={dx:e.clientX-r.left,dy:e.clientY-r.top};
 e.preventDefault();e.stopPropagation();
});
window.addEventListener('pointermove',e=>{
 if(!kbLeaderPopupDrag)return;
 const q=$('leaderPopup');
 q.style.left=Math.max(0,Math.min(innerWidth-q.offsetWidth,e.clientX-kbLeaderPopupDrag.dx))+'px';
 q.style.top=Math.max(0,Math.min(innerHeight-q.offsetHeight,e.clientY-kbLeaderPopupDrag.dy))+'px';
},true);
window.addEventListener('pointerup',()=>{kbLeaderPopupDrag=null},true);

// Export from an exact SVG snapshot instead of manually reconstructing objects.
async function kbSvgSnapshotImage(){
 document.getElementById('liveTextEditor')?.blur();
 const clone=paper.cloneNode(true);clone.querySelectorAll('.selection-ui').forEach(n=>n.remove());
 clone.setAttribute('xmlns',NS);clone.setAttribute('viewBox',`0 0 ${page.w} ${page.h}`);clone.setAttribute('width',String(page.w));clone.setAttribute('height',String(page.h));
 const bg=document.createElementNS(NS,'rect');bg.setAttribute('x','0');bg.setAttribute('y','0');bg.setAttribute('width',String(page.w));bg.setAttribute('height',String(page.h));bg.setAttribute('fill','#fff');clone.insertBefore(bg,clone.firstChild);
 const xml=new XMLSerializer().serializeToString(clone),url=URL.createObjectURL(new Blob([xml],{type:'image/svg+xml;charset=utf-8'}));
 try{const im=await loadCanvasImage(url);return{im,url}}catch(e){URL.revokeObjectURL(url);throw e}
}
async function kbRenderCurrentSheetCanvasV13(dpi){
 commitEditorsForExport();if(typeof kbSyncCurrentSheet==='function')kbSyncCurrentSheet();
 const pxW=Math.max(1,Math.round(page.w/25.4*dpi)),pxH=Math.max(1,Math.round(page.h/25.4*dpi));
 const c=document.createElement('canvas');c.width=pxW;c.height=pxH;const ctx=c.getContext('2d',{alpha:false});if(!ctx)throw new Error('Canvas недоступен');
 const snap=await kbSvgSnapshotImage();try{ctx.fillStyle='#fff';ctx.fillRect(0,0,pxW,pxH);ctx.drawImage(snap.im,0,0,pxW,pxH)}finally{URL.revokeObjectURL(snap.url)}return c;
}
renderSheetCanvas=kbRenderCurrentSheetCanvasV13;
async function kbRenderPageTilesV13(dpi,pageNo,pageCount){
 const sx=dpi/25.4,totalW=Math.max(1,Math.round(page.w*sx)),totalH=Math.max(1,Math.round(page.h*sx)),tileMax=4096,tiles=[],nx=Math.ceil(totalW/tileMax),ny=Math.ceil(totalH/tileMax),totalTiles=nx*ny;
 const snap=await kbSvgSnapshotImage();let ti=0;
 try{
   for(let y=0;y<totalH;y+=tileMax)for(let x=0;x<totalW;x+=tileMax){ti++;setStatus(`PDF: лист ${pageNo}/${pageCount}, блок ${ti}/${totalTiles}`);const w=Math.min(tileMax,totalW-x),h=Math.min(tileMax,totalH-y),c=document.createElement('canvas');c.width=w;c.height=h;const ctx=c.getContext('2d',{alpha:false});if(!ctx)throw new Error('Canvas недоступен');ctx.fillStyle='#fff';ctx.fillRect(0,0,w,h);ctx.drawImage(snap.im,-x,-y,totalW,totalH);const blob=await canvasToBlob(c,'image/jpeg',.94),bytes=new Uint8Array(await blob.arrayBuffer());tiles.push({x,y,w,h,bytes});c.width=1;c.height=1;await new Promise(r=>setTimeout(r,0))}
 }finally{URL.revokeObjectURL(snap.url)}
 return{wMm:page.w,hMm:page.h,totalW,totalH,tiles};
}
kbRenderPageTiles=kbRenderPageTilesV13;
'''
s=s[:idx]+code+s[idx:]
for token in ['KB911_V13_LEADER_EXPORT_REPAIR','kb-leader-edit-handle','kbLeaderPopupDrag','kbRenderCurrentSheetCanvasV13','kbRenderPageTilesV13']:
    if token not in s: raise SystemExit('v13 token missing '+token)
p.write_text(s,encoding='utf-8',newline='')
print('v13 leader editing/export repair applied safely')
