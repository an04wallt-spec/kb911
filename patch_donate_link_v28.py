from pathlib import Path
import re

html = Path('app/KB911.html')
s = html.read_text(encoding='utf-8')

old = r'<div id="donateQrArea"><img id="donateQrImage" src="data:image/png;base64,[A-Za-z0-9+/=]+" alt="QR-код для перевода через Т-Банк или Сбербанк"></div>'
new = ('<div id="donateLinkArea"><a id="donatePayLink" '
       'href="https://pay.cloudtips.ru/p/811ce792" target="_blank" '
       'rel="noopener noreferrer">Поддержать проект <span aria-hidden="true">↗</span></a>'
       '<div class="donate-link-hint">Страница оплаты откроется в браузере</div></div>')
s, count = re.subn(old, new, s)
if count != 1:
    raise SystemExit(f'donation link: expected one QR image, found {count}')

old_css = '#donateQrArea{display:none;text-align:center;margin-top:8px}#donateMenu.open~#donateQrArea{display:block}#donateQrImage{display:block;width:min(100%,210px);height:auto;aspect-ratio:1;margin:auto;image-rendering:pixelated}'
new_css = ('#donateLinkArea{display:none;text-align:center;margin-top:12px}'
           '#donateMenu.open~#donateLinkArea{display:block}'
           '#donatePayLink{display:flex;align-items:center;justify-content:center;gap:8px;'
           'min-height:48px;padding:9px 12px;border-radius:8px;background:#2563eb;color:#fff;'
           'font-size:15px;font-weight:700;text-decoration:none;box-shadow:0 3px 9px rgba(37,99,235,.22)}'
           '#donatePayLink:hover{background:#1d4ed8}'
           '#donatePayLink:focus-visible{outline:3px solid #93c5fd;outline-offset:2px}'
           '.donate-link-hint{margin:9px 2px 0;color:#545b67;font-size:12px;line-height:1.35}')
if s.count(old_css) != 1:
    raise SystemExit('donation link: expected QR styles not found')
s = s.replace(old_css, new_css, 1)

anchor = "$('donateMenu').addEventListener('click',e=>e.stopPropagation());"
if s.count(anchor) != 1:
    raise SystemExit('donation link: expected menu handler not found')
s = s.replace(anchor, anchor + "$('donatePayLink').addEventListener('click',e=>{if(window.chrome?.webview){e.preventDefault();window.chrome.webview.postMessage('KB911_DONATE_OPEN')}});", 1)
html.write_text(s, encoding='utf-8', newline='')

native = Path('src/main.cpp')
cpp = native.read_text(encoding='utf-8')
anchor = '    const std::wstring prefix = L"KB911_SIZE|";'
if cpp.count(anchor) != 1 or '#include <shellapi.h>' not in cpp:
    raise SystemExit('donation link: native message handler not found')
cpp = cpp.replace(anchor,
    '    if (s == L"KB911_DONATE_OPEN") {\n'
    '        ShellExecuteW(nullptr, L"open", L"https://pay.cloudtips.ru/p/811ce792", nullptr, nullptr, SW_SHOWNORMAL);\n'
    '        return;\n'
    '    }\n' + anchor, 1)
native.write_text(cpp, encoding='utf-8', newline='')
print('Donation QR replaced with external payment link')
