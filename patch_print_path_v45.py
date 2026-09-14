from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V45_PRINT_AND_PATH_MEMORY'
if marker in s:
    print('v45 already applied')
    raise SystemExit(0)

old="function updatePrintSize(){let st=$('pageStyle');if(!st){st=document.createElement('style');st.id='pageStyle';document.head.appendChild(st)}st.textContent=`@page{size:${page.w}mm ${page.h}mm;margin:0}`}"
new="function updatePrintSize(){let st=$('pageStyle');if(!st){st=document.createElement('style');st.id='pageStyle';document.head.appendChild(st)}const pn=$('paperSize')?.value||'A3',po=$('orientation')?.value||'landscape';st.textContent=`@page{size:${pn} ${po};margin:0}`;document.documentElement.style.setProperty('--kb-print-w',page.w+'mm');document.documentElement.style.setProperty('--kb-print-h',page.h+'mm')}"
if s.count(old)!=1:
    raise SystemExit('v45: print size function anchor missing')
s=s.replace(old,new,1)

repls=[
    ("id:'kb911-export',suggestedName", "id:'kb911-last-folder',startIn:'documents',suggestedName"),
    ("id:'kb911-project',suggestedName:name", "id:'kb911-last-folder',startIn:'documents',suggestedName:name"),
    ("id:'kb911-project-open',multiple:false", "id:'kb911-last-folder',startIn:'documents',multiple:false"),
]
for a,b in repls:
    if a not in s:
        raise SystemExit('v45: picker anchor missing: '+a)
    s=s.replace(a,b,1)

idx=s.rfind('</script>')
if idx<0:
    raise SystemExit('v45: closing script missing')
code="\n// KB911_V45_PRINT_AND_PATH_MEMORY\nwindow.KB911_SAVE_LOCATION_V45={sharedPickerId:'kb911-last-folder',namedPaper:true};\n"
s=s[:idx]+code+s[idx:]

for token in [marker,"@page{size:${pn} ${po};margin:0}","id:'kb911-last-folder'","startIn:'documents'","namedPaper:true"]:
    if token not in s:
        raise SystemExit('v45 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v45: named print paper size and shared remembered picker location installed')
