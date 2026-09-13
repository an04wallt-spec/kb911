from pathlib import Path
import re

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V39_REFERENCE_ORIGIN'
if marker in s:
    print('v39 reference origin already applied')
    raise SystemExit(0)

# Defaults: an older calibrated v39 document without explicit origin falls back
# to the image top-left. New calibrations overwrite these with the reference point.
old=""" const r=imageRect(img);
 if(!img.dataset.calImageW)img.dataset.calImageW=String(r.w);
 if(!img.dataset.calImageH)img.dataset.calImageH=String(r.h);"""
new=""" const r=imageRect(img);
 if(!img.dataset.calImageW)img.dataset.calImageW=String(r.w);
 if(!img.dataset.calImageH)img.dataset.calImageH=String(r.h);
 if(!Number.isFinite(kbMeasureNumV39(img.dataset.calOriginX)))img.dataset.calOriginX=String(r.x);
 if(!Number.isFinite(kbMeasureNumV39(img.dataset.calOriginY)))img.dataset.calOriginY=String(r.y);"""
if s.count(old)!=1: raise SystemExit(f'origin v39: defaults anchor count {s.count(old)}')
s=s.replace(old,new,1)

# Recomputing a parent also keeps the coordinate origin attached to its first point.
s=s.replace("img.dataset.calBaseId=String(g.dataset.id);\n }else if(role==='x')", "img.dataset.calBaseId=String(g.dataset.id);img.dataset.calOriginX=String(a.x);img.dataset.calOriginY=String(a.y);\n }else if(role==='x')",1)
s=s.replace("img.dataset.calScaleX=String(known/dx);img.dataset.calXId=String(g.dataset.id);", "img.dataset.calScaleX=String(known/dx);img.dataset.calXId=String(g.dataset.id);img.dataset.calOriginX=String(a.x);",1)
s=s.replace("img.dataset.calScaleY=String(known/dy);img.dataset.calYId=String(g.dataset.id);", "img.dataset.calScaleY=String(known/dy);img.dataset.calYId=String(g.dataset.id);img.dataset.calOriginY=String(a.y);",1)

# Initial assignment path uses the same origin semantics.
s=s.replace("img.dataset.calScaleX=String(sc);img.dataset.calScaleY=String(sc);img.dataset.calBaseId=String(g.dataset.id)", "img.dataset.calScaleX=String(sc);img.dataset.calScaleY=String(sc);img.dataset.calBaseId=String(g.dataset.id);img.dataset.calOriginX=String(a.x);img.dataset.calOriginY=String(a.y)",1)
s=s.replace("img.dataset.calScaleX=String(known/Math.abs(b.x-a.x));img.dataset.calXId=String(g.dataset.id);", "img.dataset.calScaleX=String(known/Math.abs(b.x-a.x));img.dataset.calXId=String(g.dataset.id);img.dataset.calOriginX=String(a.x);",1)
s=s.replace("img.dataset.calScaleY=String(known/Math.abs(b.y-a.y));img.dataset.calYId=String(g.dataset.id);", "img.dataset.calScaleY=String(known/Math.abs(b.y-a.y));img.dataset.calYId=String(g.dataset.id);img.dataset.calOriginY=String(a.y);",1)

# Replace grid renderer: lines extend both ways from the reference origin. Major
# lines are counted from that origin, so snapping and what the user sees coincide.
pat=r"function kbMeasureRenderGridV39\(\)\{.*?\n\}\nfunction kbMeasureSnapPointV39"
repl=r'''function kbMeasureRenderGridV39(){
 const o=kbMeasureGridOverlayV39();o.setAttribute('viewBox',`0 0 ${page.w} ${page.h}`);while(o.firstChild)o.removeChild(o.firstChild);
 for(const img of kbMeasureImagesV39()){
  if(!kbMeasureHasCalibrationV39(img)||img.dataset.measureGridShow==='0')continue;
  kbMeasureImageDefaultsV39(img);
  const r=imageRect(img),sx=kbMeasureNumV39(img.dataset.calScaleX),sy=kbMeasureNumV39(img.dataset.calScaleY),step=Math.max(.1,kbMeasureNumV39(img.dataset.measureGridStep)||10),dx=step/sx,dy=step/sy;
  const ox=kbMeasureNumV39(img.dataset.calOriginX),oy=kbMeasureNumV39(img.dataset.calOriginY);
  if(!(dx>0&&dy>0&&Number.isFinite(ox)&&Number.isFinite(oy)))continue;
  const ix0=Math.ceil((r.x-ox)/dx),ix1=Math.floor((r.x+r.w-ox)/dx),iy0=Math.ceil((r.y-oy)/dy),iy1=Math.floor((r.y+r.h-oy)/dy);
  if(ix1-ix0>1200||iy1-iy0>1200)continue;
  const g=el('g',{'data-grid-image':img.dataset.id,'data-grid-origin-v39':'KB911_V39_REFERENCE_ORIGIN'});
  for(let i=ix0;i<=ix1;i++){const x=ox+i*dx,major=((i%10)+10)%10===0;g.appendChild(el('line',{x1:x,y1:r.y,x2:x,y2:r.y+r.h,stroke:major?'#3978c5':'#6f9fd6','stroke-width':major?'.24':'.11',opacity:major?'.48':'.28','vector-effect':'non-scaling-stroke'}))}
  for(let i=iy0;i<=iy1;i++){const y=oy+i*dy,major=((i%10)+10)%10===0;g.appendChild(el('line',{x1:r.x,y1:y,x2:r.x+r.w,y2:y,stroke:major?'#3978c5':'#6f9fd6','stroke-width':major?'.24':'.11',opacity:major?'.48':'.28','vector-effect':'non-scaling-stroke'}))}
  g.appendChild(el('rect',{x:r.x,y:r.y,width:r.w,height:r.h,fill:'none',stroke:'#3978c5','stroke-width':'.25',opacity:'.55','stroke-dasharray':'2 1','vector-effect':'non-scaling-stroke'}));
  o.appendChild(g);
 }
}
function kbMeasureSnapPointV39'''
s,n=re.subn(pat,repl,s,count=1,flags=re.S)
if n!=1: raise SystemExit(f'origin v39: grid renderer matched {n}')

old_snap=""" const sx=kbMeasureNumV39(img.dataset.calScaleX),sy=kbMeasureNumV39(img.dataset.calScaleY),step=Math.max(.1,kbMeasureNumV39(img.dataset.measureGridStep)||10),r=imageRect(img);
 return{x:r.x+Math.round((p.x-r.x)*sx/step)*step/sx,y:r.y+Math.round((p.y-r.y)*sy/step)*step/sy};"""
new_snap=""" const sx=kbMeasureNumV39(img.dataset.calScaleX),sy=kbMeasureNumV39(img.dataset.calScaleY),step=Math.max(.1,kbMeasureNumV39(img.dataset.measureGridStep)||10);
 const ox=kbMeasureNumV39(img.dataset.calOriginX),oy=kbMeasureNumV39(img.dataset.calOriginY);
 if(!Number.isFinite(ox)||!Number.isFinite(oy))return p;
 return{x:ox+Math.round((p.x-ox)*sx/step)*step/sx,y:oy+Math.round((p.y-oy)*sy/step)*step/sy};"""
if s.count(old_snap)!=1: raise SystemExit(f'origin v39: snap anchor count {s.count(old_snap)}')
s=s.replace(old_snap,new_snap,1)

# Reset must remove the coordinate origin together with scale.
old_clear="['calScaleX','calScaleY','calBaseId','calXId','calYId','calImageW','calImageH']"
new_clear="['calScaleX','calScaleY','calBaseId','calXId','calYId','calImageW','calImageH','calOriginX','calOriginY']"
if s.count(old_clear)!=1: raise SystemExit(f'origin v39: reset anchor count {s.count(old_clear)}')
s=s.replace(old_clear,new_clear,1)

for token in [marker,'data-grid-origin-v39', 'calOriginX', 'calOriginY', 'Math.ceil((r.x-ox)/dx)', 'x:ox+Math.round((p.x-ox)*sx/step)*step/sx']:
    if token not in s: raise SystemExit('origin v39 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v39: measurement grid and snapping anchored to the calibration reference origin')
