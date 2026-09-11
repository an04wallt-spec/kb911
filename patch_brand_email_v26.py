from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='// KB911_V26_BRAND_EMAIL_COPY'
if marker in s:
    print('v26 already applied')
    raise SystemExit(0)

old='<div class="brand">KB911</div>'
new='<div class="brand" id="kbBrand" title="Правый клик — скопировать e-mail">KB911</div>'
if old not in s: raise SystemExit('v26: brand not found')
s=s.replace(old,new,1)

style='''\n<style>\n#kbBrand{cursor:context-menu}\n#brandContextMenu{position:fixed;z-index:120;display:none;min-width:230px;background:#fff;border:1px solid #c8c8ce;border-radius:8px;box-shadow:0 10px 28px rgba(0,0,0,.22);padding:5px}\n#brandContextMenu.open{display:block}\n#brandContextMenu button{display:block;width:100%;height:32px;text-align:left;border:0;background:transparent;padding:0 10px;border-radius:5px}\n#brandContextMenu button:hover{background:#f0f3f8}\n</style>\n'''
if '</head>' not in s: raise SystemExit('v26: head end not found')
s=s.replace('</head>',style+'</head>',1)

menu='''\n<div id="brandContextMenu" aria-hidden="true">\n  <button id="copySupportEmail" type="button">Скопировать адрес электронной почты</button>\n</div>\n'''
anchor='<div id="imageContextMenu" aria-hidden="true">'
if anchor not in s: raise SystemExit('v26: menu anchor not found')
s=s.replace(anchor,menu+anchor,1)

native='// ---------- Native KB911 project format ----------'
pos=s.find(native)
if pos<0: raise SystemExit('v26: native anchor not found')
code=r'''
// KB911_V26_BRAND_EMAIL_COPY
const KB911_SUPPORT_EMAIL='schkaf@yandex.ru';
function kbHideBrandMenuV26(){const m=$('brandContextMenu');if(!m)return;m.classList.remove('open');m.style.display='none';m.setAttribute('aria-hidden','true')}
function kbShowBrandMenuV26(x,y){const m=$('brandContextMenu');if(!m)return;m.style.display='block';m.classList.add('open');m.setAttribute('aria-hidden','false');const r=m.getBoundingClientRect();m.style.left=Math.max(4,Math.min(innerWidth-r.width-4,x))+'px';m.style.top=Math.max(4,Math.min(innerHeight-r.height-4,y))+'px'}
function kbCopyEmailFallbackV26(text){const ta=document.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.left='-10000px';ta.style.top='-10000px';document.body.appendChild(ta);ta.focus();ta.select();let ok=false;try{ok=document.execCommand('copy')}catch{}ta.remove();return ok}
async function kbCopySupportEmailV26(){let ok=false;try{if(navigator.clipboard?.writeText){await navigator.clipboard.writeText(KB911_SUPPORT_EMAIL);ok=true}}catch{}if(!ok)ok=kbCopyEmailFallbackV26(KB911_SUPPORT_EMAIL);kbHideBrandMenuV26();setStatus(ok?'Адрес электронной почты скопирован: '+KB911_SUPPORT_EMAIL:'Не удалось скопировать адрес электронной почты')}
$('kbBrand').addEventListener('contextmenu',e=>{e.preventDefault();e.stopPropagation();kbShowBrandMenuV26(e.clientX,e.clientY)},true);
$('copySupportEmail').addEventListener('click',e=>{e.preventDefault();e.stopPropagation();kbCopySupportEmailV26()});
window.addEventListener('pointerdown',e=>{if(!e.target.closest?.('#brandContextMenu')&&!e.target.closest?.('#kbBrand'))kbHideBrandMenuV26()},true);
window.addEventListener('blur',kbHideBrandMenuV26);
document.addEventListener('keydown',e=>{if(e.key==='Escape')kbHideBrandMenuV26()},true);

'''
s=s[:pos]+code+s[pos:]

for token in [marker,'id="kbBrand"','id="brandContextMenu"','id="copySupportEmail"',"KB911_SUPPORT_EMAIL='schkaf@yandex.ru'",'kbCopySupportEmailV26']:
    if token not in s: raise SystemExit('v26 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v26: brand right-click email copy added')
