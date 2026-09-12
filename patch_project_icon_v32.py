from pathlib import Path

p = Path('src/main.cpp')
s = p.read_text(encoding='utf-8')

old = 'KB911_project_v31.ico'
new = 'KB911_project_v34.ico'
if old not in s:
    raise SystemExit('v33 project icon patch: v31 path not found')
s = s.replace(old, new)
s = s.replace('KB911_V31_PROJECT_ICON_FILE', 'KB911_V34_PROJECT_ICON_FILE')
s = s.replace('KB911_V31_PROJECT_ICON_ASSOC_FILE', 'KB911_V34_PROJECT_ICON_ASSOC_FILE')

for token in ['KB911_project_v34.ico','KB911_V34_PROJECT_ICON_FILE','KB911_V34_PROJECT_ICON_ASSOC_FILE']:
    if token not in s:
        raise SystemExit('v33 project icon patch guard failed: ' + token)

p.write_text(s, encoding='utf-8', newline='')
print('v34: project ICO uses a fresh cache-busting physical path')
