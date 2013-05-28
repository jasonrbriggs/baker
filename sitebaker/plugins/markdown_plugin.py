import re

import markdown2

from events import add_filter, apply_filter

strong_re = re.compile(r'<span class="c">###</span>\n\s*', re.DOTALL | re.MULTILINE)
strong_off_re = re.compile(r'<span class="c">###</span>')

heading_re = re.compile(r'<h2>(.*?)</h2>')


def markdown(content):
    content = content.replace('[break]', '<br class="clear" />')
    rtn = markdown2.markdown(content, extras=['fenced-code-blocks'])

    while strong_re.search(rtn):
        rtn = strong_re.sub(r'<span class="lolite">', rtn, 1)
        rtn = strong_off_re.sub('</span>', rtn, 1)

    return rtn


def add_anchors(content):
    for mat in heading_re.finditer(content):
        heading = mat.group(1)
        heading_anchor = heading.replace(' ', '-')
        content = content.replace('<h2>%s</h2>' % heading, '<h2 id="%s">%s</h2>' % (heading_anchor, heading))
    return content


def process(page, index=0):
    apply_filter('pre-markdown', page)
    content = apply_filter('markdown', page.content)
    content = add_anchors(content)
    page.template.set_value('content', content, index)
    return page


add_filter('page-markdown', process)
add_filter('markdown', markdown)