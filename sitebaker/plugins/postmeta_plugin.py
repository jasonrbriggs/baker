from baker import add_filter, add_action

def process(page, index=0):
    global tag_repeat_count
    if 'posted-on' in page.headers:
        page.template.setelement('posted-on', 'Posted on %s' % page.get_posted_date(), index)
    page.template.setelement('permalink', 'Permalink', index)
    page.template.setattribute('permalink', 'href', page.url + '.html', index)

add_filter('post-meta', process)