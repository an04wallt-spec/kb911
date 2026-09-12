from pathlib import Path
import re

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')

# Keep the existing support link and its Windows browser handler; remove only
# the expandable solicitation and the icon embedded in its old button.
pattern = r'<div id="donateWrap"><button id="donateBtn"[^>]*><img src="data:image/png;base64,[A-Za-z0-9+/=]+" alt="">Попрошайка ▾</button><div id="donateMenu">[^<]*</div><div id="donateLinkArea">'
s, count = re.subn(pattern, '<div id="donateWrap"><div id="donateLinkArea">', s)
if count != 1:
    raise SystemExit(f'support button: expected one expandable donation panel, got {count}')

hint = '<div class="donate-link-hint">Страница оплаты откроется в браузере</div>'
if s.count(hint) != 1:
    raise SystemExit('support button: hint not found')
s = s.replace(hint, '', 1)

start = s.index('#donateWrap{position:relative;margin-top:10px}')
end = s.index('\n#framePanel .frame-param', start)
s = (s[:start] +
     '#donateWrap{margin-top:0}#donateLinkArea{display:block}'
     '#donatePayLink{display:flex;align-items:center;justify-content:center;gap:6px;'
     'width:100%;height:29px;padding:0 12px;border:1px solid #2563eb;'
     'border-radius:6px;background:#2563eb;color:#fff;font:inherit;font-weight:600;'
     'text-decoration:none;cursor:pointer}'
     '#donatePayLink:hover{background:#1d4ed8}'
     '#donatePayLink:focus-visible{outline:3px solid #93c5fd;outline-offset:2px}' +
     s[end:])

pattern = r'function kbPlaceDonateMenu\(\)\{.*?\}\nfunction kbCloseDonateMenu\(\)\{.*?\}\n\n(?=// KB911_V9_RUNTIME_REPAIR)'
s, count = re.subn(pattern, '', s, count=1, flags=re.S)
if count != 1:
    raise SystemExit('support button: old menu functions not found')

old = ("$('donateBtn').onclick=e=>{e.stopPropagation();const m=$('donateMenu'),open=!m.classList.contains('open');m.classList.toggle('open',open);$('donateBtn').setAttribute('aria-expanded',String(open));if(open)kbPlaceDonateMenu()};"
       "$('donateMenu').addEventListener('click',e=>e.stopPropagation());")
trailer = ("window.addEventListener('click',e=>{if(!e.target.closest('#donateWrap'))kbCloseDonateMenu()});"
           "window.addEventListener('scroll',kbPlaceDonateMenu,true);window.addEventListener('resize',kbPlaceDonateMenu);")
if s.count(old) != 1 or s.count(trailer) != 1:
    raise SystemExit('support button: old menu listeners not found')
s = s.replace(old, '', 1).replace(trailer, '', 1)

if any(token in s for token in ('donateBtn', 'donateMenu', 'donateQrArea', 'donateQrImage',
                                'kbPlaceDonateMenu', 'kbCloseDonateMenu', 'Попрошайка')):
    raise SystemExit('support button: obsolete controls remain in final HTML')
if s.count('id="donatePayLink"') != 1:
    raise SystemExit('support button: payment link missing')
p.write_text(s, encoding='utf-8', newline='')
print('Support link displayed as one compact button')
