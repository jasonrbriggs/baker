import math
import os
import time

from pages import filter_pages, Page, get_root_page
from events import add_filter, apply_filter, do_action
from proton import template
import utils


def get_posts_per_page(posts):
    try:
        return int(posts[0].config.get('blog', 'posts_per_page'))
    except:
        return 5


def process_path(path, output_path, pages):
    sorted_posts = sorted(filter_pages(path, pages.values()), key=lambda x: x.url[len(path)+1:len(path)+11], reverse=True)
    total_posts = len(sorted_posts)

    if total_posts == 0:
        return

    posts_per_page = get_posts_per_page(sorted_posts)

    count = 0
    page_num = 0
    index = 0

    if path.startswith('/'):
        path = path[1:]

    index_page = new_index_page(sorted_posts[0], page_num, count, total_posts, posts_per_page, path)

    do_action('post-meta-reset')
    for page in sorted_posts:
        cpage = Page()
        cpage.copy(page)
        cpage.template = index_page.template

        # TODO: this isn't right, need to fix later
        apply_filter('pre-markdown', cpage)

        content = apply_filter('markdown', page.content)

        cpage.template.set_value('content', content, index)
        apply_filter('post-meta', cpage, index)
        index += 1
        count += 1
        if index >= posts_per_page:
            write_index_page(index_page, output_path, path, page_num)
            do_action('post-meta-reset')
            index = 0
            page_num += 1
            index_page = new_index_page(sorted_posts[0], page_num, count, total_posts, posts_per_page, path)

    if index > 0:
        write_index_page(index_page, output_path, path, page_num)


def new_index_page(page_to_copy, page_num, count, total_posts, posts_per_page, path):
    index_page = Page()
    index_page.copy(page_to_copy)
    index_page.url = '/' + path + '/index-%s' % count
    index_page.template = template.get_template('post.html')

    apply_filter('page-head', index_page)
    apply_filter('page-meta', index_page)
    apply_filter('page-menu', index_page)
    apply_filter('page-foot', index_page)

    total_pages = math.ceil(total_posts / posts_per_page) - 1

    if page_num > 0:
        index_page.template.set_value('prevpage', '<< Newer posts')
        if page_num - 1 == 0:
            index_page.template.set_attribute('prevpage', 'href', 'index.html')
        else:
            index_page.template.set_attribute('prevpage', 'href', 'index-%s.html' % (page_num - 1))

    if page_num < total_pages:
        index_page.template.set_value('nextpage', 'Older posts >>')
        index_page.template.set_attribute('nextpage', 'href', 'index-%s.html' % (page_num + 1))

    if page_num > 0 and page_num < total_pages:
        index_page.template.set_value('pagelinksep', ' | ')

    index_page.template.repeat('posts', min(posts_per_page, total_posts - count))
    return index_page


def write_index_page(index_page, output_path, path, page_num):
    page = ''
    if page_num > 0:
        page = '-%s' % page_num
    apply_filter('blog-index-page', index_page)
    apply_filter('pre-output', index_page)

    out = str(index_page.template)
    f = open(os.path.join(output_path, path, 'index%s.html' % page), 'w+')
    f.write(out)
    f.close()


def blog_command(kernel, *args):
    """
    Create the directory, and an empty .text file, for today's blog entry.
    """
    config = utils.find_config(kernel.configs, '/')
    paths = config.get('blog', 'paths').split(',')
    path = paths[0]
    newpath = utils.url_join(kernel.options.output, path, time.strftime('%Y/%m/%d'))
    if not os.path.exists(newpath):
        os.makedirs(newpath)
        print('Created new blog dir %s' % newpath)

    if args and len(*args) > 0:
        title = ' '.join(*args)
    else:
        title = 'Temporary post'

    filename = os.path.join(newpath, title.lower().replace(' ', '-') + '.text')

    if not os.path.exists(filename):
        posted_on = time.strftime('%d %b, %Y')
        content = '''title: %(title)s
posted-on: %(posted-on)s
tags:

%(title)s
%(dashes)s

''' % {
            'title': title,
            'posted-on': posted_on,
            'dashes': ('-' * len(title))
        }

        with open(filename, 'w') as blog_file:
            blog_file.write(content)


def process_pages(pages, output_path):
    root_page = get_root_page(pages, 'blog')
    if not root_page:
        return pages
    paths = root_page.config.get('blog', 'paths')
    print('Generating blog index pages')
    if paths:
        for path in paths.split(','):
            process_path(path, output_path, pages)
    print('  - complete')
    return pages


def process_commands(commands):
    commands['blog'] = blog_command
    return commands


add_filter('pages', process_pages)
add_filter('commands', process_commands)