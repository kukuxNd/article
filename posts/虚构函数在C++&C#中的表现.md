Title: 虚构函数在C++&C#中的表现
Date: 2014-06-18
Category: UE45&Unity

好问题！这背后的原因跟 **虚函数表（vtable）机制** 和 **C++ 的析构顺序规范** 有关。我们一起来拆开讲清楚。

---

## 🎯 为什么虚析构函数能先调 `~sub()` 再调 `~base()`？

### 1️⃣ 析构函数的调用顺序规定（这是语言规范）：
- **C++ 标准规定：派生类对象销毁时，析构顺序是：**
  - **先执行派生类析构函数 `~sub()`**
  - **再执行基类析构函数 `~base()`**

这个顺序的目的是：
> 子类可能拥有自己的资源（比如 new 出来的对象），需要先释放；
> 然后再释放公共基类拥有的资源。

---

### 2️⃣ 关键点：**你是通过 `base*` 指针在 delete 对象**

```cpp
base* p = new sub();
delete p;  // 这里调用的是哪个析构函数？
```

- 如果 `~base()` **不是虚函数**：  
  C++ 编译器只知道这是个 `base` 类型的指针，它只会静态地调用 `~base()`，根本不会去查 `~sub()`。

- 如果 `~base()` 是 **虚函数**：  
  编译器会通过 `vtable` 来动态决定要调用的是 `~sub()`（即派生类的析构）。

---

### 3️⃣ vtable 是怎么帮助做到这一点的？

每个带虚函数的类都有一张“虚函数表（vtable）”，  
当你 new 一个 `sub` 对象时，它的 vtable 指向的是 `sub` 的版本，里面的 `~base()` 指针会被 override 成 `~sub()`。

于是 delete 时：

```cpp
// 假设你写了 virtual ~base()，delete 会这样做：
base* p = new sub();  // 实际上是 sub 对象
delete p;  // 会去 vtable 查 ~sub()，再隐式链到 ~base()
```

流程如下：

1. 查找 vtable → 找到 `~sub()`
2. 调用 `~sub()` → 派生类资源释放
3. 然后自动调用 `~base()` → 基类资源释放

---

## 🔥 不加 virtual 的后果？

```cpp
class base {
public:
    ~base() { std::cout << "~ base\n"; }
};

class sub : public base {
public:
    ~sub() { std::cout << "~ sub\n"; }
};

base* p = new sub();
delete p;  // 输出？
```

输出：

```
~ base
```

**Oops！`~sub()` 完全没调用。**  
如果 `~sub()` 里面释放了资源（比如 delete 一个指针），就泄漏了。

---

## ✅ 总结

| 是否加 `virtual` | delete 时是否调到 `~sub()` | 安全性 | 推荐 |
|------------------|----------------------------|--------|------|
| ❌ 非虚析构函数   | ❌ 不调，可能内存泄漏       | ❌ 不安全 | ❌ |
| ✅ 虚析构函数     | ✅ 先调 `~sub()` 再调 `~base()` | ✅ 安全释放 | ✅ |

---

好嘞！我们来搞一个 **C# 小 demo**，演示：

1. ✅ 析构函数 `~ClassName()`（Finalizer）是如何被调用的（但时间不确定）  
2. ✅ 如何用 `IDisposable` + `Dispose()` 来 **手动控制资源释放**，模拟 C++ 析构行为  
3. ✅ `GC.Collect()` 可以“强行召唤”垃圾回收（但不推荐在线程逻辑中依赖）

---

## 💡 代码示例：C# 析构 vs Dispose

```csharp
using System;

class Finalizable : IDisposable {
    private string name;

    public Finalizable(string name) {
        this.name = name;
        Console.WriteLine($"{name} 构造完成");
    }

    // 析构函数（GC调用时触发）
    ~Finalizable() {
        Console.WriteLine($"{name} 的析构函数（Finalizer）被 GC 调用了");
    }

    // 显式释放资源
    public void Dispose() {
        Console.WriteLine($"{name} 显式 Dispose() 被调用");
        GC.SuppressFinalize(this); // 告诉 GC：这个对象我自己处理了，不用再调 finalizer
    }
}

class Program {
    static void Main() {
        Console.WriteLine("🔸 进入 Main 方法");

        // 用 using 结构，自动调用 Dispose
        using (var obj1 = new Finalizable("对象1")) {
            Console.WriteLine("🧪 使用 对象1 中...");
        }

        // 手动 new，但不 Dispose
        var obj2 = new Finalizable("对象2");

        Console.WriteLine("🔸 手动 new 的对象2，不调用 Dispose，等待 GC");

        // 强行触发 GC
        GC.Collect();
        GC.WaitForPendingFinalizers();

        Console.WriteLine("🔸 Main 方法结束");
    }
}
```

---

## 🧪 输出可能是（顺序略有变化）：

```
🔸 进入 Main 方法
对象1 构造完成
🧪 使用 对象1 中...
对象1 显式 Dispose() 被调用
对象2 构造完成
🔸 手动 new 的对象2，不调用 Dispose，等待 GC
对象2 的析构函数（Finalizer）被 GC 调用了
🔸 Main 方法结束
```

---

## 🔍 观察要点：

| 行为                       | 表现                           |
|----------------------------|--------------------------------|
| using 块结束后自动调用 Dispose | ✅ 手动释放资源                  |
| 析构函数什么时候触发        | ❓ 取决于 GC，不可预测，除非手动 `Collect()` |
| `GC.SuppressFinalize(this)` | 🧹 避免多次清理                 |

---

## 🧠 小结 & 建议

| 如果你想要...                         | 推荐做法                    |
|----------------------------------------|-----------------------------|
| 像 C++ 那样确定释放资源              | 实现 `IDisposable` + `using`|
| 想了解 GC 的 finalizer 执行机制     | 写 `~ClassName()` 看 GC 调用 |
| 想手动释放资源并避免 GC 管这事        | 用 `Dispose()` + `SuppressFinalize()` |

---
好问题！你的提问非常“边界测试精神”——这种场景在真实项目里确实容易踩坑。

---

## 🎯 简短回答：

❌ **不可以**。  
一旦你调用了 `reader.Dispose()`，再调用 `reader.ReadToEnd()` 等方法，**将抛出异常**：

```csharp
System.ObjectDisposedException: Cannot access a closed StreamReader.
```

---

## 💥 举个实际例子：

```csharp
StreamReader reader = new StreamReader("example.txt");
reader.Dispose();  // 显式释放

// ❗再调用 ReadToEnd 会报错
string content = reader.ReadToEnd();  // Boom!
```

### 输出错误：

```
Unhandled exception. System.ObjectDisposedException: Cannot access a closed StreamReader.
```

---

## 🧠 为什么会这样？

因为：

1. `Dispose()` 会将内部 `Stream` 置为 null 或关闭状态
2. `StreamReader` 每次读数据都会检查内部流是否有效
3. 一旦发现是已释放的状态，就直接抛出 `ObjectDisposedException`

这是一种“保护机制”，**防止你对已经被清理的资源做无效操作**，否则会导致更严重的问题（比如内存泄漏、死锁、数据破坏等）

---

## ✅ 正确用法总结

| 操作                   | 是否安全 | 说明                           |
|------------------------|----------|--------------------------------|
| `ReadToEnd()` 正常使用 | ✅       | 前提是还没 Dispose             |
| Dispose 后再读         | ❌       | 报错 `ObjectDisposedException` |
| 多次 Dispose()         | ✅       | 多次 Dispose 不会报错，是幂等操作 |

---

## ✨ Bonus：如何优雅判断是否已 Dispose？

标准类如 `StreamReader` **没有公开提供 `IsDisposed`** 标志。  
如果你写的是自己的类，可以这样做：

```csharp
private bool _disposed = false;

public void Dispose() {
    if (!_disposed) {
        // 释放资源
        _disposed = true;
    }
}
```

---

## 总结口播版🗣️：

> `Dispose()` 就像你把书合上、灯关了、门锁上了。
> 再想读？对不起，灯黑了，门锁了，系统直接扔你一个 `ObjectDisposedException` —— **别回头看，赶紧另起炉灶！**

---

绝妙的问题！这一问直击 C# 和 Unity 开发的**语言边界行为**！

---

## 🎯 答案简洁版：

❌ **不能用**。  
如果一个类型**没有实现 `IDisposable` 接口**，你 **不能用 `using` 语法**，编译器会直接报错。

---

## 📌 编译器会报什么错？

如果你写了：

```csharp
class MyClass {
    // 没有实现 IDisposable
}

void Start() {
    using (var obj = new MyClass()) {
        // ...
    }
}
```

你会得到如下编译错误（以 Unity 和 VS 为例）：

```
error CS1674: 'MyClass': type used in a using statement must be implicitly convertible to 'System.IDisposable'
```

---

## 🔍 为什么会这样？

`using` 是 C# 的语法糖，等效于：

```csharp
{
    MyClass obj = new MyClass();
    try {
        // ...
    }
    finally {
        if (obj != null)
            ((IDisposable)obj).Dispose();
    }
}
```

所以你必须实现 `IDisposable`，否则它**不知道去哪儿找 `.Dispose()` 方法来释放资源**。

---

## ✅ 正确用法模板：

```csharp
class MyDisposable : IDisposable {
    public void Dispose() {
        Console.WriteLine("资源被释放了");
    }
}

void Start() {
    using (var obj = new MyDisposable()) {
        // 自动释放
    }
}
```

---

## 🧠 Unity 中的特例：一些 UnityEngine 类型虽然有 `.Dispose()`，但不能用 `using`！

比如 `RenderTexture.Release()`、`Texture.Destroy()`：

```csharp
RenderTexture rt = new RenderTexture(...);
rt.Release();  // 不是 IDisposable，所以不能用 using
```

这类对象不实现 `IDisposable`，你只能手动管理。

---
