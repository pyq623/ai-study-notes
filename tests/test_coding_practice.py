# -*- coding: utf-8 -*-
from pathlib import Path
import importlib.util
import hashlib
import json
import math
import random
import unittest
from collections import OrderedDict

ROOT = Path(__file__).resolve().parents[1]
SOLUTIONS = ROOT/'content/coding/solutions'

def load(name):
    spec = importlib.util.spec_from_file_location(name, SOLUTIONS/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class CodingTests(unittest.TestCase):
    def test_sqrt_against_library(self):
        floats=load('sqrt_float')
        for x in [0,1e-300,1e-12,.01,.25,1,2,4,10,1e12,1e300]:
            for fn in [floats.sqrt_binary,floats.sqrt_newton]:
                self.assertTrue(math.isclose(fn(x),math.sqrt(x),rel_tol=1e-10,abs_tol=1e-10), (fn,x))
        for x in [.25, 2, 10, 1e8 + 3]:
            for fn in [floats.sqrt_binary, floats.sqrt_newton]:
                for eps in [1e-6, 1e-10]:
                    self.assertLessEqual(abs(fn(x, eps) - math.sqrt(x)), eps, (fn, x, eps))
        for x in [-1,float('nan'),float('inf')]:
            for fn in [floats.sqrt_binary,floats.sqrt_newton]:
                with self.assertRaises(ValueError):fn(x)

    def test_softmax_online_and_shift(self):
        stable=load('softmax').stable_softmax; online=load('online_softmax').online_softmax
        rng=random.Random(23)
        for xs in [[],[-math.inf,-math.inf],[1000,1001],[0,-math.inf]]+[[rng.uniform(-1000,1000) for _ in range(50)] for _ in range(20)]:
            a,b=stable(xs),online(xs)
            for x,y in zip(a,b):self.assertAlmostEqual(x,y,places=12)
            if xs and any(math.isfinite(x) for x in xs):self.assertAlmostEqual(sum(a),1)
            for x,y in zip(a,stable([v+2000 for v in xs])):self.assertAlmostEqual(x,y,places=12)

    def test_lru_against_reference_and_list_integrity(self):
        rng=random.Random(41)
        for capacity in [1,2,5]:
            cache=load('lru').LRUCache(capacity); reference=OrderedDict()
            for _ in range(300):
                key=rng.randrange(8)
                if rng.random()<.6:
                    value=rng.randrange(100);cache.put(key,value)
                    if capacity:
                        reference[key]=value;reference.move_to_end(key)
                        if len(reference)>capacity:reference.popitem(last=False)
                else:
                    expected=reference.get(key,-1)
                    if key in reference:reference.move_to_end(key)
                    self.assertEqual(cache.get(key),expected)
                keys=[];node=cache.head
                while node.next is not cache.tail:
                    self.assertIs(node.next.prev,node)
                    node=node.next;keys.append(node.key)
                    self.assertLessEqual(len(keys),capacity)
                self.assertIs(cache.tail.prev,node)
                self.assertEqual(keys,list(reference))
                self.assertEqual(set(cache.hast_dict),set(reference))

    def test_paths_against_brute_force(self):
        paths=load('paths'); cost=load('min_path').minPathSum
        for m in range(1,8):
            for n in range(1,8):self.assertEqual(paths.uniquePaths(m,n),math.comb(m+n-2,m-1))
        self.assertEqual(cost([[1,3,1],[1,5,1],[4,2,1]]),7)
        self.assertEqual(cost([[1,2,3]]),6)

    def test_strings_against_enumeration(self):
        unique=load('substring').lengthOfLongestSubstring; palindrome=load('palindrome').longestPalindrome
        rng=random.Random(9)
        for s in ['', 'abba', 'cbbd', 'aaaa']+[''.join(rng.choice('abc') for _ in range(12)) for _ in range(100)]:
            subs=[s[i:j] for i in range(len(s)+1) for j in range(i,len(s)+1)]
            self.assertEqual(unique(s),max(map(len,(v for v in subs if len(set(v))==len(v)))))
            answer=palindrome(s)
            self.assertEqual(answer,answer[::-1]);self.assertIn(answer,s)
            self.assertEqual(len(answer),max(map(len,(v for v in subs if v==v[::-1]))))

    def test_original_solutions_are_preserved(self):
        originals=json.loads((ROOT/'content/coding/original-solutions.json').read_text())
        bank=json.loads((ROOT/'content/coding/ai-infra.json').read_text())
        self.assertEqual({item['code'] for item in originals},
                         {q['code'] for q in bank['questions'] if q['original']})
        for item in originals:
            self.assertEqual(hashlib.sha256((SOLUTIONS/item['code']).read_bytes()).hexdigest(),
                             item['sha256'], item['code'])

    def test_bank_sources_and_code(self):
        bank=json.loads((ROOT/'content/coding/ai-infra.json').read_text())
        self.assertEqual(len(bank['questions']),11)
        ids={s['id'] for s in bank['sources']}
        for q in bank['questions']:
            self.assertTrue(set(q['sources'])<=ids)
            code=(SOLUTIONS/q['code']).read_text()
            compile(code,q['code'],'exec')
            for field in ['task','examples','checks','pitfalls','complexity']:self.assertTrue(q[field])

    def test_neutral_course_has_no_employer_identifiers_or_source_post_links(self):
        for name in ['coding-ai-infra.html', 'coding-practice.html', 'index.html']:
            page=(ROOT/'docs'/name).read_text()
            self.assertNotIn('legacy-ai-infra',page)
        bank=json.loads((ROOT/'content/coding/ai-infra.json').read_text())
        self.assertTrue(all(not source['url'] for source in bank['sources']))
        self.assertTrue(all(q['id'].startswith('AI-') for q in bank['questions']))
