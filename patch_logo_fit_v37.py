from pathlib import Path

p = Path('app/KB911.html')
s = p.read_text(encoding='utf-8')

marker = 'KB911_V37_LOGO_PRESERVE_ASPECT'
if marker in s:
    print('v37 already applied')
    raise SystemExit(0)

old = "preserveAspectRatio:'none','clip-path':`url(#${clipId})`,'data-frame-logo':'1'"
new = "preserveAspectRatio:'xMidYMid meet','clip-path':`url(#${clipId})`,'data-frame-logo':'1','data-logo-fit-v37':'1'"
count = s.count(old)
if count != 1:
    raise SystemExit(f'v37: expected one frame-logo stretch anchor, got {count}')
s = s.replace(old, new, 1)

# Marker is intentionally attached near the frame-logo render path only.
s = s.replace("'data-logo-fit-v37':'1'", "'data-logo-fit-v37':'1'/* KB911_V37_LOGO_PRESERVE_ASPECT */", 1)

for token in [
    marker,
    "preserveAspectRatio:'xMidYMid meet'",
    "'data-frame-logo':'1'"
]:
    if token not in s:
        raise SystemExit('v37 guard failed: ' + token)

# Guard against accidentally changing normal imported images, which must retain their existing behavior.
if s.count("preserveAspectRatio:'none'") < 1:
    raise SystemExit('v37: imported-image preserveAspectRatio behavior was unexpectedly changed')

p.write_text(s, encoding='utf-8', newline='')
print('v37: frame logo now fits proportionally inside its adjustable box without stretching')

# v38 gives leaders/callouts their own font selector without changing other leader mechanics.
exec(Path('patch_leader_font_v38.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
# v40 changes only newly-created dimensions: fixed reference points, movable dimension line and magnetic endpoint snapping.
exec(Path('patch_dimension_anchor_v40.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
exec(Path('patch_dimension_anchor_v40_fix.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
# v41 removes the legacy tail gesture from the center control and adds recovery deletion UI.
exec(Path('patch_dimension_recovery_v41.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
# v41 quick entry keeps full properties closed after creation and uses a compact ellipsis input instead.
exec(Path('patch_dimension_quick_entry_v41.py').read_text(encoding='utf-8'), {'__name__':'__main__'})
