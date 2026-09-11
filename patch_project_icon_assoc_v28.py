from pathlib import Path

p=Path('src/main.cpp')
s=p.read_text(encoding='utf-8')
marker='// KB911_V28_PROJECT_ICON_ASSOC_REFRESH'
if marker in s:
    print('v28 already applied')
    raise SystemExit(0)

old=r'''static void RegisterProjectAssociation() {
    wchar_t exeBuf[32768]{};
    DWORD n = GetModuleFileNameW(nullptr, exeBuf, static_cast<DWORD>(_countof(exeBuf)));
    if (!n || n >= _countof(exeBuf)) return;
    std::wstring exe(exeBuf, n);
    const std::wstring progId = L"KB911.Project";
    SetRegString(HKEY_CURRENT_USER, L"Software\\Classes\\.kb911", nullptr, progId);
    SetRegString(HKEY_CURRENT_USER, L"Software\\Classes\\KB911.Project", nullptr, L"Проект KB911");
    SetRegString(HKEY_CURRENT_USER, L"Software\\Classes\\KB911.Project\\DefaultIcon", nullptr, L"\"" + exe + L"\",-103");
    SetRegString(HKEY_CURRENT_USER, L"Software\\Classes\\KB911.Project\\shell\\open\\command", nullptr, L"\"" + exe + L"\" \"%1\"");
    SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, nullptr, nullptr);
}
'''

new=r'''static void RegisterProjectAssociation() {
    // KB911_V28_PROJECT_ICON_ASSOC_REFRESH
    // Refresh every association location Explorer may use, including a legacy
    // UserChoice that resolves to Applications\\KB911.exe rather than KB911.Project.
    wchar_t exeBuf[32768]{};
    DWORD n = GetModuleFileNameW(nullptr, exeBuf, static_cast<DWORD>(_countof(exeBuf)));
    if (!n || n >= _countof(exeBuf)) return;
    std::wstring exe(exeBuf, n);
    const std::wstring progId = L"KB911.Project";
    const std::wstring iconSpec = L"\"" + exe + L"\",-103";
    const std::wstring openCommand = L"\"" + exe + L"\" \"%1\"";

    // Normal extension -> ProgID association.
    SetRegString(HKEY_CURRENT_USER, L"Software\\Classes\\.kb911", nullptr, progId);
    SetRegString(HKEY_CURRENT_USER, L"Software\\Classes\\.kb911\\OpenWithProgids", L"KB911.Project", L"");
    SetRegString(HKEY_CURRENT_USER, L"Software\\Classes\\KB911.Project", nullptr, L"Проект KB911");
    SetRegString(HKEY_CURRENT_USER, L"Software\\Classes\\KB911.Project\\DefaultIcon", nullptr, iconSpec);
    SetRegString(HKEY_CURRENT_USER, L"Software\\Classes\\KB911.Project\\shell\\open\\command", nullptr, openCommand);

    // Windows can preserve an older UserChoice as Applications\\KB911.exe.
    // Give that application ProgID the same project icon and open command too.
    const wchar_t* exeNamePtr = PathFindFileNameW(exe.c_str());
    std::wstring exeName = (exeNamePtr && *exeNamePtr) ? exeNamePtr : L"KB911.exe";
    const std::wstring appKey = L"Software\\Classes\\Applications\\" + exeName;
    SetRegString(HKEY_CURRENT_USER, appKey + L"\\DefaultIcon", nullptr, iconSpec);
    SetRegString(HKEY_CURRENT_USER, appKey + L"\\shell\\open\\command", nullptr, openCommand);
    SetRegString(HKEY_CURRENT_USER, appKey + L"\\SupportedTypes", L".kb911", L"");

    // Also advertise the ProgID to Explorer's per-user OpenWith list without
    // touching the protected UserChoice hash.
    SetRegString(HKEY_CURRENT_USER,
        L"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\.kb911\\OpenWithProgids",
        L"KB911.Project", L"");

    // Force Explorer to discard the old generic/white icon association now.
    SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST | SHCNF_FLUSH, nullptr, nullptr);
}
'''

if old not in s:
    raise SystemExit('v28: RegisterProjectAssociation block not found')
s=s.replace(old,new,1)

for token in [marker,'Software\\\\Classes\\\\Applications\\\\','SHCNF_IDLIST | SHCNF_FLUSH','OpenWithProgids','const std::wstring iconSpec']:
    if token not in s:
        raise SystemExit('v28 guard failed: '+token)

p.write_text(s,encoding='utf-8',newline='')
print('v28: project file association/icon refresh hardened for old .kb911 files')
