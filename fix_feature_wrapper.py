from pathlib import Path
p=Path('patch_feature_v7.py')
s=p.read_text(encoding='utf-8')
old="'))).decode('utf-8'))"
new="')).decode('utf-8'))"
if old not in s:
    raise SystemExit('feature wrapper pattern not found')
p.write_text(s.replace(old,new,1),encoding='utf-8',newline='')
print('Feature patch wrapper repaired')
