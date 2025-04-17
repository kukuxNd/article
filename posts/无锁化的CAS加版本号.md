Title: 无锁化的原子操作CAS加版本号示例
Date: 2025-04-18
Category: C&C++

# 无锁化的 CAS 加版本号示例

在多线程编程中，CAS（Compare-And-Swap）是一种常用的无锁化操作。为了避免 ABA 问题，可以引入版本号机制。以下是一个使用 C++ 实现的示例代码：

```cpp
#include <atomic>
#include <iostream>
#include <thread>

struct Node {
    int value;
    int version;
};

std::atomic<Node> shared_node;

void updateValue(int newValue) {
    Node oldNode = shared_node.load();
    Node newNode;

    do {
        newNode.value = newValue;
        newNode.version = oldNode.version + 1;
    } while (!shared_node.compare_exchange_weak(oldNode, newNode));
}

int main() {
    shared_node.store({0, 0});

    std::thread t1(updateValue, 42);
    std::thread t2(updateValue, 84);

    t1.join();
    t2.join();

    Node finalNode = shared_node.load();
    std::cout << "Final Value: " << finalNode.value << ", Version: " << finalNode.version << std::endl;

    return 0;
}
```

## 代码说明

1. **Node 结构体**：包含 `value` 和 `version` 两个字段，用于存储值和版本号。
2. **CAS 操作**：通过 `compare_exchange_weak` 实现无锁化更新，同时更新版本号。
3. **避免 ABA 问题**：版本号的递增确保了即使值相同，版本号的变化也能检测到状态的改变。

## 注意事项

- `compare_exchange_weak` 在某些情况下可能会失败，需要在循环中重试。
- 版本号可能会溢出，实际应用中需要根据具体场景处理。

通过这种方式，可以有效避免 ABA 问题，同时实现无锁化的安全更新。
```