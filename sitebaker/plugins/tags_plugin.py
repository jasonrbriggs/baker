import os
import re

from events import add_filter, apply_filter, add_action, do_action
from pages import Page, get_root_page
from proton import template

split_re = re.compile(r'\s*,\s*')


def reset():
    global tag_repeat_count
    tag_repeat_count = 0


def sanitise_tag(tag):
    return tag.replace(' ', '-')


def split_tags(tags):
    return split_re.split(tags)


def process_postmeta(page, index=0):
    global tag_repeat_count

    if 'tags' in page.headers:
        page.template.set_value('tags', 'Tagged: ', index)
        x = 0
        tags = split_tags(page.headers['tags'])
        page.template.repeat('taglinks', len(tags), tag_repeat_count)
        for tag in tags:
            tag = sanitise_tag(tag)
            page.template.set_attribute('taglink', 'href', '/tags/%s.html' % tag, tag_repeat_count + x)
            page.template.set_value('taglink', tag, tag_repeat_count + x)
            x += 1
        tag_repeat_count += len(tags)
    else:
        page.template.hide('taglinks')


def process_pages(pages, output_path):
    root_page = get_root_page(pages)
    if not root_page:
        return pages

    index_title = root_page.config.get('tags', 'index_title')
    tag_title = root_page.config.get('tags', 'title')

    tags = {}

    print('Generating tag index pages')
    for page in pages.values():
        if 'tags' in page.headers:
            for tag in split_tags(page.headers['tags']):
                tag = sanitise_tag(tag)
                if tag not in tags:
                    tags[tag] = []
                tags[tag].append(page)

    tag_dir = os.path.join(output_path, 'tags')

    if not os.path.exists(tag_dir):
        os.makedirs(tag_dir)

    for fname in os.listdir(tag_dir):
        os.remove(os.path.join(tag_dir, fname))

    for tag in tags:
        tmp = template.get_template('tag.html')
        print('  - generating tag %s' % tag)

        output_name = os.path.join(tag_dir, '%s.html' % tag)

        tmp.repeat('posts', len(tags[tag]))
        x = 0
        do_action('post-meta-reset')
        for page in sorted(tags[tag], key=lambda x: x.last_modified, reverse=False):
            cpage = Page()
            cpage.copy(page)
            cpage.template = tmp
            tmp.set_value('content', page.get_html_content(include_title=True), x)
            apply_filter('post-meta', cpage, x)
            x += 1

        apply_filter('page-head', cpage)
        apply_filter('page-meta', cpage)
        apply_filter('page-menu', cpage)
        apply_filter('page-foot', cpage)

        tmp.set_value('page-title', tag_title % tag)
        tmp.set_value('tag', tag_title % tag)
        
        apply_filter('tag-page', cpage)

        out = str(tmp)
        f = open(output_name, 'w+')
        f.write(out)
        f.close()

    tag_counts = {k: len(v) for k, v in tags.items()}

    tag_classes = {}
    page = next(iter(pages.values()))
    for (name, value) in page.config.items('tags'):
        if name.isdigit():
            tag_classes[name] = value

    tmp = template.get_template('tags.html')
    if tmp is None:
        return

    tmp.repeat('tags', len(tags))
    x = 0
    for tag in sorted(tags):
        tmp.set_value('tag', tag, x)
        tmp.set_attribute('tag', 'href', '/tags/%s.html' % tag, x)
        count = tag_counts[tag]

        for key in sorted(tag_classes, reverse=True):
            if count >= int(key):
                tmp.set_attribute('tag', 'class', tag_classes[key], x)
        x += 1

    cpage = Page()
    cpage.copy(page)
    cpage.template = tmp
    apply_filter('page-head', cpage)
    apply_filter('page-meta', cpage)
    apply_filter('page-menu', cpage)
    apply_filter('page-foot', cpage)

    tmp.set_value('page-title', index_title)
    
    apply_filter('tags-index-page', cpage)

    output_name = os.path.join(tag_dir, 'index.html')
    f = open(output_name, 'w+')
    f.write(str(tmp))
    f.close()

    print('  - complete')

    return pages


add_filter('pages', process_pages)
add_filter('post-meta', process_postmeta)
add_action('post-meta-reset', reset)
