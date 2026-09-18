---
name: yao-service
description: 当任务涉及 ih/service 仓库中的 Yao Service 开发、Yao Query DSL、.http.yao API、.mod.yao 模型、v8go 运行限制或 service/scripts 业务脚本时使用。优先遵守项目分层、统一 CRUD/Query 封装、Yao DSL 约束和响应规范。
---

# Yao Service Project Development Skill

## 核心准则 (Prime Directives)

1.  **架构分层优先**：严格遵守项目分层架构，不要跨层调用或混淆职责。
    -   **API 层 (`apis/*.http.yao`)**: 仅定义接口，调用 Service 脚本。
    -   **业务服务层 (`scripts/service/*.ts`)**: 实现复杂业务逻辑，使用 `model.ts` 或 `nested_query.ts`。
    -   **代理层 (`scripts/utils/proxy.ts`)**: 提供 `ModelProxy` 和 `SessionProxy` 简化调用。
    -   **原子数据层 (`scripts/utils/processor.ts`)**: 提供基础 CRUD 包装，处理通用转换。
    -   **统一转换层 (`scripts/utils/lib.ts`)**: 提供 `queryToQueryParam` 等标准化数据处理。
2.  **禁止直接使用原始 Process 调用模型**：
    -   ❌ **错误**: `Process('models.user.find', 1)`
    -   ✅ **正确 (原子层)**: `import { findModelData } from '@scripts/utils/processor'`
    -   ✅ **正确 (业务层)**: `import { getDataById } from '@scripts/service/model'`
3.  **v8go 环境限制**：
    -   **绝对禁止异步操作**：不准使用 `async/await` 或 `Promise`。
    -   **禁止 Node.js 内置模块**：无法使用 `process`, `fs` (Node), `path` (Node) 等。
    -   **始终使用 `@yao/runtime`**：导入 `Process`, `Exception`, `FS` 等。
4.  **响应标准**：始终使用 `@scripts/return` 中的 `RSuccess` 和 `RError` 返回 API 结果。
5.  **数据安全**：敏感数据必须通过 `scripts/privacy.ts` 进行脱敏处理。

## 目录结构规范

```text
service/
├── apis/                    # API 定义 (.http.yao)
├── models/                  # 数据模型 (.mod.yao)
├── scripts/
│   ├── service/             # 业务逻辑层 (Business Service Layer)
│   │   ├── model.ts         # 统一业务 CRUD 封装 (核心！)
│   │   ├── nested_query.ts  # 多层关系嵌套查询工具 (核心！)
│   ├── utils/               # 工具与底层抽象层
│   │   ├── proxy.ts         # ModelProxy & SessionProxy (代理层)
│   │   ├── processor.ts     # 原子数据操作层 (Atomic Data Layer)
│   │   ├── lib.ts           # 统一转换与处理工具 (Unified Conversion)
│   ├── return.ts            # 统一响应处理器
│   └── privacy.ts           # 数据脱敏工具
```

## 核心统一方法 (Unified Methods)

### 1. 代理调用 (Proxy)
-   **`ModelProxy`**: 屏蔽 `Process('models...')` 的繁琐，提供类型安全的 CRUD 方法。
-   **`SessionProxy`**: 标准化获取 `user_id`, `tid` (租户), `oid` (组织) 的方式。

### 2. 原子操作 (Atomic Processors)
-   位于 `scripts/utils/processor.ts`。
-   **`saveModelData`**: 自动调用 `updateInputData` 处理 UUID、JSON 转换和 `user_id` 注入。
-   **`findModelData`**: 自动处理 `updateOutputData`。

### 3. 数据转换 (Conversion Lib)
-   位于 `scripts/utils/lib.ts`。
-   **`queryToQueryParam`**: 将 AMIS/URL 查询参数转换为 Yao 标准 `QueryParam`。
-   **`PaginateArrayWithQuery`**: 对 JS 内存数组进行模糊搜索、过滤和分页。

### 4. 高级查询 (Nested Query)
-   位于 `scripts/service/nested_query.ts`。
-   **`getNestedData`**: 支持多级关系（如 `doctor.hospital`）的嵌套查询。

## Yao 框架核心文档 (Yao Framework Core)

为了深入理解框架底层机制，请参考以下原始文档：
-   [API DSL 定义](file:///Users/L/Desktop/Code/yao_projects/ih/service/.agent/skills/service-project/references/yao/api_dsl.md): 路由、Guard、输入输出绑定详解。
-   [YaoDSL 核心概念](file:///Users/L/Desktop/Code/yao_projects/ih/service/.agent/skills/service-project/references/yao/YaoDSL/index.md): 涵盖 Model, Flow, Query, Widget 等全量组件。
-   [入门与上手指南](file:///Users/L/Desktop/Code/yao_projects/ih/service/.agent/skills/service-project/references/yao/入门指南/index.md): 快速了解 Yao 的基本原理与开发起步。
