from pathlib import Path
p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
old='cancelPasteMode()});'
if old not in s:
    raise SystemExit('feature JS repair target not found')
s=s.replace(old,'cancelPasteMode()}',1)
p.write_text(s,encoding='utf-8',newline='')
print('Feature JS placePaste terminator repaired')
