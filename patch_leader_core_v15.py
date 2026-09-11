from pathlib import Path
p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='// KB911_V15_LEADER_CORE_FIX'
if marker in s:
    print('v15 already applied'); raise SystemExit(0)
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end not found')
code=r'''

// KB911_V15_LEADER_CORE_FIX
// Root cause: leader handles existed, but drawSelection() never called
// drawLeaderHandles() for a selected leader. Therefore only whole-object move
// worked. Integrate leader into the common selection path.
const kbDrawSelectionBeforeLeaderV15=drawSelection;
drawSelection=function(){
 if(selected?.dataset?.type==='leader'){
   clearUI();
   drawLeaderHandles(selected);
   return;
 }
 kbDrawSelectionBeforeLeaderV15();
};

// Keep leader selected after simple click, show its handles immediately, and
// preserve whole-leader move handled by the existing leader runtime.
paper.addEventListener('pointerup',e=>{
 const obj=groupType(e.target);
 if(obj?.dataset?.type==='leader' && !kbLeaderEdit){
   selected=obj;lastEditable=obj;drawSelection();
 }
},false);

// Reliable draggable leader popup. Use pointer capture on the header itself,
// independent of the old dimension/text popup drag state.
let kbLeaderPopupMoveV15=null;
const kbLeaderPopupV15=$('leaderPopup'),kbLeaderHeaderV15=$('leaderPopupHeader');
if(!kbLeaderPopupV15||!kbLeaderHeaderV15)throw new Error('leader popup/header missing');
kbLeaderHeaderV15.addEventListener('pointerdown',e=>{
 if(e.target.id==='leaderPopupClose')return;
 const r=kbLeaderPopupV15.getBoundingClientRect();
 kbLeaderPopupMoveV15={id:e.pointerId,dx:e.clientX-r.left,dy:e.clientY-r.top};
 try{kbLeaderHeaderV15.setPointerCapture(e.pointerId)}catch{}
 e.preventDefault();e.stopImmediatePropagation();
},true);
kbLeaderHeaderV15.addEventListener('pointermove',e=>{
 const d=kbLeaderPopupMoveV15;if(!d||d.id!==e.pointerId)return;
 kbLeaderPopupV15.style.left=Math.max(0,Math.min(innerWidth-kbLeaderPopupV15.offsetWidth,e.clientX-d.dx))+'px';
 kbLeaderPopupV15.style.top=Math.max(0,Math.min(innerHeight-kbLeaderPopupV15.offsetHeight,e.clientY-d.dy))+'px';
 e.preventDefault();e.stopImmediatePropagation();
},true);
function kbEndLeaderPopupMoveV15(e){
 if(!kbLeaderPopupMoveV15)return;
 try{kbLeaderHeaderV15.releasePointerCapture(kbLeaderPopupMoveV15.id)}catch{}
 kbLeaderPopupMoveV15=null;
 e?.stopImmediatePropagation?.();
}
kbLeaderHeaderV15.addEventListener('pointerup',kbEndLeaderPopupMoveV15,true);
kbLeaderHeaderV15.addEventListener('pointercancel',kbEndLeaderPopupMoveV15,true);

// Diagnostics/build guards exposed in the runtime so a future regression is
// easy to detect from the final embedded HTML.
window.KB911_LEADER_CORE_V15={selection:true,popupDrag:true,handles:['p1','p2','p3','text']};
'''
s=s[:idx]+code+s[idx:]
for token in ['KB911_V15_LEADER_CORE_FIX','drawLeaderHandles(selected)','kbLeaderPopupMoveV15','KB911_LEADER_CORE_V15']:
    if token not in s: raise SystemExit('v15 token missing '+token)
p.write_text(s,encoding='utf-8',newline='')
print('v15 leader selection + popup drag core fix applied')
