"""Validate the generated site as readers see it, including cross-page anchors."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit,urljoin
import json
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
CHAPTERS=[f'unit-{i}.html' for i in range(1,6)]+['engineering.html']

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
        self.assertEqual(set(self.pages),set(CHAPTERS+['index.html','about.html','404.html']))
        for name,page in self.pages.items():
            for target in CHAPTERS+['index.html']:self.assertIn(target,page.nav,name)
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
            expected=json.loads((ROOT/'content'/('engineering-questions.json' if data['unit']==6 else 'foundation-questions.json')).read_text())
            expected=[q for q in expected if q['unit']==data['unit']]
            self.assertEqual(len(data['questions']),len(expected));total+=len(expected)
            for q,original in zip(data['questions'],expected):
                self.assertEqual({k:v for k,v in q.items() if k!='answer_html'},original)
                self.assertIn('q-'+q['id'],page.ids)
                self.assertEqual(len(q['options']),4);self.assertEqual(len(q['explanations']),4)
                self.assertTrue(q['answer'] and set(q['answer'])<=set('ABCD'))
                self.assertIn(q.get('review_anchor','lesson-'+str(q['lesson'])),page.ids)
        self.assertEqual(total,158)
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
        page=self.pages['unit-5.html'].text
        for step,qid in [(1,'5-45'),(2,'5-46'),(3,'5-47'),(4,'5-48'),(5,'5-49'),(6,'5-50')]:
            section=page.split(f'<h3 id="lesson-11-step-{step}">')[1].split('<h3 id=')[0]
            self.assertIn(f'href="#q-{qid}"',section)
    def test_no_analytics_or_external_scripts(self):
        for name,page in self.pages.items():
            self.assertTrue(all(not urlsplit(r).scheme for r in page.resources),name)
    def test_readme_counts(self):
        self.assertIn('158', (ROOT/'README.md').read_text())

if __name__=='__main__':unittest.main()
