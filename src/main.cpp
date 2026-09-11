#define NOMINMAX
#include <windows.h>
#include <shlobj.h>
#include <shlwapi.h>
#include <wrl.h>
#include <string>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <cmath>
#include "WebView2.h"
#include "resource.h"

using Microsoft::WRL::Callback;

static HWND g_hwnd = nullptr;
static Microsoft::WRL::ComPtr<ICoreWebView2Controller> g_controller;
static Microsoft::WRL::ComPtr<ICoreWebView2> g_webview;
static double g_paperWmm = 297.0;
static double g_paperHmm = 210.0;

static std::wstring GetLocalAppDataDir() {
    PWSTR p = nullptr;
    std::wstring out;
    if (SUCCEEDED(SHGetKnownFolderPath(FOLDERID_LocalAppData, 0, nullptr, &p))) {
        out = p;
        CoTaskMemFree(p);
    }
    return out;
}

static bool EnsureDir(const std::wstring& path) {
    return SHCreateDirectoryExW(nullptr, path.c_str(), nullptr) == ERROR_SUCCESS || GetLastError() == ERROR_ALREADY_EXISTS;
}

static std::wstring ExtractEmbeddedHtml(HINSTANCE hInst) {
    HRSRC hrsrc = FindResourceW(hInst, MAKEINTRESOURCEW(IDR_APP_HTML), RT_RCDATA);
    if (!hrsrc) return L"";
    HGLOBAL hglob = LoadResource(hInst, hrsrc);
    if (!hglob) return L"";
    DWORD size = SizeofResource(hInst, hrsrc);
    const void* data = LockResource(hglob);
    if (!data || !size) return L"";

    std::wstring root = GetLocalAppDataDir() + L"\\KB911";
    std::wstring runtime = root + L"\\runtime";
    EnsureDir(root);
    EnsureDir(runtime);
    std::wstring file = runtime + L"\\KB911.html";
    HANDLE h = CreateFileW(file.c_str(), GENERIC_WRITE, FILE_SHARE_READ, nullptr, CREATE_ALWAYS,
                           FILE_ATTRIBUTE_NORMAL, nullptr);
    if (h == INVALID_HANDLE_VALUE) return L"";
    DWORD written = 0;
    BOOL ok = WriteFile(h, data, size, &written, nullptr);
    CloseHandle(h);
    return (ok && written == size) ? file : L"";
}

static std::wstring FileUrl(const std::wstring& path) {
    DWORD len = 4096;
    std::wstring url(len, L'\0');
    if (UrlCreateFromPathW(path.c_str(), url.data(), &len, 0) != S_OK) return L"";
    url.resize(len);
    return url;
}

static void ResizeWebView() {
    if (!g_controller || !g_hwnd) return;
    RECT r{};
    GetClientRect(g_hwnd, &r);
    g_controller->put_Bounds(r);
}

static void FitWindowToPaper(double wmm, double hmm) {
    g_paperWmm = wmm;
    g_paperHmm = hmm;

    HMONITOR mon = MonitorFromWindow(g_hwnd, MONITOR_DEFAULTTONEAREST);
    MONITORINFO mi{ sizeof(mi) };
    GetMonitorInfoW(mon, &mi);
    int workW = mi.rcWork.right - mi.rcWork.left;
    int workH = mi.rcWork.bottom - mi.rcWork.top;

    UINT dpi = 96;
    HMODULE user32 = GetModuleHandleW(L"user32.dll");
    if (user32) {
        using GetDpiForWindowFn = UINT(WINAPI*)(HWND);
        auto fn = reinterpret_cast<GetDpiForWindowFn>(GetProcAddress(user32, "GetDpiForWindow"));
        if (fn) dpi = fn(g_hwnd);
    }

    const double pxPerMm = static_cast<double>(dpi) / 25.4;
    const int sidebarPx = static_cast<int>(265.0 * dpi / 96.0);
    const int chromeX = static_cast<int>(110.0 * dpi / 96.0);
    const int chromeY = static_cast<int>(135.0 * dpi / 96.0);

    int wantedClientW = static_cast<int>(std::round(wmm * pxPerMm)) + sidebarPx + chromeX;
    int wantedClientH = static_cast<int>(std::round(hmm * pxPerMm)) + chromeY;

    RECT wr{ 0,0,wantedClientW,wantedClientH };
    AdjustWindowRectEx(&wr, WS_OVERLAPPEDWINDOW, FALSE, 0);
    int wantedW = wr.right - wr.left;
    int wantedH = wr.bottom - wr.top;

    const int maxW = static_cast<int>(workW * 0.94);
    const int maxH = static_cast<int>(workH * 0.94);
    wantedW = std::min(wantedW, maxW);
    wantedH = std::min(wantedH, maxH);
    wantedW = std::max(wantedW, 900);
    wantedH = std::max(wantedH, 650);

    int x = mi.rcWork.left + (workW - wantedW) / 2;
    int y = mi.rcWork.top + (workH - wantedH) / 2;
    SetWindowPos(g_hwnd, nullptr, x, y, wantedW, wantedH,
                 SWP_NOZORDER | SWP_NOACTIVATE);

    if (g_webview) {
        g_webview->ExecuteScript(L"window.KB911_fitToViewport && window.KB911_fitToViewport();", nullptr);
    }
}

static void HandleWebMessage(ICoreWebView2WebMessageReceivedEventArgs* args) {
    LPWSTR raw = nullptr;
    if (FAILED(args->TryGetWebMessageAsString(&raw)) || !raw) return;
    std::wstring s(raw);
    CoTaskMemFree(raw);
    const std::wstring prefix = L"KB911_SIZE|";
    if (s.rfind(prefix, 0) != 0) return;
    size_t p = s.find(L'|', prefix.size());
    if (p == std::wstring::npos) return;
    try {
        double w = std::stod(s.substr(prefix.size(), p - prefix.size()));
        double h = std::stod(s.substr(p + 1));
        if (w > 0 && h > 0) FitWindowToPaper(w, h);
    } catch (...) {}
}

static void InitWebView(HINSTANCE hInst) {
    std::wstring htmlPath = ExtractEmbeddedHtml(hInst);
    if (htmlPath.empty()) {
        MessageBoxW(g_hwnd, L"Не удалось подготовить встроенный интерфейс KB911.", L"KB911", MB_ICONERROR);
        return;
    }
    std::wstring userData = GetLocalAppDataDir() + L"\\KB911\\WebView2";
    EnsureDir(GetLocalAppDataDir() + L"\\KB911");
    EnsureDir(userData);

    HRESULT hr = CreateCoreWebView2EnvironmentWithOptions(
        nullptr,
        userData.c_str(),
        nullptr,
        Callback<ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler>(
            [htmlPath](HRESULT result, ICoreWebView2Environment* env) -> HRESULT {
                if (FAILED(result) || !env) {
                    MessageBoxW(g_hwnd,
                        L"Для KB911 требуется Microsoft Edge WebView2 Runtime.\nОбычно он уже установлен в Windows 10/11.",
                        L"KB911", MB_ICONERROR);
                    return result;
                }
                return env->CreateCoreWebView2Controller(
                    g_hwnd,
                    Callback<ICoreWebView2CreateCoreWebView2ControllerCompletedHandler>(
                        [htmlPath](HRESULT result2, ICoreWebView2Controller* controller) -> HRESULT {
                            if (FAILED(result2) || !controller) return result2;
                            g_controller = controller;
                            controller->get_CoreWebView2(&g_webview);
                            ResizeWebView();

                            Microsoft::WRL::ComPtr<ICoreWebView2Settings> settings;
                            if (SUCCEEDED(g_webview->get_Settings(&settings)) && settings) {
                                settings->put_AreDefaultContextMenusEnabled(TRUE);
                                settings->put_AreDevToolsEnabled(FALSE);
                                settings->put_IsStatusBarEnabled(FALSE);
                            }

                            EventRegistrationToken token{};
                            g_webview->add_WebMessageReceived(
                                Callback<ICoreWebView2WebMessageReceivedEventHandler>(
                                    [](ICoreWebView2*, ICoreWebView2WebMessageReceivedEventArgs* args) -> HRESULT {
                                        HandleWebMessage(args);
                                        return S_OK;
                                    }).Get(), &token);

                            std::wstring url = FileUrl(htmlPath);
                            g_webview->Navigate(url.c_str());
                            FitWindowToPaper(297.0, 210.0);
                            return S_OK;
                        }).Get());
            }).Get());

    if (FAILED(hr)) {
        MessageBoxW(g_hwnd, L"Не удалось запустить WebView2.", L"KB911", MB_ICONERROR);
    }
}

static LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp) {
    switch (msg) {
    case WM_SIZE:
        ResizeWebView();
        if (g_webview) {
            g_webview->ExecuteScript(L"window.KB911_fitToViewport && window.KB911_fitToViewport();", nullptr);
        }
        return 0;
    case WM_CLOSE:
        DestroyWindow(hwnd);
        return 0;
    case WM_DESTROY:
        g_webview.Reset();
        g_controller.Reset();
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProcW(hwnd, msg, wp, lp);
}

int WINAPI wWinMain(HINSTANCE hInst, HINSTANCE, PWSTR, int nCmdShow) {
    SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);
    CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);

    WNDCLASSEXW wc{ sizeof(wc) };
    wc.style = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInst;
    wc.hCursor = LoadCursorW(nullptr, IDC_ARROW);
    wc.hbrBackground = reinterpret_cast<HBRUSH>(COLOR_WINDOW + 1);
    wc.lpszClassName = L"KB911WindowClass";
    wc.hIcon = static_cast<HICON>(LoadImageW(hInst, MAKEINTRESOURCEW(IDI_APP_ICON), IMAGE_ICON, 0, 0, LR_DEFAULTSIZE));
    if (!wc.hIcon) wc.hIcon = LoadIconW(nullptr, IDI_APPLICATION);
    wc.hIconSm = static_cast<HICON>(LoadImageW(hInst, MAKEINTRESOURCEW(IDI_APP_ICON), IMAGE_ICON, 16, 16, LR_DEFAULTCOLOR));
    if (!wc.hIconSm) wc.hIconSm = wc.hIcon;
    RegisterClassExW(&wc);

    g_hwnd = CreateWindowExW(0, wc.lpszClassName, L"KB911",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, 1280, 820,
        nullptr, nullptr, hInst, nullptr);
    if (!g_hwnd) return 1;

    ShowWindow(g_hwnd, nCmdShow);
    UpdateWindow(g_hwnd);
    InitWebView(hInst);

    MSG m{};
    while (GetMessageW(&m, nullptr, 0, 0) > 0) {
        TranslateMessage(&m);
        DispatchMessageW(&m);
    }
    CoUninitialize();
    return static_cast<int>(m.wParam);
}
