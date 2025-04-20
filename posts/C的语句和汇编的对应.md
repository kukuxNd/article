Title: C语句和汇编的对应
Date: 2024-09-18
Category: C&C++

我们来系统地梳理 **C 语言的基本语法、变量类型及赋值方式**，并通过简单示例，**列出对应的汇编指令（以 x86-64 AT&T 语法为例）**，帮助你理解从 C 到汇编的底层对应关系。

---

## 🧱 一、C 语言基本语法结构

| 语法分类 | 示例 | 说明 |
|----------|------|------|
| 变量声明 | `int a;` | 声明一个整型变量 |
| 赋值 | `a = 10;` | 给变量赋值 |
| 表达式 | `b = a + 3;` | 表达式求值并赋值 |
| 条件语句 | `if (a > 5) {...}` | 分支 |
| 循环语句 | `while (a < 100) {...}` | 循环 |
| 函数定义 | `int sum(int x, int y)` | 定义函数 |
| 数组 | `int arr[5];` | 定义数组 |
| 指针 | `int *p = &a;` | 使用地址和指针 |
| 结构体 | `struct S { int a; float b; };` | 用户自定义类型 |

---

## 📌 二、基本类型与赋值（带汇编对照）

### 1️⃣ 整型（`int`）

```c
int a = 10;
```

**对应汇编（x86-64 AT&T）：**
```asm
movl $10, -4(%rbp)   # 假设 a 在栈帧中偏移 -4
```

---

### 2️⃣ 字符型（`char`）

```c
char c = 'A';
```

**汇编：**
```asm
movb $65, -1(%rbp)   # 'A' 的 ASCII 是 65
```

---

### 3️⃣ 短整型（`short`）

```c
short s = 300;
```

**汇编：**
```asm
movw $300, -2(%rbp)
```

---

### 4️⃣ 长整型（`long`）

```c
long l = 123456789L;
```

**汇编：**
```asm
movq $123456789, -8(%rbp)
```

---

### 5️⃣ 浮点型（`float`）

```c
float f = 3.14f;
```

**汇编（需用 SSE）：**
```asm
movss .LC0(%rip), %xmm0  # .LC0 是常量池中3.14的位置
movss %xmm0, -4(%rbp)
```

---

### 6️⃣ 双精度（`double`）

```c
double d = 6.28;
```

**汇编：**
```asm
movsd .LC1(%rip), %xmm0
movsd %xmm0, -8(%rbp)
```

---

### 7️⃣ 字符串赋值（`char*`）

```c
char* str = "Hello";
```

**汇编：**
```asm
movq $.LC2, -8(%rbp)    # .LC2 是字符串常量 "Hello" 的地址
```

---

## ⚙️ 三、常见赋值表达式和汇编

### 📌 `a = b + c;`

```c
int a, b = 3, c = 4;
a = b + c;
```

**汇编：**
```asm
movl -8(%rbp), %eax    # b
addl -12(%rbp), %eax   # c
movl %eax, -4(%rbp)    # a
```

---

### 📌 `a++;` 和 `++a;`

```c
int a = 5;
a++;
```

**汇编：**
```asm
addl $1, -4(%rbp)
```

```c
++a;
```

**同上，汇编不区分前后缀增量在底层实现**

---

### 📌 指针赋值与解引用

```c
int a = 10;
int *p = &a;
*p = 20;
```

**汇编：**
```asm
movl $10, -4(%rbp)         # a = 10
leaq -4(%rbp), %rax        # p = &a
movq %rax, -16(%rbp)
movl $20, (%rax)           # *p = 20
```

---

## 🧠 四、类型大小（x86-64）

| 类型 | 大小 (字节) |
|------|--------------|
| `char` | 1 |
| `short` | 2 |
| `int` | 4 |
| `long` | 8 |
| `float` | 4 |
| `double` | 8 |
| `pointer` | 8 |

---

## 📜 五、常见汇编指令简析（AT&T）

| 指令 | 含义 |
|------|------|
| `movl/movq/movb` | 数据移动 |
| `addl/addq` | 加法 |
| `subl/subq` | 减法 |
| `imul` | 乘法 |
| `idiv` | 除法 |
| `leaq` | 获取地址 |
| `cmp` | 比较（用于条件跳转） |
| `jmp/jne/je` | 无条件/条件跳转 |
| `call/ret` | 函数调用与返回 |

---
太好了！下面我们将通过 **3 个完整的 C 函数** 示例，展示：

1. 函数参数传递  
2. 局部变量分配  
3. 运算与返回值处理  
4. 对应的 **x86-64 AT&T 汇编指令**（带注释）

---

## ✅ 示例 1：简单加法函数

```c
int add(int a, int b) {
    int result = a + b;
    return result;
}
```

### 汇编代码（x86-64 AT&T 语法）：
```asm
add:
    pushq %rbp                # 保存上一个栈帧指针
    movq %rsp, %rbp           # 设置当前栈帧

    movl %edi, -4(%rbp)       # a 存入栈帧的 -4
    movl %esi, -8(%rbp)       # b 存入栈帧的 -8

    movl -4(%rbp), %eax       # eax = a
    addl -8(%rbp), %eax       # eax += b

    popq %rbp                 # 恢复栈帧
    ret                       # 返回 eax（函数返回值）
```

> 💡 函数参数 `a` 和 `b` 分别通过 `edi`、`esi` 传入。

---

## ✅ 示例 2：带局部变量、乘法和返回值

```c
int mul_add(int x, int y) {
    int product = x * y;
    int sum = product + x;
    return sum;
}
```

### 汇编代码：
```asm
mul_add:
    pushq %rbp
    movq %rsp, %rbp

    movl %edi, -4(%rbp)       # x
    movl %esi, -8(%rbp)       # y

    movl -4(%rbp), %eax       # eax = x
    imull -8(%rbp), %eax      # eax *= y
    movl %eax, -12(%rbp)      # product = eax

    movl -12(%rbp), %eax      # eax = product
    addl -4(%rbp), %eax       # eax += x

    popq %rbp
    ret
```

> 🧠 `imull` 表示有符号整数乘法，结果存在 `eax` 中。

---

## ✅ 示例 3：使用指针操作内存

```c
void set_value(int *p, int v) {
    *p = v;
}
```

### 汇编代码：
```asm
set_value:
    pushq %rbp
    movq %rsp, %rbp

    movq %rdi, -8(%rbp)       # p
    movl %esi, -12(%rbp)      # v

    movq -8(%rbp), %rax       # rax = p
    movl -12(%rbp), %edx      # edx = v
    movl %edx, (%rax)         # *p = v

    popq %rbp
    ret
```

> 🔍 `rdi` 和 `esi` 是前两个参数，`*p = v` 实际等价于 `movl` 到 `[p]` 指向的内存。

---

## 🚀 延伸：函数返回类型与寄存器

| 返回类型 | 寄存器 | 说明 |
|----------|--------|------|
| `int` / `char` / `short` | `eax` | 整数返回值 |
| `float` | `xmm0` | 单精度返回 |
| `double` | `xmm0` | 双精度返回 |
| `long` / `pointer` | `rax` | 64位整型或地址 |

---

## 🔍 提示：GCC 生成汇编查看命令

你可以使用如下命令直接将 `.c` 文件转为汇编代码：

```bash
gcc -S -masm=att -O0 demo.c -o demo.s
```

- `-S`：只编译生成汇编
- `-masm=att`：指定使用 AT&T 汇编语法
- `-O0`：关闭优化，便于学习

---
太好了，咱们来一波硬核进阶版，把 C 中的高级语法一一拿出来对应汇编（x86-64, AT&T 语法），每个例子都是实战中非常常见的模式，并配详细注释说明。

---

## ✅ 1. 函数调用（含参数传递、返回值）

### C 示例
```c
int square(int x) {
    return x * x;
}

int main() {
    int y = square(3);
    return y;
}
```

### 汇编核心逻辑（main 内部）：
```asm
movl $3, %edi          # 函数参数 x = 3 → 传入 %edi
call square            # 调用 square(x)
movl %eax, -4(%rbp)    # 返回值保存在 %eax → 存入 y
```

---

## ✅ 2. 函数指针 & 回调函数

### C 示例
```c
int add(int a, int b) {
    return a + b;
}

int compute(int (*op)(int, int), int x, int y) {
    return op(x, y);  // 函数指针调用
}
```

### 汇编核心（调用 `op(x, y)`）：
```asm
movq -8(%rbp), %rax     # 函数指针 op → %rax
movl -12(%rbp), %edi    # 参数 x → %edi
movl -16(%rbp), %esi    # 参数 y → %esi
call *%rax              # 间接调用函数指针
```

> 🧠 函数指针调用使用 `call *%rax`，而不是 `call label`。

---

## ✅ 3. 数组访问

### C 示例
```c
int arr[5] = {1, 2, 3, 4, 5};
int x = arr[2];   // 访问第3个元素
```

### 汇编：
```asm
movl arr+8(%rip), %eax   # 每个 int 占 4 字节，arr[2] 在偏移 8
movl %eax, -4(%rbp)
```

> 🧠 静态数组在 `.data` 区，对应汇编中的符号地址访问。

---

## ✅ 4. 结构体访问

### C 示例
```c
struct Point {
    int x;
    int y;
};

struct Point p = {10, 20};
int sum = p.x + p.y;
```

### 汇编：
```asm
movl p(%rip), %eax       # p.x
addl p+4(%rip), %eax     # p.y 加到 eax
movl %eax, -4(%rbp)
```

> 🧠 `p+4` 是结构体内偏移访问，x 在偏移 0，y 在偏移 4。

---

## ✅ 5. for 循环

### C 示例
```c
int sum = 0;
for (int i = 0; i < 10; i++) {
    sum += i;
}
```

### 汇编（逻辑简化）：
```asm
movl $0, -4(%rbp)        # sum = 0
movl $0, -8(%rbp)        # i = 0

.Lloop:
cmpl $10, -8(%rbp)       # if i >= 10
jge .Lend

movl -8(%rbp), %eax
addl %eax, -4(%rbp)      # sum += i

addl $1, -8(%rbp)        # i++
jmp .Lloop

.Lend:
```

---

## ✅ 6. while 循环

```c
int i = 0;
while (i < 5) {
    i++;
}
```

### 汇编：
```asm
movl $0, -4(%rbp)

.Lloop:
cmpl $5, -4(%rbp)
jge .Lexit

addl $1, -4(%rbp)
jmp .Lloop

.Lexit:
```

---

## ✅ 7. 指针访问数组

```c
int arr[3] = {5, 10, 15};
int *p = arr;
int x = *(p + 1); // arr[1]
```

### 汇编：
```asm
leaq arr(%rip), %rax     # rax = &arr[0]
movq %rax, -8(%rbp)      # p = arr

movq -8(%rbp), %rax      # 取出 p
movl 4(%rax), %eax       # *(p + 1) → 每个int 4字节
movl %eax, -4(%rbp)
```

---

## ✅ 8. 结构体 + 指针访问

```c
struct Point { int x; int y; };
struct Point p = {3, 7};
struct Point* ptr = &p;
int v = ptr->y;
```

### 汇编：
```asm
leaq p(%rip), %rax       # &p
movq %rax, -8(%rbp)      # ptr = &p

movq -8(%rbp), %rax
movl 4(%rax), %eax       # ptr->y 偏移 4
movl %eax, -4(%rbp)
```

---

## ✅ 9. 指针数组 + 间接调用函数指针

```c
int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }

int (*ops[2])(int, int) = {add, sub};
int r = ops[1](10, 3);  // 调用 sub
```

### 汇编关键段：
```asm
movq ops+8(%rip), %rax   # 取出 ops[1]
movl $10, %edi
movl $3, %esi
call *%rax               # 间接调用 sub
```

---

## ⚙️ 进阶技巧汇总

| C 功能 | 汇编关键操作 |
|--------|----------------|
| 函数参数传递 | `rdi`, `rsi`, `rdx`, `rcx`, `r8`, `r9` |
| 返回值 | `rax`（整数/指针），`xmm0`（浮点） |
| 函数指针调用 | `call *%rax` |
| 指针访问结构体成员 | `mov offset(%reg), %reg2` |
| for/while 跳转 | `jmp`, `cmp`, `jl/jg/jz/jnz` |

---
