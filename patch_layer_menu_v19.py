from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='// KB911_V19_LAYER_MENU_SINGLE_OWNER'
if marker in s:
    print('v19 already applied')
    raise SystemExit(0)

anchor='// ---------- Native KB911 project format ----------'
pos=s.find(anchor)
if pos<0:
    raise SystemExit('v19: project anchor not found')

code=r'''
// KB911_V19_LAYER_MENU_SINGLE_OWNER
// The menu had multiple direct click handlers from the original image code and
// the later universal-layer patch.  Hiding it was therefore unreliable because
// another already-registered handler could leave/reopen the same DOM node.
// Replace the menu node itself so all old direct listeners are discarded, and
// give the menu exactly one owner.  After every layer action replace it again
// with a fresh hidden clone.  This makes stale listeners physically impossible.
const kbLayerMenuTemplateV19=$('imageContextMenu').cloneNode(true);
function kbInstallLayerMenuV19(hidden=true){
 const cur=$('imageContextMenu');
 const m=kbLayerMenuTemplateV19.cloneNode(true);
 if(cur)cur.replaceWith(m);else document.body.appendChild(m);
 if(hidden){
   m.classList.remove('open');
   m.setAttribute('aria-hidden','true');
   m.style.setProperty('display','none','important');
   m.style.setProperty('visibility','hidden','important');
   m.style.setProperty('pointer-events','none','important');
 }
 m.addEventListener('click',e=>{
   const b=e.target.closest('button[data-layer]');
   if(!b)return;
   e.preventDefault();e.stopImmediatePropagation();
   const obj=(kbLayerTarget&&kbLayerTarget.isConnected)?kbLayerTarget:
     (selected&&['image','dimension','text','leader'].includes(selected.dataset?.type)?selected:null);
   if(obj)kbMoveLayer(obj,b.dataset.layer);
   kbLayerTarget=null;
   kbInstallLayerMenuV19(true);
 },true);
 return m;
}
// Capture starts at window, before either paper contextmenu listener.  Restore
// the fresh node to a normal display state so the existing positioning/opening
// code can show it for this right-click.
window.addEventListener('contextmenu',()=>{
 const m=$('imageContextMenu')||kbInstallLayerMenuV19(false);
 m.style.removeProperty('display');
 m.style.removeProperty('visibility');
 m.style.removeProperty('pointer-events');
},true);
kbInstallLayerMenuV19(true);

'''
s=s[:pos]+code+s[pos:]

if marker not in s:
    raise SystemExit('v19 marker missing')
if 'kbInstallLayerMenuV19(true)' not in s:
    raise SystemExit('v19 reset missing')
if "stopImmediatePropagation();" not in code:
    raise SystemExit('v19 exclusive click missing')

p.write_text(s,encoding='utf-8',newline='')
print('v19: layer menu replaced with a single-owner fresh-node lifecycle')
