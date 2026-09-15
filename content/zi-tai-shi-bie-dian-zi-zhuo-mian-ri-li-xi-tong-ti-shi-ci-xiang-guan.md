---
title: 嵌入式项目开发指南 - 姿态识别电子桌面日历系统
date: 2026-04-20
tags: [嵌入式, 项目开发, STM32, MPU6050, TFT, DHT11]
slug: zi-tai-shi-bie-dian-zi-zhuo-mian-ri-li-xi-tong-ti-shi-ci-xiang-guan
---
一、项目目标（写清楚给 Claude Code）

你可以直接用这段当项目描述：

使用 STM32F103C8T6 + GY-87 + 1.8寸 TFT（128x160 SPI）+ DHT11，实现一个姿态识别电子桌面日历系统。
系统通过 IMU 检测翻转/倾斜动作，切换不同信息页面（日期 / 时间 / 温湿度 / 状态页），并在 TFT 上实时显示。系统支持低功耗待机与外部中断唤醒。

⸻

 二、系统模块拆分（Claude Code 工作单元）

这个项目建议拆成 5 个模块，让 AI 分别生成：

Module 1：硬件抽象层（HAL封装）

内容：
	•	GPIO初始化
	•	SPI（TFT）
	•	I2C（GY-87）
	•	ADC（如果扩展）
	•	Delay / SysTick

输出：

bsp_gpio.c
bsp_spi.c
bsp_i2c.c
bsp_delay.c


⸻

Module 2：GY-87 姿态识别

功能：
	•	MPU6050读取加速度 + 陀螺仪
	•	简单姿态判断：

平放
倒置
左倾
右倾
翻转

核心算法（建议简单版）：
	•	用加速度 z 轴判断上下
	•	用 x/y 判断倾斜

输出：

imu_mpu6050.c
imu_posture.c


⸻

Module 3：TFT 1.8 显示驱动

功能：
	•	SPI初始化
	•	LCD初始化（ST7735驱动）
	•	基础绘图：

draw_pixel
draw_line
draw_rect
draw_text
clear_screen

输出：

tft_st7735.c
tft_graphics.c
font.c


⸻

Module 4：DHT11 温湿度模块

功能：
	•	单总线协议
	•	读取温度湿度
	•	返回结构体

输出：

dht11.c


⸻

Module 5：应用逻辑（核心）

这是最重要部分：

状态机设计：

enum AppState {
    PAGE_TIME,
    PAGE_DATE,
    PAGE_WEATHER_DUMMY,
    PAGE_SENSOR
};


⸻

触发逻辑：
	•	GY-87检测姿态变化 → 切页
	•	每3秒刷新数据
	•	DHT11每10秒更新

⸻

页面设计：

PAGE_DATE
	•	日期
	•	星期
 PAGE_TIME
	•	时:分:秒

PAGE_SENSOR
	•	温度
	•	湿度

PAGE_WEATHER（占位）
	•	以后扩展

 输出：

app_main.c
ui_pages.c
state_machine.c


⸻

 三、系统运行流程（Claude Code 必须理解）

上电
 ↓
初始化 STM32
 ↓
初始化 TFT / IMU / DHT11
 ↓
进入主循环

while(1)
{
    读取IMU
    如果姿态变化 → 切换页面

    每1s：
        更新时间

    每3s：
        刷新屏幕

    每10s：
        读取温湿度

    进入低功耗等待（可选）
}


⸻

⚙️ 四、建议的开发顺序（非常重要）

不要一次性写完

⸻

 Step 1（先跑屏幕）

Claude Code任务：

“帮我写 STM32F103 + ST7735 TFT 初始化 + 显示 Hello World”

成功标志：屏幕亮

⸻

 Step 2（加 IMU）

任务：

“读取 MPU6050 加速度并通过串口输出”

 成功标志：能看到 x/y/z

⸻

Step 3（姿态识别）

任务：

“根据 MPU6050 加速度判断设备是否翻转”

 输出：

UP / DOWN / LEFT / RIGHT


⸻

Step 4（UI状态机）

任务：

“实现 TFT 页面切换系统（3个页面）”

⸻

Step 5（DHT11）

任务：

“读取温湿度并显示在屏幕”

⸻

Step 6（整合）

任务：

“整合 IMU + UI + DHT11 + 状态机”

⸻

五、给 Claude Code 的“总提示词”（可以直接复制）

你可以直接丢这个：

⸻

Claude Code Prompt：

请基于 STM32F103C8T6（标准外设库或HAL均可）开发一个嵌入式应用：

硬件包括：
	•	GY-87（MPU6050）
	•	ST7735 1.8寸 SPI TFT（128x160）
	•	DHT11 温湿度模块

实现功能：
	1.	通过 MPU6050 判断设备姿态（正常/翻转/左右倾斜）
	2.	根据姿态切换显示页面
	3.	TFT显示三种页面：时间/日期/温湿度
	4.	DHT11周期性采集温湿度
	5.	使用状态机管理UI

请分模块生成代码（driver + middleware + app），并保证可移植性。

⸻

🧩 六、这个项目的关键设计点（避免翻车）

⚠️ 1. IMU不要用复杂滤波
	•	先用原始加速度
	•	不要一开始上卡尔曼

⸻

⚠️ 2. TFT刷新别太频繁
	•	1~3秒刷新一次足够

⸻

⚠️ 3. 状态机必须清晰

否则 Claude 会写成一坨 loop

⸻

⚠️ 4. DHT11要独立任务
	•	否则会卡主主循环

⸻

🚀 七、最终效果（你会得到什么）

完成后你这个系统会是：

👉 放桌上：
	•	翻转 → 自动切页面
	•	显示时间/温湿度
	•	有“电子设备交互感”

⸻

如果你下一步要继续，我可以帮你：
	•	✍️ 直接帮你写“STM32工程目录结构（可导入CubeIDE）”
	•	⚡ MPU6050姿态判断代码（可以直接用）
	•	📺 ST7735最小驱动（让屏先亮）
	•	🧠 Claude Code拆任务模板（更细粒度）

这个项目其实已经进入：
👉 “可以开始写第一行驱动代码”的阶段了