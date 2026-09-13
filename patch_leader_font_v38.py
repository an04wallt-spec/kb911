from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')

marker = 'KB911_V38_LEADER_OWN_FONT'
if marker in s:
    print('v38 already applied')
    raise SystemExit(0)

# Add an independent font selector to the leader popup. Keep the existing
# shelf/font-size row untouched; this is an additive UI change only.
row_anchor = '''  <div class="row"><div style="flex:1"><div class="label">Полка, мм</div><input id="leaderShelf" type="number" min="8" max="500" step="1" value="40" style="width:100%"></div><div style="flex:1"><div class="label">Шрифт, мм</div><input id="leaderFontSize" type="number" min="1.5" max="30" step="0.5" value="4" style="width:100%"></div></div>'''
font_row = row_anchor + '''\n  <div class="label">Шрифт</div><select id="leaderFont" style="width:100%"><option>Arial</option><option selected>Bahnschrift</option><option>Gost</option><option>Segoe UI</option><option>Tahoma</option><option>Verdana</option><option>Times New Roman</option></select>'''
if s.count(row_anchor) != 1:
    raise SystemExit(f'v38: expected one leader popup row, got {s.count(row_anchor)}')
s = s.replace(row_anchor, font_row, 1)

# Every leader popup opener must reflect the font stored on that leader.
open_anchor = "$('leaderFontSize').value=g.dataset.fontSize||4;$('leaderBold').checked=g.dataset.bold==='1';"
open_repl = "$('leaderFontSize').value=g.dataset.fontSize||4;$('leaderFont').value=g.dataset.font||'Bahnschrift';$('leaderBold').checked=g.dataset.bold==='1';"
open_count = s.count(open_anchor)
if open_count < 1:
    raise SystemExit('v38: leader popup font-size sync anchor missing')
s = s.replace(open_anchor, open_repl)

# The leader font is completely independent from dimension settings. Changing
# this selector updates only the selected leader and persists as data-font in
# the document/project just like the other leader properties.
listener_anchor = "$('leaderFontSize').oninput=()=>{if(selected?.dataset.type==='leader'){selected.dataset.fontSize=$('leaderFontSize').value;renderLeader(selected);drawSelection()}};"
listener = listener_anchor + "$('leaderFont').onchange=()=>{if(selected?.dataset.type!=='leader')return;selected.dataset.font=$('leaderFont').value||'Bahnschrift';renderLeader(selected);drawSelection();try{kbHistorySchedule(0)}catch{}};"
if s.count(listener_anchor) != 1:
    raise SystemExit(f'v38: expected one leader font-size listener, got {s.count(listener_anchor)}')
s = s.replace(listener_anchor, listener, 1)

# New leaders must start from their own Bahnschrift default, not from the
# dimension font. The current live creator already stores data-font explicitly;
# guard that contract so future changes cannot silently reintroduce inheritance.
if "'data-font':'Bahnschrift'" not in s:
    raise SystemExit('v38: leader creator does not have an independent Bahnschrift font default')

# Final render path must read the font from the leader itself.
if "'font-family':g.dataset.font||'Bahnschrift'" not in s:
    raise SystemExit('v38: leader renderer is not using leader data-font')

# Put the marker on the new control, without affecting any other font selector.
s = s.replace('id="leaderFont" style="width:100%"', 'id="leaderFont" data-v38="KB911_V38_LEADER_OWN_FONT" style="width:100%"', 1)

for token in [
    marker,
    'id="leaderFont"',
    '<option selected>Bahnschrift</option><option>Gost</option>',
    "selected.dataset.font=$('leaderFont').value||'Bahnschrift'",
    "$('leaderFont').value=g.dataset.font||'Bahnschrift'",
    "'font-family':g.dataset.font||'Bahnschrift'"
]:
    if token not in s:
        raise SystemExit('v38 guard failed: ' + token)

p.write_text(s, encoding='utf-8', newline='')
print('v38: leader gets its own font selector; Bahnschrift default and embedded Gost stay available')

# v39 adds per-image calibration, measurement grid and automatic dimensions.
exec(Path('patch_measurement_grid_v39.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
