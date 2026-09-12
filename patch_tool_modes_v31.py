from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')


def replace_once(old, new):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'tool modes v31: expected one anchor, got {count}: {old[:140]}')
    s = s.replace(old, new, 1)

# Only finish a pointer history transaction if it actually began inside WebView.
# This prevents mouse release after moving/resizing the native Windows window
# from creating an empty/duplicate Undo step.
old = """ window.addEventListener('pointerup',()=>{\n  kbHistoryPointer=false;setTimeout(kbHistoryCommit,0);\n },true);\n window.addEventListener('pointercancel',()=>{\n  kbHistoryPointer=false;kbHistorySchedule(0);\n },true);"""
new = """ window.addEventListener('pointerup',()=>{\n  if(!kbHistoryPointer)return;\n  kbHistoryPointer=false;setTimeout(kbHistoryCommit,0);\n },true);\n window.addEventListener('pointercancel',()=>{\n  if(!kbHistoryPointer)return;\n  kbHistoryPointer=false;kbHistorySchedule(0);\n },true);"""
replace_once(old, new)

anchor = "\nsetPage();\ninitKB911Project();\nkbHistoryStart();"
code = r'''

// KB911_V31_STICKY_CREATION_TOOLS
// Dimension, text, leader and line are persistent creation modes. Editing a
// just-created/existing object is temporary; OK/X returns to the selected mode.
const kbStickyToolsV31=new Set(['dimension','text','leader','line']);
let kbStickyToolV31=null;

function kbCloseEditorsV31(captureDimension=false){
 document.getElementById('liveTextEditor')?.blur();
 if(captureDimension&&selected?.dataset.type==='dimension')captureDimDefaults(selected);
 closeDimPopup();closeTextPopup();
 if(typeof closeLeaderPopup==='function')closeLeaderPopup();
 if(typeof closeSimpleLinePopup==='function')closeSimpleLinePopup();
 leaderDrag=null;simpleLineDrag=null;simpleLineSelectedHandle=null;
 clearSelection();
}
function kbResumeStickyToolV31(fallbackStatus=''){
 const next=kbStickyToolV31;
 if(next&&kbStickyToolsV31.has(next))setTool(next,true);
 else{setTool(null,true);if(fallbackStatus)setStatus(fallbackStatus)}
}
function kbSwitchStickyToolV31(next){
 if(!kbStickyToolsV31.has(next))return;
 // Switching tools also finalizes whatever object editor is currently open.
 kbCloseEditorsV31(tool==='dimension-edit');
 dimDraft=null;textDraft=null;leaderDraft=null;simpleLineDraft=null;
 dimPreview?.remove();textPreview?.remove();leaderPreview?.remove();simpleLinePreview?.remove();
 dimPreview=textPreview=leaderPreview=simpleLinePreview=null;
 kbStickyToolV31=next;
 setTool(next,true);
}
function kbExitStickyToolsV31(){
 kbStickyToolV31=null;
 document.getElementById('liveTextEditor')?.blur();
 dimDraft=null;textDraft=null;leaderDraft=null;simpleLineDraft=null;
 dimPreview?.remove();textPreview?.remove();leaderPreview?.remove();simpleLinePreview?.remove();
 dimPreview=textPreview=leaderPreview=simpleLinePreview=null;
 leaderDrag=null;simpleLineDrag=null;simpleLineSelectedHandle=null;
 closeDimPopup();closeTextPopup();
 if(typeof closeLeaderPopup==='function')closeLeaderPopup();
 if(typeof closeSimpleLinePopup==='function')closeSimpleLinePopup();
 activeImage=null;clearSelection();setTool(null,true);
}

// Replace the one-shot toolbar behavior with persistent creation modes.
document.querySelectorAll('[data-tool]').forEach(b=>{
 b.onclick=()=>kbSwitchStickyToolV31(b.dataset.tool);
});

// Finishing an object returns to the selected creation tool instead of forcing
// the user to click the toolbar again.
$('dimPopupOk').onclick=()=>{
 if(selected?.dataset.type==='dimension')captureDimDefaults(selected);
 closeDimPopup();clearSelection();kbResumeStickyToolV31('Размер зафиксирован');
};
$('textOk').onclick=()=>{
 document.getElementById('liveTextEditor')?.blur();closeTextPopup();clearSelection();kbResumeStickyToolV31('Надпись зафиксирована');
};
$('leaderOk').onclick=()=>{
 closeLeaderPopup();leaderDraft=null;leaderPreview?.remove();leaderPreview=null;leaderDrag=null;clearSelection();kbResumeStickyToolV31('Сноска зафиксирована');
};
$('lineOk').onclick=()=>{
 closeSimpleLinePopup();clearSelection();kbResumeStickyToolV31('Линия зафиксирована');
};

// X closes the editor too, but does not cancel the selected creation mode.
$('dimPopupClose').onclick=()=>{closeDimPopup();clearSelection();kbResumeStickyToolV31()};
$('textPopupClose').onclick=()=>{document.getElementById('liveTextEditor')?.blur();closeTextPopup();clearSelection();kbResumeStickyToolV31()};
$('leaderPopupClose').onclick=()=>{closeLeaderPopup();clearSelection();kbResumeStickyToolV31()};
$('linePopupClose').onclick=()=>{closeSimpleLinePopup();clearSelection();kbResumeStickyToolV31()};

// Escape always leaves the current creation mode, even when focus is inside an
// inline text editor (the older handler used the first Escape only for blur).
document.addEventListener('keydown',e=>{
 if(e.key!=='Escape')return;
 kbStickyToolV31=null;
 setTimeout(()=>{if(tool!==null)kbExitStickyToolsV31()},0);
},true);
'''
replace_once(anchor, code + anchor)

for token in [
    'KB911_V31_STICKY_CREATION_TOOLS',
    "const kbStickyToolsV31=new Set(['dimension','text','leader','line'])",
    'if(!kbHistoryPointer)return;',
    "b.onclick=()=>kbSwitchStickyToolV31(b.dataset.tool)",
    "$('dimPopupOk').onclick=()=>{",
    "$('leaderOk').onclick=()=>{",
    "$('lineOk').onclick=()=>{",
    'kbStickyToolV31=null;'
]:
    if token not in s:
        raise SystemExit('tool modes v31 guard failed: '+token)

p.write_text(s, encoding='utf-8', newline='')
print('Undo native-window guard and persistent creation tools installed')
