Title: UE中的任务Task方法集合
Date: 2025-04-28
Category: UE4&5

以下测试案例展示并验证了 UE 新任务（Tasks）API 的多种用法，主要可分为以下几个方面：

1. **基础任务调度与等待**  
   - `Launch(...).Wait()`：启动并立即等待任务完成  
   - `Launch(...)` (fire‑and‑forget)：不保留引用的“发射后忘记”任务  
   - `Wait(Tasks)`：批量等待一组任务完成  
   - `FPlatformProcess::Yield()`、`Sleep()` 用于轮询或阻塞等待  

2. **事件同步 (`FTaskEvent`)**  
   - `FTaskEvent Event;` + `Event.Trigger()` + `Event.Wait()`：手动触发/等待  
   - 多次触发同一事件、零超时等待验证  
   - 任务内等待 (busy‑waiting) 和外部触发两种同步方式  

3. **先决条件（Prerequisites）**  
   - `Launch(..., Prerequisites(task1, task2))`：在先决任务/事件完成后再执行  
   - 接受空任务、容器（`TArray<FTask>`）、`TArrayView<FTask>` 等多种形式  

4. **带返回值的任务 (`TTask<T>`)**  
   - `TTask<int>`、`TTask<FMyStruct>`：支持值和引用类型返回  
   - `GetResult()`：阻塞并取回任务结果  
   - 延后执行 vs. 延后等待，两种典型用法  

5. **可移动类型支持**  
   - 对不可拷贝、仅可移动类型（`FMoveConstructable`）的构造/析构次数进行了验证，确保只生成一次结果实例  

6. **可变 Lambda 和捕获**  
   - `[]() mutable { … }`：验证 mutable lambda 调用及返回值动作  

7. **释放任务占用**  
   - 通过 `Task = {}` 重置任务实例，释放内部资源  

8. **任务内部引用自身**  
   - 在任务体内捕获并访问自身 `FTask Task; Task.Launch(..., [&Task]{ … });`  

9. **嵌套任务 (Nested Tasks)**  
   - `AddNested(...)`：在父任务中添加子任务依赖  
   - 多层嵌套、先触发信号再完成父任务、方形嵌套等复杂场景  

10. **管道任务 (`FPipe`)**  
    - 顺序且隔离地在同一管道上执行任务  
    - 阻塞/解除管道、内联任务（`EExtendedTaskPriority::Inline`）、`WaitUntilEmpty()` 等  

11. **线程安全异步 “Actor” 样例**  
    - 在类成员中持有 `FPipe`，展示跨线程安全调用接口  

12. **等待任一任务**  
    - `WaitAny(Tasks, timeout)`：超时前无任务完成返回 `INDEX_NONE`  
    - `Any(Tasks).Wait()`：只要有一个任务完成即可返回  

13. **取消支持 (`FCancellationToken`)**  
    - 在任务体内检测 `IsCanceled()`，全局/多任务共享取消请求  

14. **并发限制 (`FTaskConcurrencyLimiter`)**  
    - `Push(..., SlotCallback)`：推送受限并发任务，确保不超过最大并发数  
    - `Wait()`：等待所有受限任务完成  
    - 压力测试验证槽位互斥、实际并发数、处理总量  

15. **线程本地存储压力测试**  
    - `FPlatformTLS::AllocTlsSlot()` vs. C++11 `thread_local`，对比性能  

16. **性能基准 (`UE_BENCHMARK`)**  
    - 对各种典型模式（批量调度、延迟、工作窃取、深度回撤等）进行多轮基准测试  

17. **深度回撤 (Retraction) 场景**  
    - 在所有工作线程阻塞情况下，验证父任务及其嵌套任务依然可被“拉回”执行  
    - 两级先决条件 + 双层嵌套测试  

18. **“待机”工作线程测试**  
    - 在单工作线程下测试过量订阅（oversubscription）行为，确保不会死锁  

---

以上即该文件中所有测试案例所覆盖的主要用法和验证场景。

这个测试和底层的 Tasks API 并不是真正意义上的「协程」（coroutine）——它是一套基于线程池、任务调度和事件同步的并发框架，而不是 C++20 那种用 `co_await`/`co_yield` 实现的语言级协程。具体来说：

- **任务（Task）不是协程**  
  每次 `Launch(...)` 都是在后台线程池里调度一个函数去跑，函数体里如果需要等待其它任务或事件，都是通过 `FTaskEvent::Wait()`（阻塞当前线程）或者轮询 `IsCompleted()` + `Yield()` 来实现的，并不会把函数「挂起」然后在同一个线程里恢复。

- **没有 `co_await`/`co_yield` 语法**  
  整个接口并没有提供语言级的挂起点（suspend point）或恢复点，也不存在对 C++20 协程的封装类型。你调用 `Task.GetResult()`、`Task.Wait()`，本质上就是同步地阻塞当前线程，直到结果就绪。

- **“内联”任务（Inline Priority）≠ 协程**  
  `EExtendedTaskPriority::Inline` 只是告诉调度器：如果当前线程空闲，就马上在同一个线程调用这个任务体；它也不会把调用点挂起，而是纯粹地同步执行。

- **“嵌套任务”（Nested Tasks）也不是协程**  
  `AddNested(...)` 只是把子任务注册为父任务完成前必须等待的先决条件，还是一套基于事件/依赖的调度模型。

如果你需要真正的协程支持（非阻塞地挂起并在稍后恢复执行上下文），目前在 UE 的 C++ API 里要么自己用 C++20 协程写，要么依赖 Unreal 针对 Blueprint 的“延迟事务”（Latent Actions）机制，或者用第三方库（如 cppcoro）。Tasks API 本身并不提供语言级协程。

Unity 的协程（Coroutine）并不是基于多线程的，而是建立在 C# 语言的迭代器（`IEnumerator`）之上，由 Unity 引擎在主线程的每一帧中轮询执行。其核心原理可以分为以下几个部分：

---

## 1. 编译器生成的状态机

- 当你在 C# 中写一个返回 `IEnumerator` 的方法，并在方法体中使用 `yield return` 时，C# 编译器会自动将它改写成一个**状态机类**（state machine）。  
- 这个类实现了 `IEnumerator` 接口，并在内部维护一个“当前状态”字段，每次调用 `MoveNext()` 就会推进到下一个 `yield` 点。  

```csharp
// 伪代码示意
private class MyCoroutineStateMachine : IEnumerator
{
    private int _state;
    public object Current { get; private set; }

    public bool MoveNext()
    {
        switch (_state)
        {
            case 0:
                // 第一次进入
                _state = 1;
                Current = null;    // 对应 yield return null;
                return true;
            case 1:
                // 第二次进入
                _state = 2;
                Current = new WaitForSeconds(1f);
                return true;
            case 2:
                // 结束
                return false;
        }
        return false;
    }
    public void Reset() { /*…*/ }
    public void Dispose() { /*…*/ }
}
```

---

## 2. 启动与调度

1. **StartCoroutine**  
   ```csharp
   StartCoroutine(MyCoroutine());
   ```
   - Unity 会在内部把生成的 `IEnumerator` 对象存到一个“待调度协程列表”里，并关联到该 `MonoBehaviour`。  
   - 并不会创建新的线程，而是注册到引擎的**主循环**（Main Loop）中。

2. **每帧推进**  
   - 在每一帧开始或结束（取决于协程类型），Unity 会遍历所有活跃的协程列表，对每个 `IEnumerator` 调用 `MoveNext()`。  
   - 如果 `MoveNext()` 返回 `false`，说明协程结束，Unity 会把它从列表中移除。

---

## 3. Yield 指令的执行时机

协程里 `yield return` 后面的对象决定下一次执行的时机：

| Yield 对象                            | 语义                                          | 何时再次调用 MoveNext()            |
|---------------------------------------|-----------------------------------------------|------------------------------------|
| `null`                                | 下一帧（相当于等待一个 Update）               | 下一帧开始                          |
| `WaitForEndOfFrame`                   | 本帧渲染结束后                              | 在渲染完成、GUI 绘制之后             |
| `WaitForFixedUpdate`                  | 下一次固定帧（FixedUpdate）                  | 下一个 FixedUpdate 调用前           |
| `new WaitForSeconds(t)`               | 延迟 t 秒后                                  | 系统内部记录剩余时间，到期时推进     |
| `WWW`/`UnityWebRequest` 等异步操作    | 网络请求完成后                              | 请求返回时推进                      |
| 自定义 `CustomYieldInstruction` 或 `IEnumerator` | 由你自己在 `keepWaiting` 中控制            | 每帧检查 `keepWaiting` 是否为 `false` |

---

## 4. 内部机制要点

- **时间管理**  
  Unity 在主循环里维护一个“协程调度器”（Coroutine Scheduler），它会跟踪每个协程当前挂起的“等待指令”，并在条件满足后恢复执行。  
- **单线程安全**  
  所有协程都运行在主线程上，不会并行执行，因此访问 Unity API（绝大多数只能在主线程调用）是安全的。  
- **停止与清理**  
  - `StopCoroutine(handle)`、`StopAllCoroutines()` 可以提前结束协程；  
  - `IEnumerator` 对象的 `Dispose()` 会在结束后被调用，用于清理资源（大多数情况下空实现）。

---

## 5. 优势与局限

**优势**  
- 语法简洁：用 `yield return` 写异步逻辑比回调或状态机更直观。  
- 与引擎渲染/物理循环天然集成：可以灵活地按帧、固定帧或时长来挂起。

**局限**  
- 只能在主线程执行，无法利用多核并行。  
- `yield return` 之外的阻塞（如 `Thread.Sleep`）仍会卡住主线程。  
- 调试时不易看出内部状态机的执行路径。

---

### 小结

Unity 的协程是一种**基于编译器生成的迭代器状态机**，配合引擎主循环中的**协程调度器**，按每帧或自定义时机推进执行，而不是语言级的、真正抢占式或多线程协程。它用起来简单灵活，但本质上仍是单线程的“伪异步”。