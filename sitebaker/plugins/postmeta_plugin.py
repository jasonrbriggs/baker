from baker import add_filter

def process(page, index=0):
    if 'posted-on' in page.headers:
        page.template.setelement('posted-on', 'Posted on %s' % page.headers['posted-on'], index)
    page.template.setelement('permalink', 'Permalink', index)
    page.template.setattribute('permalink', 'href', page.url, index)

add_filter('post-meta', process)