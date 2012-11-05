import os
import re

from baker import add_filter, apply_filter
from pages import Page
from proton.template import Templates

split_re = re.compile(r'\s*,\s*')

def sanitise_tag(tag):
    return tag.replace(' ', '-')

def process(pages, output_path):
    tags = { }

    for page in pages.values():
        if 'tags' in page.headers:
            for tag in split_re.split(page.headers['tags']):
                tag = sanitise_tag(tag)
                if tag not in tags:
                    tags[tag] = [ ]
                tags[tag].append(page)

    tag_dir = os.path.join(output_path, 'tags')

    if not os.path.exists(tag_dir):
        os.makedirs(tag_dir)

    for fname in os.listdir(tag_dir):
        os.remove(os.path.join(tag_dir, fname))

    for tag in tags:
        tmp = Templates._singleton['tag.html']

        output_name = os.path.join(tag_dir, '%s.html' % tag)

        tmp.repeat('posts', len(tags[tag]))
        x = 0
        for page in sorted(tags[tag], key=lambda x : x.get_posted_date(), reverse=True):
            cpage = Page()
            cpage.copy(page)
            cpage.template = tmp
            tmp.setelement('content', page.get_html_content(include_title=True), x)
            apply_filter('post-meta', cpage, x)
            x += 1

        apply_filter('page-head', cpage)
        apply_filter('page-meta', cpage)
        apply_filter('page-menu', cpage)

        tmp.setelement('title', 'Tag: %s' % tag)
        tmp.setelement('tag', 'Tag: %s' % tag)

        out = str(tmp)
        f = open(output_name, 'w+')
        f.write(out)
        f.close()

    tag_counts = {k:len(v) for k, v in tags.items()}

    tmp = Templates._singleton['tags.html']
    tmp.repeat('tags', len(tags))
    x = 0
    for tag in sorted(tag_counts, key=tag_counts.get, reverse=True):
        tmp.setelement('tag', tag, x)
        tmp.setattribute('tag', 'href', '/tags/%s.html' % tag, x)
        x += 1

    cpage = Page()
    cpage.copy(page)
    cpage.template = tmp
    apply_filter('page-head', cpage)
    apply_filter('page-meta', cpage)
    apply_filter('page-menu', cpage)

    output_name = os.path.join(tag_dir, 'index.html')
    f = open(output_name, 'w+')
    f.write(str(tmp))
    f.close()

add_filter('pages', process)
