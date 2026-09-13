from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')

def replace_once(old, new):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'frame settings v34: expected one anchor, got {count}: {old[:160]}')
    s = s.replace(old, new, 1)

font_anchor = '<option selected>Bahnschrift</option><option>Segoe UI</option>'
if s.count(font_anchor) != 2:
    raise SystemExit(f'frame settings v34: expected 2 font selectors, got {s.count(font_anchor)}')
s = s.replace(font_anchor, '<option selected>Bahnschrift</option><option>Gost</option><option>Segoe UI</option>')

old_hint = '''    <div class="hint">Контур <span id="frameStrokeEdit" class="frame-param" title="Двойной щелчок — изменить толщину рамки">0,3</span> мм, отступ от края листа <span id="frameInsetEdit" class="frame-param" title="Двойной щелчок — изменить отступ рамки">5</span> мм, радиус скругления <span id="frameRadiusEdit" class="frame-param" title="Двойной щелчок — изменить радиус скругления">2</span> мм. Название и логотип можно включать независимо.</div>'''
new_settings = '''    <button id="frameSettingsToggle" type="button" class="frame-settings-toggle" aria-expanded="false"><span>Настройка рамки</span><span id="frameSettingsArrow" aria-hidden="true">▾</span></button>
    <div id="frameSettingsPanel" class="frame-settings-panel" hidden>
      <div class="frame-setting-item"><div class="label">Толщина контура, мм</div><input id="frameStrokeInput" type="number" min="0.05" max="5" step="0.05" value="0.30"></div>
      <div class="frame-setting-item"><div class="label">Отступ от края, мм</div><input id="frameInsetInput" type="number" min="1" max="40" step="0.5" value="5"></div>
      <div class="frame-setting-item frame-setting-wide"><div class="label">Радиус скругления, мм</div><input id="frameRadiusInput" type="number" min="0" max="8" step="0.5" value="2"></div>
      <div class="frame-settings-subtitle">Рамка логотипа</div>
      <div class="frame-setting-item"><div class="label">Ширина, мм</div><input id="frameLogoWInput" type="number" min="5" max="200" step="0.5" value="18"></div>
      <div class="frame-setting-item"><div class="label">Высота, мм</div><input id="frameLogoHInput" type="number" min="5" max="200" step="0.5" value="18"></div>
    </div>
    <div class="hint" style="margin-top:6px">Название и логотип можно включать независимо.</div>'''
replace_once(old_hint, new_settings)

style = r'''
<style id="kbFrameSettingsStyleV34">
#framePanel .frame-settings-toggle{width:100%;margin-top:7px;display:flex;align-items:center;justify-content:space-between;text-align:left;font-weight:600}
#framePanel .frame-settings-toggle[aria-expanded="true"] #frameSettingsArrow{transform:rotate(180deg)}
#framePanel #frameSettingsArrow{display:inline-block;transition:transform .14s ease;font-size:12px}
#framePanel .frame-settings-panel{margin-top:6px;padding:8px;border:1px solid #d9dde5;border-radius:6px;background:#f8f9fb;display:grid;grid-template-columns:1fr 1fr;gap:7px}
#framePanel .frame-settings-panel[hidden]{display:none}
#framePanel .frame-setting-item input{width:100%;box-sizing:border-box}
#framePanel .frame-setting-wide{grid-column:1/-1}
#framePanel .frame-settings-subtitle{grid-column:1/-1;margin-top:2px;padding-top:7px;border-top:1px solid #e2e5eb;font-size:11px;font-weight:700;color:#475467}
</style>
'''
replace_once('</head>', style + '</head>')

replace_once(
    "let activeImage=null,imageUndo=null,imageRedo=null,saveKind='png',frameState={enabled:false,company:true,logoEnabled:false,name:'',logo:null,stroke:.3,inset:5,radius:2};",
    "let activeImage=null,imageUndo=null,imageRedo=null,saveKind='png',frameState={enabled:false,company:true,logoEnabled:false,name:'',logo:null,stroke:.3,inset:5,radius:2,logoW:18,logoH:18};"
)
replace_once(
    "const kbFrameDefaults={enabled:false,company:true,logoEnabled:false,name:'',logo:null,stroke:.3,inset:5,radius:2};",
    "const kbFrameDefaults={enabled:false,company:true,logoEnabled:false,name:'',logo:null,stroke:.3,inset:5,radius:2,logoW:18,logoH:18};"
)

old_logo = """if(showLogo){const ls=18,x=right-ls,y=inset,r=rad;if(frameState.logo){const clipId=`frameLogoClip-${uid++}`,cp=el('clipPath',{id:clipId});cp.appendChild(el('path',{d:frameLogoClipPath(x,y,ls,ls,r)}));g.appendChild(cp);g.appendChild(el('image',{href:frameState.logo,x,y,width:ls,height:ls,preserveAspectRatio:'none','clip-path':`url(#${clipId})`,'data-frame-logo':'1','data-clip-r':r}))}const d=`M ${x} ${y} L ${x} ${y+ls-r} Q ${x} ${y+ls} ${x+r} ${y+ls} L ${right} ${y+ls}`;g.appendChild(el('path',{d,fill:'none',stroke:'#111','stroke-width':sw,'stroke-linecap':'round','stroke-linejoin':'round'}))}"""
new_logo = """if(showLogo){const logoW=Math.max(5,Math.min(Math.max(5,page.w-inset*2),Number.isFinite(+frameState.logoW)?+frameState.logoW:18)),logoH=Math.max(5,Math.min(Math.max(5,page.h-inset*2),Number.isFinite(+frameState.logoH)?+frameState.logoH:18)),x=right-logoW,y=inset,r=Math.min(rad,logoW/2,logoH/2);if(frameState.logo){const clipId=`frameLogoClip-${uid++}`,cp=el('clipPath',{id:clipId});cp.appendChild(el('path',{d:frameLogoClipPath(x,y,logoW,logoH,r)}));g.appendChild(cp);g.appendChild(el('image',{href:frameState.logo,x,y,width:logoW,height:logoH,preserveAspectRatio:'none','clip-path':`url(#${clipId})`,'data-frame-logo':'1','data-clip-r':r}))}const d=`M ${x} ${y} L ${x} ${y+logoH-r} Q ${x} ${y+logoH} ${x+r} ${y+logoH} L ${right} ${y+logoH}`;g.appendChild(el('path',{d,fill:'none',stroke:'#111','stroke-width':sw,'stroke-linecap':'round','stroke-linejoin':'round'}))}"""
replace_once(old_logo, new_logo)

replace_once(
    "function saveFrameParams(){saveStore('kb911.frameParams',{stroke:frameState.stroke,inset:frameState.inset,radius:frameState.radius})}",
    "function saveFrameParams(){saveStore('kb911.frameParams',{stroke:frameState.stroke,inset:frameState.inset,radius:frameState.radius,logoW:frameState.logoW,logoH:frameState.logoH})}"
)
replace_once(
    "if(fp.radius!==undefined&&Number.isFinite(+fp.radius))frameState.radius=Math.max(0,Math.min(8,+fp.radius));refreshFrameParamLabels()",
    "if(fp.radius!==undefined&&Number.isFinite(+fp.radius))frameState.radius=Math.max(0,Math.min(8,+fp.radius));if(Number.isFinite(+fp.logoW))frameState.logoW=Math.max(5,Math.min(200,+fp.logoW));if(Number.isFinite(+fp.logoH))frameState.logoH=Math.max(5,Math.min(200,+fp.logoH));refreshFrameParamLabels()"
)

old_refresh = "function refreshFrameParamLabels(){if($('frameStrokeEdit'))$('frameStrokeEdit').textContent=fmtFrameParam(frameState.stroke);if($('frameInsetEdit'))$('frameInsetEdit').textContent=fmtFrameParam(frameState.inset);if($('frameRadiusEdit'))$('frameRadiusEdit').textContent=fmtFrameParam(frameState.radius)}"
new_refresh = """function refreshFrameParamLabels(){if($('frameStrokeEdit'))$('frameStrokeEdit').textContent=fmtFrameParam(frameState.stroke);if($('frameInsetEdit'))$('frameInsetEdit').textContent=fmtFrameParam(frameState.inset);if($('frameRadiusEdit'))$('frameRadiusEdit').textContent=fmtFrameParam(frameState.radius);if($('frameStrokeInput'))$('frameStrokeInput').value=frameState.stroke;if($('frameInsetInput'))$('frameInsetInput').value=frameState.inset;if($('frameRadiusInput'))$('frameRadiusInput').value=frameState.radius;if($('frameLogoWInput'))$('frameLogoWInput').value=frameState.logoW??18;if($('frameLogoHInput'))$('frameLogoHInput').value=frameState.logoH??18}"""
replace_once(old_refresh, new_refresh)

anchor = "$('frameEnabled').onchange="
code = r'''// KB911_V34_FRAME_SETTINGS_AND_GOST
(function(){
 const toggle=$('frameSettingsToggle'),panel=$('frameSettingsPanel'),arrow=$('frameSettingsArrow');
 if(toggle&&panel){
  toggle.onclick=()=>{const open=panel.hidden;panel.hidden=!open;toggle.setAttribute('aria-expanded',open?'true':'false');if(arrow)arrow.textContent='▾'};
 }
 const defs={
  frameStrokeInput:['stroke',.05,5,.05,2],
  frameInsetInput:['inset',1,40,.5,1],
  frameRadiusInput:['radius',0,8,.5,1],
  frameLogoWInput:['logoW',5,200,.5,1],
  frameLogoHInput:['logoH',5,200,.5,1]
 };
 for(const[id,[key,min,max,step,digits]]of Object.entries(defs)){
  const n=$(id);if(!n)continue;
  n.addEventListener('input',()=>{
   let v=Number(n.value);if(!Number.isFinite(v))return;
   v=Math.max(min,Math.min(max,Math.round(v/step)*step));frameState[key]=+v.toFixed(digits);
   saveFrameParams();renderFrame();
  });
  n.addEventListener('change',()=>{
   refreshFrameParamLabels();saveFrameParams();renderFrame();
   try{kbSyncProjectSettings()}catch{}
   try{kbHistorySchedule(0)}catch{}
  });
 }
 refreshFrameParamLabels();
})();
'''
if anchor not in s:
    raise SystemExit('frame settings v34: frame handler anchor missing')
s = s.replace(anchor, code + anchor, 1)

for token in [
    'KB911_V34_FRAME_SETTINGS_AND_GOST',
    '<option>Gost</option>',
    'id="frameSettingsToggle"',
    'id="frameLogoWInput"',
    'id="frameLogoHInput"',
    'logoW:18,logoH:18',
    'frameLogoClipPath(x,y,logoW,logoH,r)',
    "logoW:frameState.logoW,logoH:frameState.logoH"
]:
    if token not in s:
        raise SystemExit('frame settings v34 guard failed: ' + token)

p.write_text(s, encoding='utf-8', newline='')
print('v34: GOST font and collapsible frame/logo settings installed')
