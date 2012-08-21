from baker import add_filter

def process(page):
    if 'description' in page.headers:
        page.template.append('head', '<meta name="description" content="%s" />' % page.headers['description'])
    if 'keywords' in page.headers:
        page.template.append('head', '<meta name="keywords" content="%s" />' % page.headers['keywords'])
    if 'title' in page.headers:
        page.template.setelement('title', page.headers['title'])

add_filter('page-meta', process)