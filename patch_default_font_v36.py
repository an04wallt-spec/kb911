from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')

marker = 'KB911_V36_BAHNSCHRIFT_DEFAULT'
if marker in s:
    print('v36 already applied')
    raise SystemExit(0)

old = "let dimDefaults=Object.assign({},builtDim,readStore('mm.dimDefaults.v2'));"
new = """let dimDefaults=Object.assign({},builtDim,readStore('mm.dimDefaults.v2'));
// KB911_V36_BAHNSCHRIFT_DEFAULT
// v35 accidentally left some testers with Gost persisted as the dimension default.
// Migrate that state once, then preserve all future explicit user choices normally.
try{
 const kbFontMigrationKey='kb911.v36.bahnschriftDefaultMigrated';
 if(!localStorage.getItem(kbFontMigrationKey)){
  if(dimDefaults.font==='Gost'){
   dimDefaults.font='Bahnschrift';
   localStorage.setItem('mm.dimDefaults.v2',JSON.stringify(dimDefaults));
  }
  localStorage.setItem(kbFontMigrationKey,'1');
 }
}catch{}"""

if s.count(old) != 1:
    raise SystemExit(f'v36: expected one dimension-default anchor, got {s.count(old)}')
s = s.replace(old, new, 1)

# Keep both built-in defaults explicitly on Bahnschrift. Gost remains only an available option.
if "font:'Bahnschrift'" not in s:
    raise SystemExit('v36: Bahnschrift built-in default missing')
if s.count('<option selected>Bahnschrift</option><option>Gost</option>') != 2:
    raise SystemExit('v36: expected Bahnschrift to remain selected in both font lists')

for token in [
    marker,
    "if(dimDefaults.font==='Gost')",
    "dimDefaults.font='Bahnschrift'",
    "kb911.v36.bahnschriftDefaultMigrated",
    "<option selected>Bahnschrift</option><option>Gost</option>"
]:
    if token not in s:
        raise SystemExit('v36 guard failed: ' + token)

p.write_text(s, encoding='utf-8', newline='')
print('v36: Bahnschrift restored as the default; embedded Gost remains optional')

# v37 changes only frame-logo fitting: preserve the image aspect ratio inside the adjustable box.
exec(Path('patch_logo_fit_v37.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
