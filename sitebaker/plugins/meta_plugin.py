from events import add_filter


def process(page):
    """
    TBD
    """
    for header in page.headers:
        if header.startswith('meta-'):
            metatag = '<meta name="%s" content="%s" />' % (header[5:], page.headers[header])
            page.template.append('head', metatag)
    if 'title' in page.headers:
        page.template.set_value('page-title', page.headers['title'])
    return page

add_filter('page-meta', process)