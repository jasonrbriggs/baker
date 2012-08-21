from baker import add_filter
from markdown import Markdown

md = Markdown()

def process(page, index=0):
    page.template.setelement('content', md.convert(page.content), index)
    
add_filter('page-markdown', process)