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
python patch_line_free_v23.py
if errorlevel 1 exit /b 1
python patch_line_copy_v24.py
if errorlevel 1 exit /b 1
python patch_line_handles_v25.py
if errorlevel 1 exit /b 1
python patch_brand_email_v26.py
if errorlevel 1 exit /b 1
python patch_native.py
if errorlevel 1 exit /b 1
python patch_native_open_v7.py
if errorlevel 1 exit /b 1
if not exist build mkdir build
python -c "from pathlib import Path; import re; s=Path(r'app\KB911.html').read_text(encoding='utf-8'); assert 'KB911_V10_CORE_INTERACTIONS' in s; assert 'KB911_V12_EDITING_CORE' in s; assert 'KB911_V17_LEADER_CORE_IN_SCOPE' in s; assert 'KB911_V18_LEADER_TEXT_LOCK_AND_MENU_CLOSE' in s; assert 'KB911_V19_LAYER_MENU_SINGLE_OWNER' in s; assert 'KB911_V20_PRINT_RESTORE' not in s; assert 'KB911_V21_IMAGE_MENU_COMPAT' in s; assert 'KB911_V22_LINE_TOOL_AND_REDO' in s; assert 'KB911_V23_FREE_THREE_POINT_LINE' in s; assert 'KB911_V24_LINE_COPY_PASTE' in s; assert 'KB911_V25_LINE_MIDPOINT_DELETE_AND_HANDLE_SIZE' in s; assert 'KB911_V26_BRAND_EMAIL_COPY' in s; assert 'KB911_V11_EDITING_REPAIR' not in s; assert 'KB911_V13_LEADER_EXPORT_REPAIR' not in s; assert 'KB911_V15_LEADER_CORE_FIX' not in s; assert 'KB911_V16_LEADER_NATIVE_CORE' not in s; assert \"if(tool==='dimension')\" in s; assert \"if(activeImage!==obj){drag=null;return}\" in s; assert \"['dimText','value']\" in s; assert \"['fontSize','fontSize']\" in s; assert \"['textSize','fontSize']\" in s; assert 'editText(obj)' in s; assert 'kbLeaderTextPointV17' in s; assert \"data-leader-handle':'text\" not in s; assert 'kbLeaderPopupDragV17' in s; assert 'kbInstallLayerMenuV19' in s; assert \"setProperty('display','none','important')\" in s; assert 'id=\\\"printSheet\\\"' not in s; assert 'function kbPrintCurrentSheetV20()' not in s; assert 'window.print()' not in s; assert 'function closeImageMenu()' in s; assert 'function openImageMenu(img,e)' in s; assert 'data-tool=\\\"line\\\"' in s; assert 'id=\\\"linePopup\\\"' in s; assert 'function renderSimpleLine(' in s; assert 'function drawSimpleLineHandles(' in s; assert \"data-p3':`${p3.x},${p3.y}`\" in s; assert 'simpleLineDraft={stage:1,p1:p,p2:null}' in s; assert 'kbLineClipboardV24' in s; assert 'kbStartLinePasteV24' in s; assert 'kbPlaceLinePasteV24' in s; assert \"r:.72,class:'handle selection-ui leader-handle'\" in s; assert \"r:.72,class:'handle selection-ui simple-line-handle'\" in s; assert \"selected.dataset.straight='1'\" in s; assert \"simpleLineSelectedHandle==='p2'\" in s; assert 'id=\\\"redoImage\\\"' in s; assert 'id=\\\"kbBrand\\\"' in s; assert 'id=\\\"copySupportEmail\\\"' in s; assert 'schkaf@yandex.ru' in s; m=re.search(r'<script>([\s\S]*?)</script>',s); assert m, 'script not found'; Path(r'build\kb911_check.js').write_text(m.group(1),encoding='utf-8')"
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
magick build\KB911_icon.png -define icon:auto-resize=256,128,64,48,40,32,24,20,16 build\KB911.ico
if errorlevel 1 exit /b 1
magick build\KB911_icon.png -colorspace Gray -define icon:auto-resize=256,128,64,48,40,32,24,20,16 build\KB911_project.ico
if errorlevel 1 exit /b 1
rc /nologo /fo build\resource.res src\resource.rc
if errorlevel 1 exit /b 1
cl /nologo /std:c++17 /EHsc /O2 /DUNICODE /D_UNICODE /I "%WV2%\include" src\main.cpp build\resource.res ^
 /link /SUBSYSTEM:WINDOWS /OUT:build\KB911.exe /LIBPATH:"%WV2%\x64" WebView2LoaderStatic.lib ^
 user32.lib shell32.lib shlwapi.lib ole32.lib version.lib advapi32.lib
if errorlevel 1 exit /b 1
echo.
echo Built: build\KB911.exe
