from pathlib import Path

p=Path('src/main.cpp')
s=p.read_text(encoding='utf-8')

def rep(a,b,n=1):
    global s
    if a not in s: raise SystemExit('patch_native_open_v7 missing fragment: '+a[:160])
    s=s.replace(a,b,n)

rep('#include <shlwapi.h>\n', '#include <shlwapi.h>\n#include <shellapi.h>\n')
rep('static double g_paperHmm = 297.0;\n', 'static double g_paperHmm = 297.0;\nstatic std::wstring g_pendingProjectPath;\n')

helpers=r'''
static bool EndsWithI(const std::wstring& s, const std::wstring& suffix) {
    if (s.size() < suffix.size()) return false;
    return _wcsicmp(s.c_str() + (s.size() - suffix.size()), suffix.c_str()) == 0;
}

static std::wstring ReadUtf8TextFile(const std::wstring& path) {
    HANDLE h = CreateFileW(path.c_str(), GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE, nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (h == INVALID_HANDLE_VALUE) return L"";
    LARGE_INTEGER li{};
    if (!GetFileSizeEx(h, &li) || li.QuadPart <= 0 || li.QuadPart > 1024LL * 1024LL * 1024LL) { CloseHandle(h); return L""; }
    std::string bytes(static_cast<size_t>(li.QuadPart), '\0');
    size_t off = 0;
    while (off < bytes.size()) {
        DWORD chunk = static_cast<DWORD>(std::min<size_t>(bytes.size() - off, 16 * 1024 * 1024));
        DWORD got = 0;
        if (!ReadFile(h, bytes.data() + off, chunk, &got, nullptr) || got == 0) { CloseHandle(h); return L""; }
        off += got;
    }
    CloseHandle(h);
    int n = MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, bytes.data(), static_cast<int>(bytes.size()), nullptr, 0);
    if (n <= 0) n = MultiByteToWideChar(CP_UTF8, 0, bytes.data(), static_cast<int>(bytes.size()), nullptr, 0);
    if (n <= 0) return L"";
    std::wstring out(static_cast<size_t>(n), L'\0');
    MultiByteToWideChar(CP_UTF8, 0, bytes.data(), static_cast<int>(bytes.size()), out.data(), n);
    return out;
}

static void SetRegString(HKEY root, const std::wstring& keyPath, const wchar_t* valueName, const std::wstring& value) {
    HKEY key = nullptr;
    if (RegCreateKeyExW(root, keyPath.c_str(), 0, nullptr, 0, KEY_SET_VALUE, nullptr, &key, nullptr) != ERROR_SUCCESS) return;
    RegSetValueExW(key, valueName, 0, REG_SZ, reinterpret_cast<const BYTE*>(value.c_str()), static_cast<DWORD>((value.size() + 1) * sizeof(wchar_t)));
    RegCloseKey(key);
}

static std::wstring ExtractProjectIconFile() {
    // KB911_V31_PROJECT_ICON_FILE
    HINSTANCE hInst = GetModuleHandleW(nullptr);
    HRSRC hrsrc = FindResourceW(hInst, MAKEINTRESOURCEW(IDR_PROJECT_ICON_FILE), RT_RCDATA);
    if (!hrsrc) return L"";
    HGLOBAL hglob = LoadResource(hInst, hrsrc);
    if (!hglob) return L"";
    DWORD size = SizeofResource(hInst, hrsrc);
    const void* data = LockResource(hglob);
    if (!data || !size) return L"";

    PWSTR local = nullptr;
    if (FAILED(SHGetKnownFolderPath(FOLDERID_LocalAppData, 0, nullptr, &local)) || !local) return L"";
    std::wstring root = std::wstring(local) + L"\\KB911";
    CoTaskMemFree(local);
    SHCreateDirectoryExW(nullptr, root.c_str(), nullptr);

    // Versioned file name is deliberate: Explorer can hold the old ICO open
    // and cache it by path. A new path guarantees that the corrected icon is read.
    std::wstring iconPath = root + L"\\KB911_project_v31.ico";

    HANDLE h = CreateFileW(iconPath.c_str(), GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, nullptr, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (h == INVALID_HANDLE_VALUE) return L"";
    DWORD written = 0;
    BOOL ok = WriteFile(h, data, size, &written, nullptr);
    CloseHandle(h);
    return (ok && written == size) ? iconPath : L"";
}

static void RegisterProjectAssociation() {
    // KB911_V31_PROJECT_ICON_ASSOC_FILE
    wchar_t exeBuf[32768]{};
    DWORD n = GetModuleFileNameW(nullptr, exeBuf, static_cast<DWORD>(_countof(exeBuf)));
    if (!n || n >= _countof(exeBuf)) return;
    std::wstring exe(exeBuf, n);
    const std::wstring progId = L"KB911.Project";
    std::wstring projectIcon = ExtractProjectIconFile();
    const std::wstring iconSpec = projectIcon.empty()
        ? (L"\"" + exe + L"\",-103")
        : (L"\"" + projectIcon + L"\",0");
    const std::wstring openCommand = L"\"" + exe + L"\" \"%1\"";

    SetRegString(HKEY_CURRENT_USER, L"Software\\Classes\\.kb911", nullptr, progId);
    SetRegString(HKEY_CURRENT_USER, L"Software\\Classes\\.kb911\\DefaultIcon", nullptr, iconSpec);
    SetRegString(HKEY_CURRENT_USER, L"Software\\Classes\\.kb911\\OpenWithProgids", L"KB911.Project", L"");
    SetRegString(HKEY_CURRENT_USER, L"Software\\Classes\\KB911.Project", nullptr, L"Проект KB911");
    SetRegString(HKEY_CURRENT_USER, L"Software\\Classes\\KB911.Project\\DefaultIcon", nullptr, iconSpec);
    SetRegString(HKEY_CURRENT_USER, L"Software\\Classes\\KB911.Project\\shell\\open\\command", nullptr, openCommand);
    SetRegString(HKEY_CURRENT_USER, L"Software\\Classes\\SystemFileAssociations\\.kb911\\DefaultIcon", nullptr, iconSpec);

    const wchar_t* exeNamePtr = PathFindFileNameW(exe.c_str());
    std::wstring exeName = (exeNamePtr && *exeNamePtr) ? exeNamePtr : L"KB911.exe";
    const std::wstring appKey = L"Software\\Classes\\Applications\\" + exeName;
    SetRegString(HKEY_CURRENT_USER, appKey + L"\\DefaultIcon", nullptr, iconSpec);
    SetRegString(HKEY_CURRENT_USER, appKey + L"\\shell\\open\\command", nullptr, openCommand);
    SetRegString(HKEY_CURRENT_USER, appKey + L"\\SupportedTypes", L".kb911", L"");

    SetRegString(HKEY_CURRENT_USER,
        L"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\.kb911\\OpenWithProgids",
        L"KB911.Project", L"");

    if (!projectIcon.empty()) {
        SHChangeNotify(SHCNE_UPDATEITEM, SHCNF_PATHW | SHCNF_FLUSH, projectIcon.c_str(), nullptr);
    }
    SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST | SHCNF_FLUSH, nullptr, nullptr);
}

static void SendPendingProjectToWeb() {
    if (!g_webview || g_pendingProjectPath.empty()) return;
    std::wstring text = ReadUtf8TextFile(g_pendingProjectPath);
    if (text.empty()) return;
    const wchar_t* base = PathFindFileNameW(g_pendingProjectPath.c_str());
    std::wstring name = base ? base : L"project.kb911";
    std::wstring msg = L"KB911_PROJECT_FILE|" + name + L"|" + text;
    g_webview->PostWebMessageAsString(msg.c_str());
    g_pendingProjectPath.clear();
}

'''
rep('static std::wstring GetLocalAppDataDir() {', helpers+'static std::wstring GetLocalAppDataDir() {')

rep('''                            g_controller = controller;\n                            controller->get_CoreWebView2(&g_webview);\n                            ResizeWebView();''',
    '''                            g_controller = controller;\n                            controller->put_ZoomFactor(1.0);\n                            controller->get_CoreWebView2(&g_webview);\n                            ResizeWebView();''')

needle='''                            std::wstring url = FileUrl(htmlPath);\n                            g_webview->Navigate(url.c_str());\n                            FitWindowToPaper(420.0, 297.0);'''
replacement='''                            EventRegistrationToken navToken{};\n                            g_webview->add_NavigationCompleted(\n                                Callback<ICoreWebView2NavigationCompletedEventHandler>(\n                                    [](ICoreWebView2*, ICoreWebView2NavigationCompletedEventArgs*) -> HRESULT {\n                                        if (g_controller) g_controller->put_ZoomFactor(1.0);\n                                        SendPendingProjectToWeb();\n                                        if (g_webview) g_webview->ExecuteScript(L"setTimeout(()=>{const p=document.getElementById('paperSize'),o=document.getElementById('orientation');if(p&&o){p.value='A3';o.value='landscape';p.dispatchEvent(new Event('change',{bubbles:true}));}setTimeout(()=>window.KB911_fitToViewport&&window.KB911_fitToViewport(),180);},120);", nullptr);\n                                        return S_OK;\n                                    }).Get(), &navToken);\n\n                            std::wstring url = FileUrl(htmlPath);\n                            g_webview->Navigate(url.c_str());\n                            FitWindowToPaper(420.0, 297.0);'''
rep(needle,replacement)

needle='''    SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);\n    CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);\n'''
replacement='''    SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);\n    CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);\n    RegisterProjectAssociation();\n    int argc = 0;\n    LPWSTR* argv = CommandLineToArgvW(GetCommandLineW(), &argc);\n    if (argv) {\n        if (argc > 1 && argv[1] && EndsWithI(argv[1], L".kb911")) g_pendingProjectPath = argv[1];\n        LocalFree(argv);\n    }\n'''
rep(needle,replacement)

for token in ['KB911_V31_PROJECT_ICON_FILE','KB911_V31_PROJECT_ICON_ASSOC_FILE','IDR_PROJECT_ICON_FILE','KB911_project_v31.ico','SystemFileAssociations\\\\.kb911\\\\DefaultIcon','SHCNE_UPDATEITEM']:
    if token not in s: raise SystemExit('patch_native_open_v7 v31 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('Native .kb911 Explorer-open support applied; project icon uses a versioned physical ICO path')
