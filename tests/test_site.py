"""Validate the generated site as readers see it, including cross-page anchors."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit,urljoin
import json
import hashlib
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
CHAPTERS=[f'unit-{i}.html' for i in range(1,9)]+['engineering.html']

class Page(HTMLParser):
    def __init__(self,path):
        super().__init__();self.ids=[];self.links=[];self.resources=[];self.nav=[];self.in_nav=False;self.text=path.read_text();self.feed(self.text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='nav' and a.get('aria-label')=='全站导航':self.in_nav=True
        if tag=='a' and 'href' in a:
            self.links.append(a['href'])
            if self.in_nav:self.nav.append(a['href'])
        if tag in ('img','script') and 'src' in a:self.resources.append(a['src'])
        if tag=='link' and 'href' in a:self.resources.append(a['href'])
    def handle_endtag(self,tag):
        if tag=='nav':self.in_nav=False

class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.pages={p.name:Page(p) for p in DOCS.glob('*.html')}
    def test_pages_and_navigation(self):
        self.assertEqual(set(self.pages),set(CHAPTERS+[f'interview-unit-{u}.html' for u in range(1,6)]+['index.html','study.html','interview.html','interview-research.html','interview-sources.html','interview-print.html','about.html','404.html']))
        for name,page in self.pages.items():
            for target in ['index.html','study.html','interview.html']:self.assertIn(target,page.nav,name)
            self.assertIn('main-content',page.ids)
    def test_nested_404_navigation(self):
        page=self.pages['404.html']
        base=re.search(r'<base href="([^"]+)"',page.text).group(1)
        nested='https://pyq623.github.io/ai-study-notes/missing/path'
        resolved=urljoin(nested,base)
        for link in page.nav+page.resources:
            if not urlsplit(link).scheme:
                self.assertTrue(urljoin(resolved,link).startswith('https://pyq623.github.io/ai-study-notes/'))
                self.assertNotIn('/missing/',urljoin(resolved,link))
    def test_options_use_full_labels(self):
        for name in CHAPTERS:
            options=re.findall(r'<label class="option">(.*?)</label>',self.pages[name].text,re.S)
            self.assertTrue(options)
            for option in options:
                self.assertNotIn('aria-label=',option)
                self.assertIn('<span>',option)
    def test_unique_anchors(self):
        for name,page in self.pages.items():self.assertEqual(len(page.ids),len(set(page.ids)),name)
    def test_internal_links_and_assets(self):
        for name,page in self.pages.items():
            for link in page.links+page.resources:
                url=urlsplit(link)
                if url.scheme or url.netloc:continue
                path=unquote(url.path)
                if path.startswith('/ai-study-notes/'):path=path[len('/ai-study-notes/'):]
                target=DOCS/(path or name)
                if target.is_dir():target=target/'index.html'
                self.assertTrue(target.exists(),(name,link))
                if url.fragment:
                    self.assertIn(unquote(url.fragment),self.pages[target.name].ids,(name,link))
    def test_all_question_data_and_reviews(self):
        total=0
        for name in CHAPTERS:
            page=self.pages[name]
            data=json.loads(re.search(r'<script id="quiz-data" type="application/json">(.*?)</script>',page.text,re.S).group(1))
            expected=json.loads((ROOT/'content'/('engineering-questions.json' if data['unit']==8 else 'rl-questions.json' if data['unit']==9 else 'foundation-questions.json')).read_text())
            expected=[q for q in expected if q['unit']==data['unit']]
            self.assertEqual(len(data['questions']),len(expected));total+=len(expected)
            for q,original in zip(data['questions'],expected):
                self.assertEqual({k:v for k,v in q.items() if k!='answer_html'},original)
                self.assertIn('q-'+q['id'],page.ids)
                self.assertEqual(len(q['options']),4);self.assertEqual(len(q['explanations']),4)
                self.assertTrue(q['answer'] and set(q['answer'])<=set('ABCD'))
                self.assertIn(q.get('review_anchor','lesson-'+str(q['lesson'])),page.ids)
        self.assertEqual(total,208)
    def test_search_targets(self):
        data=json.loads(re.search(r'<script id="search-data" type="application/json">(.*?)</script>',self.pages['index.html'].text,re.S).group(1))
        self.assertGreater(len(data),100)
        for item in data:
            file,anchor=item['url'].split('#');self.assertIn(anchor,self.pages[file].ids)
    def test_formula_and_private_path_hygiene(self):
        for name,page in self.pages.items():
            self.assertNotIn('FORMULASLOT',page.text,name)
            self.assertNotIn('katex-error',page.text,name)
            for value in ['/Users/','file:///','原108题','10月17日笔试准备']:
                self.assertNotIn(value,page.text,name)
        self.assertIn('katex-mathml',self.pages['unit-4.html'].text)
    def test_diagrams_reserve_layout_space(self):
        for name in CHAPTERS:
            for tag in re.findall(r'<img[^>]+>',self.pages[name].text):
                self.assertRegex(tag,r'width="[0-9.]+"')
                self.assertRegex(tag,r'height="[0-9.]+"')
    def test_katex_font_files(self):
        css=(DOCS/'assets/katex/katex.min.css').read_text()
        for path in re.findall(r'url\(([^)]+)\)',css):
            self.assertTrue((DOCS/'assets/katex'/path.strip('\"\'')).is_file(),path)
        self.assertTrue((DOCS/'assets/katex/LICENSE').exists())
    def test_practice_links_follow_knowledge(self):
        for file,anchor,qid in [
            ('unit-6.html','lesson-2-step-1','5-21'),
            ('unit-6.html','lesson-3-step-5','5-39'),
            ('unit-6.html','lesson-5-step-1','5-49'),
            ('unit-6.html','lesson-5-step-2','5-50'),
            ('unit-7.html','lesson-2-step-1','5-45'),
            ('unit-7.html','lesson-2-step-2','5-46'),
            ('unit-7.html','lesson-3-step-1','5-47'),
            ('unit-7.html','lesson-3-step-2','5-48')]:
            section=self.pages[file].text.split(f'<h3 id="{anchor}">')[1].split('<h3 id=')[0].split('<h2 id=')[0]
            self.assertIn(f'href="#q-{qid}"',section)
    def test_split_preserves_every_question(self):
        expected=json.loads((ROOT/'tests/question-fingerprints.json').read_text())
        actual={}
        for file in ['foundation-questions.json','engineering-questions.json','rl-questions.json']:
            for q in json.loads((ROOT/'content'/file).read_text()):
                self.assertNotIn(q['id'],actual)
                actual[q['id']]=hashlib.sha256(json.dumps({k:q[k] for k in ('stem','type','options','answer','explanations')},ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        self.assertEqual({k:actual[k] for k in expected},expected)
        self.assertEqual(set(actual)-set(expected),{f'8-{n:02}' for n in range(1,33)})
    def test_infra_exercises_follow_their_topics(self):
        questions=json.loads((ROOT/'content/foundation-questions.json').read_text())
        for q in questions:
            if q['unit']!=5 or q['lesson']!=3:continue
            section=self.pages['unit-5.html'].text.split(f'<h3 id="{q["review_anchor"]}">')[1].split('<h3 id=')[0].split('<h2 id=')[0]
            self.assertIn(f'href="#q-{q["id"]}"',section)
        for page in self.pages.values():
            self.assertIn('268道',page.text)
            self.assertNotIn('158道',page.text)

    def test_rl_unit_labels_neighbors_and_topic_practice(self):
        page=self.pages['unit-8.html']
        data=json.loads(re.search(r'<script id="quiz-data" type="application/json">(.*?)</script>',page.text,re.S).group(1))
        self.assertEqual(data['label'],'单元8')
        self.assertEqual(data['storage_key'],'ai-study-notes-unit-8-v2')
        self.assertEqual(len(data['questions']),32)
        for q in data['questions']:
            section=page.text.split(f'<h3 id="{q["review_anchor"]}">')[1].split('<h3 id=')[0].split('<h2 id=')[0]
            self.assertIn(f'href="#q-{q["id"]}"',section)
        self.assertIn('href="unit-8.html">下一章：强化学习与偏好优化算法',self.pages['unit-7.html'].text)
        self.assertIn('href="engineering.html">下一章：工程专题',page.text)
        self.assertIn('href="unit-8.html">← 上一章',self.pages['engineering.html'].text)
        self.assertIn('>单元8</a>',self.pages['study.html'].text)

    def test_split_chapter_boundaries(self):
        infra=(ROOT/'content/unit-5.md').read_text()
        algorithms=(ROOT/'content/unit-6.md').read_text()
        systems=(ROOT/'content/unit-7.md').read_text()
        self.assertNotIn('## 6.',infra)
        self.assertNotIn('TCP：字节流',infra)
        for figure in ['tree-bst-search.svg','tree-btree-search-split.svg','tree-bplus-range.svg']:
            self.assertIn(figure,algorithms)
        self.assertNotIn('落到MySQL InnoDB',algorithms)
        self.assertIn('落到MySQL InnoDB',systems)
        self.assertIn('unit-6.html#lesson-5-step-2',systems)
    def test_old_bookmarks_resolve(self):
        mapping=json.loads((ROOT/'content/legacy-unit-5-links.json').read_text())
        # All moved old section anchors, including every previously numbered h3.
        expected={f'lesson-{n}' for n in range(6,13)}
        for lesson,steps in [(7,6),(8,9),(9,5),(11,8)]:
            expected.update(f'lesson-{lesson}-step-{n}' for n in range(1,steps+1))
        expected.update(f'q-5-{n:02}' for n in range(11,51))
        self.assertEqual(set(mapping),expected)
        for anchor,target in mapping.items():
            self.assertIn(anchor,self.pages['unit-5.html'].ids)
            file,new_anchor=target.split('#')
            self.assertIn(new_anchor,self.pages[file].ids)
        self.assertEqual(mapping['lesson-11-step-5'],'unit-6.html#lesson-5-step-1')
        self.assertEqual(mapping['lesson-11-step-4'],'unit-7.html#lesson-3-step-2')
    def test_progress_uses_disjoint_questions_and_storage(self):
        data=json.loads(re.search(r'<script id="progress-data" type="application/json">(.*?)</script>',self.pages['study.html'].text,re.S).group(1))
        self.assertEqual([len(x['question_ids']) for x in data],[14,16,15,15,28,32,8,32,48])
        self.assertEqual(len({x['storage_key'] for x in data}),9)
        self.assertEqual(data[-1]['storage_key'],'ai-study-notes-unit-6-v2')
        all_ids=[qid for x in data for qid in x['question_ids']]
        self.assertEqual(len(set(all_ids)),208)
        for x in data:
            file=x['url']
            quiz=json.loads(re.search(r'<script id="quiz-data" type="application/json">(.*?)</script>',self.pages[file].text,re.S).group(1))
            self.assertEqual(quiz['storage_key'],x['storage_key'])
            self.assertEqual(quiz.get('legacy_storage_key'),x.get('legacy_storage_key'))
    def test_no_analytics_or_external_scripts(self):
        for name,page in self.pages.items():
            self.assertTrue(all(not urlsplit(r).scheme for r in page.resources),name)
    def test_readme_counts(self):
        self.assertIn('208', (ROOT/'README.md').read_text())

if __name__=='__main__':unittest.main()
