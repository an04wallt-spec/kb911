from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')

marker = 'KB911_V33_ACTIVE_TOOL_OUTLINE'
if marker in s:
    print('active tool outline v33 already installed')
    raise SystemExit(0)

anchor = '</head>'
if s.count(anchor) != 1:
    raise SystemExit(f'active tool outline v33: expected one </head>, got {s.count(anchor)}')

style = r'''<style id="kb911ActiveToolOutlineV33">
/* KB911_V33_ACTIVE_TOOL_OUTLINE
   Only the four persistent creation tools get the red active-state frame. */
button[data-tool="dimension"].active,
button[data-tool="leader"].active,
button[data-tool="text"].active,
button[data-tool="line"].active {
  outline: 2px solid #e53935 !important;
  outline-offset: -2px;
}
</style>
'''

s = s.replace(anchor, style + anchor, 1)

for token in [
    'KB911_V33_ACTIVE_TOOL_OUTLINE',
    'button[data-tool="dimension"].active',
    'button[data-tool="leader"].active',
    'button[data-tool="text"].active',
    'button[data-tool="line"].active',
    'outline: 2px solid #e53935 !important;'
]:
    if token not in s:
        raise SystemExit('active tool outline v33 guard failed: ' + token)

p.write_text(s, encoding='utf-8', newline='')
print('v33: red outline added only to the four persistent creation tools')

# v34 is deliberately chained after v33 so the stable build order remains intact.
exec(Path('patch_frame_settings_v34.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
# v35 is a visual/font-only layer on top of the user-tested v34 behavior.
exec(Path('patch_embedded_gost_v35.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
# v44 keeps leader defaults independent from dimensions and restores OS text paste.
exec(Path('patch_leader_defaults_v44.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
exec(Path('patch_native_text_paste_v44.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
# v45 makes printing use named ISO paper sizes and shares the remembered picker folder.
exec(Path('patch_print_path_v45.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
# v46 keeps technical linework lossless inside PDF instead of JPEG-compressed tiles.
exec(Path('patch_pdf_line_quality_v46.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
