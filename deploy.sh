#!/bin/bash
# 一键将 ~/.skillshub 下所有技能自动投影分发给所有 AI 工具
set -e

HUB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGETS=(
  "$HOME/.claude/skills"
  "$HOME/.gemini/config/skills"
  "$HOME/.gemini/skills"
  "$HOME/.cursor/skills"
  "$HOME/.codex/skills"
  "$HOME/.agents/skills"
)

echo "=== 正在将 ~/.skillshub 技能统一投影到各 AI 工具 ==="

# 统计有效技能
skills=()
for d in "$HUB_DIR"/*; do
  if [ -d "$d" ] && [ -f "$d/SKILL.md" ]; then
    skills+=("$(basename "$d")")
  fi
done

echo "在中央库中发现 ${#skills[@]} 个有效技能。"

for target in "${TARGETS[@]}"; do
  mkdir -p "$target"
  linked=0
  for s in "${skills[@]}"; do
    src="$HUB_DIR/$s"
    dst="$target/$s"
    if [ ! -e "$dst" ] && [ ! -L "$dst" ]; then
      ln -s "$src" "$dst"
      ((linked++))
    fi
  done
  echo "工具目录 $(basename "$(dirname "$target")")/$(basename "$target"): 新增链接 $linked 个 (总计 $(ls -1 "$target" | wc -l | tr -d ' ') 个)"
done

echo "✅ 投影分发完成！所有 AI 工具已实时同步最新技能。"
