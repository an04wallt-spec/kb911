from pathlib import Path

p=Path('app/KB911.html')
s=p.read_text(encoding='utf-8')
marker='KB911_V50_SESSION_ONLY_DIMENSION_DEFAULTS'
if marker in s:
    print('v50 already applied')
    raise SystemExit(0)

anchor='\nsetPage();\ninitKB911Project();\nkbHistoryStart();'
if s.count(anchor)!=1:
    raise SystemExit('v50: startup anchor missing')

code=r'''

// KB911_V50_SESSION_ONLY_DIMENSION_DEFAULTS
// Dimension creation defaults live only for the current app session.
// Existing dimensions keep their own dataset style; projects/history/recovery
// must not replace the active tool defaults when a document is opened/restored.
Object.assign(builtDim,{
 prefix:'',suffix:'',
 arrow:'slim',arrowSize:'5',arrowAngle:'10',
 tailSize:'2',lineWidth:'0.50',
 lineColor:'#000000',font:'Bahnschrift',fontSize:'3',textColor:'#000000',
 italic:false
});
// Keep the existing bold default unless the user changes it during the session.
// Start every fresh application launch from the fixed standard above.
dimDefaults=Object.assign({},builtDim);
try{localStorage.removeItem('mm.dimDefaults.v2')}catch{}

// Legacy code still calls saveStore after editing a dimension. Keep that useful
// in-memory behavior, but never persist dimension defaults across launches.
const kbSaveStoreBeforeV50=saveStore;
saveStore=function(k,v){
 if(k==='mm.dimDefaults.v2')return;
 return kbSaveStoreBeforeV50(k,v);
};

// A project stores every dimension's actual styling in that object's dataset.
// Tool defaults are session UI state, not project data.
const kbPackProjectBeforeV50=kbPackProject;
kbPackProject=function(){
 const packed=kbPackProjectBeforeV50();
 if(packed&&typeof packed==='object')delete packed.dimDefaults;
 return packed;
};
const kbUnpackProjectBeforeV50=kbUnpackProject;
kbUnpackProject=function(data){
 const sessionDefaults=Object.assign({},dimDefaults);
 const project=kbUnpackProjectBeforeV50(data);
 dimDefaults=sessionDefaults;
 return project;
};

// Undo/Redo and crash recovery restore the document only. They must not import
// a previous session's creation defaults from a serialized history snapshot.
const kbHistoryRestoreBeforeV50=kbHistoryRestore;
kbHistoryRestore=function(state){
 const sessionDefaults=Object.assign({},dimDefaults);
 const result=kbHistoryRestoreBeforeV50(state);
 dimDefaults=sessionDefaults;
 return result;
};
'''

s=s.replace(anchor,code+anchor,1)
for token in [marker,"arrow:'slim'","tailSize:'2'","lineWidth:'0.50'","lineColor:'#000000'","font:'Bahnschrift'","fontSize:'3'","textColor:'#000000'","localStorage.removeItem('mm.dimDefaults.v2')","delete packed.dimDefaults",'kbHistoryRestoreBeforeV50']:
    if token not in s:
        raise SystemExit('v50 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v50: dimension defaults are session-only and reset to fixed standard on every launch')
