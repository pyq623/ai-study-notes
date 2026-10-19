"""Build the interview collection from portable lesson data and shared site components."""
import html
import json
import re
import question_rendering


def load(content):
    return json.loads((content/'interview-course.json').read_text())


def questions(bundle):
    return [q for unit in bundle['units'] for lesson in unit['lessons'] for q in lesson['questions']]


def math_strings(bundle):
    for unit in bundle['units']:
        for lesson in unit['lessons']:
            yield lesson['body']
            for q in lesson['questions']:
                yield from [q['stem'],*q['options'],*q['explanations']]


def build(root,out,bundle,render,shell,search):
    escape=html.escape
    units=bundle['units'];sources=bundle['sources']
    # Related foundation pages complement the interview lesson, without renumbering either course.
    related={
        (1,1):[('engineering.html#lesson-1','Agent与工程闭环'),('unit-8.html#lesson-1','token log-prob与mask'),('unit-8.html#lesson-2','Return与Advantage')],
        (1,2):[('unit-8.html#lesson-2','Return与Advantage')],
        (1,3):[('unit-8.html#lesson-10','DPO的四个log-prob')],
        (1,4):[('unit-1.html#lesson-7','模型评估基础')],
        (2,1):[('unit-7.html#lesson-1','线程、锁与死锁')],
        (2,2):[('engineering.html#lesson-7','恢复、重试与幂等')],
        (2,3):[('unit-5.html#lesson-1','显存与资源预算')],
        (2,4):[('engineering.html#lesson-12','评测与验收')],
        (3,1):[('unit-8.html#lesson-1','token log-prob与mask')],
        (3,2):[('engineering.html#lesson-3','上下文与状态')],
        (3,3):[('unit-5.html#lesson-2','并行训练与全局batch')],
        (3,4):[('unit-1.html#lesson-7','独立评测与数据划分')],
        (4,1):[('unit-8.html#lesson-7','GRPO组内优势')],
        (4,2):[('unit-8.html#lesson-4','PPO的四种clip情况')],
        (4,3):[('unit-8.html#lesson-6','熵与reference KL')],
        (4,4):[('unit-8.html#lesson-8','DAPO与聚合权重'),('unit-8.html#lesson-9','GSPO')],
        (5,1):[('engineering.html#lesson-8','并发与取消')],
        (5,2):[('unit-5.html#lesson-5','Prefill、Decode与吞吐')],
        (5,3):[('unit-8.html#lesson-3','Critic与GAE')],
        (5,4):[('interview-research.html#questions','12组面试追问')],
    }
    cards=[];print_parts=[]
    for unit in units:
        u=unit['id'];file=f'interview-unit-{u}.html'
        qs=[q for lesson in unit['lessons'] for q in lesson['questions']]
        cards.append('<section class="home-card"><div class="meta">面试单元'+str(u)+' · 4节 · 12题</div><h2>'+escape(unit['title'])+'</h2><p>'+escape(unit['description'])+'</p><a class="button" href="'+file+'">打开讲义与练习 →</a></section>')
        subtopics={l['number']:re.findall(r'^### (.+)$',l['body'],re.M) for l in unit['lessons']}
        toc='<aside class="course-toc"><details open><summary>本单元目录</summary>'+''.join('<a href="#lesson-'+str(l['number'])+'">'+str(l['number'])+'. '+escape(l['title'])+'</a>'+('<details class="topic-subnav"><summary>展开分步讲解</summary>'+''.join('<a href="#lesson-'+str(l['number'])+'-step-'+str(i)+'">'+escape(title)+'</a>' for i,title in enumerate(subtopics[l['number']],1))+'</details>' if subtopics[l['number']] else '') for l in unit['lessons'])+'<a href="#practice-controls">筛选错题与导出笔记</a></details></aside>'
        controls='<section class="panel" id="practice-controls"><p>每节读完紧接3题，再用口述追问练表达。</p><div class="toolbar"><label>练习范围<select id="scope"><option value="all">全部题目</option><option value="wrong">最近答错</option><option value="uncertain">最近犹豫／猜测</option><option value="unanswered">尚未提交</option></select></label><button type="button" id="practice-mode" aria-pressed="false">只看习题</button><button type="button" id="export">导出答题与口述笔记</button></div><p id="summary" class="summary" aria-live="polite"></p><p id="save-status" class="status"></p><p id="filter-status" class="status" aria-live="polite"></p></section>'
        lessons=[]
        print_parts.append('<h2 id="print-unit-'+str(u)+'">面试单元'+str(u)+' · '+escape(unit['title'])+'</h2>')
        for lesson in unit['lessons']:
            n=lesson['number'];title=escape(lesson['title']);body=render(lesson['body'])
            for i,_ in enumerate(subtopics[n],1):
                body=body.replace('<h3>','<h3 id="lesson-'+str(n)+'-step-'+str(i)+'">',1)
            rubric='<ul>'+''.join('<li>'+escape(r)+'</li>' for r in lesson['rubric'])+'</ul>'
            oral_answer=render(lesson['oral_answer']) if lesson.get('oral_answer') else ''
            oral_reference='<details><summary>展开精简参考答案</summary>'+oral_answer+'</details>' if oral_answer else ''
            links=''.join('<a href="interview-sources.html#'+k+'">'+k+' · '+escape(sources[k]['title'])+'</a> ' for k in lesson['sources'])
            oral='<details class="oral"><summary>继续口述：'+escape(lesson['oral'])+'</summary><p>先闭卷讲2分钟，再对照要点；页面不自动判断口述正确性。</p><textarea data-oral="u'+str(u)+'-l'+str(n)+'" aria-label="第'+str(n)+'节口述笔记" placeholder="写下回答、项目证据或待补的问题……"></textarea>'+oral_reference+'<details><summary>展开口述自检要点</summary>'+rubric+'</details></details>'
            cross='<aside class="related"><strong>回到基础与工程笔记</strong><p>'+''.join('<a href="'+url+'">'+escape(label)+' →</a>' for url,label in related[(u,n)])+'</p></aside>'
            lessons.append('<section class="lesson" id="lesson-'+str(n)+'"><h2>'+str(n)+'. '+title+'</h2><div class="lesson-body">'+body+'</div><p class="source-note">原整理核对依据：'+links+'</p>'+cross+'<div class="questions"><h3>读完本节，立即练3题</h3>'+''.join(question_rendering.question_html(q) for q in lesson['questions'])+'</div>'+oral+'</section>')
            print_body=body.replace('id="lesson-'+str(n)+'-step-','id="print-u'+str(u)+'-l'+str(n)+'-step-')
            print_parts.append('<section><h3 id="print-u'+str(u)+'-l'+str(n)+'">'+title+'</h3>'+print_body+'<p class="source-note">原整理核对依据：'+links+'</p>')
            for q in lesson['questions']:
                answer=question_rendering.answer_html(q).replace('href="#lesson-'+str(n)+'"','href="#print-u'+str(u)+'-l'+str(n)+'"')
                print_parts.append('<section class="question"><h4>'+q['id']+' · '+question_rendering.rich(q['stem'])+'</h4><ol type="A">'+''.join('<li>'+question_rendering.rich(o)+'</li>' for o in q['options'])+'</ol>'+answer+'</section>')
            print_parts.append('<h4>口述自检</h4><p>'+escape(lesson['oral'])+'</p>'+rubric+('<h4>精简参考答案</h4>'+oral_answer if oral_answer else '')+'</section>')
            search.append(dict(title=lesson['title'],course='面试笔记 · '+unit['title'],url=file+'#lesson-'+str(n)))
        previous=f'interview-unit-{u-1}.html' if u>1 else 'interview.html'
        following=f'interview-unit-{u+1}.html' if u<5 else 'interview.html'
        body='<div class="eyebrow">面试笔记 · Agentic RL</div><h1>面试单元'+str(u)+' · '+escape(unit['title'])+'</h1><p class="lead">'+escape(unit['description'])+'</p>'+controls+'<div class="course-layout">'+toc+'<main id="main-content" class="course-article"><article id="course-content">'+''.join(lessons)+'</article><div class="unit-navigation"><a href="'+previous+'">← '+('上一单元' if u>1 else '面试笔记目录')+'</a><a href="'+following+'">'+('下一单元' if u<5 else '返回面试笔记目录')+' →</a></div></main></div>'
        data=dict(unit=u,questions=[dict(q,answer_html=question_rendering.answer_html(q)) for q in qs])
        encoded=json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('&','\\u0026')
        scripts='<script id="quiz-data" type="application/json">'+encoded+'</script><script src="assets/interview-quiz.js" defer></script>'
        (out/file).write_text(shell('面试单元'+str(u)+' · '+unit['title'],body,scripts=scripts))
    home='<main id="main-content"><section class="hero"><div class="eyebrow">面经 · 知识点 · 练习 · 口述</div><h1>面试笔记</h1><p class="lead">围绕Agentic RL与后训练工程，把公开面经、技术复习和项目表达放在一起。按主题阅读，每节就地做题，再用追问检查能否讲清楚。</p><p class="meta">5个单元 · 20节讲解 · 60道练习 · 20道口述追问</p></section><div class="collection-tools"><a class="button" href="interview-research.html">面经与12组追问 →</a><a class="button" href="interview-sources.html">技术资料与来源 →</a><a class="button" href="interview-print.html">复习总册／打印版 →</a></div><div class="home-grid">'+''.join(cards)+'</div><section class="panel"><h2>把面试问题接回基础知识</h2><p>GRPO、clip或DPO算不清时，回看<a href="unit-8.html">强化学习与偏好优化算法</a>；通信、KV与吞吐问题回看<a href="unit-5.html">AI Infra</a>；工具调用、状态和恢复问题回看<a href="engineering.html">工程专题</a>。各节末尾也提供直接回看链接。</p><p>练习与口述记录只保存在当前浏览器，可筛选错题、重做并导出。原本地文件版的记录不会自动迁移到此网站，目前不支持导入。</p><p class="meta">面经和技术资料沿用2026年10月18日的整理记录；候选人回忆、自编教学题与技术推演分别标注。</p></section></main>'
    (out/'interview.html').write_text(shell('面试笔记',home))
    research=(root/'content/interview-research.html').read_text()
    (out/'interview-research.html').write_text(shell('面经与追问整理','<main id="main-content" class="research-report">'+research+'</main>'))
    source_body='<main id="main-content" class="passage"><h1>面试笔记：技术资料与来源</h1><p>各条资料注明最近核对日期。官方文档与论文用于核对技术原理，面经只提供复习方向；API与默认配置应按实施版本重新确认。</p><p><a href="interview-research.html">面经来源及适用边界 →</a></p><ol class="source-list">'+''.join('<li id="'+k+'"><strong>'+k+' · '+escape(s['kind'])+'</strong><p><a href="'+escape(s['url'],quote=True)+'">'+escape(s['title'])+'</a></p><p class="meta">核对日期：'+escape(s['checked_at'])+'</p></li>' for k,s in sources.items())+'</ol></main>'
    (out/'interview-sources.html').write_text(shell('面试资料来源',source_body))
    print_body='<main id="main-content" class="course-article interview-print"><h1>Agentic RL面试复习总册</h1><p>20节讲义、60题与口述自检要点。本页直接显示答案；练习请进入各单元。</p><button class="no-print" onclick="window.print()">打印／存为PDF</button>'+''.join(print_parts)+'</main>'
    (out/'interview-print.html').write_text(shell('面试复习总册',print_body))
    for anchor,label in [('sources','8篇公开面经'),('questions','12组面试追问'),('team','团队公开技术'),('plan','复习顺序建议')]:
        search.append(dict(title=label,course='面试笔记',url='interview-research.html#'+anchor))
