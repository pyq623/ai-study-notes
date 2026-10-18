"""Independently recompute the numerical answers in the RL exercise bank."""
import json
import math
from pathlib import Path
import unittest

BANK={q['id']:q for q in json.loads((Path(__file__).resolve().parents[1]/'content/rl-questions.json').read_text())}


class RLArithmetic(unittest.TestCase):
    def choice(self,qid,expected):
        q=BANK[qid]
        self.assertEqual(q['type'],'单选')
        self.assertEqual(q['options']['ABCD'.index(q['answer'])],expected,qid)

    def test_log_prob_and_return(self):
        self.choice('8-01',f'{math.log(0.5*0.25):.3f}'.replace('-','−'))
        self.choice('8-03',str(int(sum((0.5**i)*r for i,r in enumerate([1,2,4])))))
        self.choice('8-04',f'{10-8}与{6-8}'.replace('-','−'))

    def test_terminal_gae_and_target(self):
        self.choice('8-06',str(2+0-5).replace('-','−'))
        # Reverse traversal uses the next advantage, with no continuation beyond terminal.
        advantages=[];following=0
        for delta in reversed([1,2]):
            following=delta+0.9*0.5*following
            advantages.append(following)
        self.choice('8-07',f'({advantages[-1]:g},{advantages[0]:g})')
        self.choice('8-09',str(2+3))

    def test_ppo_ratio_and_sign_dependent_clipping(self):
        self.choice('8-10',f'{math.exp(-1.3+1.5):.3f}')
        for qid,advantage,ratio in [('8-11',2,1.4),('8-12',-2,0.6)]:
            objective=min(ratio*advantage,max(0.8,min(1.2,ratio))*advantage)
            self.choice(qid,f'{objective:g}、{-objective:g}'.replace('-','−'))
        total=-1.2+0.5*(3-5)**2/2-0.1*0.5
        self.choice('8-15',f'{total:.2f}'.replace('-','−'))

    def test_kl_group_advantage_and_grpo_loss(self):
        kl=sum(p*math.log(p/q) for p,q in zip([0.5,0.5],[0.75,0.25]))
        self.choice('8-17',f'{kl:.3f}')
        self.choice('8-19',f'{2-math.log(2)-1:.3f}')
        rewards=[1,1,0,0];mean=sum(rewards)/len(rewards)
        std=math.sqrt(sum((r-mean)**2 for r in rewards)/len(rewards))
        self.choice('8-20',('('+','.join(f'{(r-mean)/std:g}' for r in rewards)+')').replace('-','−'))
        self.choice('8-22',f'{-((1.1-0.9)/2-0.1*0.2):.2f}'.replace('-','−'))

    def test_reduction_dapo_and_gspo(self):
        from fractions import Fraction
        sequences=[[1,1],[3,3,3,3]]
        sequence_mean=sum(Fraction(sum(s),len(s)) for s in sequences)/len(sequences)
        token_mean=Fraction(sum(map(sum,sequences)),sum(map(len,sequences)))
        self.choice('8-23',f'{sequence_mean}与{token_mean}')
        self.choice('8-24',f'[0.8,1.28]、{min(1.3,1.28):g}')
        self.choice('8-26',f'{1+(80-90)/20:g}')
        sequence_ratio=math.prod([2,0.5])**0.5
        self.choice('8-27',f'{sequence_ratio:g}')
        token_objective=(min(2,1.2)+min(0.5,0.8))/2
        self.choice('8-28',f'{token_objective:g}与{sequence_ratio:g}')

    def test_dpo_margin_loss_and_gradient(self):
        margin=(-2-(-4))-(-3-(-4))
        self.choice('8-29',f'{margin}与{math.log1p(math.exp(-margin)):.3f}')
        # Finite differences also check the negative derivative at a zero margin.
        loss=lambda gap:math.log1p(math.exp(-gap))
        h=1e-5
        self.assertAlmostEqual((loss(h)-loss(-h))/(2*h),-0.5,places=7)
        self.assertLess(loss(math.log(0.3/0.1)),loss(math.log(0.4/0.2)))


if __name__=='__main__':unittest.main()
