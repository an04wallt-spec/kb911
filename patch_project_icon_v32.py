from pathlib import Path

p = Path('src/main.cpp')
s = p.read_text(encoding='utf-8')

old = 'KB911_project_v31.ico'
new = 'KB911_project_v32.ico'
if old not in s:
    raise SystemExit('v32 project icon patch: v31 path not found')
s = s.replace(old, new)
s = s.replace('KB911_V31_PROJECT_ICON_FILE', 'KB911_V32_PROJECT_ICON_FILE')
s = s.replace('KB911_V31_PROJECT_ICON_ASSOC_FILE', 'KB911_V32_PROJECT_ICON_ASSOC_FILE')

for token in ['KB911_project_v32.ico','KB911_V32_PROJECT_ICON_FILE','KB911_V32_PROJECT_ICON_ASSOC_FILE']:
    if token not in s:
        raise SystemExit('v32 project icon patch guard failed: ' + token)

p.write_text(s, encoding='utf-8', newline='')
print('v32: corrected project ICO uses a new physical cache-busting path')
