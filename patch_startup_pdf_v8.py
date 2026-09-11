from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')

old="function setPage(){let[w,h]=sizes[$('paperSize').value];if($('orientation').value==='landscape')[w,h]=[h,w];page={w,h};paper.setAttribute('viewBox',`0 0 ${w} ${h}`);paper.setAttribute('width',`${w}mm`);paper.setAttribute('height',`${h}mm`);wrap.style.width=`${w}mm`;wrap.style.height=`${h}mm`;applyZoom();updatePrintSize();renderFrame();try{window.chrome?.webview?.postMessage(`KB911_SIZE|${w}|${h}`)}catch{}}"
new="function setPage(){let[w,h]=sizes[$('paperSize').value];if($('orientation').value==='landscape')[w,h]=[h,w];page={w,h};paper.setAttribute('viewBox',`0 0 ${w} ${h}`);paper.setAttribute('width',`${w}mm`);paper.setAttribute('height',`${h}mm`);wrap.style.width=`${w}mm`;wrap.style.height=`${h}mm`;applyZoom();updatePrintSize();renderFrame();try{window.chrome?.webview?.postMessage(`KB911_SIZE|${w}|${h}`)}catch{}setTimeout(()=>{try{window.KB911_fitToViewport&&window.KB911_fitToViewport()}catch{}},60)}"
if old not in s:
    raise SystemExit('setPage block not found for v8 patch')
s=s.replace(old,new,1)

old_pdf="const dpi=$('saveDpi'),vals=kind==='pdf'?[100,300,600,1200,1800,2400]:[100,300];"
new_pdf="const dpi=$('saveDpi'),vals=kind==='pdf'?[100,300,600]:[100,300];"
if old_pdf not in s:
    raise SystemExit('PDF DPI list not found for v8 patch')
s=s.replace(old_pdf,new_pdf,1)

# The generated UI must start as A3 landscape. patch_v4 normally does this;
# keep this guard so a future base-file change cannot silently regress startup.
s=s.replace('<select id="paperSize"><option selected>A4</option><option>A3</option>',
            '<select id="paperSize"><option>A4</option><option selected>A3</option>',1)

# Extra delayed fit after the whole application/project UI has initialized.
marker='initKB911Project();\n})();'
if marker in s:
    s=s.replace(marker,"initKB911Project();\nsetTimeout(()=>{try{window.KB911_fitToViewport&&window.KB911_fitToViewport()}catch{}},180);\n})();",1)
else:
    marker='setPage();\n})();'
    if marker in s:
        s=s.replace(marker,"setPage();\nsetTimeout(()=>{try{window.KB911_fitToViewport&&window.KB911_fitToViewport()}catch{}},180);\n})();",1)
    else:
        raise SystemExit('startup marker not found for delayed fit')

# Build-time sanity checks.
assert '<option selected>A3</option>' in s, 'A3 is not selected by default'
assert "kind==='pdf'?[100,300,600]" in s, 'PDF DPI cap was not applied'
assert '1200,1800,2400' not in s[s.find('function openSaveDialog'):s.find('function closeSaveDialog')], 'high PDF DPI values remain'

p.write_text(s,encoding='utf-8',newline='')
print('A3 startup fit and PDF 600 DPI cap applied')
