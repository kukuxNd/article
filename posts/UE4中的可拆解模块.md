Title: UE4中可拆解的高性能C++模块
Date: 2014-06-18
Category: Unreal&Unity

---

# 在自研引擎中复用 UE4 的“低耦合、轻量级”模块

在自研引擎中，有时我们只想拿 UE4 中「低耦合、轻量级」的那部分功能，从而避免整引擎源码的庞杂依赖。以下列出了若干常见且易于拆出的模块（含简介、主要功能及最小依赖），并附上官方文档或社区示例的引用，方便你直接将对应目录拷贝到自己项目里。

---

## 概览

- **Core**：基础 C++ 框架，提供基本类型、容器、数学库、日志与多线程等功能，且无额外依赖 [1]  
- **Task System & TaskGraph**：轻量异步任务调度，支持任务图、并行循环，仅依赖 Core [2][3][4]  
- **JSON**：纯 C++ JSON 库，序列化/反序列化功能，无外部依赖，仅需 Core [5]  
- **JsonUtilities**：UStruct ↔ JSON 映射工具，依赖 CoreUObject [6]  
- **HTTP**：跨平台 HTTP 客户端，支持 REST 请求，依赖 Core + Json [7]  
- **SlateCore**：跨平台 UI 框架，仅依赖 Core、InputCore，可用于轻量级界面 [8]  

---

## Runtime/Core：最小 C++ 基础库

- **基本类型与容器**：`FString` / `FName` / `TArray` / `TMap`  
- **数学库**：`FMath`, `FVector`, 矩阵与四元数  
- **日志与检查**：`UE_LOG`、`check()`、`ensure()` 宏  
- **多线程支持**：`FRunnable`、`FRunnableThread`、`FCriticalSection`  
- **序列化接口**：`FArchive`

**依赖**：仅平台 HAL，无其他 UE 模块依赖 [1]

---

## Runtime/Core/Public/Async：Task System & TaskGraph

### Task System

- **头文件**：`#include "Tasks/Task.h"`
- **特点**：基于任务图轻量调度，支持任务依赖、嵌套任务 [3]

### TaskGraph 接口

- **获取实例**：`FTaskGraphInterface::Get()`
- **异步任务**：`TAsyncGraphTask<ResultType>`
- **并行循环**：`ParallelFor(Num, Lambda)` [2]

### 任务完成回调

- `FTaskGraphInterface::TriggerEventWhenTasksComplete(...)` [4]

---

## Runtime/Json：纯 C++ JSON 库

- **核心类**：`FJsonSerializer` / `FJsonReader` / `FJsonWriter`  
- **容器类型**：`TSharedPtr<FJsonObject>`、`TSharedPtr<FJsonValue>`  
- **模块依赖**：仅需 Core [5]

```cpp
FString JsonString = TEXT("{\"key\":42}");
TSharedPtr<FJsonObject> JsonObj;
TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonString);
if (FJsonSerializer::Deserialize(Reader, JsonObj)) {
    int32 Value = JsonObj->GetIntegerField(TEXT("key"));
}
```

---

## Runtime/JsonUtilities：UStruct ↔ JSON 映射

- **主要功能**：
  - `FJsonObjectConverter::UStructToJsonObjectString(...)`
  - `FJsonObjectConverter::JsonObjectToUStruct(...)`
- **模块依赖**：Core + CoreUObject [6]

---

## Runtime/Online/HTTP：轻量级 HTTP 客户端

- **典型 API**：
  - `FHttpModule::Get().CreateRequest()`
  - `OnProcessRequestComplete` 回调
- **依赖**：Core + Json [7]

---

## Runtime/SlateCore：独立 UI 基础

- **功能**：基础绘制命令、Slate 核心 Widget 与绘制接口
- **模块依赖**：Core、InputCore [8]

---

## 其他可选“轻量”组件

- **FastXml（XML 解析）**：`FFastXml` 实现无额外依赖 [9]  
- **Delegate（多播事件）**：类型安全的回调机制，支持 UObject 与普通类绑定 [10]  
- **Logging（日志系统）**：`UE_LOG` 宏，printf 风格输出到屏幕与日志文件 [11]  
- **Reflection 辅助**：零散工具如 `PropertyPathHelpers.h`、`ReflectionCapture.h` 等，可按需拷贝。

---

## 拆出方法与注意事项

1. **复制模块目录**：将 `Engine/Source/Runtime/<模块名>/` 拷贝到自研引擎中，并在 CMake/VS 项目里加入头路径。
2. **同步宏定义**：拷贝 `BuildConfigurations.h`、`PlatformTypes.h` 等宏配置头文件。
3. **裁剪无用部分**：如 HTTP 中只需 JSON，删除 FTP、WebSocket 相关文件。
4. **逐步测试**：先用最小 demo（如只用 `FString`、`ParallelFor`、`FJsonSerializer`）验证可编译，再逐步扩展。

---

## 参考地址

[1] [IWYU | Unreal Engine 4.27 Documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/iwyu?application_version=4.27)  
[2] [ParallelFor() in UE](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Core/Async/ParallelForWithTaskContext/2)  
[3] [Tasks API Reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Core/Async/Task)  
[4] [FTaskGraphInterface::TriggerEventWhenTasksComplete](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Core/Async/FTaskGraphInterface/TriggerEventWhenTasksComplete)  
[5] [Serialization (Json) API Reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Json/Serialization)  
[6] [FJsonObjectConverter API Reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/JsonUtilities/FJsonObjectConverter)  
[7] [FHttpModule API Reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/HTTP/FHttpModule)  
[8] [SlateCore Overview | UE4 Docs](https://docs.unrealengine.com/4.27/en-US/ProgrammingAndScripting/Slate/SlateCore/)  
[9] [FastXml.h | Epic GitHub](https://github.com/EpicGames/UnrealEngine/blob/release/Engine/Source/Runtime/Core/Public/HAL/FastXml.h)  
[10] [Delegates in Unreal Engine](https://docs.unrealengine.com/4.27/en-US/ProgrammingAndScripting/ProgrammingWithCPP/Delegates/)  
[11] [Logging System | UE4 Docs](https://docs.unrealengine.com/4.27/en-US/ProgrammingAndScripting/ProgrammingWithCPP/Logging/)


---
