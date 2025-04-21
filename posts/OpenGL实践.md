Title: OpenGL 3.3 Core Profile 实践
Date: 2024-03-08
Category: 图形渲染

下面给出一个完整示例，演示如何在 OpenGL 3.3 Core Profile 中同时使用 Instancing 和 Uniform Buffer Object（UBO）。

---

## 1. GLSL 着色器

**顶点着色器 (`instanced_shader.vs`)**  
```glsl
#version 330 core

// 统一块，绑定点为 0，包含投影矩阵和视图矩阵
layout(std140) uniform Matrices {
    mat4 projection;
    mat4 view;
};

// 顶点属性
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aNormal;

// 实例化模型矩阵，拆成 4 个 vec4 属性
layout(location = 2) in vec4 instanceMat0;
layout(location = 3) in vec4 instanceMat1;
layout(location = 4) in vec4 instanceMat2;
layout(location = 5) in vec4 instanceMat3;

out vec3 FragPos;
out vec3 Normal;

void main()
{
    // 重组模型矩阵
    mat4 model = mat4(
        instanceMat0,
        instanceMat1,
        instanceMat2,
        instanceMat3
    );

    vec4 worldPos = model * vec4(aPos, 1.0);
    FragPos = worldPos.xyz;
    Normal = mat3(transpose(inverse(model))) * aNormal;

    gl_Position = projection * view * worldPos;
}
```

**片段着色器 (`instanced_shader.fs`)**  
```glsl
#version 330 core
in vec3 FragPos;
in vec3 Normal;
out vec4 FragColor;
void main()
{
    vec3 color = normalize(Normal) * 0.5 + 0.5;
    FragColor = vec4(color, 1.0);
}
```

---

## 2. C++ 端初始化代码

```cpp
// 已有：GLuint program = 编译链接 instanced_shader.vs/fs

// 1) 创建 UBO 并绑定到 binding point = 0
GLuint uboMatrices;
glGenBuffers(1, &uboMatrices);
glBindBuffer(GL_UNIFORM_BUFFER, uboMatrices);
glBufferData(GL_UNIFORM_BUFFER, 2 * sizeof(glm::mat4), nullptr, GL_STATIC_DRAW);
// 将 UBO 绑定到 binding point 0
glBindBufferRange(GL_UNIFORM_BUFFER, 0, uboMatrices, 0, 2 * sizeof(glm::mat4));
// 在 Shader 中获取 uniform block 索引并关联到 binding point 0
GLuint blockIndex = glGetUniformBlockIndex(program, "Matrices");
glUniformBlockBinding(program, blockIndex, 0);

// 2) 创建 VAO/VBO 并上传顶点数据（位置+法线），略…

// 3) 创建实例化用的 VBO，假设有 N 个实例，且已经准备好 glm::mat4 modelMatrices[N]
GLuint instanceVBO;
glGenBuffers(1, &instanceVBO);
glBindBuffer(GL_ARRAY_BUFFER, instanceVBO);
glBufferData(GL_ARRAY_BUFFER, N * sizeof(glm::mat4), modelMatrices, GL_STATIC_DRAW);

// 将 instanceVBO 的内容附加到已有 VAO
glBindVertexArray(vao);
GLsizei vec4Size = sizeof(glm::vec4);
for (GLuint i = 0; i < 4; i++) {
    GLuint loc = 2 + i; // attribute locations 2,3,4,5
    glEnableVertexAttribArray(loc);
    glVertexAttribPointer(
        loc,                                   // location
        4,                                     // size (vec4)
        GL_FLOAT,                              // type
        GL_FALSE,                              // normalized
        sizeof(glm::mat4),                     // stride
        (void*)(i * vec4Size)                  // offset
    );
    // 每个实例切换一次数据
    glVertexAttribDivisor(loc, 1);
}
glBindVertexArray(0);
```

---

## 3. 每帧更新 UBO 数据

```cpp
// 每帧计算好 proj 和 view
glm::mat4 projection = glm::perspective(...);
glm::mat4 view       = glm::lookAt(...);

// 更新 UBO
glBindBuffer(GL_UNIFORM_BUFFER, uboMatrices);
glBufferSubData(GL_UNIFORM_BUFFER, 0, sizeof(glm::mat4), glm::value_ptr(projection));
glBufferSubData(GL_UNIFORM_BUFFER, sizeof(glm::mat4), sizeof(glm::mat4), glm::value_ptr(view));
glBindBuffer(GL_UNIFORM_BUFFER, 0);
```

---

## 4. 绘制调用

```cpp
glUseProgram(program);
glBindVertexArray(vao);

// 一次 DrawInstanced，绘制 N 个实例
glDrawElementsInstanced(
    GL_TRIANGLES,
    indexCount,      // 索引数
    GL_UNSIGNED_INT,
    0,
    N                // 实例数量
);

glBindVertexArray(0);
```

---

这样，你就完成了：

1. **UBO** 用于高效传递 **projection**/​**view** 等全局统一数据。  
2. **Instancing** 通过 `glVertexAttribDivisor` 让每个实例使用不同的模型矩阵。  

> TIP：若实例数据（如模型矩阵）更新不频繁，可将 `GL_STATIC_DRAW` 换为 `GL_DYNAMIC_DRAW` 并用 `glBufferSubData` 局部刷新。