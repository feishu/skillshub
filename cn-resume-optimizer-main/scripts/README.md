本目录提供最小可执行链路（本地优先）：

- extract_pdf_text.py：PDF→文本（依赖 PyMuPDF）
- parse_resume_cn.py：中文简历文本→结构化 JSON（可控的启发式解析，保留 raw block）
- parse_jd_cn.py：中文 JD 文本→结构化 JSON（职责/要求/关键词）
- md2pdf.sh：Markdown→PDF（依赖 pandoc + weasyprint + 中文字体）

设计目标是让简历优化的“输入/结构化/输出”都可控、可审计；改写与对齐逻辑放在主技能层做。
