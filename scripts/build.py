"""Build the public study site from Markdown and question data; no private paths."""
from pathlib import Path
import html
import json
import re
import shutil
import subprocess
from markdown_it import MarkdownIt
import question_rendering

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs'
CONTENT = ROOT / 'content'
REPO = 'https://github.com/pyq623/ai-study-notes'
TITLE = 'AI基础与工程笔记'
MATH = re.compile(r'\$\$([\s\S]*?)\$\$|(?<!\$)\$([^\n$]+?)\$(?!\$)')
COURSES = [
    (1, '机器学习入门', '从样本、特征和标签，到近邻、聚类与模型评估。'),
    (2, '线性代数基础', '向量、矩阵、秩、特征值与正定，配逐步计算。'),
    (3, '概率、统计与信息论', '条件概率、常见分布、期望方差、熵与最大熵。'),
    (4, '神经网络与训练', '前向与反向传播、损失、AdamW、归一化与梯度裁剪。'),
    (5, 'AI Infra与计算机基础', '并行训练、推理优化，以及数据结构、网络与数据库。'),
    (6, '工程专题', 'Agent、工具调用、上下文、RAG、并发与故障恢复。'),
]
FILES = {u: f'unit-{u}' if u < 6 else 'engineering' for u, _, _ in COURSES}
LEGACY = {'5-12':'lesson-7-step-3','5-13':'lesson-7-step-1',
          '5-14':'lesson-8-step-4','5-15':'lesson-8-step-6',
          '5-18':'lesson-11-step-4','5-19':'lesson-11-step-7','5-20':'lesson-11-step-8'}
RELATED = {
    (1,7):[(3,'lesson-1','概率与统计基础')],
    (2,8):[(4,'lesson-4','反向传播与矩阵梯度')],
    (3,7):[(4,'lesson-2','Softmax与交叉熵')],
    (4,2):[(3,'lesson-7','信息论与熵')],
    (4,5):[(5,'lesson-1','训练状态与显存')],
    (4,7):[(5,'lesson-2','数据并行与全局batch')],
    (5,2):[(4,'lesson-5','梯度与优化器')],
    (5,4):[(6,'lesson-3','上下文管理')],
    (5,10):[(6,'lesson-2-shared-config','共享配置与互斥'),(6,'lesson-8','并发与取消')],
    (5,11):[(6,'lesson-7','重试与幂等'),(6,'lesson-10','缓存、限流与索引')],
    (6,2):[(5,'lesson-8-step-9','DAG与拓扑排序')],
    (6,3):[(5,'lesson-4','Attention与KV cache')],
    (6,7):[(5,'lesson-11-step-8','事务与消息重投')],
    (6,8):[(5,'lesson-10','线程、锁与死锁')],
    (6,10):[(5,'lesson-7','数组、栈、队列与哈希'),(5,'lesson-11-step-6','B+树与索引')],
    (6,11):[(5,'lesson-5','Prefill、Decode与延迟'),(5,'lesson-11-step-4','HTTP版本与传输')],
}

def escaped_json(value):
    return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c').replace('&', '\\u0026')

def nav(current=None):
    links = [('index.html','首页',0)] + [(FILES[u]+'.html',f'单元{u}' if u<6 else '工程专题',u) for u,_,_ in COURSES]
    return '<header class="site-header"><a class="brand" href="index.html">'+TITLE+'</a><nav class="site-nav" aria-label="全站导航">'+''.join('<a href="'+url+'"'+(' aria-current="page"' if current==u else '')+'>'+label+'</a>' for url,label,u in links)+'<a href="'+REPO+'">GitHub ↗</a></nav></header>'

def shell(title,body,current=None,scripts='',base=''):
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'+('<base href="'+html.escape(base,quote=True)+'">' if base else '')+'<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="开放的AI基础与工程学习笔记：五个基础单元、Agent工程专题、158道练习、图解与手算例题。"><title>'+html.escape(title)+' · '+TITLE+'</title><link rel="stylesheet" href="assets/katex/katex.min.css"><link rel="stylesheet" href="assets/course.css"></head><body><a class="skip-link" href="#main-content">跳到正文</a><div class="wrap">'+nav(current)+body+'<footer class="site-footer"><p>开放学习笔记 · 158道新编教学题 · 非官方题库</p><a href="about.html">关于、来源与许可</a><a href="'+REPO+'/issues">勘误与建议</a><a href="'+REPO+'">查看源码</a><p>答题记录只保存在当前浏览器，不上传服务器；不同设备和域名之间不会自动同步。</p></footer></div>'+scripts+'</body></html>'

def build():
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
    katex=ROOT/'node_modules/katex'
    shutil.copytree(katex/'dist',OUT/'assets/katex',dirs_exist_ok=True)
    shutil.copy(katex/'LICENSE',OUT/'assets/katex/LICENSE')
    sources={u:(CONTENT/(FILES[u]+'.md')).read_text() for u,_,_ in COURSES}
    banks={u:[] for u,_,_ in COURSES}
    for q in json.loads((CONTENT/'foundation-questions.json').read_text()):banks[q['unit']].append(q)
    banks[6]=json.loads((CONTENT/'engineering-questions.json').read_text())
    keys=list(dict.fromkeys((m.group(1) is not None,m.group(1) or m.group(2)) for s in list(sources.values())+[text for bank in banks.values() for q in bank for text in [q['stem'],*q['options'],*q['explanations']]] for m in MATH.finditer(s)))
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
                if u==6 and heading=='共享配置文件：为什么需要互斥（E-08题对应例子）':anchor='lesson-2-shared-config'
                if u==6 and heading=='三个容易混的概念':anchor='lesson-5-tool-mcp-skill'
                t.attrSet('id',anchor);steps.setdefault(count,[]).append((anchor,heading))
                search.append({'title':heading,'course':title,'url':FILES[u]+'.html#'+anchor})
        body=md.renderer.render(tokens,md.options,{})
        def diagram(m):
            svg=(ROOT/'assets'/m.group(1)).read_text()
            width,height=re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"',svg).groups()
            return f'src="assets/{m.group(1)}" width="{width}" height="{height}" loading="lazy"'
        body=re.sub(r'src="\.\./assets/(tree-[a-z0-9-]+\.svg)"',diagram,body)
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
            if u==5 and lesson in (7,8,11):
                parts=re.split(r'(?=<h3 id="[^"]+">)',section);assigned=set()
                for j,part in enumerate(parts):
                    step_match=re.match(r'<h3 id="([^"]+)">',part)
                    if not step_match:continue
                    qs=[q for q in related if q.get('review_anchor',LEGACY.get(q['id']))==step_match.group(1)]
                    if not qs:continue
                    assigned.update(q['id'] for q in qs)
                    marker='<h4>AVL：' if step_match.group(1)=='lesson-8-step-3' else '<p><strong>题源与方法依据：'
                    parts[j]=part.replace(marker,callout(qs)+marker,1) if marker in part else part+callout(qs)
                assert assigned=={q['id'] for q in related}
                section=''.join(parts)
            elif related:section+=callout(related)
            cross=RELATED.get((u,lesson),[])
            if cross:section+='<aside class="related"><strong>把知识连起来</strong><p>'+''.join('<a href="'+FILES[v]+'.html#'+anchor+'">'+html.escape(label)+' →</a>' for v,anchor,label in cross)+'</p></aside>'
            sections[i]=section
        body=''.join(sections)
        toc_html='<aside class="course-toc"><details open><summary>本章目录</summary>'+''.join('<a href="#lesson-'+str(n)+'">'+html.escape(t)+'</a>'+('<details class="topic-subnav"><summary>展开分步讲解</summary>'+''.join('<a href="#'+a+'">'+html.escape(b)+'</a>' for a,b in steps[n])+'</details>' if n in steps else '') for n,t in toc)+'<a class="practice-link" href="#practice">配套练习 · '+str(len(banks[u]))+'题</a></details></aside>'
        practice='<section id="practice" class="questions-heading"><h2>配套练习 · '+str(len(banks[u]))+'题</h2><p>先答题，再看逐项解析；多选须全部选对。可筛选错题、记录把握程度并导出答题记录。</p><div class="toolbar"><label>练习范围 <select id="scope"><option value="all">本章全部题</option><option value="wrong">最近提交答错</option><option value="uncertain">犹豫／猜测</option><option value="unanswered">本轮尚未提交</option></select></label><button id="export" type="button">导出答题记录</button></div><div id="summary" class="summary" aria-live="polite"></div><p id="save-status" class="status"></p><noscript><p>脚本未启用，仍可展开每道题的答案与解析。</p></noscript><div id="questions">'+''.join(question_rendering.question_html(q) for q in banks[u])+'</div></section>'
        extra=''
        if u==6:
            refs=json.loads((CONTENT/'engineering-sources.json').read_text())
            extra='<section id="sources"><h2>工程专题资料来源</h2><p>公开回忆用于确定学习方向，技术资料用于核对概念；题目均为新编教学题。</p><ol class="source-list">'+''.join('<li id="source-'+s['id']+'"><a href="'+html.escape(s['url'],quote=True)+'">'+html.escape(s['id']+' · '+s['title'])+'</a><p>'+html.escape(s['coverage'])+'</p></li>' for s in refs)+'</ol></section>'
        prev='<a class="button" href="'+(FILES[u-1]+'.html' if u>1 else 'index.html')+'">← '+('上一章' if u>1 else '返回首页')+'</a>'
        nxt='<a class="button primary" href="'+(FILES[u+1]+'.html' if u<6 else 'index.html')+'">'+('下一章：'+COURSES[u][1] if u<6 else '回到学习总览')+' →</a>'
        tools='<div class="page-tools"><a href="#practice">直接做本章练习</a><a href="'+REPO+'/blob/main/content/'+FILES[u]+'.md">查看Markdown源码</a><button type="button" onclick="window.print()">打印／存为PDF</button></div>'
        page=tools+'<div class="course-layout">'+toc_html+'<main id="main-content" class="course-article">'+body+practice+extra+'<div class="unit-navigation">'+prev+nxt+'</div></main></div>'
        data={'unit':u,'questions':[dict(q,answer_html=question_rendering.answer_html(q)) for q in banks[u]]}
        scripts='<script id="quiz-data" type="application/json">'+escaped_json(data)+'</script><script src="assets/quiz.js" defer></script><script src="assets/site.js" defer></script>'
        (OUT/(FILES[u]+'.html')).write_text(shell(title,page,u,scripts))
    home='<main id="main-content"><section class="hero"><div class="eyebrow">概念 · 图解 · 手算 · 练习</div><h1>AI基础与工程笔记</h1><p class="lead">从数学与机器学习，到模型训练、AI Infra与Agent工程。把概念讲清楚，把计算一步步写出来，再用练习检查理解。</p><a class="button primary" href="unit-1.html">从基础开始 →</a> <a class="button" href="engineering.html">直接看工程专题</a><p class="meta">6部分内容 · 158道新编练习 · 免费阅读，无需登录</p></section><section class="search-panel"><label for="search"><strong>查找知识点</strong></label><p class="meta">例如：特征值、Adam、HTTP、KV cache、互斥</p><input id="search" type="search" placeholder="输入关键词，搜索章节标题" autocomplete="off"><p id="search-status" aria-live="polite"></p><ul id="search-results"></ul></section><div class="home-grid">'
    for u,title,desc in COURSES:
        home+='<section class="home-card course-card"><div class="meta">'+('单元 '+str(u) if u<6 else '工程专题')+' · '+str(len(banks[u]))+'道练习</div><h2>'+title+'</h2><p>'+desc+'</p><p id="progress-'+str(u)+'" class="home-progress">尚未读取学习记录</p><a class="button" href="'+FILES[u]+'.html">打开讲义与练习 →</a></section>'
    home+='</div><section class="panel"><h2>怎么使用这份笔记</h2><p>初学可以按单元1～5阅读，再进入工程专题；已有基础可以按关键词或目录直达。例题就在知识点旁，练习入口紧跟对应小节。顶部导航可随时切换六部分内容，“把知识连起来”会带你到相关章节。</p><p>答题记录保存在当前浏览器，首次结果和最近结果分别保留。更换设备前可以导出JSON备份；目前不提供记录导入或跨设备同步。本地文件版的记录不会自动迁移到此网站。</p><p>这些笔记由个人整理并借助AI辅助编写，配套题为教学自编，不是官方试题。欢迎通过GitHub指出错误、补充例题。</p></section></main>'
    (OUT/'index.html').write_text(shell('学习总览',home,0,'<script id="search-data" type="application/json">'+escaped_json(search)+'</script><script src="assets/site.js" defer></script>'))
    about=md.render((CONTENT/'about.md').read_text())
    (OUT/'about.html').write_text(shell('关于与许可','<main id="main-content" class="passage">'+about+'</main>'))
    (OUT/'404.html').write_text(shell('页面未找到','<main id="main-content"><h1>这个页面暂时找不到</h1><p>请从<a href="/ai-study-notes/">学习首页</a>重新选择章节。</p></main>',base='/ai-study-notes/'))
    (OUT/'.nojekyll').write_text('')
    print(json.dumps({'chapters':6,'questions':sum(map(len,banks.values())),'formulas':len(formulas),'search_entries':len(search)},ensure_ascii=False))

if __name__=='__main__':build()
