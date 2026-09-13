from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V39_AUTO_DIMENSION_FLOW'
if marker in s:
    print('v39 auto dimension flow already applied')
    raise SystemExit(0)

anchor='\nsetPage();\ninitKB911Project();\nkbHistoryStart();'
if s.count(anchor)!=1: raise SystemExit(f'v39 flow: startup anchor count {s.count(anchor)}')

code=r'''

// KB911_V39_AUTO_DIMENSION_FLOW
// Once an image is calibrated, creating dimensions becomes a measuring workflow:
// the value is calculated immediately and the sticky Dimension tool stays active.
// Full settings remain available later by double-clicking the dimension.
const kbCreateDimBaseV39=createDim;
createDim=function(p1,p2){
 const calibrated=kbMeasureFindImageForSegmentV39(p1,p2,true);
 kbCreateDimBaseV39(p1,p2);
 const g=selected?.dataset?.type==='dimension'?selected:null;
 if(!g||!calibrated)return;
 g.dataset.autoValue='1';g.dataset.calImageId=String(calibrated.dataset.id);
 const v=kbMeasureValueV39(g,calibrated);if(v!=null)g.dataset.value=kbMeasureFormatV39(v,calibrated);
 renderDim(g);$('dimText').value=g.dataset.value||'';kbMeasureSyncDimModeUiV39(g);
 setTimeout(()=>{
  if(!g.isConnected||g.dataset.autoValue!=='1')return;
  if(document.activeElement===$('dimText'))document.activeElement.blur();
  closeDimPopup();
  if(selected===g)clearSelection();
  try{kbHistorySchedule(0)}catch{}
  if(typeof kbResumeStickyToolV31==='function')kbResumeStickyToolV31();else setTool('dimension',true);
  setStatus(`Авторазмер ${g.dataset.value||''} мм. Размер остаётся активным — наносите следующий`);
 },0);
};
'''
s=s.replace(anchor,code+anchor,1)

for token in [marker,'const kbCreateDimBaseV39=createDim',"g.dataset.autoValue='1'",'kbResumeStickyToolV31()', 'Авторазмер ${g.dataset.value']:
    if token not in s: raise SystemExit('v39 flow guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v39: calibrated dimensions place continuously without forcing the settings popup')
