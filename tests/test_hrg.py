"""Keep public HRG builds independent of explicitly selected local drafts."""
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import hrg


class HrgBuildTests(unittest.TestCase):
    def test_default_build_replaces_local_draft_including_download(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'content').mkdir()
            out = root / 'docs'
            out.mkdir()
            public = '# Public guide\n\n### Q08 · General question\n\nPublic template\n'
            (root / 'content/accio-hrg.md').write_text(public)
            local = root / 'local.md'
            local.write_text('# LOCAL_ONLY_SENTINEL\n')
            shell = lambda title, body: '<html><head></head><body>' + body + '</body></html>'
            with patch.dict(os.environ, {'HRG_LOCAL_SOURCE': str(local)}):
                hrg.build(root, out, shell)
            self.assertIn('noindex,nofollow', (out / 'accio-hrg.html').read_text())
            with patch.dict(os.environ, {}, clear=True):
                hrg.build(root, out, shell)
            rendered = (out / 'accio-hrg.html').read_text()
            self.assertNotIn('LOCAL_ONLY_SENTINEL', rendered)
            self.assertNotIn('noindex', rendered)
            self.assertIn('id="q08"', rendered)
            self.assertEqual((out / 'accio-hrg.md').read_text(), public)

    def test_public_question_navigation_and_templates(self):
        root = Path(__file__).resolve().parents[1]
        source = (root / 'content/accio-hrg.md').read_text()
        self.assertEqual(source.count('class="hrg-answer-first"'), 18)
        for number in range(1, 19):
            self.assertIn(f'href="#q{number:02}"', source)
        self.assertNotIn('#personal-sources', source)
