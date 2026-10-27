# AI学习与面试笔记

一个入口打开两份中文笔记：AI基础与工程笔记（208题），以及Agentic RL面试笔记（60题、20道口述追问）。包含268道交互练习，另有11道面试手撕练习，配图解、手算与逐项解析。

**在线阅读：https://pyq623.github.io/ai-study-notes/**

基础与面试入口：[基础与工程笔记](https://pyq623.github.io/ai-study-notes/study.html)、[面试笔记](https://pyq623.github.io/ai-study-notes/interview.html)。

| 内容 | 练习 |
|---|---:|
| 单元1 · 机器学习入门 | 14 |
| 单元2 · 线性代数基础 | 16 |
| 单元3 · 概率、统计与信息论 | 15 |
| 单元4 · 神经网络与训练 | 15 |
| 单元5 · AI Infra基础 | 28 |
| 单元6 · 数据结构与算法 | 32 |
| 单元7 · 计算机系统基础 | 8 |
| 单元8 · 强化学习与偏好优化算法 | 32 |
| 工程专题 · Agent、上下文与工程实践 | 48 |
| 面试笔记 · Agentic RL的5个单元 | 60 |

全站可相互跳转，首页支持搜索两份笔记与手撕专项，基础笔记目录位于`study.html`，相关知识点提供跨章链接。两份笔记的交互题支持判分、逐项解析、错题筛选与JSON导出。答题记录只保存在读者当前浏览器，不上传、不跨设备同步；本地文件版记录不会自动迁移，目前没有导入功能。

笔记由pyq623整理并借助AI辅助编写，练习均为自编教学题，非官方题库。技术资料在各小节列出，欢迎通过Issues和Pull Requests勘误。

## 面试手撕专项

入口 `coding-practice.html`，AI Infra 专题为 `coding-ai-infra.html`。11 道 Python/PyTorch 练习（5 道必练、3 道巩固、3 道选做）覆盖 sqrt、Attention、LRU、Softmax、路径 DP 与字符串，提供折叠答案、自测清单、草稿、复习状态和 JSON 导出；不在网页执行代码或自动判题。记录仅保存在当前浏览器与域名下，`?preview=1` 隔离测试记录。

源码为 `content/coding/ai-infra.json` 与 `content/coding/solutions/`，由 `scripts/coding_practice.py` 生成。调整顺序时保留题号，避免复习记录错位。运行 Attention 和张量 Softmax 示例需要另外安装 PyTorch；构建网站不需要 PyTorch。`npm test` 会在已安装 PyTorch 时运行 `tests/test_coding_torch.py` 的数值测试，未安装时明确跳过该组测试。

## 本地构建

需要 Python 3.11+、Node.js 20+。安装依赖后即可离线构建：

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm ci
npm run build
npm test
python3 -m http.server 8000 --directory docs
```

打开 http://localhost:8000 。生成文件位于 `docs/`，不提交至Git；GitHub Actions会从源码重新构建并部署。普通网页阅读不需要安装任何依赖。

## 修改内容

- `content/unit-1.md` ～ `unit-8.md`：八个主题单元。
- `content/engineering.md`：工程专题。
- `content/interview-course.json`、`interview-research.html`：面试讲义、60题、口述提纲和经过公开化整理的面经来源。
- `scripts/interviews.py`、`assets/interview-quiz.js`：面试页面生成与就地练习／口述笔记。
- `content/*-questions.json`：题目、正确选项、逐项解析与回看锚点。新增题目请追加ID，不重排已有题号，以保留读者记录。
- `assets/tree-*.svg`、`rl-*.svg`：教学图示。
- `scripts/build.py`：页面、章节锚点、练习入口和跨章链接。
- `assets/quiz.js`、`site.js`、`course.css`：练习、导航与样式。

提交前运行 `npm run build && npm test`。合并到main后自动发布；初次部署需在仓库 Settings → Pages 中选择 **GitHub Actions**。

`VERSION`和更新日志使用四段站点发布号；`package.json`使用npm要求的三段SemVer版本号。

## 旧版兼容

单元5原有内容拆为单元5～7，保留全部题号；旧链接会定位到新小节。网页版本已有答题记录按题号继续读取，工程专题的记录保持独立；该兼容不涉及本地文件版或跨设备同步。

`content/legacy-unit-5-links.json`保存旧锚点映射。`scripts/build.py`中的`STORAGE`指定固定存储键，不要随单元编号调整：工程专题保留旧unit-6-v2键，新单元6使用unit-6-v3；单元6、7从旧unit-5-v2读取对应题目作为回退，新记录优先。

新增单元8使用`content/rl-questions.json`，题号8-01～8-32。内部课程ID独立于展示编号：工程专题仍为8，新单元8为9；构建器的`FILES`、`LABELS`和`STORAGE`分别指定网页、展示名称与记录存储，保持旧记录兼容。

面试笔记保留原题号AR1-01～AR5-12和独立存储键`accio-agentic-rl-v1-u1`～`u5`。个人口述与答题记录只在浏览器中保存；本地文件版记录不会跨域自动迁移。公开内容不包含个人面试日程或聊天记录。

## 许可

原创文字、题目与图示采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名为pyq623，并链接本仓库。构建代码和原创样式采用[MIT](LICENSE)。第三方依赖与引用资料不纳入本项目原创许可，参见[第三方声明](THIRD_PARTY_NOTICES.md)。
