# -*- coding: utf-8 -*-
"""Build coding interview collections from tracked content and Python solutions."""
import html
import json
import shutil
from pathlib import Path


def build(root, out, shell, search):
    data = json.loads((root / 'content/coding/ai-infra.json').read_text())
    questions = data['questions']
    e = html.escape
    def ul(items):
        return '<ul>' + ''.join('<li>' + e(x) + '</li>' for x in items) + '</ul>'
    def wrap(title, body):
        page = shell(title, body, scripts='<script defer src="assets/coding-state.js?v=20261027-release"></script><script defer src="assets/coding-practice.js?v=20261027-release"></script>')
        return page.replace('</head>', '<link rel="stylesheet" href="assets/coding-practice.css?v=20261027-release"></head>')
    dest = out / 'coding-solutions'
    dest.mkdir(exist_ok=True)
    for path in (root / 'content/coding/solutions').glob('*.py'):
        shutil.copy2(path, dest / path.name)
    hub = '''<main id="main-content" class="coding-hub"><section class="hero"><div class="eyebrow">CODING INTERVIEW / PYTHON</div><h1>面试手撕专项复习</h1><p class="lead">按知识点与岗位组织练习。先读题、独立写，再展开提示与参考实现，用边界用例检查自己。</p></section><div class="home-grid"><section class="home-card"><div class="meta">专题 01 · Python / PyTorch</div><h2>AI Infra 面试手撕</h2><p>从 sqrt、MHA 到 LRU 与路径 DP。结合常见面试题型与已有手写笔记，明确每道题的依据和扩展范围。</p><p>11 道练习 · 5 道必练 · 3 道巩固 · 3 道选做</p><a class="button primary" href="coding-ai-infra.html">进入专项复习 →</a></section></div><section class="panel"><h2>怎样复习</h2><ol><li>先澄清输入、输出、约束和边界。</li><li>给自己一个时间盒，脱离参考代码独立完成。</li><li>展开答案对照，标记待巩固或已掌握。</li><li>完成自测并解释复杂度，再尝试追问。</li></ol><p>代码草稿与状态只保存在当前浏览器，可导出 JSON 备份；页面不执行 Python，也不会自动判题。</p></section></main>'''
    (out / 'coding-practice.html').write_text(wrap('面试手撕专项复习', hub))
    toc = '<aside class="course-toc"><a href="coding-practice.html">← 手撕专项目录</a><details open><summary>本专题 · 11 道题</summary>'
    toc += ''.join('<a href="#'+q['id']+'">'+q['id']+' '+e(q['title'])+'</a>' for q in questions)
    toc += '<a href="#sources">面经与选题依据</a></details></aside>'
    intro = '''<div class="eyebrow">专项 01 / PYTHON & PYTORCH</div><h1>AI Infra 面试手撕</h1><p class="lead">优先练 sqrt → MHA／MQA／GQA → LRU，再巩固 Softmax 与路径 DP。题目经过教学改编，面经只证明出现过相应题型，不代表出题概率或官方题库。</p><p class="meta">整理于 2026-10-26 · 11 道题 · 答案默认折叠</p><details class="coding-plan"><summary>今晚 3 小时怎么分配</summary><ol><li>浮点 sqrt（二分与牛顿法）：20 分钟。</li><li>MHA、MQA、GQA：60 分钟。</li><li>LRU：35 分钟。</li><li>Softmax：20 分钟。</li><li>路径 DP：25 分钟。</li><li>重写卡住的部分：20 分钟。选做题留有余力再练。</li></ol></details><div class="coding-toolbar"><label>搜索题目<input id="coding-search" type="search" placeholder="题名、编号、关键词"></label><label>优先级<select id="coding-tier"><option value="">全部</option><option>必练</option><option>巩固</option><option>选做</option></select></label><label>复习状态<select id="coding-filter"><option value="">全部</option><option value="todo">未开始</option><option value="review">待巩固</option><option value="done">已掌握</option></select></label><button type="button" id="coding-export">导出复习记录</button></div><p id="coding-progress" role="status"></p><progress id="coding-meter" max="11" value="0" aria-label="已掌握题目进度"></progress><p id="coding-save" role="status">草稿与状态只保存在当前浏览器；这里不运行代码、不自动判题。</p><p id="coding-empty" hidden>没有匹配题目。调整搜索词或筛选条件即可恢复。</p>'''
    cards=[]
    for q in questions:
        id=q['id']; code=(root/'content/coding/solutions'/q['code']).read_text()
        source_links=' · '.join('<a href="#source-'+s+'">来源 '+s+'</a>' for s in q['sources']) or '为覆盖知识迁移新增，作为扩展练习'
        original=q.get('original')
        link='<a href="'+e(original['url'],quote=True)+'" data-original-note>'+e(original['label'])+' →</a>' if original else ''
        cards.append('<article class="coding-question" id="'+id+'" data-tier="'+q['tier']+'"><div class="coding-meta"><span>'+id+' · '+q['tier']+' · 建议 '+str(q['minutes'])+' 分钟</span><span>'+e(q['evidence'])+'</span></div><h2>'+e(q['title'])+'</h2><p>'+e(q['task'])+'</p><h3>输入输出示例</h3>'+ul(q['examples'])+'<p class="coding-source">'+source_links+'</p><details><summary>需要一点提示</summary>'+ul(q['hints'])+'</details><details class="coding-work"><summary>写下你的代码与思路</summary><label for="draft-'+id+'">Python 草稿（不在浏览器运行）</label><textarea id="draft-'+id+'" class="coding-draft" spellcheck="false" placeholder="先写接口、边界，再写实现……"></textarea><label for="notes-'+id+'">卡住的地方／复盘笔记</label><textarea id="notes-'+id+'" class="coding-notes" placeholder="例如：mask 的含义、指针操作顺序……"></textarea></details><details class="coding-answer"><summary>展开参考答案与易错点</summary><div class="coding-actions"><button type="button" data-copy="code-'+id+'">复制参考代码</button><a download href="coding-solutions/'+q['code']+'">下载 .py</a>'+link+'</div><pre><code id="code-'+id+'">'+e(code)+'</code></pre><p><strong>复杂度：</strong>'+e(q['complexity'])+'</p><h3>易错点</h3>'+ul(q['pitfalls'])+'<h3>面试官可能继续追问</h3>'+ul(q['followups'])+'</details><details class="coding-checks"><summary>自测清单 · '+str(len(q['checks']))+' 项</summary>'+''.join('<label><input type="checkbox" data-check="'+str(i)+'">'+e(c)+'</label>' for i,c in enumerate(q['checks']))+'</details><label class="coding-state">复习状态<select data-review aria-label="'+id+' 复习状态"><option value="todo">未开始</option><option value="review">待巩固</option><option value="done">已掌握</option></select></label></article>')
        search.append({'title':q['title'],'course':data['title'],'url':'coding-ai-infra.html#'+id})
    refs='<section id="sources"><h2>面经与选题依据</h2><p>来源按岗位与题型归纳。未获得完整原题时，题面采用明确约束的标准版本。参考代码是本专题的学习实现，不是面试官标准答案。</p><ol>'
    for s in data['sources']:
        title='<a href="'+e(s['url'],quote=True)+'">'+e(s['title'])+'</a>' if s['url'] else e(s['title'])
        refs+='<li id="source-'+s['id']+'">'+title+'<p>'+e(s['note'])+'</p></li>'
    refs+='</ol></section>'
    page='<div class="course-layout">'+toc+'<main id="main-content" class="course-article coding-course" data-coding-course="ai-infra">'+intro+''.join(cards)+refs+'</main></div>'
    (out/'coding-ai-infra.html').write_text(wrap(data['title'],page))
