Title: UE4中可拆解的高性能C++模块
Date: 2014-06-18
Category: C&C++

在自研引擎中，有时我们只想拿 UE4 中「低耦合、轻量级」的那部分功能，从而避免整个引擎源码的庞杂依赖。以下列出了若干常见且易于拆出的模块（含简介、主要功能及最小依赖），并附上官方文档或社区示例的引用，方便你直接把它们拷贝到自己项目里。

---

## 概览

- **Core（Runtime/Core）**：UE 最基础的 C++ 框架，包括基础类型、容器、数学库、日志与线程等，几乎所有模块都依赖它，但它本身没有其他依赖。  
- **Task System & TaskGraph（Runtime/Core/Public/Async）**：轻量的异步任务框架，支持任务图调度与并行循环，实现并发工作分发，仅依赖 Core。  
- **JSON（Runtime/Json）**：纯 C++ 实现的 JSON 解析/序列化库，无外部依赖，仅需 Core。  
- **JsonUtilities（Runtime/JsonUtilities）**：基于 JSON 模块提供的 UObject ↔ JSON 映射工具，依赖 CoreUObject。  
- **HTTP（Runtime/Online/HTTP）**：跨平台 HTTP 客户端，实现 REST 请求，可与 JSON 结合使用，依赖 Core + Json 模块。  
- **Slate Core（Runtime/SlateCore）**：跨平台的基础 UI 框架，仅依赖 Core、InputCore，可用于制作工具或轻量级界面。  

下面按模块分别介绍。

---

## Runtime/Core：最小 C++ 基础库 citeturn1search2

### 功能概览  
- **基本类型与容器**：`FString`/`FName`/`TArray`/`TMap` 等。  
- **数学库**：`FMath`、`FVector`、矩阵与四元数运算。  
- **日志与检查**：`UE_LOG`、`check()`、`ensure()` 宏。  
- **多线程支持**：`FRunnable`、`FRunnableThread`、`FCriticalSection` 等。  
- **序列化接口**：`FArchive` 系列。  

### 依赖  
- 无其他 UE 模块依赖，仅依赖平台 HAL（在 Engine/Source/Runtime/Core）  

---

## Runtime/Core/Public/Async：Task System & TaskGraph citeturn4search0turn4search2

### Task System  
- **API 头**：`#include "Tasks/Task.h"`  
- **特点**：基于任务图的轻量级调度，支持任务依赖、嵌套任务。  

### TaskGraph 接口  
- **Singleton**：`FTaskGraphInterface::Get()` citeturn4search2  
- **异步任务模板**：`TAsyncGraphTask<ResultType>` citeturn4search3  
- **并行循环**：`ParallelFor(...)` 系列函数 citeturn4search5  

### 典型用法  
```cpp
// 并行执行 100 次工作
ParallelFor(100, [](int32 Index){
    // 你的并行逻辑
});
```

---

## Runtime/Json：纯 C++ JSON 库 citeturn3search4

### 核心类  
- `FJsonSerializer`/`FJsonReader`/`FJsonWriter`  
- `TSharedPtr<FJsonObject>`、`TSharedPtr<FJsonValue>`  

### 模块依赖  
- **仅依赖**：Core 模块  

### 代码示例  
```cpp
FString JsonString = TEXT("{\"key\":42}");
TSharedPtr<FJsonObject> JsonObj;
TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonString);
if (FJsonSerializer::Deserialize(Reader, JsonObj)) {
    int32 Value = JsonObj->GetIntegerField(TEXT("key"));
}
```

---

## Runtime/JsonUtilities：UStruct ↔ JSON 映射 citeturn3search9

### 主要功能  
- `FJsonObjectConverter::UStructToJsonObjectString(...)`  
- `FJsonObjectConverter::JsonObjectToUStruct(...)`  

### 模块依赖  
- **Core**, **CoreUObject**（用于 UObject/UStruct 反射）  

---

## Runtime/Online/HTTP：轻量级 HTTP 客户端 citeturn3search2

### 典型 API  
- `FHttpModule::Get().CreateRequest()`  
- 支持 `OnProcessRequestComplete` 回调  

### 依赖  
- **Core**, **Json**（如需解析 JSON 响应）  

---

## Runtime/SlateCore：独立 UI 基础 citeturn0search1

### 功能  
- 基础绘制命令（Slate 核心 Widget 与绘制接口）。  
- **不含** Editor 扩展，仅窗口层面 UI。  

### 模块依赖  
- **Core**, **InputCore**  

---

## 其他可选“轻量”组件

- **FastXml**（Core/Public/HAL/FastXml.h）：高性能 XML 解析，依赖 Core。  
- **CsvParser**（Core/Public/Misc/CsvParser.h）：CSV 文本解析，依赖 Core。  
- **Delegate**（Core/Public/Delegates）：多播事件系统，依赖 Core。  
- **Logging**：`UE_LOG`、`GLog`、`FOutputDevice` 系列，依赖 Core。  
- **Reflection 辅助**：`ReflectionCapture.h`、`PropertyPathHelpers.h` 等零散工具，可按需拷贝。  

---

### 拆出方法与注意事项

1. **复制对应模块目录**：如要使用 JSON，就拷 `Engine/Source/Runtime/Json/` 整个目录，并在你的 CMake/VS 项目里加入头路径。  
2. **处理宏定义**：Core 模块里有大量平台与编译配置宏，需在你的项目中同步 `BuildConfigurations`、`PlatformTypes` 等头文件。  
3. **裁剪无用部分**：比如 HTTP 里只用 JSON，就删掉与 FTP、WebSocket 无关的文件。  
4. **测试先行**：将每个模块放入你的引擎后，先写最小 demo（例如只用 `FString`、`ParallelFor`、`FJsonSerializer`）验证可编译再逐步扩展。

通过上述拆分方式，你可以在自研引擎中重用 UE4 众多成熟工具，而无需承担全引擎的重量与复杂度。