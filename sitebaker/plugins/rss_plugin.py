import datetime
import os
import time

from pages import filter_pages, get_root_page
from events import add_filter
from proton import template


def process_path(path, output_path, pages):
    vals = pages
    if type(vals) == dict:
        vals = vals.values()
    sorted_posts = sorted(filter_pages(path, vals), key=lambda x: x.url[len(path)+1:len(path)+11], reverse=True)
    total_posts = min(len(sorted_posts), 20)

    if total_posts == 0:
        return

    tmp = template.get_template('rss.xml')
    if not tmp:
        return

    page = sorted_posts[0]

    tmp.set_value('channel-title', page.config.get('feed', 'title'))
    tmp.set_value('channel-link', page.config.get('feed', 'link'))
    tmp.set_value('channel-description', page.config.get('feed', 'description'))
    tmp.set_value('generator', 'SiteBaker')

    last_build = time.strftime('%a, %d %b %Y %H:%M:%S %Z')
    # temporary hack
    last_build = last_build.replace('BST', 'GMT')
    tmp.set_value('lastbuild', last_build)

    max_modified = sorted_posts[0].last_modified
    tmp.repeat('items', total_posts)
    for x in range(0, total_posts):
        page = sorted_posts[x]
        max_modified = max(page.last_modified, max_modified)

        html_content = page.get_html_content()

        link = page.get_permalink()

        if page.config.has_section('microblog'):
            tmp.hide('title', x)
        else:
            tmp.set_value('title', page.headers['title'], x)

        d = time.strftime('%a, %d %b %Y', time.strptime(page.get_posted_date(), '%d %b, %Y'))
        t = page.get_posted_datetime().strftime(' %H:%M:%S %z')
        tmp.set_value('pubdate', (d + t).rstrip(), x)
        tmp.set_value('description', '<![CDATA[%s]]>' % html_content, x)
        tmp.set_value('link', link + '.html', x)
        tmp.set_value('guid', link, x)

    if path.startswith('/'):
        path = path[1:]

    feed_file = os.path.join(output_path, path, 'feed.xml')
    if os.path.exists(feed_file):
        statbuf = os.stat(feed_file)
        last_modified = datetime.datetime.fromtimestamp(statbuf.st_mtime)
    else:
        last_modified = None

    if not last_modified or max_modified >= last_modified:
        out = str(tmp)
        f = open(feed_file, 'w+')
        f.write(out)
        f.close()


def process(pages, output_path):
    root_page = get_root_page(pages, 'blog')
    if not root_page:
        return pages
    paths = root_page.config.get('blog', 'paths')
    if paths:
        root_page.config.remove_section('microblog')
        for path in paths.split(','):
            process_path(path, output_path, pages)
    return pages


add_filter('pages', process)