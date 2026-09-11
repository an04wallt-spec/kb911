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
python fix_feature_wrapper.py
if errorlevel 1 exit /b 1
python patch_feature_v7.py
if errorlevel 1 exit /b 1
python fix_feature_js_v7.py
if errorlevel 1 exit /b 1
python patch_startup_pdf_v8.py
if errorlevel 1 exit /b 1
python patch_runtime_repair_v9.py
if errorlevel 1 exit /b 1
python patch_core_interactions_v10.py
if errorlevel 1 exit /b 1
python patch_editing_core_v12.py
if errorlevel 1 exit /b 1
python patch_leader_core_v17.py
if errorlevel 1 exit /b 1
python patch_leader_menu_v18.py
if errorlevel 1 exit /b 1
python patch_layer_menu_v19.py
if errorlevel 1 exit /b 1
python patch_print_v20.py
if errorlevel 1 exit /b 1
python patch_image_menu_compat_v21.py
if errorlevel 1 exit /b 1
python patch_line_toolbar_v22.py
if errorlevel 1 exit /b 1
python patch_native.py
if errorlevel 1 exit /b 1
python patch_native_open_v7.py
if errorlevel 1 exit /b 1
if not exist build mkdir build
python -c "from pathlib import Path; import re; s=Path(r'app\KB911.html').read_text(encoding='utf-8'); assert 'KB911_V10_CORE_INTERACTIONS' in s; assert 'KB911_V12_EDITING_CORE' in s; assert 'KB911_V17_LEADER_CORE_IN_SCOPE' in s; assert 'KB911_V18_LEADER_TEXT_LOCK_AND_MENU_CLOSE' in s; assert 'KB911_V19_LAYER_MENU_SINGLE_OWNER' in s; assert 'KB911_V20_PRINT_RESTORE' in s; assert 'KB911_V21_IMAGE_MENU_COMPAT' in s; assert 'KB911_V22_LINE_TOOL_AND_REDO' in s; assert 'KB911_V11_EDITING_REPAIR' not in s; assert 'KB911_V13_LEADER_EXPORT_REPAIR' not in s; assert 'KB911_V15_LEADER_CORE_FIX' not in s; assert 'KB911_V16_LEADER_NATIVE_CORE' not in s; assert \"if(tool==='dimension')\" in s; assert \"if(activeImage!==obj){drag=null;return}\" in s; assert \"['dimText','value']\" in s; assert \"['fontSize','fontSize']\" in s; assert \"['textSize','fontSize']\" in s; assert 'editText(obj)' in s; assert 'kbLeaderTextPointV17' in s; assert \"data-leader-handle':'text\" not in s; assert 'kbLeaderPopupDragV17' in s; assert 'kbInstallLayerMenuV19' in s; assert \"setProperty('display','none','important')\" in s; assert 'id=\\\"printSheet\\\"' in s; assert 'function kbPrintCurrentSheetV20()' in s; assert 'window.print()' in s; assert 'updatePrintSize()' in s; assert 'function closeImageMenu()' in s; assert 'function openImageMenu(img,e)' in s; assert 'data-tool=\\\"line\\\"' in s; assert 'id=\\\"linePopup\\\"' in s; assert 'function renderSimpleLine(' in s; assert 'function drawSimpleLineHandles(' in s; assert 'id=\\\"redoImage\\\"' in s; m=re.search(r'<script>([\s\S]*?)</script>',s); assert m, 'script not found'; Path(r'build\kb911_check.js').write_text(m.group(1),encoding='utf-8')"
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
python -c "import struct,pathlib; p=pathlib.Path(r'build\KB911_icon.png').read_bytes(); pathlib.Path(r'build\KB911.ico').write_bytes(struct.pack('<HHH',0,1,1)+struct.pack('<BBBBHHII',0,0,0,0,1,32,len(p),22)+p); q=pathlib.Path(r'build\KB911_project_icon.png').read_bytes(); pathlib.Path(r'build\KB911_project.ico').write_bytes(struct.pack('<HHH',0,1,1)+struct.pack('<BBBBHHII',0,0,0,0,1,32,len(q),22)+q)"
if errorlevel 1 exit /b 1
rc /nologo /fo build\resource.res src\resource.rc
if errorlevel 1 exit /b 1
cl /nologo /std:c++17 /EHsc /O2 /DUNICODE /D_UNICODE /I "%WV2%\include" src\main.cpp build\resource.res ^
 /link /SUBSYSTEM:WINDOWS /OUT:build\KB911.exe /LIBPATH:"%WV2%\x64" WebView2LoaderStatic.lib ^
 user32.lib shell32.lib shlwapi.lib ole32.lib version.lib advapi32.lib
if errorlevel 1 exit /b 1
echo.
echo Built: build\KB911.exe
