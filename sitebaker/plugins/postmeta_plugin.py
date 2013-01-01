from baker import add_filter

from tag_utils import *

def process(page, index=0):
    if 'posted-on' in page.headers:
        page.template.setelement('posted-on', 'Posted on %s' % page.get_posted_date(), index)
    page.template.setelement('permalink', 'Permalink', index)
    page.template.setattribute('permalink', 'href', page.url + '.html', index)
    '''
    if 'tags' in page.headers:
        page.template.setelement('tags', 'Tagged: ')
        page.template.repeat('taglinks', len(page.headers['tags']), index)
        x = 0
        for tag in split_tags(page.headers['tags']):
            tag = sanitise_tag(tag)
            page.template.setattribute('taglink', 'href', '/tags/%s.html' % tag, index + x)
            page.template.setelement('taglink', tag, index + x)
            x += 1
    else:
        page.template.hide('taglinks')
    '''

add_filter('post-meta', process)