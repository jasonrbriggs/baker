from events import add_filter


def process(page, index=0):
    global tag_repeat_count
    if 'posted-on' in page.headers:
        page.template.set_value('posted-on', 'Posted on %s' % page.get_posted_date(), index)
        page.template.set_value('post-date', page.get_posted_date(), index)
    if 'title' in page.headers:
        page.template.set_value('title', page.headers['title'], index)
    if 'sub-title' in page.headers:
        page.template.set_value('sub-title', page.headers['sub-title'], index)
    page.template.set_value('permalink', 'Permalink', index)
    page.template.set_attribute('permalink', 'href', page.url + '.html', index)
    page.template.set_value('permalink-url', page.url, index)
    page.template.set_attribute('permalink-url', 'href', page.url + '.html', index)
    return page

add_filter('post-meta', process)