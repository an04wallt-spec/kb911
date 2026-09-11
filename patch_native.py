from pathlib import Path
p=Path('src/main.cpp')
s=p.read_text(encoding='utf-8')
s=s.replace('static double g_paperWmm = 297.0;\nstatic double g_paperHmm = 210.0;','static double g_paperWmm = 420.0;\nstatic double g_paperHmm = 297.0;')
s=s.replace('FitWindowToPaper(297.0, 210.0);','FitWindowToPaper(420.0, 297.0);')
p.write_text(s,encoding='utf-8',newline='')
print('Native A3 default applied')
