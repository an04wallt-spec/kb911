from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='// KB911_V11_EDITING_REPAIR'
if marker in s:
    print('editing repair already applied')
    raise SystemExit(0)

idx=s.rfind('</script>')
if idx<0:
    raise SystemExit('closing script tag missing')

patch=r'''
// KB911_V11_EDITING_REPAIR
(function(){
  const byId=id=>document.getElementById(id);

  function activateDimensionEditor(g){
    if(!g||g.dataset?.type!=='dimension')return;
    selected=g;lastEditable=g;
    try{setTool('dimension-edit',true)}catch{tool='dimension-edit'}
    try{syncDimProps()}catch{}
    try{drawSelection()}catch{}
    try{openDimPopup()}catch{}
    const f=byId('dimText');
    if(f)setTimeout(()=>{try{f.focus();f.select()}catch{}},0);
  }
  function activateTextEditor(g){
    if(!g||g.dataset?.type!=='text')return;
    selected=g;lastEditable=g;
    try{setTool('text-edit',true)}catch{tool='text-edit'}
    try{syncTextProps()}catch{}
    try{drawSelection()}catch{}
    try{openTextPopup()}catch{}
  }

  // Editing is deliberately double-click only. Capture phase makes this the
  // authoritative behavior even if older handlers remain in the generated app.
  paper.addEventListener('dblclick',e=>{
    const obj=groupType(e.target);
    if(!obj)return;
    if(obj.dataset.type==='dimension'){
      e.preventDefault();e.stopImmediatePropagation();activateDimensionEditor(obj);return;
    }
    if(obj.dataset.type==='text'){
      e.preventDefault();e.stopImmediatePropagation();activateTextEditor(obj);return;
    }
  },true);

  function bindInput(id,fn){
    const n=byId(id);if(!n)return;
    n.addEventListener('input',fn);
    n.addEventListener('change',fn);
  }
  function updateDim(id,key){
    bindInput(id,()=>{
      if(selected?.dataset?.type!=='dimension')return;
      const n=byId(id);if(!n)return;
      selected.dataset[key]=n.value;
      renderDim(selected);drawSelection();
      try{captureDimDefaults(selected)}catch{}
    });
  }
  function updateDimCheck(id,key){
    const n=byId(id);if(!n)return;
    const fn=()=>{
      if(selected?.dataset?.type!=='dimension')return;
      selected.dataset[key]=n.checked?'1':'0';
      renderDim(selected);drawSelection();
      try{captureDimDefaults(selected)}catch{}
    };
    n.addEventListener('change',fn);
  }
  [['dimPrefix','prefix'],['dimText','value'],['dimSuffix','suffix'],['arrowStyle','arrow'],['arrowAngle','arrowAngle'],['arrowSize','arrowSize'],['tailSize','tailSize'],['lineWidth','lineWidth'],['lineColor','lineColor'],['fontFamily','font'],['fontSize','fontSize'],['textColor','textColor']].forEach(([id,key])=>updateDim(id,key));
  updateDimCheck('fontBold','bold');
  updateDimCheck('fontItalic','italic');

  function updateText(id,key){
    bindInput(id,()=>{
      if(selected?.dataset?.type!=='text')return;
      const n=byId(id);if(!n)return;
      selected.dataset[key]=n.value;
      renderText(selected);drawSelection();
      const ta=byId('liveTextEditor');
      if(ta&&ta.isConnected){
        if(key==='fontSize')ta.style.fontSize=(+n.value||4)/page.w*paper.getBoundingClientRect().width+'px';
        if(key==='font')ta.style.fontFamily=n.value;
      }
    });
  }
  [['textValue','value'],['textBoxW','w'],['textBoxH','h'],['textFont','font'],['textSize','fontSize'],['textAngle','angle'],['textAlign','align'],['textFill','textColor'],['textBg','bg'],['textBgOpacity','bgOpacity']].forEach(([id,key])=>updateText(id,key));

  const tb=byId('textBold');
  if(tb)tb.addEventListener('change',()=>{
    if(selected?.dataset?.type!=='text')return;
    selected.dataset.bold=tb.checked?'1':'0';renderText(selected);drawSelection();
  });
  const ti=byId('textItalic');
  if(ti)ti.addEventListener('change',()=>{
    if(selected?.dataset?.type!=='text')return;
    selected.dataset.italic=ti.checked?'1':'0';renderText(selected);drawSelection();
  });
  const to=byId('textOutline');
  if(to)to.addEventListener('change',()=>{
    if(selected?.dataset?.type!=='text')return;
    selected.dataset.outline=to.checked?'1':'0';renderText(selected);drawSelection();
  });

  // Keep creation behavior predictable: immediately expose the value field for
  // a newly-created dimension and the property window for a newly-created text.
  const oldCreateDim=createDim;
  createDim=function(p1,p2){
    oldCreateDim(p1,p2);
    const g=selected?.dataset?.type==='dimension'?selected:null;
    if(g)activateDimensionEditor(g);
  };
  const oldCreateTextBox=createTextBox;
  createTextBox=function(x,y,w,h){
    oldCreateTextBox(x,y,w,h);
    const g=selected?.dataset?.type==='text'?selected:null;
    if(g){try{syncTextProps();openTextPopup()}catch{}}
  };
})();
'''

s=s[:idx]+patch+s[idx:]
for token in ['KB911_V11_EDITING_REPAIR','activateDimensionEditor','activateTextEditor',"['dimText','value']","['textSize','fontSize']"]:
    assert token in s, 'editing repair token missing: '+token

p.write_text(s,encoding='utf-8',newline='')
print('Editing repair v11 applied: dimension values and text properties rebound')
