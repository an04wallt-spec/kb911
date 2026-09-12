from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')

def replace_once(old, new):
    global s
    if s.count(old) != 1:
        raise SystemExit(f'dimension label side: expected one occurrence, got {s.count(old)}: {old[:90]}')
    s = s.replace(old, new, 1)

# The choice belongs to each dimension. Missing data in existing projects retains
# the established placement above the line.
replace_once(
    "const off=fs*.9+1.1,tm={x:mid.x+nx*off,y:mid.y+ny*off};",
    "const off=(fs*.9+1.1)*(g.dataset.labelSide==='below'?-1:1),tm={x:mid.x+nx*off,y:mid.y+ny*off};"
)

replace_once(
    '<div class="dp-grid">',
    '<div class="dp-grid"><div class="dp-full"><div class="dp-label">Положение размера</div><select id="dimLabelSide" class="dp-field"><option value="above">Над линией</option><option value="below">Под линией</option></select></div>'
)

replace_once(
    "$('fontItalic').checked=g.dataset.italic==='1'}\nfunction captureDimDefaults",
    "$('fontItalic').checked=g.dataset.italic==='1';$('dimLabelSide').value=g.dataset.labelSide==='below'?'below':'above'}\nfunction captureDimDefaults"
)

replace_once(
    "$('imageOpacity').oninput=",
    "$('dimLabelSide').onchange=()=>{if(selected?.dataset.type!=='dimension')return;selected.dataset.labelSide=$('dimLabelSide').value==='below'?'below':'above';renderDim(selected);drawSelection()};\n$('imageOpacity').oninput="
)

p.write_text(s, encoding='utf-8', newline='')
print('Dimension text side can be changed per dimension')
