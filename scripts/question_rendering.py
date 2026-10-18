"""Question cards shared by all sections."""
def answer_html(q):
    anchor = q.get('review_anchor', 'lesson-' + str(q['lesson']))
    return '<strong>正确答案：' + q['answer'] + '</strong><ol class="explanation-list">' + ''.join(('<li>' + rich(e) + '</li>' for e in q['explanations'])) + '</ol><a href="#' + anchor + '">回到本题对应讲解</a>'

def question_html(q):
    letters = 'ABCD'
    options = ''.join(('<label class="option"><input type="' + ('radio' if q['type'] == '单选' else 'checkbox') + '" name="q-' + q['id'] + '" value="' + letters[i] + '"><b>' + letters[i] + '</b><span>' + rich(v) + '</span></label>' for (i, v) in enumerate(q['options'])))
    return '<section class="question" id="q-' + q['id'] + '" data-id="' + q['id'] + '"><div class="meta">第' + q['id'] + '题 · ' + q['type'] + ' · 对应第' + str(q['lesson']) + '节</div><h3>' + rich(q['stem']) + '</h3><fieldset class="options"><legend class="meta">' + ('选择一个答案' if q['type'] == '单选' else '选择所有正确答案，多选需全部选对') + '</legend>' + options + '</fieldset><label class="certainty">作答把握<select class="confidence" aria-label="第' + q['id'] + '题作答把握"><option value="">请选择</option><option value="sure">确定，能解释</option><option value="unsure">犹豫</option><option value="guess">猜测</option></select></label><div class="actions"><button type="button" class="primary" data-submit="' + q['id'] + '">提交并看逐项解析</button><button type="button" data-retry="' + q['id'] + '">收起解析，重做本题</button></div><p class="attempt-note"></p><div class="feedback" aria-live="polite"></div><details class="offline-answer"><summary>无脚本阅读：查看答案与解析</summary>' + answer_html(q) + '</details><div class="print-answer">' + answer_html(q) + '</div></section>'
