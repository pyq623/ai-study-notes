# -*- coding: utf-8 -*-
"""Build the public study site from Markdown and question data; no private paths."""
from pathlib import Path
import html
import json
import re
import shutil
import subprocess
from markdown_it import MarkdownIt
import question_rendering
import interviews
import coding_practice

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs'
CONTENT = ROOT / 'content'
REPO = 'https://github.com/pyq623/ai-study-notes'
TITLE = 'AI基础与工程笔记'
SITE_TITLE = 'AI学习与面试笔记'
QUESTION_FILES = ('foundation-questions.json', 'rl-questions.json', 'engineering-questions.json')
STUDY_QUESTIONS = sum(len(json.loads((CONTENT / name).read_text())) for name in QUESTION_FILES)
INTERVIEW = interviews.load(CONTENT)
TOTAL_QUESTIONS = STUDY_QUESTIONS + len(interviews.questions(INTERVIEW))
MATH = re.compile(r'\$\$([\s\S]*?)\$\$|(?<!\$)\$([^\n$]+?)\$(?!\$)')
COURSES = [
    (1, '机器学习入门', '从样本、特征和标签，到近邻、聚类与模型评估。'),
    (2, '线性代数基础', '向量、矩阵、秩、特征值与正定，配逐步计算。'),
    (3, '概率、统计与信息论', '条件概率、常见分布、期望方差、熵与最大熵。'),
    (4, '神经网络与训练', '前向与反向传播、损失、AdamW、归一化与梯度裁剪。'),
    (5, 'AI Infra基础', '显存估算、并行训练、通信算子、KV cache与推理性能。'),
    (6, '数据结构与算法', '复杂度、数组与链表、树与图、排序，以及B-tree与B+树。'),
    (7, '计算机系统基础', '线程与锁、TCP与HTTP、数据库索引、缓存与消息重试。'),
    (9, '强化学习与偏好优化算法', 'Advantage、GAE、PPO、GRPO、DAPO、GSPO与DPO，配公式推导与手算。'),
    (8, '工程专题', 'Agent、工具调用、上下文、RAG、并发与故障恢复。'),
]
# IDs are stable identities, not display positions: engineering already owns ID 8.
FILES = {u: f'unit-{u}' for u, _, _ in COURSES}
FILES.update({8: 'engineering', 9: 'unit-8'})
LABELS = {u: f'单元{u}' for u, _, _ in COURSES}
LABELS.update({8: '工程专题', 9: '单元8'})
# Storage identity is independent of display order. Engineering keeps its original key.
STORAGE = {u: {'storage_key': f'ai-study-notes-unit-{u}-v2'} for u,_,_ in COURSES}
STORAGE[6] = {'storage_key': 'ai-study-notes-unit-6-v3', 'legacy_storage_key': 'ai-study-notes-unit-5-v2'}
STORAGE[7] = {'storage_key': 'ai-study-notes-unit-7-v2', 'legacy_storage_key': 'ai-study-notes-unit-5-v2'}
STORAGE[8] = {'storage_key': 'ai-study-notes-unit-6-v2'}
STORAGE[9] = {'storage_key': 'ai-study-notes-unit-8-v2'}
RELATED = {
    (1,7):[(3,'lesson-1','概率与统计基础')],
    (2,8):[(4,'lesson-4','反向传播与矩阵梯度')],
    (3,7):[(4,'lesson-2','Softmax与交叉熵'),(9,'lesson-6','策略熵与reference KL')],
    (4,2):[(3,'lesson-7','信息论与熵'),(9,'lesson-10','DPO的成对偏好loss')],
    (4,5):[(5,'lesson-1','训练状态与显存'),(9,'lesson-5','PPO的Actor与Critic更新')],
    (4,7):[(5,'lesson-2','数据并行与全局batch')],
    (5,2):[(4,'lesson-5','梯度与优化器')],
    (5,4):[(8,'lesson-3','上下文管理')],
    (6,5):[(7,'lesson-4','数据库索引：回表与覆盖索引')],
    (7,1):[(8,'lesson-2-shared-config','共享配置与互斥'),(8,'lesson-8','并发与取消')],
    (7,3):[(8,'lesson-11','流式响应与背压')],
    (7,4):[(6,'lesson-5','B-tree与B+树的结构和图示'),(8,'lesson-10','缓存、限流与索引')],
    (7,6):[(8,'lesson-7','重试与幂等')],
    (8,2):[(6,'lesson-3-step-9','DAG与拓扑排序')],
    (8,3):[(5,'lesson-4','Attention与KV cache')],
    (8,7):[(7,'lesson-6','事务与消息重投')],
    (8,8):[(7,'lesson-1','线程、锁与死锁')],
    (8,10):[(6,'lesson-2','数组、栈、队列与哈希'),(7,'lesson-4','数据库索引')],
    (8,11):[(5,'lesson-5','Prefill、Decode与延迟'),(7,'lesson-3-step-2','HTTP版本与传输')],
    (9,1):[(4,'lesson-2','Softmax与交叉熵')],
    (9,5):[(4,'lesson-5','优化器与梯度更新'),(5,'lesson-1','训练状态与显存')],
    (9,6):[(3,'lesson-7','信息论与KL')],
    (9,9):[(5,'lesson-5','长回答与MoE训练背景')],
    (9,10):[(4,'lesson-2','交叉熵与logistic损失')],
}

def escaped_json(value):
    return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c').replace('&', '\\u0026')

def nav(current=None,area='study'):
    collections=[('index.html','总览','hub'),('study.html','基础与工程笔记','study'),('interview.html','面试笔记','interview'),('coding-practice.html','手撕专项','coding')]
    global_nav='<nav class="site-nav" aria-label="全站导航">'+''.join('<a href="'+url+'"'+(' aria-current="page"' if area==key else '')+'>'+label+'</a>' for url,label,key in collections)+'<a href="'+REPO+'">GitHub ↗</a></nav>'
    links=[(FILES[u]+'.html',LABELS[u],u) for u,_,_ in COURSES] if area=='study' else [(f'interview-unit-{u}.html',f'面试单元{u}',None) for u in range(1,6)]+[('interview-research.html','面经与追问',None),('interview-sources.html','资料来源',None)] if area=='interview' else []
    chapters='<nav class="site-nav chapter-nav" aria-label="'+('笔记章节' if area=='study' else '面试章节')+'">'+''.join('<a href="'+url+'"'+(' aria-current="page"' if current is not None and current==u else '')+'>'+label+'</a>' for url,label,u in links)+'</nav>' if links else ''
    return '<header class="site-header"><a class="brand" href="index.html">'+SITE_TITLE+'</a>'+global_nav+chapters+'</header>'

def shell(title,body,current=None,scripts='',base='',area='study'):
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'+('<base href="'+html.escape(base,quote=True)+'">' if base else '')+'<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="AI基础与工程笔记、面试笔记：'+str(TOTAL_QUESTIONS)+'道练习、图解、手算与口述复习。"><title>'+html.escape(title)+' · '+SITE_TITLE+'</title><link rel="stylesheet" href="assets/katex/katex.min.css"><link rel="stylesheet" href="assets/course.css"></head><body class="area-'+html.escape(area,quote=True)+'"><a class="skip-link" href="#main-content">跳到正文</a><div class="wrap">'+nav(current,area)+body+'<footer class="site-footer"><p>开放学习笔记 · '+str(TOTAL_QUESTIONS)+'道新编教学题 · 非官方题库</p><a href="about.html">关于、来源与许可</a><a href="'+REPO+'/issues">勘误与建议</a><a href="'+REPO+'">查看源码</a><p>答题记录只保存在当前浏览器，不上传服务器；不同设备和域名之间不会自动同步。</p></footer></div>'+scripts+'</body></html>'

def build():
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
    katex=ROOT/'node_modules/katex'
    shutil.copytree(katex/'dist',OUT/'assets/katex',dirs_exist_ok=True)
    shutil.copy(katex/'LICENSE',OUT/'assets/katex/LICENSE')
    sources={u:(CONTENT/(FILES[u]+'.md')).read_text() for u,_,_ in COURSES}
    banks={u:[] for u,_,_ in COURSES}
    for name in QUESTION_FILES:
        for q in json.loads((CONTENT/name).read_text()):banks[q['unit']].append(q)
    keys=list(dict.fromkeys((m.group(1) is not None,m.group(1) or m.group(2)) for s in list(sources.values())+[text for bank in banks.values() for q in bank for text in [q['stem'],*q['options'],*q['explanations']]]+list(interviews.math_strings(INTERVIEW)) for m in MATH.finditer(s)))
    rendered=subprocess.run(['node',str(ROOT/'scripts/render_math.cjs')],input=json.dumps([{'display':d,'tex':t} for d,t in keys]),text=True,capture_output=True,check=True)
    formulas=dict(zip(keys,json.loads(rendered.stdout)))
    def rich(s):
        pieces=[];start=0
        for m in MATH.finditer(s):
            pieces.extend([html.escape(s[start:m.start()]),formulas[(m.group(1) is not None,m.group(1) or m.group(2))]])
            start=m.end()
        return ''.join(pieces)+html.escape(s[start:])
    question_rendering.rich=rich
    md=MarkdownIt('commonmark',{'html':False}).enable('table')
    def render_interview(source):
        slots={}
        def protect(m):
            key='FORMULASLOT'+str(len(slots))+'END';display=m.group(1) is not None
            slots[key]=(display,formulas[(display,m.group(1) or m.group(2))])
            return '\n\n'+key+'\n\n' if display else key
        body=md.render(MATH.sub(protect,source))
        for key,(display,formula) in slots.items():
            if display:body=body.replace('<p>'+key+'</p>','<div class="math-block">'+formula+'</div>')
            body=body.replace(key,formula)
        def diagram(m):
            svg=(ROOT/'assets'/m.group(1)).read_text()
            width,height=re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"',svg).groups()
            return f'src="assets/{m.group(1)}" width="{width}" height="{height}" loading="lazy"'
        return re.sub(r'src="\.\./assets/(interview-[a-z0-9-]+\.svg)"',diagram,body)
    legacy_links=json.loads((CONTENT/'legacy-unit-5-links.json').read_text())
    legacy_labels={}
    for course,source in sources.items():
        lesson=step=0
        for line in source.splitlines():
            if line.startswith('## '):
                lesson+=1;step=0
                legacy_labels[FILES[course]+f'.html#lesson-{lesson}']=line[3:]
            elif line.startswith('### '):
                step+=1
                legacy_labels[FILES[course]+f'.html#lesson-{lesson}-step-{step}']=line[4:]
    for course,bank in banks.items():
        for q in bank:legacy_labels[FILES[course]+'.html#q-'+q['id']]='第'+q['id']+'题'
    legacy_labels['unit-5.html#main-content']='AI Infra基础提纲'
    search=[]
    for u,title,description in COURSES:
        slots={}
        def protect(m):
            key='FORMULASLOT'+str(len(slots))+'END'
            slots[key]=(m.group(1) is not None,formulas[(m.group(1) is not None,m.group(1) or m.group(2))])
            return '\n\n'+key+'\n\n' if m.group(1) is not None else key
        tokens=md.parse(MATH.sub(protect,sources[u]));toc=[];steps={};count=0;step=0
        for i,t in enumerate(tokens):
            if t.type=='heading_open' and t.tag=='h2':
                count+=1;step=0;anchor=f'lesson-{count}';t.attrSet('id',anchor);toc.append((count,tokens[i+1].content))
                search.append({'title':tokens[i+1].content,'course':title,'url':FILES[u]+'.html#'+anchor})
            elif t.type=='heading_open' and t.tag=='h3' and count:
                step+=1;anchor=f'lesson-{count}-step-{step}';heading=tokens[i+1].content
                if u==8 and heading=='共享配置文件：为什么需要互斥（E-08题对应例子）':anchor='lesson-2-shared-config'
                if u==8 and heading=='三个容易混的概念':anchor='lesson-5-tool-mcp-skill'
                t.attrSet('id',anchor);steps.setdefault(count,[]).append((anchor,heading))
                search.append({'title':heading,'course':title,'url':FILES[u]+'.html#'+anchor})
        body=md.renderer.render(tokens,md.options,{})
        def diagram(m):
            svg=(ROOT/'assets'/m.group(1)).read_text()
            width,height=re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"',svg).groups()
            return f'src="assets/{m.group(1)}" width="{width}" height="{height}" loading="lazy"'
        body=re.sub(r'src="\.\./assets/((?:tree|rl)-[a-z0-9-]+\.svg)"',diagram,body)
        for key,(display,formula) in slots.items():
            if display:body=body.replace('<p>'+key+'</p>','<div class="math-block">'+formula+'</div>')
            body=body.replace(key,formula)
        sections=re.split(r'(?=<h2 id="lesson-\d+">)',body)
        for i,section in enumerate(sections):
            match=re.match(r'<h2 id="lesson-(\d+)">',section)
            if not match:continue
            lesson=int(match.group(1));related=[q for q in banks[u] if q['lesson']==lesson]
            def callout(qs):
                return '<p class="callout no-print"><strong>读完这个知识点，接着练：</strong> '+' · '.join('<a href="#q-'+q['id']+'">第'+q['id']+'题</a>' for q in qs)+'</p>'
            if u==9 or (u==5 and lesson==3) or (u==6 and lesson in (2,3,5)) or (u==7 and lesson in (2,3)):
                parts=re.split(r'(?=<h3 id="[^"]+">)',section);assigned=set()
                for j,part in enumerate(parts):
                    step_match=re.match(r'<h3 id="([^"]+)">',part)
                    if not step_match:continue
                    qs=[q for q in related if q.get('review_anchor')==step_match.group(1)]
                    if not qs:continue
                    assigned.update(q['id'] for q in qs)
                    marker='<h4>AVL：' if u==6 and step_match.group(1)=='lesson-3-step-3' else '<p><strong>题源与方法依据：'
                    parts[j]=part.replace(marker,callout(qs)+marker,1) if marker in part else part+callout(qs)
                assert assigned=={q['id'] for q in related}
                section=''.join(parts)
            elif related:section+=callout(related)
            if u==7 and lesson==4:section+=callout([q for q in banks[u] if q['id']=='5-20'])
            cross=RELATED.get((u,lesson),[])
            if cross:section+='<aside class="related"><strong>把知识连起来</strong><p>'+''.join('<a href="'+FILES[v]+'.html#'+anchor+'">'+html.escape(label)+' →</a>' for v,anchor,label in cross)+'</p></aside>'
            sections[i]=section
        body=''.join(sections)
        toc_html='<aside class="course-toc"><details open><summary>本章目录</summary>'+''.join('<a href="#lesson-'+str(n)+'">'+html.escape(t)+'</a>'+('<details class="topic-subnav"><summary>展开分步讲解</summary>'+''.join('<a href="#'+a+'">'+html.escape(b)+'</a>' for a,b in steps[n])+'</details>' if n in steps else '') for n,t in toc)+'<a class="practice-link" href="#practice">配套练习 · '+str(len(banks[u]))+'题</a></details></aside>'
        practice='<section id="practice" class="questions-heading"><h2>配套练习 · '+str(len(banks[u]))+'题</h2><p>先答题，再看逐项解析；多选须全部选对。可筛选错题、记录把握程度并导出答题记录。</p><div class="toolbar"><label>练习范围 <select id="scope"><option value="all">本章全部题</option><option value="wrong">最近提交答错</option><option value="uncertain">犹豫／猜测</option><option value="unanswered">本轮尚未提交</option></select></label><button id="export" type="button">导出答题记录</button></div><div id="summary" class="summary" aria-live="polite"></div><p id="save-status" class="status"></p><noscript><p>脚本未启用，仍可展开每道题的答案与解析。</p></noscript><div id="questions">'+''.join(question_rendering.question_html(q) for q in banks[u])+'</div></section>'
        extra=''
        if u==5:
            extra='<details class="legacy-links"><summary>旧版单元5的内容已搬到哪里？</summary><p>数据结构与算法见单元6，系统与网络见单元7。打开旧收藏会自动跳到对应小节；也可在下面手动选择。</p><ul>'+''.join('<li id="'+anchor+'"><a href="'+target+'">'+html.escape(legacy_labels[target])+' → 单元'+target[5]+'</a></li>' for anchor,target in legacy_links.items())+'</ul></details>'
        if u==8:
            refs=json.loads((CONTENT/'engineering-sources.json').read_text())
            extra='<section id="sources"><h2>工程专题资料来源</h2><p>公开回忆用于确定学习方向，技术资料用于核对概念；题目均为新编教学题。</p><ol class="source-list">'+''.join('<li id="source-'+s['id']+'"><a href="'+html.escape(s['url'],quote=True)+'">'+html.escape(s['id']+' · '+s['title'])+'</a><p>'+html.escape(s['coverage'])+'</p></li>' for s in refs)+'</ol></section>'
        position=next(i for i,course in enumerate(COURSES) if course[0]==u)
        previous=COURSES[position-1] if position else None
        following=COURSES[position+1] if position+1<len(COURSES) else None
        prev='<a class="button" href="'+(FILES[previous[0]]+'.html' if previous else 'study.html')+'">← '+('上一章' if previous else '返回笔记目录')+'</a>'
        nxt='<a class="button primary" href="'+(FILES[following[0]]+'.html' if following else 'study.html')+'">'+('下一章：'+following[1] if following else '回到笔记目录')+' →</a>'
        tools='<div class="page-tools"><a href="#practice">直接做本章练习</a><a href="'+REPO+'/blob/main/content/'+FILES[u]+'.md">查看Markdown源码</a><button type="button" onclick="window.print()">打印／存为PDF</button></div>'
        page=tools+'<div class="course-layout">'+toc_html+'<main id="main-content" class="course-article">'+body+practice+extra+'<div class="unit-navigation">'+prev+nxt+'</div></main></div>'
        data={'unit':u,'label':LABELS[u],'title':title,**STORAGE[u],'questions':[dict(q,answer_html=question_rendering.answer_html(q)) for q in banks[u]]}
        scripts='<script id="quiz-data" type="application/json">'+escaped_json(data)+'</script><script src="assets/records.js" defer></script><script src="assets/quiz.js" defer></script><script src="assets/site.js" defer></script>'
        if u==5:scripts='<script id="legacy-links" type="application/json">'+escaped_json(legacy_links)+'</script><script src="assets/legacy-links.js" defer></script>'+scripts
        (OUT/(FILES[u]+'.html')).write_text(shell(title,page,u,scripts))
    home='<main id="main-content"><section class="hero"><div class="eyebrow">概念 · 图解 · 手算 · 练习</div><h1>AI基础与工程笔记</h1><p class="lead">涵盖数学、机器学习、模型训练、AI Infra、数据结构、计算机系统、强化学习与偏好优化、Agent工程。结合概念、图解和例题，按你的兴趣与需要选择主题阅读。</p><p class="meta">'+str(len(COURSES))+'部分内容 · '+str(STUDY_QUESTIONS)+'道新编练习 · 免费阅读，无需登录</p></section><section class="search-panel"><label for="search"><strong>查找知识点</strong></label><p class="meta">例如：特征值、Adam、PPO、DPO、KV cache、互斥</p><input id="search" type="search" placeholder="输入关键词，搜索章节标题" autocomplete="off"><p id="search-status" aria-live="polite"></p><ul id="search-results"></ul></section><div class="home-grid">'
    for u,title,desc in COURSES:
        home+='<section class="home-card course-card"><div class="meta">'+LABELS[u]+' · '+str(len(banks[u]))+'道练习</div><h2>'+title+'</h2><p>'+desc+'</p><p id="progress-'+str(u)+'" class="home-progress">尚未读取学习记录</p><a class="button" href="'+FILES[u]+'.html">打开讲义与练习 →</a></section>'
    home+='</div><section class="panel"><h2>怎么使用这份笔记</h2><p>各部分按主题组织，可从章节目录自由选择，也可搜索关键词直达知识点。例题就在知识点旁，练习入口紧跟对应小节。顶部导航可随时切换各部分内容，“把知识连起来”会带你到相关章节。</p><p>答题记录保存在当前浏览器，首次结果和最近结果分别保留。更换设备前可以导出JSON备份；目前不提供记录导入或跨设备同步。本地文件版的记录不会自动迁移到此网站。</p><p>这些笔记由个人整理并借助AI辅助编写，配套题为教学自编，不是官方试题。欢迎通过GitHub指出错误、补充例题。</p></section></main>'
    progress=[dict(unit=u,url=FILES[u]+'.html',question_ids=[q['id'] for q in banks[u]],**STORAGE[u]) for u,_,_ in COURSES]
    (OUT/'study.html').write_text(shell('基础与工程笔记',home,0,'<script src="assets/records.js" defer></script><script id="progress-data" type="application/json">'+escaped_json(progress)+'</script><script id="search-data" type="application/json">'+escaped_json(search)+'</script><script src="assets/site.js" defer></script>'))
    interviews.build(ROOT,OUT,INTERVIEW,render_interview,lambda title,body,scripts='':shell(title,body,scripts=scripts,area='interview'),search)
    coding_practice.build(ROOT, OUT, lambda title, body, scripts='': shell(title, body, scripts=scripts, area='coding'), search)
    hub='<main id="main-content"><section class="hero"><div class="eyebrow">学习 · 练习 · 面试复习</div><h1>AI学习与面试笔记</h1><p class="lead">基础知识与面试复习放在同一个入口。按需要选择一份笔记，也可以搜索知识点，在讲解、例题和面试追问之间切换。</p></section><div class="home-grid collection-grid"><section class="home-card"><div class="meta">'+str(len(COURSES)-1)+'个主题单元 + 工程专题 · '+str(STUDY_QUESTIONS)+'道练习</div><h2>AI基础与工程笔记</h2><p>数学、机器学习、神经网络、AI Infra、数据结构、计算机系统、强化学习与Agent工程。</p><a class="button" href="study.html">打开基础与工程笔记 →</a></section><section class="home-card"><div class="meta">5个面试单元 · 60道练习 · 20道口述追问</div><h2>面试笔记</h2><p>Agentic RL、训练沙箱、轨迹与数据、训练技巧、异步系统，结合公开面经、项目表达与系统设计。</p><a class="button" href="interview.html">打开面试笔记 →</a></section></div><section class="search-panel"><label for="search"><strong>查找知识点与面试主题</strong></label><p class="meta">例如：GRPO、沙箱、通信、DPO、项目、口述</p><input id="search" type="search" placeholder="搜索两份笔记的章节标题" autocomplete="off"><p id="search-status" aria-live="polite"></p><ul id="search-results"></ul></section></main>'
    hub=hub.replace('</div><section class="search-panel">','<section class="home-card"><div class="meta">按知识点与岗位 · Python</div><h2>面试手撕专项复习</h2><p>AI Infra：sqrt、Attention、LRU、Softmax 与路径 DP，11 道练习。</p><a class="button" href="coding-practice.html">进入手撕专项 →</a></section></div><section class="search-panel">',1)
    (OUT/'index.html').write_text(shell('笔记总览',hub,scripts='<script id="search-data" type="application/json">'+escaped_json(search)+'</script><script src="assets/site.js" defer></script>',area='hub'))
    about=md.render((CONTENT/'about.md').read_text())
    (OUT/'about.html').write_text(shell('关于与许可','<main id="main-content" class="passage">'+about+'</main>',area='hub'))
    (OUT/'404.html').write_text(shell('页面未找到','<main id="main-content"><h1>这个页面暂时找不到</h1><p>请从<a href="/ai-study-notes/">学习首页</a>重新选择章节。</p></main>',base='/ai-study-notes/',area='hub'))
    (OUT/'.nojekyll').write_text('')
    print(json.dumps({'chapters':len(COURSES),'questions':TOTAL_QUESTIONS,'interview_units':5,'interview_lessons':20,'formulas':len(formulas),'search_entries':len(search)},ensure_ascii=False))

if __name__=='__main__':build()
