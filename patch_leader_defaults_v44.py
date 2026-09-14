from pathlib import Path
p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V44_LEADER_DEFAULTS'
if marker in s:
    print('v44 leader defaults already applied'); raise SystemExit(0)

anchor='\nsetPage();\ninitKB911Project();\nkbHistoryStart();'
if s.count(anchor)!=1: raise SystemExit('v44 leader startup anchor')

code=r'''
// KB911_V44_LEADER_DEFAULTS
const kbLeaderBuiltV44={shelf:'40',font:'Bahnschrift',fontSize:'4',bold:true,italic:false,arrow:'slim',arrowSize:'5',arrowAngle:'10',lineWidth:'0.40',lineColor:'#111111',textColor:'#111111'};
let kbLeaderDefaultsV44=Object.assign({},kbLeaderBuiltV44,readStore('mm.leaderDefaults.v1'));
function kbSaveLeaderDefaultsV44(g){
 if(!g||g.dataset.type!=='leader')return;
 kbLeaderDefaultsV44={shelf:g.dataset.shelf||'40',font:g.dataset.font||'Bahnschrift',fontSize:g.dataset.fontSize||'4',bold:g.dataset.bold==='1',italic:g.dataset.italic==='1',arrow:g.dataset.arrow||'slim',arrowSize:g.dataset.arrowSize||'5',arrowAngle:g.dataset.arrowAngle||'10',lineWidth:g.dataset.lineWidth||'0.40',lineColor:g.dataset.lineColor||'#111111',textColor:g.dataset.textColor||'#111111'};
 saveStore('mm.leaderDefaults.v1',kbLeaderDefaultsV44);
}
createLeader=function(p1,p2){
 const d=kbLeaderDefaultsV44,dir=p2.x>=p1.x?1:-1;
 const g=el('g',{'data-type':'leader','data-id':uid++,'data-p1':`${p1.x},${p1.y}`,'data-p2':`${p2.x},${p2.y}`,'data-dir':String(dir),'data-shelf':d.shelf||'40','data-value':'Сноска','data-font':d.font||'Bahnschrift','data-font-size':d.fontSize||'4','data-bold':d.bold?'1':'0','data-italic':d.italic?'1':'0','data-arrow':d.arrow||'slim','data-arrow-size':d.arrowSize||'5','data-arrow-angle':d.arrowAngle||'10','data-line-width':d.lineWidth||'0.40','data-line-color':d.lineColor||'#111111','data-text-color':d.textColor||'#111111'});
 appendContent(g);renderLeader(g);selected=g;lastEditable=g;drawSelection();openLeaderPopup(g);setStatus('Сноска создана');
};
const kbLeaderPopupV44=$('leaderPopup');
if(kbLeaderPopupV44){
 const capture=()=>{const g=selected?.dataset.type==='leader'?selected:null;if(g)setTimeout(()=>{if(g.isConnected)kbSaveLeaderDefaultsV44(g)},0)};
 kbLeaderPopupV44.addEventListener('input',capture);
 kbLeaderPopupV44.addEventListener('change',capture);
}
const kbLeaderOkV44=$('leaderOk');
if(kbLeaderOkV44)kbLeaderOkV44.addEventListener('click',()=>{if(selected?.dataset.type==='leader')kbSaveLeaderDefaultsV44(selected)},true);
if(kbLeaderOkV44&&!document.getElementById('leaderSetDefaultV44')){
 const b=document.createElement('button');b.id='leaderSetDefaultV44';b.type='button';b.textContent='По умолчанию';
 b.onclick=()=>{if(selected?.dataset.type!=='leader')return;kbSaveLeaderDefaultsV44(selected);setStatus('Настройки сноски сохранены по умолчанию')};
 kbLeaderOkV44.parentElement?.insertBefore(b,kbLeaderOkV44);
}
'''
s=s.replace(anchor,code+anchor,1)
for t in [marker,"readStore('mm.leaderDefaults.v1')",'createLeader=function(p1,p2)','leaderSetDefaultV44']:
    if t not in s: raise SystemExit('v44 leader guard '+t)
seg=s[s.index('createLeader=function(p1,p2)'):s.index('const kbLeaderPopupV44')]
if 'dimDefaults' in seg: raise SystemExit('v44 leader creator still uses dimension defaults')
p.write_text(s,encoding='utf-8',newline='')
print('v44: independent leader defaults installed')
