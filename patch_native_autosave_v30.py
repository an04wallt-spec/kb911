from pathlib import Path

p = Path('src/main.cpp')
s = p.read_text(encoding='utf-8')


def replace_once(old, new):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'native autosave v30: expected one anchor, got {count}: {old[:140]}')
    s = s.replace(old, new, 1)


replace_once(
    'static std::wstring g_pendingProjectPath;\n',
    'static std::wstring g_pendingProjectPath;\nstatic bool g_startedWithProjectFileV30 = false;\n'
)

helpers = r'''
// KB911_V30_NATIVE_AUTOSAVE
static std::wstring AutosavePathV30() {
    std::wstring root = GetLocalAppDataDir() + L"\\KB911";
    EnsureDir(root);
    return root + L"\\recovery-v1.json";
}

static bool WriteUtf8AtomicV30(const std::wstring& path, const std::wstring& text) {
    int n = WideCharToMultiByte(CP_UTF8, 0, text.data(), static_cast<int>(text.size()), nullptr, 0, nullptr, nullptr);
    if (n < 0) return false;
    std::string bytes(static_cast<size_t>(n), '\0');
    if (n > 0 && WideCharToMultiByte(CP_UTF8, 0, text.data(), static_cast<int>(text.size()), bytes.data(), n, nullptr, nullptr) != n) return false;

    const std::wstring tmp = path + L".tmp";
    HANDLE h = CreateFileW(tmp.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (h == INVALID_HANDLE_VALUE) return false;

    bool ok = true;
    size_t off = 0;
    while (off < bytes.size()) {
        DWORD chunk = static_cast<DWORD>(std::min<size_t>(bytes.size() - off, 16 * 1024 * 1024));
        DWORD written = 0;
        if (!WriteFile(h, bytes.data() + off, chunk, &written, nullptr) || written != chunk) { ok = false; break; }
        off += written;
    }
    if (ok) ok = FlushFileBuffers(h) != FALSE;
    CloseHandle(h);
    if (!ok) { DeleteFileW(tmp.c_str()); return false; }

    if (!MoveFileExW(tmp.c_str(), path.c_str(), MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)) {
        DeleteFileW(tmp.c_str());
        return false;
    }
    return true;
}

static void ClearAutosaveV30() {
    const std::wstring path = AutosavePathV30();
    DeleteFileW(path.c_str());
    DeleteFileW((path + L".tmp").c_str());
}

static void SendAutosaveRecoveryToWebV30() {
    if (!g_webview || g_startedWithProjectFileV30) return;
    const std::wstring path = AutosavePathV30();
    if (GetFileAttributesW(path.c_str()) == INVALID_FILE_ATTRIBUTES) return;
    std::wstring text = ReadUtf8TextFile(path);
    if (text.empty()) { ClearAutosaveV30(); return; }
    std::wstring msg = L"KB911_AUTOSAVE_RECOVERY|" + text;
    g_webview->PostWebMessageAsString(msg.c_str());
}

'''
replace_once('static void HandleWebMessage(ICoreWebView2WebMessageReceivedEventArgs* args) {', helpers + 'static void HandleWebMessage(ICoreWebView2WebMessageReceivedEventArgs* args) {')

message_anchor = '    const std::wstring prefix = L"KB911_SIZE|";'
message_new = r'''    const std::wstring autosavePrefixV30 = L"KB911_AUTOSAVE_SAVE|";
    if (s.rfind(autosavePrefixV30, 0) == 0) {
        const std::wstring payload = s.substr(autosavePrefixV30.size());
        const bool ok = !payload.empty() && WriteUtf8AtomicV30(AutosavePathV30(), payload);
        if (g_webview) g_webview->PostWebMessageAsString(ok ? L"KB911_AUTOSAVE_SAVED" : L"KB911_AUTOSAVE_ERROR");
        return;
    }
    if (s == L"KB911_AUTOSAVE_CLEAR") {
        ClearAutosaveV30();
        return;
    }

    const std::wstring prefix = L"KB911_SIZE|";'''
replace_once(message_anchor, message_new)

replace_once(
    '                                        SendPendingProjectToWeb();',
    '                                        SendPendingProjectToWeb();\n                                        SendAutosaveRecoveryToWebV30();'
)

cmd = '        if (argc > 1 && argv[1] && EndsWithI(argv[1], L".kb911")) g_pendingProjectPath = argv[1];'
cmd_v30 = '        if (argc > 1 && argv[1] && EndsWithI(argv[1], L".kb911")) { g_pendingProjectPath = argv[1]; g_startedWithProjectFileV30 = true; }'
replace_once(cmd, cmd_v30)

for token in [
    'KB911_V30_NATIVE_AUTOSAVE',
    'recovery-v1.json',
    'KB911_AUTOSAVE_SAVE|',
    'KB911_AUTOSAVE_RECOVERY|',
    'MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH',
    'SendAutosaveRecoveryToWebV30();'
]:
    if token not in s:
        raise SystemExit('native autosave v30 guard failed: '+token)

p.write_text(s, encoding='utf-8', newline='')
print('Native atomic autosave storage installed')
