"""Build the source-attributed HRG reading column using the existing site shell."""
from pathlib import Path
import os
import re
from markdown_it import MarkdownIt


def build(root: Path, out: Path, shell):
    # Personal drafts live outside the public source repository. Only an explicit
    # local build may use one; the default build remains the public column.
    local_source = os.environ.get('HRG_LOCAL_SOURCE')
    source = Path(local_source).read_text() if local_source else (root / 'content/accio-hrg.md').read_text()
    body = MarkdownIt('commonmark', {'html': True}).enable('table').render(source)
    body = re.sub(r'<h3>(Q(\d{2}) · .*?)</h3>', r'<h3 id="q\2">\1</h3>', body)
    headings = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    toc = '<nav aria-label="HRG 专栏目录">' + ''.join(
        f'<a href="#{anchor}">{title}</a>' for anchor, title in headings
    ) + '</nav>'
    tools = '<div class="page-tools"><a href="accio-hrg.md" download>下载 Markdown / 口述练习稿</a><a href="#questions">进入 18 题</a><a href="#sources">查看来源与边界</a></div>'
    body = body.replace('</h1>', '</h1>' + tools, 1)
    page = '<div class="course-layout"><aside class="course-toc">' + toc + '</aside><main id="main-content" class="course-article">' + body + '</main></div>'
    rendered = shell('Accio · HRG 面试准备专栏', page)
    head = '<link rel="stylesheet" href="assets/hrg.css">'
    if local_source:
        head += '<meta name="robots" content="noindex,nofollow">'
    (out / 'accio-hrg.html').write_text(rendered.replace('</head>', head + '</head>', 1))
    (out / 'accio-hrg.md').write_text(source)
