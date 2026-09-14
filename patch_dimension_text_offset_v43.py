from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')
marker = 'KB911_V43_CENTER_DBLCLICK_AND_SPACE_OFFSET'
if marker in s:
    print('v43 dimension text offset already applied')
    raise SystemExit(0)

style = r'''<style id="kb911DimensionV43Style">
/* KB911_V43_CENTER_DBLCLICK_AND_SPACE_OFFSET */
.kb-dim-line-handle-v40{cursor:move!important}
</style>
'''
if s.count('</head>') != 1:
    raise SystemExit('v43: expected one </head>')
s = s.replace('</head>', style + '</head>', 1)

anchor = '\nsetPage();\ninitKB911Project();\nkbHistoryStart();'
if s.count(anchor) != 1:
    raise SystemExit('v43: startup anchor missing')

code = r'''

// KB911_V43_CENTER_DBLCLICK_AND_SPACE_OFFSET
// Boundary spaces in prefix/suffix are deliberate positioning commands for
// anchored dimensions. Prefix spaces move the visible dimension text to the
// readable-text right; suffix spaces move it left. One space = one character
// step derived from the current dimension font size, so the effect scales with
// drawing text rather than browser zoom.
function kbDimSpaceOffsetV43(g){
 const prefix=String(g?.dataset?.prefix||''),suffix=String(g?.dataset?.suffix||'');
 const pre=(prefix.match(/ /g)||[]).length,suf=(suffix.match(/ /g)||[]).length;
 const fs=+g?.dataset?.fontSize||4,step=fs*.72;
 return{pre,suf,steps:pre-suf,step,prefix:prefix.replace(/ /g,''),suffix:suffix.replace(/ /g,'')};
}
function kbDimReadableAxisV43(m){
 const a=Math.atan2(m.uy,m.ux)*180/Math.PI;
 const flip=a>90||a<-90;
 return{x:flip?-m.ux:m.ux,y:flip?-m.uy:m.uy};
}
function kbApplyDimSpaceOffsetV43(g){
 if(!kbIsAnchoredDimV40(g))return;
 const info=kbDimSpaceOffsetV43(g),t=g.querySelector('.dim-label'),grab=g.querySelector('.dim-label-grab');
 if(!t)return;
 // Spaces are commands, not printable characters.
 t.textContent=info.prefix+(g.dataset.value||'…')+info.suffix;
 if(!info.steps)return;
 const m=kbAnchoredDimGeomV40(g),axis=kbDimReadableAxisV43(m),shift=info.steps*info.step,dx=axis.x*shift,dy=axis.y*shift;
 const x=+t.getAttribute('x')||0,y=+t.getAttribute('y')||0,tx=x+dx,ty=y+dy;
 let ang=Math.atan2(m.q2.y-m.q1.y,m.q2.x-m.q1.x)*180/Math.PI;if(ang>90||ang<-90)ang+=180;
 t.setAttribute('x',tx);t.setAttribute('y',ty);t.setAttribute('transform',`rotate(${ang} ${tx} ${ty})`);
 if(grab){
  grab.setAttribute('x',(+grab.getAttribute('x')||0)+dx);grab.setAttribute('y',(+grab.getAttribute('y')||0)+dy);
  grab.setAttribute('transform',`rotate(${ang} ${tx} ${ty})`);
 }
}
const kbRenderAnchoredDimBeforeV43=kbRenderAnchoredDimV40;
kbRenderAnchoredDimV40=function(g){kbRenderAnchoredDimBeforeV43(g);kbApplyDimSpaceOffsetV43(g)};

// Keep the compact first-entry box aligned with the shifted dimension text when
// the current defaults already contain prefix/suffix positioning spaces.
const kbQuickDimScreenPointBeforeV43=kbQuickDimScreenPointV41;
kbQuickDimScreenPointV41=function(g){
 const q=kbQuickDimScreenPointBeforeV43(g),info=kbDimSpaceOffsetV43(g);
 if(!info.steps)return q;
 const m=kbAnchoredDimGeomV40(g),axis=kbDimReadableAxisV43(m),r=paper.getBoundingClientRect();
 const mmPerPxX=page.w/Math.max(1,r.width),mmPerPxY=page.h/Math.max(1,r.height),shift=info.steps*info.step;
 return{x:q.x+axis.x*shift/mmPerPxX,y:q.y+axis.y*shift/mmPerPxY};
};

// The center handle is both a drag handle and an explicit entry point to the
// complete dimension editor. Capture phase is required because selection-ui
// handles are direct SVG children, not children of the dimension <g>.
paper.addEventListener('dblclick',e=>{
 const h=e.target.closest?.('.kb-dim-line-handle-v40');
 if(!h)return;
 const g=findOwner(h.dataset.owner,'dimension');if(!kbIsAnchoredDimV40(g))return;
 e.preventDefault();e.stopImmediatePropagation();
 kbDimLineDragV40=null;kbDimAnchorDragV40=null;kbClearSnapMarkV40();
 selected=g;lastEditable=g;drawSelection();setTool('dimension-edit',true);syncDimProps();openDimPopup();
 setStatus('Настройки размера');
},true);
'''

s = s.replace(anchor, code + anchor, 1)
for token in [
    marker,
    'kbDimSpaceOffsetV43',
    'prefix.replace(/ /g',
    'suffix.replace(/ /g',
    'kbRenderAnchoredDimBeforeV43',
    "paper.addEventListener('dblclick'",
    "e.target.closest?.('.kb-dim-line-handle-v40')",
    "setTool('dimension-edit',true);syncDimProps();openDimPopup()"
]:
    if token not in s:
        raise SystemExit('v43 guard failed: '+token)

p.write_text(s, encoding='utf-8', newline='')
print('v43: center handle double-click opens dimension settings; prefix/suffix spaces offset dimension text')
