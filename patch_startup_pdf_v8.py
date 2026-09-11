from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')

old="function setPage(){let[w,h]=sizes[$('paperSize').value];if($('orientation').value==='landscape')[w,h]=[h,w];page={w,h};paper.setAttribute('viewBox',`0 0 ${w} ${h}`);paper.setAttribute('width',`${w}mm`);paper.setAttribute('height',`${h}mm`);wrap.style.width=`${w}mm`;wrap.style.height=`${h}mm`;applyZoom();updatePrintSize();renderFrame();try{window.chrome?.webview?.postMessage(`KB911_SIZE|${w}|${h}`)}catch{}}"
new="function setPage(){let[w,h]=sizes[$('paperSize').value];if($('orientation').value==='landscape')[w,h]=[h,w];page={w,h};paper.setAttribute('viewBox',`0 0 ${w} ${h}`);paper.setAttribute('width',`${w}mm`);paper.setAttribute('height',`${h}mm`);wrap.style.width=`${w}mm`;wrap.style.height=`${h}mm`;applyZoom();updatePrintSize();renderFrame();try{window.chrome?.webview?.postMessage(`KB911_SIZE|${w}|${h}`)}catch{}requestAnimationFrame(()=>requestAnimationFrame(()=>{try{window.KB911_fitToViewport&&window.KB911_fitToViewport()}catch{}}))}"
if old not in s:
    raise SystemExit('setPage block not found for v8 patch')
s=s.replace(old,new,1)

old_fit="window.KB911_fitToViewport=function(){const sidebar=265,header=48,pad=78,availW=Math.max(240,innerWidth-sidebar-pad),availH=Math.max(180,innerHeight-header-pad),paperW=page.w*3.7795275591,paperH=page.h*3.7795275591;zoom=Math.max(.25,Math.min(1,availW/paperW,availH/paperH));applyZoom();viewport.scrollLeft=0;viewport.scrollTop=0;};"
new_fit="window.KB911_fitToViewport=function(){paperStage();const prev=wrap.style.transform;wrap.style.transform='none';const baseW=Math.max(1,wrap.offsetWidth||wrap.getBoundingClientRect().width||1),baseH=Math.max(1,wrap.offsetHeight||wrap.getBoundingClientRect().height||1);wrap.style.transform=prev;const pad=68,availW=Math.max(120,viewport.clientWidth-pad),availH=Math.max(120,viewport.clientHeight-pad);zoom=Math.max(.1,Math.min(6,availW/baseW,availH/baseH));applyZoom();viewport.scrollLeft=0;viewport.scrollTop=0;};"
if old_fit not in s:
    raise SystemExit('fit function not found for v8 patch')
s=s.replace(old_fit,new_fit,1)

old_pdf="const dpi=$('saveDpi'),vals=kind==='pdf'?[100,300,600,1200,1800,2400]:[100,300];"
new_pdf="const dpi=$('saveDpi'),vals=kind==='pdf'?[100,300,600]:[100,300];"
if old_pdf not in s:
    raise SystemExit('PDF DPI list not found for v8 patch')
s=s.replace(old_pdf,new_pdf,1)

# Hard guard: generated interface must start on A3 landscape.
s=s.replace('<select id="paperSize"><option selected>A4</option><option>A3</option>',
            '<select id="paperSize"><option>A4</option><option selected>A3</option>',1)

# Final fit after WebView layout has settled. Use two passes because the native
# host may resize the window again after receiving the A3 dimensions.
insert="\nwindow.addEventListener('load',()=>{setTimeout(()=>{try{window.KB911_fitToViewport&&window.KB911_fitToViewport()}catch{}},120);setTimeout(()=>{try{window.KB911_fitToViewport&&window.KB911_fitToViewport()}catch{}},420)});\n"
idx=s.rfind('</script>')
if idx < 0:
    raise SystemExit('closing script tag not found')
s=s[:idx]+insert+s[idx:]

assert '<option selected>A3</option>' in s, 'A3 is not selected by default'
assert "kind==='pdf'?[100,300,600]" in s, 'PDF DPI cap was not applied'
assert 'viewport.clientWidth-pad' in s and 'wrap.offsetWidth' in s, 'measured fit was not applied'
section=s[s.find('function openSaveDialog'):s.find('function closeSaveDialog')]
assert '1200' not in section and '1800' not in section and '2400' not in section, 'high PDF DPI values remain'

p.write_text(s,encoding='utf-8',newline='')
print('Measured A3 startup fit and PDF 600 DPI cap applied')
