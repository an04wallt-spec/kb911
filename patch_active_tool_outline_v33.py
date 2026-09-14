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

exec(Path('patch_frame_settings_v34.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
exec(Path('patch_embedded_gost_v35.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
exec(Path('patch_leader_defaults_v44.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
exec(Path('patch_native_text_paste_v44.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
exec(Path('patch_print_path_v45.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
exec(Path('patch_pdf_line_quality_v46.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
exec(Path('patch_pdf_stroke_calibration_v46b.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
exec(Path('patch_dimension_dblclick_v47.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
exec(Path('patch_dimension_axis_resize_v48.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
exec(Path('patch_dimension_handle_dblclick_v49.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
exec(Path('patch_dimension_session_defaults_v50.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
