"""Optional numerical checks for the downloadable PyTorch study examples."""
import importlib.util
from pathlib import Path
import unittest

try:
    import torch
except ModuleNotFoundError as exc:
    if exc.name != 'torch':
        raise
    torch = None

SOLUTIONS = Path(__file__).resolve().parents[1] / 'content/coding/solutions'


def load(name):
    spec = importlib.util.spec_from_file_location('coding_' + name, SOLUTIONS / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@unittest.skipIf(torch is None, 'Optional PyTorch runtime is not installed')
class CodingTorchTests(unittest.TestCase):
    def setUp(self):
        # Keep deterministic examples from changing other tests' random state.
        rng = torch.random.fork_rng(devices=[])
        rng.__enter__()
        self.addCleanup(rng.__exit__, None, None, None)
        torch.manual_seed(23)
        self.mha = load('mha').MultiHeadAttention
        self.mqa = load('mqa').MultiQueryAttention
        self.gqa = load('gqa').MultiGroupAttention

    def models(self):
        return [self.mha(16, 4).double(), self.mqa(16, 4).double(),
                self.gqa(16, 4, 2).double()]

    def assertClose(self, actual, expected):
        torch.testing.assert_close(actual, expected, rtol=1e-10, atol=1e-12)

    def test_shapes_and_causal_invariance(self):
        for model in self.models():
            with self.subTest(model=type(model).__name__):
                x = torch.randn(2, 5, 16, dtype=torch.float64)
                changed = x.clone()
                changed[:, 3:] += torch.randn_like(changed[:, 3:]) * 10
                output = model(x, causal=True)
                self.assertEqual(tuple(output.shape), (2, 5, 16))
                self.assertClose(output[:, :3], model(changed, causal=True)[:, :3])
                self.assertFalse(torch.allclose(model(x), model(changed)))

    def test_padding_key_invariance(self):
        # Only compare unchanged queries: a key mask does not mask query inputs.
        mask = torch.tensor([[1, 1, 0, 1, 0], [1, 0, 1, 0, 1]], dtype=torch.bool)
        for model in self.models():
            for causal in [False, True]:
                with self.subTest(model=type(model).__name__, causal=causal):
                    x = torch.randn(2, 5, 16, dtype=torch.float64)
                    changed = x.clone()
                    changed[~mask] += torch.randn_like(changed[~mask]) * 10
                    original = model(x, causal=causal, attention_mask=mask)
                    updated = model(changed, causal=causal, attention_mask=mask)
                    self.assertClose(original[mask], updated[mask])

    def test_valid_masks_have_finite_forward_and_backward(self):
        # Keep the first key valid so every causal query has a visible key.
        mask = torch.tensor([[1, 0, 1, 0, 0], [1, 1, 0, 1, 1]], dtype=torch.bool)
        for model in self.models():
            with self.subTest(model=type(model).__name__):
                x = torch.randn(2, 5, 16, dtype=torch.float64, requires_grad=True)
                output = model(x, causal=True, attention_mask=mask)
                self.assertTrue(torch.isfinite(output).all().item())
                output.square().sum().backward()
                self.assertTrue(torch.isfinite(x.grad).all().item())
                for name, parameter in model.named_parameters():
                    self.assertIsNotNone(parameter.grad, name)
                    self.assertTrue(torch.isfinite(parameter.grad).all().item(), name)

    def test_gqa_endpoints_match_aligned_mqa_and_mha(self):
        mqa, mha = self.mqa(16, 4).double(), self.mha(16, 4).double()
        one_group, all_groups = self.gqa(16, 4, 1).double(), self.gqa(16, 4, 4).double()
        one_group.load_state_dict(mqa.state_dict())
        with torch.no_grad():
            all_groups.q_proj.weight.copy_(mha.qkv_proj.weight[:16])
            all_groups.q_proj.bias.copy_(mha.qkv_proj.bias[:16])
            all_groups.kv_proj.weight.copy_(mha.qkv_proj.weight[16:])
            all_groups.kv_proj.bias.copy_(mha.qkv_proj.bias[16:])
        all_groups.out_proj.load_state_dict(mha.out_proj.state_dict())
        x = torch.randn(2, 5, 16, dtype=torch.float64)
        mask = torch.tensor([[1, 1, 1, 0, 1], [1, 0, 1, 0, 0]], dtype=torch.bool)
        for causal in [False, True]:
            for attention_mask in [None, mask]:
                for grouped, reference in [(one_group, mqa), (all_groups, mha)]:
                    with self.subTest(groups=grouped.group, causal=causal,
                                      masked=attention_mask is not None):
                        self.assertClose(grouped(x, causal, attention_mask),
                                         reference(x, causal, attention_mask))

    def test_gqa_intermediate_groups_use_consecutive_query_heads(self):
        model = self.gqa(16, 4, 2).double()
        x = torch.randn(2, 5, 16, dtype=torch.float64)
        q = model.q_proj(x).reshape(2, 5, 4, 4)
        k, v = model.kv_proj(x).reshape(2, 5, 2, 2, 4).unbind(dim=2)
        heads = []
        for head in range(4):
            group = head // 2
            scores = q[:, :, head] @ k[:, :, group].transpose(-1, -2) / 2
            heads.append(torch.softmax(scores, dim=-1) @ v[:, :, group])
        expected = model.out_proj(torch.cat(heads, dim=-1))
        self.assertClose(model(x), expected)

    def test_tensor_softmax_matches_last_dimension_reference(self):
        softmax = load('softmax').stable_softmax_attention
        for shape in [(2, 3, 4, 5), (1, 1, 2, 1)]:
            scores = torch.randn(*shape, dtype=torch.float64) * 1000
            if shape[-1] > 1:
                scores[..., 0] = -torch.inf
            actual = softmax(scores)
            self.assertEqual(tuple(actual.shape), shape)
            self.assertClose(actual, torch.softmax(scores, dim=-1))
            self.assertClose(actual.sum(dim=-1), torch.ones(shape[:-1], dtype=torch.float64))


if __name__ == '__main__':
    unittest.main()
