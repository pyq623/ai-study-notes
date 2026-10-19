"""Check both collections, preserved interview questions, and publication boundaries."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
BUNDLE=json.loads((ROOT/'content/interview-course.json').read_text())


class InterviewCollection(unittest.TestCase):
    def test_original_questions_preserved_and_practice_is_local_to_lesson(self):
        expected=json.loads((ROOT/'tests/interview-question-fingerprints.json').read_text())
        actual={};oral=0
        for unit in BUNDLE['units']:
            page=(ROOT/f'docs/interview-unit-{unit["id"]}.html').read_text()
            data=json.loads(re.search(r'<script id="quiz-data" type="application/json">(.*?)</script>',page,re.S).group(1))
            self.assertEqual(len(data['questions']),12)
            for lesson in unit['lessons']:
                self.assertEqual(len(lesson['questions']),3)
                section=page.split(f'<section class="lesson" id="lesson-{lesson["number"]}">')[1].split('<section class="lesson"')[0]
                self.assertIn('<textarea data-oral=',section);oral+=1
                self.assertIn('class="related"',section)
                for q in lesson['questions']:
                    self.assertIn('id="q-'+q['id']+'"',section)
                    rendered=next(x for x in data['questions'] if x['id']==q['id'])
                    self.assertEqual({k:v for k,v in rendered.items() if k!='answer_html'},q)
                    actual[q['id']]=hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        self.assertEqual(actual,expected)
        self.assertEqual(len(actual),60);self.assertEqual(oral,20)

    def test_hub_and_collection_search(self):
        hub=(ROOT/'docs/index.html').read_text()
        self.assertIn('href="study.html">打开基础与工程笔记',hub)
        self.assertIn('href="interview.html">打开面试笔记',hub)
        self.assertNotIn('class="button primary"',hub)
        search=json.loads(re.search(r'<script id="search-data" type="application/json">(.*?)</script>',hub,re.S).group(1))
        self.assertTrue(any(x['url'].startswith('unit-8.html') for x in search))
        self.assertEqual(sum(x['url'].startswith('interview-unit-') for x in search),20)
        self.assertTrue(any(x['url']=='interview-research.html#questions' for x in search))

    def test_no_personal_interview_schedule_or_session_context_is_published(self):
        for path in list((ROOT/'docs').glob('*.html'))+[ROOT/'content/interview-course.json',ROOT/'content/interview-research.html']:
            content=path.read_text()
            for private in ['10月22日','09:30','09:15','已读取聊天','登录态','前两面已聚焦','具体三面日期','/Users/']:
                self.assertNotIn(private,content,str(path))

    def test_interview_sources_and_print_book(self):
        sources=(ROOT/'docs/interview-sources.html').read_text()
        book=(ROOT/'docs/interview-print.html').read_text()
        for key in BUNDLE['sources']:self.assertIn('id="'+key+'"',sources)
        for unit in BUNDLE['units']:
            for lesson in unit['lessons']:
                for q in lesson['questions']:self.assertIn(q['id']+' · ',book)
        self.assertNotIn('<textarea',book)
        self.assertNotIn('id="quiz-data"',book)
        # Retain the original course's storage identity while keeping it distinct from study records.
        script=(ROOT/'assets/interview-quiz.js').read_text()
        self.assertIn("'accio-agentic-rl-v1-u'+UNIT",script)
        self.assertIn('records:state.records,oral:state.oral',script)


if __name__=='__main__':unittest.main()
