# 统计复习台

数理统计课程练习系统

把教材知识点、公式、题库和常见问答整理为可以按章复习的 Web 应用。当前题库文件包含 **205 道题**，内容与程序分开保存，便于核对和更新。

## 功能与使用场景

| 复习任务 | 对应功能 |
| --- | --- |
| 梳理课程 | 按章、节与知识点浏览课程结构 |
| 集中练习 | 按章节、难度、标签与来源筛选题目，另有核心题入口 |
| 查公式与概念 | 公式手册及 χ²/t/F 分布、估计、检验等高频问答 |
| 自测与回顾 | 测验页面和题目分布仪表盘 |

## 本地运行

在项目根目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

打开 `http://localhost:5050`，也可通过 `PORT` 环境变量调整端口。

## 数据与实现

| 路径 | 内容 |
| --- | --- |
| `app.py` | Flask 页面路由与 JSON API |
| `data/problems.json` | 205 道题的结构化数据 |
| `data/core_problems.json` | 单独整理的核心题 |
| `data/formulas.json` | 公式数据 |
| `data/knowledge_content.json` | 知识点内容 |
| `data/textbook_structure.json` | 课程章节结构 |
| `templates/` | 原生 HTML、CSS 与 JavaScript 页面模板 |
| `render.yaml` | Render 部署配置 |

数据抽取与修复脚本位于 `data/`。将资料整理为 JSON，再通过 API 支持不同复习入口，是本项目的主要实践内容。

## 当前边界

- 考试日期在 `app.py` 中固定为 `2026-07-01`，新学期复用前需修改；过期倒计时不代表当前考试安排。
- 课程题目和解答属于学习整理材料，使用时应对照教材与教师要求核验。
- [knowledge-base](https://github.com/Wangxy009/knowledge-base) 内保留早期副本；独立应用以后续本仓库为主要入口。两处内容不自动同步。

项目通过 AI 辅助开发与资料整理形成，采用 Flask 3、gunicorn 与结构化 JSON。
