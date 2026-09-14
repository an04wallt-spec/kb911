from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V46_LOSSLESS_PDF_LINEWORK'
if marker in s:
    print('v46 already applied')
    raise SystemExit(0)

old="""async function kbRenderPageTiles(dpi,pageNo,pageCount){const sx=dpi/25.4,totalW=Math.max(1,Math.round(page.w*sx)),totalH=Math.max(1,Math.round(page.h*sx)),tileMax=4096,cache=await kbPageImageCache(),tiles=[],nx=Math.ceil(totalW/tileMax),ny=Math.ceil(totalH/tileMax),totalTiles=nx*ny;let ti=0;for(let y=0;y<totalH;y+=tileMax){for(let x=0;x<totalW;x+=tileMax){ti++;setStatus(`PDF: лист ${pageNo}/${pageCount}, фрагмент ${ti}/${totalTiles}`);const w=Math.min(tileMax,totalW-x),h=Math.min(tileMax,totalH-y),c=document.createElement('canvas');c.width=w;c.height=h;const ctx=c.getContext('2d',{alpha:false});if(!ctx)throw new Error('Canvas недоступен');ctx.fillStyle='#fff';ctx.fillRect(0,0,w,h);ctx.save();ctx.scale(sx,sx);ctx.translate(-x/sx,-y/sx);await kbDrawSheetToContext(ctx,cache);ctx.restore();const blob=await canvasToBlob(c,'image/jpeg',.94),bytes=new Uint8Array(await blob.arrayBuffer());tiles.push({x,y,w,h,bytes});c.width=1;c.height=1;await new Promise(r=>setTimeout(r,0))}}return{wMm:page.w,hMm:page.h,totalW,totalH,tiles}}"""

if old not in s:
    raise SystemExit('v46: PDF tile renderer anchor not found')

new="""// KB911_V46_LOSSLESS_PDF_LINEWORK
async function kbPdfRgbTileV46(ctx,w,h){
 const rgba=ctx.getImageData(0,0,w,h).data,rgb=new Uint8Array(w*h*3);
 for(let i=0,j=0;i<rgba.length;i+=4){rgb[j++]=rgba[i];rgb[j++]=rgba[i+1];rgb[j++]=rgba[i+2]}
 if(typeof CompressionStream==='function'){
  const cs=new CompressionStream('deflate'),stream=new Blob([rgb]).stream().pipeThrough(cs),ab=await new Response(stream).arrayBuffer();
  return{bytes:new Uint8Array(ab),flate:true};
 }
 return{bytes:rgb,flate:false};
}
async function kbRenderPageTiles(dpi,pageNo,pageCount){const sx=dpi/25.4,totalW=Math.max(1,Math.round(page.w*sx)),totalH=Math.max(1,Math.round(page.h*sx)),tileMax=2048,cache=await kbPageImageCache(),tiles=[],nx=Math.ceil(totalW/tileMax),ny=Math.ceil(totalH/tileMax),totalTiles=nx*ny;let ti=0;for(let y=0;y<totalH;y+=tileMax){for(let x=0;x<totalW;x+=tileMax){ti++;setStatus(`PDF: лист ${pageNo}/${pageCount}, фрагмент ${ti}/${totalTiles}`);const w=Math.min(tileMax,totalW-x),h=Math.min(tileMax,totalH-y),c=document.createElement('canvas');c.width=w;c.height=h;const ctx=c.getContext('2d',{alpha:false,willReadFrequently:true});if(!ctx)throw new Error('Canvas недоступен');ctx.fillStyle='#fff';ctx.fillRect(0,0,w,h);ctx.save();ctx.scale(sx,sx);ctx.translate(-x/sx,-y/sx);await kbDrawSheetToContext(ctx,cache);ctx.restore();const enc=await kbPdfRgbTileV46(ctx,w,h);tiles.push({x,y,w,h,bytes:enc.bytes,flate:enc.flate});c.width=1;c.height=1;await new Promise(r=>setTimeout(r,0))}}return{wMm:page.w,hMm:page.h,totalW,totalH,tiles}}"""
s=s.replace(old,new,1)

old_obj="""p.tiles.forEach((t,i)=>{objs[r.imageIds[i]]=concatBytes([asciiBytes(`<< /Type /XObject /Subtype /Image /Width ${t.w} /Height ${t.h} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${t.bytes.length} >>\\nstream\\n`),t.bytes,asciiBytes('\\nendstream')])})"""
if old_obj not in s:
    raise SystemExit('v46: PDF image object anchor not found')
new_obj="""p.tiles.forEach((t,i)=>{const filter=t.flate?' /Filter /FlateDecode':'';objs[r.imageIds[i]]=concatBytes([asciiBytes(`<< /Type /XObject /Subtype /Image /Width ${t.w} /Height ${t.h} /ColorSpace /DeviceRGB /BitsPerComponent 8${filter} /Length ${t.bytes.length} >>\\nstream\\n`),t.bytes,asciiBytes('\\nendstream')])})"""
s=s.replace(old_obj,new_obj,1)

# The PDF-only renderer must include the standalone line tool as well.
s=s.replace("g[data-type=\"dimension\"],g[data-type=\"leader\"]'))drawDimensionObject(ctx,n)","g[data-type=\"dimension\"],g[data-type=\"leader\"],g[data-type=\"line\"]'))drawDimensionObject(ctx,n)",1)

for token in [marker,"CompressionStream('deflate')",'tileMax=2048','/Filter /FlateDecode','willReadFrequently:true']:
    if token not in s: raise SystemExit('v46 guard failed: '+token)
if "canvasToBlob(c,'image/jpeg',.94)" in s:
    raise SystemExit('v46: legacy JPEG PDF tile path still present')

p.write_text(s,encoding='utf-8',newline='')
print('v46: PDF tiles are lossless RGB/Flate; thin technical linework no longer passes through JPEG')
