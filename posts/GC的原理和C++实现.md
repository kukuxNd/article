Title: GC的原理和C++实现
Date: 2025-05-20
Category: C&C++
---

高级语言的 GC（Garbage Collection，垃圾回收）是为了解决程序中**内存自动管理**的问题，核心目标是：

> **自动释放不再使用的内存**，防止内存泄漏，提升开发效率，避免程序员手动释放带来的错误。

以下是 GC 的核心原理和典型实现方式：

---

## 🧠 一、GC 的核心思想

GC 的目标是识别哪些对象是\*\*“垃圾”\*\* —— 即：

> **程序中不再被访问、引用的对象**。

只要一个对象**不可达（unreachable）**，就可以回收。

---

## 🔍 二、对象可达性（Reachability）

GC 判定对象是否还能“被用到”，一般通过：

### 1. **引用计数（Reference Counting）**

* 每个对象维护一个“被引用的计数”。
* 当引用+1 或 -1 时更新计数。
* 计数为 0 就可以回收。

✅ 优点：简单，实时回收
❌ 缺点：**无法处理循环引用**

```python
a = {}
b = {}
a["b"] = b
b["a"] = a
```

即使 a 和 b 不再被使用，但彼此引用，引用计数都不是0，无法释放。

---

### 2. **根对象追踪（Tracing GC）**

以一些“根对象”（Root，如栈上的变量、全局变量、线程栈）为起点，通过引用关系，标记所有能访问到的对象。

* **可达**：活对象，不能回收
* **不可达**：垃圾，回收！

---

## 🔄 三、常见 GC 算法

### ✅ 1. **Mark & Sweep（标记-清除）**

**流程：**

1. **标记**：从 Root 出发，遍历所有可达对象，打上“活着”的标记。
2. **清除**：遍历堆内存，清除没有被标记的对象。

优点：能处理循环引用
缺点：碎片化严重、停顿明显

---

### ✅ 2. **Copying（复制 GC）**

将内存分为两块区域（From、To）：

* 活对象从 From 复制到 To，清空 From。
* 下次交换角色。

适用于短命对象多的场景，如 Java 的 **新生代 GC（Young Gen）**

优点：紧凑、没有碎片
缺点：需要双倍内存、长生命周期对象复制成本高

---

### ✅ 3. **Mark & Compact（标记-整理）**

与 Mark & Sweep 类似，但回收时不是直接清除，而是**将活着的对象压缩整理到一边**，形成连续空间，避免碎片。

优点：解决碎片问题
缺点：整理过程比较耗时

---

### ✅ 4. **分代 GC（Generational GC）**

将堆划分为几个代：

* **年轻代（Young）**：对象刚创建，寿命短，采用 **复制算法**。
* **老年代（Old）**：长期存活对象，使用 **标记-清除 或 标记-整理算法**。
* **永久代/元空间（Metaspace）**：类元数据（Java）。

👉 **年轻代回收频率高，老年代回收慢但代价大**

Java、.NET 等语言都采用分代 GC。

---

## ⚙️ 四、主流语言 GC 实现概况

| 语言                  | GC 类型                        | 特点                            |
| ------------------- | ---------------------------- | ----------------------------- |
| **Java**            | 分代、Mark-Sweep-Compact、G1、ZGC | 多种 GC 策略可选，适合服务器              |
| **Python（CPython）** | 引用计数 + 循环垃圾清除                | 引用计数为主                        |
| **Go**              | 三色标记、并发 GC                   | 停顿时间小                         |
| **JavaScript (V8)** | 分代 GC                        | 年轻代 Scavenge，老年代 Mark-Compact |
| **C# (.NET)**       | 分代 GC                        | 有三代，支持并行和并发 GC                |

---

## 🔄 五、并发与增量 GC

为了解决“GC 会导致程序停顿”的问题，引入了：

* **并发 GC（Concurrent GC）**：GC 与程序并行执行，减少卡顿
* **增量 GC（Incremental GC）**：把 GC 拆成小步执行

如：Java 的 G1 GC、ZGC，Go 的并发 GC 都是高级优化。

---

## 💡 总结一句话

> GC 的核心是“可达性分析”，常见算法有 **标记-清除、复制、压缩整理与分代收集**，并发与低延迟是现代 GC 的重点方向。

如果你想，我可以继续展开讲「三色标记法」「写屏障」「对象分配策略」等高级机制。是否继续？

我们可以实现一个**简化版的 GC 收集器**，核心功能如下：

* 管理一批对象
* 用**引用计数 + 手动清理循环引用**的方式
* 用户可以通过 `gc_new<T>()` 创建托管对象，使用 `GCPtr<T>` 智能指针管理引用
* 支持打印出当前内存状态

---

## 🧩 一、代码结构（C++ 实现）

我们会用三个部分来构成简易 GC 系统：

1. `GCObject`：所有托管对象的基类
2. `GCPtr<T>`：引用计数型指针
3. `GC`：垃圾收集器管理器

---

## ✅ 完整代码（简化版 GC 框架 + 示例）

### 🔧 gc.h（头文件）

```cpp
#pragma once
#include <iostream>
#include <unordered_set>
#include <unordered_map>
#include <memory>
#include <type_traits>

class GCObject;

class GC {
public:
    static GC& instance();

    void registerObject(GCObject* obj);
    void collect();

    void printStats();

private:
    std::unordered_set<GCObject*> objects;
};

class GCObject {
public:
    GCObject() : refCount(0) {
        GC::instance().registerObject(this);
    }

    virtual ~GCObject() {}

    void retain() { ++refCount; }
    void release() {
        if (--refCount == 0)
            delete this;
    }

    int getRefCount() const { return refCount; }

private:
    int refCount;
};

template<typename T>
class GCPtr {
    static_assert(std::is_base_of<GCObject, T>::value, "GCPtr only works with GCObject");

public:
    GCPtr() : ptr(nullptr) {}
    GCPtr(T* p) : ptr(p) {
        if (ptr) ptr->retain();
    }

    GCPtr(const GCPtr& other) : ptr(other.ptr) {
        if (ptr) ptr->retain();
    }

    GCPtr& operator=(const GCPtr& other) {
        if (ptr != other.ptr) {
            if (ptr) ptr->release();
            ptr = other.ptr;
            if (ptr) ptr->retain();
        }
        return *this;
    }

    ~GCPtr() {
        if (ptr) ptr->release();
    }

    T* operator->() { return ptr; }
    T& operator*() { return *ptr; }
    T* get() const { return ptr; }
    operator bool() const { return ptr != nullptr; }

private:
    T* ptr;
};

template<typename T, typename... Args>
GCPtr<T> gc_new(Args&&... args) {
    return GCPtr<T>(new T(std::forward<Args>(args)...));
}
```

---

### 🔧 gc.cpp（实现文件）

```cpp
#include "gc.h"

GC& GC::instance() {
    static GC gc;
    return gc;
}

void GC::registerObject(GCObject* obj) {
    objects.insert(obj);
}

void GC::collect() {
    // 暂不处理循环引用，打印仍存活对象
    std::cout << "[GC] Collecting...\n";
    for (auto* obj : objects) {
        if (obj->getRefCount() > 0) {
            std::cout << " - Object @" << obj << " still alive. RefCount: " << obj->getRefCount() << "\n";
        }
    }
}

void GC::printStats() {
    std::cout << "[GC] Total objects managed: " << objects.size() << "\n";
}
```

---

### 🧪 main.cpp（使用示例）

```cpp
#include "gc.h"

class Node : public GCObject {
public:
    Node(int v) : value(v) {
        std::cout << "Node " << value << " constructed\n";
    }

    ~Node() {
        std::cout << "Node " << value << " destroyed\n";
    }

    void setNext(const GCPtr<Node>& n) {
        next = n;
    }

    void print() {
        std::cout << "Node(" << value << ") ";
        if (next) std::cout << "-> Node(" << next->value << ")";
        std::cout << "\n";
    }

    int value;
    GCPtr<Node> next;
};

int main() {
    {
        GCPtr<Node> a = gc_new<Node>(1);
        GCPtr<Node> b = gc_new<Node>(2);

        a->setNext(b);
        b->setNext(a); // 创建循环引用！

        a->print();
        b->print();

        // 手动打断循环
        b->setNext(nullptr);
    }

    GC::instance().collect();

    return 0;
}
```

---

## ✅ 输出示例

```
Node 1 constructed
Node 2 constructed
Node(1) -> Node(2)
Node(2) -> Node(1)
Node 1 destroyed
Node 2 destroyed
[GC] Collecting...
```

---

## 📌 小结

| 部件         | 功能                       |
| ---------- | ------------------------ |
| `GCObject` | 所有托管对象基类，带引用计数           |
| `GCPtr<T>` | 类似智能指针，自动 retain/release |
| `GC`       | 注册对象 + 收集器接口             |
| 示例         | 展示引用计数 + 循环引用问题          |

---

## 🔧 可扩展方向

* 增加**可达性分析**（根对象追踪）
* 支持**周期性清理机制**
* 用图结构检测**强引用环**
* 多线程安全（加锁）
* 或改用 Boehm GC 集成真实 GC 引擎

---

好的！下面是一个 **简化版 C++ 三色标记 GC 模拟器**，演示三色状态流转、引用关系、GC 收集过程，**可追踪对象状态变化**。

---

## 🧠 实现目标

* 支持三色标记（白、灰、黑）
* 用图结构表示对象和引用
* 模拟 GC 扫描流程（mark、scan、collect）
* 可打印每个对象的状态
* 模拟写屏障（只做演示，不实现并发）

---

## ✅ 完整代码（单文件版，直接可跑）

```cpp
#include <iostream>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <memory>
#include <queue>
#include <string>

// 三色枚举
enum class Color {
    White,
    Gray,
    Black
};

// 模拟的 GC 对象
struct Object {
    std::string name;
    Color color = Color::White;
    std::vector<Object*> references;

    Object(const std::string& n) : name(n) {}
};

// GC 管理器
class TricolorGC {
public:
    void addObject(Object* obj) {
        objects.insert(obj);
    }

    void addRoot(Object* obj) {
        roots.insert(obj);
    }

    void runGC() {
        // 1. 初始化阶段：所有对象为白
        for (auto* obj : objects) {
            obj->color = Color::White;
        }

        // 2. 根对象染灰
        std::queue<Object*> grayQueue;
        for (auto* root : roots) {
            root->color = Color::Gray;
            grayQueue.push(root);
        }

        // 3. 灰对象扫描过程
        while (!grayQueue.empty()) {
            Object* current = grayQueue.front();
            grayQueue.pop();

            for (auto* ref : current->references) {
                if (ref->color == Color::White) {
                    ref->color = Color::Gray;
                    grayQueue.push(ref);
                }
            }
            current->color = Color::Black;
        }

        // 4. 回收所有白对象
        std::cout << "\n[GC] Collected objects:\n";
        for (auto it = objects.begin(); it != objects.end();) {
            if ((*it)->color == Color::White) {
                std::cout << " - " << (*it)->name << "\n";
                delete *it;
                it = objects.erase(it);
            } else {
                ++it;
            }
        }

        std::cout << "\n[GC] Remaining objects:\n";
        for (auto* obj : objects) {
            std::cout << " - " << obj->name << " (Color: " << colorToString(obj->color) << ")\n";
        }
    }

private:
    std::unordered_set<Object*> objects;
    std::unordered_set<Object*> roots;

    std::string colorToString(Color c) {
        switch (c) {
            case Color::White: return "White";
            case Color::Gray: return "Gray";
            case Color::Black: return "Black";
        }
        return "?";
    }
};
```

---

## 🧪 示例代码（main）

```cpp
int main() {
    TricolorGC gc;

    // 创建对象
    Object* A = new Object("A");
    Object* B = new Object("B");
    Object* C = new Object("C");
    Object* D = new Object("D");

    // 引用关系
    A->references.push_back(B);
    B->references.push_back(C);
    C->references.push_back(D);

    // 模拟 root 引用
    gc.addObject(A);
    gc.addObject(B);
    gc.addObject(C);
    gc.addObject(D);
    gc.addRoot(A); // Only A is root

    std::cout << "[Before GC] Objects created and connected:\n";
    std::cout << "A -> B -> C -> D\n";

    gc.runGC(); // 模拟一次 GC

    return 0;
}
```

---

## 🧾 输出示例：

```
[Before GC] Objects created and connected:
A -> B -> C -> D

[GC] Collected objects:

[GC] Remaining objects:
 - A (Color: Black)
 - B (Color: Black)
 - C (Color: Black)
 - D (Color: Black)
```

---

## 🧪 模拟丢失引用情况（模拟对象 D 不可达）

你可以注释掉：

```cpp
C->references.push_back(D);
```

再运行，输出：

```
[GC] Collected objects:
 - D

[GC] Remaining objects:
 - A (Color: Black)
 - B (Color: Black)
 - C (Color: Black)
```

---

## ✅ 可选拓展

你可以继续扩展这个模拟器：

* 模拟**写屏障**机制（检测黑指向白）
* 添加**增量 GC 调度器**
* 支持**引用断开、动态场景**
* 可视化（输出 DOT 图）
* 多代 GC 模拟（新生代/老年代）

---