from pathlib import Path
p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V44_NATIVE_TEXT_PASTE'
if marker in s:
    print('v44 native text paste already applied'); raise SystemExit(0)

a=" const pasteKey=ctrl&&(e.code==='KeyV'||e.key?.toLowerCase()==='v'||e.key==='м'||e.key==='М');\n if(copyKey){"
b=" const pasteKey=ctrl&&(e.code==='KeyV'||e.key?.toLowerCase()==='v'||e.key==='м'||e.key==='М');\n const kbTextFocusV44=['INPUT','TEXTAREA','SELECT'].includes(document.activeElement?.tagName)||!!document.activeElement?.isContentEditable;\n if(copyKey&&!kbTextFocusV44){"
if s.count(a)!=1: raise SystemExit('v44 main clipboard anchor')
s=s.replace(a,b,1)

a="if(pasteKey&&clipboardItem){e.preventDefault();e.stopPropagation();closeDimPopup();closeTextPopup();clearUI();selected=null;startPasteMode();return}"
b="if(pasteKey&&clipboardItem&&!kbTextFocusV44){e.preventDefault();e.stopPropagation();closeDimPopup();closeTextPopup();clearUI();selected=null;startPasteMode();return}"
if s.count(a)!=1: raise SystemExit('v44 main paste anchor')
s=s.replace(a,b,1)

start=s.find('// KB911_V24_LINE_COPY_PASTE')
end=s.find('// ---------- Native KB911 project format ----------',start)
if start<0 or end<0: raise SystemExit('v44 line clipboard section')
frag=s[start:end]
a=" const ctrl=e.ctrlKey||e.metaKey;\n if(ctrl&&(e.code==='KeyC'||String(e.key).toLowerCase()==='c'||e.key==='с'||e.key==='С')&&selected?.dataset.type==='line'){"
b=" const ctrl=e.ctrlKey||e.metaKey;\n const kbTextFocusLineV44=['INPUT','TEXTAREA','SELECT'].includes(document.activeElement?.tagName)||!!document.activeElement?.isContentEditable;\n if(ctrl&&!kbTextFocusLineV44&&(e.code==='KeyC'||String(e.key).toLowerCase()==='c'||e.key==='с'||e.key==='С')&&selected?.dataset.type==='line'){"
if a not in frag: raise SystemExit('v44 line copy anchor')
frag=frag.replace(a,b,1)
a=" if(ctrl&&(e.code==='KeyV'||String(e.key).toLowerCase()==='v'||e.key==='м'||e.key==='М')&&kbLineClipboardV24){"
b=" if(ctrl&&!kbTextFocusLineV44&&(e.code==='KeyV'||String(e.key).toLowerCase()==='v'||e.key==='м'||e.key==='М')&&kbLineClipboardV24){"
if a not in frag: raise SystemExit('v44 line paste anchor')
frag=frag.replace(a,b,1)
frag=frag.replace('// KB911_V24_LINE_COPY_PASTE','// KB911_V24_LINE_COPY_PASTE\n// KB911_V44_NATIVE_TEXT_PASTE',1)
s=s[:start]+frag+s[end:]

for t in [marker,'kbTextFocusV44','kbTextFocusLineV44','pasteKey&&clipboardItem&&!kbTextFocusV44']:
    if t not in s: raise SystemExit('v44 paste guard '+t)
p.write_text(s,encoding='utf-8',newline='')
print('v44: native Ctrl+C/Ctrl+V restored in text fields')
