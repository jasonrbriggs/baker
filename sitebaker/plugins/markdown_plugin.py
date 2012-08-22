from baker import add_filter
from markdown import Markdown

md = Markdown()

def process(page, index=0):
    print('>>>>>>> GOT HERE')
    page.template.setelement('content', md.convert(page.content), index)
    
add_filter('page-markdown', process)
print('>>>>>>>> ADD FILTER')