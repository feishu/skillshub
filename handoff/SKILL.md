---
name: handoff
description: MAPAI 平台项目架构上下文、已完成工程基线、质量门禁与下一阶段（Gate 2）无缝接续实施指引。
---

# MAPAI 平台研发交接与接续实施指引

本文档作为 MAPAI 平台的全局交接基准。后续会话无论由任何 Agent 或工程师接手，均可通过本 Skill 快速恢复完整上下文，并无缝进入下一阶段的研发。

---

## 1. 项目核心背景与不可变原则

1. **工作区与代码库结构**:
   - **MAPAI 平台核心工作区**: `/Users/L/Desktop/MAPAI/platform`（独立 Git 仓库 `main` 分支）。
   - **Mastra 引擎源码目录**: `/Users/L/Desktop/MAPAI/code/mastra`（**绝对只读，严禁任何修改、补丁或侵入式变更**）。
   - **Mastra 引用隔离门禁**: 仅允许在 `packages/adapters/mastra` 内部引用 `@mastra/*` 模块。运行 `pnpm check:mastra-imports` 强制校验，全平台其余模块对 Mastra 零直接依赖。

2. **数据库与多租户架构**:
   - **远程测试库**: `39.101.71.171:5432/syddb`（配置于 `platform/.env.test.local`）。
   - **行级安全 (RLS)**: 所有核心表均启用 `FORCE ROW LEVEL SECURITY`，严格绑定 `current_setting('app.tenant_id', true)`。
   - **数据库迁移脚本**: 位于 `db/migrations/` 与 `db/rls/`，严格按编号顺延（目前已完成 `0001` ~ `0008`）。

3. **编码与工程规范**:
   - **语言规范**: 所有文档、注释、提交信息均使用简体中文。
   - **TypeScript 配置**: 继承 `tsconfig.base.json`，启用 `strict: true` 与 `exactOptionalPropertyTypes: true`。可选属性联合需显式支持 `| undefined`。
   - **并发与测试模式**: 在 PostgreSQL 并发测试（如 100 并发重试）中，必须使用 `runWithPoolLimit(..., limit = 4)` 受控连接池模式，防止连接耗尽。
   - **测试项目划分**: 纯单元测试命名为 `*.test.ts`（运行在 unit 项目）；依赖 PostgreSQL 的测试命名为 `*.integration.test.ts` 或 `e2e/**/*.e2e.test.ts`（运行在 integration 项目）。

---

## 2. 已完成里程碑与工程资产 (Gate 1 已 100% 达成)

截至当前版本，Gate 1 匿名合成随访闭环验证已全部完成，共沉淀 14 个核心 Package / App：

### 2.1 模块资产明细

| 层次 | 模块 / 应用 | 核心职责与关键实现 |
| :--- | :--- | :--- |
| **Domain** | `@mapai/domain` | 强类型品牌标识（`TenantId`, `ExecutionId`, `AttemptId`, `CommandId`, `ReleaseId`）、状态枚举与统一错误类型 |
| **Runtime** | `@mapai/tenant-runtime` | 租户运行时解析器（`TenantRuntimeResolver`）、单飞防穿透缓存、`ExecutionEnvelope` 签名与验签 |
| **Execution** | `@mapai/execution` | 命令总线（`CreateExecution`, `StartAttempt`, `ResumeApproved`, `RequestCancellation`, `ReconcileExecution`）、CAS 状态机、租约 Fencing 与 JSON-safe 检查点 |
| **Release** | `@mapai/release` | 不可变发布包 `ReleaseBundle` 契约、哈希指纹校验与版本别名原子解析 |
| **Capability** | `@mapai/capability` | 双重门禁体系（`CapabilityAdmission`）、拒绝矩阵（严禁 raw Tool/direct MCP/Workspace）、派发策略（`DispatchPolicy`） |
| **Governance** | `@mapai/governance` | 审批事实表 `ApprovalFact`（职责分离 `requester != approver`、token 哈希存储）与副作用事实表 `EffectFact` 状态机（`PREPARED` -> `DISPATCHING` -> `COMMITTED`/`REJECTED`/`OUTCOME_UNKNOWN`） |
| **Followup** | `@mapai/followup` | 匿名随访领域：`ContextCompiler` 授权最小化编译（类别白名单与过期剔除）与 `RiskClassifier` 确定性红旗风险评估（红旗症状绝对防降级） |
| **Postgres Adapter** | `@mapai/adapter-postgres` | PostgreSQL 仓储实现（Execution、Release、Approval/Effect、Outbox/Inbox、Lease），迁移执行器与租户上下文事务封装 |
| **Mastra Adapter** | `@mapai/adapter-mastra` | Mastra 引擎封装：每租户物理独立 `PostgresStore` 运行时工厂、`WorkflowRuntimeAdapter` 与阶段重入适配器 |
| **Connectors Adapter**| `@mapai/adapter-connectors` | 纯内存合成连接器（`SyntheticReadConnector`、按 `operationId` 幂等去重 `SyntheticIdempotentWriteConnector`、断链故障注入 `SyntheticAmbiguousConnector`） |
| **Gateway App** | `apps/capability-gateway` | 网关派发器：不可逆点协议（事务内 Claim -> 事务外脱机 Connector 派发 -> 新事务终态提交与对账状态投影） |
| **API App** | `apps/platform-api` | 统一 HTTP 传输层（Hono 驱动），Synthetic Bearer 鉴权中间件，多租户隔离与 404 零信息泄露 |
| **Worker App** | `apps/operations-worker` | 异步作业与对账 Worker 基础架构 |
| **E2E & Spike** | `e2e/`, `docs/spike/` | 端到端随访业务闭环测试、7 维故障注入矩阵测试、数据清单扫描与 Gate 1 Go/No-Go 决策报告 |

---

## 3. 验证基线与质量门禁

在开始任何新阶段任务之前，必须先运行以下命令确认基线状态为 100% 绿灯：

```bash
cd /Users/L/Desktop/MAPAI/platform

# 1. Mastra 引用隔离检查
pnpm check:mastra-imports

# 2. 全局类型与代码规范检查
pnpm lint && pnpm typecheck

# 3. 全量单元测试 (124/124 PASS)
pnpm test

# 4. 全量集成与 E2E 测试 (52/52 PASS)
pnpm test:integration

# 5. Mastra 源码只读完整性检查
git -C ../code/mastra diff --quiet
```

---

## 4. 下一阶段（Gate 2）核心目标与接续实施路线

Gate 1 确立了平台的纯内存合成闭环与基础安全体系。**Gate 2 的核心目标是：从合成匿名验证迈向真实合规生产化**。

### 4.1 Gate 2 核心工作分解

1. **真实数据合规与 PHI 生命周期管理**:
   - 数据库字段级加密（Field-Level Encryption）与密钥管理服务（KMS / Envelope Encryption）。
   - 敏感 PHI（患者真实身份、就诊记录）去标识化/假名化引擎与动态脱敏脱敏切面。
   - 审计日志全量归档（WORM 存储不可篡改合规日志）。
2. **传输层与网络安全加固**:
   - 强制启用 PostgreSQL TLS/SSL 双向认证与连接加密（解决 Gate 1 测试库明文警告）。
   - 细粒度 IAM / OAuth2.0 / MTLS 服务间身份互认。
3. **真实系统连接器与适配器研发**:
   - 基于 FHIR R4 / HL7 协议的真实医院 HIS/EMR 临床数据连接器。
   - 统一短信/微信公众号/患者端推送网关连接器（具备真实重试与对账策略）。
4. **大模型风控与模型安全护栏 (Guardrails)**:
   - 真实医疗大模型（如 Med-PaLM / 通义医疗等）对接与上下文长度自适应管理。
   - 医疗合规安全护栏：幻觉检测、处方越权拦截、模型输出与确定性医学指南强对齐。
5. **分布式调度与高可用 Worker**:
   - 分布式 Outbox 投递 Worker 与对账 Engine。
   - 租约自动续期与节点宕机无损故障转移（Failover）。

---

## 5. 新会话进入与执行流程

新会话开始时，建议遵循以下步骤：
1. **加载本交接 Skill**: 确认当前工作区状态与提交日志（`git log -n 5`）。
2. **运行基线检查**: 执行第 3 节的质量门禁命令，确保没有未提交的脏变更。
3. **制定 Gate 2 细化实施计划**: 进入 Plan Mode，创建 `implementation_plan.md` 并更新 `tasks/todo.md`。
4. **严格遵循 TDD 驱动实施**: 编写失败测试 -> 编写最小实现 -> 验证通过 -> 提交代码并记录进度。
