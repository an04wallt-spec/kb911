from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')

def replace_once(old, new):
    global s
    if s.count(old) != 1:
        raise SystemExit(f'undo history: expected one anchor, got {s.count(old)}: {old[:90]}')
    s = s.replace(old, new, 1)

replace_once('id="undoImage" class="mini" title="Вернуть картинку обратно" aria-label="Вернуть картинку обратно"',
             'id="undoImage" class="mini" title="Отменить последнее действие" aria-label="Отменить последнее действие"')
replace_once('id="redoImage" class="mini" title="Вернуть отменённое положение картинки" aria-label="Вернуть отменённое положение картинки"',
             'id="redoImage" class="mini" title="Вернуть отменённое действие" aria-label="Вернуть отменённое действие"')

anchor = 'setPage();\ninitKB911Project();'
code = r'''
// KB911_V27_DOCUMENT_HISTORY
// History is local to this editing session. The project format is unchanged.
let kbHistory=[],kbHistoryIndex=-1,kbHistoryBusy=false,kbHistoryTimer=null;
let kbHistoryPointer=false,kbHistoryObserver=null;
function kbHistorySvg(){
 return [...paper.children].filter(n=>
  !n.classList?.contains('selection-ui') && n.dataset?.type!=='frame' &&
  n!==dimPreview && n!==textPreview && n!==leaderPreview &&
  n!==simpleLinePreview && n!==pasteDraft?.ghost
 ).map(n=>n.outerHTML).join('');
}
function kbHistoryState(){
 const project=kbClone(kbProject);
 project.name=$('projectName').value||project.name;
 project.current=kbProject.current;
 project.settings=kbSettingsFromUI();
 const current=project.sheets[project.current];
 if(current){
  current.name=$('projectSheetName').value||current.name;
  current.paperSize=$('paperSize').value;
  current.orientation=$('orientation').value;
  current.frame=kbClone(frameState);
  current.svg=kbHistorySvg();
 }
 return JSON.stringify({project,dimDefaults,textDefaults,simpleLineDefaults});
}
function kbHistoryCommit(){
 if(kbHistoryBusy||!kbProject?.sheets?.length||document.body.classList.contains('exporting'))return;
 if(dimDraft||textDraft||leaderDraft||simpleLineDraft||pasteDraft)return;
 const state=kbHistoryState();
 if(state===kbHistory[kbHistoryIndex])return;
 kbHistory.splice(kbHistoryIndex+1);
 kbHistory.push(state);
 if(kbHistory.length>35)kbHistory.shift();
 kbHistoryIndex=kbHistory.length-1;
}
function kbHistorySchedule(delay=380){
 if(kbHistoryBusy)return;
 clearTimeout(kbHistoryTimer);
 kbHistoryTimer=setTimeout(()=>{
  if(kbHistoryPointer){kbHistorySchedule(600);return}
  kbHistoryCommit();
 },delay);
}
function kbHistoryRestore(state){
 const data=JSON.parse(state);
 kbHistoryBusy=true;
 clearTimeout(kbHistoryTimer);
 kbHistoryObserver?.disconnect();
 try{
  document.getElementById('liveTextEditor')?.blur();
  closeDimPopup();closeTextPopup();
  if(typeof closeLeaderPopup==='function')closeLeaderPopup();
  if(typeof closeSimpleLinePopup==='function')closeSimpleLinePopup();
  dimDraft=null;dimPreview?.remove();dimPreview=null;
  textDraft=null;textPreview?.remove();textPreview=null;
  leaderDraft=null;leaderPreview?.remove();leaderPreview=null;
  simpleLineDraft=null;simpleLinePreview?.remove();simpleLinePreview=null;
  drag=null;endpointDrag=null;tailDrag=null;imageResize=null;textResize=null;
  activeImage=null;imageUndo=null;imageRedo=null;selected=null;hoverDim=null;hoverText=null;
  kbProject=data.project;
  dimDefaults=data.dimDefaults;textDefaults=data.textDefaults;simpleLineDefaults=data.simpleLineDefaults;
  saveStore('mm.dimDefaults.v2',dimDefaults);
  $('projectName').value=kbProject.name;
  const index=kbProject.current;
  kbLoadSheet(index);
  setTool(null,true);
 }finally{
  kbHistoryObserver?.takeRecords();
  kbHistoryObserver?.observe(paper,{subtree:true,childList:true,attributes:true,characterData:true});
  kbHistoryBusy=false;
 }
}
function kbHistoryStep(direction){
 kbHistoryPointer=false;
 kbHistoryCommit();
 const next=kbHistoryIndex+direction;
 if(next<0||next>=kbHistory.length){setStatus(direction<0?'Нечего отменять':'Нечего возвращать');return}
 kbHistoryIndex=next;
 kbHistoryRestore(kbHistory[next]);
 setStatus(direction<0?'Последнее действие отменено':'Действие возвращено');
}
$('undoImage').onclick=()=>kbHistoryStep(-1);
$('redoImage').onclick=()=>kbHistoryStep(1);

function kbHistoryRelevantMutation(m){
 const n=m.type==='childList'?(m.addedNodes[0]||m.removedNodes[0]||m.target):m.target;
 const node=n?.nodeType===1?n:n?.parentElement;
 if(!node)return false;
 if(node===paper)return m.type==='childList' && [...m.addedNodes,...m.removedNodes].some(x=>
   x.nodeType===1 && !x.classList?.contains('selection-ui') && x.dataset?.type!=='frame' &&
   x!==dimPreview && x!==textPreview && x!==leaderPreview && x!==simpleLinePreview
 );
 return !node.closest?.('.selection-ui,[data-type="frame"]') &&
        ![dimPreview,textPreview,leaderPreview,simpleLinePreview].some(x=>x&&(node===x||x.contains(node)));
}
function kbHistoryStart(){
 kbHistory=[kbHistoryState()];kbHistoryIndex=0;
 kbHistoryObserver=new MutationObserver(records=>{
  if(!kbHistoryBusy && records.some(kbHistoryRelevantMutation))kbHistorySchedule();
 });
 kbHistoryObserver.observe(paper,{subtree:true,childList:true,attributes:true,characterData:true});
 window.addEventListener('pointerdown',e=>{
  if(e.target.closest?.('#undoImage,#redoImage'))return;
  kbHistoryCommit();kbHistoryPointer=true;
 },true);
 window.addEventListener('pointerup',()=>{
  kbHistoryPointer=false;setTimeout(kbHistoryCommit,0);
 },true);
 window.addEventListener('pointercancel',()=>{
  kbHistoryPointer=false;kbHistorySchedule(0);
 },true);
 document.addEventListener('input',e=>{
  if(e.target.matches?.('#projectName,#projectSheetName,#frameCompanyName'))kbHistorySchedule(500);
 });
 document.addEventListener('change',e=>{
  if(e.target.matches?.('#paperSize,#orientation,#frameEnabled,#frameCompanyEnabled,#frameLogoEnabled,#frameLogoFile,#projectSheet'))kbHistorySchedule(e.target.id==='frameLogoFile'?950:0);
 });
 document.addEventListener('click',e=>{
  if(e.target.closest?.('#projectSheetAdd,#projectSheetDup,#projectSheetDel,#frameLogoClear'))kbHistorySchedule(0);
 });
 const readProject=kbReadProjectFile;
 kbReadProjectFile=async function(...args){await readProject(...args);kbHistory=[kbHistoryState()];kbHistoryIndex=0};
}
'''
replace_once(anchor, code+'\n'+anchor+'\nkbHistoryStart();')

# A native project open callback is assigned after initialization; reset the
# session history once the imported project has actually loaded.
replace_once('window.KB911_openProjectText=async function(text,name=\'\'){const data=JSON.parse(text);kbProject=kbUnpackProject(data);kbEnsureProjectSettings();kbLoadSheet(0);setStatus(\'Проект открыт: \'+(name||kbProject.name))};',
             'window.KB911_openProjectText=async function(text,name=\'\'){const data=JSON.parse(text);kbProject=kbUnpackProject(data);kbEnsureProjectSettings();kbLoadSheet(0);kbHistory=[kbHistoryState()];kbHistoryIndex=0;setStatus(\'Проект открыт: \'+(name||kbProject.name))};')

p.write_text(s,encoding='utf-8',newline='')
print('Universal document undo/redo installed')
