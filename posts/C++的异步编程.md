# C++ 的异步编程案例

Title: C++异步编程
Date: 2025-04-18
Category: C&C++

异步编程是一种提高程序性能和响应速度的重要技术。在 C++ 中，可以使用多种方式实现异步编程，例如 `std::async`、线程池或第三方库（如 Boost.Asio）。以下是一个简单的异步编程案例，展示如何使用 `std::async` 实现异步任务。

## 使用 `std::async` 的异步任务示例

```cpp
#include <iostream>
#include <future>
#include <thread>
#include <chrono>

// 模拟一个耗时任务
int longTask(int seconds) {
    std::this_thread::sleep_for(std::chrono::seconds(seconds));
    return seconds;
}

int main() {
    std::cout << "启动异步任务..." << std::endl;

    // 使用 std::async 启动异步任务
    std::future<int> result = std::async(std::launch::async, longTask, 3);

    std::cout << "主线程继续执行..." << std::endl;

    // 获取异步任务的结果
    int duration = result.get();
    std::cout << "异步任务完成，耗时: " << duration << " 秒" << std::endl;

    return 0;
}
```

## 代码解析

1. **`std::async`**: 用于启动异步任务。`std::launch::async` 指定任务在新线程中运行。
2. **`std::future`**: 用于获取异步任务的结果。
3. **`result.get()`**: 阻塞主线程，直到异步任务完成并返回结果。

## 输出示例

```
启动异步任务...
主线程继续执行...
异步任务完成，耗时: 3 秒
```

通过这种方式，主线程可以在等待异步任务完成的同时继续执行其他操作，从而提高程序的并发性。

## 使用线程池的异步任务示例

线程池是一种高效的异步编程方式，可以避免频繁创建和销毁线程的开销。以下是一个简单的线程池实现及其使用示例：

### 简单线程池实现

```cpp
#include <iostream>
#include <vector>
#include <thread>
#include <queue>
#include <functional>
#include <condition_variable>
#include <future>

class ThreadPool {
public:
    ThreadPool(size_t numThreads) {
        for (size_t i = 0; i < numThreads; ++i) {
            workers.emplace_back([this] {
                while (true) {
                    std::function<void()> task;
                    {
                        std::unique_lock<std::mutex> lock(this->queueMutex);
                        this->condition.wait(lock, [this] {
                            return this->stop || !this->tasks.empty();
                        });
                        if (this->stop && this->tasks.empty()) return;
                        task = std::move(this->tasks.front());
                        this->tasks.pop();
                    }
                    task();
                }
            });
        }
    }

    template <class F, class... Args>
    auto enqueue(F&& f, Args&&... args) -> std::future<typename std::result_of<F(Args...)>::type> {
        using returnType = typename std::result_of<F(Args...)>::type;

        auto task = std::make_shared<std::packaged_task<returnType()>>(
            std::bind(std::forward<F>(f), std::forward<Args>(args)...)
        );

        std::future<returnType> res = task->get_future();
        {
            std::unique_lock<std::mutex> lock(queueMutex);
            if (stop) throw std::runtime_error("enqueue on stopped ThreadPool");
            tasks.emplace([task]() { (*task)(); });
        }
        condition.notify_one();
        return res;
    }

    ~ThreadPool() {
        {
            std::unique_lock<std::mutex> lock(queueMutex);
            stop = true;
        }
        condition.notify_all();
        for (std::thread& worker : workers) worker.join();
    }

private:
    std::vector<std::thread> workers;
    std::queue<std::function<void()>> tasks;
    std::mutex queueMutex;
    std::condition_variable condition;
    bool stop = false;
};
```

### 使用线程池的示例

```cpp
#include <iostream>
#include <chrono>

int longTask(int seconds) {
    std::this_thread::sleep_for(std::chrono::seconds(seconds));
    return seconds;
}

int main() {
    ThreadPool pool(4); // 创建包含 4 个线程的线程池

    std::cout << "提交任务到线程池..." << std::endl;

    auto future1 = pool.enqueue(longTask, 2);
    auto future2 = pool.enqueue(longTask, 3);
    auto future3 = pool.enqueue(longTask, 1);

    std::cout << "主线程继续执行..." << std::endl;

    std::cout << "任务 1 耗时: " << future1.get() << " 秒" << std::endl;
    std::cout << "任务 2 耗时: " << future2.get() << " 秒" << std::endl;
    std::cout << "任务 3 耗时: " << future3.get() << " 秒" << std::endl;

    return 0;
}
```

### 代码解析

1. **线程池类**: `ThreadPool` 管理一组工作线程，并维护一个任务队列。
2. **`enqueue` 方法**: 将任务添加到任务队列，并返回一个 `std::future` 对象以获取任务结果。
3. **任务执行**: 工作线程从任务队列中取出任务并执行。

### 输出示例

```
提交任务到线程池...
主线程继续执行...
任务 1 耗时: 2 秒
任务 2 耗时: 3 秒
任务 3 耗时: 1 秒
```

通过线程池，可以高效地管理多个异步任务，避免频繁创建和销毁线程的开销。