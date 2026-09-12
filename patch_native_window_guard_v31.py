from pathlib import Path

p=Path('src/main.cpp')
s=p.read_text(encoding='utf-8')

old='''        if (w > 0 && h > 0) FitWindowToPaper(w, h);'''
new='''        if (w > 0 && h > 0) {
            // KB911_V31_NATIVE_WINDOW_GUARD
            // setPage() is also called by Undo/Redo restoration.  Re-fitting an
            // unchanged sheet used to resize/re-center the native Windows window,
            // making window placement look like part of document history.
            // Only a real paper-size/orientation change may resize the host window.
            const bool samePaper = std::abs(w - g_paperWmm) < 0.01 && std::abs(h - g_paperHmm) < 0.01;
            if (!samePaper) FitWindowToPaper(w, h);
        }'''
if s.count(old)!=1:
    raise SystemExit(f'native window guard: expected one size handler, got {s.count(old)}')
s=s.replace(old,new,1)

for token in ['KB911_V31_NATIVE_WINDOW_GUARD','const bool samePaper','if (!samePaper) FitWindowToPaper(w, h);']:
    if token not in s:
        raise SystemExit('native window guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('Native window placement removed from redundant setPage/Undo restores')
