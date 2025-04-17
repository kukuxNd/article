Title: 高并发C++
Date: 2025-04-18
Category: C&C++

下面给出两个示例：

1. **高并发 IO 服务器（基于 epoll + 线程池）**  
2. **客户端渲染高并发（任务线程池并发处理渲染命令）**  
3. **123457888999
---

## 1. 高并发 IO 服务器（Epoll + C++11 线程池）

```cpp
// server.cpp
#include <sys/epoll.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <unistd.h>
#include <cstring>
#include <iostream>
#include <vector>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <functional>
#include <queue>

// 简单线程池
class ThreadPool {
public:
    ThreadPool(size_t n) : stop(false) {
        for (size_t i = 0; i < n; ++i) {
            workers.emplace_back([this]() {
                for (;;) {
                    std::function<void()> job;
                    {
                        std::unique_lock<std::mutex> lk(mtx);
                        cv.wait(lk, [this]() { return stop || !tasks.empty(); });
                        if (stop && tasks.empty()) return;
                        job = std::move(tasks.front());
                        tasks.pop();
                    }
                    job();
                }
            });
        }
    }
    ~ThreadPool() {
        {
            std::unique_lock<std::mutex> lk(mtx);
            stop = true;
        }
        cv.notify_all();
        for (auto &t : workers) t.join();
    }
    void enqueue(std::function<void()> job) {
        {
            std::unique_lock<std::mutex> lk(mtx);
            tasks.push(std::move(job));
        }
        cv.notify_one();
    }
private:
    std::vector<std::thread> workers;
    std::queue<std::function<void()>> tasks;
    std::mutex mtx;
    std::condition_variable cv;
    bool stop;
};

int setNonBlocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

void handleClient(int sock) {
    char buf[1024];
    ssize_t n = ::recv(sock, buf, sizeof(buf), 0);
    if (n <= 0) {
        ::close(sock);
        return;
    }
    // 简单回显
    ::send(sock, buf, n, 0);
}

int main() {
    const int PORT = 8888;
    int listen_fd = ::socket(AF_INET, SOCK_STREAM, 0);
    setNonBlocking(listen_fd);

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;
    bind(listen_fd, (sockaddr*)&addr, sizeof(addr));
    listen(listen_fd, SOMAXCONN);

    int epfd = epoll_create1(0);
    epoll_event ev{};
    ev.events = EPOLLIN | EPOLLET;
    ev.data.fd = listen_fd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, listen_fd, &ev);

    ThreadPool pool(std::thread::hardware_concurrency());
    const int MAX_EVENTS = 1024;
    std::vector<epoll_event> events(MAX_EVENTS);

    while (true) {
        int n = epoll_wait(epfd, events.data(), MAX_EVENTS, -1);
        for (int i = 0; i < n; ++i) {
            int fd = events[i].data.fd;
            if (fd == listen_fd) {
                // 接受所有新连接
                while (true) {
                    sockaddr_in cli{};
                    socklen_t len = sizeof(cli);
                    int conn = accept(listen_fd, (sockaddr*)&cli, &len);
                    if (conn < 0) break;
                    setNonBlocking(conn);
                    epoll_event cev{EPOLLIN | EPOLLET, conn};
                    epoll_ctl(epfd, EPOLL_CTL_ADD, conn, &cev);
                }
            } else {
                // 异步提交到线程池
                pool.enqueue([fd]() { handleClient(fd); });
            }
        }
    }

    close(epfd);
    close(listen_fd);
    return 0;
}
```

**要点说明：**  
- 非阻塞 socket + epoll 边缘触发（ET）保证单线程复用大量连接。  
- `ThreadPool` 用 C++11 `<thread>`、`<mutex>`、`<condition_variable>` 实现，可并行处理 IO 事件。  
- `handleClient` 中示范了最简单的回显逻辑，生产环境可替换为协议解析／业务处理。

---

## 2. 客户端渲染高并发示例（任务并行化）

```cpp
// client_render.cpp
#include <iostream>
#include <vector>
#include <thread>
#include <future>
#include <chrono>

// 模拟渲染命令
struct RenderCommand {
    int objectId;
    // 其它渲染参数……
};

// 模拟渲染函数
void renderObject(const RenderCommand& cmd) {
    // 假设渲染耗时
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    std::cout << "Rendered object #" << cmd.objectId
              << " on thread " << std::this_thread::get_id() << "\n";
}

// 简易并行执行（用 async）
int main() {
    const int numObjects = 100;
    std::vector<RenderCommand> commands;
    commands.reserve(numObjects);
    for (int i = 0; i < numObjects; ++i)
        commands.push_back({i});

    // 并发提交所有渲染任务
    std::vector<std::future<void>> futures;
    futures.reserve(numObjects);
    for (auto& cmd : commands) {
        futures.emplace_back(
            std::async(std::launch::async, renderObject, cmd)
        );
    }

    // 等待全部完成
    for (auto& f : futures) f.get();

    std::cout << "All rendering complete.\n";
    return 0;
}
```

**要点说明：**  
- 用 `std::async(std::launch::async, ...)` 在后台线程池并行执行渲染命令。  
- 每个渲染任务独立，不同线程并行工作，适用于 CPU 绑定的预处理或场景构建。  
- 生产环境中可用更完善的线程池／任务系统（上例服务器中 ThreadPool 同理可移植）。  

---

> **扩展思路**  
> - 渲染最终仍需回到主线程（或特定渲染线程）提交 GPU Draw Call，可在 `renderObject` 中只做准备工作（计算顶点、生成命令缓冲等），再统一回传主线程。  
> - IO server 与渲染 client 都可复用同一套 C++11 线程池，实现“网络事件驱动 + 并行任务处理”。  

这样，你既可以处理上万并发连接的网络 IO，也可以在客户端用多线程并发准备渲染指令，从而充分利用多核 CPU。