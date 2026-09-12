from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')


def replace_once(old, new):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'autosave v30: expected one anchor, got {count}: {old[:120]}')
    s = s.replace(old, new, 1)


# A successful explicit project save becomes the new clean baseline.  We do
# not touch the .kb911 file itself: the recovery copy is a separate native file.
save_line = "if(handle){const w=await handle.createWritable();await w.write(blob);await w.close();setStatus('Проект сохранён: '+(handle.name||name))}else{downloadBlob(blob,name);setStatus('Проект сохранён: '+name)}"
save_line_v30 = "if(handle){const w=await handle.createWritable();await w.write(blob);await w.close();setStatus('Проект сохранён: '+(handle.name||name));kbAutosaveMarkCleanV30()}else{downloadBlob(blob,name);setStatus('Проект сохранён: '+name);kbAutosaveMarkCleanV30()}"
replace_once(save_line, save_line_v30)

# Install autosave only after the already-stable universal undo/redo history has
# started.  The history snapshot is lossless and, unlike kbPackProject(), does
# not blur the live text editor while the user is typing.
anchor = '\nkbHistoryStart();'
code = r'''

// KB911_V30_AUTOSAVE_RECOVERY
// Recovery is intentionally independent of the user's .kb911 project file.
// The native host stores one atomic recovery snapshot in LocalAppData.
let kbAutosaveLastStateV30=kbHistory[kbHistoryIndex]||kbHistoryState();
let kbAutosavePendingStateV30=null;
let kbAutosaveNativeBusyV30=false;

function kbAutosavePostV30(message){
 try{
  const w=window.chrome?.webview;
  if(!w)return false;
  w.postMessage(message);
  return true;
 }catch(e){console.warn('KB911 autosave message failed',e);return false}
}
function kbAutosaveCurrentStateV30(){
 if(kbHistoryBusy||kbHistoryPointer||document.body.classList.contains('exporting'))return null;
 if(dimDraft||textDraft||leaderDraft||simpleLineDraft||pasteDraft)return null;
 kbHistoryCommit();
 return kbHistory[kbHistoryIndex]||kbHistoryState();
}
function kbAutosaveResetBaselineV30(clearNative=false){
 const state=kbAutosaveCurrentStateV30()||kbHistory[kbHistoryIndex]||kbHistoryState();
 kbAutosaveLastStateV30=state;
 kbAutosavePendingStateV30=null;
 kbAutosaveNativeBusyV30=false;
 if(clearNative)kbAutosavePostV30('KB911_AUTOSAVE_CLEAR');
}
function kbAutosaveMarkCleanV30(){
 // Called only after an explicit .kb911 save completed successfully.
 kbAutosaveResetBaselineV30(true);
}
function kbAutosaveTickV30(){
 if(kbAutosaveNativeBusyV30)return;
 const state=kbAutosaveCurrentStateV30();
 if(!state||state===kbAutosaveLastStateV30||state===kbAutosavePendingStateV30)return;
 const envelope=JSON.stringify({
  app:'KB911',kind:'autosave',version:1,savedAt:Date.now(),
  projectName:($('projectName')?.value||kbProject?.name||'Проект KB911'),state
 });
 if(!kbAutosavePostV30('KB911_AUTOSAVE_SAVE|'+envelope))return;
 kbAutosavePendingStateV30=state;
 kbAutosaveNativeBusyV30=true;
}
function kbAutosaveRestoreV30(envelope){
 if(!envelope||envelope.app!=='KB911'||envelope.kind!=='autosave'||typeof envelope.state!=='string')throw new Error('Некорректная автокопия');
 const d=new Date(+envelope.savedAt||0);
 const stamp=Number.isFinite(d.getTime())&&d.getTime()>0?d.toLocaleString('ru-RU'):'';
 const name=String(envelope.projectName||'Проект KB911');
 const question='Найдена автосохранённая копия предыдущей работы'+(stamp?' от '+stamp:'')+'.\n\nПроект: '+name+'\n\nВосстановить её?';
 if(confirm(question)){
  kbHistoryRestore(envelope.state);
  kbHistory=[envelope.state];kbHistoryIndex=0;
  kbAutosaveLastStateV30=envelope.state;
  kbAutosavePendingStateV30=null;
  kbAutosaveNativeBusyV30=false;
  setStatus('Автосохранённая копия восстановлена');
 }else{
  kbAutosaveResetBaselineV30(true);
  setStatus('Автосохранённая копия удалена');
 }
}

// Opening another project intentionally establishes a new baseline and removes
// any stale recovery copy from the previous document.
const kbAutosaveReadProjectFileV30=kbReadProjectFile;
kbReadProjectFile=async function(...args){
 await kbAutosaveReadProjectFileV30(...args);
 kbAutosaveResetBaselineV30(true);
};

try{
 window.chrome?.webview?.addEventListener('message',e=>{
  const m=e.data;
  if(typeof m!=='string')return;
  if(m==='KB911_AUTOSAVE_SAVED'){
   if(kbAutosavePendingStateV30)kbAutosaveLastStateV30=kbAutosavePendingStateV30;
   kbAutosavePendingStateV30=null;kbAutosaveNativeBusyV30=false;return;
  }
  if(m==='KB911_AUTOSAVE_ERROR'){
   kbAutosavePendingStateV30=null;kbAutosaveNativeBusyV30=false;return;
  }
  const prefix='KB911_AUTOSAVE_RECOVERY|';
  if(!m.startsWith(prefix))return;
  try{kbAutosaveRestoreV30(JSON.parse(m.slice(prefix.length)))}catch(err){
   console.error(err);kbAutosavePostV30('KB911_AUTOSAVE_CLEAR');
   kbAutosaveResetBaselineV30(false);setStatus('Повреждённая автокопия удалена');
  }
 });
}catch{}

// A few seconds is fast enough for crash recovery without continuously
// serializing large image-heavy projects while the user is dragging objects.
setInterval(kbAutosaveTickV30,6000);
'''
replace_once(anchor, anchor + code)

# Native Explorer-open callback is created after init.  When a .kb911 file is
# explicitly opened from Windows, it is a deliberate new baseline.
native_open = "window.KB911_openProjectText=async function(text,name=''){const data=JSON.parse(text);kbProject=kbUnpackProject(data);kbEnsureProjectSettings();kbLoadSheet(0);kbHistory=[kbHistoryState()];kbHistoryIndex=0;setStatus('Проект открыт: '+(name||kbProject.name))};"
native_open_v30 = "window.KB911_openProjectText=async function(text,name=''){const data=JSON.parse(text);kbProject=kbUnpackProject(data);kbEnsureProjectSettings();kbLoadSheet(0);kbHistory=[kbHistoryState()];kbHistoryIndex=0;kbAutosaveResetBaselineV30(true);setStatus('Проект открыт: '+(name||kbProject.name))};"
replace_once(native_open, native_open_v30)

for token in [
    'KB911_V30_AUTOSAVE_RECOVERY',
    'KB911_AUTOSAVE_SAVE|',
    'KB911_AUTOSAVE_RECOVERY|',
    'kbAutosaveMarkCleanV30()',
    'setInterval(kbAutosaveTickV30,6000)'
]:
    if token not in s:
        raise SystemExit('autosave v30 guard failed: '+token)

p.write_text(s, encoding='utf-8', newline='')
print('Safe autosave/recovery UI layer installed')
