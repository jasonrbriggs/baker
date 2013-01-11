from baker import add_filter, add_action

from tag_utils import *

global tag_repeat_count
tag_repeat_count = 0

def reset():
    global tag_repeat_count
    tag_repeat_count = 0

def process(page, index=0):
    global tag_repeat_count
    if 'posted-on' in page.headers:
        page.template.setelement('posted-on', 'Posted on %s' % page.get_posted_date(), index)
    page.template.setelement('permalink', 'Permalink', index)
    page.template.setattribute('permalink', 'href', page.url + '.html', index)

    if 'tags' in page.headers:
        page.template.setelement('tags', 'Tagged: ', index)
        x = 0
        tags = split_tags(page.headers['tags'])
        page.template.repeat('taglinks', len(tags), index)
        for tag in tags:
            tag = sanitise_tag(tag)
            page.template.setattribute('taglink', 'href', '/tags/%s.html' % tag, tag_repeat_count + x)
            page.template.setelement('taglink', tag, tag_repeat_count + x)
            #if x < len(tags) - 1:
            #    page.template.setelement('tagsep', ', ', tag_repeat_count + x)
            x += 1
        tag_repeat_count += len(tags)
    else:
        page.template.hide('taglinks')


add_filter('post-meta', process)
add_action('post-meta-reset', reset)