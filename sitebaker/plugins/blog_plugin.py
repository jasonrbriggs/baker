import math

from pages import *
from baker import apply_filter, add_filter
from markdown import Markdown
from proton.template import Templates

md = Markdown()

def process_path(path, output_path, pages):
    sorted_posts = sorted(filter_pages(path, pages.values()), key=lambda x : x.url[len(path)+1:len(path)+11], reverse=True)
    total_posts = len(sorted_posts)
    posts_per_page = int(sorted_posts[0].config.get('blog', 'posts_per_page'))

    count = 0
    page_num = 0
    index = 0

    index_page = new_index_page(sorted_posts[0], page_num, count, total_posts, posts_per_page)

    if path.startswith('/'):
        path = path[1:]

    for page in sorted_posts:
        cpage = Page()
        cpage.copy(page)
        cpage.template = index_page.template
        cpage.template.setelement('content', md.convert(page.content), index)
        apply_filter('post-meta', cpage, index)
        index += 1
        count += 1
        if index >= posts_per_page:
            write_index_page(index_page.template, output_path, path, page_num)
            index = 0
            page_num += 1
            index_page = new_index_page(sorted_posts[0], page_num, count, total_posts, posts_per_page)

    if index > 0:
        write_index_page(index_page.template, output_path, path, page_num)

def new_index_page(page_to_copy, page_num, count, total_posts, posts_per_page):
    index_page = Page()
    index_page.url = None
    index_page.copy(page_to_copy)
    index_page.template = Templates._singleton['post.html'] #todo: replace with config

    apply_filter('page-head', index_page)
    apply_filter('page-meta', index_page)
    apply_filter('page-menu', index_page)

    total_pages = math.ceil(total_posts / posts_per_page) - 1

    if page_num > 0:
        index_page.template.setelement('prevpage', '<< Newer posts')
        if page_num - 1 == 0:
            index_page.template.setattribute('prevpage', 'href', 'index.html')
        else:
            index_page.template.setattribute('prevpage', 'href', 'index-%s.html' % (page_num - 1))

    if page_num < total_pages:
        index_page.template.setelement('nextpage', 'Older posts >>')
        index_page.template.setattribute('nextpage', 'href', 'index-%s.html' % (page_num + 1))

    if page_num > 0 and page_num < total_pages:
        index_page.template.setelement('pagelinksep', ' | ')



    index_page.template.repeat('posts', min(posts_per_page, total_posts - count))
    return index_page

def write_index_page(tmp, output_path, path, page_num):
    page = ''
    if page_num > 0:
        page = '-%s' % page_num
    out = str(tmp)
    f = open(os.path.join(output_path, path, 'index%s.html' % page), 'w+')
    f.write(out)
    f.close()

def process(pages, output_path):
    paths = list(pages.values())[0].config.get('indexer', 'paths')
    for path in paths.split(','):
        process_path(path, output_path, pages)

    
add_filter('pages', process)