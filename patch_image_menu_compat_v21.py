from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='// KB911_V21_IMAGE_MENU_COMPAT'
if marker in s:
    print('v21 image menu compatibility already applied')
    raise SystemExit(0)

anchor='// ---------- Native KB911 project format ----------'
pos=s.find(anchor)
if pos<0:
    raise SystemExit('v21: project anchor not found')

code=r'''
// KB911_V21_IMAGE_MENU_COMPAT
// Several older handlers still call openImageMenu()/closeImageMenu(), but the
// recent single-owner layer-menu repair replaced the menu lifecycle and those
// two helpers disappeared.  Export calls closeImageMenu() before rendering,
// which made PNG/JPEG/PDF fail with ReferenceError.  Restore only the missing
// compatibility helpers and delegate closing to the proven v19 lifecycle.
function closeImageMenu(){
  try{
    kbLayerTarget=null;
    if(typeof kbInstallLayerMenuV19==='function'){
      kbInstallLayerMenuV19(true);
      return;
    }
  }catch{}
  const m=$('imageContextMenu');
  if(!m)return;
  m.classList.remove('open');
  m.setAttribute('aria-hidden','true');
  m.style.setProperty('display','none','important');
  m.style.setProperty('visibility','hidden','important');
  m.style.setProperty('pointer-events','none','important');
}
function openImageMenu(img,e){
  if(!img)return;
  try{kbLayerTarget=img}catch{}
  try{selected=img;showProps();drawSelection()}catch{}
  const m=$('imageContextMenu');
  if(!m)return;
  m.style.removeProperty('display');
  m.style.removeProperty('visibility');
  m.style.removeProperty('pointer-events');
  m.classList.add('open');
  m.setAttribute('aria-hidden','false');
  const w=205,h=76,x=e?.clientX??20,y=e?.clientY??20;
  m.style.left=Math.max(4,Math.min(x,innerWidth-w-6))+'px';
  m.style.top=Math.max(4,Math.min(y,innerHeight-h-6))+'px';
}

'''
s=s[:pos]+code+s[pos:]

for token in [marker,'function closeImageMenu()','function openImageMenu(img,e)','kbInstallLayerMenuV19(true)']:
    if token not in s: raise SystemExit('v21 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v21: restored image-menu compatibility helpers; export no longer fails on closeImageMenu')
