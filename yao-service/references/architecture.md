# Service Project Architecture Layers

## 1. 外部接口层 (API Layer)
-   **位置**: `apis/*.http.yao`
-   **职责**: 定义路由、HTTP 方法、Guards 和输入输出映射。
-   **规范**: 禁止在 API 中直接实现逻辑，必须调用 `scripts.service.*`。

## 2. 业务服务层 (Business Service Layer)
-   **位置**: `scripts/service/*.ts`
-   **职责**: 实现具体的业务用例（UseCase）。如：下单、挂号、开方。
-   **核心依赖**:
    -   `@scripts/service/model`: 用于标准的业务 CRUD。
    -   `@scripts/service/user`: 用于授权和用户上下文。
    -   `@scripts/return`: 用于标准化输出。

## 3. 抽象代理层 (Proxy Layer)
-   **位置**: `scripts/utils/proxy.ts`
-   **职责**: 提供面向对象的代理对象。
-   -   `ModelProxy`: 简化对 `models.*` 处理器的调用，提供链式或方法式调用。
-   -   `SessionProxy`: 强类型的会话变量访问。

## 4. 原子数据层 (Atomic Data Layer)
-   **位置**: `scripts/utils/processor.ts`
-   **职责**: 封装最基础的 Yao 处理器调用，并注入“统一转换逻辑”。
-   **转换逻辑**:
    -   执行 `updateInputData`: UUID 生成, JSON 序列化转换, 数字类型强制转换。
    -   执行 `updateOutputData`: JSON 反序列化, Decimal 还原, Boolean 还原。

## 5. 统一转换层 (Unified Conversion Layer)
-   **位置**: `scripts/utils/lib.ts`
-   **职责**: 提供跨层级通用的数据结构转换工具。
-   **核心工具**:
    -   `queryToQueryParam`: URL 请求 -> Yao 查询参数。
    -   `PaginateArrayWithQuery`: 模拟 SQL 查询 JS 数组。

## 6. 数据模型层 (Data Model Layer)
-   **位置**: `models/*.mod.yao`
-   **职责**: 数据库 Schema 定义。
