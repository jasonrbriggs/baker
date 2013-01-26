import re

import markdown2

from baker import add_filter, apply_filter

strong_re = re.compile(r'###(.*?)###', re.DOTALL | re.MULTILINE)

def markdown(content):
    rtn = markdown2.markdown(content, extras=['fenced-code-blocks'])
    match = strong_re.search(rtn)
    if match:
        rtn = strong_re.sub(r'<strong>\1</strong>', rtn)
    return rtn

def process(page, index=0):
    content = apply_filter('markdown', page.content)
    page.template.setelement('content', content, index)
    return page
    
add_filter('page-markdown', process)
add_filter('markdown', markdown)