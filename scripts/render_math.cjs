const katex = require('katex');
let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => raw += chunk);
process.stdin.on('end', () => {
  try {
    const rendered = JSON.parse(raw).map(({tex, display}) => katex.renderToString(tex, {
      displayMode: display, throwOnError: true, strict: 'error', trust: false,
      output: 'htmlAndMathml'
    }).replace(/\uE020/g, '∕'));
    process.stdout.write(JSON.stringify(rendered));
  } catch (error) { process.stderr.write(error.message); process.exitCode = 1; }
});
