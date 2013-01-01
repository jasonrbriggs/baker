import os
import time

from pages import filter_pages
from baker import add_filter
from proton.template import Templates

def process_path(path, output_path, pages):
    sorted_posts = sorted(filter_pages(path, pages.values()), key=lambda x : x.url[len(path)+1:len(path)+11], reverse=True)
    total_posts = min(len(sorted_posts), 20)

    tmp = Templates._singleton['rss.xml']

    page = sorted_posts[0]
    tmp.setelement('channel-title', page.config.get('feed', 'title'))
    tmp.setelement('channel-link', page.config.get('feed', 'link'))
    tmp.setelement('channel-description', page.config.get('feed', 'description'))
    tmp.setelement('generator', 'SiteBaker')

    last_build = time.strftime('%a, %d %b %Y %H:%M:%S %Z')
    # temporary hack
    last_build = last_build.replace('BST', 'GMT')
    tmp.setelement('lastbuild', last_build)

    max_modified = 0
    tmp.repeat('items', total_posts)
    for x in range(0, total_posts):
        page = sorted_posts[x]
        max_modified = max(page.last_modified, max_modified)

        html_content = page.get_html_content()

        link = page.get_permalink()

        tmp.setelement('title', page.headers['title'], x)

        d = time.strftime('%a, %d %b %Y', time.strptime(page.get_posted_date(), '%d %b, %Y'))
        t = time.strftime(' %H:%M:%S %Z', time.localtime((page.last_modified))).replace('BST', 'GMT')
        tmp.setelement('pubdate', d + t, x)
        tmp.setelement('description', '<![CDATA[%s]]>' % html_content, x)
        tmp.setelement('link', link + '.html', x)
        tmp.setelement('guid', link, x)

    if path.startswith('/'):
        path = path[1:]

    feed_file = os.path.join(output_path, path, 'feed.xml')
    if os.path.exists(feed_file):
        statbuf = os.stat(feed_file)
        last_modified = statbuf.st_mtime
    else:
        last_modified = 0

    if max_modified >= last_modified:
        out = str(tmp)
        f = open(feed_file, 'w+')
        f.write(out)
        f.close()

def process(pages, output_path):
    paths = list(pages.values())[0].config.get('indexer', 'paths')
    for path in paths.split(','):
        process_path(path, output_path, pages)


add_filter('pages', process)