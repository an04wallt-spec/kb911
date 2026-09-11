from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')

old="function setPage(){let[w,h]=sizes[$('paperSize').value];if($('orientation').value==='landscape')[w,h]=[h,w];page={w,h};paper.setAttribute('viewBox',`0 0 ${w} ${h}`);paper.setAttribute('width',`${w}mm`);paper.setAttribute('height',`${h}mm`);wrap.style.width=`${w}mm`;wrap.style.height=`${h}mm`;applyZoom();updatePrintSize();renderFrame();try{window.chrome?.webview?.postMessage(`KB911_SIZE|${w}|${h}`)}catch{}}"
new="function setPage(){let[w,h]=sizes[$('paperSize').value];if($('orientation').value==='landscape')[w,h]=[h,w];page={w,h};paper.setAttribute('viewBox',`0 0 ${w} ${h}`);paper.setAttribute('width',`${w}mm`);paper.setAttribute('height',`${h}mm`);wrap.style.width=`${w}mm`;wrap.style.height=`${h}mm`;applyZoom();updatePrintSize();renderFrame();try{window.chrome?.webview?.postMessage(`KB911_SIZE|${w}|${h}`)}catch{}setTimeout(()=>{try{window.KB911_fitToViewport&&window.KB911_fitToViewport()}catch{}},80)}"
if old not in s:
    raise SystemExit('setPage block not found for v8 patch')
s=s.replace(old,new,1)

old_pdf="const dpi=$('saveDpi'),vals=kind==='pdf'?[100,300,600,1200,1800,2400]:[100,300];"
new_pdf="const dpi=$('saveDpi'),vals=kind==='pdf'?[100,300,600]:[100,300];"
if old_pdf not in s:
    raise SystemExit('PDF DPI list not found for v8 patch')
s=s.replace(old_pdf,new_pdf,1)

# Hard guard: generated interface must start on A3 landscape.
s=s.replace('<select id="paperSize"><option selected>A4</option><option>A3</option>',
            '<select id="paperSize"><option>A4</option><option selected>A3</option>',1)

# Force one more fit after full DOM/WebView layout without depending on a fragile
# end-of-file marker. This runs only for a fresh application startup; opening a
# project may subsequently select its stored sheet settings.
insert="\nwindow.addEventListener('load',()=>setTimeout(()=>{try{window.KB911_fitToViewport&&window.KB911_fitToViewport()}catch{}},220));\n"
idx=s.rfind('</script>')
if idx < 0:
    raise SystemExit('closing script tag not found')
s=s[:idx]+insert+s[idx:]

assert '<option selected>A3</option>' in s, 'A3 is not selected by default'
assert "kind==='pdf'?[100,300,600]" in s, 'PDF DPI cap was not applied'
section=s[s.find('function openSaveDialog'):s.find('function closeSaveDialog')]
assert '1200' not in section and '1800' not in section and '2400' not in section, 'high PDF DPI values remain'

p.write_text(s,encoding='utf-8',newline='')
print('A3 startup fit and PDF 600 DPI cap applied')
