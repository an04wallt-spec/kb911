from pathlib import Path
p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
# patch_v4 used escaped newline markers in code-generation strings. Convert only
# markers that sit between JavaScript statements/declarations; do not touch \n
# inside ordinary JS string literals (PDF generation etc.).
patterns=[
    ('}\\nfunction ', '}\nfunction '),
    (';\\nfunction ', ';\nfunction '),
    ('\\npaper.addEventListener', '\npaper.addEventListener'),
    ('\\nwindow.addEventListener', '\nwindow.addEventListener'),
    (';\\n$(\'', ';\n$(\''),
    ('}\\n$(\'', '}\n$(\''),
]
count=0
for a,b in patterns:
    n=s.count(a)
    if n:
        s=s.replace(a,b)
        count+=n
p.write_text(s,encoding='utf-8',newline='')
print('Syntax newline repair applied:',count)
