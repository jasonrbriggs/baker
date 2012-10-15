import math
import os

from pages import filter_pages, Page
from baker import add_filter, apply_filter
from markdown import Markdown
from proton.template import Templates

md = Markdown()

def process_path(path, output_path, pages):
    sorted_posts = sorted(filter_pages(path, pages.values()), key=lambda x : x.url[len(path)+1:len(path)+11], reverse=True)
    total_posts = max(len(sorted_posts), 20)

    print('got here %s' % total_posts)


def process(pages, output_path):
    paths = list(pages.values())[0].config.get('indexer', 'paths')
    for path in paths.split(','):
        process_path(path, output_path, pages)


add_filter('pages', process)