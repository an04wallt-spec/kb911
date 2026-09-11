@echo off
setlocal
set WV2_VER=1.0.4191.47
if not exist app\KB911.html (
  echo Reconstructing app\KB911.html from parts...
)
(for %%F in (app\parts\part*.txt) do @type "%%F") > app\KB911.html
if errorlevel 1 exit /b 1
python patch_ui.py app\KB911.html
if errorlevel 1 exit /b 1
python patch_v4.py app\KB911.html
if errorlevel 1 exit /b 1
python patch_dimension_fix.py
if errorlevel 1 exit /b 1
python patch_frame_params.py
if errorlevel 1 exit /b 1
python patch_syntax_fix.py
if errorlevel 1 exit /b 1
python patch_leader_fix.py
if errorlevel 1 exit /b 1
python patch_project_v1.py
if errorlevel 1 exit /b 1
python patch_project_persistence_v2.py
if errorlevel 1 exit /b 1
python patch_native.py
if errorlevel 1 exit /b 1
if not exist build mkdir build
python -c "from pathlib import Path; import re; s=Path(r'app\KB911.html').read_text(encoding='utf-8'); m=re.search(r'<script>([\s\S]*?)</script>',s); assert m, 'script not found'; Path(r'build\kb911_check.js').write_text(m.group(1),encoding='utf-8')"
if errorlevel 1 exit /b 1
node --check build\kb911_check.js
if errorlevel 1 exit /b 1
if not exist packages\Microsoft.Web.WebView2.%WV2_VER% (
  nuget install Microsoft.Web.WebView2 -Version %WV2_VER% -OutputDirectory packages
  if errorlevel 1 exit /b 1
)
set WV2=packages\Microsoft.Web.WebView2.%WV2_VER%\build\native
powershell -NoProfile -ExecutionPolicy Bypass -File make_icon.ps1
if errorlevel 1 exit /b 1
python -c "import struct,pathlib; p=pathlib.Path(r'build\KB911_icon.png').read_bytes(); pathlib.Path(r'build\KB911.ico').write_bytes(struct.pack('<HHH',0,1,1)+struct.pack('<BBBBHHII',0,0,0,0,1,32,len(p),22)+p)"
if errorlevel 1 exit /b 1
rc /nologo /fo build\resource.res src\resource.rc
if errorlevel 1 exit /b 1
cl /nologo /std:c++17 /EHsc /O2 /DUNICODE /D_UNICODE /I "%WV2%\include" src\main.cpp build\resource.res ^
 /link /SUBSYSTEM:WINDOWS /OUT:build\KB911.exe /LIBPATH:"%WV2%\x64" WebView2LoaderStatic.lib ^
 user32.lib shell32.lib shlwapi.lib ole32.lib version.lib advapi32.lib
if errorlevel 1 exit /b 1
echo.
echo Built: build\KB911.exe
