@echo off
setlocal
set WV2_VER=1.0.4191.47
if not exist app\KB911.html (
  echo Reconstructing app\KB911.html from parts...
)
(for %%F in (app\parts\part*.txt) do @type "%%F") > app\KB911.html
if errorlevel 1 exit /b 1
if not exist packages\Microsoft.Web.WebView2.%WV2_VER% (
  nuget install Microsoft.Web.WebView2 -Version %WV2_VER% -OutputDirectory packages
  if errorlevel 1 exit /b 1
)
set WV2=packages\Microsoft.Web.WebView2.%WV2_VER%\build\native
if not exist build mkdir build
rc /nologo /fo build\resource.res src\resource.rc
if errorlevel 1 exit /b 1
cl /nologo /std:c++17 /EHsc /O2 /DUNICODE /D_UNICODE /I "%WV2%\include" src\main.cpp build\resource.res ^
 /link /SUBSYSTEM:WINDOWS /OUT:build\KB911.exe /LIBPATH:"%WV2%\x64" WebView2LoaderStatic.lib ^
 user32.lib shell32.lib shlwapi.lib ole32.lib version.lib
if errorlevel 1 exit /b 1
echo.
echo Built: build\KB911.exe
