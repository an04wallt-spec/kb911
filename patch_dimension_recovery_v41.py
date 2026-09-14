from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')
marker = 'KB911_V41_DIM_LINE_RECOVERY_UI'
if marker in s:
    print('v41 follow-up already applied')
    raise SystemExit(0)

style = r'''<style id="kb911V41RecoveryStyle">
/* KB911_V41_DIM_LINE_RECOVERY_UI */
#kbRecoveryOverlayV41{position:fixed;inset:0;z-index:10000;background:rgba(0,0,0,.28);display:flex;align-items:center;justify-content:center;padding:20px}
#kbRecoveryDialogV41{width:min(440px,calc(100vw - 40px));background:#fff;border:1px solid #c8ccd2;border-radius:10px;box-shadow:0 18px 60px rgba(0,0,0,.30);font-family:Bahnschrift,Segoe UI,Arial,sans-serif;color:#20242a}
#kbRecoveryDialogV41 .kb-rec-head{padding:14px 16px 10px;font-size:17px;font-weight:700;border-bottom:1px solid #e3e5e8}
#kbRecoveryDialogV41 .kb-rec-body{padding:14px 16px;line-height:1.42;font-size:14px}
#kbRecoveryDialogV41 .kb-rec-meta{margin-top:9px;padding:9px 10px;background:#f6f7f9;border-radius:7px;font-size:13px;color:#4a515b}
#kbRecoveryDialogV41 .kb-rec-actions{display:flex;gap:9px;justify-content:flex-end;padding:12px 16px;border-top:1px solid #e3e5e8}
#kbRecoveryDeleteV41{margin-right:auto;border-color:#c94747;color:#a62d2d;background:#fff}
#kbRecoveryRestoreV41{font-weight:700}
.kb-dim-line-handle-v40{cursor:move}
</style>
'''
if s.count('</head>') != 1:
    raise SystemExit('v41: expected one </head>')
s = s.replace('</head>', style + '</head>', 1)

anchor = '\nsetPage();\ninitKB911Project();\nkbHistoryStart();'
if s.count(anchor) != 1:
    raise SystemExit(f'v41: startup anchor count {s.count(anchor)}')

code = r'''

// KB911_V41_DIM_LINE_RECOVERY_UI
// 1) The middle control belongs exclusively to the dimension-line offset.
// Do not give it the legacy dim-tail-handle class: that class changes witness
// line tails in the v38 interaction layer and must never receive this gesture.
kbDrawAnchoredDimHandlesV40=function(g,hoverOnly=false){
 const m=kbAnchoredDimGeomV40(g),r=hoverOnly?.58:.68;
 [[m.a1,'start'],[m.a2,'end']].forEach(([p,k])=>paper.appendChild(el('circle',{cx:p.x,cy:p.y,r,class:`dim-end-handle dim-handle-${k} kb-dim-anchor-v40 selection-ui`,'data-owner':g.dataset.id,'data-anchor-v40':k})));
 paper.appendChild(el('circle',{cx:(m.q1.x+m.q2.x)/2,cy:(m.q1.y+m.q2.y)/2,r,class:'kb-dim-line-handle-v40 selection-ui','data-owner':g.dataset.id,'data-line-handle-v40':'1'}));
};

// 2) Opening the dimension properties is explicit after the third click that
// fixes the line position. This restores the stable-v38 "enter size now" flow.
const kbCreateAnchoredDimensionBeforeV41=kbCreateAnchoredDimensionV40;
kbCreateAnchoredDimensionV40=function(p1,p2,offset){
 const g=kbCreateAnchoredDimensionBeforeV41(p1,p2,offset);
 if(g){
  selected=g;syncDimProps();openDimPopup();drawSelection();
  setStatus('Размер создан. Укажите значение размера');
  setTimeout(()=>{try{$('dimText').focus();$('dimText').select()}catch{}},0);
 }
 return g;
};

// 3) Replace the browser confirm with a small KB911 recovery dialog. The user
// gets an explicit permanent-delete button; no Windows folders are exposed.
function kbCloseRecoveryDialogV41(){document.getElementById('kbRecoveryOverlayV41')?.remove()}
kbAutosaveRestoreV30=function(envelope){
 if(!envelope||envelope.app!=='KB911'||envelope.kind!=='autosave'||typeof envelope.state!=='string')throw new Error('Некорректная автокопия');
 kbCloseRecoveryDialogV41();
 const d=new Date(+envelope.savedAt||0),stamp=Number.isFinite(d.getTime())&&d.getTime()>0?d.toLocaleString('ru-RU'):'';
 const name=String(envelope.projectName||'Проект KB911');
 const overlay=document.createElement('div');overlay.id='kbRecoveryOverlayV41';
 const box=document.createElement('div');box.id='kbRecoveryDialogV41';
 const head=document.createElement('div');head.className='kb-rec-head';head.textContent='Восстановление проекта';
 const body=document.createElement('div');body.className='kb-rec-body';
 const intro=document.createElement('div');intro.textContent='Найдена автосохранённая копия предыдущей работы.';
 const meta=document.createElement('div');meta.className='kb-rec-meta';
 const nameRow=document.createElement('div');nameRow.textContent='Проект: '+name;meta.appendChild(nameRow);
 if(stamp){const dateRow=document.createElement('div');dateRow.textContent='Автосохранение: '+stamp;meta.appendChild(dateRow)}
 body.appendChild(intro);body.appendChild(meta);
 const actions=document.createElement('div');actions.className='kb-rec-actions';
 const del=document.createElement('button');del.id='kbRecoveryDeleteV41';del.type='button';del.textContent='Удалить автосохранение';
 const restore=document.createElement('button');restore.id='kbRecoveryRestoreV41';restore.type='button';restore.className='primary';restore.textContent='Восстановить';
 actions.appendChild(del);actions.appendChild(restore);box.appendChild(head);box.appendChild(body);box.appendChild(actions);overlay.appendChild(box);document.body.appendChild(overlay);
 restore.onclick=()=>{
  kbCloseRecoveryDialogV41();
  kbHistoryRestore(envelope.state);kbHistory=[envelope.state];kbHistoryIndex=0;
  kbAutosaveLastStateV30=envelope.state;kbAutosavePendingStateV30=null;kbAutosaveNativeBusyV30=false;
  setStatus('Автосохранённая копия восстановлена');
 };
 del.onclick=()=>{
  kbCloseRecoveryDialogV41();
  kbAutosaveResetBaselineV30(true);
  setStatus('Автосохранение удалено');
 };
};
'''

s = s.replace(anchor, code + anchor, 1)

for token in [
    marker,
    "class:'kb-dim-line-handle-v40 selection-ui'",
    "openDimPopup();drawSelection()",
    "del.textContent='Удалить автосохранение'",
    "kbAutosaveResetBaselineV30(true)"
]:
    if token not in s:
        raise SystemExit('v41 guard failed: ' + token)

# Strong guard: the new anchored middle handle must no longer carry the legacy
# tail-handle class anywhere in the V41 override.
fragment = s[s.index('// KB911_V41_DIM_LINE_RECOVERY_UI'):s.index('setPage();', s.index('// KB911_V41_DIM_LINE_RECOVERY_UI'))]
if "dim-tail-handle kb-dim-line-handle-v40" in fragment:
    raise SystemExit('v41: legacy tail class still attached to line handle')

p.write_text(s, encoding='utf-8', newline='')
print('v41: dimension line drag isolated, dimension popup restored, autosave delete dialog added')
