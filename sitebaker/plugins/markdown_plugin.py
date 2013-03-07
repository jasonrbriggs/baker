import re

import markdown2

from baker import add_filter, apply_filter

strong_re = re.compile(r'\<span class="c"\>###\</span\>\n\s*', re.DOTALL | re.MULTILINE)
strong_off_re = re.compile(r'\<span class="c"\>###\</span\>')

def markdown(content):
    rtn = markdown2.markdown(content, extras=['fenced-code-blocks'])

    while strong_re.search(rtn):
        rtn = strong_re.sub(r'<span class="lolite">', rtn, 1)
        rtn = strong_off_re.sub('</span>', rtn, 1)

    return rtn

def process(page, index=0):
    content = apply_filter('markdown', page.content)
    page.template.setelement('content', content, index)
    return page
    
add_filter('page-markdown', process)
add_filter('markdown', markdown)