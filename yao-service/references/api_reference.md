# Service Project API Reference

## 1. 业务服务层 (`@scripts/service/model`)
*这是开发中最常用的层级，封装了所有业务必须的自动化逻辑（如生成 UUID、填充 `tid`/`oid`）。*

-   **`getDataById(modelId, id, select?, isWithRelation?)`**: 获取单条数据，支持自动加载关联关系。
-   **`dataSearch(modelId, page, perPage, querys, params, payload)`**: 综合搜索方法，含 URL 查询转换。
-   **`newData(modelId, payload)`**: 创建数据。自动生成 UUID，注入 `tid`/`oid`。
-   **`saveDataByUUID(modelId, uuid, payload)`**: 按 UUID 更新数据。

## 2. 嵌套查询层 (`@scripts/service/nested_query`)
-   **`getNestedData(modelId, id, options)`**: 支持 `relations: ['doctor', 'prescriptions.items']`。

## 3. 原子数据层 (`@scripts/utils/processor`)
*底层 CRUD 包装，通常用于简单逻辑或当业务层封装太重时。*

-   **`saveModelData(modelId, payload)`**: 保存数据，内部执行 `updateInputData`。
-   **`findModelData(modelId, id, queryParam?)`**: 查找数据，内部执行 `updateOutputData`。

## 4. 统一转换层 (`@scripts/utils/lib`)
-   **`queryToQueryParam(model, querys, queryParams?)`**: 将 URL/AMIS 参数（`keywords`, `status`）转换为 Yao `wheres`。
-   **`updateInputData(model, data)`**: 数据落库前的预处理（cast 类型、生成 UUID）。
-   **`updateOutputData(model, data)`**: 数据查出后的后期处理（JSON 反序列化、Boolean 修复）。
-   **`PaginateArrayWithQuery(data, querys, payload, searchFields)`**: 对 JS 数组进行模糊搜索和分页。

## 5. 代理层 (`@scripts/utils/proxy`)
-   **`ModelProxy` Class**: `Find()`, `Paginate()`, `Create()`, `Update()`, `Delete()`。
-   **`SessionProxy.GetMany(['user_id', 'tuuid', 'ouuid'])`**: 获取多个会话变量。

## 6. 其他常用工具
-   **`@scripts/service/user.getUserSession()`**: 获取当前登录用户常用信息。
-   **`@scripts/return.RSuccess(data, message?)`**: 成功响应。
-   **`@scripts/return.RError(message, code?)`**: 失败响应。
