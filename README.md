# AI基础与工程笔记

从数学、机器学习到模型训练、AI Infra与Agent工程的中文开放学习笔记，配图解、逐步计算和158道交互练习。

**在线阅读：https://pyq623.github.io/ai-study-notes/**

| 内容 | 练习 |
|---|---:|
| 单元1 · 机器学习入门 | 14 |
| 单元2 · 线性代数基础 | 16 |
| 单元3 · 概率、统计与信息论 | 15 |
| 单元4 · 神经网络与训练 | 15 |
| 单元5 · AI Infra与计算机基础 | 50 |
| 工程专题 · Agent、上下文与工程实践 | 48 |

全站可相互跳转，首页支持章节标题搜索，相关知识点提供跨章链接。题目支持判分、逐项解析、错题筛选与JSON导出。答题记录只保存在读者当前浏览器，不上传、不跨设备同步；本地文件版记录不会自动迁移，目前没有导入功能。

笔记由pyq623整理并借助AI辅助编写，练习均为自编教学题，非官方题库。技术资料在各小节列出，欢迎通过Issues和Pull Requests勘误。

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

- `content/unit-1.md` ～ `unit-5.md`：五个基础单元。
- `content/engineering.md`：工程专题。
- `content/*-questions.json`：题目、正确选项、逐项解析与回看锚点。新增题目请追加ID，不重排已有题号，以保留读者记录。
- `assets/tree-*.svg`：教学图示。
- `scripts/build.py`：页面、章节锚点、练习入口和跨章链接。
- `assets/quiz.js`、`site.js`、`course.css`：练习、导航与样式。

提交前运行 `npm run build && npm test`。合并到main后自动发布；初次部署需在仓库 Settings → Pages 中选择 **GitHub Actions**。

`VERSION`和更新日志使用四段站点发布号；`package.json`使用npm要求的三段SemVer版本号。

## 许可

原创文字、题目与图示采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名为pyq623，并链接本仓库。构建代码和原创样式采用[MIT](LICENSE)。第三方依赖与引用资料不纳入本项目原创许可，参见[第三方声明](THIRD_PARTY_NOTICES.md)。
