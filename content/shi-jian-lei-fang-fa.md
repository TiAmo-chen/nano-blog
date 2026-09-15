---
title: C++ 时间类方法
date: 2026-01-30
tags: [C++, 时间处理]
slug: shi-jian-lei-fang-fa
---
```cpp
SYSTEMTIME st;
::GetLocalTime(&st);//当前时间
TCHAR strLogPath[MAX_PATH];
_stprintf_s(strLogPath, MAX_PATH, _T("%s\\%02d_%02d_%02d_%02d_%02d_%02d.csv"), m_report.c_str(), st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond);


```

********
```cpp
struct tm tm;
time_t t = time(NULL);
localtime_s(&tm, &t);
char buf[128];
strftime(buf, sizeof(buf), "%Y_%m_%d__%H_%M_%S", &tm);

```

********
```cpp
#include <chrono>
chrono::steady_clock::time_point t1;
t1 = chrono::steady_clock::now();
t2 = chrono::steady_clock::now();
AddThreadLog((boost::format("%s[INFO]:Sensor烧录成功,总耗时:%dms") % __FUNCTION__% std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count()).str());


auto tt = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
struct tm* ptm = localtime(&tt);

std::string fail_path = (boost::format("%s\\%s_%04d%02d%02d%02d%02d%02d.bmp") % txtpath % product_sn.c_str() % (ptm->tm_year + 1900) % (ptm->tm_mon + 1) % (ptm->tm_mday) % (ptm->tm_hour) % (ptm->tm_min) % (ptm->tm_sec)).str();


```

********
- 32位的无符号整数（`DWORD`）大约是49天,有溢出风险
```cpp
#define _WIN32_WINNT 0x0600 // Windows Vista
//GetTickCount64必须使用的宏
ULONGLONG start_time = GetTickCount64();

DWORD end_time = GetTickCount();


```

[GetTickCount64 函数 (sysinfoapi.h) - Win32 apps | Microsoft Learn](https://learn.microsoft.com/zh-cn/windows/win32/api/sysinfoapi/nf-sysinfoapi-gettickcount64?redirectedfrom=MSDN)

## 延时的几种方法

[# C++中延时的几种使用方式](https://blog.csdn.net/Littlehero_121/article/details/104021642)

[# 计时器使用steady_clock还是high_resolution_clock](https://blog.csdn.net/caohongfei881/article/details/100631743)

- vs2013 win10 使用steady_clock

参考：Boost 时间管理库