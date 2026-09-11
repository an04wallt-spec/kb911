from pathlib import Path
p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='// KB911_V12_EDITING_CORE'
if marker in s:
    print('editing core already applied')
    raise SystemExit(0)

# Restore text double-click to the last known-good behavior: open properties AND
# the live editor, instead of only opening the properties window.
old="paper.addEventListener('dblclick',e=>{const obj=groupType(e.target);if(!obj)return;e.preventDefault();if(obj.dataset.type==='text'){select(obj);setTool('text-edit',true);syncTextProps();openTextPopup();setStatus('Редактирование надписи')}else if(obj.dataset.type==='dimension'){select(obj);setTool('dimension-edit',true);syncDimProps();openDimPopup()}else if(obj.dataset.type==='image'){drag=null;imageResize=null;activeImage=obj;select(obj);tool='image-edit';setStatus('Режим картинки включён двойным кликом: теперь её можно перемещать или менять размер. Esc — зафиксировать')}});"
new="paper.addEventListener('dblclick',e=>{const obj=groupType(e.target);if(!obj)return;e.preventDefault();if(obj.dataset.type==='text'){select(obj);setTool('text-edit',true);syncTextProps();openTextPopup();editText(obj);setStatus('Редактирование надписи')}else if(obj.dataset.type==='dimension'){select(obj);setTool('dimension-edit',true);syncDimProps();openDimPopup();setTimeout(()=>{$('dimText').focus();$('dimText').select()},0)}else if(obj.dataset.type==='image'){drag=null;imageResize=null;activeImage=obj;select(obj);tool='image-edit';setStatus('Режим картинки включён двойным кликом: теперь её можно перемещать или менять размер. Esc — зафиксировать')}});"
if old not in s: raise SystemExit('base dblclick handler not found')
s=s.replace(old,new,1)

# Put the editing event bindings into the proven core section, before project
# initialization. Do not rely on any late repair block running successfully.
anchor="$('imageOpacity').oninput="
if anchor not in s: raise SystemExit('core image property anchor not found')
core=r'''
// KB911_V12_EDITING_CORE
const kbDimInputMap=[['dimPrefix','prefix'],['dimText','value'],['dimSuffix','suffix'],['arrowStyle','arrow'],['arrowAngle','arrowAngle'],['arrowSize','arrowSize'],['tailSize','tailSize'],['lineWidth','lineWidth'],['lineColor','lineColor'],['fontFamily','font'],['fontSize','fontSize'],['textColor','textColor']];
for(const [id,key] of kbDimInputMap){
 const n=$(id);if(!n)continue;
 const fn=()=>{if(selected?.dataset?.type!=='dimension')return;selected.dataset[key]=n.value;renderDim(selected);drawSelection();try{captureDimDefaults(selected)}catch{}};
 n.oninput=fn;n.onchange=fn;
}
for(const [id,key] of [['fontBold','bold'],['fontItalic','italic']]){
 const n=$(id);if(!n)continue;n.onchange=()=>{if(selected?.dataset?.type!=='dimension')return;selected.dataset[key]=n.checked?'1':'0';renderDim(selected);drawSelection();try{captureDimDefaults(selected)}catch{}};
}
const kbTextInputMap=[['textValue','value'],['textBoxW','w'],['textBoxH','h'],['textFont','font'],['textSize','fontSize'],['textAngle','angle'],['textAlign','align'],['textFill','textColor'],['textBg','bg'],['textBgOpacity','bgOpacity']];
for(const [id,key] of kbTextInputMap){
 const n=$(id);if(!n)continue;
 const fn=()=>{if(selected?.dataset?.type!=='text')return;selected.dataset[key]=n.value;renderText(selected);drawSelection();const ta=document.getElementById('liveTextEditor');if(ta&&ta.isConnected){if(key==='fontSize')ta.style.fontSize=(+n.value||4)/page.w*paper.getBoundingClientRect().width+'px';if(key==='font')ta.style.fontFamily=n.value;if(key==='value')ta.value=n.value;}};
 n.oninput=fn;n.onchange=fn;
}
for(const [id,key] of [['textBold','bold'],['textItalic','italic'],['textBorder','border']]){
 const n=$(id);if(!n)continue;n.onchange=()=>{if(selected?.dataset?.type!=='text')return;selected.dataset[key]=n.checked?'1':'0';renderText(selected);drawSelection();};
}
'''
s=s.replace(anchor,core+'\n'+anchor,1)

# Build guards for exactly the controls the user reported broken.
for token in [marker,"['dimText','value']","['fontSize','fontSize']","['textSize','fontSize']","editText(obj)"]:
    if token not in s: raise SystemExit('editing core guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('Editing core v12 restored in main runtime section')
