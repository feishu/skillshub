# AI Agent Skills Central Hub (~/.skillshub)

本项目是本机所有 AI Agent（Claude Code, Cursor, Codex, Gemini/Antigravity 等）技能的**单一真实数据源（SSOT）**。

## 目录与分发规范
- 实体代码存放在本目录：`~/.skillshub/<skill-name>/SKILL.md`
- 各客户端通过符号链接（Symlink）投影：
  - Claude Code: `~/.claude/skills/`
  - Gemini Antigravity: `~/.gemini/config/skills/`
  - Gemini CLI: `~/.gemini/skills/`
  - Cursor: `~/.cursor/skills/`
  - Codex: `~/.codex/skills/`
  - Agents: `~/.agents/skills/`

## 维护指引
1. **新增/修改技能**：直接在 `~/.skillshub/` 下创建或修改，所有客户端实时生效。
2. **版本备份**：本目录已建立 Git 本地仓库，可直接 `git add . && git commit`。如需云端备份，可添加私有远程库 `git remote add origin <your-private-repo-url>` 并推送到 GitHub。
