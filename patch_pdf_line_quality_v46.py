from pathlib import Path
import re

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V46_LOSSLESS_PDF_LINEWORK'
if marker in s:
    print('v46 already applied')
    raise SystemExit(0)

# Replace the complete multi-page PDF tile renderer structurally instead of
# depending on localized status strings or previous minor edits.
pat=r"async function kbRenderPageTiles\(dpi,pageNo,pageCount\)\{.*?\}\nfunction kbMakeMultiPagePdf"
new_renderer=r'''// KB911_V46_LOSSLESS_PDF_LINEWORK
async function kbPdfRgbTileV46(ctx,w,h){
 const rgba=ctx.getImageData(0,0,w,h).data,rgb=new Uint8Array(w*h*3);
 for(let i=0,j=0;i<rgba.length;i+=4){rgb[j++]=rgba[i];rgb[j++]=rgba[i+1];rgb[j++]=rgba[i+2]}
 if(typeof CompressionStream==='function'){
  const cs=new CompressionStream('deflate'),stream=new Blob([rgb]).stream().pipeThrough(cs),ab=await new Response(stream).arrayBuffer();
  return{bytes:new Uint8Array(ab),flate:true};
 }
 return{bytes:rgb,flate:false};
}
async function kbRenderPageTiles(dpi,pageNo,pageCount){
 const sx=dpi/25.4,totalW=Math.max(1,Math.round(page.w*sx)),totalH=Math.max(1,Math.round(page.h*sx)),tileMax=2048,cache=await kbPageImageCache(),tiles=[];
 const nx=Math.ceil(totalW/tileMax),ny=Math.ceil(totalH/tileMax),totalTiles=nx*ny;let ti=0;
 for(let y=0;y<totalH;y+=tileMax){for(let x=0;x<totalW;x+=tileMax){
  ti++;setStatus(`PDF: лист ${pageNo}/${pageCount}, фрагмент ${ti}/${totalTiles}`);
  const w=Math.min(tileMax,totalW-x),h=Math.min(tileMax,totalH-y),c=document.createElement('canvas');c.width=w;c.height=h;
  const ctx=c.getContext('2d',{alpha:false,willReadFrequently:true});if(!ctx)throw new Error('Canvas недоступен');
  ctx.fillStyle='#fff';ctx.fillRect(0,0,w,h);ctx.save();ctx.scale(sx,sx);ctx.translate(-x/sx,-y/sx);await kbDrawSheetToContext(ctx,cache);ctx.restore();
  const enc=await kbPdfRgbTileV46(ctx,w,h);tiles.push({x,y,w,h,bytes:enc.bytes,flate:enc.flate});
  c.width=1;c.height=1;await new Promise(r=>setTimeout(r,0));
 }}
 return{wMm:page.w,hMm:page.h,totalW,totalH,tiles};
}
function kbMakeMultiPagePdf'''
s,n=re.subn(pat,new_renderer,s,count=1,flags=re.S)
if n!=1:
    raise SystemExit(f'v46: expected one PDF tile renderer, got {n}')

# In the multi-page PDF writer, replace JPEG/DCT image objects with either
# zlib/Flate-compressed RGB or raw RGB as a compatibility fallback.
a=s.find('function kbMakeMultiPagePdf')
b=s.find('async function kbPerformSaveV7',a)
if a<0 or b<0:
    raise SystemExit('v46: multi-page PDF writer range not found')
block=s[a:b]
needle=" /Filter /DCTDecode /Length ${t.bytes.length}"
if block.count(needle)!=1:
    raise SystemExit(f'v46: expected one DCT tile filter in PDF writer, got {block.count(needle)}')
block=block.replace(needle,"${t.flate?' /Filter /FlateDecode':''} /Length ${t.bytes.length}",1)
s=s[:a]+block+s[b:]

# The PDF-specific renderer must include the standalone line tool too.
old="g[data-type=\"dimension\"],g[data-type=\"leader\"]'))drawDimensionObject(ctx,n)"
new="g[data-type=\"dimension\"],g[data-type=\"leader\"],g[data-type=\"line\"]'))drawDimensionObject(ctx,n)"
if old in s:
    s=s.replace(old,new,1)

for token in [marker,"CompressionStream('deflate')",'tileMax=2048','/Filter /FlateDecode','willReadFrequently:true','kbPdfRgbTileV46']:
    if token not in s: raise SystemExit('v46 guard failed: '+token)

# JPEG is still allowed for JPEG export and an obsolete single-page helper, but
# the active multi-page PDF tile renderer must no longer encode JPEG tiles.
a=s.find('async function kbRenderPageTiles')
b=s.find('function kbMakeMultiPagePdf',a)
active=s[a:b]
if "canvasToBlob(c,'image/jpeg'" in active or '/DCTDecode' in active:
    raise SystemExit('v46: active PDF tile renderer still contains JPEG')

p.write_text(s,encoding='utf-8',newline='')
print('v46: PDF tiles are lossless RGB/Flate; thin technical linework no longer passes through JPEG')
