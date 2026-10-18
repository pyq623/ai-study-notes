"""Check numerical answer keys against independently counted payloads and events."""
import json
from pathlib import Path
import unittest
from fractions import Fraction

BANK={q['id']:q for q in json.loads((Path(__file__).resolve().parents[1]/'content/foundation-questions.json').read_text())}
MiB=2**20

def ring_send(full_bytes,ranks,phases=1):
    # One equal chunk sent to the next rank in every ring round of each phase.
    return sum(Fraction(full_bytes,ranks) for _ in range(phases) for _ in range(ranks-1))

class InfraArithmetic(unittest.TestCase):
    def choice(self,qid,expected):
        q=BANK[qid]
        self.assertEqual(q['type'],'单选')
        self.assertEqual(q['options']['ABCD'.index(q['answer'])],expected,qid)

    def test_ring_tp_sp(self):
        a=4*2048*4096*2
        self.choice('5-51',f'{a//MiB} MiB、{2*(4-1)}轮、{ring_send(a,4,2)//MiB} MiB')
        self.choice('5-53',f'{4*24*4}次')
        ar=ring_send(a,8,2)//MiB
        self.choice('5-54',f'{2*ar} MiB、{4*ar} MiB')
        sp=ring_send(a,4)//MiB
        self.choice('5-56',f'6 AG＋4 RS、{(6+4)*sp} MiB')

    def test_pp_boundaries(self):
        stages=4;batch_count=5
        messages=sum(1 for _ in range(batch_count) for _ in ('fwd','bwd') for _ in range(stages-1))
        self.choice('5-57',f'{messages}条、{messages*64} MiB')
        per_rank=[64*((rank<stages-1)+(rank>0)) for rank in range(stages)]
        self.choice('5-58','、'.join(map(str,per_rank))+' MiB')
        decode=Fraction(8*4096*2*10*(stages-1),MiB)
        self.choice('5-59',f'{float(decode):g} MiB')
        self.choice('5-68',f'{4*(32//stages)*4}次')

    def test_cp_counts_key_and_value_separately(self):
        self.choice('5-60',f'{4-1}轮、{ring_send(16*MiB,4)//MiB} MiB')
        key=2*4096*1024*2;value=key
        self.assertEqual((key+value)//MiB,32)
        train=3*ring_send(key+value,4)//MiB
        self.choice('5-61',f'{train} MiB、{train*4} MiB')

    def test_ep_and_dp(self):
        self.choice('5-63',f'{64//8}个；2次；4次')
        # Uniform destinations: exactly seven eighths of assignments go remote.
        route=1024*2*4096*2
        remote=Fraction(route*7,8)//MiB
        self.choice('5-64',f'{remote*2} MiB、{remote*4} MiB')
        buckets=[32*MiB]*4
        self.choice('5-66',f'{len(buckets)}次、{sum(ring_send(b,4,2) for b in buckets)//MiB} MiB')
        dp=ring_send(1_000_000*4,8,2)
        self.choice('5-67',f'{int(dp):,}；{int(dp*8):,}')
