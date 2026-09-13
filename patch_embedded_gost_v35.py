from pathlib import Path
import base64
import hashlib
import html
import urllib.request

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')

marker = 'KB911_V35_EMBEDDED_GOST_UI_TUNING'
if marker in s:
    print('v35 already applied')
    raise SystemExit(0)

# Fixed, immutable source revision. The font is OpenGOST Type B (OFL-1.1).
FONT_URL = 'https://raw.githubusercontent.com/amaton/alexdress/14535efe54c0954cc9c0cb54da5ac75661958f63/skin/frontend/alexdress/default/fonts/opengosttypeb-regular.woff'
FONT_GIT_BLOB_SHA1 = '01185932fded2df3f4f44f41208949e6c2e39f3c'
LICENSE_URL = 'https://raw.githubusercontent.com/ingenium-am/open-gost-arm/4c8aca3fe4da3d7e7805aaf7c312b196d5274620/LICENSE.txt'
LICENSE_GIT_BLOB_SHA1 = '201e8a1dfc4a51d3e9d64e65c0b72e8fa5af89c9'


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'KB911-build/35'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def git_blob_sha1(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\\0' + data).hexdigest()

font_bytes = fetch(FONT_URL)
if not font_bytes.startswith(b'wOFF'):
    raise SystemExit('v35: downloaded OpenGOST asset is not WOFF')
if git_blob_sha1(font_bytes) != FONT_GIT_BLOB_SHA1:
    raise SystemExit('v35: OpenGOST font hash mismatch')

license_bytes = fetch(LICENSE_URL)
if git_blob_sha1(license_bytes) != LICENSE_GIT_BLOB_SHA1:
    raise SystemExit('v35: OpenGOST license hash mismatch')
license_text = license_bytes.decode('utf-8', errors='strict')

font_b64 = base64.b64encode(font_bytes).decode('ascii')
style = f'''<style id="kb911V35EmbeddedGostUiTuning">
/* {marker} */
@font-face{{
  font-family:'Gost';
  src:url(data:font/woff;base64,{font_b64}) format('woff');
  font-weight:400;
  font-style:normal;
  font-display:block;
}}
/* The blue status/help field uses the same text size as the top toolbar. */
header #status{{font-size:14px}}
/* Frame numeric fields are deliberately compact; the panel layout stays unchanged. */
#framePanel .frame-setting-item input[type=number]{{width:72px;height:28px;padding:0 5px}}
</style>
<div id="kb911OpenGostLicenseV35" hidden><pre>{html.escape(license_text)}</pre></div>
'''

if s.count('</head>') != 1:
    raise SystemExit('v35: expected one </head>')
s = s.replace('</head>', style + '</head>', 1)

# Warm the embedded face immediately so canvas measurement/export never falls back
# to an installed Windows font when the user later chooses Gost.
anchor = "setPage();\ninitKB911Project();"
if anchor not in s:
    raise SystemExit('v35: startup anchor not found')
s = s.replace(anchor, "try{document.fonts?.load('16px Gost')}catch{}\n" + anchor, 1)

for token in [
    marker,
    "font-family:'Gost'",
    'data:font/woff;base64,',
    'header #status{font-size:14px}',
    '#framePanel .frame-setting-item input[type=number]{width:72px;height:28px;padding:0 5px}',
    "document.fonts?.load('16px Gost')",
    'id="kb911OpenGostLicenseV35"',
    '<option>Gost</option>'
]:
    if token not in s:
        raise SystemExit('v35 guard failed: ' + token)

p.write_text(s, encoding='utf-8', newline='')
print('v35: embedded OpenGOST, toolbar status font size, and compact frame fields applied')
