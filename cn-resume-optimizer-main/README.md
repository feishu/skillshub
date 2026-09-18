# cn-resume-optimizer (OpenClaw Skill)

面向**中国职场（技术岗）** 的简历优化 Skill：本地优先（不外发简历）、可审计、可扩展。

核心链路：**PDF → 文本 → 简历结构化 / JD 结构化 → Rubric 评估 → 输出优化稿（Markdown）+ 报告**，并可选导出 PDF。

> 注意：本项目是「工具链 + 规则模板」而不是“一键改简历魔法”。它追求的是**稳定、可控、可追问的证据链**。

---

## 安装（两种方式）

### 方式 A：拖入 OpenClaw skills 目录（推荐）

把整个文件夹 `cn-resume-optimizer/` 复制为：

```bash
# 1) 你的 OpenClaw skills 目录（通常是 ~/.openclaw/skills）
mkdir -p ~/.openclaw/skills

# 2) 拷贝进去（把目录名改成你希望的 slug）
cp -a ./cn-resume-optimizer ~/.openclaw/skills/cn-resume-optimizer
```

随后在 OpenClaw 中通过该 skill 的脚本运行（见下方“快速开始”）。

### 方式 B：作为普通脚本工具使用

你也可以不依赖 OpenClaw，直接运行 `scripts/` 下的脚本完成提取/解析/导出。

> 仓库名建议：`cn-resume-optimizer`（与 skill slug 同名，便于安装与定位）。

---

## 依赖

### 必需

- **Python 3**
- `pip install PyMuPDF`（用于 PDF 文本提取，import 名称为 `fitz`）

```bash
pip install PyMuPDF
```

### 可选（用于 Markdown → PDF 导出）

- `pandoc`
- `weasyprint`（本项目默认用 pip 安装）
- 中文字体（推荐 Noto CJK）

Ubuntu/Debian 参考：

```bash
sudo apt-get update
sudo apt-get install -y pandoc fonts-noto-cjk
pip install weasyprint
```

---

## 快速开始

### 1) PDF → 文本

```bash
python3 scripts/extract_pdf_text.py resume.pdf > out/raw.txt
```

### 2) 简历结构化

```bash
python3 scripts/parse_resume_cn.py out/raw.txt > out/resume.json
```

### 3) JD 结构化

```bash
python3 scripts/parse_jd_cn.py jd.txt > out/jd.json
```

### 4) 导出 PDF（可选）

```bash
bash scripts/md2pdf.sh optimized_resume.md optimized_resume.pdf
```

---

## references（必读）

- `references/china_resume_rubric.md`：评估 Rubric（对口度/结果/可信度/结构 + “抽象上提”规则）
- `references/china_resume_template.md`：中文简历模板（技术岗默认）

---

## 安全边界

- 默认不进行任何外网请求，不上传简历内容。
- 只处理你传入的文件路径，输出写入你指定的目录。

---

## 许可证

建议使用 MIT（你可以按需替换）。
