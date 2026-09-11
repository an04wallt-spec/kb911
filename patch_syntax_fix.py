from pathlib import Path
p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
# Convert only escaped newline markers that were emitted between JavaScript
# statements by code-generation patches. Do not touch \n inside normal JS strings.
patterns=[
    ('}\\nfunction ', '}\nfunction '),
    (';\\nfunction ', ';\nfunction '),
    ('}\\n(function', '}\n(function'),
    (';\\n(function', ';\n(function'),
    ('\\npaper.addEventListener', '\npaper.addEventListener'),
    ('\\nwindow.addEventListener', '\nwindow.addEventListener'),
    (';\\n$(\'', ';\n$(\''),
    ('}\\n$(\'', '}\n$(\''),
    (')\\n$(\'', ')\n$(\''),
    (';\\nif(', ';\nif('),
    ('}\\nif(', '}\nif('),
]
count=0
for a,b in patterns:
    n=s.count(a)
    if n:
        s=s.replace(a,b)
        count+=n
p.write_text(s,encoding='utf-8',newline='')
print('Syntax newline repair applied:',count)
