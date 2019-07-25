import emoji
import git
import math
import os
import re
import sys
import time

from pages import filter_pages, Page, get_root_page
from events import add_filter, apply_filter, do_action
from proton import template
import utils

import rss_plugin

mastodon_pat = re.compile(r'@([^\@]+)@([^@]+)')


def get_posts_per_page(posts):
    try:
        return int(posts[0].config.get('microblog', 'posts_per_page'))
    except:
        return 30


def process_micro_content(kernel, content):
    domain = kernel.config.get('site', 'domain')

    content_list = content.split(' ')
    for x in range(0, len(content_list)):
        word = content_list[x]
        mat = mastodon_pat.match(word)
        if mat:
            url = 'https://' + mat.group(2) + '/@' + mat.group(1)
            content_list[x] = '[%s](%s)' % (word, url)
        elif word.startswith('@'):
            url = 'https://twitter.com/' + word[1:]
            content_list[x] = '[%s](%s)' % (word, url)
        elif word.startswith('/'):
            url = 'https://' + domain + word
            word = word[0:20] + '&#x2026;'
            content_list[x] = '[%s](%s)' % (word, url)

    return emoji.emojize(' '.join(content_list))


def process_path(path, output_path, pages):
    sorted_posts = sorted(filter_pages(path, pages.values()), key=lambda x: x.url[len(path)+1:len(path)+11], reverse=True)
    total_posts = len(sorted_posts)

    if total_posts == 0:
        return

    kernel = sorted_posts[0].kernel

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

        if not cpage.config.has_section('feed'):
            cpage.config.add_section('feed')

        if not cpage.config.has_section('microblog'):
            cpage.config.add_section('microblog')

        cpage.config['feed']['title'] = cpage.config.get('site', 'title') + ' microblog'
        cpage.config['feed']['link'] = 'http://' +  cpage.config.get('site', 'domain')
        cpage.config['feed']['description'] = 'Microblog feed for ' + cpage.config.get('site', 'domain')

        single_page_tmp = template.get_template('micro-page.html')

        # TODO: this isn't right, need to fix later
        apply_filter('pre-markdown', cpage)

        content = process_micro_content(kernel, page.content)

        content = apply_filter('markdown', content)

        cpage.template.set_attribute('post-date-time', 'href', page.url + '.html', index)

        cpage.template.set_value('content', content, index)
        single_page_tmp.set_value('content', content)

        cpage.headers['title'] = '<![CDATA[' + content.rstrip() + ']]>'

        singlepage = Page()
        singlepage.copy(page)
        singlepage.template = single_page_tmp
        apply_filter('post-meta', singlepage)

        utils.write_page(single_page_tmp, output_path, '', cpage.url + '.html')

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

    rss_plugin.process_path('/' + path, output_path, sorted_posts)


def new_index_page(page_to_copy, page_num, count, total_posts, posts_per_page, path):
    index_page = Page()
    index_page.copy(page_to_copy)
    index_page.url = '/' + path + '/index-%s' % count
    index_page.template = template.get_template('micro-post.html')

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

    utils.write_page(index_page.template, output_path, path, 'index%s.html' % page)


def process_pages(pages, output_path):
    print('>>>>>>>>>>>> got here 1')
    root_page = get_root_page(pages, 'microblog')
    if not root_page:
        print('>>>>>>>> got here 2')
        return pages
    paths = root_page.config.get('microblog', 'paths')
    print('Generating microblog index pages')
    if paths:
        for path in paths.split(','):
            process_path(path, output_path, pages)
    print('  - complete')
    return pages


def process_commands(commands):
    commands['micro'] = microblog_command
    return commands


def microblog_command(kernel, *args):
    """
    Create the directory, and an empty .text file, for today's microblog entry.
    """
    config = utils.find_config(kernel.configs, '/')
    paths = config.get('microblog', 'paths').split(',')
    path = paths[0]
    newpath = utils.url_join(kernel.options.output, path, time.strftime('%Y/%m/%d'))
    if not os.path.exists(newpath):
        os.makedirs(newpath)
        print('Created new microblog dir %s' % newpath)

    args = args[0]

    title = time.strftime('%H%M%S')
    content = ' '.join(args[0:])
    content = emoji.emojize(content)

    if len(content) > 350:
        print('Not micro... length is %s' % (len(content)))
        sys.exit(1)

    content = process_micro_content(kernel, content)

    print()
    print(content)
    ok = input('Ok? ')
    if ok.lower() not in ('yes', 'y'):
        print('Microblog page creation halted.')
        sys.exit(0)

    filename = os.path.join(newpath, title + '.text')
    print('filename: %s' % filename)

    if not os.path.exists(filename):
        posted_time = time.strftime('%Y-%m-%dT%H:%M:%S%z')
        content = '''posted-time: %(posted-time)s

%(content)s''' % {
            'posted-time': posted_time,
            'content': content
        }

        with open(filename, 'w') as blog_file:
            blog_file.write(content)

    kernel.load_pages()
    kernel.run_command('generate')

    repo = git.Repo('.')
    g = repo.git
    g.add('-A')
    g.commit('-am', 'Microblog entry')
    g.push()

add_filter('pages', process_pages)
add_filter('commands', process_commands)