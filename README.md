# AI Agent Skills Central Hub (~/.skillshub)

本项目是本机所有 AI Agent（Claude Code, Cursor, Codex, Gemini/Antigravity 等）技能的**单一真实数据源（SSOT）**与**自动化上游追更中心**。

## 架构与分发规范
- **物理源码唯一存储**：`~/.skillshub/<skill-name>/SKILL.md`
- **各客户端通过软链接（Symlink）投影**：
  - Claude Code: `~/.claude/skills/`
  - Gemini Antigravity: `~/.gemini/config/skills/`
  - Gemini CLI: `~/.gemini/skills/`
  - Cursor: `~/.cursor/skills/`
  - Codex: `~/.codex/skills/`
  - Agents: `~/.agents/skills/`

## 上游追更与同步机制（解决代码孤岛）
本项目通过 `skills-manifest.json` 显式声明了各大官方技能上游，并配置了自动追更体系：

### 1. 声明式清单 (`skills-manifest.json`)
- **官方上游**：`gstack`、`superpowers`、`samber-golang`、`mattpocock`、`anthropic`、`vercel` 等
- **受保护自研技能**：`yao-service`、`handoff`、`cn-resume-optimizer-main`（绝不被官方覆盖）

### 2. 本地一键追更 (`sync-upstream.sh`)
```bash
# 检查各大上游是否有新版本（不修改任何文件）
./sync-upstream.sh --check

# 同步指定上游（例如 gstack 或 superpowers）
./sync-upstream.sh gstack
./sync-upstream.sh samber-golang

# 一键拉取所有上游最新代码
./sync-upstream.sh --all
```

### 3. GitHub Actions 云端周更流水线 (`.github/workflows/upstream-sync.yml`)
- 每周一自动检查各大上游变更。
- 若有更新，自动创建 Pull Request 供你审查 Diff。
- 你在 GitHub 网页上点击 Merge 后，本地只需 `git pull` 即可同步最新成果！
