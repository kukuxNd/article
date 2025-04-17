Title: Lua检测工具
Date: 2015-01-08
Category: 性能优化

Unity + Lua 组合在手游和国产项目中常见，但 Lua 的性能检测、内存泄漏排查、协程卡顿、GC频繁等问题，往往是难点。以下是 **Unity + Lua 环境下的 Lua 调试与分析工具**，涵盖 **性能分析、内存检测、调用栈追踪、热更辅助** 等内容。

---

## 🔧 Unity + Lua 性能分析与调试工具

### 1. **LuaProfiler（腾讯开源）**  
- **功能**：采集函数调用耗时、调用栈、GC 信息  
- **特点**：适用于 `ToLua` / `xlua` 环境，兼容 Unity  
- **地址**：<https://github.com/LuaProfiler/LuaProfiler>  
- **说明**：支持将数据发送到 `Unity Editor` 控制台或写入文件，适合嵌入游戏逻辑分析。

---

### 2. **xlua自带的统计功能（xlua.statistic）**  
- **功能**：内存对象统计、Lua表数量、GC分析  
- **说明**：`require("xlua.util").start()` 开启后，会在控制台打印出 Lua 表和 C# 引用关系  
- **适用范围**：仅适用于 xlua，内置功能轻量但实用  
- **链接**：<https://github.com/Tencent/xLua>

---

### 3. **MobDebug + ZeroBraneStudio**  
- **功能**：完整的 Lua 单步调试器，支持断点、变量查看  
- **说明**：适合在 PC 上远程调试 Lua 脚本，嵌入 Unity 工程中调试 Lua 模块  
- **地址**：  
  - MobDebug: <https://github.com/pkulchenko/MobDebug>  
  - ZeroBrane Studio: <https://studio.zerobrane.com/>  

---

### 4. **Pluto（冷门但强大）**  
- **功能**：Lua 函数序列化/反序列化，保存 Lua 状态，适合热更与状态转储  
- **地址**：<https://github.com/hoelzro/lua-pluto>  
- **注意**：需搭配 LuaJIT 或支持 C 扩展的运行环境

---

### 5. **Lua Memory Snapshot 工具（字节跳动内部工具）**  
- **功能**：快照 Lua 内存状态，找出泄漏对象和引用链  
- **说明**：虽然未完全开源，但可以模仿其原理：  
  - 用 `debug.getregistry()` 遍历所有 Lua 对象  
  - 构建引用图，查找无法被 GC 回收的链路  
- **参考实现**：<https://zhuanlan.zhihu.com/p/48083093>  

---

### 6. **Unity Profiler + Lua Hook 联动**  
- 自定义插桩，在关键 Lua 函数中使用 `UnityEngine.Profiling.Profiler.BeginSample("XXX")` 包裹逻辑  
- 可以让 Lua 调用出现在 Unity Profiler 的时间轴上  
- 示例代码：
  ```lua
  local Profiler = CS.UnityEngine.Profiling.Profiler
  function WrappedFunc()
      Profiler.BeginSample("MyLuaFunc")
      -- your logic
      Profiler.EndSample()
  end
  ```

---

### 7. **LuaTrace**  
- **功能**：收集函数调用频率和耗时，追踪 callgraph  
- **特点**：轻量级，Lua 5.1/5.3 通用  
- **地址**：<https://github.com/geoffleyland/luatrace>  

---

### 🔍 小贴士（适配建议）

| 框架   | 推荐工具                   | 调用耗时 | 内存泄漏 | 热更状态 | 调试断点 |
|--------|----------------------------|----------|----------|-----------|------------|
| xlua   | LuaProfiler + xlua.stat    | ✅       | ✅       | ✅        | ❌（推荐 MobDebug） |
| ToLua  | LuaProfiler + Unity Profiler | ✅     | ✅       | ✅        | ❌           |
| SLua   | 需手动嵌入 debug/tracer     | ✅       | ✅       | ❌        | ❌           |

---

太好了，下面给你整理出：

---

## ✅ **Unity + Lua 项目性能分析接入脚本示例（基于 xlua + LuaProfiler）**

### 🔧 1. 安装 LuaProfiler（适配 xlua/toLua）

- Github 项目地址：<https://github.com/LuaProfiler/LuaProfiler>
- 将 `LuaProfiler` 中的 `LuaProfiler` 文件夹放入 Unity 的 `Assets/Plugins/` 目录中。
- 根据使用的框架（xlua / tolua）选择集成方式。

---

### 🧩 2. Unity C# 接入（示例）

```csharp
using UnityEngine;
using LuaInterface; // 对于 ToLua
using XLua;         // 对于 xLua

public class LuaProfilerInitializer : MonoBehaviour
{
    public LuaEnv luaEnv;

    void Start()
    {
        // 若是 xLua 框架
        LuaProfiler.SetMainLuaEnv(luaEnv);
        LuaProfiler.BeginSample("LuaProfilerStart");
        luaEnv.DoString("require('main')"); // 启动你的主 Lua 文件
        LuaProfiler.EndSample();
    }

    void Update()
    {
        LuaProfiler.Update();
    }

    void OnDestroy()
    {
        LuaProfiler.Destroy();
    }
}
```

---

### 📜 3. Lua 接入代码（main.lua）

```lua
local Profiler = require("LuaProfiler")

Profiler.start("LuaProfileLog")  -- 日志输出路径（自动加时间戳）

function heavy_logic()
    Profiler.beginSample("heavy_logic")

    -- 模拟 CPU 消耗逻辑
    for i = 1, 1e5 do
        local x = math.sqrt(i)
    end

    Profiler.endSample()
end

heavy_logic()
Profiler.stop()
```

---

### 📁 4. 生成日志文件（自动记录到 `/Unity项目路径/LuaProfileLog_xxx.txt`）

内容类似于：

```
Function Name                  | Time(ms) | Calls
-------------------------------------------------
global.heavy_logic            |   2.35   | 1
math.sqrt                     |   1.12   | 100000
```

---

## 🧭 Unity + Lua 项目性能调试流程指南

| 步骤 | 内容 | 工具/方法 |
|------|------|-----------|
| ✅ 1. 开启基础监控 | 在 `Update()` 和 `LuaEnv.DoString()` 前后加 `BeginSample/EndSample` 包裹 | `UnityEngine.Profiler` |
| ✅ 2. 加入 LuaProfiler | 集成开源 LuaProfiler 插件 | [LuaProfiler](https://github.com/LuaProfiler/LuaProfiler) |
| ✅ 3. 插桩关键函数 | 在重要业务逻辑前后加 `Profiler.beginSample()` | Lua 内部函数插桩 |
| ✅ 4. 分析日志 | 观察调用次数多、耗时久的函数 | 自动生成 txt/csv |
| ✅ 5. 结合 Unity Profiler Timeline | 将 C# 和 Lua 脚本关联起来分析 | Unity Profiler 里的“Timeline” |
| ✅ 6. 内存泄漏检测 | 使用 `debug.getregistry()` 枚举所有 Lua 对象并记录未释放对象 | 自研小工具或 `xlua.statistic()` |
| ✅ 7. 热更状态转储（可选） | 使用 `MobDebug`/ZeroBrane 实现远程断点调试 | 或用 Lua 的状态序列化 |
| ✅ 8. 优化方向定位 | 根据分析结果，优化 GC 频率、表结构、函数复用 | 合理拆分协程，避免深栈与循环调用 |

---

## 📎 附加推荐脚本：统计当前 Lua 对象个数（内存泄漏排查）

```lua
-- 统计全局 Lua 表对象数量
local seen = {}
local function count_table(t)
    if type(t) ~= "table" or seen[t] then return 0 end
    seen[t] = true
    local count = 1
    for k, v in pairs(t) do
        count = count + count_table(k)
        count = count + count_table(v)
    end
    return count
end

print("Total Lua Table Objects: ", count_table(_G))
```

---


如你使用的是 `ToLua` 或 `SLua`，也可以帮你适配对应的脚本版本；
需要一个完整工具集成Demo工程我也可以打包给你。如果你还有运行平台限制（如 Android 真机/IOS）、需要自动上传日志、可视化分析工具（如 Excel 生成图表），也可以继续细化～