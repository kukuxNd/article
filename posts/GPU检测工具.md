Title: GPU检测工具
Date: 2025-03-28
Category: 图形渲染

# GPU 渲染管线阶段剖析工具

以下工具可帮助你在渲染管线中细分分析顶点着色、几何着色、光栅化、片元着色等各阶段的性能表现。按硬件平台与系统分类，并附简要介绍。

---

## 移动端 (Android / iOS)

### Qualcomm 平台 (Android)
- **Snapdragon Profiler** [1]  
  Qualcomm 官方性能剖析工具，支持 Android 真机远程帧捕获与管线阶段分析，可查看顶点着色、片元着色、纹理采样等硬件计数器数据。

### Arm Mali 平台 (Android)
- **Arm Mobile Studio (Mali Graphics Debugger)** [2]  
  Arm 官方图形调试套件，针对 Mali GPU 提供帧捕获、管线阶段时间线可视化，以及多种硬件计数器统计。

### Huawei Kirin 平台 (Android)
- **Huawei Graphics Profiler** [3]  
  华为自研性能剖析工具，专为 Kirin SoC 优化，支持单帧或连续帧捕获，并细分渲染管线各阶段的执行序列与时延。

### Apple 平台 (iOS)
- **Xcode Metal Frame Capture / Instruments** [9]  
  Xcode 集成的 Metal 调试器，可在 iOS 设备上捕获 Metal/OpenGL ES 帧，细分各渲染阶段（顶点／片元）执行情况，并结合 Instruments 采集系统级性能。

---

## 桌面端 (Windows / Linux / macOS)

### NVIDIA GPU (Windows / Linux / macOS)
- **NVIDIA Nsight Graphics** [5]  
  NVIDIA 官方深度调试与剖析工具，支持帧捕获与 GPU Trace，能细分顶点、几何、光栅、片元及后处理各阶段的硬件性能数据。

### AMD GPU (Windows / Linux)
- **AMD Radeon™ GPU Profiler (RGP)** [6]  
  AMD 官方分析器，针对 RDNA 架构提供 Wavefront 层级剖析、事件时序、管线状态与指令级耗时统计。

### Intel GPU (Windows / Linux / macOS)
- **Intel® Graphics Performance Analyzers (GPA)** [7]  
  Intel 官方图形性能套件，Frame Profiler 可对顶点／片元阶段、纹理单元调用和硬件计数器进行细粒度剖析。

### 通用跨平台
- **RenderDoc** [4]  
  开源免费图形调试器，支持跨平台帧捕获与 Pipeline State 查看（着色器输入输出、资源绑定、DrawCall 列表等），并可与厂商 Profiler（RGP、Nsight）联动。

### Windows 专用 (DirectX 12)
- **PIX (for Windows)** [8]  
  微软官方 DirectX 12 性能调试工具，支持 GPU Capture、Timing Capture，分解图形／计算／拷贝队列中每个阶段的执行时间与状态。

---

## 参考链接

1. Snapdragon Profiler | Qualcomm Developer  
   https://www.qualcomm.com/developer/software/snapdragon-profiler  
2. Introduction to Arm Mobile Studio – Mali Graphics Debugger | Arm Developer  
   https://developer.arm.com/documentation/101469/2021-0/Introduction-to-Arm-Development-Studio/Mali-Graphics-Debugger  
3. Huawei Graphics Profiler | Huawei Developer  
   https://developer.huawei.com/consumer/cn/huawei-graphics-profiler/  
4. Shader Viewer — RenderDoc documentation  
   https://renderdoc.org/docs/window/shader_viewer.html  
5. NVIDIA Nsight Graphics | NVIDIA Developer  
   https://developer.nvidia.com/nsight-graphics  
6. Radeon™ GPU Profiler – AMD GPUOpen  
   https://gpuopen.com/rgp/  
7. Intel® Graphics Performance Analyzers (GPA) | Intel  
   https://www.intel.cn/content/www/cn/zh/developer/tools/graphics-performance-analyzers/overview.html  
8. 使用 GPU 捕获分析帧 – Win32 apps | Microsoft Learn  
   https://learn.microsoft.com/zh-cn/windows/win32/direct3dtools/pix/pix-gpu-captures  
9. Capturing a Metal workload in Xcode | Apple Developer  
   https://developer.apple.com/documentation/xcode/capturing-a-metal-workload-in-xcode  
