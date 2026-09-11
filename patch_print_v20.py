from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='// KB911_V20_PRINT_RESTORE'
if marker in s:
    print('v20 print already applied')
    raise SystemExit(0)

# Add an explicit print command to the existing export panel.  Older builds
# already carried correct @media print and dynamic @page sizing, but printing
# depended on Chromium/WebView2 Ctrl+P.  Keep that print layout and restore a
# deterministic entry point without touching drawing/project/export logic.
anchor='<button id="exportPdf" class="primary" style="width:100%">Сохранить как PDF</button>'
if anchor not in s:
    raise SystemExit('v20: export PDF button anchor not found')
s=s.replace(anchor, anchor+'\n    <button id="printSheet" style="width:100%;margin-top:6px">Печать</button>',1)

# Strengthen the already-existing print stylesheet: only the physical sheet is
# printable; transient selection/editing UI must never reach paper.
old='''@media print{\n body{background:#fff;overflow:visible} header,aside{display:none!important} #app{display:block;height:auto} main{display:block} #viewport{padding:0;overflow:visible;background:#fff;display:block} #paperWrap{box-shadow:none;transform:none!important;margin:0} #paper{width:100%;height:auto}\n}'''
new='''@media print{\n html,body{margin:0!important;padding:0!important;background:#fff!important;overflow:visible!important}\n header,aside,#dimPopup,#textPopup,#leaderPopup,#saveDialog,#imageContextMenu,.selection-ui{display:none!important}\n #app{display:block!important;height:auto!important}\n main{display:block!important}\n #viewport{padding:0!important;margin:0!important;overflow:visible!important;background:#fff!important;display:block!important}\n #paperWrap{box-shadow:none!important;transform:none!important;margin:0!important;width:var(--kb-print-w)!important;height:var(--kb-print-h)!important}\n #paper{display:block!important;width:var(--kb-print-w)!important;height:var(--kb-print-h)!important}\n}'''
if old not in s:
    raise SystemExit('v20: print stylesheet anchor not found')
s=s.replace(old,new,1)

# Install print entry points inside the live application scope, immediately
# before the native-project section.  Do not intercept Ctrl+P while typing in a
# field; Chromium's native shortcut is replaced only at application level.
anchor='// ---------- Native KB911 project format ----------'
pos=s.find(anchor)
if pos<0:
    raise SystemExit('v20: project anchor not found')
code=r'''
// KB911_V20_PRINT_RESTORE
function kbPrintCurrentSheetV20(){
 try{document.getElementById('liveTextEditor')?.blur()}catch{}
 try{closeDimPopup()}catch{}
 try{closeTextPopup()}catch{}
 try{closeLeaderPopup()}catch{}
 try{closeSaveDialog()}catch{}
 try{closeImageMenu()}catch{}
 try{clearUI()}catch{}
 try{kbMultiSelected=[]}catch{}
 try{kbSyncCurrentSheet()}catch{}
 try{updatePrintSize()}catch{}
 document.documentElement.style.setProperty('--kb-print-w',page.w+'mm');
 document.documentElement.style.setProperty('--kb-print-h',page.h+'mm');
 setStatus('Открываю печать…');
 requestAnimationFrame(()=>requestAnimationFrame(()=>window.print()));
}
$('printSheet').addEventListener('click',kbPrintCurrentSheetV20);
document.addEventListener('keydown',e=>{
 if(!(e.ctrlKey||e.metaKey)||e.altKey||e.shiftKey)return;
 if(!(e.code==='KeyP'||String(e.key||'').toLowerCase()==='p'||e.key==='з'||e.key==='З'))return;
 const a=document.activeElement;
 if(a&&['INPUT','TEXTAREA','SELECT'].includes(a.tagName))return;
 e.preventDefault();e.stopImmediatePropagation();
 kbPrintCurrentSheetV20();
},true);
window.addEventListener('afterprint',()=>{try{window.KB911_fitToViewport&&window.KB911_fitToViewport()}catch{};setStatus('Готово')});

'''
s=s[:pos]+code+s[pos:]

for token in [marker,'id="printSheet"','function kbPrintCurrentSheetV20()','window.print()','updatePrintSize()','--kb-print-w']:
    if token not in s: raise SystemExit('v20 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v20: explicit print command and Ctrl+P restored using existing page-size print layout')
